# SID Surface-Form Paper Cases

This is a compact, paper-facing version of `/root/gsm8k_sid_surface_case_study.md`.
It highlights cases where high-uplift SID buckets correspond to visible surface-form differences, plus examples where SID selection fixes the original translated question.

## Main Observation

Across the six languages, high-uplift SID buckets often correspond to questions that are shorter, less repetitive, and have clearer numeric anchors. This is most visible in low-resource/noisy translations such as Nepali, Sinhala, Yoruba, and Zulu. In Swahili and Somali, the distinction is subtler, but the high-uplift buckets still capture cleaner arithmetic word-problem forms.

## One Representative SID Bucket Per Language

| lang | SID rule | train acc/uplift | test hit acc | test miss acc | visible surface pattern |
| --- | --- | ---: | ---: | ---: | --- |
| npi_Deva | L19-K2-SID140 | 0.656 / +0.312 | 0.702 | 0.353 | shorter questions (26.6 vs 32.7 tokens); less repetition (max run 1.0 vs 1.8) |
| sin_Sinh | L20-K2-SID206 | 0.571 / +0.275 | 0.509 | 0.312 | shorter questions (30.7 vs 36.5 tokens); less repetition (max run 1.2 vs 2.5) |
| som_Latn | L27-K2-SID210 | 0.656 / +0.296 | 0.670 | 0.370 | shorter questions (34.5 vs 39.5 tokens); less repetition (max run 1.0 vs 2.2) |
| swh_Latn | L29-K2-SID148 | 0.782 / +0.294 | 0.802 | 0.500 | a latent cluster whose coarse lexical features are subtle |
| yor_Latn | L20-K2-SID166 | 0.554 / +0.332 | 0.371 | 0.231 | shorter questions (36.3 vs 44.2 tokens); more explicit numeric anchors (4.1 vs 3.4); less repetition (max run 1.1 vs 3.7) |
| zul_Latn | L17-K2-SID47 | 0.603 / +0.296 | 0.576 | 0.310 | shorter questions (20.8 vs 27.5 tokens) |

## Language-Level Case Notes

### npi_Deva

Representative high-uplift rule: `layer=19, level=2, sid=140`.
On test variants, this bucket has strict-else-relaxed accuracy `0.702` versus `0.353` outside the bucket.
Surface pattern: shorter questions (26.6 vs 32.7 tokens); less repetition (max run 1.0 vs 1.8).

Representative bucket hits:

- `test-00049-v3` (correct, pred=30, target=30): रिचर्डको भवनमा 15 तहहरू छन्, प्रत्येक तहमा 8 एकाइहरू छन्, र कुल एकाइहरूको 3/4 हाल ओगटेका छन्। खाली एकाइहरूको कुल संख्या निर्धारण गर्नुहोस्।
- `test-00055-v0` (correct, pred=14, target=14): 30 ललिपपपहरू जीनसँग छन्। जीनले ललिपपपहरूको 2 खान्छ। बाँकी ललिपपपहरूसँग, जीनले 2 ललिपपपहरू एउटा झोलामा प्याक गर्न चाहन्छ। कति झोलाहरू जीनले भर्न सक्छ?
- `test-00060-v4` (correct, pred=17, target=17): 25 नारंगी एक टोकरीमा छन्; 1 खराब छ, 20% अपरिपक्व छ, 2 खट्टा छ, र बाँकी राम्रो छ। राम्रो नारंगीको संख्या निर्धारण गर्नुहोस्।

Selection fixes original v0:

- source_idx `17`, selected variant `2`, target `57500`, selected pred `57500`
  - Original v0: यदि उनले 50 हप्ता एक वर्ष, 35 घण्टा एक हप्ता शिक्षक र 15 घण्टा एक हप्ता कोचको रूपमा काम गर्दछ भने, उनको वार्षिक तलब के हो? $20 $30
  - SID-selected variant: यदि जिल्लको प्रति घण्टा शुल्क $20 शिक्षण र $30 चीयरलिड कोचिंगको लागि हो, र उनले 35 शिक्षण घण्टा र 15 कोचिंग घण्टा हरेक हप्ता 50 हप्ताको लागि राख्छिन्, उसले वार्षिक कति कमाउँछ?
- source_idx `18`, selected variant `4`, target `7`, selected pred `7`
  - Original v0: 4 हप्तामा कति दर्जन अण्डा खानुहुन्छ? 3
  - SID-selected variant: 4 हप्ता पछि क्लेयरले कति दर्जन अण्डा खान्छ यदि उनी हरेक बिहान 3 अण्डा ओम्लेट बनाउँछिन्?

### sin_Sinh

Representative high-uplift rule: `layer=20, level=2, sid=206`.
On test variants, this bucket has strict-else-relaxed accuracy `0.509` versus `0.312` outside the bucket.
Surface pattern: shorter questions (30.7 vs 36.5 tokens); less repetition (max run 1.2 vs 2.5).

Representative bucket hits:

- `test-00003-v2` (correct, pred=540, target=540): ජේම්ස් 3 ස්ප් රින්ට් එක සම්පූර්ණ කරනවා නම්, 60 මීටර් එකකට, ඔහු මෙය 3 සතියකට වතාවක් කරනවා නම්, ඔහුගේ සතිපතා මුළු දුර මීටර් වලින් කීයද?
- `test-00036-v2` (correct, pred=75, target=75): ටෙරී දිනපතා 2 යෝගට් ආහාරයට ගනී නම් සහ සාප්පුව 4 යෝගට් විකිණීම $5.00 සඳහා නම්, ඔහු දින 30 තුළ යෝගට් සඳහා කොපමණ මුදලක් වියදම් කරයිද?
- `test-00055-v3` (correct, pred=14, target=14): ජින්ට මුලින් 30 ලූසිප්ස් තියෙනවා. ඇය 2, පරිභෝජනය කරනවා, පසුව ඉතිරි ටික 2 ලූසිප්ස් එකකට දාගන්න බෑග් වලට දාන්න හදනවා. බෑග් කීයක් පුරවන්න පුළුවන්ද?

Selection fixes original v0:

- source_idx `3`, selected variant `2`, target `540`, selected pred `540`
  - Original v0: ජේම්ස් තීරණය කරනවා 3 ස්ප් රින්ට් 3 සතියකට වතාවක් දුවන්න. ඔහු 60 මීටර් එක් එක් ස්ප් රින්ට් එකකට දුවනවා. ඔහු සතියකට දුවන්නේ මීටර් කීයක්ද?
  - SID-selected variant: ජේම්ස් 3 ස්ප් රින්ට් එක සම්පූර්ණ කරනවා නම්, 60 මීටර් එකකට, ඔහු මෙය 3 සතියකට වතාවක් කරනවා නම්, ඔහුගේ සතිපතා මුළු දුර මීටර් වලින් කීයද?
- source_idx `5`, selected variant `1`, target `64`, selected pred `64`
  - Original v0: කයිලර් ඔහුගේ නව නිවස සඳහා වීදුරු මිලදී ගැනීමට සාප්පුවට ගියේය. එක් වීදුරුවකට $5, මිල වන නමුත් සෑම දෙවන වීදුරුවකටම මිලෙන් 60% පමණි. කයිලර්ට 16 වීදුරු මිලදී ගැනීමට අවශ් යයි. ඔහු ඒවා සඳහා කොපමණ මුදලක් ගෙවිය යුතුද?
  - SID-selected variant: කයිලාර් ඔහුගේ නව නිවස සඳහා වීදුරු මිලදී ගැනීමට සාප්පුවකට ගියේය. සාමාන් යයෙන් එක් වීදුරුවකට $5, මිල වන නමුත් සෑම දෙවන වීදුරුවකටම එම මිලෙන් 60% පමණි. ඔහුට 16 වීදුරු අවශ් ය නම්, ඔහු මුළු වශයෙන් කොපමණ මුදලක් ගෙවනු ඇත්ද?

### som_Latn

Representative high-uplift rule: `layer=27, level=2, sid=210`.
On test variants, this bucket has strict-else-relaxed accuracy `0.670` versus `0.370` outside the bucket.
Surface pattern: shorter questions (34.5 vs 39.5 tokens); less repetition (max run 1.0 vs 2.2).

Representative bucket hits:

- `test-00024-v1` (correct, pred=26, target=26): Kyle wuxuu iibsaday buugga ugu iibka badan sanadkii hore $19.50, taas oo ka tarjumaysa qiimo dhimis 25% qiimaha asalka ah.
- `test-00026-v1` (correct, pred=243, target=243): M Mish Mishka wuxuu iibsaday 3 labo shorts midkiiba $16.50, 3 labo surwaal midkiiba $22.50, iyo 3 laba kabood midkiiba $42 Immisa doolar ayuu Mishka ku bixiyay?
- `test-00026-v4` (correct, pred=243, target=243): M Mishka wuxuu tagay dukaameysiga wuxuuna iibsaday 3 labo shorts ah $16.50 qofkiiba, 3 labo surwaal ah $22.50 qofkiiba, iyo 3 labo kabo ah $42 qofkiiba.

Selection fixes original v0:

- source_idx `10`, selected variant `5`, target `366`, selected pred `366`
  - Original v0: Barnaamij cusub ayaa lahaa 60 downloads bishii ugu horeysay. tirada downloads ee bisha labaad ahaa saddex jeer ka badan downloads ee bishii ugu horeysay, laakiin ka dibna hoos u by 30% ee bisha saddexaad. Immisa downloads ayaa barnaamijka lahaa guud ahaan s...
  - SID-selected variant: Bilkii ugu horeeyay waxaa la arkay 60 downloads barnaamijka cusub. bisha labaad waxay lahayd saddex jeer downloads bisha ugu horeysay, laakiin downloads bisha saddexaad ayaa hoos u dhacay 30%. waa maxay tirada guud ee downloads saddexda bilood?
- source_idx `13`, selected variant `5`, target `18`, selected pred `18`
  - Original v0: Melanie waa qof guryaha iibisa. waxay sadex meelood meel ka iibisay qalabkeeda wax lagu nadiifiyo guriga cagaaran, 2 waxay iibisay in ka badan guriga cas, iyo badhka waxa ka haray guriga orange. hadii Melanie ay haysato qalab wax lagu nadiifiyo guriga orang...
  - SID-selected variant: Melanie, oo ka shaqeysa albaab ilaa albaab, waxay saddex meelood meel ka mid ah wasakhdaha ay ku iibisay guriga cagaaran, ka dibna 2 waxay ku iibisay guriga cas, ka dibna waxay ku iibisay badhka kaydka haray guriga orange. Maaddaama ay haysato 5 wasakhdaha ...

### swh_Latn

Representative high-uplift rule: `layer=29, level=2, sid=148`.
On test variants, this bucket has strict-else-relaxed accuracy `0.802` versus `0.500` outside the bucket.
Surface pattern: a latent cluster whose coarse lexical features are subtle.

Representative bucket hits:

- `test-00026-v2` (correct, pred=243, target=243): M Mishka alinunua jozi 3 ya shorts kwa bei $16.50 kwa jozi, 3 jozi za suruali kwa bei $22.50 kwa jozi, na 3 jozi za viatu kwa bei $42 kwa jozi. Ni kiasi gani cha jumla kilichotumiwa?
- `test-00046-v4` (correct, pred=163, target=163): Kazini Candice aliweka post-it note moja kwenye kila kikombe kati ya vikombe 220. Alikuwa na 80 notes awali na alinunua package njiani. Kama mwishoni alibaki na 23, package ilikuwa na notes ngapi?
- `test-00090-v2` (correct, pred=225, target=225): Katika picnic, kila adult dinosaur atakula 10 lbs za potato salad na kila child dinosaur atakula 5 lbs. Kwa adults 20 na children 5, jumla ya salad inayohitajika ni ngapi?

Selection fixes original v0:

- source_idx `1`, selected variant `4`, target `3`, selected pred `3`
  - Original v0: Kanzu inahitaji vifungo 2 vya nyuzi za bluu na nusu ya nyuzi nyeupe.
  - SID-selected variant: Ikiwa kanzu ina vifungo 2 vya nyuzi za bluu na nusu ya vifungo vingi vya nyuzi nyeupe, jumla ya vifungo ni ngapi?
- source_idx `5`, selected variant `1`, target `64`, selected pred `64`
  - Original v0: Kylar alikwenda duka kununua glasi kwa ajili ya nyumba yake mpya. glasi moja gharama $5, lakini kila glasi pili gharama tu 60% ya bei. Kylar anataka kununua glasi 16. ni kiasi gani yeye haja ya kulipa kwa ajili yao?
  - SID-selected variant: Ky Kylar alikwenda duka kununua glasi kwa ajili ya nyumba yake mpya; kila glasi kawaida gharama $5, lakini kila glasi pili gharama tu 60% ya bei hiyo. Kama anataka 16 glasi, ni kiasi gani yeye kulipa kwa jumla?

### yor_Latn

Representative high-uplift rule: `layer=20, level=2, sid=166`.
On test variants, this bucket has strict-else-relaxed accuracy `0.371` versus `0.231` outside the bucket.
Surface pattern: shorter questions (36.3 vs 44.2 tokens); more explicit numeric anchors (4.1 vs 3.4); less repetition (max run 1.1 vs 3.7).

Representative bucket hits:

- `test-00058-v4` (correct, pred=57, target=57): Níwọ̀n bí Stephen ti ń san $40.00 fún àwọn nǹkan ìnáwó rẹ̀, ó wá fi owó 25% kún owó tí wọ́n ń san fún un, ó tún fi owó $3.00 kún owó tí wọ́n ń san fún un, ó sì fi owó $4.00 kún owó tí wọ́n ń san fún un.
- `test-00072-v5` (correct, pred=221, target=221): Ṣe àròpọ̀ iye tí Tommy rí gbà nígbà tó ta 43 búrẹ́dì fún $3 ẹnì kọ̀ọ̀kan àti 23 ìyàngbẹ cheesecake fún $4 ẹnì kọ̀ọ̀kan.
- `test-00090-v1` (correct, pred=225, target=225): Ted tó jẹ́ ọmọ T-Rex ń se satelaiti fún àpèjẹ àwọn ẹranko tó ń jẹ́ dinosaur. Ó mọ̀ pé àwọn ẹranko tó ti dàgbà máa ń jẹ 10 lbs satelaiti, nígbà tí àwọn ọmọ dinosaur máa ń jẹ ìdajì iye yẹn. Bí àwọn àgbàlagbà 20 àtàwọn ọmọ 5 bá wà níbẹ̀, iye kíláàsì satelaiti ...

Selection fixes original v0:

- source_idx `0`, selected variant `4`, target `18`, selected pred `18`
  - Original v0: Janet ń jẹ mẹ́ta nínú wọn fún àárọ̀, ó sì ń ṣe àpò fún àwọn ọ̀rẹ́ rẹ̀ lójoojúmọ́ pẹ̀lú mẹ́rin. Ó ń ta èyí tó ṣẹ́ kù lójoojúmọ́ ní ọjà àgbẹ̀ fún $2 fún ẹyin kan tí wọ́n fi ṣe àdàpọ̀. 16
  - SID-selected variant: Jan Janet ń fi 16 ẹyin sílẹ̀ lójoojúmọ́; lẹ́yìn tó jẹ mẹ́ta fún oúnjẹ àárọ̀ àti tó ṣe àwọn búrẹ́dì mẹ́rin fún àwọn ọ̀rẹ́ rẹ̀, ó ta àwọn ẹyin tó ṣẹ́ kù ní $2 ní ọjà àwọn àgbẹ̀.
- source_idx `3`, selected variant `2`, target `540`, selected pred `540`
  - Original v0: James pinnu láti sáré 3 ìje 3 ní ìgbà kan lọ́sẹ̀. Ó sáré 60 mítà ní ìje kọ̀ọ̀kan.
  - SID-selected variant: Bí James bá ṣe 3 sprint tó ní 60 mítà ní ẹnì kọ̀ọ̀kan, tó sì ṣe èyí 3 ní ìgbà mélòó lọ́sẹ̀, kí ni iye ibi tó ń rìn ní gbogbo ọ̀sẹ̀ ní mítà?

### zul_Latn

Representative high-uplift rule: `layer=17, level=2, sid=47`.
On test variants, this bucket has strict-else-relaxed accuracy `0.576` versus `0.310` outside the bucket.
Surface pattern: shorter questions (20.8 vs 27.5 tokens).

Representative bucket hits:

- `test-00003-v2` (correct, pred=540, target=540): Uma uJames eqeda 3 sprints 60 amamitha ngamunye, futhi wenza lokhu 3 izikhathi ngesonto, yini ibanga lakhe lonke ngesonto ngamamitha?
- `test-00005-v4` (correct, pred=64, target=64): Ukuze athenge ifulethi lakhe elisha, uKylar uzothenga izibuko 16. Intengo yengilazi ngayinye ingu- $5, kodwa ingilazi ngayinye yesibili ibiza 60% kuphela yale ntengo. Uzochitha malini? 2
- `test-00011-v1` (correct, pred=694, target=694): UTou Toula wavakashela indawo yokubhaka futhi wathenga 3 amadonathi ayishumi ngentengo $68 ngeshumi, 2 amadonathi amancane ama-cupcake ngentengo $80 ngeshumi, 6 amadonathi amancane ama-chees cakes abiza $55 ngeshumi; ingakanani imali esetshenzisiwe?

Selection fixes original v0:

- source_idx `1`, selected variant `2`, target `3`, selected pred `3`
  - Original v0: Ingubo ithatha ama-bolts 2 enentambo eluhlaza okwesibhakabhaka nengxenye eningi eluhlaza okwesibhakabhaka.
  - SID-selected variant: Ukuze wenze ingubo udinga ama-bolts 2 enombala oluhlaza kanye nowobuciko obumhlophe olingana nengxenye yawo; zingaki ama-bolts esewonke?
- source_idx `3`, selected variant `2`, target `540`, selected pred `540`
  - Original v0: UJames unquma ukugijima 3 izikhathi ezingu- 3 ngesonto. Ugijima 60 amamitha ngesipikili ngasinye. Mangaki amamitha esewonke agijima ngesonto?
  - SID-selected variant: Uma uJames eqeda 3 sprints 60 amamitha ngamunye, futhi wenza lokhu 3 izikhathi ngesonto, yini ibanga lakhe lonke ngesonto ngamamitha?

## How To Use In The Paper

- Use the table above as evidence that SID buckets are not arbitrary labels: many align with shorter, cleaner, less repetitive surface forms.
- Use one or two source-level examples to illustrate the mechanism: the original translation loses or obscures constraints, while the selected variant states the same numbers and relations more explicitly.
- Avoid claiming that every SID is human-interpretable. The safer claim is that high-uplift SID regions partially align with visible surface-form quality, while also capturing latent features not fully explained by simple lexical metrics.
