"""tools/generate.py と生成物の試験。

動かし方: python3 -m unittest discover -s tests
本体を使う試験は、環境変数 BODY_DIR（既定は ./body）に本体のチェックアウトを置いたときだけ動き、
ないときは理由を出して飛ばす。小さな作りものの本体を使う試験は、本体がなくても動く。
標準ライブラリだけ。
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(REPO, "tools", "generate.py")
BODY = os.path.abspath(os.environ.get("BODY_DIR") or os.path.join(REPO, "body"))
SKILL_REL = os.path.join("skills", "yomiyasu", "SKILL.md")
GENERATED = ("pocket.txt", "MANIFEST.json", "SOURCES.md", "README.md")

# 指示文に入っていなければならない決まりの一覧（決まりの名前、守る部分の role、その部分の文に合う正規表現）。
# 正規表現は文末まで含めて、打ち消しや保つ言い方の文末が変わったら落ちるようにする。
# 部分は1文ずつなので、[^。]* で文の外にはみ出さない。決まりを足すときも、部分の文を書き直すときも、ここを直す。
REQUIRED_RULES = [
    ("意味を変えない", "meaning", r"意味を変えずに[^。]*ください。$"),
    ("文の働き（問いを含む）を保つ", "meaning", r"文の働き（[^）]*問い[^）]*）[^。]*変えません。$"),
    ("言い切りの強さを保つ", "meaning", r"言い切りの強さ[^。]*変えません。$"),
    ("数値を保つ", "meaning", r"数値[^。]*変えません。$"),
    ("条件を保つ", "meaning", r"条件[^。]*変えません。$"),
    ("否定を保つ", "meaning", r"否定[^。]*変えません。$"),
    ("情報を足さない", "meaning", r"原文にない情報[^。]*足さず[^。]*ません。$"),
    ("文を削らない", "meaning", r"文も削りません。$"),
    ("分からない所を推測で埋めない", "meaning", r"推測で埋めず[^。]*残します。$"),
    ("文体と見出しや箇条書きの数と順を保つ", "meaning", r"文体[^。]*見出しや箇条書きの数と順[^。]*保ちます。$"),
    ("かぎかっこの中の言葉を保つ", "meaning", r"かぎかっこの中の言葉[^。]*保ちます。$"),
    ("つながりを変えない", "meaning", r"つながりを変える書き換え[^。]*しません。$"),
    ("本文だけを返す", "output", r"本文だけ[^。]*付けません。$"),
    ("AIらしい言い回しを直す", "style", r"AIらしい言い回し[^。]*直します。$"),
    ("自然な文と慣用句は直さない", "restraint", r"自然な文と慣用句[^。]*直しません。$"),
]

# README に書かないもの。指示文の部分（生成する印のあいだ）は指示文そのものなので、除いてから探す
# （指示文の「文の働き（事実、意見、依頼、予定）」は、今後の予定を書いたものではない）。
README_FORBIDDEN = [
    ("claude.ai", re.compile(r"claude\.ai", re.I)),
    ("未確認", re.compile(r"未確認")),
    ("確かめていません", re.compile(r"確かめていません")),
    ("日付 YYYY-MM-DD", re.compile(r"\d{4}-\d{1,2}-\d{1,2}")),
    ("日付 YYYY年M月", re.compile(r"\d{4}\s*年\s*\d{1,2}\s*月")),
    ("日付 M月D日", re.compile(r"\d{1,2}\s*月\s*\d{1,2}\s*日")),
    ("Co-Authored-By", re.compile(r"co-authored-by", re.I)),
    ("ここに書きます", re.compile(r"ここに書きます")),
    ("予定", re.compile(r"予定")),
    ("今後", re.compile(r"今後")),
    ("いずれ", re.compile(r"いずれ(?![もか])")),  # 「いずれも」「いずれか」は今後の話ではない
    ("近日", re.compile(r"近日")),
]


def region(text, name):
    """README の生成する印のあいだの中身。組が1つでなければ None。"""
    found = G.region_re(name).findall(text)
    return found[0][1] if len(found) == 1 else None


def readme_without_instruction(text):
    return G.region_re("instruction").sub("", text)

MIT_LINES = [
    "MIT License",
    "Copyright (c) 2026 nanaism",
    "Permission is hereby granted, free of charge, to any person obtaining a copy",
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR',
]


def load_generate():
    spec = importlib.util.spec_from_file_location("pocket_generate", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = load_generate()


def read(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(text.encode("utf-8"))


def run_gen(args, gen=GEN):
    p = subprocess.run([sys.executable, "-B", gen] + args, capture_output=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    return p.returncode, p.stdout.decode("utf-8"), p.stderr.decode("utf-8")


def have_body():
    return os.path.isfile(os.path.join(BODY, SKILL_REL))


def need_body(test):
    if not have_body():
        test.skipTest("本体のチェックアウトがないので飛ばします: BODY_DIR=%s（%s がありません）。"
                      "git clone --depth 1 --branch v2.1.1 https://github.com/nanaism/yomiyasu body で置けます。"
                      % (BODY, SKILL_REL))


def table():
    return json.loads(read(os.path.join(REPO, "extract", "table.json")))


def copy_body_files(dst):
    """抽出表が指すファイルだけを本体から写す（本体の木は大きいので全部は写さない）。"""
    files = {s["file"] for s in table()["sections"]} | {G.VERSION_FILE}
    for rel in files:
        target = os.path.join(dst, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(os.path.join(BODY, rel), target)


def copy_repo(dst):
    """試験で抽出表を書き直してよいように、このリポジトリを写す（.git と body は写さない）。"""
    shutil.copytree(REPO, dst, ignore=shutil.ignore_patterns(".git", "body", "__pycache__", "*.pyc"))


class RealBodyTest(unittest.TestCase):
    """本体 v2.1.1 から作る試験。"""

    def setUp(self):
        need_body(self)
        self.tmp = tempfile.mkdtemp(prefix="pocket-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_check_matches_committed_files(self):
        code, out, err = run_gen(["--body", BODY, "--check"])
        self.assertEqual(code, 0, err)

    def test_generation_is_deterministic(self):
        a, b = os.path.join(self.tmp, "a"), os.path.join(self.tmp, "b")
        for d in (a, b):
            code, out, err = run_gen(["--body", BODY, "--out", d])
            self.assertEqual(code, 0, err)
        for name in GENERATED:
            with open(os.path.join(a, name), "rb") as fa, open(os.path.join(b, name), "rb") as fb:
                self.assertEqual(fa.read(), fb.read(), name)
            with open(os.path.join(a, name), "rb") as fa, open(os.path.join(REPO, name), "rb") as fr:
                self.assertEqual(fa.read(), fr.read(), name + " がリポジトリのものと違う")
        self.assertFalse(os.path.exists(os.path.join(a, "extract")), "ハッシュが合うときは抽出表を書かない")

    def test_missing_heading_stops(self):
        body = os.path.join(self.tmp, "body")
        copy_body_files(body)
        skill = os.path.join(body, SKILL_REL)
        text = read(skill)
        self.assertIn("\n### 情報の不増補（足さない）\n", text)
        write(skill, text.replace("\n### 情報の不増補（足さない）\n", "\n"))
        out_dir = os.path.join(self.tmp, "out")
        code, out, err = run_gen(["--body", body, "--out", out_dir])
        self.assertEqual(code, 2, err)
        self.assertIn("情報の不増補（足さない）", err)
        self.assertIn("S02", err)
        self.assertFalse(os.path.exists(out_dir), "止まったときは何も書かない")

    def changed_body(self):
        """S03 の節の中の1行を変えた本体の写しを作る。"""
        body = os.path.join(self.tmp, "body")
        copy_body_files(body)
        skill = os.path.join(body, SKILL_REL)
        lines = read(skill).split("\n")
        i = lines.index("### 情報が足りない場合の暫定文")
        j = next(k for k in range(i + 1, len(lines)) if lines[k].strip())
        lines[j] += "（試験で足した語）"
        write(skill, "\n".join(lines))
        return body

    def test_changed_section_is_listed(self):
        body = self.changed_body()
        out_dir = os.path.join(self.tmp, "out")
        code, out, err = run_gen(["--body", body, "--out", out_dir])
        self.assertEqual(code, 3, err)
        self.assertIn("見直しが必要な節", err)
        self.assertIn("S03", err)
        self.assertIn("情報が足りない場合の暫定文", err)
        self.assertNotIn("S01 ", err)
        self.assertFalse(os.path.exists(out_dir), "止まったときは何も書かない")

    def test_accept_changes_rewrites_hashes(self):
        body = self.changed_body()
        repo = os.path.join(self.tmp, "repo")
        copy_repo(repo)
        before = json.loads(read(os.path.join(repo, "extract", "table.json")))
        code, out, err = run_gen(["--body", body, "--accept-changes"], gen=os.path.join(repo, "tools", "generate.py"))
        self.assertEqual(code, 0, err)
        after = json.loads(read(os.path.join(repo, "extract", "table.json")))
        old = {s["id"]: s["sha256"] for s in before["sections"]}
        new = {s["id"]: s["sha256"] for s in after["sections"]}
        self.assertNotEqual(old["S03"], new["S03"])
        self.assertEqual({k: v for k, v in old.items() if k != "S03"}, {k: v for k, v in new.items() if k != "S03"})
        manifest = json.loads(read(os.path.join(repo, "MANIFEST.json")))
        self.assertEqual({s["id"]: s["sha256"] for s in manifest["sections"]}, new)
        code, out, err = run_gen(["--body", body, "--check"], gen=os.path.join(repo, "tools", "generate.py"))
        self.assertEqual(code, 0, err)
        # 元のリポジトリの抽出表は変わっていない
        self.assertEqual(json.loads(read(os.path.join(REPO, "extract", "table.json"))), before)

    def test_body_version_matches_table(self):
        self.assertEqual(G.body_version(read(os.path.join(BODY, SKILL_REL))), table()["body"]["version"])

    def test_readme_body_size_is_len_of_body_skill(self):
        n = len(read(os.path.join(BODY, SKILL_REL)))
        readme = read(os.path.join(REPO, "README.md"))
        tag = table()["body"]["tag"]
        for name in ("body-size", "body-size-row"):
            self.assertEqual(region(readme, name), "{:,}字の SKILL.md（{}）".format(n, tag), name)
        manifest = json.loads(read(os.path.join(REPO, "MANIFEST.json")))
        self.assertEqual(manifest["body_skill"], {"file": "skills/yomiyasu/SKILL.md", "characters": n})


class CommittedFilesTest(unittest.TestCase):
    """リポジトリに置いた生成物の試験。本体がなくても動く。"""

    def setUp(self):
        self.table = table()
        self.instruction = read(os.path.join(REPO, "pocket.txt"))

    def test_instruction_is_short_single_paragraph(self):
        self.assertTrue(self.instruction.endswith("\n"))
        text = self.instruction[:-1]
        self.assertNotIn("\n", text)
        self.assertNotIn("\r", text)
        self.assertLessEqual(len(text), 400)
        self.assertGreater(len(text.strip()), 0)

    def piece_texts(self):
        """部分の (role, 文) の並び。verbatim の文は本体がないと分からないので、そのときは飛ばす。"""
        out = []
        for p in self.table["pieces"]:
            if p["kind"] != "rewritten":
                self.skipTest("verbatim の部分があるので、決まりの試験は rewritten の部分だけでは確かめられません")
            out.append((p["role"], p["text"]))
        return out

    def test_instruction_has_required_rules(self):
        pieces = self.piece_texts()
        for name, role, pattern in REQUIRED_RULES:
            hits = [t for r, t in pieces if r == role and re.search(pattern, t)]
            self.assertTrue(hits, "role %s の部分に「%s」の文（%s）がない" % (role, name, pattern))
            for t in hits:
                self.assertIn(t, self.instruction)

    def test_every_meaning_and_output_piece_is_a_required_rule(self):
        # 意味を守る部分と返し方の部分は、どれも REQUIRED_RULES のどれかの文に合う（ゆるい文を残さない）
        for role, text in self.piece_texts():
            if role in ("meaning", "output"):
                self.assertTrue(any(r == role and re.search(pat, text) for _, r, pat in REQUIRED_RULES),
                                "REQUIRED_RULES に合わない %s の部分: %s" % (role, text))

    def test_every_piece_has_a_role(self):
        for p in self.table["pieces"]:
            self.assertIn(p.get("role"), G.ROLES, p["id"])
        self.assertEqual([p["id"] for p in self.table["pieces"] if p["role"] == "output"], ["T2"])
        self.assertEqual([p["id"] for p in self.table["pieces"] if p["role"] == "restraint"], ["T10"])

    def test_instruction_equals_pieces(self):
        pieces = self.table["pieces"]
        if any(p["kind"] != "rewritten" for p in pieces):
            self.skipTest("verbatim の部分があるので、本体を使う試験で確かめます")
        self.assertEqual(self.instruction, "".join(p["text"] for p in pieces) + "\n")

    def test_release_format(self):
        self.assertRegex(self.table["release"], r"^\d+\.\d+\.\d+-r\d+$")
        self.assertTrue(self.table["release"].startswith(self.table["body"]["version"] + "-r"))

    def test_body_commit_is_recorded_everywhere(self):
        commit = self.table["body"]["commit"]
        self.assertRegex(commit, r"^[0-9a-f]{40}$")
        manifest = json.loads(read(os.path.join(REPO, "MANIFEST.json")))
        self.assertEqual(manifest["body"]["commit"], commit)
        self.assertEqual(manifest["release"], self.table["release"])
        self.assertIn(commit, read(os.path.join(REPO, "README.md")))
        self.assertIn(commit, read(os.path.join(REPO, "SOURCES.md")))

    def test_manifest_describes_instruction(self):
        manifest = json.loads(read(os.path.join(REPO, "MANIFEST.json")))
        text = self.instruction[:-1]
        self.assertEqual(manifest["instruction"]["characters"], len(text))
        self.assertEqual(manifest["instruction"]["sha256"], hashlib.sha256(text.encode("utf-8")).hexdigest())

    def test_pieces_have_existing_sources(self):
        ids = {s["id"] for s in self.table["sections"]}
        for p in self.table["pieces"]:
            srcs = G.piece_sources(p)
            self.assertTrue(srcs, p["id"])
            for s in srcs:
                self.assertIn(s, ids, p["id"])

    def test_sections_have_hashes(self):
        for s in self.table["sections"]:
            self.assertRegex(s["sha256"], r"^[0-9a-f]{64}$", s["id"])
            self.assertTrue(all(h.lstrip().startswith("#") for h in s["heading"]), s["id"])

    def test_table_is_valid(self):
        G.check_table(self.table)

    def test_license_is_mit(self):
        lic = read(os.path.join(REPO, "LICENSE"))
        for line in MIT_LINES:
            self.assertIn(line, lic)

    def test_readme_has_no_forbidden_content(self):
        readme = readme_without_instruction(read(os.path.join(REPO, "README.md")))
        for name, rx in README_FORBIDDEN:
            self.assertIsNone(rx.search(readme), "README に「%s」がある" % name)
        self.assertIn("\n## 測った結果\n", readme)
        self.assertIn("(./measurements/README.md)", readme)

    def test_readme_body_size_matches_manifest(self):
        readme = read(os.path.join(REPO, "README.md"))
        manifest = json.loads(read(os.path.join(REPO, "MANIFEST.json")))
        want = "{:,}字の SKILL.md（{}）".format(manifest["body_skill"]["characters"], manifest["body"]["tag"])
        for name in ("body-size", "body-size-row"):
            self.assertEqual(region(readme, name), want, name)

    def test_readme_shows_instruction(self):
        readme = read(os.path.join(REPO, "README.md"))
        self.assertIn("```text\n" + self.instruction + "```\n", readme)


class MeasurementsTest(unittest.TestCase):
    """measurements/ に置いた測定の結果の試験。本体がなくても動く。"""

    FINAL = "P2"  # 最終の指示文の候補の名前（measurements/variants.json の鍵）
    RESULT_KEYS = {"cond", "run", "doc", "status", "meaning_risk_count", "risks", "lint_before", "lint_after",
                   "lint_after_rules", "changed_per_1000", "identical", "service_tier"}

    def load(self, name):
        return json.loads(read(os.path.join(REPO, "measurements", name)))

    def test_final_variant_is_the_instruction(self):
        variants = self.load("variants.json")
        self.assertEqual(variants[self.FINAL]["text"] + "\n", read(os.path.join(REPO, "pocket.txt")))
        for name, v in variants.items():
            self.assertTrue(v.get("text") and v.get("note"), name)

    def test_pass_line(self):
        # 合格の線: 最終の候補の意味が変わる恐れが、3回の合計でも1回ずつでも本体を超えない
        summary = self.load("summary.json")
        body = [v for k, v in summary.items() if k.startswith("body/")]
        final = [v for k, v in summary.items() if k.startswith("pocket_%s/" % self.FINAL)]
        self.assertEqual(len(body), 3)
        self.assertEqual(len(final), 3)
        for v in body + final:
            self.assertEqual(v["n"], 115)
            self.assertEqual(v["ok"], 115)
        self.assertLessEqual(sum(v["meaning_risk"] for v in final), sum(v["meaning_risk"] for v in body))
        self.assertLessEqual(max(v["meaning_risk"] for v in final), min(v["meaning_risk"] for v in body))

    def test_pocket_only_risks_are_read(self):
        only = self.load("pocket_only.json")
        self.assertTrue(only)
        for x in only:
            self.assertTrue(x.get("reading", "").strip(), x)

    def test_results_hold_counts_not_texts(self):
        for row in self.load("results.json"):
            self.assertLessEqual(set(row), self.RESULT_KEYS)


# --- 本体がなくても動く、作りものの本体での試験 ---

TINY_SKILL = """---
name: tiny
metadata:
  version: "9.9.9"
---

# tiny

## 1. 基本原則

### 意味

意味を変えない。

#### 細かい点

ここも意味の節に入る。

```markdown
## 2. 手順
### 意味
囲みの中の見出しは数えない。
```

### 足さない

足さない。

## 2. 手順

### 意味

手順の側の意味。

~~~bash
# 囲みの中の見出し
~~~
"""


def tiny_table(pieces=None):
    return {
        "format": "yomiyasu-pocket-extract",
        "format_version": 1,
        "release": "9.9.9-r1",
        "body": {"repository": "https://example.invalid/tiny", "version": "9.9.9", "tag": "v9.9.9",
                 "commit": "0" * 40},
        "sections": [
            {"id": "S01", "file": "skills/yomiyasu/SKILL.md", "heading": ["## 1. 基本原則", "### 意味"], "sha256": ""},
            {"id": "S02", "file": "skills/yomiyasu/SKILL.md", "heading": ["## 1. 基本原則", "### 足さない"],
             "sha256": ""},
            {"id": "S03", "file": "skills/yomiyasu/SKILL.md", "heading": ["## 2. 手順", "### 意味"], "sha256": ""},
        ],
        "pieces": pieces or [
            {"id": "T1", "kind": "rewritten", "role": "meaning", "text": "意味を変えずに直します。", "sources": ["S01"]},
            {"id": "T2", "kind": "rewritten", "role": "meaning", "text": "足しません。", "sources": ["S02", "S03"]},
        ],
    }


TINY_README = """# tiny

<!-- pocket:version:begin -->
<!-- pocket:version:end -->

本体は<!-- pocket:body-size:begin --><!-- pocket:body-size:end -->です。

| 長さ | <!-- pocket:body-size-row:begin -->古い値<!-- pocket:body-size-row:end --> |

<!-- pocket:instruction:begin -->
<!-- pocket:instruction:end -->
"""


class TinyBodyTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pocket-tiny-")
        self.body = os.path.join(self.tmp, "body")
        self.repo = os.path.join(self.tmp, "repo")
        write(os.path.join(self.body, SKILL_REL), TINY_SKILL)
        os.makedirs(os.path.join(self.repo, "tools"))
        shutil.copyfile(GEN, os.path.join(self.repo, "tools", "generate.py"))
        write(os.path.join(self.repo, "README.md"), TINY_README)
        self.set_table(tiny_table())
        self.lines = G.split_lines(TINY_SKILL)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def set_table(self, t):
        write(os.path.join(self.repo, "extract", "table.json"), json.dumps(t, ensure_ascii=False, indent=2) + "\n")

    def gen(self, *args):
        return run_gen(["--body", self.body] + list(args), gen=os.path.join(self.repo, "tools", "generate.py"))

    def section(self, path):
        a, b = G.find_section(self.lines, path)
        return "".join(self.lines[a:b])

    def test_fenced_headings_are_ignored(self):
        texts = [t for _, _, t in G.headings(self.lines)]
        self.assertNotIn("# 囲みの中の見出し", texts)
        self.assertEqual(texts.count("## 2. 手順"), 1)
        # 囲みの中の「## 2. 手順」で節が切れず、囲みの中の「### 意味」とも取り違えない
        s = self.section(["## 1. 基本原則", "### 意味"])
        self.assertIn("囲みの中の見出しは数えない。", s)
        self.assertTrue(s.endswith("```\n\n"))

    def test_nested_path_picks_the_right_parent(self):
        self.assertIn("意味を変えない。", self.section(["## 1. 基本原則", "### 意味"]))
        self.assertIn("手順の側の意味。", self.section(["## 2. 手順", "### 意味"]))

    def test_section_keeps_deeper_headings(self):
        s = self.section(["## 1. 基本原則", "### 意味"])
        self.assertIn("#### 細かい点", s)
        self.assertNotIn("### 足さない", s)

    def test_missing_heading_raises(self):
        with self.assertRaises(G.HeadingError):
            G.find_section(self.lines, ["## 1. 基本原則", "### ない見出し"])
        with self.assertRaises(G.HeadingError):
            G.find_section(self.lines, ["## 2. 手順", "### 足さない"])

    def test_cli_flow(self):
        code, out, err = self.gen()
        self.assertEqual(code, 3, err)
        code, out, err = self.gen("--accept-changes")
        self.assertEqual(code, 0, err)
        code, out, err = self.gen("--check")
        self.assertEqual(code, 0, err)
        self.assertEqual(read(os.path.join(self.repo, "pocket.txt")), "意味を変えずに直します。足しません。\n")
        readme = read(os.path.join(self.repo, "README.md"))
        self.assertIn("版 9.9.9-r1（本体 v9.9.9、コミット %s から生成）" % ("0" * 40), readme)
        size = "{:,}字の SKILL.md（v9.9.9）".format(len(TINY_SKILL))
        self.assertIn("本体は<!-- pocket:body-size:begin -->%s<!-- pocket:body-size:end -->です。" % size, readme)
        self.assertIn("| 長さ | <!-- pocket:body-size-row:begin -->%s<!-- pocket:body-size-row:end --> |" % size,
                      readme)
        manifest = json.loads(read(os.path.join(self.repo, "MANIFEST.json")))
        self.assertEqual(manifest["body_skill"]["characters"], len(TINY_SKILL))
        self.assertEqual([p["role"] for p in manifest["pieces"]], ["meaning", "meaning"])
        # 手で書き換えると --check が落ちる
        write(os.path.join(self.repo, "pocket.txt"), "違う\n")
        code, out, err = self.gen("--check")
        self.assertEqual(code, 1)
        self.assertIn("pocket.txt", err)
        # 見出しを消すと止まり、何も書かない
        write(os.path.join(self.body, SKILL_REL), TINY_SKILL.replace("### 足さない\n", ""))
        code, out, err = self.gen()
        self.assertEqual(code, 2)
        self.assertIn("### 足さない", err)
        self.assertEqual(read(os.path.join(self.repo, "pocket.txt")), "違う\n")

    def test_version_mismatch_stops(self):
        write(os.path.join(self.body, SKILL_REL), TINY_SKILL.replace('"9.9.9"', '"9.9.10"'))
        code, out, err = self.gen("--accept-changes")
        self.assertEqual(code, 5)
        self.assertIn("9.9.10", err)

    def test_verbatim_piece_takes_section_body(self):
        self.set_table(tiny_table([
            {"id": "T1", "kind": "verbatim", "role": "meaning", "section": "S02"},
            {"id": "T2", "kind": "rewritten", "role": "output", "text": "以上です。", "sources": ["S01"]},
        ]))
        self.assertEqual(self.gen("--accept-changes")[0], 0)
        self.assertEqual(read(os.path.join(self.repo, "pocket.txt")), "足さない。以上です。\n")
        self.assertIn("| T1 | 足さない。 | そのまま | 意味を守る（meaning） |", read(os.path.join(self.repo, "SOURCES.md")))
        # 節の中身が複数の段落だと、1段落の決まりで止まる
        self.set_table(tiny_table([{"id": "T1", "kind": "verbatim", "role": "meaning", "section": "S01"}]))
        code, out, err = self.gen("--accept-changes")
        self.assertEqual(code, 4, err)

    def test_git_commit_is_compared(self):
        if shutil.which("git") is None:
            self.skipTest("git がないので飛ばします")
        env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "t"]):
            subprocess.run(["git", "-C", self.body] + args, check=True, capture_output=True, env=env)
        head = subprocess.run(["git", "-C", self.body, "rev-parse", "HEAD"], check=True, capture_output=True,
                              env=env).stdout.decode().strip()
        code, out, err = self.gen()
        self.assertEqual(code, 5)
        self.assertIn(head, err)
        self.assertEqual(self.gen("--accept-changes")[0], 0)
        t = json.loads(read(os.path.join(self.repo, "extract", "table.json")))
        self.assertEqual(t["body"]["commit"], head)
        self.assertIn(head, read(os.path.join(self.repo, "MANIFEST.json")))
        self.assertEqual(self.gen("--check")[0], 0)

    def test_too_long_instruction_stops(self):
        self.set_table(tiny_table([{"id": "T1", "kind": "rewritten", "role": "meaning", "text": "あ" * 401,
                                    "sources": ["S01"]}]))
        code, out, err = self.gen("--accept-changes")
        self.assertEqual(code, 4)
        self.assertIn("401", err)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "pocket.txt")))

    def test_bad_table_stops(self):
        t = tiny_table()
        t["release"] = "9.9.9"
        t["pieces"][0]["sources"] = ["S99"]
        self.set_table(t)
        code, out, err = self.gen()
        self.assertEqual(code, 5)
        self.assertIn("release", err)
        self.assertIn("S99", err)

    def assert_nothing_written(self):
        for name in ("pocket.txt", "MANIFEST.json", "SOURCES.md"):
            self.assertFalse(os.path.exists(os.path.join(self.repo, name)), name)
        self.assertEqual(read(os.path.join(self.repo, "README.md")), self.readme_before)
        self.assertEqual(json.loads(read(os.path.join(self.repo, "extract", "table.json"))), self.table_before)

    def snapshot(self):
        self.readme_before = read(os.path.join(self.repo, "README.md"))
        self.table_before = json.loads(read(os.path.join(self.repo, "extract", "table.json")))

    def test_piece_without_valid_role_stops(self):
        for role in (None, "", "meaning-ish"):
            pieces = [{"id": "T1", "kind": "rewritten", "text": "意味を変えません。", "sources": ["S01"]}]
            if role is not None:
                pieces[0]["role"] = role
            self.set_table(tiny_table(pieces))
            self.snapshot()
            code, out, err = self.gen("--accept-changes")
            self.assertEqual(code, 5, (role, err))
            self.assertIn("T1: role", err)
            self.assert_nothing_written()

    def test_missing_readme_marker_stops(self):
        for marker in ("<!-- pocket:version:end -->", "<!-- pocket:body-size:begin -->",
                       "<!-- pocket:body-size-row:end -->", "<!-- pocket:instruction:begin -->"):
            write(os.path.join(self.repo, "README.md"), TINY_README.replace(marker, ""))
            self.snapshot()
            code, out, err = self.gen("--accept-changes")
            self.assertEqual(code, 5, (marker, err))
            self.assertIn("README.md", err)
            self.assert_nothing_written()
        # 印が2組あっても止まる
        write(os.path.join(self.repo, "README.md"), TINY_README + "<!-- pocket:body-size:begin --><!-- pocket:body-size:end -->\n")
        self.snapshot()
        self.assertEqual(self.gen("--accept-changes")[0], 5)
        self.assert_nothing_written()

    def test_duplicate_and_missing_headings_are_listed_together(self):
        # 「## 1. 基本原則」の下に「### 足さない」を2つにし、S03 の「## 2. 手順」の「### 意味」を消す
        skill = TINY_SKILL.replace("### 足さない\n\n足さない。\n", "### 足さない\n\n足さない。\n\n### 足さない\n\n重ねた。\n")
        skill = skill.replace("### 意味\n\n手順の側の意味。\n", "手順の側の意味。\n")
        write(os.path.join(self.body, SKILL_REL), skill)
        self.snapshot()
        code, out, err = self.gen("--accept-changes")
        self.assertEqual(code, 2, err)
        self.assertIn("S02", err)
        self.assertIn("見出しが2個あり", err)
        self.assertIn("S03", err)
        self.assertIn("見つからない見出し: ### 意味", err)
        self.assertNotIn("S01:", err)
        self.assert_nothing_written()


# 囲みの扱いを確かめる小さな文書
FENCE_DOC = """# 文書

## 外

`````text
4つ以上の囲みの手前
`````

````markdown
```bash
## 3つの囲みの中の見出し
```
### 4つの囲みの中の見出し
```
````

### 外の下

```not`a fence
## 情報の文字列に ` がある行のあとの見出し

本文。
"""


class FenceTest(unittest.TestCase):

    def setUp(self):
        self.lines = G.split_lines(FENCE_DOC)
        self.texts = [t for _, _, t in G.headings(self.lines)]

    def test_four_backtick_fence_hides_inner_fence_and_headings(self):
        self.assertNotIn("## 3つの囲みの中の見出し", self.texts)
        self.assertNotIn("### 4つの囲みの中の見出し", self.texts)
        # 中の ``` で囲みが閉じず、その後の ``` でも閉じず、```` で閉じる
        self.assertIn("### 外の下", self.texts)
        a, b = G.find_section(self.lines, ["## 外"])
        s = "".join(self.lines[a:b])
        self.assertIn("### 4つの囲みの中の見出し", s)
        self.assertIn("### 外の下", s)
        a, b = G.find_section(self.lines, ["## 外", "### 外の下"])
        self.assertTrue("".join(self.lines[a:b]).startswith("### 外の下\n"))

    def test_backtick_in_info_string_is_not_a_fence(self):
        # 「```not`a fence」は、情報の文字列に ` があるので囲みを開かない。次の行は見出しになる
        self.assertIn("## 情報の文字列に ` がある行のあとの見出し", self.texts)
        self.assertEqual(self.texts, ["# 文書", "## 外", "### 外の下", "## 情報の文字列に ` がある行のあとの見出し"])
        a, b = G.find_section(self.lines, ["## 外"])
        self.assertNotIn("本文。", "".join(self.lines[a:b]))

    def test_tilde_fence_does_not_close_backtick_fence(self):
        lines = G.split_lines("```\n~~~\n## 中\n```\n## 外\n")
        self.assertEqual([t for _, _, t in G.headings(lines)], ["## 外"])


if __name__ == "__main__":
    unittest.main()
