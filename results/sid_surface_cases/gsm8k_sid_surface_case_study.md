# SID Surface-Form Case Study

This report inspects whether high-uplift SID buckets correspond to visible question-surface patterns.
All statistics are computed from existing `variants.parquet`, `eval_results.parquet`, `sids.uint16.memmap`, and `significant_sid_rules.parquet`; no model was rerun.

Interpretation note: SID rules were learned on train variants. The case descriptions below are qualitative and should be used as examples, not as independent significance claims.

## Cross-Language Summary

| lang | train baseline | test original | test SID selected | significant rules | qualitative pattern |
| --- | ---: | ---: | ---: | ---: | --- |
| npi_Deva | 0.3433 | 0.3298 | 0.3882 | 880 | shorter prompts |
| sin_Sinh | 0.2956 | 0.2919 | 0.3495 | 873 | shorter prompts |
| som_Latn | 0.3606 | 0.3783 | 0.4102 | 704 | shorter prompts |
| swh_Latn | 0.4885 | 0.4981 | 0.5527 | 895 | latent bucket not obvious from coarse features |
| yor_Latn | 0.2221 | 0.1683 | 0.3101 | 888 | shorter prompts; more explicit numbers |
| zul_Latn | 0.3074 | 0.2669 | 0.3381 | 870 | shorter prompts |

## npi_Deva

### High-Uplift SID Buckets

#### Case 1: layer 19 / level 2 / sid 140

- Train bucket: n=703, accuracy=0.6558, uplift=0.3125, q=4.33e-63
- Test hit: n=114, strict-else-relaxed accuracy=0.7018; miss accuracy=0.3532
- Surface means: tokens hit/miss=26.6/32.7; numbers hit/miss=3.2/3.5; ascii-word-rate hit/miss=0.000/0.001; max repeated-token run hit/miss=1.0/1.8
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 31 | 0.7742 |
| 1 | 22 | 0.7273 |
| 2 | 10 | 0.6000 |
| 3 | 16 | 0.5625 |
| 4 | 17 | 0.7647 |
| 5 | 18 | 0.6667 |

- Representative hit examples:

  - `test-00049-v3` (correct, pred=30, target=30): रिचर्डको भवनमा 15 तहहरू छन्, प्रत्येक तहमा 8 एकाइहरू छन्, र कुल एकाइहरूको 3/4 हाल ओगटेका छन्। खाली एकाइहरूको कुल संख्या निर्धारण गर्नुहोस्।
  - `test-00055-v0` (correct, pred=14, target=14): 30 ललिपपपहरू जीनसँग छन्। जीनले ललिपपपहरूको 2 खान्छ। बाँकी ललिपपपहरूसँग, जीनले 2 ललिपपपहरू एउटा झोलामा प्याक गर्न चाहन्छ। कति झोलाहरू जीनले भर्न सक्छ?
  - `test-00060-v4` (correct, pred=17, target=17): 25 नारंगी एक टोकरीमा छन्; 1 खराब छ, 20% अपरिपक्व छ, 2 खट्टा छ, र बाँकी राम्रो छ। राम्रो नारंगीको संख्या निर्धारण गर्नुहोस्।
  - `test-00081-v5` (correct, pred=17, target=17): चार्लीले सुरुमा 10 स्टिकरहरू थिए, त्यसपछि उनले एक मल्ल स्टोरबाट 21 स्टिकरहरू प्राप्त गरे र 23 स्टिकरहरू जन्मदिनको उपहारको रूपमा प्राप्त गरे। पछि उनले आफ्नो बहिनीलाई 9 स्टिकरहरू दिए र ग्रीटिंग कार्ड सजाउन 28 स्टिकरहरू प्रयोग गरे। चार्लीसँग कति स्टिकरहरू बाँकी छन्?

#### Case 2: layer 27 / level 2 / sid 140

- Train bucket: n=512, accuracy=0.6465, uplift=0.3032, q=2.85e-43
- Test hit: n=85, strict-else-relaxed accuracy=0.7059; miss accuracy=0.3545
- Surface means: tokens hit/miss=28.5/32.6; numbers hit/miss=3.6/3.5; ascii-word-rate hit/miss=0.000/0.001; max repeated-token run hit/miss=1.0/1.8
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 23 | 0.7391 |
| 1 | 12 | 0.5000 |
| 2 | 11 | 0.8182 |
| 3 | 11 | 0.9091 |
| 4 | 12 | 0.5833 |
| 5 | 16 | 0.6875 |

- Representative hit examples:

  - `test-00055-v0` (correct, pred=14, target=14): 30 ललिपपपहरू जीनसँग छन्। जीनले ललिपपपहरूको 2 खान्छ। बाँकी ललिपपपहरूसँग, जीनले 2 ललिपपपहरू एउटा झोलामा प्याक गर्न चाहन्छ। कति झोलाहरू जीनले भर्न सक्छ?
  - `test-00081-v0` (correct, pred=17, target=17): चार्लीले 10 स्टिकरहरू किने। उनले मल्लमा एउटा पसलबाट 21 स्टिकरहरू किने र आफ्नो जन्मदिनको लागि 23 स्टिकरहरू पाए। त्यसपछि चार्लीले 9 स्टिकरहरू आफ्नी बहिनीलाई दिए र 28 लाई ग्रीटिंग कार्ड सजाउन प्रयोग गरे। चार्लीसँग कति स्टिकरहरू बाँकी छन्?
  - `test-00081-v1` (correct, pred=17, target=17): चार्लीले 10 स्टिकरहरूसँग सुरु गरे, त्यसपछि उनले 21 स्टिकरहरू एक मल्ल स्टोरमा किन्नुभयो र पछि 23 स्टिकरहरू जन्मदिनको उपहारको रूपमा प्राप्त गरे; 9 स्टिकरहरू आफ्नी बहिनीलाई दिएपछि र ग्रीटिंग कार्डको लागि 28 स्टिकरहरू प्रयोग गरेपछि, कति स्टिकरहरू चार्लीसँग बाँकी छन्?
  - `test-00081-v2` (correct, pred=17, target=17): 10 स्टिकरहरू पाएपछि, चार्लीले एउटा मल्ल पसलमा 21 स्टिकरहरू किन्नुभयो र आफ्नो जन्मदिनको लागि 23 स्टिकरहरू प्राप्त गर्नुभयो। त्यसपछि उनले 9 स्टिकरहरू आफ्नी बहिनीलाई दिए र 28 स्टिकरहरू प्रयोग गरेर ग्रीटिंग कार्ड सजाए। चार्लीसँग अझै कति स्टिकरहरू छन्?

#### Case 3: layer 20 / level 2 / sid 140

- Train bucket: n=797, accuracy=0.6261, uplift=0.2828, q=7.86e-59
- Test hit: n=150, strict-else-relaxed accuracy=0.7400; miss accuracy=0.3509
- Surface means: tokens hit/miss=30.5/32.6; numbers hit/miss=3.4/3.5; ascii-word-rate hit/miss=0.000/0.001; max repeated-token run hit/miss=1.4/1.8
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 37 | 0.7568 |
| 1 | 21 | 0.7619 |
| 2 | 29 | 0.6897 |
| 3 | 18 | 0.6111 |
| 4 | 25 | 0.8000 |
| 5 | 20 | 0.8000 |

- Representative hit examples:

  - `test-00049-v3` (correct, pred=30, target=30): रिचर्डको भवनमा 15 तहहरू छन्, प्रत्येक तहमा 8 एकाइहरू छन्, र कुल एकाइहरूको 3/4 हाल ओगटेका छन्। खाली एकाइहरूको कुल संख्या निर्धारण गर्नुहोस्।
  - `test-00056-v0` (correct, pred=3, target=3): पिटरले यो हप्ता सिनेमा जाने योजना बनाएको छ। उसले सधैं $7 को लागि टिकट र $7 को लागि पपकोर्न पाउँछ। यदि उसको हप्ताको लागि 42 डलर छ भने, ऊ कति पटक सिनेमा जान सक्छ?
  - `test-00060-v4` (correct, pred=17, target=17): 25 नारंगी एक टोकरीमा छन्; 1 खराब छ, 20% अपरिपक्व छ, 2 खट्टा छ, र बाँकी राम्रो छ। राम्रो नारंगीको संख्या निर्धारण गर्नुहोस्।
  - `test-00081-v5` (correct, pred=17, target=17): चार्लीले सुरुमा 10 स्टिकरहरू थिए, त्यसपछि उनले एक मल्ल स्टोरबाट 21 स्टिकरहरू प्राप्त गरे र 23 स्टिकरहरू जन्मदिनको उपहारको रूपमा प्राप्त गरे। पछि उनले आफ्नो बहिनीलाई 9 स्टिकरहरू दिए र ग्रीटिंग कार्ड सजाउन 28 स्टिकरहरू प्रयोग गरे। चार्लीसँग कति स्टिकरहरू बाँकी छन्?

#### Case 4: layer 16 / level 2 / sid 181

- Train bucket: n=589, accuracy=0.6248, uplift=0.2815, q=4.69e-43
- Test hit: n=124, strict-else-relaxed accuracy=0.6935; miss accuracy=0.3529
- Surface means: tokens hit/miss=22.6/32.7; numbers hit/miss=3.9/3.5; ascii-word-rate hit/miss=0.001/0.001; max repeated-token run hit/miss=1.0/1.8
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 9 | 0.6667 |
| 1 | 24 | 0.5833 |
| 2 | 19 | 0.7895 |
| 3 | 24 | 0.7083 |
| 4 | 22 | 0.6818 |
| 5 | 26 | 0.7308 |

- Representative hit examples:

  - `test-00011-v1` (correct, pred=694, target=694): टु टुलाले एउटा बेकरीमा गएर 3 दर्जनौं डोनट्स $68 प्रति दर्जन, 2 दर्जनौं मिनी कपकेक $80 प्रति दर्जन, र 6 दर्जनौं मिनी चिज केक $55 प्रति दर्जनमा किने; कुल खर्च गरिएको रकम के हो?
  - `test-00011-v3` (correct, pred=694, target=694): 3 दर्जन डोनट्स $68 प्रति दर्जन, 2 दर्जन मिनी कपकेक $80 प्रति दर्जन, र 6 दर्जन मिनी चीज केक $55 प्रति दर्जनमा किन्दा टुलाले कति खर्च गर्यो?
  - `test-00011-v4` (correct, pred=694, target=694): टोलाको बेकरी खरिदमा 3 दर्जन डोनट्सको मूल्य $68 प्रति दर्जन, 2 दर्जन मिनी कपकेकको मूल्य $80 प्रति दर्जन, र 6 दर्जन मिनी चिज केकको मूल्य $55 प्रति दर्जन समावेश छ; कुल मूल्य गणना गर्नुहोस्।
  - `test-00011-v5` (correct, pred=694, target=694): यदि टुलाले 3 दर्जन डोनट $68 प्रति दर्जन, 2 दर्जन मिनी कपकेक $80 प्रति दर्जन, र 6 दर्जन मिनी चीज केक $55 प्रति दर्जनमा किन्छ भने, उसले कुल कति खर्च गर्छ?

### Source-Level Cases Where SID Selection Fixes Original v0

- source_idx `17`, selected variant `2`, target `57500`, selected pred `57500`
  - Original v0: यदि उनले 50 हप्ता एक वर्ष, 35 घण्टा एक हप्ता शिक्षक र 15 घण्टा एक हप्ता कोचको रूपमा काम गर्दछ भने, उनको वार्षिक तलब के हो? $20 $30
  - Selected: यदि जिल्लको प्रति घण्टा शुल्क $20 शिक्षण र $30 चीयरलिड कोचिंगको लागि हो, र उनले 35 शिक्षण घण्टा र 15 कोचिंग घण्टा हरेक हप्ता 50 हप्ताको लागि राख्छिन्, उसले वार्षिक कति कमाउँछ?
- source_idx `18`, selected variant `4`, target `7`, selected pred `7`
  - Original v0: 4 हप्तामा कति दर्जन अण्डा खानुहुन्छ? 3
  - Selected: 4 हप्ता पछि क्लेयरले कति दर्जन अण्डा खान्छ यदि उनी हरेक बिहान 3 अण्डा ओम्लेट बनाउँछिन्?
- source_idx `23`, selected variant `1`, target `8`, selected pred `8`
  - Original v0: 1:00 PM देखि 5:00 PM सम्म बग्ने बत्ती कति सेन्टिमिटर छोटो हुन्छ? 2
  - Selected: यदि एउटा मोमबत्ती प्रत्येक घण्टामा 2 सेन्टिमिटर छोटो हुन्छ भने, 1:00 PM बाट 5:00 PM सम्म यो कति छोटो हुन्छ?
- source_idx `25`, selected variant `1`, target `2`, selected pred `2`
  - Original v0: $8.50 को मूल्यमा प्रत्येक बक्समा कति बक्स पिज्जा अर्डर गरे? को मूल्यमा प्रत्येक बक्समा कति बक्स पिज्जा अर्डर गरे? को मूल्यमा प्रत्येक बक्समा कति बक्स पिज्जा अर्डर गरे? को मूल्यमा प्रत्येक बक्समा कति बक्स पिज्जा अर्डर गरे? को मूल्यमा प्रत्येक बक्समा कति बक्स पिज्जा अर्डर गरे? क...
  - Selected: $12, 5 मा मुर्गाको भोजन किन्नुभयो, $3, 4 मा स्याउहरू $1.50 मा प्रत्येक प्याक, र पिज्जाको केही बक्सहरू; उनको कुल बिल $50 थियो। प्रत्येक बक्सको मूल्य $8.50 हो भने उनले कति बक्स पिज्जा किन्नुभयो?
- source_idx `31`, selected variant `4`, target `80`, selected pred `80`
  - Original v0: गुन्टरले एउटा गिलासमा जेली बीन्स गणना गर्न खोजिरहेको छ। उसले आफ्ना साथीहरूलाई सोध्छ कि उनीहरूको विचारमा कति बीन्स छन्। एउटाले 80 भन्छ। अर्कोले 20 पहिलो भन्दा आधा बढी भन्छ। तेस्रोले 25% पहिलो भन्दा बढी भन्छ। उनीहरूको औसत अनुमान के हो?
  - Selected: गन्टरले एउटा गिलासमा भएको जेली बीन्स गणना गर्न खोज्दा तिन जना साथीहरूलाई उनीहरूको अनुमान सोध्छन्: एउटाले 80, भन्छ, अर्कोले त्यो संख्या आधाभन्दा बढी 20, हुन्छ र तेस्रोले यो पहिलो अनुमानभन्दा 25% बढी हो भन्छ। यी तीन अनुमानहरूको औसत के हो?

## sin_Sinh

### High-Uplift SID Buckets

#### Case 1: layer 20 / level 2 / sid 206

- Train bucket: n=622, accuracy=0.5707, uplift=0.2751, q=3.76e-45
- Test hit: n=108, strict-else-relaxed accuracy=0.5093; miss accuracy=0.3125
- Surface means: tokens hit/miss=30.7/36.5; numbers hit/miss=3.0/3.5; ascii-word-rate hit/miss=0.002/0.002; max repeated-token run hit/miss=1.2/2.5
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 13 | 0.4615 |
| 1 | 18 | 0.5556 |
| 2 | 21 | 0.6190 |
| 3 | 21 | 0.7143 |
| 4 | 15 | 0.3333 |
| 5 | 20 | 0.3000 |

- Representative hit examples:

  - `test-00003-v2` (correct, pred=540, target=540): ජේම්ස් 3 ස්ප් රින්ට් එක සම්පූර්ණ කරනවා නම්, 60 මීටර් එකකට, ඔහු මෙය 3 සතියකට වතාවක් කරනවා නම්, ඔහුගේ සතිපතා මුළු දුර මීටර් වලින් කීයද?
  - `test-00036-v2` (correct, pred=75, target=75): ටෙරී දිනපතා 2 යෝගට් ආහාරයට ගනී නම් සහ සාප්පුව 4 යෝගට් විකිණීම $5.00 සඳහා නම්, ඔහු දින 30 තුළ යෝගට් සඳහා කොපමණ මුදලක් වියදම් කරයිද?
  - `test-00055-v3` (correct, pred=14, target=14): ජින්ට මුලින් 30 ලූසිප්ස් තියෙනවා. ඇය 2, පරිභෝජනය කරනවා, පසුව ඉතිරි ටික 2 ලූසිප්ස් එකකට දාගන්න බෑග් වලට දාන්න හදනවා. බෑග් කීයක් පුරවන්න පුළුවන්ද?
  - `test-00120-v2` (correct, pred=240, target=240): මයිගල් සතියකට 2 පෑඩ් පෑඩ් භාවිතා කරනවා නම්, සෑම පෑඩ් එකකටම 30 පත් ර තිබේ නම්, ඔහුගේ මාසික සමස්ත පත් ර භාවිතය කුමක්ද?

#### Case 2: layer 20 / level 2 / sid 179

- Train bucket: n=572, accuracy=0.5629, uplift=0.2673, q=2.41e-39
- Test hit: n=95, strict-else-relaxed accuracy=0.7053; miss accuracy=0.3104
- Surface means: tokens hit/miss=31.4/36.5; numbers hit/miss=3.4/3.4; ascii-word-rate hit/miss=0.001/0.002; max repeated-token run hit/miss=1.1/2.5
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 31 | 0.6774 |
| 1 | 16 | 0.6250 |
| 2 | 13 | 0.7692 |
| 3 | 10 | 0.7000 |
| 4 | 15 | 0.8667 |
| 5 | 10 | 0.6000 |

- Representative hit examples:

  - `test-00056-v4` (correct, pred=3, target=3): සෑම සිනමා චාරිකාවකටම ප් රවේශ පත් රයක් සඳහා $7 සහ පොප්කෝන් සඳහා $7 අවශ් ය වන අතර පීටර්ට සතිය සඳහා $42 ඇති බැවින් ඔහුට සිනමා චාරිකා කීයක් කළ හැකිද?
  - `test-00068-v4` (correct, pred=36, target=36): ඩොක්ටර් වෙර්ට්ස්ගේ පාසලේ ගැහැණු ළමයින් මෙන් දෙගුණයක් පිරිසක් සිටී. ගැහැණු ළමයින්ගේ සංඛ් යාව 60 නම් සහ එක් එක් ගුරුවරයා 5 සිසුන් සඳහා වගකිව යුතු නම්, ගුරුවරුන්ගේ සංඛ් යාව ගණනය කරන්න.
  - `test-00117-v2` (correct, pred=360, target=360): ජෝන් ගේ 3 දරුවන්ගෙන් එක් එක් කෙනාට 2 සපත්තු යුගලයක් ලැබෙනවා, මිල $60 එකකට. ජෝන් ගෙවන මුළු මුදල කීයද?
  - `test-00148-v0` (correct, pred=30, target=30): බ් රිටනි සහ ඇගේ අම්මා කෞතුකාගාරයට යනවා. ඇතුල්වීමේ වියදම වැඩිහිටියන්ට $12 සහ දරුවන්ට $10. බ් රිටනිගේ අම්මා ළමා ටිකට්පතට 1 සහ වැඩිහිටි ටිකට්පතට 1 සඳහා මුදල් ලබා දෙනවා. ඇයට $8 මුදල් ලැබුණොත්, ඇය ඩොලර් වලින් කොපමණ මුදලක් මුදල් ලබා දුන්නාද?

#### Case 3: layer 17 / level 2 / sid 206

- Train bucket: n=868, accuracy=0.5565, uplift=0.2609, q=6.04e-57
- Test hit: n=134, strict-else-relaxed accuracy=0.5522; miss accuracy=0.3111
- Surface means: tokens hit/miss=32.9/36.5; numbers hit/miss=3.3/3.4; ascii-word-rate hit/miss=0.003/0.002; max repeated-token run hit/miss=2.4/2.5
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 25 | 0.8000 |
| 1 | 24 | 0.5417 |
| 2 | 25 | 0.4400 |
| 3 | 24 | 0.5000 |
| 4 | 18 | 0.5000 |
| 5 | 18 | 0.5000 |

- Representative hit examples:

  - `test-00003-v2` (correct, pred=540, target=540): ජේම්ස් 3 ස්ප් රින්ට් එක සම්පූර්ණ කරනවා නම්, 60 මීටර් එකකට, ඔහු මෙය 3 සතියකට වතාවක් කරනවා නම්, ඔහුගේ සතිපතා මුළු දුර මීටර් වලින් කීයද?
  - `test-00036-v0` (correct, pred=75, target=75): ටෙරී දිනකට 2 යෝගට් කනවා. 4 යෝගට් වල ඒවා දැනට විකිණේ $5.00 සඳහා. 30 දිනවල ඔහු යෝගට් සඳහා කොපමණ මුදලක් වියදම් කරනවාද?
  - `test-00036-v2` (correct, pred=75, target=75): ටෙරී දිනපතා 2 යෝගට් ආහාරයට ගනී නම් සහ සාප්පුව 4 යෝගට් විකිණීම $5.00 සඳහා නම්, ඔහු දින 30 තුළ යෝගට් සඳහා කොපමණ මුදලක් වියදම් කරයිද?
  - `test-00063-v3` (correct, pred=1596, target=1596): වසරේ පළමු මාස හය තුළ ඇලීනා මාසිකව $140 ගෙවන්නේ ඇගේ ප් රවාහ දායකත්වය සඳහා වන අතර පසුගිය මාස හය තුළ ඇය 10% අඩු මුදලක් ගෙවයි; ඇගේ මුළු වාර්ෂික ගෙවීම ගණනය කරන්න.

#### Case 4: layer 14 / level 2 / sid 206

- Train bucket: n=580, accuracy=0.5534, uplift=0.2579, q=2.99e-37
- Test hit: n=107, strict-else-relaxed accuracy=0.5047; miss accuracy=0.3125
- Surface means: tokens hit/miss=32.6/36.5; numbers hit/miss=3.3/3.4; ascii-word-rate hit/miss=0.001/0.002; max repeated-token run hit/miss=2.6/2.5
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 15 | 0.6000 |
| 1 | 20 | 0.5000 |
| 2 | 17 | 0.5882 |
| 3 | 12 | 0.6667 |
| 4 | 17 | 0.3529 |
| 5 | 26 | 0.4231 |

- Representative hit examples:

  - `test-00036-v0` (correct, pred=75, target=75): ටෙරී දිනකට 2 යෝගට් කනවා. 4 යෝගට් වල ඒවා දැනට විකිණේ $5.00 සඳහා. 30 දිනවල ඔහු යෝගට් සඳහා කොපමණ මුදලක් වියදම් කරනවාද?
  - `test-00036-v1` (correct, pred=75, target=75): T ටෙරී දිනකට 2 යෝගට් පරිභෝජනය කරන අතර, වර්තමාන විකුණුම් 4 යෝගට් $5.00 සඳහා ලබා දෙයි; ඔහුගේ මුළු යෝගට් වියදම 30 දින තුළ ගණනය කරන්න.
  - `test-00036-v3` (correct, pred=75, target=75): ටෙරීගේ දෛනික යෝගට් ප් රමාණය 2, වන අතර ප් රවර්ධන මිල 4 යෝගට් වේ $5.00 සඳහා; 30 දින වලින් පසු යෝගට් සඳහා ඔහුගේ මුළු වියදම තීරණය කරන්න.
  - `test-00036-v5` (correct, pred=75, target=75): T ටෙරී දිනකට 2 යෝගට් කනවා; $5.00 සඳහා 4 යෝගට් ප් රමාණයක් සමඟ, 30 දිනවලදී යෝගට් සඳහා ඔහු වියදම් කරන මුදල සොයා ගන්න.

### Source-Level Cases Where SID Selection Fixes Original v0

- source_idx `3`, selected variant `2`, target `540`, selected pred `540`
  - Original v0: ජේම්ස් තීරණය කරනවා 3 ස්ප් රින්ට් 3 සතියකට වතාවක් දුවන්න. ඔහු 60 මීටර් එක් එක් ස්ප් රින්ට් එකකට දුවනවා. ඔහු සතියකට දුවන්නේ මීටර් කීයක්ද?
  - Selected: ජේම්ස් 3 ස්ප් රින්ට් එක සම්පූර්ණ කරනවා නම්, 60 මීටර් එකකට, ඔහු මෙය 3 සතියකට වතාවක් කරනවා නම්, ඔහුගේ සතිපතා මුළු දුර මීටර් වලින් කීයද?
- source_idx `5`, selected variant `1`, target `64`, selected pred `64`
  - Original v0: කයිලර් ඔහුගේ නව නිවස සඳහා වීදුරු මිලදී ගැනීමට සාප්පුවට ගියේය. එක් වීදුරුවකට $5, මිල වන නමුත් සෑම දෙවන වීදුරුවකටම මිලෙන් 60% පමණි. කයිලර්ට 16 වීදුරු මිලදී ගැනීමට අවශ් යයි. ඔහු ඒවා සඳහා කොපමණ මුදලක් ගෙවිය යුතුද?
  - Selected: කයිලාර් ඔහුගේ නව නිවස සඳහා වීදුරු මිලදී ගැනීමට සාප්පුවකට ගියේය. සාමාන් යයෙන් එක් වීදුරුවකට $5, මිල වන නමුත් සෑම දෙවන වීදුරුවකටම එම මිලෙන් 60% පමණි. ඔහුට 16 වීදුරු අවශ් ය නම්, ඔහු මුළු වශයෙන් කොපමණ මුදලක් ගෙවනු ඇත්ද?
- source_idx `10`, selected variant `2`, target `366`, selected pred `366`
  - Original v0: නව වැඩසටහනක් පළමු මාසයේ බාගත කිරීම් 60 විය. දෙවන මාසයේ බාගත කිරීම් ගණන පළමු මාසයේ බාගත කිරීම් මෙන් තුන් ගුණයක් වූ නමුත් පසුව තුන්වන මාසයේ 30% කින් අඩු විය. මෙම මාස තුන තුළ වැඩසටහනට බාගත කිරීම් ගණන කොපමණද?
  - Selected: පළමු මාසය තුළ නව මෘදුකාංගය බාගත කිරීම් 60 විය. දෙවන මාසයේ බාගත කිරීම් පළමු මාසයේ s මෙන් තුන් ගුණයක් වූ නමුත් තුන්වන මාසයේ 30% අඩු වීමක් දක්නට ලැබුණි. මාස තුන තුළ මුළු වශයෙන් බාගත කිරීම් කීයක් වාර්තා වී තිබේද?
- source_idx `16`, selected variant `2`, target `230`, selected pred `230`
  - Original v0: සැන් රෆායෙල් නගරයෙන් එකවර දුම්රිය දෙකක් පිටත් වෙනවා. ඒ දුම්රිය දෙකම බටහිර දෙසට ගමන් කරනවා. ඊළඟ දවසේ උතුරට ගමන් කරනවා. ඒ දුම්රිය දෙකම දින දෙකකදී ගමන් කරන්නේ කොපමණ දුරක්ද? 80 150
  - Selected: සැන් රෆායෙල් වල එකම මොහොතේ ආරම්භ වන දුම්රිය දෙකක් 80 සැතපුම් ගණනක් බටහිරට ගමන් කරයි. ඊළඟ දවසේ ඔවුන් උතුරට ගමන් කර 150 සැතපුම් ගණනක් ගමන් කරයි. එක් එක් දුම්රිය දින දෙකේම මුළු වශයෙන් සැතපුම් කීයක් ගමන් කරයිද?
- source_idx `22`, selected variant `1`, target `7`, selected pred `7`
  - Original v0: බිලී ඩීවීඩී විකුණනවා. ඔහුට 8 ගනුදෙනුකරුවන් අඟහරුවාදා ඉන්නවා. ඔහුගේ පළමු 3 ගනුදෙනුකරුවන් එක් එක් ඩීවීඩී එකක් මිලදී ගන්නවා. ඔහුගේ ඊළඟ 2 ගනුදෙනුකරුවන් එක් එක් ඩීවීඩී එකක් මිලදී ගන්නවා. ඔහුගේ අවසන් 3 ගනුදෙනුකරුවන් කිසිදු ඩීවීඩී එකක් මිලදී ගන්නේ නැහැ. බිලී අඟහරුවාදා ඩීවීඩී කීයක් වි...
  - Selected: බිලීට 8 ගනුදෙනුකරුවන් අඟහරුවාදා ඇත; පළමු 3 එක් එක් DVD එකක් මිලදී ගන්න, ඊළඟ 2 එක් එක් මිලදී ගැනීම 2 DVD, සහ අවසාන අඟහරුවාදා 3 ගනුදෙනුකරුවන් කිසිවක් මිලදී නොගනී.

## som_Latn

### High-Uplift SID Buckets

#### Case 1: layer 27 / level 2 / sid 210

- Train bucket: n=655, accuracy=0.6565, uplift=0.2959, q=2.24e-52
- Test hit: n=103, strict-else-relaxed accuracy=0.6699; miss accuracy=0.3697
- Surface means: tokens hit/miss=34.5/39.5; numbers hit/miss=3.5/3.4; ascii-word-rate hit/miss=0.720/0.738; max repeated-token run hit/miss=1.0/2.2
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 13 | 0.6154 |
| 1 | 17 | 0.7647 |
| 2 | 19 | 0.6316 |
| 3 | 16 | 0.7500 |
| 4 | 20 | 0.5500 |
| 5 | 18 | 0.7222 |

- Representative hit examples:

  - `test-00024-v1` (correct, pred=26, target=26): Kyle wuxuu iibsaday buugga ugu iibka badan sanadkii hore $19.50, taas oo ka tarjumaysa qiimo dhimis 25% qiimaha asalka ah.
  - `test-00026-v1` (correct, pred=243, target=243): M Mish Mishka wuxuu iibsaday 3 labo shorts midkiiba $16.50, 3 labo surwaal midkiiba $22.50, iyo 3 laba kabood midkiiba $42 Immisa doolar ayuu Mishka ku bixiyay?
  - `test-00026-v4` (correct, pred=243, target=243): M Mishka wuxuu tagay dukaameysiga wuxuuna iibsaday 3 labo shorts ah $16.50 qofkiiba, 3 labo surwaal ah $22.50 qofkiiba, iyo 3 labo kabo ah $42 qofkiiba.
  - `test-00034-v3` (correct, pred=23, target=23): Haddii ururinta Raymond ay tahay 40 jawharad, tirada Aaronna ay tahay nus ka mid ah intaas oo lagu daray 5, halka Siobian uu leeyahay 2 ka yar Aaron, go'aami tirada Siobhan ee jawharad.

#### Case 2: layer 18 / level 2 / sid 197

- Train bucket: n=501, accuracy=0.6387, uplift=0.2781, q=1.68e-35
- Test hit: n=97, strict-else-relaxed accuracy=0.6907; miss accuracy=0.3697
- Surface means: tokens hit/miss=30.2/39.5; numbers hit/miss=3.6/3.4; ascii-word-rate hit/miss=0.716/0.738; max repeated-token run hit/miss=1.0/2.2
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 11 | 0.6364 |
| 1 | 18 | 0.6667 |
| 2 | 16 | 0.7500 |
| 3 | 20 | 0.7500 |
| 4 | 11 | 0.6364 |
| 5 | 21 | 0.6667 |

- Representative hit examples:

  - `test-00109-v3` (correct, pred=28, target=28): Saldhigga shidaalka wuxuu iibiyaa shidaal $3.00 halkii gallon iyo app wuxuu bixiyaa $.20 lacag celinta gallon; xisaabi qiimaha iibsashada 10 gallon ka dib markaad hesho lacag celinta.
  - `test-00152-v0` (correct, pred=4, target=4): Carl wuxuu iibsadaa toban xirmo oo cookies ah. xirmo kasta oo cookies ah waxaa ku jira lix cookies gudaha. cookie kasta qiimihiisu waa $0.10. intee in le'eg ayuu helayaa Carl haddii uu ku bixiyo biilka $10?
  - `test-00152-v2` (correct, pred=4, target=4): Toban xirmo oo buskud ah, mid walbana lix buskud ah, ayaa uu iibsadaa Carl. iyadoo buskud kasta uu qiimihiisu yahay $0.10, waa maxay lacagta bedelka ah ee uu ku soo celiyo kadib markii uu ku bixiyo biilka $10?
  - `test-00257-v4` (correct, pred=5600, target=5600): Geedka Redwood wuxuu dhererkiisu yahay 200 fuudh wuxuuna ka kooban yahay qaybo adag 10-fuudh oo midkiiba miisaankoodu yahay 400 pounds, laakiin geedku wuxuu ka saaray 30% qoryihiisa; xisaabi culeyskiisa hadda.

#### Case 3: layer 28 / level 2 / sid 210

- Train bucket: n=768, accuracy=0.6315, uplift=0.2709, q=1.19e-51
- Test hit: n=136, strict-else-relaxed accuracy=0.7132; miss accuracy=0.3677
- Surface means: tokens hit/miss=34.8/39.5; numbers hit/miss=3.6/3.4; ascii-word-rate hit/miss=0.719/0.738; max repeated-token run hit/miss=1.1/2.2
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 16 | 0.5625 |
| 1 | 27 | 0.8519 |
| 2 | 26 | 0.6923 |
| 3 | 28 | 0.8214 |
| 4 | 20 | 0.6500 |
| 5 | 19 | 0.5789 |

- Representative hit examples:

  - `test-00026-v3` (correct, pred=243, target=243): M Mishka wuxuu iibsaday 3 labo shorts oo qiimahoodu yahay $16.50, 3 labo surwaal oo qiimahoodu yahay $22.50, iyo 3 labo kabo oo qiimahoodu yahay $42. Immisa doolar ayuu Mishka ku bixiyay dhammaan alaabadaas?
  - `test-00026-v4` (correct, pred=243, target=243): M Mishka wuxuu tagay dukaameysiga wuxuuna iibsaday 3 labo shorts ah $16.50 qofkiiba, 3 labo surwaal ah $22.50 qofkiiba, iyo 3 labo kabo ah $42 qofkiiba.
  - `test-00031-v1` (correct, pred=80, target=80): Gunter wuxuu rabaa inuu ogaado inta jelly beans ee ku jira dhalo, sidaas darteed wuxuu weydiiyay asxaabtiisa qiyaasta: mid ka mid ah saaxiibada ayaa sheegay in ay jiraan 80, mid kale ayaa ku daray in tirada ay tahay 20 in ka badan kala bar qiyaasta koowaad, iyo mid saddexaad ayaa sheegtay in wadarta guud ay tahay 25% in ka badan qiyaasta koowaad...
  - `test-00032-v2` (correct, pred=35, target=35): Haddii John uu daryeelo 10 eey iyo eey kasta uu u baahan yahay .5 saacadood maalin kasta socodka iyo ganacsiga, waa maxay tirada guud ee todobaadlaha ah ee saacadaha uu ku qaato iyaga?

#### Case 4: layer 25 / level 2 / sid 210

- Train bucket: n=914, accuracy=0.6171, uplift=0.2564, q=3.02e-55
- Test hit: n=163, strict-else-relaxed accuracy=0.6626; miss accuracy=0.3676
- Surface means: tokens hit/miss=34.5/39.5; numbers hit/miss=3.8/3.4; ascii-word-rate hit/miss=0.712/0.738; max repeated-token run hit/miss=1.1/2.2
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 17 | 0.6471 |
| 1 | 35 | 0.7429 |
| 2 | 30 | 0.5667 |
| 3 | 34 | 0.6765 |
| 4 | 24 | 0.6250 |
| 5 | 23 | 0.6957 |

- Representative hit examples:

  - `test-00011-v5` (correct, pred=694, target=694): Haddii Toula ay iibsato 3 tobanaan donuts ah $68 halkii tobanaan, 2 tobanaan cupcakes ah $80 halkii tobanaan, iyo 6 tobanaan mini cheese cakes ah $55 halkii tobanaan, qiimaha guud ee ay qaadaneyso waa maxay?
  - `test-00026-v3` (correct, pred=243, target=243): M Mishka wuxuu iibsaday 3 labo shorts oo qiimahoodu yahay $16.50, 3 labo surwaal oo qiimahoodu yahay $22.50, iyo 3 labo kabo oo qiimahoodu yahay $42. Immisa doolar ayuu Mishka ku bixiyay dhammaan alaabadaas?
  - `test-00026-v4` (correct, pred=243, target=243): M Mishka wuxuu tagay dukaameysiga wuxuuna iibsaday 3 labo shorts ah $16.50 qofkiiba, 3 labo surwaal ah $22.50 qofkiiba, iyo 3 labo kabo ah $42 qofkiiba.
  - `test-00031-v1` (correct, pred=80, target=80): Gunter wuxuu rabaa inuu ogaado inta jelly beans ee ku jira dhalo, sidaas darteed wuxuu weydiiyay asxaabtiisa qiyaasta: mid ka mid ah saaxiibada ayaa sheegay in ay jiraan 80, mid kale ayaa ku daray in tirada ay tahay 20 in ka badan kala bar qiyaasta koowaad, iyo mid saddexaad ayaa sheegtay in wadarta guud ay tahay 25% in ka badan qiyaasta koowaad...

### Source-Level Cases Where SID Selection Fixes Original v0

- source_idx `10`, selected variant `5`, target `366`, selected pred `366`
  - Original v0: Barnaamij cusub ayaa lahaa 60 downloads bishii ugu horeysay. tirada downloads ee bisha labaad ahaa saddex jeer ka badan downloads ee bishii ugu horeysay, laakiin ka dibna hoos u by 30% ee bisha saddexaad. Immisa downloads ayaa barnaamijka lahaa guud ahaan saddex bilood?
  - Selected: Bilkii ugu horeeyay waxaa la arkay 60 downloads barnaamijka cusub. bisha labaad waxay lahayd saddex jeer downloads bisha ugu horeysay, laakiin downloads bisha saddexaad ayaa hoos u dhacay 30%. waa maxay tirada guud ee downloads saddexda bilood?
- source_idx `13`, selected variant `5`, target `18`, selected pred `18`
  - Original v0: Melanie waa qof guryaha iibisa. waxay sadex meelood meel ka iibisay qalabkeeda wax lagu nadiifiyo guriga cagaaran, 2 waxay iibisay in ka badan guriga cas, iyo badhka waxa ka haray guriga orange. hadii Melanie ay haysato qalab wax lagu nadiifiyo guriga orange, imisa ayay bilaaw...
  - Selected: Melanie, oo ka shaqeysa albaab ilaa albaab, waxay saddex meelood meel ka mid ah wasakhdaha ay ku iibisay guriga cagaaran, ka dibna 2 waxay ku iibisay guriga cas, ka dibna waxay ku iibisay badhka kaydka haray guriga orange. Maaddaama ay haysato 5 wasakhdaha ay ka hartay, imisa ...
- source_idx `14`, selected variant `2`, target `60`, selected pred `60`
  - Original v0: Fasalka qoob ka ciyaarka ee ardayda 20, 20% waxay ku qalin jebiyeen qoob ka ciyaarka casriga ah, 25% ee ka hartay waxay ku qalinjebiyeen qoob ka ciyaarka jazz, inta kalena waxay ku qalinjebiyeen qoob ka ciyaarka hip-hop. boqolkiiba intee in le'eg oo ardayda oo dhan ayaa ku qal...
  - Selected: Fasalka 20 ee qoob ka ciyaarka, 20% wuxuu ku biiraa qoob ka ciyaarka casriga ah. ardayda ka baxday kadib, 25% waxay ku biiraan qoob ka ciyaarka jazz-ka, inta kalena waxay ku biiraan hip-hop-ka. boqolkiiba intee in le'eg oo fasalka oo dhan ah ayaa ku biiray hip-hop?
- source_idx `21`, selected variant `5`, target `14`, selected pred `14`
  - Original v0: Raymond iyo Samantha waa adeer. Raymond waxa uu dhashay 6 sano ka hor Samantha. Raymond wuxuu dhalay wiil da'diisu ahayd 23. hadii Samantha ay hadda tahay 31, imisa sano ka hor ayaa dhashay wiilkii Raymond?
  - Selected: Haddii Samantha ay hadda tahay 31 walaalkeed Raymondna uu yahay 6 sano ka weyn, Raymondna uu aabbe noqday 23, imisa sano ka hor ayuu wiilkiisa dunida yimid?
- source_idx `26`, selected variant `1`, target `243`, selected pred `243`
  - Original v0: Mishka wuxuu iibsaday 3 labo shorts, 3 labo surwaal, iyo 3 labo kabo. hal surwaal ayaa ku kacaya $16.50. hal surwaal ayaa ku kacaya $22.50 iyo hal kabo ayaa ku kacaya $42. imisa doolar ayuu Mishka ku bixiyay dharka oo dhan?
  - Selected: M Mish Mishka wuxuu iibsaday 3 labo shorts midkiiba $16.50, 3 labo surwaal midkiiba $22.50, iyo 3 laba kabood midkiiba $42 Immisa doolar ayuu Mishka ku bixiyay?

## swh_Latn

### High-Uplift SID Buckets

#### Case 1: layer 29 / level 2 / sid 148

- Train bucket: n=739, accuracy=0.7821, uplift=0.2937, q=9.39e-60
- Test hit: n=101, strict-else-relaxed accuracy=0.8020; miss accuracy=0.4998
- Surface means: tokens hit/miss=34.0/36.8; numbers hit/miss=3.5/3.4; ascii-word-rate hit/miss=0.729/0.729; max repeated-token run hit/miss=1.0/1.3
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 19 | 0.8421 |
| 1 | 11 | 0.8182 |
| 2 | 20 | 0.7000 |
| 3 | 14 | 0.6429 |
| 4 | 20 | 0.8500 |
| 5 | 17 | 0.9412 |

- Representative hit examples:

  - `test-00026-v2` (correct, pred=243, target=243): M Mishka alinunua jozi 3 ya shorts kwa bei $16.50 kwa jozi, 3 jozi za suruali kwa bei $22.50 kwa jozi, na 3 jozi za viatu kwa bei $42 kwa jozi. Ni kiasi gani cha jumla kilichotumiwa?
  - `test-00046-v4` (correct, pred=163, target=163): Kazini Candice aliweka post-it note moja kwenye kila kikombe kati ya vikombe 220. Alikuwa na 80 notes awali na alinunua package njiani. Kama mwishoni alibaki na 23, package ilikuwa na notes ngapi?
  - `test-00090-v2` (correct, pred=225, target=225): Katika picnic, kila adult dinosaur atakula 10 lbs za potato salad na kila child dinosaur atakula 5 lbs. Kwa adults 20 na children 5, jumla ya salad inayohitajika ni ngapi?
  - `test-00159-v1` (correct, pred=15, target=15): Finn kwanza anaona 11 tadp harakati katika bwawa, kisha 6 yao kuibuka kutoka chini ya lily pad, na baada ya 2 yao kujificha wenyewe chini ya mwamba; ni tadpoles ngapi kubaki inayoonekana kwa Finn?

#### Case 2: layer 31 / level 2 / sid 148

- Train bucket: n=599, accuracy=0.7813, uplift=0.2928, q=4.17e-48
- Test hit: n=80, strict-else-relaxed accuracy=0.8125; miss accuracy=0.5005
- Surface means: tokens hit/miss=34.1/36.8; numbers hit/miss=3.5/3.4; ascii-word-rate hit/miss=0.724/0.729; max repeated-token run hit/miss=1.0/1.3
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 14 | 0.7857 |
| 1 | 15 | 0.7333 |
| 2 | 14 | 0.8571 |
| 3 | 11 | 0.5455 |
| 4 | 12 | 0.9167 |
| 5 | 14 | 1.0000 |

- Representative hit examples:

  - `test-00026-v2` (correct, pred=243, target=243): M Mishka alinunua jozi 3 ya shorts kwa bei $16.50 kwa jozi, 3 jozi za suruali kwa bei $22.50 kwa jozi, na 3 jozi za viatu kwa bei $42 kwa jozi. Ni kiasi gani cha jumla kilichotumiwa?
  - `test-00158-v3` (correct, pred=34, target=34): Ikiwa Raphael hununua kalamu 4 kwa $1.5 kila moja, notebooks 2 kwa $4 kila moja, na mzunguko wa karatasi ya dhamana ambayo inagharimu $20, ni gharama yake ya jumla ni nini?
  - `test-00159-v1` (correct, pred=15, target=15): Finn kwanza anaona 11 tadp harakati katika bwawa, kisha 6 yao kuibuka kutoka chini ya lily pad, na baada ya 2 yao kujificha wenyewe chini ya mwamba; ni tadpoles ngapi kubaki inayoonekana kwa Finn?
  - `test-00171-v0` (correct, pred=1210, target=1210): Jake ni kutembea kwa njia ya Makumbusho ya Entomology. Anaona 80 buibui na 8 miguu kila, 90 wadudu na 6 miguu kila, na 3 nadra mutant invertebrates na 10 miguu kila. Je, miguu ngapi Jake kuona jumla?

#### Case 3: layer 30 / level 2 / sid 148

- Train bucket: n=655, accuracy=0.7786, uplift=0.2902, q=1.36e-51
- Test hit: n=88, strict-else-relaxed accuracy=0.7955; miss accuracy=0.5004
- Surface means: tokens hit/miss=35.3/36.8; numbers hit/miss=3.5/3.4; ascii-word-rate hit/miss=0.726/0.729; max repeated-token run hit/miss=1.0/1.3
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 14 | 0.8571 |
| 1 | 16 | 0.7500 |
| 2 | 16 | 0.7500 |
| 3 | 14 | 0.5714 |
| 4 | 13 | 0.8462 |
| 5 | 15 | 1.0000 |

- Representative hit examples:

  - `test-00026-v2` (correct, pred=243, target=243): M Mishka alinunua jozi 3 ya shorts kwa bei $16.50 kwa jozi, 3 jozi za suruali kwa bei $22.50 kwa jozi, na 3 jozi za viatu kwa bei $42 kwa jozi. Ni kiasi gani cha jumla kilichotumiwa?
  - `test-00105-v1` (correct, pred=20, target=20): Cody hutumia mara tatu idadi ya biskuti kwamba Amir anakula. Amir anakula 5 biskuti, hivyo ni biskuti wangapi wao kula kwa jumla?
  - `test-00159-v1` (correct, pred=15, target=15): Finn kwanza anaona 11 tadp harakati katika bwawa, kisha 6 yao kuibuka kutoka chini ya lily pad, na baada ya 2 yao kujificha wenyewe chini ya mwamba; ni tadpoles ngapi kubaki inayoonekana kwa Finn?
  - `test-00165-v3` (correct, pred=77, target=77): Kwa bajeti ya € 1500 iliyotolewa na familia yake kwa siku yake ya kuzaliwa ya 30, El Elvira ana mpango wa kuweka pesa kwa nguo. Ananunua kompyuta na skrini, kibodi na panya kwa € 1090, skanner kwa € 157, burner CD kwa € 74, na printer kwa € 102. Ni kiasi gani cha pesa kilichobaki kwa ununuzi wa nguo zake?

#### Case 4: layer 20 / level 2 / sid 141

- Train bucket: n=713, accuracy=0.7784, uplift=0.2899, q=4.20e-56
- Test hit: n=124, strict-else-relaxed accuracy=0.8065; miss accuracy=0.4988
- Surface means: tokens hit/miss=32.7/36.8; numbers hit/miss=4.0/3.4; ascii-word-rate hit/miss=0.714/0.729; max repeated-token run hit/miss=1.0/1.3
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 11 | 0.9091 |
| 1 | 32 | 0.8438 |
| 2 | 19 | 0.8421 |
| 3 | 21 | 0.9048 |
| 4 | 16 | 0.7500 |
| 5 | 25 | 0.6400 |

- Representative hit examples:

  - `test-00009-v1` (correct, pred=460, target=460): Eliza hupata $10 kwa saa kwa saa ya kwanza 40 anafanya kazi kila wiki, na muda wowote wa ziada hulipwa kwa 1.2 mara ya kiwango chake cha kawaida; ikiwa alifanya kazi 45 saa wiki hii, ni nini mapato yake yote?
  - `test-00009-v3` (correct, pred=460, target=460): Mshahara wa kawaida wa Eliza ni $10 kwa saa kwa hadi saa O40 kila wiki, na saa za ziada zinatozwa kwa 1.2 mara ya kiwango cha kawaida; anapata kiasi gani ikiwa alifanya kazi 45 saa wiki hii?
  - `test-00011-v0` (correct, pred=694, target=694): Toula alikwenda kwenye duka la mikate na kununua aina mbalimbali za keki. Yeye alinunua 3 kadhaa donuts ambayo gharama $68 kwa dozi, 2 kadhaa mini cupcakes ambayo gharama $80 kwa dozi, na 6 kadhaa mini cheesecakes kwa $55 kwa dozi. kiasi gani jumla ya gharama?
  - `test-00011-v1` (correct, pred=694, target=694): Tou Toula alitembelea duka la mikate na kununua 3 dozi ya donuts kwa bei ya $68 kwa dozi, 2 dozi ya keki ndogo kwa bei ya $80 kwa dozi, na 6 dozi ya keki ndogo za jibini kwa bei ya $55 kwa dozi; ni kiasi gani cha jumla kilichotumiwa?

### Source-Level Cases Where SID Selection Fixes Original v0

- source_idx `1`, selected variant `4`, target `3`, selected pred `3`
  - Original v0: Kanzu inahitaji vifungo 2 vya nyuzi za bluu na nusu ya nyuzi nyeupe.
  - Selected: Ikiwa kanzu ina vifungo 2 vya nyuzi za bluu na nusu ya vifungo vingi vya nyuzi nyeupe, jumla ya vifungo ni ngapi?
- source_idx `5`, selected variant `1`, target `64`, selected pred `64`
  - Original v0: Kylar alikwenda duka kununua glasi kwa ajili ya nyumba yake mpya. glasi moja gharama $5, lakini kila glasi pili gharama tu 60% ya bei. Kylar anataka kununua glasi 16. ni kiasi gani yeye haja ya kulipa kwa ajili yao?
  - Selected: Ky Kylar alikwenda duka kununua glasi kwa ajili ya nyumba yake mpya; kila glasi kawaida gharama $5, lakini kila glasi pili gharama tu 60% ya bei hiyo. Kama anataka 16 glasi, ni kiasi gani yeye kulipa kwa jumla?
- source_idx `38`, selected variant `4`, target `10`, selected pred `10`
  - Original v0: John anaendesha [P0 maili] kwa wiki. Anaendesha 3 siku kwa wiki. Anaendesha 3 masaa siku ya kwanza na nusu kama siku mbili anazoendesha. Anaendesha kwa kasi gani? 60
  - Selected: Katika wiki moja John anaendesha 60 maili kwa siku 3. siku ya kwanza anaendesha kwa 3 masaa, na siku mbili nyingine anaendesha kwa nusu muda huo kila mmoja. ni nini kasi yake?
- source_idx `46`, selected variant `4`, target `163`, selected pred `163`
  - Original v0: Candice kuweka 80 post-it noti katika mkoba wake kabla ya yeye kuelekea nje kwa kazi yake katika duka la kahawa. Katika njia yake, yeye kusimamishwa mbali katika duka na kununuliwa mfuko wa Post-it noti; Kazini, yeye kuweka moja Post-it noti juu ya kila mmoja wa P1 tofauti vik...
  - Selected: Kazini Candice aliweka post-it note moja kwenye kila kikombe kati ya vikombe 220. Alikuwa na 80 notes awali na alinunua package njiani. Kama mwishoni alibaki na 23, package ilikuwa na notes ngapi?
- source_idx `60`, selected variant `1`, target `17`, selected pred `17`
  - Original v0: Kikapu kina 25 machungwa ambayo kati yake 1 ni mbaya, 20% ni unripe, 2 ni machungu na wengine ni nzuri.
  - Selected: Katika kikapu kuna 25 machungwa; 1 yao ni mbaya, 20% ni unripe, 2 ni machungu, na mabaki ni nzuri. Ni wangapi ni nzuri?

## yor_Latn

### High-Uplift SID Buckets

#### Case 1: layer 20 / level 2 / sid 166

- Train bucket: n=650, accuracy=0.5538, uplift=0.3317, q=1.42e-74
- Test hit: n=140, strict-else-relaxed accuracy=0.3714; miss accuracy=0.2308
- Surface means: tokens hit/miss=36.3/44.2; numbers hit/miss=4.1/3.4; ascii-word-rate hit/miss=0.127/0.137; max repeated-token run hit/miss=1.1/3.7
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 36 | 0.3611 |
| 1 | 22 | 0.4091 |
| 2 | 19 | 0.2632 |
| 3 | 15 | 0.5333 |
| 4 | 18 | 0.3889 |
| 5 | 30 | 0.3333 |

- Representative hit examples:

  - `test-00058-v4` (correct, pred=57, target=57): Níwọ̀n bí Stephen ti ń san $40.00 fún àwọn nǹkan ìnáwó rẹ̀, ó wá fi owó 25% kún owó tí wọ́n ń san fún un, ó tún fi owó $3.00 kún owó tí wọ́n ń san fún un, ó sì fi owó $4.00 kún owó tí wọ́n ń san fún un.
  - `test-00072-v5` (correct, pred=221, target=221): Ṣe àròpọ̀ iye tí Tommy rí gbà nígbà tó ta 43 búrẹ́dì fún $3 ẹnì kọ̀ọ̀kan àti 23 ìyàngbẹ cheesecake fún $4 ẹnì kọ̀ọ̀kan.
  - `test-00090-v1` (correct, pred=225, target=225): Ted tó jẹ́ ọmọ T-Rex ń se satelaiti fún àpèjẹ àwọn ẹranko tó ń jẹ́ dinosaur. Ó mọ̀ pé àwọn ẹranko tó ti dàgbà máa ń jẹ 10 lbs satelaiti, nígbà tí àwọn ọmọ dinosaur máa ń jẹ ìdajì iye yẹn. Bí àwọn àgbàlagbà 20 àtàwọn ọmọ 5 bá wà níbẹ̀, iye kíláàsì satelaiti wo ni Ted gbọ́dọ̀ mú wá kí gbogbo èèyàn lè jẹ?
  - `test-00158-v0` (correct, pred=34, target=34): Raphael lọ ra àwọn ohun èlò ilé ìwé kan. Ó ra 4 àkọsílẹ̀ tí ó ná $1.5 ní ìkan, 2 ìwé àkọsílẹ̀ tí ó ná $4 ní ìkan, àti àgbá ìwé ìka tí ó ná $20 ní ìkan.

#### Case 2: layer 22 / level 2 / sid 166

- Train bucket: n=667, accuracy=0.5397, uplift=0.3176, q=1.45e-70
- Test hit: n=145, strict-else-relaxed accuracy=0.3724; miss accuracy=0.2307
- Surface means: tokens hit/miss=36.4/44.2; numbers hit/miss=4.3/3.4; ascii-word-rate hit/miss=0.127/0.137; max repeated-token run hit/miss=1.1/3.7
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 41 | 0.3415 |
| 1 | 22 | 0.3182 |
| 2 | 17 | 0.2941 |
| 3 | 21 | 0.5714 |
| 4 | 19 | 0.4737 |
| 5 | 25 | 0.2800 |

- Representative hit examples:

  - `test-00026-v4` (correct, pred=243, target=243): M. Mishka lọ ra nǹkan, ó sì ra 3 àpò ẹ̀wù gígùn fún $16.50 ẹnì kọ̀ọ̀kan, 3 àpò ẹ̀wù gígùn fún $22.50 ẹnì kọ̀ọ̀kan, àti 3 àpò bàtà fún $42 ẹnì kọ̀ọ̀kan.
  - `test-00072-v5` (correct, pred=221, target=221): Ṣe àròpọ̀ iye tí Tommy rí gbà nígbà tó ta 43 búrẹ́dì fún $3 ẹnì kọ̀ọ̀kan àti 23 ìyàngbẹ cheesecake fún $4 ẹnì kọ̀ọ̀kan.
  - `test-00137-v0` (correct, pred=29, target=29): Rory pàṣẹ 2 subs fún $7.50 kọọkan, 2 àpò àwọn ẹ̀rọ àfọ̀rọ̀wérò $1.50 fún kọọkan àti 2 cookies fún $1.00 kọọkan fún ìfilọ. A ti fi owó ìfilọ 20% kún un nígbà ìfilọ́ àti ó fẹ́ fi owó ìfilọ́ $5.00 kún un.
  - `test-00158-v0` (correct, pred=34, target=34): Raphael lọ ra àwọn ohun èlò ilé ìwé kan. Ó ra 4 àkọsílẹ̀ tí ó ná $1.5 ní ìkan, 2 ìwé àkọsílẹ̀ tí ó ná $4 ní ìkan, àti àgbá ìwé ìka tí ó ná $20 ní ìkan.

#### Case 3: layer 21 / level 2 / sid 166

- Train bucket: n=767, accuracy=0.5359, uplift=0.3137, q=2.02e-79
- Test hit: n=159, strict-else-relaxed accuracy=0.3711; miss accuracy=0.2304
- Surface means: tokens hit/miss=35.5/44.2; numbers hit/miss=4.0/3.4; ascii-word-rate hit/miss=0.128/0.137; max repeated-token run hit/miss=1.1/3.7
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 43 | 0.3721 |
| 1 | 24 | 0.2917 |
| 2 | 20 | 0.3500 |
| 3 | 22 | 0.5000 |
| 4 | 18 | 0.4444 |
| 5 | 32 | 0.3125 |

- Representative hit examples:

  - `test-00022-v0` (correct, pred=7, target=7): Billy ta DVD. ó ní àwọn oníbàárà 8 ní ọjọ́ Tuesday. àwọn oníbàárà 3 rẹ̀ àkọ́kọ́ rà DVD kan. àwọn oníbàárà 2 rẹ̀ tó tẹ̀ lé e rà DVD 2 ní ẹnì kọ̀ọ̀kan. àwọn oníbàárà 3 rẹ̀ tó kẹ́yìn kò ra DVD kankan. iye DVD wo ni Billy ta ní ọjọ́ Tuesday?
  - `test-00058-v4` (correct, pred=57, target=57): Níwọ̀n bí Stephen ti ń san $40.00 fún àwọn nǹkan ìnáwó rẹ̀, ó wá fi owó 25% kún owó tí wọ́n ń san fún un, ó tún fi owó $3.00 kún owó tí wọ́n ń san fún un, ó sì fi owó $4.00 kún owó tí wọ́n ń san fún un.
  - `test-00064-v2` (correct, pred=300, target=300): Lẹ́yìn tí Sophia ti fi 4 gálọ̀nù epo rin 100 kìlómítà, ó fẹ́ mọ bí ọkọ̀ tó kún fún 12 gálọ̀nù epo ṣe lè rìn tó, gẹ́gẹ́ bí ìwé ìtọ́ni onílé rẹ̀ ṣe sọ.
  - `test-00072-v5` (correct, pred=221, target=221): Ṣe àròpọ̀ iye tí Tommy rí gbà nígbà tó ta 43 búrẹ́dì fún $3 ẹnì kọ̀ọ̀kan àti 23 ìyàngbẹ cheesecake fún $4 ẹnì kọ̀ọ̀kan.

#### Case 4: layer 18 / level 2 / sid 113

- Train bucket: n=700, accuracy=0.5057, uplift=0.2836, q=5.59e-60
- Test hit: n=92, strict-else-relaxed accuracy=0.4891; miss accuracy=0.2302
- Surface means: tokens hit/miss=34.8/44.1; numbers hit/miss=2.9/3.4; ascii-word-rate hit/miss=0.161/0.136; max repeated-token run hit/miss=1.1/3.7
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 8 | 0.3750 |
| 1 | 18 | 0.6667 |
| 2 | 13 | 0.4615 |
| 3 | 17 | 0.6471 |
| 4 | 17 | 0.2941 |
| 5 | 19 | 0.4211 |

- Representative hit examples:

  - `test-00072-v4` (correct, pred=221, target=221): Tommy ṣe ìkóra-ẹni-níjàánu, ó ní 43 brownies tí wọ́n ń ta ní $3 àti 23 cheesecake slices tí wọ́n ń ta ní $4; kà iye owó tí wọ́n kó jọ.
  - `test-00083-v5` (correct, pred=600, target=600): Níwọ̀n bí Dánì ti gbin àwọn igi rósì 3, tí ọ̀kọ̀ọ̀kan wọn ní òdòdó rósì 25, tí òdòdó rósì kọ̀ọ̀kan sì ní ẹ̀gún 8, pinnu iye ẹ̀gún tó wà nínú wọn.
  - `test-00171-v1` (correct, pred=1210, target=1210): Jake rìn gba inú ibi ìkóhun-ìṣẹ̀ǹbáyé-sí-àwọn-ohun-ní-agbo kọjá, ó sì rí àwọn ewéko 80 tí kọ̀ọ̀kan wọn ní ẹsẹ̀ 8, àwọn kòkòrò 90 tí kọ̀ọ̀kan wọn ní ẹsẹ̀ 6, àti àwọn ẹranko aláìlábààwọ́n tí wọ́n jẹ́ aláìsàn àbùdá 3 tí kò wọ́pọ̀, tí kọ̀ọ̀kan wọn ní ẹsẹ̀ 10; ẹsẹ̀ mélòó ló rí ní gbogbo?
  - `test-00241-v1` (correct, pred=6, target=6): Dolly ní ìwé méjì, Pandora sì ní ìwé kan; bí olúkúlùkù wọn bá ka ìwé tirẹ̀ àti ti ẹnì kejì, iye ìwé wo ni wọ́n ti kà ní àpapọ̀?

### Source-Level Cases Where SID Selection Fixes Original v0

- source_idx `0`, selected variant `4`, target `18`, selected pred `18`
  - Original v0: Janet ń jẹ mẹ́ta nínú wọn fún àárọ̀, ó sì ń ṣe àpò fún àwọn ọ̀rẹ́ rẹ̀ lójoojúmọ́ pẹ̀lú mẹ́rin. Ó ń ta èyí tó ṣẹ́ kù lójoojúmọ́ ní ọjà àgbẹ̀ fún $2 fún ẹyin kan tí wọ́n fi ṣe àdàpọ̀. 16
  - Selected: Jan Janet ń fi 16 ẹyin sílẹ̀ lójoojúmọ́; lẹ́yìn tó jẹ mẹ́ta fún oúnjẹ àárọ̀ àti tó ṣe àwọn búrẹ́dì mẹ́rin fún àwọn ọ̀rẹ́ rẹ̀, ó ta àwọn ẹyin tó ṣẹ́ kù ní $2 ní ọjà àwọn àgbẹ̀.
- source_idx `3`, selected variant `2`, target `540`, selected pred `540`
  - Original v0: James pinnu láti sáré 3 ìje 3 ní ìgbà kan lọ́sẹ̀. Ó sáré 60 mítà ní ìje kọ̀ọ̀kan.
  - Selected: Bí James bá ṣe 3 sprint tó ní 60 mítà ní ẹnì kọ̀ọ̀kan, tó sì ṣe èyí 3 ní ìgbà mélòó lọ́sẹ̀, kí ni iye ibi tó ń rìn ní gbogbo ọ̀sẹ̀ ní mítà?
- source_idx `16`, selected variant `5`, target `230`, selected pred `230`
  - Original v0: Àwọn ọkọ̀ ojú irin méjì máa ń kúrò ní San Rafael ní àkókò kan náà. Wọ́n máa ń rìnrìn àjò lọ sí apá ìwọ̀ oòrùn, àwọn méjèèjì máa ń rìnrìn àjò fún 80 kìlómítà. Lọ́jọ́ kejì, wọ́n máa ń rìnrìn àjò lọ sí apá àríwá, wọ́n á sì rìnrìn àjò fún 150 kìlómítà.
  - Selected: Àwọn ọkọ̀ ojú irin méjì máa ń kúrò ní San Rafael ní àkókò kan náà, wọ́n á rìnrìn àjò lọ sí ìwọ̀ oòrùn fún 80 kìlómítà, wọ́n á sì tún rìnrìn àjò lọ sí àríwá fún 150 kìlómítà lọ́jọ́ kejì.
- source_idx `19`, selected variant `1`, target `6`, selected pred `6`
  - Original v0: Bí Marissa bá ń rìnrìn àjò kan tó gùn tó 12 mílíọ̀nù, ó gba 1 wákàtí kan láti rìnrìn àjò méjì àkọ́kọ́, ó sì tún gba wákàtí kan láti rìnrìn àjò méjì tó tẹ̀ lé e. Bí ó bá fẹ́ kí ìwọ̀n ìyípadà tó ń ṣe jẹ́ 4 mílíọ̀nù ní wákàtí kan, kí ni ìyípadà tó yẹ kó ṣe láti rìnrìn àjò tó kù? 4
  - Selected: Mar Marissa rìnrìn àjò kan tó gùn tó 12 kìlómítà. Ó lo 1 wákàtí kan fún 4 kìlómítà àkọ́kọ́, ó sì tún lo 1 wákàtí kan sí 2 tó tẹ̀ lé e. Kí ó tó lè ní ìlọ́po mẹ́ta 4 kìlómítà ní wákàtí kan, kí ni ó máa ṣe nígbà tó bá ń rìnrìn àjò náà?
- source_idx `28`, selected variant `3`, target `25`, selected pred `25`
  - Original v0: Henry dúró sí ibi méjì nígbà tó ń gun kẹ̀kẹ́ rẹ̀ tó gùn tó 60 mílíọ̀nù. Ó kọ́kọ́ dúró lẹ́yìn 20 mílíọ̀nù. 15
  - Selected: Nígbà tí Henry ń gun kẹ̀kẹ́ tó gùn tó 60 kìlómítà, ó dúró díẹ̀ lẹ́yìn 20 kìlómítà, ó sì tún dúró díẹ̀ lẹ́yìn náà 15 kìlómítà kí ìrìn àjò náà tó parí.

## zul_Latn

### High-Uplift SID Buckets

#### Case 1: layer 17 / level 2 / sid 47

- Train bucket: n=529, accuracy=0.6030, uplift=0.2956, q=1.64e-43
- Test hit: n=118, strict-else-relaxed accuracy=0.5763; miss accuracy=0.3098
- Surface means: tokens hit/miss=20.8/27.5; numbers hit/miss=3.3/3.6; ascii-word-rate hit/miss=0.850/0.870; max repeated-token run hit/miss=1.0/1.3
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 12 | 0.5000 |
| 1 | 24 | 0.6250 |
| 2 | 19 | 0.5789 |
| 3 | 21 | 0.6667 |
| 4 | 20 | 0.5500 |
| 5 | 22 | 0.5000 |

- Representative hit examples:

  - `test-00003-v2` (correct, pred=540, target=540): Uma uJames eqeda 3 sprints 60 amamitha ngamunye, futhi wenza lokhu 3 izikhathi ngesonto, yini ibanga lakhe lonke ngesonto ngamamitha?
  - `test-00005-v4` (correct, pred=64, target=64): Ukuze athenge ifulethi lakhe elisha, uKylar uzothenga izibuko 16. Intengo yengilazi ngayinye ingu- $5, kodwa ingilazi ngayinye yesibili ibiza 60% kuphela yale ntengo. Uzochitha malini? 2
  - `test-00011-v1` (correct, pred=694, target=694): UTou Toula wavakashela indawo yokubhaka futhi wathenga 3 amadonathi ayishumi ngentengo $68 ngeshumi, 2 amadonathi amancane ama-cupcake ngentengo $80 ngeshumi, 6 amadonathi amancane ama-chees cakes abiza $55 ngeshumi; ingakanani imali esetshenzisiwe?
  - `test-00044-v0` (correct, pred=20, target=20): UCharlie ufuna ukuthengisa amakhandlela e-beewax. Nge-pound ngayinye ye-beewax, angenza amakhandlela e-10 aphuzi. I-pound eyodwa ye-beewax namagceke abiza $10.00 kokuthengiswayo. Uma ethengisa ikhandlela ngalinye nge-$2.00 ngalinye, yini inzuzo yakhe uma enza futhi ethengisa amakhandlela 20?

#### Case 2: layer 21 / level 2 / sid 47

- Train bucket: n=636, accuracy=0.5818, uplift=0.2744, q=2.76e-45
- Test hit: n=123, strict-else-relaxed accuracy=0.5772; miss accuracy=0.3096
- Surface means: tokens hit/miss=22.9/27.5; numbers hit/miss=3.7/3.6; ascii-word-rate hit/miss=0.845/0.870; max repeated-token run hit/miss=1.0/1.3
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 11 | 0.3636 |
| 1 | 33 | 0.6061 |
| 2 | 18 | 0.6111 |
| 3 | 20 | 0.6500 |
| 4 | 17 | 0.4706 |
| 5 | 24 | 0.6250 |

- Representative hit examples:

  - `test-00017-v0` (correct, pred=57500, target=57500): UJill ukhokhelwa $20 ngehora lokufundisa futhi $30 ngokuba ngumqeqeshi wezinsizwa ezikhuthazayo. Uma esebenza 50 amasonto ngonyaka, 35 amahora ngesonto njengothisha futhi 15 amahora ngesonto njengomqeqeshi, uyini umholo wakhe wonyaka?
  - `test-00017-v1` (correct, pred=57500, target=57500): UJill uthola $20 ngehora lokufundisa futhi $30 ngehora njengomqeqeshi we-cheerleader; usebenza 35 amahora ngesonto efundisa futhi 15 amahora ngesonto eqeqesha, amasonto 50 ngonyaka. Iyini imali yakhe engenayo yonyaka?
  - `test-00017-v3` (correct, pred=57500, target=57500): UJill ukhokhelwa $20 ihora lokufundisa futhi $30 ihora lokuqeqesha abajabule. Usebenza 35 amahora masonto onke njengothisha futhi 15 amahora masonto onke njengomqeqeshi, phakathi 50 amasonto unyaka ngamunye. Iyini iholo lakhe lonyaka?
  - `test-00036-v4` (correct, pred=75, target=75): Njengoba uTerry edla 2 yogurts ngosuku futhi intengo yokuthengisa ingu 4 yogurts ye $5.00, iyini intengo yakhe ephelele yogurt phezu 30 izinsuku?

#### Case 3: layer 20 / level 2 / sid 47

- Train bucket: n=709, accuracy=0.5712, uplift=0.2638, q=8.34e-47
- Test hit: n=132, strict-else-relaxed accuracy=0.6061; miss accuracy=0.3088
- Surface means: tokens hit/miss=23.2/27.5; numbers hit/miss=3.5/3.6; ascii-word-rate hit/miss=0.851/0.870; max repeated-token run hit/miss=1.0/1.3
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 28 | 0.6071 |
| 1 | 27 | 0.6667 |
| 2 | 20 | 0.7000 |
| 3 | 14 | 0.7143 |
| 4 | 20 | 0.5000 |
| 5 | 23 | 0.4783 |

- Representative hit examples:

  - `test-00026-v0` (correct, pred=243, target=243): UMishka wathenga 3 amajazi amafushane, 3 amajazi amabhulukwe, 3 amajazi izicathulo. Ijazi elilodwa libiza $16.50. Ijazi elilodwa libiza $22.50 futhi isicathulo esisodwa sibiza $42. UMishka wasebenzisa amaRandi amangaki kuzo zonke lezi zinto zokugqoka?
  - `test-00026-v1` (correct, pred=243, target=243): UMish Mishka wathenga amabhulukwe 3 ngalinye nge- $16.50, amabhulukwe 3 ngalinye nge- $22.50, nezicathulo 3 ngalinye nge- $42.
  - `test-00036-v4` (correct, pred=75, target=75): Njengoba uTerry edla 2 yogurts ngosuku futhi intengo yokuthengisa ingu 4 yogurts ye $5.00, iyini intengo yakhe ephelele yogurt phezu 30 izinsuku?
  - `test-00050-v5` (correct, pred=294, target=294): Njengoba amaqanda 252 ekhiqizwa nsuku zonke epulazini likaLloyd futhi intengo yokuthengisa ingu- $2 ngeyishumi nambili, uhola malini ngamaqanda ngesonto?

#### Case 4: layer 25 / level 2 / sid 12

- Train bucket: n=837, accuracy=0.5711, uplift=0.2637, q=2.75e-55
- Test hit: n=139, strict-else-relaxed accuracy=0.6259; miss accuracy=0.3082
- Surface means: tokens hit/miss=22.4/27.5; numbers hit/miss=2.8/3.6; ascii-word-rate hit/miss=0.895/0.869; max repeated-token run hit/miss=1.0/1.3
- Variant distribution in this bucket:

| variant_idx | count | accuracy |
| ---: | ---: | ---: |
| 0 | 35 | 0.5714 |
| 1 | 27 | 0.7037 |
| 2 | 18 | 0.6667 |
| 3 | 19 | 0.5263 |
| 4 | 21 | 0.6667 |
| 5 | 19 | 0.6316 |

- Representative hit examples:

  - `test-00022-v0` (correct, pred=7, target=7): Billy ithengisa ama-DVD. Unamakhasimende 8 ngoLwesibili. amakhasimende akhe 3 lokuqala ukuthenga DVD eyodwa ngamunye. amakhasimende akhe 2 olandelayo ukuthenga 2 DVD ngamunye. amakhasimende akhe 3 zokugcina musa ukuthenga noma iyiphi ama-DVD. Bangaki ama-DVD Billy wathengisa ngoLwesibili?
  - `test-00059-v1` (correct, pred=187, target=187): Kunezigaba 6, ngasinye siqukethe izithelo 20, kanye nezithelo ezengeziwe 67 ezihlakazekile esihlahleni sama-raspberry; zingaki ama-raspberries esewonke?
  - `test-00060-v0` (correct, pred=17, target=17): Inqwaba iqukethe amawolintshi 25 phakathi kwawo 1 angahlelekanga, 20% angavuthiwe, 2 amunyu kanti amanye mahle. Mangaki amawolintshi amahle?
  - `test-00060-v1` (correct, pred=17, target=17): Ebhasikidini kukhona 25 amawolintshi; 1 awo mabi, 20% awakavuthi, 2 amunyu, futhi asele mahle. Mangaki amawolintshi amahle?

### Source-Level Cases Where SID Selection Fixes Original v0

- source_idx `1`, selected variant `2`, target `3`, selected pred `3`
  - Original v0: Ingubo ithatha ama-bolts 2 enentambo eluhlaza okwesibhakabhaka nengxenye eningi eluhlaza okwesibhakabhaka.
  - Selected: Ukuze wenze ingubo udinga ama-bolts 2 enombala oluhlaza kanye nowobuciko obumhlophe olingana nengxenye yawo; zingaki ama-bolts esewonke?
- source_idx `3`, selected variant `2`, target `540`, selected pred `540`
  - Original v0: UJames unquma ukugijima 3 izikhathi ezingu- 3 ngesonto. Ugijima 60 amamitha ngesipikili ngasinye. Mangaki amamitha esewonke agijima ngesonto?
  - Selected: Uma uJames eqeda 3 sprints 60 amamitha ngamunye, futhi wenza lokhu 3 izikhathi ngesonto, yini ibanga lakhe lonke ngesonto ngamamitha?
- source_idx `5`, selected variant `4`, target `64`, selected pred `64`
  - Original v0: UKylar waya esitolo eyothenga izibuko zendlu yakhe entsha. Ingilazi eyodwa ibiza u-P0, kodwa ingilazi ngayinye yesibili ibiza u-P1 kuphela. UKylar ufuna ukuthenga izibuko zika-P2. Udinga ukukhokha malini ngazo? $5, 60% 16
  - Selected: Ukuze athenge ifulethi lakhe elisha, uKylar uzothenga izibuko 16. Intengo yengilazi ngayinye ingu- $5, kodwa ingilazi ngayinye yesibili ibiza 60% kuphela yale ntengo. Uzochitha malini? 2
- source_idx `6`, selected variant `5`, target `260`, selected pred `260`
  - Original v0: Toulouse has kabili izimvu eziningi kuno Charleston. Charleston has 4 izikhathi eziningi izimvu kuka Seattle. Zingaki izimvu Toulouse, Charleston, futhi Seattle babe ndawonye uma Seattle has 20 izimvu?
  - Selected: Seattle has 20 izimvu. Charleston sika izimvu count kuyinto 4 izikhathi Seattle sika, futhi Toulouse sika inani kabili Charleston sika. Yini isamba zonke izimvu kulezi zindawo ezintathu?
- source_idx `11`, selected variant `1`, target `694`, selected pred `694`
  - Original v0: UToula waya ebhikawozi wathenga izinhlobo ezihlukahlukene zokubhaka. Wathenga 3 amadonathi ayishumi nambili abiza $68 ngeshumi nambili, 2 amaminikhi ayishumi nambili abiza $80 ngeshumi nambili, 6 amaminikhi ayishumi nambili ama-cheesecake abiza $55 ngeshumi nambili. Yayibiza m...
  - Selected: UTou Toula wavakashela indawo yokubhaka futhi wathenga 3 amadonathi ayishumi ngentengo $68 ngeshumi, 2 amadonathi amancane ama-cupcake ngentengo $80 ngeshumi, 6 amadonathi amancane ama-chees cakes abiza $55 ngeshumi; ingakanani imali esetshenzisiwe?
