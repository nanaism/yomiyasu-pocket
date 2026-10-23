"""run.py の結果を、本体 v2.2.2 の diff と lint で数える。

使い方:
  python3 -B score.py --body-tree <本体 v2.2.2> [--root ../runs] [--conds body,pocket_P0] [--jobs 8]
  python3 -B score.py --table [--conds body,pocket_P0,...]   （数えた結果を表にする）

- 1組ごとに before.md と after.md を一時のフォルダに写し、本体の CLI を動かす（終了コードと JSON をそのまま使う）。
  - 意味が変わる恐れ: yomiyasu_diff.py before.md after.md --fail-on meaning-risk --json の fail_on_meaning_risk_count と
    meaning_risks の counted のもの（kind、subkind、行）。文書の種類は指定しない（どの条件でも同じ）。
  - 残った候補: yomiyasu_lint.py after.md --json の counts（error、warn、info）と、原文の counts。
  - 書き換えた量: 原文と後の文の文字の差（difflib の opcodes の equal 以外で、元と後の長いほうの字数を足す）を、
    原文の空白を除いた字数1,000字あたりにした値。
- 結果は各組の score.json。--table は条件ごと、群ごとの合計と平均を出し、table.json と table.md を書く。
標準ライブラリだけ。本体の木（タグ v2.2.2）は --body-tree（なければ環境変数 BODY_DIR、それもなければリポジトリの body/）。
"""
import argparse
import concurrent.futures as cf
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.dirname(HERE)  # measurements/
REPO = os.path.dirname(DEV)
TREE = None  # main で --body-tree から決める
GROUPS = ("raw_ai", "blacklist_ai", "edge_cases", "human")


def run_cli(args, cwd):
    p = subprocess.run([sys.executable, "-B"] + args, cwd=cwd, capture_output=True, timeout=600,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


_FAIL_ON_KINDS = None


def counted(risk):
    """本体の diff の fail_on_count と同じ決まり（kind が FAIL_ON_KINDS か、unsupported/number）。"""
    global _FAIL_ON_KINDS
    if _FAIL_ON_KINDS is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_body_diff", os.path.join(TREE, "scripts", "yomiyasu_diff.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
        _FAIL_ON_KINDS = tuple(mod.FAIL_ON_KINDS)
    return risk.get("kind") in _FAIL_ON_KINDS or (risk.get("kind"), risk.get("subkind")) == ("unsupported", "number")


def change_per_1000(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    changed = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal")
    base = len(re.sub(r"\s", "", a)) or 1
    return round(changed * 1000.0 / base, 1)


def score_one(run_dir):
    res = json.load(open(os.path.join(run_dir, "result.json"), encoding="utf-8"))
    out = {"doc": res["doc"], "cond": res["cond"], "run": res["run"], "status": res["status"]}
    if res["status"] != "ok":
        json.dump(out, open(os.path.join(run_dir, "score.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return out
    work = tempfile.mkdtemp(prefix="pocket-score-")
    try:
        shutil.copy(os.path.join(run_dir, "before.md"), os.path.join(work, "before.md"))
        shutil.copy(os.path.join(run_dir, "after.md"), os.path.join(work, "after.md"))
        code, so, se = run_cli([os.path.join(TREE, "scripts", "yomiyasu_diff.py"), "before.md", "after.md",
                                "--fail-on", "meaning-risk", "--json"], work)
        d = json.loads(so)
        out["diff_exit"] = code
        out["meaning_risk_count"] = d.get("fail_on_meaning_risk_count", 0)
        out["risks"] = [{"kind": r.get("kind"), "subkind": r.get("subkind"), "old_line": r.get("old_line"),
                         "new_line": r.get("new_line"), "old": r.get("old"), "new": r.get("new")}
                        for r in d.get("meaning_risks") or [] if counted(r)]
        out["all_risk_count"] = len(d.get("meaning_risks") or [])
        for name in ("before", "after"):
            code, so, se = run_cli([os.path.join(TREE, "scripts", "yomiyasu_lint.py"), name + ".md", "--json"], work)
            ld = json.loads(so)
            out["lint_" + name] = ld.get("counts") or {}
            out["lint_" + name + "_rules"] = sorted({f.get("rule") for f in ld.get("findings") or []})
        a = open(os.path.join(work, "before.md"), encoding="utf-8").read()
        b = open(os.path.join(work, "after.md"), encoding="utf-8").read()
        out["changed_per_1000"] = change_per_1000(a, b)
        out["identical"] = a.strip() == b.strip()
    finally:
        shutil.rmtree(work, ignore_errors=True)
    json.dump(out, open(os.path.join(run_dir, "score.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


def run_dirs(root, conds):
    for c in conds:
        base = os.path.join(root, c)
        if not os.path.isdir(base):
            continue
        for r in sorted(os.listdir(base)):
            for g in GROUPS:
                gd = os.path.join(base, r, g)
                if not os.path.isdir(gd):
                    continue
                for n in sorted(os.listdir(gd)):
                    d = os.path.join(gd, n)
                    if os.path.exists(os.path.join(d, "result.json")) and ".failed-" not in n:
                        yield d


def lint_total(c):
    return sum(int(c.get(k, 0)) for k in ("error", "warn", "info"))


def table(root, conds):
    rows = {}
    for d in run_dirs(root, conds):
        p = os.path.join(d, "score.json")
        if not os.path.exists(p):
            continue
        s = json.load(open(p, encoding="utf-8"))
        cond = d[len(root) + 1:].split(os.sep)[0]
        run = d[len(root) + 1:].split(os.sep)[1]
        group = s["doc"].split("/")[0]
        rows.setdefault((cond, run), []).append((group, s))
    out = {}
    for (cond, run), items in sorted(rows.items()):
        key = cond + "/" + run
        t = out[key] = {"n": len(items), "ok": 0, "risk": 0, "docs_with_risk": 0, "lint_after": 0, "lint_before": 0,
                        "warn_after": 0, "identical": 0, "groups": {}}
        for group, s in items:
            g = t["groups"].setdefault(group, {"n": 0, "ok": 0, "risk": 0, "lint_after": 0, "change": []})
            g["n"] += 1
            if s.get("status") != "ok":
                continue
            t["ok"] += 1
            g["ok"] += 1
            t["risk"] += s["meaning_risk_count"]
            g["risk"] += s["meaning_risk_count"]
            t["docs_with_risk"] += 1 if s["meaning_risk_count"] else 0
            t["lint_after"] += lint_total(s["lint_after"])
            g["lint_after"] += lint_total(s["lint_after"])
            t["lint_before"] += lint_total(s["lint_before"])
            t["warn_after"] += int(s["lint_after"].get("warn", 0)) + int(s["lint_after"].get("error", 0))
            t["identical"] += 1 if s.get("identical") else 0
            g["change"].append(s["changed_per_1000"])
        for g in t["groups"].values():
            ch = sorted(g.pop("change"))
            g["change_median"] = ch[len(ch) // 2] if ch else None
            g["change_mean"] = round(sum(ch) / len(ch), 1) if ch else None
    json.dump(out, open(os.path.join(root, "table.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    lines = ["| 条件/回 | 本数(ok) | 意味が変わる恐れ | 恐れのある本 | lint 後(warn以上) | lint 前 | 原文のまま | human の書き換え量(中央値) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for key, t in out.items():
        hum = t["groups"].get("human", {})
        lines.append("| {} | {}({}) | {} | {} | {}({}) | {} | {} | {} |".format(
            key, t["n"], t["ok"], t["risk"], t["docs_with_risk"], t["lint_after"], t["warn_after"], t["lint_before"],
            t["identical"], hum.get("change_median")))
    open(os.path.join(root, "table.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    global TREE
    ap = argparse.ArgumentParser()
    ap.add_argument("--body-tree", default=os.environ.get("BODY_DIR") or os.path.join(REPO, "body"),
                    help="本体 v2.2.2 の木（既定は環境変数 BODY_DIR か、リポジトリの body/）")
    ap.add_argument("--root", default=os.path.join(DEV, "runs"))
    ap.add_argument("--conds", default="")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--rescore", action="store_true")
    a = ap.parse_args()
    TREE = os.path.abspath(a.body_tree)
    root = os.path.abspath(a.root)
    conds = a.conds.split(",") if a.conds else sorted(os.listdir(root)) if os.path.isdir(root) else []
    conds = [c for c in conds if os.path.isdir(os.path.join(root, c))]
    if a.table:
        table(root, conds)
        return
    todo = [d for d in run_dirs(root, conds) if a.rescore or not os.path.exists(os.path.join(d, "score.json"))]
    print("score", len(todo), flush=True)
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for i, _ in enumerate(ex.map(score_one, todo), 1):
            if i % 50 == 0:
                print(i, flush=True)
    table(root, conds)


if __name__ == "__main__":
    main()
