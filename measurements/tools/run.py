"""本体（v2.1.1 のスキル）と pocket の指示文で、同じ原稿を Codex CLI に推敲させる。

使い方:
  python3 -B run.py --body-tree <本体 v2.1.1> --codex-home <測定用の CODEX_HOME> --cond body --runs 1,2 [--docs raw_ai/01_tech_arch_sonnet_casual,...] [--jobs 6]
  python3 -B run.py --body-tree <本体> --codex-home <CODEX_HOME> --cond pocket:P0 --runs 1 [--jobs 8]
  python3 -B run.py --plan --cond pocket:P0 --runs 1     （組を数えるだけ）

- 本体の木は --body-tree（なければ環境変数 BODY_DIR、それもなければリポジトリの body/）。
- CODEX_HOME は --codex-home（なければ環境変数 CODEX_HOME）。ふだんの設定と分けた、測定用のものを渡す。
- 原稿は本体 v2.1.1 の木の tests/corpus/{raw_ai,blacklist_ai,edge_cases,human}/*.md（115本）。鍵は「群/名前」。
- 条件 body: 作業場所の .agents/skills/yomiyasu に本体 v2.1.1 の skills/yomiyasu を写し、draft.md に原稿を置き、
  「$yomiyasu:yomiyasu で draft.md を推敲し、最終稿を out.md に保存してください。」と頼む。砂場は workspace-write。
  後の文は out.md（なければ no_out）。
- 条件 pocket:<名前>: variants.json（既定は measurements/variants.json）の指示文と原稿を1つの依頼にして渡す（指示文、空行、原稿）。スキルもファイルも置かない。
  砂場は read-only。後の文は最後の返事（全体がコードの囲みに入っていれば中身を取り出し、そのことを記録する）。
- Codex の起動の形は下の CODEX_ARGV（--ignore-user-config ほか）。
  モデル gpt-6-astra、effort high、-c service_tier="ultrafast"。CODEX_HOME は測定用のもの（auth.json は読まない）。
- 結果は runs/<条件>/r<回>/<群>/<名前>/ に、before.md、after.md、last-message.txt、stderr.txt、events.jsonl、result.json。
  status: ok、no_out（動いたが後の文がない）、failed（timeout、returncode が0でない）。ok と no_out は飛ばす。
  --redo-failed で failed だけをやり直す。
標準ライブラリだけ。
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.dirname(HERE)  # measurements/
REPO = os.path.dirname(DEV)
TREE = None  # main で --body-tree から決める
CODEX_HOME = None  # main で --codex-home から決める
CODEX_BIN = "codex"
MODEL = "gpt-6-astra"
EFFORT = "high"
TIER = "ultrafast"
GROUPS = ("raw_ai", "blacklist_ai", "edge_cases", "human")
BODY_PROMPT = "$yomiyasu:yomiyasu で draft.md を推敲し、最終稿を out.md に保存してください。"
LOCK = threading.Lock()

# Codex CLI の起動の形。{codex_skills_disable} は、利用者のスキルを外す -c skills.config=[...] に展開する。
CODEX_ARGV = [
    "{bin}", "exec", "--json", "-C", "{ws}", "--skip-git-repo-check", "-s", "workspace-write",
    "-c", 'approval_policy="never"', "--ignore-rules", "--ignore-user-config",
    "-m", "{model}", "-c", 'model_reasoning_effort="{effort}"',
    "-c", "memories.generate_memories=false",
    "--disable", "memories", "--disable", "plugins", "--disable", "remote_plugin", "--disable", "apps",
    "--disable", "multi_agent",
    "-c", 'web_search="disabled"', "-c", "allow_login_shell=false", "-c", "skills.bundled.enabled=false",
    "{codex_skills_disable}",
    "-o", "{run_dir}/last-message.txt",
    "-",
]

# 子の環境は、この名前だけを親から受け継ぎ、CHILD_ENV を足して作る
ENV_PASSTHROUGH = [
    "HOME", "USER", "LOGNAME", "SHELL", "TMPDIR", "LANG", "LC_ALL", "LC_CTYPE", "LC_MESSAGES", "TERM", "COLORTERM",
    "__CF_USER_TEXT_ENCODING", "ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN", "OPENAI_API_KEY",
    "NODE_EXTRA_CA_CERTS", "SSL_CERT_FILE", "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY",
    "https_proxy", "http_proxy", "no_proxy",
]
CHILD_ENV = {
    "PYTHONDONTWRITEBYTECODE": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_TERMINAL_PROMPT": "0",
    "GIT_AUTHOR_NAME": "dev",
    "GIT_AUTHOR_EMAIL": "dev@example.invalid",
    "GIT_COMMITTER_NAME": "dev",
    "GIT_COMMITTER_EMAIL": "dev@example.invalid",
}


def docs_all():
    out = []
    for g in GROUPS:
        folder = os.path.join(TREE, "tests", "corpus", g)
        for name in sorted(os.listdir(folder)):
            if name.endswith(".md") and not name.startswith("."):
                out.append(g + "/" + name[:-3])
    return out


def skill_paths_to_disable():
    home = os.path.expanduser("~")
    found = set()
    for r in (os.path.join(home, ".agents", "skills"), os.path.join(CODEX_HOME, "skills")):
        if not os.path.isdir(r):
            continue
        for dirpath, dirnames, filenames in os.walk(r, followlinks=True):
            if os.path.relpath(dirpath, r).count(os.sep) >= 4:
                dirnames[:] = []
            if "SKILL.md" in filenames:
                found.add(os.path.join(dirpath, "SKILL.md"))
    return sorted(found)


def build_argv(ws, run_dir, sandbox):
    out = []
    for a in CODEX_ARGV:
        if a == "{codex_skills_disable}":
            paths = skill_paths_to_disable()
            if paths:
                out += ["-c", "skills.config=[" + ",".join("{path=%s,enabled=false}" % json.dumps(p) for p in paths) + "]"]
            continue
        out.append(a.replace("{bin}", CODEX_BIN).replace("{model}", MODEL).replace("{effort}", EFFORT)
                   .replace("{ws}", ws).replace("{run_dir}", run_dir))
    if sandbox != "workspace-write":
        i = out.index("-s")
        out[i + 1] = sandbox
    i = out.index("-")
    out[i:i] = ["-c", 'service_tier="%s"' % TIER]
    return out


def child_env():
    env = {k: os.environ[k] for k in ENV_PASSTHROUGH if k in os.environ}
    env["PATH"] = os.environ.get("PATH", "/usr/bin:/bin")
    env.update(CHILD_ENV)
    env["CODEX_HOME"] = CODEX_HOME
    return env


def load_variants(path):
    return json.load(open(path, encoding="utf-8"))


def unfence(text):
    m = re.fullmatch(r"\s*```[a-zA-Z]*\n(.*?)\n```\s*", text, re.S)
    return (m.group(1) + "\n", True) if m else (text, False)


def run_one(cond, run_idx, key, root, timeout, instruction):
    group, name = key.split("/", 1)
    run_dir = os.path.join(os.path.abspath(root), cond.replace(":", "_"), "r%d" % run_idx, group, name)
    res_path = os.path.join(run_dir, "result.json")
    if os.path.exists(res_path):
        old = json.load(open(res_path, encoding="utf-8"))
        if old.get("status") in ("ok", "no_out") or not ARGS.redo_failed:
            return old.get("status")
        shutil.move(run_dir, run_dir + ".failed-%d" % int(time.time()))
    os.makedirs(run_dir, exist_ok=True)
    src = open(os.path.join(TREE, "tests", "corpus", group, name + ".md"), encoding="utf-8").read()
    open(os.path.join(run_dir, "before.md"), "w", encoding="utf-8").write(src)
    ws = tempfile.mkdtemp(prefix="pocket-ws-")
    result = {"cond": cond, "run": run_idx, "doc": key, "model": MODEL, "effort": EFFORT, "service_tier": TIER}
    try:
        if cond == "body":
            shutil.copytree(os.path.join(TREE, "skills", "yomiyasu"), os.path.join(ws, ".agents", "skills", "yomiyasu"))
            open(os.path.join(ws, "draft.md"), "w", encoding="utf-8").write(src)
            prompt = BODY_PROMPT
            sandbox = "workspace-write"
        else:
            prompt = instruction + "\n\n" + src
            sandbox = "read-only"
        argv = build_argv(ws, run_dir, sandbox)
        result["argv"] = [a if not a.startswith("skills.config=") else "skills.config=[...]" for a in argv]
        start = time.time()
        try:
            p = subprocess.run(argv, input=prompt.encode("utf-8"), capture_output=True, timeout=timeout,
                               env=child_env(), cwd=ws)
            result["returncode"] = p.returncode
            open(os.path.join(run_dir, "events.jsonl"), "wb").write(p.stdout)
            open(os.path.join(run_dir, "stderr.txt"), "wb").write(p.stderr)
        except subprocess.TimeoutExpired:
            result["returncode"] = "timeout"
        result["seconds"] = round(time.time() - start, 1)
        last = os.path.join(run_dir, "last-message.txt")
        last_text = open(last, encoding="utf-8").read() if os.path.exists(last) else ""
        after = None
        if result["returncode"] != 0:
            result["status"] = "failed"
        elif cond == "body":
            out = os.path.join(ws, "out.md")
            if os.path.exists(out):
                after = open(out, encoding="utf-8").read()
            names = sorted(n for n in os.listdir(ws) if not n.startswith("."))
            result["workspace_files"] = names
            if os.path.isdir(os.path.join(ws, ".yomiyasu")):
                result["records"] = sorted(os.listdir(os.path.join(ws, ".yomiyasu", "runs"))) \
                    if os.path.isdir(os.path.join(ws, ".yomiyasu", "runs")) else []
            ev = open(os.path.join(run_dir, "events.jsonl"), encoding="utf-8", errors="replace").read()
            result["read_skill"] = "SKILL.md" in ev
            result["ran_check"] = "yomiyasu_check.py" in ev
            result["status"] = "ok" if after is not None else "no_out"
        else:
            if last_text.strip():
                after, fenced = unfence(last_text)
                result["unfenced"] = fenced
                result["status"] = "ok"
            else:
                result["status"] = "no_out"
        if after is not None:
            open(os.path.join(run_dir, "after.md"), "w", encoding="utf-8").write(after)
    finally:
        shutil.rmtree(ws, ignore_errors=True)
    json.dump(result, open(res_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return result["status"]


def main():
    global ARGS, TREE, CODEX_HOME, CODEX_BIN
    ap = argparse.ArgumentParser()
    ap.add_argument("--body-tree", default=os.environ.get("BODY_DIR") or os.path.join(REPO, "body"),
                    help="本体 v2.1.1 の木（既定は環境変数 BODY_DIR か、リポジトリの body/）")
    ap.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", ""),
                    help="測定用の CODEX_HOME（既定は環境変数 CODEX_HOME）")
    ap.add_argument("--codex-bin", default="codex", help="Codex CLI のコマンド")
    ap.add_argument("--variants", default=os.path.join(DEV, "variants.json"), help="pocket の指示文の候補")
    ap.add_argument("--cond", required=True)
    ap.add_argument("--runs", default="1")
    ap.add_argument("--docs", default="all")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--root", default=os.path.join(DEV, "runs"))
    ap.add_argument("--timeout", type=int, default=0)
    ap.add_argument("--redo-failed", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ARGS = ap.parse_args()
    TREE = os.path.abspath(ARGS.body_tree)
    CODEX_BIN = ARGS.codex_bin
    if not os.path.isdir(os.path.join(TREE, "tests", "corpus")):
        sys.exit("本体の木に tests/corpus がありません: " + TREE)
    docs = docs_all() if ARGS.docs == "all" else ARGS.docs.split(",")
    instruction = None
    if ARGS.cond.startswith("pocket:"):
        instruction = load_variants(ARGS.variants)[ARGS.cond.split(":", 1)[1]]["text"]
    elif ARGS.cond != "body":
        sys.exit("cond は body か pocket:<名前>")
    timeout = ARGS.timeout or (1200 if ARGS.cond == "body" else 300)
    jobs = [(int(r), d) for r in ARGS.runs.split(",") for d in docs]
    print("cond", ARGS.cond, "runs", ARGS.runs, "docs", len(docs), "jobs", len(jobs), flush=True)
    if ARGS.plan:
        return
    if not ARGS.codex_home:
        sys.exit("測定用の CODEX_HOME を --codex-home か環境変数 CODEX_HOME で渡してください")
    CODEX_HOME = os.path.abspath(ARGS.codex_home)
    counts = {}
    done = 0
    with cf.ThreadPoolExecutor(ARGS.jobs) as ex:
        futs = {ex.submit(run_one, ARGS.cond, r, d, ARGS.root, timeout, instruction): (r, d) for r, d in jobs}
        for f in cf.as_completed(futs):
            try:
                s = f.result()
            except Exception as e:  # noqa: BLE001
                s = "error:" + type(e).__name__
                print("error", futs[f], e, flush=True)
            counts[s] = counts.get(s, 0) + 1
            done += 1
            if done % 10 == 0 or done == len(jobs):
                print(done, "/", len(jobs), counts, flush=True)


if __name__ == "__main__":
    main()
