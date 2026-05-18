# Public source patch

This directory contains the public source-level patch corresponding to the decoder-control experiment.

`probe3_whisper_sequence_score.patch` shows the minimal `src/whisper.cpp` change used to add an experimental scoring surface inside `whisper_sequence_score`.

The patch is intentionally scoped to the sequence-scoring layer. It does not include model weights, audio files, transcript data, private experiment machinery, or broader research-selection logic.

The added control weights default to zero. With all weights unset or set to `0.0`, the modified score equals the original sequence score and baseline behavior is preserved.

The public control variables are:

- `PAPEREQ_WHISPER_PROBE=3`
- `PAPEREQ_WHISPER_WIGGLE_GAP`
- `PAPEREQ_WHISPER_WIGGLE_ENTROPY`
- `PAPEREQ_WHISPER_WIGGLE_LEN`

The tested score surface is:

`score_new = score_base + w_gap * (avg_logprobs - score_base) + w_entropy * entropy + w_len * log(1 + result_len)`
