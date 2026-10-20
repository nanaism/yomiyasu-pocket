# 測定のスクリプト

本体（yomiyasu v2.1.1）と pocket の指示文に、同じ原稿を同じモデルと設定で推敲させ、本体 v2.1.1 の検査で数えるためのスクリプトです。Python の標準ライブラリだけを使います。

## 測る条件

- 推敲させる道具: Codex CLI（`codex exec`）
- モデル: gpt-6-astra
- effort: high（`-c model_reasoning_effort="high"`）
- service_tier: ultrafast（`-c service_tier="ultrafast"`）
- 原稿: 本体 v2.1.1 の `tests/corpus/` の `raw_ai/`、`blacklist_ai/`、`edge_cases/`、`human/` の `.md`（115本）
- 指示文の候補: `../variants.json`（`P0` がいまの指示文と同じ文です）

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
