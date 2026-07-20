# GSM8K Nepali SID Pipeline Worklog

Language: `npi_Deva`
Language name: `Nepali`
Input: `/root/gsm8k_nllb_direct/npi_Deva`
Output: `/root/gsm8k_single_language_experiment/npi_Deva`
Worker: `fdbd:dccd:cdc2:12c8:0:2d4::`, port `11373`

## 2026-07-17

- Read `/root/worker_ssh_notes (1).md` and resolved the worker SSH port from `/home/tiger/.ssh/known_hosts`.
- Verified worker SSH with `/home/tiger/.ssh/id_rsa`; worker sees 8 x H100.
- Confirmed large output/model entrypoints are symlinks to `/mnt/bn/search-gec-agentic-search-useast1b/guo`.
- Confirmed `/root/gsm8k_nllb_direct/npi_Deva` contains translated GSM8K parquet files.
- Prepared source data: train `7473`, test `1319`, total `8792`.
- Reused target-independent English rewrites from `swh_Latn`: unique OK records `8792`, source bad rows ignored `156`.
- During NLLB rewrite translation, noticed Nepali translations can localize placeholders such as `[P0]` to `[P०]`.
- Updated `/root/translate_gsm8k_nllb_direct.py` so placeholder restoration handles both ASCII and Devanagari placeholder digits before reconstructing final rewrites.

## Stage Status

- `prepare`: done
- `reuse English rewrites`: done
- `translate rewrites`: done
- `rewrite repair`: done
- `build variants`: done
- `extract hidden`: done
- `train RQ-VAE`: done
- `encode SIDs`: done
- `eval generate`: done
- `merge eval`: done
- `analyze`: done
- `LightGBM selectors`: done
- `metric backfill`: done
- `audit`: done

## Update 2026-07-17 18:05:04 UTC

- Reused complete target-independent English rewrite records for `npi_Deva` from `swh_Latn`.
- Unique OK English rewrite records: `8792`; target records: `8792`; source bad rows ignored: `156`.
- Wrote `/root/gsm8k_single_language_experiment/npi_Deva/rewrites_en/english_rewrite_records.jsonl` and `/root/gsm8k_single_language_experiment/npi_Deva/rewrites_en/reused_english_rewrite_meta.json`.

## Update 2026-07-17 18:54:14 UTC

- Rebuilt `/root/gsm8k_nllb_direct/npi_Deva` from the existing NLLB cache after fixing placeholder restoration.
- Cache rows: `71012`; unique source texts required: `71012`; missing: `0`.
- Backed up the previous direct translation directory to `/root/gsm8k_nllb_direct/npi_Deva.backup_before_placeholder_fix_1784314451`.
- Wrote rebuild metadata to `/root/gsm8k_nllb_direct/npi_Deva_placeholder_fix_meta.json`.

## Update 2026-07-17 18:59:33 UTC

- Rebuilt `/root/gsm8k_nllb_direct/npi_Deva` from the existing NLLB cache after fixing placeholder restoration.
- Cache rows: `71012`; unique source texts required: `71012`; missing: `0`.
- Backed up the previous direct translation directory to `/root/gsm8k_nllb_direct/npi_Deva.backup_before_placeholder_fix_1784314770`.
- Wrote rebuild metadata to `/root/gsm8k_nllb_direct/npi_Deva_placeholder_fix_meta.json`.

## Update 2026-07-17 19:04:39 UTC

- Rebuilt `/root/gsm8k_nllb_direct/npi_Deva` from the existing NLLB cache after fixing placeholder restoration.
- Cache rows: `71012`; unique source texts required: `71012`; missing: `0`.
- Backed up the previous direct translation directory to `/root/gsm8k_nllb_direct/npi_Deva.backup_before_placeholder_fix_1784315076`.
- Wrote rebuild metadata to `/root/gsm8k_nllb_direct/npi_Deva_placeholder_fix_meta.json`.

## Update 2026-07-17 19:09:29 UTC

- Reused complete target-independent English rewrite records for `npi_Deva` from `swh_Latn`.
- Unique OK English rewrite records: `8792`; target records: `8792`; source bad rows ignored: `156`.
- Wrote `/root/gsm8k_single_language_experiment/npi_Deva/rewrites_en/english_rewrite_records.jsonl` and `/root/gsm8k_single_language_experiment/npi_Deva/rewrites_en/reused_english_rewrite_meta.json`.

## Update 2026-07-17 19:13:26 UTC

- Added fallback repairs for `716` Nepali rewrite records that failed NLLB number/script validation.
- Repair method: append missing original number tokens when possible; otherwise wrap the original Nepali question in a short Nepali prompt.
- These repairs are intended to keep the variant table complete; they are lower-diversity fallback variants and should be treated as such in audit notes.
- Wrote repair records to `/root/gsm8k_single_language_experiment/npi_Deva/rewrites/fallback_repaired_nepali_rewrites.jsonl` and appended them to `/root/gsm8k_single_language_experiment/npi_Deva/rewrites/rewrite_records.jsonl`.
- Backup before append: `/root/gsm8k_single_language_experiment/npi_Deva/rewrites/rewrite_records.jsonl.backup_before_npi_fallback_repair_1784315606`.

## Final Summary 2026-07-18

- Completed the end-to-end `npi_Deva` GSM8K low-resource SID pipeline under `/root/gsm8k_single_language_experiment/npi_Deva`.
- Final audit: `ok=true` in `/root/gsm8k_single_language_experiment/npi_Deva/audit_report.json`.
- Source rows: train `7473`, test `1319`, total `8792`.
- Variant rows: train `44838`, test `7914`, total `52752`.
- Hidden states: shape `[52752, 33, 4096]`, missing rows `0`.
- SIDs: shape `[52752, 33, 3]`.
- Eval rows: `52752 / 52752`, missing rows `0`.
- Overall strict accuracy: `0.34029041552926903`.
- Overall relaxed last-number accuracy: `0.3791135881104034`.
- Overall strict-else-relaxed accuracy: `0.3790946314831665`.
- Test original variant strict accuracy: `0.3297952994692949`; strict-else-relaxed accuracy: `0.3616376042456406`.
- SID rules selected test strict accuracy: `0.38817285822592873`; strict-else-relaxed accuracy: `0.4268385140257771`.
- LightGBM all-level and no-level0 selected test strict accuracy: `0.378316906747536`; strict-else-relaxed accuracy: `0.4086429112964367`.
- Transparent SID rules beat both LightGBM variants on selected-test strict and strict-else-relaxed metrics.

Important quality notes:

- The direct Nepali source was rebuilt from `/root/gsm8k_nllb_direct/.cache/eng_Latn__npi_Deva.jsonl` after fixing placeholder restoration for NLLB outputs such as `[P०]` and unlabeled `[०]`.
- Some NLLB source translations remain low quality even after placeholder repair, including cases compressed to short numeric strings or page-marker artifacts such as `[पृष्ठ २३]`.
- `716` rewrite records required fallback repair to keep the variant table complete. These variants are lower-diversity fallbacks, not high-quality independent paraphrases.
- Final selected-test metric reports are in `/root/gsm8k_single_language_experiment/npi_Deva/eval/test_selected_metric_summary.json` and `/root/gsm8k_single_language_experiment/npi_Deva/eval/test_selected_metric_comparison.md`.
- Selector comparison summary is in `/root/gsm8k_single_language_experiment/npi_Deva/analysis_lgbm_comparison.md`.
