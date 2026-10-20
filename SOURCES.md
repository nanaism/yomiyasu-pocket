# 指示文の出どころ

<!-- このファイルは tools/generate.py が作ります。手で直さず、extract/table.json を直して作り直してください。 -->

版 2.1.1-r1。本体 https://github.com/nanaism/yomiyasu のタグ v2.1.1（コミット fbe02c93877d697cc53d9377b7a45dd8a1dd99b3）の節から作りました。

## 文ごとの出どころ

| 番号 | 文 | 種類 | 役割 | 本体の見出し |
|---|---|---|---|---|
| T1 | 次の文章を、意味を変えずに読みやすい日本語に書き直してください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01） |
| T2 | 返すのは書き直した本文だけにし、説明や前置きは付けません。 | 書き直し | 返し方（output） | skills/yomiyasu/SKILL.md > 3. 出力フォーマット（S13）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文（S03） |
| T3 | 主張、比重、文の働き（事実、意見、依頼、問い、予定）、言い切りの強さ（推量、可能、許可、義務）、数値、固有名詞、日付、条件、否定は変えません。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し（S05） |
| T4 | 原文にない情報、理由、主語、例は足さず、文も削りません。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報の不増補（足さない）（S02）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり）（S09） |
| T5 | 分からない所は推測で埋めず、原文のまま残します。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文（S03） |
| T6 | 文体（です・ます、だ・である）、見出しや箇条書きの数と順、かぎかっこの中の言葉は保ちます。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文書の立場と文末（S04）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し（S05） |
| T7 | AIらしい言い回しはふつうの言葉に直します。 | 書き直し | 直す型（style） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化（S07） |
| T8 | 物や概念を人のように動かす比喩、「重要なのは」のような前置き、意味の増えない「AではなくB」、絵文字、ダッシュ、文末のコロン、間を作るだけの読点です。 | 書き直し | 直す型（style） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 擬人化の解消（S06）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化（S07）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > セルフラベリングと否定対比の整理（S08）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 装飾記号の排除と太字の表示（S10）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 文長と読点の調整（S11） |
| T9 | 「仕様変更が」を「仕様が変わると」にするような、つながりを変える書き換えもしません。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり）（S09）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01） |
| T10 | 自然な文と慣用句は直しません。 | 書き直し | 直さないもの（restraint） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化（S07）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > コピー調の抑制（S12） |

## 指した節

| 節 | 本体の見出し | 中身の sha256 |
|---|---|---|
| S01 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持 | `0800c0509f2091bd6334c1d0f9262775975c36d4db5993dda4971c94704f0e34` |
| S02 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報の不増補（足さない） | `068277e35d9aba246bbae82952004186a4623bb6e4dd4e9cf1d2551768f1edaa` |
| S03 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文 | `cb26196f3bfedffdd877bf493fdcafb686b02ec926d75bf0a1cfd98aa391e40d` |
| S04 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文書の立場と文末 | `d2fb3178181c7fa3b38ddf8ee70d260ccafba3cbf32cac4be953a346a7cfb25d` |
| S05 | skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し | `65164213852ac3195dc2a63a223f722dbb893f0b8158c89d05f6b820d04f0275` |
| S06 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 擬人化の解消 | `0a7a6511091da1f1d44bd4b1dca85a4b15534e80d3d8e8ccbb6b2e9611528318` |
| S07 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化 | `66a238b41b4d7e796817dff940ad26096c992bb353121a8a490358fe7ca0442f` |
| S08 | skills/yomiyasu/SKILL.md > 1. 基本原則 > セルフラベリングと否定対比の整理 | `46c5c71d9b0495d2e1b34fc147cf51dc38c2f064fba90f05e716460e26373fea` |
| S09 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり） | `1a0894b31e82e94c8f183903268683f0ec623f60116b4a41067f8e6f0308499a` |
| S10 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 装飾記号の排除と太字の表示 | `d2073d0308bd924e4a3dcf01df44f5ea09b78c5ba3d2450f1352470e843608fa` |
| S11 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文長と読点の調整 | `189dbb2078e0deea3524cb322bafe3a996150f968398fb8a187f584e0ad4220c` |
| S12 | skills/yomiyasu/SKILL.md > 1. 基本原則 > コピー調の抑制 | `c4a6223395deb516040cb2454febb10f9b99173f6385b5becb423031df96e3b5` |
| S13 | skills/yomiyasu/SKILL.md > 3. 出力フォーマット | `ce3964e1841429d960e0e377b7e0c852c96fec4db85cbe8c5ba9801e8ad448cc` |
