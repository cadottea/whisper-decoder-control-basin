# ASR engineering brief

This repository is a compact public case study in source-level ASR decoder experimentation.

It is intended to show practical ability to work inside an ASR decoder, design a controlled scoring intervention, evaluate word error rate changes, and report results without overstating the evidence.

## One-sentence summary

A zero-default source-level scoring surface was added inside `whisper.cpp`'s `whisper_sequence_score`, producing stable WER/error-count reductions on several tested hard-manifest/model surfaces while also exposing neutral and worse regions.

## What was actually changed

The intervention was added directly inside:

`src/whisper.cpp`

in:

`whisper_sequence_score`

This is the function where token-level log probabilities are reduced into final sequence-level scores used for candidate ranking.

The public patch is:

`../patches/probe3_whisper_sequence_score.patch`

The tested control surface was:

`score_new = score_base + w_gap * (avg_logprobs - score_base) + w_entropy * entropy + w_len * log(1 + result_len)`

The patch is zero-default. If the control weights are unset or set to `0.0`, then `score_new == score_base`, preserving baseline behavior.

## Why this is relevant to ASR engineering

This case study demonstrates several skills that matter for speech-recognition systems:

- locating the correct decoder scoring layer rather than tuning an external wrapper
- modifying production-style C++ inference code with a minimal patch
- preserving baseline behavior with zero-default controls
- designing parameter sweeps over decoder-control axes
- evaluating changes using word-level edit counts and WER
- separating improvement regions from neutral and worse regions
- reporting both positive and negative outcomes
- documenting reproducibility boundaries clearly

The main engineering point is not that this is a universal decoding rule. The point is that a small source-level scoring surface exposed measurable, structured decoder behavior.

## Public results

The public aggregate results include:

| Model / surface | Baseline errors | Selected errors | Delta | Relative reduction |
|---|---:|---:|---:|---:|
| tiny, fold 0 → 1 | 972 | 922 | -50 | 5.14% |
| tiny, fold 1 → 0 | 928 | 865 | -63 | 6.79% |
| base, fold 0 → 1 | 771 | 740 | -31 | 4.02% |
| base, fold 1 → 0 | 769 | 755 | -14 | 1.82% |
| small, small-specific hard manifest | 48 | 42 | -6 | 12.50% |
| small, tiny-original hard manifest | 28 | 25 | -3 | 10.71% |
| medium, small-specific hard manifest | 17 | 14 | -3 | 17.65% |
| medium, tiny-original hard manifest | 10 | 10 | 0 | 0.00% |
| medium, medium-specific hard manifest | 42 | 36 | -6 | 14.29% |

The medium / tiny-original hard-manifest case is important because it did not improve. That neutral result helps show that the method is not being presented as universally positive.

## Basin interpretation

The strongest public visualization is:

`../figures/source_level_basin_public_map.png`

That figure collapses over `w_gap`, which was mostly inactive in the public sweeps, and shows the visible control surface over:

`w_entropy × w_len`

The map shows:

- connected tied-best regions where the control surface worked best
- broader improved regions that reduced WER but were not tied-best
- neutral regions
- worse regions
- untested regions

This supports a limited claim: the decoder intervention exposed a low-dimensional, partially degenerate control basin on the tested surfaces.

## What this does not claim

This repository does not claim:

- universal ASR improvement
- superiority on broad benchmarks
- a production-ready decoding rule
- replacement for large-scale ASR evaluation
- that every dataset or model size improves

The evidence supports a narrower claim:

A source-level sequence-scoring intervention inside `whisper.cpp` exposed stable local improvement regions on the tested manifests and model sizes.

## How I would extend this in a production ASR setting

The next engineering steps would be:

1. Run the same source-level control surface on larger and more diverse evaluation sets.
2. Stratify results by utterance length, acoustic difficulty, baseline confidence, and error type.
3. Add candidate-margin diagnostics to determine when the scoring surface can safely alter ranking.
4. Replace static parameter sweeps with a conservative runtime policy that activates only in validated uncertainty regimes.
5. Measure latency, memory, and throughput impact under realistic batch and streaming constraints.
6. Compare against standard decoding controls such as beam size, length penalty, temperature fallback, and confidence thresholds.
7. Keep the intervention zero-default and feature-flagged until validated on production-scale regression suites.

## Interview summary

This project is best described as:

“I modified the C++ sequence-scoring layer of `whisper.cpp`, added a zero-default decoder-control surface, and evaluated WER changes across several model/hard-manifest surfaces. The result was not universal, but it exposed connected improvement regions and clear failure regions. The project demonstrates source-level ASR decoder work, controlled experimentation, WER evaluation, and careful reporting.”

