# Protocol: AI and the Opportunity Ladder

Version 1.1 (2026-11-25). Agents follow this document exactly.

## Question

Which career pathways open to young people from low-income families (especially those not
requiring a bachelor's degree) are most exposed to AI doing the work, which ones AI makes more
productive, and which rest on human relationships or physical presence? Results inform the
pathways mentors and programs steer youth toward, region by region.

## Task ratings (one object per O*NET task)

Rate each task **as it is performed today by a typical worker**, against **AI systems widely
available in late 2026**: large language models and AI agents that can read, write, analyze
data, code, search, see images and use common software. Do **not** assume general-purpose
robots; count robotics only where it is already common for that task. Judge the task as
written, not the whole job.

| Field | Values |
|---|---|
| `ai_alone` | `0` AI cannot do it (or only trivial pieces); `1` AI can do small parts but a person does most of it; `2` AI can do most of it, with a person checking or finishing; `3` AI can routinely do all of it to an acceptable standard without a person |
| `ai_speedup` | Time a worker would save on this task by using AI tools, at the same quality: `none`, `moderate` (some time saved, under about half), `large` (at least half the time saved) |
| `human_core` | How much the task's value depends on a human relationship: trust, care, persuasion, teaching, leadership, or in-person judgment that others must rely on and hold accountable: `0` not at all, `1` somewhat, `2` essential |
| `physical` | How much the task needs physical presence, manipulation or mobility in varied, real-world settings: `0` none, `1` some, `2` essential |
| `notes` | at most 8 words naming what the task acts on, in your own words (e.g. "patient vital signs", "invoice records") |

Anchors for `ai_alone` (apply strictly):
- `3` only when, in normal practice, the AI's output can be used **without a person reviewing it**
  (routine data entry, standard reports from structured data, scheduling, transcription,
  translation of routine text, simple code). Errors would be caught by routine checks.
- `2` when the AI does **most of the work** (a usable draft, analysis or result) and a person mainly
  reviews, corrects or signs off.
- **Decisions someone must be accountable for** (approving loans, diagnosing, sentencing, hiring,
  setting strategy, signing off on safety) are at most `2`, and `1` when the judgment itself is the
  task.
- Tasks done **with or on people in person** (teaching a class, counseling, nursing care, coaching)
  are at most `1`, even if AI can prepare materials.

Consistency rules:
- If `physical` is `2`, `ai_alone` is usually `0` or `1`.
- `ai_alone` of `3` usually means `ai_speedup` is `large`.
- Rate supervisory and coordinating tasks on what the person actually does (directing people
  is `human_core` 1-2; filling in schedules is not).

## Quality control

- `scripts/validate.py`: JSON, IDs match the batch, allowed values, word limits and the
  row-alignment check (notes must match their own task better than their neighbors').
- **Reliability:** 5 fixed batches (about 1,000 tasks) are rated a second time, independently, by
  the reference model; agreement and weighted kappa per field go to
  `output/rating_reliability.csv`.
- **External validation:** about 99.7% of tasks also appear in Eloundou et al. (2024), whose
  human annotators labeled whether an LLM could cut task time by at least half (E1) or could
  with extra software (E2). Our `ai_speedup = large` is compared with those labels at the task
  and occupation level. Their labels date from 2023, so some drift is expected and reported.
- The main pass uses Sonnet. Before external use, a person checks a sample of ratings.

## Changelog

- 1.0 (2026-11-25): initial protocol.
- 1.1 (2026-11-25): pilot (batch 2, 198 tasks) gave weighted kappa 0.60 on `ai_alone`, with Sonnet
  rating higher than the reference model (mean 1.70 vs 1.35). Strict anchors added for levels 2-3,
  accountable decisions and in-person tasks. The pilot was discarded and batch 2 was re-rated under
  1.1.
- 1.1a (2026-11-26): one main-pass agent (batch 32, postsecondary teachers) assigned ratings with a
  keyword rule table instead of rating tasks individually. Its agreement with the reference model on
  `physical` was 53% (main mean 0.14 vs 0.61). The batch was discarded and re-rated, and the prompt
  now forbids rule-based rating.
