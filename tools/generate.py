#!/usr/bin/env python3
"""
抽出表（extract/table.json）と本体の写しから、pocket の指示文と付属のファイルを作る。

使い方:
  python3 tools/generate.py --body <本体のチェックアウト>
  python3 tools/generate.py --body <本体> --check            （作った中身とリポジトリのファイルを比べるだけ）
  python3 tools/generate.py --body <本体> --accept-changes   （節のハッシュと本体のコミットを抽出表に書き直す）
  python3 tools/generate.py --body <本体> --out <フォルダ>    （生成物を別のフォルダに書く。試験用）

作るもの: pocket.txt、MANIFEST.json、SOURCES.md、README.md の生成する部分（印のコメントのあいだ）。
README の生成する部分は、指示文と本体の SKILL.md の字数（len で数え、41,445字の形で書く）。生成元の本体の版とコミットは MANIFEST.json と SOURCES.md に書く。
時刻は入れないので、同じ抽出表と同じ本体からは同じバイト列ができる。

終了コード:
  0 できた（--check では、ファイルが生成物と同じ）
  1 --check で、生成物と違うファイルがある（何も書かない）
  2 抽出表が指す見出しが本体にないか、同じ道筋の見出しが2つ以上あって節を決められない。
    ないものと重なったものを1つの一覧にまとめて出し、何も書かない
  3 節の中身のハッシュが抽出表と違う（見直しが必要な節を出し、何も書かない。--accept-changes なら書き直して続ける）
  4 指示文が1段落でないか、400字を超える（何も書かない）
  5 抽出表の形（部分の role がない、知らない role を含む）、本体の版やコミット、README の印がおかしい（何も書かない。
    コミットの違いだけは --accept-changes で書き直して続ける）
標準ライブラリだけ。Python 3.9 以上。
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE_PATH = os.path.join("extract", "table.json")
VERSION_FILE = "skills/yomiyasu/SKILL.md"  # metadata.version を読むファイル
MAX_CHARS = 400
TABLE_FORMAT = "yomiyasu-pocket-extract"
TABLE_FORMAT_VERSION = 1
MANIFEST_FORMAT = "yomiyasu-pocket-manifest"
MANIFEST_FORMAT_VERSION = 1
RELEASE_RE = re.compile(r"^\d+\.\d+\.\d+$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
KINDS = ("rewritten", "verbatim")
# 部分の役割。output は返し方、meaning は意味を守る決まり、style は直す型、restraint は直さないもの。
ROLES = ("output", "meaning", "style", "restraint")
README_REGIONS = ("instruction", "body-size", "body-size-row")

HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]|$)")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


class HeadingError(Exception):
    """見出しで節を決められない（ない、または2つ以上ある）。args[0] は利用者に見せる文。"""


class GenError(Exception):
    """終了コードと、利用者に見せる文を持つ。"""

    def __init__(self, code, message):
        Exception.__init__(self, message)
        self.code = code
        self.message = message


# --- Markdown の見出しと節 ---

def split_lines(text):
    """改行（LF）を残したまま行に分ける。str.splitlines は LF 以外でも分けるので使わない。"""
    parts = text.split("\n")
    lines = [p + "\n" for p in parts[:-1]]
    if parts[-1]:
        lines.append(parts[-1])
    return lines


def headings(lines):
    """コードの囲みの外にある見出しを (行の番号, 段, 見出しの行) で返す。"""
    out = []
    fence = None  # 開いている囲みの記号の列（``` や ~~~~）
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        m = FENCE_RE.match(line)
        if fence is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                fence = m.group(1)
                continue
            h = HEADING_RE.match(line)
            if h:
                out.append((i, len(h.group(1)), line.strip()))
        elif m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2).strip():
            fence = None
    return out


def find_section(lines, path):
    """見出しの道筋（外側から順）に合う節を (始まりの行, 終わりの行の次) で返す。

    節は見出しの行から、同じ段かそれより上の次の見出しの手前まで。
    見つからないときも、2つ以上あって決められないときも、HeadingError を出す。
    """
    hs = headings(lines)
    start, end = 0, len(lines)
    for depth, want in enumerate(path):
        want = want.strip()
        hits = [(i, lv) for i, lv, text in hs if start <= i < end and text == want]
        if depth > 0:
            hits = [(i, lv) for i, lv in hits if i != start]
        if not hits:
            raise HeadingError("見つからない見出し: " + want)
        if len(hits) > 1:
            raise HeadingError("見出しが%d個あり、節を決められません: %s（%s 行目）" % (
                len(hits), want, "、".join(str(i + 1) for i, _ in hits)))
        i, lv = hits[0]
        nxt = [j for j, lv2, _ in hs if j > i and j < end and lv2 <= lv]
        start, end = i, (nxt[0] if nxt else end)
    return start, end


def section_body(text):
    """節の中身から見出しの行を除き、前後の空行を落とす（verbatim の部分に使う）。"""
    return "".join(split_lines(text)[1:]).strip("\n")


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8").replace("\r\n", "\n")


def body_version(skill_text):
    """SKILL.md の先頭の YAML から metadata.version を読む。"""
    lines = skill_text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    in_meta = False
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.startswith((" ", "\t")):
            in_meta = line.rstrip() == "metadata:"
            continue
        m = re.match(r"^\s+version:\s*[\"']?([^\"'\s]+)[\"']?\s*$", line)
        if in_meta and m:
            return m.group(1)
    return None


def git_head(path):
    """本体が git のチェックアウトなら HEAD のコミットを返す。そうでなければ None。"""
    if not os.path.exists(os.path.join(path, ".git")):
        return None
    try:
        p = subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    out = p.stdout.decode("utf-8", "replace").strip()
    return out if p.returncode == 0 and COMMIT_RE.match(out) else None


# --- 抽出表 ---

def load_table(repo):
    path = os.path.join(repo, TABLE_PATH)
    try:
        table = json.loads(read_text(path))
    except (OSError, ValueError) as e:
        raise GenError(5, "抽出表を読めません: %s (%s)" % (path, e))
    check_table(table)
    return table


def check_table(t):
    """抽出表の形を確かめる。おかしいところはまとめて出す。"""
    errs = []
    if t.get("format") != TABLE_FORMAT or t.get("format_version") != TABLE_FORMAT_VERSION:
        errs.append("format と format_version が %s / %d ではありません" % (TABLE_FORMAT, TABLE_FORMAT_VERSION))
    if not RELEASE_RE.match(str(t.get("release", ""))):
        errs.append("release が 1.0.0 のような3つの数の形ではありません: %r" % t.get("release"))
    body = t.get("body") or {}
    for k in ("repository", "version", "tag", "commit"):
        if not isinstance(body.get(k), str) or not body.get(k):
            errs.append("body.%s がありません" % k)
    if body.get("commit") and not COMMIT_RE.match(body["commit"]):
        errs.append("body.commit が40桁の16進数ではありません")
    ids = set()
    for s in t.get("sections") or []:
        sid = s.get("id")
        if not sid or sid in ids:
            errs.append("節の id がないか、重なっています: %r" % sid)
        ids.add(sid)
        if not isinstance(s.get("file"), str) or not s.get("file"):
            errs.append("%s: file がありません" % sid)
        if not isinstance(s.get("heading"), list) or not s.get("heading"):
            errs.append("%s: heading は見出しの行の並びにします" % sid)
        if not isinstance(s.get("sha256", ""), str):
            errs.append("%s: sha256 は文字列にします" % sid)
    if not ids:
        errs.append("sections が空です")
    pids = set()
    for p in t.get("pieces") or []:
        pid = p.get("id")
        if not pid or pid in pids:
            errs.append("部分の id がないか、重なっています: %r" % pid)
        pids.add(pid)
        kind = p.get("kind")
        if kind not in KINDS:
            errs.append("%s: kind は %s のどれかにします" % (pid, "、".join(KINDS)))
        if p.get("role") not in ROLES:
            errs.append("%s: role は %s のどれかにします: %r" % (pid, "、".join(ROLES), p.get("role")))
        if kind == "rewritten" and not (isinstance(p.get("text"), str) and p.get("text")):
            errs.append("%s: rewritten には text が要ります" % pid)
        if kind == "verbatim":
            if p.get("section") not in ids:
                errs.append("%s: verbatim の section が sections にありません: %r" % (pid, p.get("section")))
            if "text" in p:
                errs.append("%s: verbatim の文は本体の節から取るので、text は書きません" % pid)
        srcs = piece_sources(p)
        if not srcs:
            errs.append("%s: sources がありません" % pid)
        for s in srcs:
            if s not in ids:
                errs.append("%s: sources の %s が sections にありません" % (pid, s))
    if not pids:
        errs.append("pieces が空です")
    if errs:
        raise GenError(5, "抽出表の形がおかしいところがあります:\n" + "\n".join("  - " + e for e in errs))


def piece_sources(p):
    """部分の出どころ。verbatim で sources を書かなければ、取ってくる節だけ。"""
    srcs = list(p.get("sources") or [])
    if p.get("kind") == "verbatim" and p.get("section") and p["section"] not in srcs:
        srcs.insert(0, p["section"])
    return srcs


def dump_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def heading_label(s):
    return s["file"] + " > " + " > ".join(h.lstrip("#").strip() for h in s["heading"])


# --- 生成 ---

def read_sections(table, body):
    """本体から節を取り出す。見出しがないものと2つ以上あるものは、1つの一覧にまとめて終了コード2で止める。"""
    cache = {}
    texts = {}
    missing = []
    for s in table["sections"]:
        path = os.path.join(body, s["file"])
        if s["file"] not in cache:
            cache[s["file"]] = split_lines(read_text(path)) if os.path.isfile(path) else None
        lines = cache[s["file"]]
        if lines is None:
            missing.append("%s: %s がありません" % (s["id"], s["file"]))
            continue
        try:
            a, b = find_section(lines, s["heading"])
        except HeadingError as e:
            missing.append("%s: %s > %s（%s）" % (s["id"], s["file"], " > ".join(s["heading"]), e.args[0]))
            continue
        texts[s["id"]] = "".join(lines[a:b])
    if missing:
        raise GenError(2, "抽出表が指す見出しが本体にないか、2つ以上あって節を決められません。生成を止めます。\n" +
                       "\n".join("  - " + m for m in missing))
    return texts


def instruction_of(table, texts):
    parts = []
    for p in table["pieces"]:
        parts.append(section_body(texts[p["section"]]) if p["kind"] == "verbatim" else p["text"])
    text = "".join(parts)
    errs = []
    if "\n" in text or "\r" in text:
        errs.append("指示文が1段落になっていません（改行があります）")
    if len(text) > MAX_CHARS:
        errs.append("指示文が %d 字で、%d 字を超えています" % (len(text), MAX_CHARS))
    if not text.strip():
        errs.append("指示文が空です")
    if errs:
        raise GenError(4, "\n".join(errs))
    return text


def body_size(path):
    """本体の SKILL.md の字数。UTF-8 で読んだファイル全体（先頭の YAML を含む、改行も1字）の len。"""
    with open(path, "rb") as f:
        return len(f.read().decode("utf-8"))


def size_label(n):
    return "{:,}字".format(n)


def build_manifest(table, instruction, skill_chars):
    body = table["body"]
    return {
        "format": MANIFEST_FORMAT,
        "format_version": MANIFEST_FORMAT_VERSION,
        "release": table["release"],
        "body": {k: body[k] for k in ("repository", "version", "tag", "commit")},
        "body_skill": {"file": VERSION_FILE, "characters": skill_chars},
        "instruction": {
            "file": "pocket.txt",
            "characters": len(instruction),
            "sha256": sha256_text(instruction),
        },
        "sections": [{"id": s["id"], "file": s["file"], "heading": s["heading"], "sha256": s["sha256"]}
                     for s in table["sections"]],
        "pieces": [{"id": p["id"], "kind": p["kind"], "role": p["role"], "sources": piece_sources(p)}
                   for p in table["pieces"]],
    }


def cell(text):
    return text.replace("|", "\\|").replace("\n", " ")


def build_sources(table, texts):
    body = table["body"]
    secs = {s["id"]: s for s in table["sections"]}
    kind_ja = {"rewritten": "書き直し", "verbatim": "そのまま"}
    role_ja = {"output": "返し方", "meaning": "意味を守る", "style": "直す型", "restraint": "直さないもの"}
    out = [
        "# 指示文の出どころ",
        "",
        "<!-- このファイルは tools/generate.py が作ります。手で直さず、extract/table.json を直して作り直してください。 -->",
        "",
        "版 %s。本体 %s のタグ %s（コミット %s）の節から作りました。" % (
            table["release"], body["repository"], body["tag"], body["commit"]),
        "",
        "## 文ごとの出どころ",
        "",
        "| 番号 | 文 | 種類 | 役割 | 本体の見出し |",
        "|---|---|---|---|---|",
    ]
    for p in table["pieces"]:
        text = section_body(texts[p["section"]]) if p["kind"] == "verbatim" else p["text"]
        where = "<br>".join("%s（%s）" % (cell(heading_label(secs[s])), s) for s in piece_sources(p))
        out.append("| %s | %s | %s | %s（%s） | %s |" % (
            p["id"], cell(text), kind_ja[p["kind"]], role_ja[p["role"]], p["role"], where))
    out += ["", "## 指した節", "", "| 節 | 本体の見出し | 中身の sha256 |", "|---|---|---|"]
    for s in table["sections"]:
        out.append("| %s | %s | `%s` |" % (s["id"], cell(heading_label(s)), s["sha256"]))
    return "\n".join(out) + "\n"


def region_marks(name):
    return "<!-- pocket:%s:begin -->" % name, "<!-- pocket:%s:end -->" % name


def region_re(name):
    begin, end = region_marks(name)
    return re.compile("(%s)(.*?)(%s)" % (re.escape(begin), re.escape(end)), re.S)


def build_readme(readme, table, instruction, skill_chars):
    """README の印のあいだを埋める。instruction は行の塊、body-size と body-size-row は文の中に置く。
    生成元の本体の版とコミットは README には書かず、MANIFEST.json と SOURCES.md に書く。"""
    body = table["body"]
    size = "%sの SKILL.md（%s）" % (size_label(skill_chars), body["tag"])
    fills = {
        "instruction": "\n```text\n" + instruction + "\n```\n",
        "body-size": size,
        "body-size-row": size,
    }
    for name in README_REGIONS:
        begin, end = region_marks(name)
        rx = region_re(name)
        if readme.count(begin) != 1 or readme.count(end) != 1 or len(rx.findall(readme)) != 1:
            raise GenError(5, "README.md に %s と %s の組が1つずつありません" % (begin, end))
        readme = rx.sub(lambda m, f=fills[name]: m.group(1) + f + m.group(3), readme)
    return readme


def generate(repo, body, accept=False, log=None):
    """生成物を {相対パス: 中身} で返す。抽出表を書き直すときは、その中身も入れる。"""
    log = log or (lambda msg: print(msg, file=sys.stderr))
    table = load_table(repo)
    tb = table["body"]
    skill = os.path.join(body, VERSION_FILE)
    if not os.path.isfile(skill):
        raise GenError(5, "本体に %s がありません: %s" % (VERSION_FILE, body))
    skill_text = read_text(skill)
    version = body_version(skill_text)
    if version != tb["version"]:
        raise GenError(5, "本体の版が抽出表と違います: 本体 %s、抽出表 %s。抽出表の body と release を直してから作り直します。"
                       % (version, tb["version"]))
    table_changed = False
    head = git_head(body)
    if head is None:
        log("注: 本体は git のチェックアウトではないので、コミットは比べません（抽出表のコミット %s を使います）。"
            % tb["commit"])
    elif head != tb["commit"]:
        if not accept:
            raise GenError(5, "本体のコミットが抽出表と違います: 本体 %s、抽出表 %s。"
                              "見直したうえで --accept-changes を付けると書き直します。" % (head, tb["commit"]))
        log("本体のコミットを書き直します: %s -> %s" % (tb["commit"], head))
        tb["commit"] = head
        table_changed = True

    texts = read_sections(table, body)
    changed = []
    for s in table["sections"]:
        new = sha256_text(texts[s["id"]])
        if s.get("sha256") != new:
            changed.append((s, s.get("sha256") or "（なし）", new))
    if changed:
        lines = ["%s  %s\n      前 %s\n      今 %s" % (s["id"], heading_label(s), old, new) for s, old, new in changed]
        if not accept:
            raise GenError(3, "見直しが必要な節（中身のハッシュが抽出表と違います）:\n" + "\n".join("  " + l for l in lines) +
                           "\n節を読み、指示文の部分を見直してから --accept-changes で書き直します。")
        log("見直しが必要な節のハッシュを書き直します:\n" + "\n".join("  " + l for l in lines))
        for s, _, new in changed:
            s["sha256"] = new
        table_changed = True

    instruction = instruction_of(table, texts)
    skill_chars = body_size(skill)
    readme_path = os.path.join(repo, "README.md")
    try:
        readme_text = read_text(readme_path)
    except OSError as e:
        raise GenError(5, "README.md を読めません: %s (%s)" % (readme_path, e))
    readme = build_readme(readme_text, table, instruction, skill_chars)
    files = {
        "pocket.txt": instruction + "\n",
        "MANIFEST.json": dump_json(build_manifest(table, instruction, skill_chars)),
        "SOURCES.md": build_sources(table, texts),
        "README.md": readme,
    }
    if table_changed:
        files[TABLE_PATH] = dump_json(table)
    return files


def write_files(root, files):
    for rel, text in sorted(files.items()):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "wb") as f:
            f.write(text.encode("utf-8"))


def check_files(root, files):
    """生成物とディスクのファイルを比べ、違うものの相対パスを返す。"""
    diff = []
    for rel, text in sorted(files.items()):
        path = os.path.join(root, rel)
        try:
            with open(path, "rb") as f:
                same = f.read() == text.encode("utf-8")
        except OSError:
            same = False
        if not same:
            diff.append(rel)
    return diff


def main(argv=None):
    ap = argparse.ArgumentParser(description="抽出表と本体から pocket の指示文を作る")
    ap.add_argument("--body", required=True, help="本体（nanaism/yomiyasu）のチェックアウトか、その木")
    ap.add_argument("--check", action="store_true", help="書かずに、リポジトリのファイルが生成物と同じかを確かめる")
    ap.add_argument("--accept-changes", action="store_true",
                    help="節のハッシュと本体のコミットの違いを受け入れ、抽出表を書き直す")
    ap.add_argument("--out", help="生成物をこのフォルダに書く（抽出表を書き直すときも、ここの extract/ に書く）")
    a = ap.parse_args(argv)
    if a.check and a.accept_changes:
        ap.error("--check と --accept-changes は一緒に使えません")
    body = os.path.abspath(a.body)
    if not os.path.isdir(body):
        print("本体のフォルダがありません: " + body, file=sys.stderr)
        return 5
    try:
        files = generate(REPO, body, accept=a.accept_changes)
    except GenError as e:
        print(e.message, file=sys.stderr)
        return e.code
    if a.check:
        diff = check_files(os.path.abspath(a.out) if a.out else REPO, files)
        if diff:
            print("生成物と違うファイルがあります: " + "、".join(diff), file=sys.stderr)
            print("python3 tools/generate.py --body <本体> で作り直してください。", file=sys.stderr)
            return 1
        print("生成物と同じです（%s）" % "、".join(sorted(files)))
        return 0
    root = os.path.abspath(a.out) if a.out else REPO
    write_files(root, files)
    print("書きました: %s（%s）" % ("、".join(sorted(files)), root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
