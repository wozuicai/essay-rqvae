# SID Score Collection Linguistic Analysis

This report analyzes collections of variants with high aggregate SID-rule scores, rather than individual `(layer, level, sid)` buckets. This is intended to find more stable surface-form patterns suitable for a paper case study.

Definitions:
- `top-score`: the top 1,319 test variants by aggregate SID-rule score, roughly one variant per test source on average.
- `bottom-score`: the bottom 1,319 test variants by aggregate SID-rule score.
- Metrics use `strict_else_relaxed_correct` unless explicitly marked as strict.

## Cross-Language Collection Summary

| lang | top acc | bottom acc | top tokens | bottom tokens | top num count | bottom num count | top max-run | bottom max-run | interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| npi_Deva | 0.591 | 0.096 | 29.6 | 30.7 | 3.5 | 4.1 | 1.0 | 5.4 | 高分集合明显更短、重复更少，并更常把工资/时间/数量条件集中在同一句中。 |
| sin_Sinh | 0.514 | 0.089 | 34.2 | 41.3 | 3.7 | 3.9 | 1.2 | 8.7 | 高分集合偏向显式条件句和总量问句，数字与单位靠得更近。 |
| som_Latn | 0.572 | 0.159 | 35.1 | 41.6 | 3.5 | 3.5 | 1.1 | 7.6 | 高分集合更像规整的商品/价格/数量枚举，减少长重复从句。 |
| swh_Latn | 0.682 | 0.271 | 31.5 | 37.9 | 3.3 | 3.6 | 1.0 | 2.5 | Swahili 整体质量较高，粗粒度差异小；高分集合仍偏向清晰单位价格和总量结构。 |
| yor_Latn | 0.417 | 0.064 | 42.1 | 49.3 | 3.2 | 4.0 | 1.1 | 9.1 | 高分集合更短、数字锚点更多，且重复 token 明显减少。 |
| zul_Latn | 0.494 | 0.150 | 23.5 | 25.7 | 3.1 | 4.3 | 1.0 | 2.5 | 高分集合偏向短条件句，数字、单位、价格表达紧凑。 |

## npi_Deva

中文总结：高分集合明显更短、重复更少，并更常把工资/时间/数量条件集中在同一句中。

- Top-score collection accuracy: `0.591`; bottom-score accuracy: `0.096`.
- Top-score questions are `29.6` tokens on average vs `30.7` for bottom-score.
- Top-score max repeated-token run is `1.0` vs `5.4`.
- Top-score number count is `3.5` vs `4.1`.

Top enriched lexical items in high-score collection:

| token | top rate | bottom rate | delta |
| --- | ---: | ---: | ---: |
| कति | 0.851 | 0.466 | 0.384 |
| यदि | 0.349 | 0.104 | 0.245 |
| प्रत्येक | 0.293 | 0.102 | 0.191 |
| भने | 0.314 | 0.137 | 0.177 |
| कुल | 0.292 | 0.155 | 0.137 |
| लागि | 0.285 | 0.148 | 0.137 |
| खर्च | 0.183 | 0.067 | 0.116 |
| प्रति | 0.196 | 0.083 | 0.113 |
| उसले | 0.201 | 0.093 | 0.108 |
| हरेक | 0.149 | 0.048 | 0.102 |

Selected-win examples with Chinese gloss:

- source_idx `571`, selected variant `2`, target `308`, prediction `308`
  - Original v0: लेआले भर्खरै एउटा नयाँ बिरालो पाएकी छिन्। उनको $200, कोटामा नसबंदी गराउनुको लागि 3 खोपको लागि $20 खर्च गर्नुपर्नेछ, र बिरालोले 4 कोटा तोडेको छ जसको प्रत्येकको लागत $12 छ। अहिलेसम्म बिरालोको कति खर्च भएको छ?
  - SID-selected: लेआले भर्खरै ग्रहण गरेको बिरालोलाई $200 स्टेराइज, 3 शट $20 मा प्रत्येक, र 4 भाँडाको भाँडामा $12 प्रत्येकमा भत्कायो अब सम्म यसको मूल्य कति छ?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `387`, selected variant `5`, target `36`, prediction `36`
  - Original v0: 6 र 8 पेन्सिलको मूल्य कति हुन्छ? $2 $3
  - SID-selected: 6 इरेजर (प्रत्येक $2) र 8 पेन्सिल (प्रत्येक $3) को कुल लागत कति हुन्छ?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `875`, selected variant `2`, target `60`, prediction `60`
  - Original v0: पावलले 52 मर्च छ. उसको साथीले 28 मर्च दिए. त्यसपछि, उसले 1/4 आफ्नो मर्च गुमायो. पावलले कति मर्च बाँकी छ?
  - SID-selected: 52 गोलाहरू पाएर र आफ्नो साथीबाट 28 थप पाएपछि, पावलले 1/4 गुमाए। कति गोलाहरू बाँकी छन्?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `902`, selected variant `4`, target `8`, prediction `8`
  - Original v0: विलियमले पाँचवटा नोटबुक र एउटा बलपेन किने। उनले सबैमा कति खर्च गरे? $1.50 $0.5
  - SID-selected: यदि शैक्षिक पसलले प्रति नोटबुक $1.50 र प्रति बलपेन $0.5 शुल्क लिन्छ भने, र विलियमले पाँचवटा नोटबुक र एक बलपेन किन्छ भने, उसले खर्च गरेको कुल रकम कति हो?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。

## sin_Sinh

中文总结：高分集合偏向显式条件句和总量问句，数字与单位靠得更近。

- Top-score collection accuracy: `0.514`; bottom-score accuracy: `0.089`.
- Top-score questions are `34.2` tokens on average vs `41.3` for bottom-score.
- Top-score max repeated-token run is `1.2` vs `8.7`.
- Top-score number count is `3.7` vs `3.9`.

Top enriched lexical items in high-score collection:

| token | top rate | bottom rate | delta |
| --- | ---: | ---: | ---: |
| කොපමණ | 0.328 | 0.130 | 0.198 |
| මුළු | 0.291 | 0.117 | 0.174 |
| සඳහා | 0.376 | 0.205 | 0.171 |
| මුදලක් | 0.198 | 0.060 | 0.138 |
| සෑම | 0.259 | 0.123 | 0.136 |
| නම් | 0.264 | 0.130 | 0.133 |
| මිලදී | 0.265 | 0.151 | 0.114 |
| කීයක් | 0.281 | 0.171 | 0.109 |
| වියදම් | 0.155 | 0.052 | 0.103 |
| එක් | 0.247 | 0.146 | 0.101 |

Selected-win examples with Chinese gloss:

- source_idx `1132`, selected variant `1`, target `45000`, prediction `45000`
  - Original v0: වැලරි මාසෙකට P0 උපයනවා, එයාගේ සහෝදරයා උපයන ගානට වඩා. $5000 1/2
  - SID-selected: වැලරී මාසිකව උපයන්නේ $5000, ඒ කියන්නේ 1/2 ඇගේ සහෝදරයාගේ මාසික ආදායමෙන්; ඔවුන්ගේ මව ඔවුන්ගේ වැටුප මෙන් දෙගුණයක් උපයනවා, ඉතින් ඔවුන් සියල්ලන්ටම මුළු මුදල කොපමණද?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `460`, selected variant `2`, target `84`, prediction `84`
  - Original v0: ග් රේසන් සෑම සතියකම මුදල් සඳහා බඳුන් සහ බෝතල් ප් රතිචක් රීකරණය කරයි. ඇලුමිනියම් බඳුනකට සෙන්ට් දෙකක් වටිනවා සහ ප්ලාස්ටික් බෝතලයක් සෙන්ට් තුනක් වටිනවා. ඇය සතියකට ඇලුමිනියම් බඳුන් තුනක් සෝඩා සහ ප්ලාස්ටික් බෝතල් පහක් වතුර පානය කරයි. ග් රේසන්...
  - SID-selected: සෑම සතියකම ග් රේසන් ඇලුමිනියම් බඳුන් තුනක් (එකකට සෙන්ට් දෙකක වටිනාකමක්) සහ ප්ලාස්ටික් බෝතල් පහක් (එකකට සෙන්ට් තුනක වටිනාකමක්) ප් රතිචක් රීකරණය කරයි. සති හතරක මාසයකදී ඇය උපයන මුළු මුදල සෙන්ට් කීයද?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `902`, selected variant `1`, target `8`, prediction `8`
  - Original v0: විලියම් පොත්පත් පහක් සහ පොත්පත් එකක් මිලදී ගත්තා. ඔහු කොපමණ මුදලක් වියදම් කළාද? $1.50 $0.5
  - SID-selected: අධ් යාපන වෙළඳසැලෙන් එක් එක් $1.50 සඳහා නෝට්බුක් සහ එක් එක් $0.5 සඳහා බෝල පෑන් විකුණයි; විලියම් නෝට්බුක් පහක් සහ එක් බෝල පෑන් එකක් මිලදී ගත්තා, ඉතින් ඔහු මුළු මුදල කොපමණද?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `387`, selected variant `5`, target `36`, prediction `36`
  - Original v0: 6 මකන්න සහ 8 කැන්වස් වලට කීයක් වැය වෙනවද? $2 $3
  - SID-selected: 6 මකන්න (එකකට $2) සහ 8 කැන්වස් (එකකට $3) එකට කොපමණ මුදලක් වැය වේද?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。

## som_Latn

中文总结：高分集合更像规整的商品/价格/数量枚举，减少长重复从句。

- Top-score collection accuracy: `0.572`; bottom-score accuracy: `0.159`.
- Top-score questions are `35.1` tokens on average vs `41.6` for bottom-score.
- Top-score max repeated-token run is `1.1` vs `7.6`.
- Top-score number count is `3.5` vs `3.5`.

Top enriched lexical items in high-score collection:

| token | top rate | bottom rate | delta |
| --- | ---: | ---: | ---: |
| imisa | 0.431 | 0.157 | 0.274 |
| ayuu | 0.290 | 0.105 | 0.186 |
| maxay | 0.198 | 0.036 | 0.162 |
| ayay | 0.220 | 0.063 | 0.157 |
| immisa | 0.194 | 0.051 | 0.143 |
| waa | 0.303 | 0.196 | 0.106 |
| intee | 0.161 | 0.058 | 0.104 |
| guud | 0.153 | 0.055 | 0.098 |
| haddii | 0.202 | 0.105 | 0.097 |
| lacag | 0.130 | 0.035 | 0.096 |

Selected-win examples with Chinese gloss:

- source_idx `902`, selected variant `4`, target `8`, prediction `8`
  - Original v0: Dukaanka waxbarashadu wuxuu iibiyaa buugaag qoraal ah oo midkiiba qiimihiisu yahay $1.50 iyo qalinka kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda kubbadda k...
  - SID-selected: Hadii dukaanka waxbarashadu uu qaato $1.50 buug kasta iyo $0.5 qalin kasta, Williamna uu iibsado shan buug oo lagu daray hal qalin, waa maxay wadarta lacagta uu bixiyay?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `849`, selected variant `4`, target `75`, prediction `75`
  - Original v0: Beeraley ayaa haysta ukumo. wuxuu ku riday saxanka, kaas oo ku jira ukumo kasta oo 30 ah. intee in le'eg ayuu beeraleygu kasbanayaa hadii uu ku iibiyo $2.5 saxanka? 900
  - SID-selected: Haddii beeraley uu leeyahay 900 ukumo oo uu isticmaalo saxan ay ku jiraan 30 ukumo kasta, saxan walbana uu ku iibiyo $2.5, waa maxay wadarta dakhliga beeraleyda?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `26`, selected variant `1`, target `243`, prediction `243`
  - Original v0: Mishka wuxuu iibsaday 3 labo shorts, 3 labo surwaal, iyo 3 labo kabo. hal surwaal ayaa ku kacaya $16.50. hal surwaal ayaa ku kacaya $22.50 iyo hal kabo ayaa ku kacaya $42. imisa doolar ayuu Mishka ku bixiyay dharka oo dhan?
  - SID-selected: M Mish Mishka wuxuu iibsaday 3 labo shorts midkiiba $16.50, 3 labo surwaal midkiiba $22.50, iyo 3 laba kabood midkiiba $42 Immisa doolar ayuu Mishka ku bixiyay?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `1076`, selected variant `3`, target `162`, prediction `162`
  - Original v0: Terry wuxuu iibiyaa 6 milkshakes qofkiiba $5.50, sagaal hamburger qofkiiba $11, iyo 20 soda qofkiiba $1.50.
  - SID-selected: Haddii Terry uu iibiyo 6 milkshakes midkiiba $5.50, sagaal burger midkiiba $11, iyo 20 soda midkiiba $1.50, waa maxay dakhligiisa guud?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。

## swh_Latn

中文总结：Swahili 整体质量较高，粗粒度差异小；高分集合仍偏向清晰单位价格和总量结构。

- Top-score collection accuracy: `0.682`; bottom-score accuracy: `0.271`.
- Top-score questions are `31.5` tokens on average vs `37.9` for bottom-score.
- Top-score max repeated-token run is `1.0` vs `2.5`.
- Top-score number count is `3.3` vs `3.6`.

Top enriched lexical items in high-score collection:

| token | top rate | bottom rate | delta |
| --- | ---: | ---: | ---: |
| gani | 0.416 | 0.058 | 0.359 |
| ngapi | 0.340 | 0.049 | 0.291 |
| kiasi | 0.333 | 0.113 | 0.220 |
| ikiwa | 0.216 | 0.036 | 0.180 |
| jumla | 0.300 | 0.133 | 0.167 |
| cha | 0.248 | 0.161 | 0.086 |
| kama | 0.177 | 0.102 | 0.076 |
| nini | 0.080 | 0.013 | 0.067 |
| kila | 0.490 | 0.431 | 0.058 |
| gharama | 0.113 | 0.062 | 0.051 |

Selected-win examples with Chinese gloss:

- source_idx `511`, selected variant `3`, target `110`, prediction `110`
  - Original v0: Gerald anafanya kazi katika daycare ambayo humlipa $30 kila siku. Alifanya kazi kwa wiki nzima na alitumia jumla ya $100. Ana pesa ngapi?
  - SID-selected: Ikiwa Gerald hupata $30 kila siku kutoka kwa kazi yake ya daycare na alifanya kazi kila siku kwa wiki, baada ya kutumia $100 kwa jumla, ana pesa ngapi?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `179`, selected variant `1`, target `130`, prediction `130`
  - Original v0: Lloyd anapata $10 saa moja kwa masomo ya hesabu. Alifundisha 5 masaa kwa wiki ya kwanza na 8 masaa kwa wiki ya pili. Ni kiasi gani alipata kwa wiki mbili za kwanza?
  - SID-selected: Lloyd anapata $10 kwa saa ya kufundisha hesabu; alifanya kazi 5 saa katika wiki ya kwanza na 8 saa katika wiki ya pili. Ni kiasi gani cha fedha alichopata katika wiki hizo mbili?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `599`, selected variant `1`, target `48`, prediction `48`
  - Original v0: Kwa sasa, duka la wanyama wa kufugwa lina mbwa 5, paka 2, na ndege 10.
  - SID-selected: Kuna mbwa 5, paka 2, na ndege 10 katika duka la wanyama wa kufugwa; wanyama hao wote wana miguu mingapi pamoja?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `260`, selected variant `1`, target `11`, prediction `11`
  - Original v0: Vikombe viwili vya unga ni muhimu kwa ajili ya kufanya biskuti kadhaa. Carla ni kufanya biskuti 36 leo na biskuti 30 kesho. ni vikombe ngapi vya unga itakuwa Carla haja ya kuoka biskuti leo na kesho?
  - SID-selected: Ikiwa Carla hutumia vikombe viwili vya unga kwa kila kuki kumi na mbili, anahitaji vikombe vingapi vya unga kuoka kuki 36 leo na kuki 30 kesho pamoja?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。

## yor_Latn

中文总结：高分集合更短、数字锚点更多，且重复 token 明显减少。

- Top-score collection accuracy: `0.417`; bottom-score accuracy: `0.064`.
- Top-score questions are `42.1` tokens on average vs `49.3` for bottom-score.
- Top-score max repeated-token run is `1.1` vs `9.1`.
- Top-score number count is `3.2` vs `4.0`.

Top enriched lexical items in high-score collection:

| token | top rate | bottom rate | delta |
| --- | ---: | ---: | ---: |
| iye | 0.618 | 0.302 | 0.316 |
| mélòó | 0.340 | 0.108 | 0.233 |
| owó | 0.226 | 0.142 | 0.084 |
| gbogbo | 0.178 | 0.098 | 0.080 |
| fún | 0.396 | 0.328 | 0.068 |
| gbà | 0.117 | 0.055 | 0.062 |
| àti | 0.349 | 0.290 | 0.059 |
| gba | 0.154 | 0.096 | 0.058 |
| jẹ́ | 0.075 | 0.022 | 0.053 |
| rẹ̀ | 0.074 | 0.028 | 0.045 |

Selected-win examples with Chinese gloss:

- source_idx `646`, selected variant `1`, target `79`, prediction `79`
  - Original v0: Alisa fi kẹ̀kẹ́ rin 12 kìlómítà ní wákàtí kan fún wákàtí kan. Stanley fi kẹ̀kẹ́ rin 10 kìlómítà ní wákàtí kan fún wákàtí kan. 4.5 2.5
  - SID-selected: Al Alisa gun kẹ̀kẹ́ rẹ̀ ní 12 mílíọ̀nù ní wákàtí kan fún wákàtí 4.5, nígbà tí Stanley gun kẹ̀kẹ́ rẹ̀ ní 10 mílíọ̀nù ní wákàtí kan fún wákàtí 2.5; kìlómítà mélòó ni wọ́n jọ rìn?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `850`, selected variant `4`, target `70`, prediction `70`
  - Original v0: Ọ̀gbẹ́ni Smith ní oko méjì, Farm X àti Farm Y. Ó ní àwọn ewúrẹ́ 55 nínú Farm X àti àwọn ewúrẹ́ 45 nínú Farm Y. Ó ta àwọn ewúrẹ́ 10 látinú Farm X àti àwọn ewúrẹ́ tó pọ̀ ju iye wọn lọ nínú Farm Y.
  - SID-selected: Ọ̀gbẹ́ni Smith ní àwọn ewúrẹ́ 55 ní Àgbẹ̀ X àti àwọn ewúrẹ́ 45 ní Àgbẹ̀ Y. Lẹ́yìn tí ó ti ta àwọn ewúrẹ́ 10 láti Àgbẹ̀ X àti ìlọ́po méjì iye yẹn láti Àgbẹ̀ Y, iye ewúrẹ́ tó kù ní àgbẹ̀ méjèèjì náà wá jẹ́ mélòó?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `704`, selected variant `4`, target `50`, prediction `50`
  - Original v0: Bí Gerald bá ná owó $10 lórí ìwé kan, iye owó wo ló kù fún un? $100 3 2
  - SID-selected: Ger Gerald àti Julia pín $100 ní ìbámu pẹ̀lú 3:2 ìdàpò; lẹ́yìn tí Gerald ná $10 lórí ìwé kan, iye wo ló kù fún un?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `1057`, selected variant `2`, target `24`, prediction `24`
  - Original v0: Bí wọ́n bá ń wo fíìmù lópin ọ̀sẹ̀, iye fíìmù wo ni wọ́n lè wo láàárín ọ̀sẹ̀ 4? 4
  - SID-selected: J Jill àtàwọn ọ̀rẹ́ rẹ̀ máa ń wo fíìmù 4 ní ọjọ́ Saturday, wọ́n á sì máa wo ìdajì iye yẹn ní ọjọ́ Sunday; bí wọ́n bá ń wo irú fíìmù yìí fún ọ̀sẹ̀ 4, iye fíìmù wo ni wọ́n máa wò?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。

## zul_Latn

中文总结：高分集合偏向短条件句，数字、单位、价格表达紧凑。

- Top-score collection accuracy: `0.494`; bottom-score accuracy: `0.150`.
- Top-score questions are `23.5` tokens on average vs `25.7` for bottom-score.
- Top-score max repeated-token run is `1.0` vs `2.5`.
- Top-score number count is `3.1` vs `4.3`.

Top enriched lexical items in high-score collection:

| token | top rate | bottom rate | delta |
| --- | ---: | ---: | ---: |
| uma | 0.377 | 0.244 | 0.133 |
| malini | 0.158 | 0.047 | 0.111 |
| mangaki | 0.107 | 0.028 | 0.079 |
| bangaki | 0.105 | 0.036 | 0.069 |
| ngamunye | 0.133 | 0.077 | 0.057 |
| futhi | 0.428 | 0.382 | 0.046 |
| amangaki | 0.117 | 0.074 | 0.042 |
| zingaki | 0.067 | 0.026 | 0.041 |
| esewonke | 0.044 | 0.006 | 0.038 |
| iyini | 0.044 | 0.006 | 0.038 |

Selected-win examples with Chinese gloss:

- source_idx `420`, selected variant `2`, target `17000`, prediction `17000`
  - Original v0: Ukuze akhokhele isitolo sakhe, uMnu.Josue wacela imali emabhange amabili.Ibhange lokuqala lamnika $4000, futhi inkampani yesibili yamnika kabili.Uma ekuqaleni wayene- $5000 enhlokodolobha, unemali engakanani manje?
  - SID-selected: Njengoba kakade wayene- $5000 enhlokodolobha, uMnu Josue wathola $4000 ebhange elilodwa futhi wathola imali ephindwe kabili kwenye; unemali engakanani manje?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `816`, selected variant `1`, target `4500`, prediction `4500`
  - Original v0: UJohane uya emakethe futhi uthenga izimbuzi 3 nge-P1 ngayinye nezinkomo 2 nge-P3 ngayinye. $500 $1500
  - SID-selected: UJohane uthenga 3 izimbuzi nge $500 ngayinye futhi uthenga 2 nezinkomo nge $1500 ngayinye; usebenzisa malini esewonke?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `72`, selected variant `3`, target `221`, prediction `221`
  - Original v0: Uma uTommy ethengisa u-P2 wama-brownies no-P3 wama-cheesecake, uTommy uthola malini? $3 $4 43 23
  - SID-selected: Uma uTommy ethengisa ama-brownies 43 nge- $3 ngesicucu ngasinye nama-cheesecake 23 nge- $4 ngesicucu ngasinye, uqoqa malini?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。
- source_idx `1150`, selected variant `5`, target `21`, prediction `21`
  - Original v0: UPatricia unezimbali 30. wanika unina izimbali 24. wathenga izimbali 15 eziningi.
  - SID-selected: Uma ekuqaleni uPatricia wayenama-rose 30, wanika unina 24, futhi kamuva wathenga amanye 15, manje unama-rose amangaki?
  - 中文解读：SID 选择的题面通常把关键数量、单位和求解目标放在更局部、更直接的句式中，降低模型需要从翻译噪声中恢复约束的负担。

## Paper-Facing Takeaway

The aggregate SID score is not merely selecting isolated code IDs. Across languages, high-score variants form collections with visible linguistic properties: compact conditional clauses, explicit numeric anchors, adjacent unit/price expressions, and fewer repeated tokens. These properties are especially clear in lower-quality translations, while cleaner languages show subtler but still measurable differences.
