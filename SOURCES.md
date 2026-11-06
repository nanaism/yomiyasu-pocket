# 指示文の出どころ

<!-- このファイルは tools/generate.py が作ります。手で直さず、extract/table.json を直して作り直してください。 -->

バージョン 2.0.0。本体 https://github.com/nanaism/yomiyasu のタグ v3.0.0（コミット e0177404840178cb6dfb648b19b9928380abd04a）の節から作りました。

## 文ごとの出どころ

| 番号 | 文 | 種類 | 役割 | 本体の見出し |
|---|---|---|---|---|
| T1 | 次の文章を意味を変えずに読みやすく書き直してください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01） |
| T2 | 書き直した本文だけを返し、説明や前置きは付けないでください。 | 書き直し | 返し方（output） | skills/yomiyasu/SKILL.md > 3. 出力フォーマット（S13）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文（S03） |
| T3 | 主張、比重、文の働き（事実、意見、依頼、問い、予定）、言い切りの強さ（推量、可能、許可、義務）、数値と数え方、固有名詞、日付、条件、否定は変えないでください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 上から読み、1か所ずつ直す（S05） |
| T4 | 原文にない情報、理由、主語、相手、例は足さず、文も削らないでください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報の不増補（足さない）（S02）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり）（S09）<br>skills/yomiyasu/references/review-points.md > 2. 出力の節ごとの見方 > ■ 原文にない人や担当を足した文（S17） |
| T5 | 分からない所は推測で埋めず、原文のまま残してください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文（S03） |
| T6 | 文体、見出しや箇条書きの数と順、指定の見出しの形、かぎかっこの中、漢語と和語の選び方も保ってください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文書の立場と文末（S04）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 上から読み、1か所ずつ直す（S05）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 案内用の見出し（S14）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 直訳語、漢語の詰まり、連用形名詞（S18） |
| T7 | 物を人のように動かす比喩、英語を一語ずつ写した言い回しや英語の術語に当てた漢字1字（版、頭、印）、本文に出てこない比喩の見出し、「重要なのは」などの前置き、意味の増えない「AではなくB」、絵文字、ダッシュ、間を作るだけの読点など、AIらしい言い回しはふつうの言葉に直し、読点は足さないでください。 | 書き直し | 直す型（style） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化と擬人化の解消（S06）<br>skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 上から読み、1か所ずつ直す（S05）<br>skills/yomiyasu/references/calques.md > 1. 5つの型（S16）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 直訳語、漢語の詰まり、連用形名詞（S18）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 案内用の見出し（S14）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > セルフラベリングと否定対比の整理（S08）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 装飾記号の排除と太字の表示、コピー調の抑制（S10）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 文長と読点の調整（S11） |
| T10 | 文末の「と言えるでしょう」は区分の判断でなければ「でしょう」にしてください。 | 書き直し | 直す型（style） | skills/yomiyasu/references/slop-catalog.md > 6. 不要な前置きと定型の結び（S15） |
| T8 | 「仕様変更が」→「仕様が変わると」のようなつながりを変える書き換えはしないでください。 | 書き直し | 意味を守る（meaning） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり）（S09）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持（S01） |
| T9 | 自然な文と慣用句も直さないでください。 | 書き直し | 直さないもの（restraint） | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化と擬人化の解消（S06）<br>skills/yomiyasu/SKILL.md > 1. 基本原則 > 装飾記号の排除と太字の表示、コピー調の抑制（S10） |

## 指した節

| 節 | 本体の見出し | 中身の sha256 |
|---|---|---|
| S01 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 最優先ルール: 意味の保持 | `52c6574e63857caf2b5e620e9be8e5e9042229d082ca987d6fbabc483c6e0c6c` |
| S02 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報の不増補（足さない） | `f2d11fea8d0ccecfd6cee2b0aad115a149a632ffe81a8d823b364826793b5ff5` |
| S03 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 情報が足りない場合の暫定文 | `6214ec2863886c81f17c28a23e8b772cce88dc9b17135dee9951348c4421be3b` |
| S04 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文書の立場と文末 | `71a6d4ba12250197535377e0080a453155b72c75931dd47292304802a800a88e` |
| S05 | skills/yomiyasu/SKILL.md > 2. 実行手順 > Step 2: 上から読み、1か所ずつ直す | `fd429f84b6a607dfb5f610c4f497115812db53d8793586624ee141fadf9cbf5f` |
| S06 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 比喩動詞の具体化と擬人化の解消 | `4de5c9910caf08142ac7911ea291849657d62962ab0af35a2e836abd0b475975` |
| S08 | skills/yomiyasu/SKILL.md > 1. 基本原則 > セルフラベリングと否定対比の整理 | `6e2c109fc9ba9452bc7655b2f8368157f7d93dc27cc5be6c7283087c8e5a6b40` |
| S09 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 段落と文の論理構造（つながり） | `7e9a8d016ea08e53b3dccea13ef5ef015bc1ef14f5f395b20a356b4100244af1` |
| S10 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 装飾記号の排除と太字の表示、コピー調の抑制 | `73e6bfbcc7a4ae0ded0044dcfe3abdb6c2a43b60bd14b635882c09def82f513c` |
| S11 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 文長と読点の調整 | `288ee70b2ae0213acdfe7a57097825c1f638e943654edd7cee9009b98fdddb53` |
| S13 | skills/yomiyasu/SKILL.md > 3. 出力フォーマット | `e72ef0630db1debbc3677b341ec2e54fbad9f7eb7482d2103ba5815b05d19b15` |
| S14 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 案内用の見出し | `d86479733b86c44addb37d81b9d5caa6c10d0c70208dbf04d0d9319d4993efd9` |
| S15 | skills/yomiyasu/references/slop-catalog.md > 6. 不要な前置きと定型の結び | `cb1f62509fda0215dda7290ef5790fb3933bc834c686248b0809ba1b71e76719` |
| S16 | skills/yomiyasu/references/calques.md > 1. 5つの型 | `31d30b704662c667e72eafca5f96e15c0b14fad47a6af2a0e70c2861ad818d28` |
| S17 | skills/yomiyasu/references/review-points.md > 2. 出力の節ごとの見方 > ■ 原文にない人や担当を足した文 | `cc95e5cba96ab2bc826883e5b67aa3bd2842eaf8620732d759215fad6532bda0` |
| S18 | skills/yomiyasu/SKILL.md > 1. 基本原則 > 直訳語、漢語の詰まり、連用形名詞 | `7dd2542453538902474fa9d729799e07d374ef87a9ef0505143b7bd625e60f9f` |
