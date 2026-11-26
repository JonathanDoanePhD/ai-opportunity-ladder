# 11 - AI and the Opportunity Ladder

**Question:** Which career pathways open to young people from low-income families, especially
those that don't require a bachelor's degree, are most exposed to AI doing the work? Which does
AI make more productive, and which rest on human relationships or physical presence? The
results are meant to inform which pathways mentors and programs steer youth toward.

**Status:** first pass complete (2026-11-26). All 18,797 O*NET 30.0 tasks across 923
occupations are rated and validated, and the analysis outputs are built. Next: a person
spot-checks a sample of ratings, and the pathway lists are reviewed with workforce and
career-counseling partners (see Next steps).

> **Exploratory, AI-assisted research.** Task ratings come from Claude agents following
> [docs/protocol.md](docs/protocol.md), with validation, a reference-model pass and comparison
> with published human labels. A task AI *can* do is not the same as a job lost: adoption,
> cost, regulation and demand decide that. All figures need verification against original
> sources before they go to funders or the public.

## Key findings

1. **The jobs AI can do most of are concentrated in work that requires a degree.** Weighting
   occupations by employment:

   | Jobs | Human-anchored | AI can do much of it | AI-augmented / mixed |
   |---|---|---|---|
   | All jobs | 48% | 27% | 24% |
   | Typically entered without a bachelor's | 63% | 19% | 17% |
   | Typically need a bachelor's or more | 26% | 39% | 34% |

   Postsecondary certificate jobs are the most human-anchored tier (71% of task importance),
   with median pay of about $52K. Higher pay goes only weakly with AI capability across
   occupations (r = 0.14) (`exposure_by_education.csv`, `fig_earnings_vs_ai.png`).
2. **The office "first rung" is where AI reaches youth pathways most.** About **17 million jobs
   open without a bachelor's** fall in the "AI can do much of it" group. The largest are:

   | Occupation | Jobs | Median pay (full-time) | Share of tasks AI can mostly do |
   |---|---|---|---|
   | Customer service representatives | 3.0M | $42K | 84% |
   | Secretaries and administrative assistants | 2.1M | $45K | 66% |
   | Office clerks | 1.3M | $42K | 71% |
   | Receptionists | 1.3M | $36K | 78% |
   | Bookkeeping clerks | 1.3M | $49K | 81% |

   These have long been the entry jobs that lead young people without a degree into
   white-collar careers.
3. **Many good jobs without a bachelor's are human-anchored.** Of 137 occupations typically
   entered without a bachelor's that pay at least the national full-time median ($60,192), 89
   are human-anchored, 26 mixed and 22 mostly AI-doable (`pathways_no_ba.csv`). Large
   human-anchored examples:
   - Electrical power-line installers ($92K)
   - MRI technologists ($86K)
   - Firefighters ($78K)
   - Respiratory therapists ($75K)
   - Aircraft mechanics ($74K)
   - Dental hygienists ($71K)
   - Radiologic technologists ($71K)
   - Crane operators ($71K)
   - Cardiovascular technologists ($66K)

   Good-paying jobs that AI can do much of include executive assistants, tax preparers,
   technical writers and production and expediting clerks.
4. **Short, affordable credentials lead to AI-resilient, decent-paying work**
   (`programs_to_pathways.csv`, College Scorecard national earnings five years out for students
   who had Pell grants):
   - Industrial equipment maintenance: $61-69K
   - Electrical and power transmission: $68K (associate)
   - Agricultural mechanization: $58-66K
   - Practical nursing: $57-60K
   - Vehicle maintenance and repair: $52-58K
   - HVAC: $49-58K

   In each case the target jobs have only 11-21% of tasks that AI can mostly do.
5. **Priority counties' jobs are less exposed, not more.** In Project 01's priority counties,
   the jobs-weighted share of work AI can mostly do is 30%, against 35% elsewhere, and 56% of
   work is human-anchored against 50%. Higher-need counties are less exposed overall (r = −0.35
   with Project 01's need index), because their jobs lean toward physical, care and service
   work (`county_exposure.csv`, `fig_county_exposure.png`). The risk there is less AI taking
   local jobs, and more that local youth are steered toward remote office work that AI is
   absorbing, while local hands-on trades and health jobs need credentials that are hard to
   reach nearby (Project 04).

## What this suggests for mentoring

- **Steer toward human-anchored credentials:** skilled trades, allied health (respiratory,
  imaging, dental hygiene), utilities, and public safety, through certificates and associate
  degrees. Mentors who work in these fields are the bridging ties that matter (Projects 02, 08).
- **Treat office entry jobs as stepping stones, not destinations.** Pair them with AI skills
  and a plan to move into roles that are mostly judgment, coordination or care.
- **Teach AI as a tool for every pathway.** Even in human-anchored jobs, about 15-25% of task
  importance is work AI speeds up (records, scheduling, diagnostics reading).

## Reliability and validation

- **Reference model** (`output/rating_reliability.csv`): 968 tasks in 5 fixed batches were
  rated independently by the reference model under protocol 1.1. Linearly weighted kappa:

  | Field | Weighted kappa | Exact agreement |
  |---|---|---|
  | AI can do it alone (0-3) | 0.79 | 80% |
  | AI speedup | 0.84 | 87% |
  | Human relationship | 0.78 | 81% |
  | Physical presence | 0.90 | 90% |

  The two models' ratings are within one point on 99.5% or more of tasks.
- **Human labels** (`output/external_validation.csv`): Eloundou et al. (2024) had human
  annotators label 18,740 of these tasks. Our "AI can mostly do it" share per occupation
  correlates **r = 0.80** (Spearman 0.83) with their share of tasks exposed to an LLM alone or
  with software (E1+E2), across all 923 occupations. Task-level agreement is moderate (kappa
  0.50), as expected given their 2023 labels and a different rubric.
- **Protocol changes during the run:**
  - **Version 1.1:** the pilot showed `ai_alone` at kappa 0.60, so anchors were tightened and
    the pilot re-rated.
  - **Version 1.1a:** one batch rated by keyword rules (physical agreement 53%) was discarded
    and re-rated, and rule-based rating is now forbidden.

## Data

| Source | What |
|---|---|
| O*NET 30.0 (CC BY 4.0) | 18,797 task statements and importance ratings; required education; job zones |
| ACS 2023 1-year tables B24121, B24114 | Median full-time earnings and employment by detailed occupation (national) |
| ACS 2019-2023 5-year table C24010 | County occupation mix (25 groups) |
| Census 2018 occupation crosswalk; NCES CIP-SOC crosswalk | Census occupations to SOC; college programs to occupations |
| College Scorecard field-of-study file | National median earnings five years out, all completers and Pell recipients, by program and credential |
| Eloundou et al. (2024), GPTs are GPTs (MIT) | Task-level human exposure labels, used for validation only |
| Project 01 | Priority counties and need index |

BLS wage files (OEWS) and projections were the original plan, but bls.gov refused downloads
from this environment on 2026-11-25 (HTTP 403). ACS summary files replace them, and no access
workaround was attempted.

## How it works

| Step | Script |
|---|---|
| Batches (about 200 tasks, whole occupations together) | `scripts/01_make_batches.py` |
| Occupation table (education, earnings, employment, county group) | `scripts/02_build_occupations.py` |
| Agent ratings (99 batches, Sonnet; 5 reference batches) | `scripts/workflows/rate.js` (see `RESUME.md`) |
| Reliability and external validation | `scripts/03_reliability.py` |
| Analysis | `scripts/04_analysis.py` |

Occupation shares are task-importance-weighted (O*NET importance):

| Share | Tasks counted |
|---|---|
| `ai_can_do` | `ai_alone` ≥ 2 |
| `ai_speeds` | `ai_alone` ≤ 1 with moderate or large speedup |
| `anchored` | `ai_alone` ≤ 1 and (`human_core` = 2 or `physical` = 2) |

Category: "AI can do much of it" if `ai_can_do` ≥ 0.5; "Human-anchored" if `anchored` ≥ 0.5;
otherwise "AI-augmented / mixed".

## Outputs

| File | What |
|---|---|
| `output/occupation_ai_profile.csv` | Per occupation: AI shares, category, typical education, job zone, median earnings, employment (with `census_occ_shared_by`) |
| `output/exposure_by_education.csv` | Employment-weighted AI profile by typical required education |
| `output/pathways_no_ba.csv` | Occupations typically entered without a bachelor's that pay at least the median, ranked by resilience |
| `output/programs_to_pathways.csv` | Certificate and associate programs, linked occupations' AI profile, national earnings (all and Pell) |
| `output/county_exposure.csv` | Per county: jobs-weighted AI shares from its occupation mix; priority flag |
| `output/rating_reliability.csv`, `external_validation.csv` | Reliability and validation |
| `output/occupation_match_report.csv` | How many occupations matched each source |
| `output/ladder_summary.json` | Headline numbers |
| `output/fig_earnings_vs_ai.png`, `fig_county_exposure.png` | Figures |
| `data/coded/main/`, `data/coded/reference/` | All task ratings |

## Rebuild

```bash
python3 -I scripts/fetch_data.py .
python3 -I scripts/01_make_batches.py
python3 -I scripts/02_build_occupations.py
# ratings: committed in data/coded/ (re-rating: see RESUME.md)
python3 -I scripts/03_reliability.py
python3 -I scripts/04_analysis.py
```

## Caveats

- **Capability, not displacement.** Ratings describe what AI systems widely available in late
  2026 could do with a task, not whether employers will adopt it, what it costs or how demand
  shifts. AI that makes a job more productive can grow or shrink employment.
- **Ratings come from AI models.** Agreement with a second model and with 2023 human labels is
  good but not proof. Ratings of AI by AI may carry shared blind spots.
- **Task lists are O*NET's,** which update slowly and describe typical, not local, jobs.
- **Earnings and employment** are ACS national medians for full-time year-round workers.
  - Where a Census occupation covers several O*NET occupations, they share its median, and
    its employment is split evenly (`census_occ_shared_by` > 1). Those job counts are rough.
  - Earnings are top-coded at about $250K.
- **County exposure uses 25 occupation groups,** so detailed local differences are smoothed.
- **"Typically entered without a bachelor's"** uses O*NET's required-education survey (under
  half of workers in the job need a bachelor's or more), and some occupations are borderline.
- **Program earnings** are national medians by program and credential, not for any particular
  college.

## Next steps

- **Human spot-check** of 100 random task ratings, stratified by rating.
- **Review the pathway lists** with workforce boards and career counselors, especially for
  rural priority regions, and add local wages when an accessible source is available.
- **Local programs:** link `programs_to_pathways.csv` to colleges within reach of priority
  counties, using Project 04's college distances, to give each priority area a short list of
  nearby credentials.
- **Track change:** re-rate yearly as AI capabilities change; the protocol and batches are
  reusable.

## License, citation and data terms

- **Code:** MIT (see `LICENSE`). **Outputs:** CC BY 4.0, subject to the source terms below.
- **Cite this project as:** JonathanDoanePhD (2026). *AI and the Opportunity Ladder*. https://github.com/JonathanDoanePhD/ai-opportunity-ladder
- **Data sources and terms** (from `data/sources.csv`; recorded versions and checksums in `data/sources.lock.csv`):

| Source | Terms |
|---|---|
| O*NET 30.0 Database (text files): task statements and ratings; education and job zones | CC BY 4.0 - cite O*NET 30.0 Database by the U.S. Department of Labor Employment and Training Administration (USDOL/ETA) |
| ACS 2023 1-year table B24121: detailed occupation by median earnings (full-time year-round) | Public domain (U.S. government work) |
| ACS 2023 1-year table B24114: detailed occupation (employment counts) | Public domain (U.S. government work) |
| ACS 2019-2023 5-year table C24010: sex by occupation (county job mix) | Public domain (U.S. government work) |
| ACS 2023 table shells (line labels) | Public domain (U.S. government work) |
| Census 2018 occupation codes to SOC 2018 crosswalk | Public domain (U.S. government work) |
| NCES/BLS CIP 2020 to SOC 2018 crosswalk (college programs to occupations) | Public domain (U.S. government work) |
| College Scorecard field-of-study file (earnings by credential and program) | Public domain (U.S. Department of Education) |
| Eloundou et al. (2024) GPTs are GPTs: task-level exposure labels (human and GPT-4) | MIT License (Copyright 2024 OpenAI); used for validation only |
| Eloundou et al. (2024) GPTs are GPTs: occupation-level exposure | MIT License (Copyright 2024 OpenAI); used for validation only |

Built with AI assistance (Claude). Exploratory research: every statistic needs checking against its original source
before it appears in funder reports, grant applications or public material.

## Status and limitations

Published 2026-11-26 as exploratory research. The analysis is complete and reproducible, but these checks have **not yet been done**, so treat figures as provisional:

- Statistics in this README and in `output/` have not been independently checked against their original sources.
- A person spot-checks about 100 task ratings.
- Review the pathway lists with workforce and career-counseling partners.
- O*NET is CC BY 4.0: keep the attribution.
