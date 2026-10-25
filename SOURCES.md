# 指示文の出どころ

<!-- このファイルは tools/generate.py が作ります。手で直さず、extract/table.json を直して作り直してください。 -->

バージョン 1.1.0。本体 https://github.com/nanaism/yomiyasu のタグ v2.4.0（コミット ae258d7a57b335673e30b88a018ae08d4f72c449）の節から作りました。

## 文ごとの出どころ

| 番号 | 文 | 種類 | 役割 | 本体の見出し |
|---|---|---|---|---|
| T1 | 次の文章を、意味を変えずに読みやすく書き直してください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01） |
| T2 | 書き直した本文だけを返し、説明や前置きは付けないでください。 | 書き直し | 返し方（output） | skills/yomiyasu/SKILL.md > 3. 出力フォーマット（S13）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文（S03） |
| T3 | 主張、比重、文の働き（事実、意見、依頼、問い、予定）、言い切りの強さ（推量、可能、許可、義務）、数値と数え方、固有名詞、日付、条件、否定は変えないでください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し（S05） |
| T4 | 原文にない情報、理由、主語、相手、例は足さず、文も削らないでください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報の不増補（足さない）（S02）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり）（S09）<br>skills/yomiyasu/references/review-points.md > 2. 出力の節ごとの見方 > ■ 原文にない人や担当を足した文（S17） |
| T5 | 分からない所は推測で埋めず、原文のまま残してください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文（S03） |
| T6 | 文体（です・ます、だ・である）、見出しや箇条書きの数と順、かぎかっこの中の言葉も保ってください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文書の立場と文末（S04）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し（S05） |
| T7 | 物を人のように動かす比喩、英語を一語ずつ写した言い回しや英語の術語に当てた漢字1字（版、頭、印）、本文に出てこない比喩の見出し、「重要なのは」などの前置き、意味の増えない「AではなくB」、絵文字、ダッシュ、文末のコロン、間を作るだけの読点など、AIらしい言い回しはふつうの言葉に直してください。 | 書き直し | 直す型（style） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 擬人化の解消（S06）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化（S07）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し（S05）<br>skills/yomiyasu/references/calques.md > 1. 4つの型（S16）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 案内用の見出し（S14）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > セルフラベリングと否定対比の整理（S08）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 装飾記号の排除と太字の表示（S10）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 文長と読点の調整（S11） |
| T10 | 文末の「と言えるでしょう」は、区分の判断でなければ「でしょう」にしてください。 | 書き直し | 直す型（style） | skills/yomiyasu/references/slop-catalog.md > 6. 不要な前置きと定型の結び（S15） |
| T8 | 「仕様変更が」を「仕様が変わると」にするような、つながりを変える書き換えはしないでください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり）（S09）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01） |
| T9 | 自然な文と慣用句も直さないでください。 | 書き直し | 直さないもの（restraint） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化（S07）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > コピー調の抑制（S12） |

## 指した節

| 節 | 本体の見出し | 中身の sha256 |
|---|---|---|
| S01 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持 | `0800c0509f2091bd6334c1d0f9262775975c36d4db5993dda4971c94704f0e34` |
| S02 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報の不増補（足さない） | `068277e35d9aba246bbae82952004186a4623bb6e4dd4e9cf1d2551768f1edaa` |
| S03 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文 | `cb26196f3bfedffdd877bf493fdcafb686b02ec926d75bf0a1cfd98aa391e40d` |
| S04 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文書の立場と文末 | `d2fb3178181c7fa3b38ddf8ee70d260ccafba3cbf32cac4be953a346a7cfb25d` |
| S05 | skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し | `5043e1012fddc34b71fb358a24d3469d5013c389a8b74b7e5671f2b674450f66` |
| S06 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 擬人化の解消 | `0a7a6511091da1f1d44bd4b1dca85a4b15534e80d3d8e8ccbb6b2e9611528318` |
| S07 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化 | `66a238b41b4d7e796817dff940ad26096c992bb353121a8a490358fe7ca0442f` |
| S08 | skills/yomiyasu/SKILL.md > 1. 基本原則 > セルフラベリングと否定対比の整理 | `46c5c71d9b0495d2e1b34fc147cf51dc38c2f064fba90f05e716460e26373fea` |
| S09 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり） | `1c73b283492b1e57503175e3a1a1643c9d9bd30c62199b3ecbc48f7d2785aa1a` |
| S10 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 装飾記号の排除と太字の表示 | `eda74fd0ac7b4e424717e04bb255e003f4098d3016357c484a67aac14d144829` |
| S11 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文長と読点の調整 | `818ec10bb4910e3c14740f40a3d02767f192290d7766c5d33963369c29d99e15` |
| S12 | skills/yomiyasu/SKILL.md > 1. 基本原則 > コピー調の抑制 | `1f18c57dc3cdf9ede4f08b9384741813b9b9a001a64406e14c988bc9356372a3` |
| S13 | skills/yomiyasu/SKILL.md > 3. 出力フォーマット | `484a1de67ea8aa2d6970d2f7c093792dfdfe5b481e2f0f61fe9ae746bb92f5a9` |
| S14 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 案内用の見出し | `ab63ebdb2e9138485bf54bc60c0be31c6fa30ddad3d02ffb258d8cda1fb91ecd` |
| S15 | skills/yomiyasu/references/slop-catalog.md > 6. 不要な前置きと定型の結び | `56688eea0dba4176b6cbf02dcaa9d37ad9e553f11f26b8245665c141418d57ed` |
| S16 | skills/yomiyasu/references/calques.md > 1. 4つの型 | `96f6832c7faa256a7eef9b6d86641a4df3dcf83e08267579731b3593a3034465` |
| S17 | skills/yomiyasu/references/review-points.md > 2. 出力の節ごとの見方 > ■ 原文にない人や担当を足した文 | `cc95e5cba96ab2bc826883e5b67aa3bd2842eaf8620732d759215fad6532bda0` |
