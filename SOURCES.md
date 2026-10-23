# 指示文の出どころ

<!-- このファイルは tools/generate.py が作ります。手で直さず、extract/table.json を直して作り直してください。 -->

版 1.0.0。本体 https://github.com/nanaism/yomiyasu のタグ v2.2.2（コミット 488dd37c0baa67ec65bf155aced9fa1a01d261e2）の節から作りました。

## 文ごとの出どころ

| 番号 | 文 | 種類 | 役割 | 本体の見出し |
|---|---|---|---|---|
| T1 | 次の文章を、意味を変えずに読みやすい日本語に書き直してください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01） |
| T2 | 書き直した本文だけを返し、説明や前置きは付けないでください。 | 書き直し | 返し方（output） | skills/yomiyasu/SKILL.md > 3. 出力フォーマット（S13）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文（S03） |
| T3 | 主張、比重、文の働き（事実、意見、依頼、問い、予定）、言い切りの強さ（推量、可能、許可、義務）、数値と数え方、固有名詞、日付、条件、否定は変えないでください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し（S05） |
| T4 | 原文にない情報、理由、主語、例は足さず、文も削らないでください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報の不増補（足さない）（S02）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり）（S09） |
| T5 | 分からない所は推測で埋めず、原文のまま残してください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文（S03） |
| T6 | 文体（です・ます、だ・である）、見出しや箇条書きの数と順、かぎかっこの中の言葉も保ってください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文書の立場と文末（S04）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し（S05） |
| T7 | 物や概念を人のように動かす比喩、英語を一語ずつ写した言い回し、本文に出てこない比喩の見出し、「重要なのは」のような前置き、意味の増えない「AではなくB」、絵文字、ダッシュ、文末のコロン、間を作るだけの読点など、AIらしい言い回しはふつうの言葉に直してください。 | 書き直し | 直す型（style） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 擬人化の解消（S06）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化（S07）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し（S05）<br>skills/yomiyasu/references/calques.md > 1. 3つの型（S16）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 案内用の見出し（S14）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > セルフラベリングと否定対比の整理（S08）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 装飾記号の排除と太字の表示（S10）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 文長と読点の調整（S11） |
| T10 | 文末の「と言えるでしょう」は、「〜に当たる」のような区分の判断でなければ「でしょう」にしてください。 | 書き直し | 直す型（style） | skills/yomiyasu/references/slop-catalog.md > 6. 不要な前置きと定型の結び（S15） |
| T8 | ただし、「仕様変更が」を「仕様が変わると」にするような、つながりを変える書き換えはしないでください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり）（S09）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01） |
| T9 | 自然な文と慣用句も直さないでください。 | 書き直し | 直さないもの（restraint） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化（S07）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > コピー調の抑制（S12） |

## 指した節

| 節 | 本体の見出し | 中身の sha256 |
|---|---|---|
| S01 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持 | `0800c0509f2091bd6334c1d0f9262775975c36d4db5993dda4971c94704f0e34` |
| S02 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報の不増補（足さない） | `068277e35d9aba246bbae82952004186a4623bb6e4dd4e9cf1d2551768f1edaa` |
| S03 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文 | `cb26196f3bfedffdd877bf493fdcafb686b02ec926d75bf0a1cfd98aa391e40d` |
| S04 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文書の立場と文末 | `d2fb3178181c7fa3b38ddf8ee70d260ccafba3cbf32cac4be953a346a7cfb25d` |
| S05 | skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 文章の書き直し | `be2fb98d62598fbf1c427daca8f906ac481591c47f280fb4880798dce303a709` |
| S06 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 擬人化の解消 | `0a7a6511091da1f1d44bd4b1dca85a4b15534e80d3d8e8ccbb6b2e9611528318` |
| S07 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化 | `66a238b41b4d7e796817dff940ad26096c992bb353121a8a490358fe7ca0442f` |
| S08 | skills/yomiyasu/SKILL.md > 1. 基本原則 > セルフラベリングと否定対比の整理 | `46c5c71d9b0495d2e1b34fc147cf51dc38c2f064fba90f05e716460e26373fea` |
| S09 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり） | `1a0894b31e82e94c8f183903268683f0ec623f60116b4a41067f8e6f0308499a` |
| S10 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 装飾記号の排除と太字の表示 | `d2073d0308bd924e4a3dcf01df44f5ea09b78c5ba3d2450f1352470e843608fa` |
| S11 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文長と読点の調整 | `189dbb2078e0deea3524cb322bafe3a996150f968398fb8a187f584e0ad4220c` |
| S12 | skills/yomiyasu/SKILL.md > 1. 基本原則 > コピー調の抑制 | `1f18c57dc3cdf9ede4f08b9384741813b9b9a001a64406e14c988bc9356372a3` |
| S13 | skills/yomiyasu/SKILL.md > 3. 出力フォーマット | `ce3964e1841429d960e0e377b7e0c852c96fec4db85cbe8c5ba9801e8ad448cc` |
| S14 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 案内用の見出し | `3eac75ee670c976cda05206eed702d42417abb135e034fef30f18c804bf586aa` |
| S15 | skills/yomiyasu/references/slop-catalog.md > 6. 不要な前置きと定型の結び | `7309fa3c13efbaa92c4823cf3102a7d2c4f439aff7bb78c371c5ef014333d922` |
| S16 | skills/yomiyasu/references/calques.md > 1. 3つの型 | `b7c31c85c2c4885b301c3ae8d876b4b989a3ede58dcab8c9e3f0dddf2c4b99cb` |
