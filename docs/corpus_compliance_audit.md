# Corpus Compliance Audit

This audit checks whether the current `RAG Docs` folder matches the asset expectations in the brief from `Brdge_WorkTest_DS_AI_RAG (1) (2).pdf`.

## In Plain English

I checked the folder as if I were packing 31 boxes, one for each required sub-facet in the brief.

For each box, I looked for:

- a transcript
- slides
- a worksheet/exercise
- posts

Why this matters:

- the brief assumes each sub-facet has its own set of learning materials
- if some materials are missing, the app must handle that honestly
- if filenames are messy, we need a mapping layer before building retrieval

## What I Found

- `31/31` sub-facets have a slide asset in `RAG Docs/Presentation materials/PDF Slides for Videos`
- `29/31` sub-facets have a direct worksheet/exercise match
- `0/31` sub-facets have an obvious transcript file in the current export
- `0/31` sub-facets have an obvious posts file in the current export
- `2/31` sub-facets are missing a direct worksheet match:
  - `Identifying a mentor or coach`
  - `People you can confide in`

## What This Means

The current corpus is strong enough to support a first version built around:

- sub-facet-specific slides
- sub-facet-specific worksheets/exercises
- assessment reports

But it does **not yet prove** that the corpus fully matches the brief's ideal asset model of:

- video transcript(s)
- slide text
- worksheet/exercises
- 2–3 posts per sub-facet

So the implementation should be built against the **real corpus**, not the idealized one, and should explicitly say when an asset type is unavailable.

## Naming Drift We Need To Normalize

Several files use different wording from the canonical brief names. This is normal, but it means we need a registry/mapping layer before ingestion and retrieval.

Examples:

- `Avoiding procrastination` appears as `Procrastination`
- `Managing emotions` appears as `Understanding and Managing Emotions`
- `A healthy and balanced diet` appears as `Improving Nutrition`
- `Quality sleep` appears as `Improving quality and length of Sleep` / `Quality of Sleep`
- `Recognising stress triggers` appears as `Stress Triggers`
- `Self-awareness` appears as `Self Awarenesss` in one slide filename
- `Taking regular exercise` appears under the misspelled folder `Taking Regular Ecercise`

## Coverage Matrix

| Facet | Sub-facet | Transcript | Slides | Worksheet/Exercises | Posts | Notes |
|---|---|---|---|---|---|---|
| Mindset | Adapting to change | No file found | `Adapting to Change Slides.pdf` | `Adapting to Change/Adapting to Change - Worksheet.pdf` | No file found | - |
| Mindset | Avoiding procrastination | No file found | `Procrastination Slides.pdf` | `Procrastination/(3 worksheet files)` | No file found | Slide/worksheet naming uses procrastination, not the canonical brief label. |
| Mindset | Focus on what you can control | No file found | `Focus on What You Can Control Slides.pdf` | `Focus on What You Can Control/Focus on What You Can Control - Worksheet.pdf` | No file found | - |
| Mindset | Keeping things in perspective | No file found | `Keeping Things in Perspective Slides.pdf` | `Keeping Things in Perspective/Keeping Things in Perspective - Worksheet.pdf` | No file found | - |
| Mindset | Managing perfectionism | No file found | `Managing Perfectionism Slides.pdf` | `Perfectionism/Perfectionism Worksheet.pdf` | No file found | - |
| Mindset | Perseverance | No file found | `Perseverance Slides.pdf` | `Perseverance/Perseverance - Worksheet.pdf` | No file found | - |
| Mindset | Positivity | No file found | `Positivity and Optimism Slides.pdf` | `Positivity and Optimism/(6 worksheet files)` | No file found | Folder uses `Positivity and Optimism`. |
| Mindset | Prioritisation | No file found | `Prioritisation Slides.pdf` | `Prioritisation/(4 files)` | No file found | - |
| Self-Perception | Self-confidence | No file found | `Self Confidence slides.pdf` | `Self-confidence/Self-confidence - Worksheet.pdf` | No file found | Filename casing/spelling drift only. |
| Self-Perception | Self-efficacy | No file found | `Self Efficacy Slides.pdf` | `Self-efficacy/(3 files)` | No file found | One worksheet in this folder is named `Imposter Syndrome`, so cross-label noise exists. |
| Purpose | Having a clear life direction | No file found | `Defining a clear Purpose or Direction in your Life Slides.pdf` | `Having a Clear Life Direction/(2 files)` | No file found | - |
| Purpose | Identifying clear goals | No file found | `Clear Goals Slides.pdf` | `Identifying Clear Goals/Identifying Clear Goals - Worksheet.pdf` | No file found | - |
| Purpose | Leveraging your strengths | No file found | `Leveraging your Strengths Slides.pdf` | `Leveraging Your Strengths/Identifying your Core Strengths Self-Evaluation - Worksheet.pdf` | No file found | - |
| Purpose | Understanding your core values | No file found | `Understand your core values slides.pdf` | `Understanding Your Core Values/(2 files)` | No file found | - |
| Health | A healthy and balanced diet | No file found | `Improving Nutrition Slides.pdf` | `A Healthy and Balanced Diet/A Healthy and Balanced Diet.pdf` | No file found | Slide title differs from canonical name. |
| Health | Quality sleep | No file found | `Improving quality and length of Sleep Slides.pdf` | `Quality of Sleep/(2 files)` | No file found | Slide/worksheet names differ from canonical name. |
| Health | Separating work from home | No file found | `Separating Work from Home Slides.pdf` | `Separating Work From Home/(2 files)` | No file found | - |
| Health | Taking regular exercise | No file found | `Taking Regular Exercise Slides.pdf` | `Taking Regular Ecercise/Taking regular Exercise Worksheet.pdf` | No file found | Worksheet folder misspells `Exercise`. |
| Health | Time to relax and recharge | No file found | `Taking Time to Relax and Recharge Slides.pdf` | `Time to Relax and Recharge/(3 files)` | No file found | - |
| Health | Work-life balance | No file found | `Work Life Balance Slides.pdf` | `Work-Life Balance/(2 files)` | No file found | - |
| Relationships | Asking for help | No file found | `Asking for Help Slides.pdf` | `Asking for Help/Asking for Help - Worksheet.pdf` | No file found | - |
| Relationships | Managing conflict | No file found | `Managing Conflict Slides.pdf` | `Managing Conflict/(2 files)` | No file found | - |
| Relationships | Managing emotions | No file found | `Managing Emotions Slides.pdf` | `Understanding and Managing Emotions/Understanding and Managing Emotions - Worksheet.pdf` | No file found | Worksheet folder uses a longer name than the canonical brief label. |
| Relationships | Recognising stress triggers | No file found | `Stress Triggers Slides.pdf` | `Stress Triggers/(2 files)` | No file found | Slide/worksheet names use `Stress Triggers`. |
| Relationships | Seeking feedback | No file found | `Feedback Slides.pdf` | `Seeking Feedback/Seeking Feedback Worksheet.pdf` | No file found | Slide title differs from canonical name. |
| Relationships | Self-awareness | No file found | `Self Awarenesss Slides.pdf` | `Self-awareness/Self-awareness_Worksheet.pdf` | No file found | Slide filename has a spelling error: `Awarenesss`. |
| Relationships | Self-esteem | No file found | `Self Esteem Slides.pdf` | `Self-esteem/Self-esteem - Worksheet 1.pdf` | No file found | - |
| Relationships | An established support network | No file found | `An Established Support Network Slides.pdf` | `Established Support Network/An Established Support Network - Worksheet (1).pdf` | No file found | - |
| Relationships | Identifying a mentor or coach | No file found | `Mentor or Coach slides.pdf` | No direct file found | No file found | No direct worksheet folder found for this sub-facet. |
| Relationships | People you can confide in | No file found | `Identifying People you can Trust and Confide in (Within Established Network)Slides.pdf` | No direct file found | No file found | No direct worksheet folder found for this sub-facet. |
| Relationships | Imposter syndrome | No file found | `Imposter Syndrome Slides.pdf` | `Imposter Syndrome/Imposter Syndrome - Worksheet.pdf` | No file found | - |

## Recommended Decision Before Building

Use this audit as the implementation gate:

1. Build the app around the assets we actually have: slides, worksheets, and reports.
2. Add a canonical registry that maps messy real filenames to the 31 brief-defined sub-facets.
3. Treat transcripts and posts as missing unless more files are provided.
4. Make the app respond honestly when an asset type is unavailable.
