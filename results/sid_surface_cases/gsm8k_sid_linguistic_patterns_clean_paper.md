# Clean SID Linguistic Pattern Cases

This is the paper-facing version of the SID case analysis.

Important correction: selected-vs-original examples can be misleading, because the `original v0` translation is often exactly the corrupted or under-specified variant that the selector avoids. Therefore this report does **not** use `original v0` as a linguistic contrast case.

Instead, it uses collection-level evidence:

- `top-score`: the top 1,319 test variants by aggregate SID-rule score.
- `bottom-score`: the bottom 1,319 test variants by aggregate SID-rule score.
- The comparison asks whether high SID score corresponds to recurring surface-form patterns.

The example questions below are used only as representative high-score surface forms. They were checked against the English GSM8K source for obvious number loss, placeholder residue, and gross semantic mismatch. They should still be reviewed by a native speaker before final camera-ready use.

## Collection-Level Patterns

| lang | top acc | bottom acc | top tokens | bottom tokens | top numbers | bottom numbers | top max-run | bottom max-run | interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `npi_Deva` | 0.591 | 0.096 | 29.6 | 30.7 | 3.5 | 4.1 | 1.0 | 5.4 | High-score questions are less repetitive and use explicit `कति / यदि / प्रत्येक / कुल / प्रति` style quantity framing. |
| `sin_Sinh` | 0.514 | 0.089 | 34.2 | 41.3 | 3.7 | 3.9 | 1.2 | 8.7 | High-score questions enrich total/amount/condition words such as `කොපමණ`, `මුළු`, `නම්`, `සෑම`. |
| `som_Latn` | 0.572 | 0.159 | 35.1 | 41.6 | 3.5 | 3.5 | 1.1 | 7.6 | High-score questions look like regularized price/quantity enumerations with `imisa`, `guud`, `haddii`, `lacag`. |
| `swh_Latn` | 0.682 | 0.271 | 31.5 | 37.9 | 3.3 | 3.6 | 1.0 | 2.5 | Swahili is cleaner overall; high-score questions still enrich `ngapi`, `kiasi`, `ikiwa`, `jumla`, and `kila`. |
| `yor_Latn` | 0.417 | 0.064 | 42.1 | 49.3 | 3.2 | 4.0 | 1.1 | 9.1 | High-score questions are less repetitive and more often use `iye`, `mélòó`, `owó`, `gbogbo` quantity/amount framing. |
| `zul_Latn` | 0.494 | 0.150 | 23.5 | 25.7 | 3.1 | 4.3 | 1.0 | 2.5 | High-score questions favor compact conditional/count phrasing with `uma`, `malini`, `mangaki`, `ngamunye`. |

## High-Score Surface Examples

### Nepali (`npi_Deva`)

Pattern: high-score questions often put the unit price or count relation directly next to the number, and end with a direct `कति` question.

- Target-language surface:
  `6 इरेजर (प्रत्येक $2) र 8 पेन्सिल (प्रत्येक $3) को कुल लागत कति हुन्छ?`
  
  Chinese gloss:
  `6 个橡皮每个 2 美元，8 支铅笔每支 3 美元，总费用是多少？`

- Target-language surface:
  `यदि शैक्षिक पसलले प्रति नोटबुक $1.50 र प्रति बलपेन $0.5 शुल्क लिन्छ भने, र विलियमले पाँचवटा नोटबुक र एक बलपेन किन्छ भने, उसले खर्च गरेको कुल रकम कति हो?`
  
  Chinese gloss:
  `如果文具店每本笔记本 1.50 美元、每支圆珠笔 0.5 美元，William 买了 5 本笔记本和 1 支圆珠笔，总共花了多少钱？`

Why this is a useful case:
the high-score forms explicitly bind quantities to units (`प्रति ...`) and make the requested total (`कुल रकम कति`) local and direct.

### Sinhala (`sin_Sinh`)

Pattern: high-score questions enrich explicit amount/total question words and parenthesized unit values.

- Target-language surface:
  `සෑම සතියකම ග්‍රේසන් ඇලුමිනියම් බඳුන් තුනක් (එකකට සෙන්ට් දෙකක වටිනාකමක්) සහ ප්ලාස්ටික් බෝතල් පහක් (එකකට සෙන්ට් තුනක වටිනාකමක්) ප්‍රතිචක්‍රීකරණය කරයි. සති හතරක මාසයකදී ඇය උපයන මුළු මුදල සෙන්ට් කීයද?`
  
  Chinese gloss:
  `Grayson 每周回收 3 个铝罐（每个 2 美分）和 5 个塑料瓶（每个 3 美分）。四周一个月里，她总共能赚多少美分？`

- Target-language surface:
  `අධ්‍යාපන වෙළඳසැලෙන් එක් එක් $1.50 සඳහා නෝට්බුක් සහ එක් එක් $0.5 සඳහා බෝල පෑන් විකුණයි; විලියම් නෝට්බුක් පහක් සහ එක් බෝල පෑන් එකක් මිලදී ගත්තා, ඉතින් ඔහු මුළු මුදල කොපමණද?`
  
  Chinese gloss:
  `文具店每本笔记本卖 1.50 美元，每支圆珠笔卖 0.5 美元；William 买了 5 本笔记本和 1 支圆珠笔，他总共花了多少钱？`

Why this is a useful case:
the surface form explicitly marks per-item values and total amount, using `එක් එක්`, `මුළු`, and `කොපමණ`.

### Somali (`som_Latn`)

Pattern: high-score questions often use `haddii` conditional framing and `wadarta / guud / imisa` total-amount prompts.

- Target-language surface:
  `Haddii beeraley uu leeyahay 900 ukumo oo uu isticmaalo saxan ay ku jiraan 30 ukumo kasta, saxan walbana uu ku iibiyo $2.5, waa maxay wadarta dakhliga beeraleyda?`
  
  Chinese gloss:
  `如果农民有 900 个鸡蛋，每个托盘装 30 个，每个托盘卖 2.5 美元，他的总收入是多少？`

- Target-language surface:
  `Haddii Terry uu iibiyo 6 milkshakes midkiiba $5.50, sagaal burger midkiiba $11, iyo 20 soda midkiiba $1.50, waa maxay dakhligiisa guud?`
  
  Chinese gloss:
  `如果 Terry 卖出 6 杯奶昔，每杯 5.50 美元；9 份汉堡套餐，每份 11 美元；20 杯汽水，每杯 1.50 美元，他总收入是多少？`

Why this is a useful case:
the high-score form presents a clean enumeration of item counts and unit prices, then asks for the total revenue.

### Swahili (`swh_Latn`)

Pattern: high-score questions often have clean unit-rate constructions with `kwa`, `kila`, `jumla`, and `ngapi`.

- Target-language surface:
  `Ikiwa Gerald hupata $30 kila siku kutoka kwa kazi yake ya daycare na alifanya kazi kila siku kwa wiki, baada ya kutumia $100 kwa jumla, ana pesa ngapi?`
  
  Chinese gloss:
  `如果 Gerald 在日托工作每天赚 30 美元，一周每天都工作，并且总共花掉 100 美元，他还剩多少钱？`

- Target-language surface:
  `Kuna mbwa 5, paka 2, na ndege 10 katika duka la wanyama wa kufugwa; wanyama hao wote wana miguu mingapi pamoja?`
  
  Chinese gloss:
  `宠物店里有 5 只狗、2 只猫和 10 只鸟；这些动物总共有多少条腿？`

Why this is a useful case:
the question keeps the entity list compact and ends with a direct count request (`ngapi pamoja`).

### Yoruba (`yor_Latn`)

Pattern: high-score questions are less repetitive and enrich amount/count words such as `iye`, `mélòó`, `owó`, and `gbogbo`.

- Target-language surface:
  `Ọ̀gbẹ́ni Smith ní àwọn ewúrẹ́ 55 ní Àgbẹ̀ X àti àwọn ewúrẹ́ 45 ní Àgbẹ̀ Y. Lẹ́yìn tí ó ti ta àwọn ewúrẹ́ 10 láti Àgbẹ̀ X àti ìlọ́po méjì iye yẹn láti Àgbẹ̀ Y, iye ewúrẹ́ tó kù ní àgbẹ̀ méjèèjì náà wá jẹ́ mélòó?`
  
  Chinese gloss:
  `Smith 先生在 X 农场有 55 只山羊，在 Y 农场有 45 只山羊。他从 X 农场卖掉 10 只，又从 Y 农场卖掉这个数量的两倍。两个农场一共还剩多少只山羊？`

- Target-language surface:
  `Gerald àti Julia pín $100 ní ìbámu pẹ̀lú 3:2 ìdàpò; lẹ́yìn tí Gerald ná $10 lórí ìwé kan, iye wo ló kù fún un?`
  
  Chinese gloss:
  `Gerald 和 Julia 按 3:2 分 100 美元；Gerald 花 10 美元买了一本书后，他还剩多少钱？`

Why this is a useful case:
the useful surface form keeps ratio/count relationships explicit and avoids scattering numbers at the sentence end.

### Zulu (`zul_Latn`)

Pattern: high-score questions tend to use short conditional/count structures with `uma`, `malini`, `mangaki`, and `ngamunye`.

- Target-language surface:
  `UJohane uthenga 3 izimbuzi nge $500 ngayinye futhi uthenga 2 nezinkomo nge $1500 ngayinye; usebenzisa malini esewonke?`
  
  Chinese gloss:
  `John 买了 3 只山羊，每只 500 美元，又买了 2 头牛，每头 1500 美元；他总共花了多少钱？`

- Target-language surface:
  `Uma uTommy ethengisa ama-brownies 43 nge- $3 ngesicucu ngasinye nama-cheesecake 23 nge- $4 ngesicucu ngasinye, uqoqa malini?`
  
  Chinese gloss:
  `如果 Tommy 卖出 43 块 brownie，每块 3 美元，又卖出 23 块 cheesecake，每块 4 美元，他一共筹到多少钱？`

Why this is a useful case:
the high-score form places each quantity next to its unit price and asks a direct total-money question.

## Safer Paper Claim

A safe claim is:

> High aggregate SID scores tend to identify surface forms with clearer local binding between quantities, units, prices, and the final question. These forms are shorter and less repetitive on average, and they enrich language-specific question words for totals, counts, and conditional relations.

Avoid claiming:

> SID selection fixes translation errors.

That claim is too strong and confounds translation quality with surface-form selection.

