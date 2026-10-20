# 測定のスクリプト

本体（yomiyasu v2.1.1）と pocket の指示文に、同じ原稿を同じモデルと設定で推敲させ、本体 v2.1.1 の検査で数えるためのスクリプトです。測った結果は [../README.md](../README.md) にあります。Python の標準ライブラリだけを使います。

## 測る条件

- 推敲させる道具: Codex CLI（`codex exec`）
- モデル: gpt-6-astra
- effort: high（`-c model_reasoning_effort="high"`）
- service_tier: 既定は指定しない（Codex の既定の速さ）。`--service-tier` か環境変数 `POCKET_SERVICE_TIER` に `default` 以外の値を渡すと、`-c service_tier="<値>"` を付けます
- 原稿: 本体 v2.1.1 の `tests/corpus/` の `raw_ai/`、`blacklist_ai/`、`edge_cases/`、`human/` の `.md`（115本）
- 指示文の候補: `../variants.json`（`Q1` がいまの指示文と同じ文、`P2` は文末を依頼の形にそろえる前の指示文です）

Codex の起動の形は `run.py` の `CODEX_ARGV` にあります。利用者の設定（`--ignore-user-config`）、プラグイン、メモリ、ウェブ検索、同梱と利用者のスキルを外して動かします。

## 準備

1. 本体 v2.1.1 を取り出します。

   ```bash
   git clone --depth 1 --branch v2.1.1 https://github.com/nanaism/yomiyasu body
   ```

2. ふだんの設定と分けた測定用の CODEX_HOME を作り、そこで Codex CLI にログインします。

   ```bash
   mkdir -p /path/to/codex-home && chmod 700 /path/to/codex-home
   CODEX_HOME=/path/to/codex-home codex login
   ```

## 動かし方

推敲させます。結果は `measurements/runs/<条件>/r<回>/<群>/<名前>/` に入ります。

```bash
# 本体: 作業場所の .agents/skills/yomiyasu に本体のスキルを写し、$yomiyasu:yomiyasu で推敲させる
python3 -B measurements/tools/run.py --body-tree body --codex-home /path/to/codex-home --cond body --runs 1,2

# pocket: variants.json の指示文と原稿を1つの依頼にして渡す
python3 -B measurements/tools/run.py --body-tree body --codex-home /path/to/codex-home --cond pocket:P0 --runs 1,2

# 速さを指定して流す
python3 -B measurements/tools/run.py --body-tree body --codex-home /path/to/codex-home --cond pocket:P2 --runs 1 --service-tier ultrafast

# 組の数だけを数える
python3 -B measurements/tools/run.py --body-tree body --plan --cond pocket:P0 --runs 1
```

本体の v2.1.1 の `yomiyasu_diff.py --fail-on meaning-risk` と `yomiyasu_lint.py` で数え、表にします。

```bash
python3 -B measurements/tools/score.py --body-tree body --conds body,pocket_P0
python3 -B measurements/tools/score.py --body-tree body --table --conds body,pocket_P0
```

表は `measurements/runs/table.md` と `table.json` に書かれます。数えるものは次の3つです。

- 意味が変わる恐れ: 元の原稿と書き直した文を `yomiyasu_diff.py --fail-on meaning-risk --json` で比べた件数（`fail_on_meaning_risk_count`）
- 残った候補: 書き直した文を `yomiyasu_lint.py --json` で調べた件数
- 書き換えた量: 原稿の空白を除いた1,000字あたりの、書き換えた字数

`--body-tree` を省くと、環境変数 `BODY_DIR`、それもなければリポジトリの `body/` を使います。`--codex-home` を省くと、環境変数 `CODEX_HOME` を使います。

## まとめ

`aggregate.py` は、`run.py` と `score.py` が `measurements/runs/` に書いた結果から、リポジトリに入れる `results.json`、`summary.json`、`pocket_only.json` を作ります。原稿と書き直した文の全文は入れません。

```bash
python3 -B measurements/tools/aggregate.py --final P2 --runs-dir measurements/runs --out measurements
```

- `--final` は、本体と比べる候補の名前です。本体と3回ずつ比べた `P2` を渡します（いまの指示文は `Q1` です）。`pocket_only.json` には、その候補で出た意味が変わる恐れのうち、同じ原稿で同じ種類の恐れが本体の回のどれにも出ていないものが入ります。
- `--runs-dir` を省くと `measurements/runs/`、`--out` を省くと `measurements/` を使います。
- `--out` にすでに `pocket_only.json` があれば、同じ組（回、原稿、種類、行、元と後の文）の読んだ記録（`reading`）を引き継ぎます。新しく出た組の `reading` は空なので、1件ずつ読んで書きます。
