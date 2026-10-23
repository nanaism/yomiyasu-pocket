"""score.py の結果をまとめ、リポジトリに入れる測定の結果を作る。

使い方: python3 -B measurements/tools/aggregate.py --final C5 [--runs-dir measurements/runs] [--out measurements]
- 入力は run.py と score.py が書いた --runs-dir（既定は measurements/runs）の <条件>/r<回>/<群>/<名前>/ の
  score.json と result.json。
- results.json: 条件・回・原稿ごとの数（意味が変わる恐れの件数と種類、元と後の文、lint の候補の数、書き換えた量、原文のままか）。
  本文そのものは入れない（原稿は本体の tests/corpus にある）。
- summary.json: 条件ごとの合計（回ごと）と、群ごとの数。
- pocket_only.json: 最終の条件で恐れが出た原稿のうち、本体の3回のどれにも同じ種類の恐れがない組の一覧（読んだ記録を
  付けるための元）。同じ原稿・同じ kind/subkind が本体の回のどれかにあれば「本体にもある」とする。
  --out にすでに pocket_only.json があれば、同じ組（回、原稿、種類、行、元と後の文）の reading を引き継ぐ。
標準ライブラリだけ。
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEV = os.path.dirname(HERE)  # measurements/
GROUPS = ("raw_ai", "blacklist_ai", "edge_cases", "human")


def load(root):
    rows = []
    for cond in sorted(os.listdir(root)):
        cd = os.path.join(root, cond)
        if not os.path.isdir(cd) or cond.startswith("."):
            continue
        for run in sorted(os.listdir(cd)):
            for g in GROUPS:
                gd = os.path.join(cd, run, g)
                if not os.path.isdir(gd):
                    continue
                for n in sorted(os.listdir(gd)):
                    p = os.path.join(gd, n, "score.json")
                    if ".failed-" in n or not os.path.exists(p):
                        continue
                    s = json.load(open(p, encoding="utf-8"))
                    res = json.load(open(os.path.join(gd, n, "result.json"), encoding="utf-8"))
                    s["cond"], s["run"] = cond, run
                    s["service_tier"] = res.get("service_tier")
                    s["seconds"] = res.get("seconds")
                    rows.append(s)
    return rows


def only_key(x):
    return tuple(x.get(k) for k in ("run", "doc", "kind", "subkind", "old_line", "new_line", "old", "new"))


def lint_total(c):
    return sum(int(c.get(k, 0)) for k in ("error", "warn", "info"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", required=True, help="最終の pocket の条件の名前（C5 など）")
    ap.add_argument("--runs-dir", default=os.path.join(DEV, "runs"), help="run.py と score.py の結果のフォルダ")
    ap.add_argument("--out", default=DEV, help="results.json、summary.json、pocket_only.json を書くフォルダ")
    a = ap.parse_args()
    if not os.path.isdir(a.runs_dir):
        sys.exit("結果のフォルダがありません: " + a.runs_dir)
    os.makedirs(a.out, exist_ok=True)
    rows = load(a.runs_dir)
    keep = ("cond", "run", "doc", "status", "meaning_risk_count", "risks", "lint_before", "lint_after",
            "lint_after_rules", "changed_per_1000", "identical", "service_tier")
    results = [{k: r.get(k) for k in keep} for r in rows]
    json.dump(results, open(os.path.join(a.out, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    summary = {}
    for r in rows:
        key = r["cond"] + "/" + r["run"]
        s = summary.setdefault(key, {"n": 0, "ok": 0, "meaning_risk": 0, "docs_with_risk": 0, "lint_before": 0,
                                     "lint_after": 0, "lint_after_warn": 0, "identical": 0, "human_change": [],
                                     "groups": {}})
        s["n"] += 1
        if r["status"] != "ok":
            continue
        s["ok"] += 1
        s["meaning_risk"] += r["meaning_risk_count"]
        s["docs_with_risk"] += 1 if r["meaning_risk_count"] else 0
        s["lint_before"] += lint_total(r["lint_before"])
        s["lint_after"] += lint_total(r["lint_after"])
        s["lint_after_warn"] += int(r["lint_after"].get("warn", 0)) + int(r["lint_after"].get("error", 0))
        s["identical"] += 1 if r.get("identical") else 0
        g = r["doc"].split("/")[0]
        gs = s["groups"].setdefault(g, {"n": 0, "meaning_risk": 0, "lint_after": 0})
        gs["n"] += 1
        gs["meaning_risk"] += r["meaning_risk_count"]
        gs["lint_after"] += lint_total(r["lint_after"])
        if g == "human":
            s["human_change"].append(r["changed_per_1000"])
    for s in summary.values():
        ch = sorted(s.pop("human_change"))
        s["human_change_median"] = ch[len(ch) // 2] if ch else None
    json.dump(summary, open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    body = {}
    for r in rows:
        if r["cond"] == "body" and r["status"] == "ok":
            for risk in r["risks"]:
                body.setdefault(r["doc"], set()).add((risk["kind"], risk["subkind"]))
    readings = {}
    only_path = os.path.join(a.out, "pocket_only.json")
    if os.path.exists(only_path):
        with open(only_path, encoding="utf-8") as f:
            for x in json.load(f):
                readings[only_key(x)] = x.get("reading", "")
    only = []
    for r in rows:
        if r["cond"] != "pocket_" + a.final or r["status"] != "ok":
            continue
        for risk in r["risks"]:
            if (risk["kind"], risk["subkind"]) not in body.get(r["doc"], set()):
                only.append({"run": r["run"], "doc": r["doc"], "kind": risk["kind"], "subkind": risk["subkind"],
                             "old_line": risk.get("old_line"), "new_line": risk.get("new_line"),
                             "old": risk.get("old"), "new": risk.get("new"), "reading": ""})
                only[-1]["reading"] = readings.get(only_key(only[-1]), "")
    json.dump(only, open(os.path.join(a.out, "pocket_only.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("rows", len(rows), "pocket_only", len(only))


if __name__ == "__main__":
    main()
