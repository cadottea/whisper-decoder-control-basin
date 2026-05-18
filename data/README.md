# Public data files

This directory contains aggregate public result tables for the Whisper decoder-control basin report.

No model weights, audio files, full transcripts, or private experiment machinery are included here.

## Files

| File | Purpose |
|---|---|
| `public_result_summary.csv` | Compact table used for the README key-results table. |
| `heldout_selector_summary.csv` | Held-out selector summary for tiny/base experiments. |
| `small_dual_manifest_summary.csv` | Small-model Probe 3 parameter-basin sweep summary. |
| `medium_dual_manifest_summary.csv` | Medium-model transfer sweep summary on previously defined hard manifests. |
| `medium_specific_hard_summary.csv` | Medium-model sweep summary on the medium-specific hard manifest. |

## Common columns

| Column | Meaning |
|---|---|
| `result_group` | Public result category, such as `heldout_selector` or `parameter_basin`. |
| `model` | Whisper model or model-size label used for the public row. |
| `dataset` | Fold or hard-manifest label used for the evaluation. |
| `case` | Parameter setting or baseline row name. Probe 3 cases encode control weights. |
| `baseline_errors` | Word-level edit errors for baseline decoding. |
| `selected_errors` | Word-level edit errors for the selected control state. |
| `delta_errors` | Selected errors minus baseline errors. Negative means fewer errors than baseline. |
| `edits` | Word-level edit count for a specific row in a sweep summary. |
| `words` | Number of reference words in the evaluated manifest. |
| `wer` | Word error rate, computed as `edits / words`. |
| `delta_edits_vs_baseline` | Edit-count change relative to baseline. Negative means improvement. |
| `relative_reduction` | Relative error reduction for compact public summaries. |
| `rel_reduction_vs_baseline` | Relative error reduction in sweep summaries. |
| `wall_sec` | Wall-clock runtime in seconds for the row, where available. |
| `whisper_total_ms` | Whisper-reported total runtime in milliseconds, where available. |
| `note` | Short human-readable note about the row. |

## Probe 3 parameter names

Probe 3 sweep cases use names like:

`probe3_wg-0.8_we0.0_wl1.2`

These encode:

| Token | Meaning |
|---|---|
| `wg` | `w_gap`, the score-gap weight. |
| `we` | `w_entropy`, the entropy weight. |
| `wl` | `w_len`, the sequence-length weight. |

The tested source-level scoring surface is documented in `../patches/probe3_whisper_sequence_score.patch`.
