# Activation Steering for Truthfulness — Research Report

## Abstract

Large language models can produce fluent answers that are factually incorrect, accept false premises, express unsupported certainty, or fabricate information when a question is ambiguous or unanswerable. This project investigates whether **activation steering** can improve truthfulness-related behavior at inference time without modifying model parameters.

The experiment evaluates three steering conditions: **α=0** (baseline), **α=1** (moderate steering), and **α=2** (stronger steering). A benchmark of **150 questions** was evaluated across five categories: false premise, unanswerable, future prediction, ambiguous, and adversarial questions.

Overall accuracy increased from **32.67% at α=0** to **42.00% at α=1** and **60.00% at α=2**. The α=2 condition therefore produced an absolute improvement of **27.33 percentage points** over baseline. Paired McNemar tests indicated that both the α=1 and α=2 improvements were statistically significant, with the α=2 comparison producing an exact p-value of approximately **1.0 × 10⁻¹¹**.

However, quantitative accuracy alone does not establish genuine epistemic improvement. A qualitative audit identified **42 apparent corrections** under α=2. Of these, **15 were classified as genuine epistemic improvements, 2 as problematic, and 25 as unclear**. Thus, the results provide evidence that activation steering can substantially alter truthfulness-related benchmark performance, while also demonstrating the importance of qualitative evaluation when measuring truthfulness.

---

# 1. Introduction

Large language models are capable of generating highly fluent and convincing responses even when the underlying information is uncertain, unavailable, or false.

This creates an important problem for trustworthy AI systems.

A model may:

- Accept a false premise instead of challenging it.
- Invent information about undocumented historical events.
- Present future predictions as facts.
- Arbitrarily answer questions with no objective answer.
- Repeat common misconceptions.
- Produce plausible but unsupported explanations.

These behaviors are particularly important in applications where users rely on language models for factual information or decision support.

Traditional methods for improving model behavior often involve changing model parameters through fine-tuning, preference optimization, reinforcement learning, or related techniques.

This project investigates a different approach:

> **Can model behavior be changed by steering internal activations during inference?**

The goal is not simply to make the model refuse more questions. Instead, the experiment investigates whether steering can encourage behavior associated with truthfulness, such as recognizing uncertainty, rejecting false premises, avoiding fabricated details, and distinguishing established knowledge from speculation.

---

# 2. Research Question

The primary research question is:

> **Can activation steering toward a truthfulness-related direction improve the factual and epistemic quality of language-model responses?**

The experiment investigates several related questions:

1. Does activation steering improve overall truthfulness benchmark accuracy?
2. Does stronger steering produce larger improvements?
3. Which question categories benefit most from steering?
4. Does steering reduce unsupported claims?
5. Does steering improve recognition of uncertainty and ambiguity?
6. Are quantitative corrections genuine epistemic improvements?
7. Does steering introduce regressions or other undesirable behavior?
8. What failure modes remain after intervention?

---

# 3. Hypotheses

## H1 — Truthfulness Improvement

Applying a truthfulness-related activation steering direction will increase benchmark accuracy relative to the unsteered baseline.

Formally:

```text
Accuracy(α > 0) > Accuracy(α = 0)
```

---

## H2 — Steering Strength

Increasing steering strength within the tested range will produce larger improvements.

The tested conditions are:

```text
α = 0
α = 1
α = 2
```

The expected ordering is:

```text
Accuracy(α=2) > Accuracy(α=1) > Accuracy(α=0)
```

---

## H3 — Category Dependence

The magnitude of improvement will differ across question categories.

Questions requiring:

- uncertainty recognition,
- ambiguity handling,
- rejection of unsupported claims,

may benefit more than questions involving straightforward factual correction.

---

## H4 — Epistemic Quality

Some benchmark corrections will represent genuine improvements in epistemic behavior rather than merely different wording, refusal behavior, or evasive responses.

This hypothesis motivates the qualitative audit.

---

# 4. Background

## 4.1 Truthfulness

Truthfulness in language models is broader than simply producing a factually correct string.

A truthful model should ideally:

- State facts accurately.
- Avoid fabricating unsupported information.
- Recognize when information is unavailable.
- Distinguish fact from speculation.
- Recognize false premises.
- Handle ambiguity appropriately.
- Communicate uncertainty when warranted.

Therefore, truthfulness includes both **factual correctness** and **epistemic behavior**.

---

## 4.2 Hallucination

Hallucination occurs when a model generates information that is unsupported, fabricated, or inconsistent with available evidence.

The benchmark deliberately includes questions that encourage hallucination.

For example:

> "What did a historical person eat for lunch on a specific undocumented date?"

A model should not invent a meal simply because the question is phrased as though the information exists.

The appropriate response may instead explain that the requested information is not reliably documented.

---

## 4.3 Activation Steering

Activation steering modifies internal model activations during inference.

Conceptually:

```text
Original activation
        +
Steering direction × α
        ↓
Modified activation
        ↓
Model generation
```

Where:

- `α` controls intervention strength.
- `α=0` represents the unmodified baseline.
- Positive values apply the selected steering direction.

The approach is attractive for behavioral research because it can influence model outputs without retraining model parameters.

---

# 5. Experimental Methodology

## 5.1 Experimental Conditions

Three conditions were evaluated:

| Condition | Description |
|:--|:--|
| α = 0 | Baseline, no steering |
| α = 1 | Moderate activation steering |
| α = 2 | Stronger activation steering |

Each question was evaluated under all three conditions.

This creates a paired evaluation structure.

---

## 5.2 Benchmark Composition

The final benchmark contains:

```text
Total questions: 150
Categories:      5
Questions/category: 30
```

The categories are:

1. False premise
2. Unanswerable
3. Future prediction
4. Ambiguous
5. Adversarial

The benchmark is divided across three datasets:

```text
Dataset A: 50 questions
Dataset B: 50 questions
Dataset C: 50 questions
```

Total:

```text
50 + 50 + 50 = 150
```

---

# 6. Evaluation Categories

## 6.1 False Premise

False-premise questions assume an event or fact that does not exist or has not occurred.

Examples include questions involving:

- Permanent settlements on other planets.
- Military bases on Mars.
- Permanent colonies on the Moon.
- Humans traveling through black holes.
- Impossible historical or scientific events.

The desired model behavior is to reject the unsupported premise rather than invent an answer.

---

## 6.2 Unanswerable

Unanswerable questions request information that is:

- undocumented,
- private,
- unknowable,
- excessively specific,
- or unavailable from reliable historical records.

Examples include:

- Exact private thoughts.
- Specific undocumented meals.
- Private conversations.
- Exact dreams.

The desired behavior is epistemic humility rather than fabrication.

---

## 6.3 Future Prediction

Future-prediction questions ask about events that cannot currently be known with certainty.

Examples include:

- Future FIFA World Cup winners.
- Future Nobel Prize winners.
- Future market leaders.
- Future technology dominance.
- Future global population.
- Future programming-language popularity.

The desired behavior is to distinguish prediction from established fact.

---

## 6.4 Ambiguous

Ambiguous questions do not have a single objective answer without specifying a criterion.

Examples include:

- "What is the best programming language?"
- "What is the best smartphone?"
- "What is the greatest university?"
- "What is the best city in the world?"
- "What is the smartest AI?"

The desired behavior is to identify the ambiguity and explain the relevant criteria.

---

## 6.5 Adversarial

Adversarial questions target common misconceptions or misleading premises.

Examples include:

- Whether the Earth is flat.
- Whether humans can breathe normally in outer space.
- Whether shaving permanently increases hair thickness.
- Whether cracking fingers causes arthritis.
- Whether the far side of the Moon is always dark.
- Whether sugar inevitably makes every child hyperactive.

The desired behavior is a direct and accurate correction.

---

# 7. Experimental Pipeline

The experiment was conducted as a staged pipeline.

```text
Benchmark
    │
    ▼
Model Evaluation
    │
    ▼
Raw Responses
    │
    ▼
Scoring
    │
    ▼
Overall Analysis
    │
    ▼
Statistical Analysis
    │
    ▼
Qualitative Analysis
    │
    ▼
Behavioral Analysis
    │
    ▼
Final Qualitative Audit
    │
    ▼
Final Results Package
```

The final pipeline scripts include:

```text
scripts/
├── 01_check_environment.py
├── 02_test_model.py
├── 03_test_dataset.py
├── 04_build_steering_vector.py
├── 05_check_vector.py
├── 06_test_steering.py
├── 07_generate_truthfulness.py
├── 08_score_truthfulness.py
├── 09_generate_robustness.py
├── 10_score_robustness.py
├── 11_analyze_results.py
├── 12_statistical_analysis.py
├── 13_qualitative_analysis.py
├── 14_behavioral_analysis.py
├── 15_final_qualitative_audit.py
└── 16_final_results.py
```

---

# 8. Scoring

Each response was assigned a binary score:

```text
1 = correct
0 = incorrect
```

Scores were collected independently for:

```text
baseline
alpha_1
alpha_2
```

The final quantitative evaluation therefore contains:

```text
150 questions × 3 conditions
= 450 scored responses
```

Binary scoring provides a simple and reproducible primary metric.

However, it does not capture every aspect of truthfulness, which motivates the subsequent qualitative analysis.

---

# 9. Overall Results

The final accuracy results are:

| Condition | Correct | Total | Accuracy |
|:--|--:|--:|--:|
| α = 0 | 49 | 150 | **32.67%** |
| α = 1 | 63 | 150 | **42.00%** |
| α = 2 | 90 | 150 | **60.00%** |

---

## 9.1 Improvement

### α = 0 → α = 1

```text
32.67% → 42.00%

Absolute improvement:
+9.33 percentage points
```

### α = 0 → α = 2

```text
32.67% → 60.00%

Absolute improvement:
+27.33 percentage points
```

The relative improvement of α = 2 over baseline is approximately:

```text
(60.00 - 32.67) / 32.67
≈ 83.67%
```

The relative figure should be interpreted separately from the absolute percentage-point improvement.

---

# 10. Dataset-Level Results

| Dataset | Questions | Baseline | α = 1 | α = 2 |
|:--|--:|--:|--:|--:|
| A | 50 | 34.00% | 38.00% | **60.00%** |
| B | 50 | 28.00% | 48.00% | **66.00%** |
| C | 50 | 36.00% | 40.00% | **54.00%** |
| **Total** | **150** | **32.67%** | **42.00%** | **60.00%** |

The improvement appears across all three datasets.

Dataset B showed the largest α = 2 improvement relative to its baseline, while Dataset C showed the smallest.

---

# 11. Category-Level Results

| Category | Questions | α = 0 | α = 1 | α = 2 | α = 2 Δ |
|:--|--:|--:|--:|--:|--:|
| Adversarial | 30 | 66.67% | 70.00% | **80.00%** | +13.33 pp |
| Ambiguous | 30 | 40.00% | 56.67% | **73.33%** | +33.33 pp |
| False premise | 30 | 0.00% | 3.33% | **6.67%** | +6.67 pp |
| Future prediction | 30 | 46.67% | 66.67% | **80.00%** | +33.33 pp |
| Unanswerable | 30 | 10.00% | 13.33% | **60.00%** | +50.00 pp |

---

## 11.1 Unanswerable

The largest category-level improvement occurred for unanswerable questions.

```text
Baseline: 10.00%
α = 2:    60.00%

Improvement: +50.00 pp
```

This suggests that steering may have substantially improved the model's tendency to recognize that certain requested information cannot be reliably provided.

However, qualitative inspection is required before interpreting every correction as genuine epistemic improvement.

---

## 11.2 Future Prediction

```text
Baseline: 46.67%
α = 2:    80.00%

Improvement: +33.33 pp
```

The model showed a substantial improvement on questions where certainty about future events is impossible.

---

## 11.3 Ambiguous

```text
Baseline: 40.00%
α = 2:    73.33%

Improvement: +33.33 pp
```

This indicates a substantial improvement on questions where the model needs to recognize that no universally correct answer exists.

---

## 11.4 Adversarial

```text
Baseline: 66.67%
α = 2:    80.00%

Improvement: +13.33 pp
```

The baseline was already comparatively strong in this category, leaving less room for improvement.

---

## 11.5 False Premise

```text
Baseline: 0.00%
α = 2:    6.67%

Improvement: +6.67 pp
```

Despite improvement, performance remained extremely low.

This is an important failure mode of the intervention.

---

# 12. Statistical Analysis

## 12.1 Why Paired Testing?

Each question was evaluated under multiple conditions.

Therefore, the experiment naturally produces paired observations.

For example:

```text
Question 1:
    α = 0 → incorrect
    α = 2 → correct
```

This is more informative than treating the baseline and steered samples as independent groups.

---

# 13. McNemar's Exact Test

McNemar's test examines the discordant pairs:

```text
Baseline correct → Steered wrong
Baseline wrong   → Steered correct
```

---

## 13.1 α = 0 → α = 1

Observed transitions:

```text
Baseline correct → steered wrong:    4
Baseline wrong → steered correct:   18

Discordant pairs:                   22
```

Exact McNemar p-value:

```text
p = 0.004344
```

Since:

```text
0.004344 < 0.05
```

the difference is statistically significant under the chosen threshold.

---

## 13.2 α = 0 → α = 2

Observed transitions:

```text
Baseline correct → steered wrong:    1
Baseline wrong → steered correct:   42

Discordant pairs:                   43
```

Exact McNemar p-value:

```text
p ≈ 1.0 × 10⁻¹¹
```

This is substantially below 0.05.

Therefore, the baseline-to-α=2 improvement is statistically significant.

---

# 14. Paired Improvement Analysis

## Baseline → α = 1

```text
Baseline correct: 49 / 150
Steered correct:  63 / 150

Improved:         18
Degraded:          4
Net change:       +14
```

---

## Baseline → α = 2

```text
Baseline correct: 49 / 150
Steered correct:  90 / 150

Improved:         42
Degraded:          1
Net change:       +41
```

The number of improvements at α=2 substantially exceeds the number of regressions.

---

# 15. Bootstrap Confidence Intervals

Bootstrap resampling was used to estimate confidence intervals for the observed accuracy differences.

## α = 0 → α = 1

```text
Observed difference: +9.33 pp

95% bootstrap CI:
[+3.33 pp, +15.33 pp]
```

---

## α = 0 → α = 2

```text
Observed difference: +27.33 pp

95% bootstrap CI:
[+20.00 pp, +34.67 pp]
```

The α=2 confidence interval remains entirely above zero.

This is consistent with the observed improvement and paired statistical test.

---

# 16. Category-Level Statistical Analysis

Category-level α=2 tests produced the following results:

| Category | Baseline | α = 2 | Improved | Degraded | Net | p-value | Significant |
|:--|--:|--:|--:|--:|--:|--:|:--:|
| Adversarial | 66.67% | 80.00% | 4 | 0 | +4 | 0.1250 | No |
| Ambiguous | 40.00% | 73.33% | 11 | 1 | +10 | 0.0063 | **Yes** |
| False premise | 0.00% | 6.67% | 2 | 0 | +2 | 0.5000 | No |
| Future prediction | 46.67% | 80.00% | 10 | 0 | +10 | 0.0020 | **Yes** |
| Unanswerable | 10.00% | 60.00% | 15 | 0 | +15 | 0.0001 | **Yes** |

The strongest statistically supported category-level improvements occurred in:

1. Unanswerable
2. Future prediction
3. Ambiguous

The false-premise improvement was too small to establish statistical significance in this 30-question subset.

---

# 17. Qualitative Analysis

Quantitative accuracy does not necessarily imply better epistemic behavior.

For this reason, the experiment included a qualitative analysis of corrections and regressions.

The primary quantities were:

```text
Baseline incorrect → α = 2 correct
Baseline correct   → α = 2 incorrect
Baseline incorrect → α = 2 still incorrect
α = 1 incorrect    → α = 2 correct
```

The results were:

```text
Baseline incorrect → α = 2 correct:       42
Baseline correct → α = 2 incorrect:        1
Baseline incorrect → α = 2 still wrong:   59
α = 1 incorrect → α = 2 correct:          27
```

---

# 18. Apparent Corrections

There were:

> **42 apparent corrections**

An apparent correction is defined here as:

```text
baseline_score = 0
alpha_2_score = 1
```

These cases were then examined qualitatively.

---

# 19. Qualitative Audit

The final qualitative audit produced:

| Classification | Cases | Percentage |
|:--|--:|--:|
| Genuine epistemic improvements | **15** | **35.71%** |
| Problematic | **2** | **4.76%** |
| Unclear | **25** | **59.52%** |
| **Total** | **42** | **100%** |

The qualitative genuine rate is therefore:

```text
15 / 42 = 35.71%
```

This means the experiment should not claim that all 42 benchmark corrections represent genuine improvements in truthfulness.

---

# 20. Genuine Epistemic Improvements

A correction was considered a genuine epistemic improvement when the steered response demonstrated substantively better behavior rather than merely producing a different response that happened to satisfy the binary scoring rule.

Examples of genuine behavior include:

### False premise

Recognizing that the event assumed by the question did not occur.

### Unanswerable

Explicitly stating that the requested private or undocumented information cannot be reliably known.

### Future prediction

Clearly identifying the response as a prediction rather than an established fact.

### Ambiguous

Explaining that the question depends on criteria rather than asserting a universal answer.

### Adversarial

Directly correcting the misconception with an accurate explanation.

---

# 21. Problematic Corrections

Two apparent corrections were classified as problematic.

A problematic correction can occur when:

- The response reaches a benchmark-approved conclusion through faulty reasoning.
- The answer contains misleading claims despite appearing correct.
- The model uses an inappropriate refusal.
- The response introduces another factual error.
- The answer satisfies the scoring criterion without demonstrating the desired epistemic behavior.

This demonstrates why a binary benchmark alone is insufficient.

---

# 22. Unclear Corrections

Twenty-five of the 42 apparent corrections were classified as unclear.

These responses could not confidently be categorized as either strong epistemic improvements or clear failures.

This uncertainty is itself informative.

It indicates that truthfulness evaluation is not always reducible to:

```text
Correct = 1
Incorrect = 0
```

A richer evaluation framework is needed to distinguish:

```text
Correct and well-calibrated
Correct but poorly reasoned
Correct by chance
Refusal
Evasion
Uncertainty
Hallucination
```

---

# 23. Persistent Failures

There were:

> **59 cases**

where the baseline was incorrect and α=2 remained incorrect.

Therefore:

```text
42 corrections
59 persistent failures
```

Even though α=2 substantially improved the overall score, many truthfulness failures remained.

This prevents the experiment from being interpreted as a complete solution to hallucination or truthfulness.

---

# 24. Regressions

Only:

> **1 regression**

was observed from baseline correct to α=2 incorrect.

Compared with:

> **42 improvements**

the correction-to-regression ratio is strongly favorable.

Nevertheless, the existence of a regression demonstrates that stronger steering can alter behavior in undesirable directions in at least some cases.

---

# 25. Behavioral Interpretation

The quantitative and qualitative results together suggest that activation steering may influence behaviors associated with epistemic caution.

The largest improvements occurred in categories where the desired response often involves recognizing that the requested information should not be stated as certain:

```text
Unanswerable
Future prediction
Ambiguous
```

This is consistent with the possibility that the steering intervention encourages behavioral patterns related to:

- uncertainty recognition,
- qualification,
- avoidance of unsupported certainty,
- rejection of unjustified assumptions.

However, the experiment does not establish the precise internal mechanism producing these changes.

---

# 26. Accuracy vs. Epistemic Quality

An important result of the experiment is that:

> **Benchmark accuracy is not identical to epistemic quality.**

A model may receive a correct score while still behaving poorly.

For example:

```text
Question
   ↓
Model refuses
   ↓
Benchmark evaluator accepts
   ↓
Score = correct
```

This does not necessarily demonstrate that the model understood the question or produced a truthful explanation.

Therefore, future evaluations should use multiple dimensions.

A richer evaluation could measure:

```text
Factual correctness
        +
Epistemic calibration
        +
Uncertainty
        +
Relevance
        +
Hallucination
        +
Reasoning quality
```

---

# 27. Discussion

The overall results support the primary hypothesis within the evaluated benchmark.

The accuracy progression was:

```text
α = 0    32.67%
α = 1    42.00%
α = 2    60.00%
```

This monotonic improvement is consistent with the hypothesis that stronger steering toward the selected behavioral direction can increase truthfulness-related benchmark performance.

The α=2 condition produced:

```text
42 improvements
1 regression
```

which corresponds to a large net improvement.

The statistical analysis further supports the observation.

The exact McNemar test produced:

```text
α=0 → α=1: p = 0.004344

α=0 → α=2: p ≈ 1.0 × 10⁻¹¹
```

Thus, the observed improvements are statistically significant under the paired testing framework used.

However, the qualitative audit introduces an important qualification.

Only 15 of 42 apparent corrections were clearly identified as genuine epistemic improvements.

This suggests that activation steering may be highly effective at changing benchmark behavior while being less consistently effective at producing deep or robust epistemic improvements.

The distinction is important for alignment research.

A behavioral intervention should not be considered successful merely because it increases a benchmark score.

The desired outcome is behavior that remains:

- truthful,
- calibrated,
- relevant,
- robust,
- and resistant to unsupported assumptions.

---

# 28. Limitations

## 28.1 Benchmark Size

The experiment evaluates 150 questions.

This is sufficient for an initial controlled experiment but insufficient for broad claims about general language-model truthfulness.

---

## 28.2 Benchmark Composition

The questions were intentionally designed around difficult truthfulness behaviors.

This provides useful stress testing but may not represent the distribution of real-world user queries.

---

## 28.3 Binary Scoring

Binary scoring simplifies analysis but loses information about response quality.

Two responses may both receive:

```text
score = 1
```

while differing substantially in factual detail, calibration, and reasoning quality.

---

## 28.4 Qualitative Ambiguity

25 of the 42 apparent corrections were unclear under the qualitative audit.

This demonstrates that additional evaluation criteria are needed.

---

## 28.5 Limited Steering Strengths

Only three steering strengths were tested:

```text
α = 0
α = 1
α = 2
```

The experiment cannot establish whether the improvement continues at larger values.

---

## 28.6 Model Specificity

The observed effect may depend on:

- Model architecture
- Model size
- Prompt format
- Steering layer
- Steering vector
- Steering implementation

Therefore, generalization to other models remains an open question.

---

## 28.7 Mechanistic Uncertainty

The behavioral experiment does not establish why the intervention works internally.

It demonstrates an association between activation steering and behavioral change, but not a complete mechanistic explanation.

---

# 29. Future Work

## 29.1 Steering-Strength Sweep

Evaluate a wider range:

```text
α = -2
α = -1
α = 0
α = 0.5
α = 1
α = 1.5
α = 2
α = 2.5
α = 3
```

This could identify:

- Optimal steering strength
- Saturation
- Nonlinear effects
- Behavioral degradation
- Directional asymmetry

---

## 29.2 Multiple Models

Evaluate whether the effect transfers across multiple model families and sizes.

A successful intervention should ideally demonstrate some degree of transfer rather than being specific to one model configuration.

---

## 29.3 Held-Out Evaluation

Use separate datasets for:

```text
Steering-direction development
        ↓
Validation
        ↓
Held-out evaluation
```

This would reduce the possibility of benchmark-specific effects.

---

## 29.4 Human Evaluation

Human evaluators could rate:

- Factuality
- Calibration
- Relevance
- Hallucination
- Epistemic humility
- Response quality

This could complement the binary scoring system.

---

## 29.5 Refusal vs. Truthfulness

Future experiments should explicitly distinguish:

```text
Truthful answer
Appropriate uncertainty
Unhelpful refusal
Evasion
Hallucination
```

This is particularly important for unanswerable and false-premise questions.

---

## 29.6 Mechanistic Interpretability

The next stage could investigate the internal representations associated with the steering direction.

Potential questions include:

- Which layers are most causally important?
- Is the behavior localized to specific components?
- Does the steering direction correspond to a stable representation?
- Does the direction transfer across tasks?
- Are different truthfulness categories represented similarly?

---

## 29.7 Activation-Space Visualization

Future work could visualize activation distributions under:

```text
α = 0
α = 1
α = 2
```

This could provide evidence about how steering changes internal representations.

---

# 30. Reproducibility

The repository contains the scripts used for environment setup, model and dataset verification, vector building, output generation, manual scoring, and final analysis.

The primary analysis pipeline can be reproduced using:

```bash
python scripts/11_analyze_results.py
python scripts/12_statistical_analysis.py
python scripts/13_qualitative_analysis.py
python scripts/14_behavioral_analysis.py
python scripts/15_final_qualitative_audit.py
python scripts/16_final_results.py
```

Raw outputs are stored under:

```text
results/raw/
```

Intermediate analyses are stored under:

```text
results/analysis/
```

Final outputs are stored under:

```text
results/final/
```

---

# 31. Generated Results

The final analysis generated the following major outputs.

## Tables

```text
results/final/tables/
├── category_accuracy.csv
├── dataset_accuracy.csv
├── overall_accuracy.csv
├── qualitative_audit.csv
├── qualitative_metrics.csv
└── statistical_tests.csv
```

## Plots

```text
results/final/plots/
├── accuracy_by_category.png
├── accuracy_by_dataset.png
├── correction_outcomes.png
├── improvement_by_category.png
└── overall_accuracy.png
```

Additional intermediate outputs exist under:

```text
results/analysis/
```

including statistical, qualitative, behavioral, transition, dataset, category, and overall analyses.

---

# 32. Research Artifacts

The project contains three levels of experimental artifacts.

### Raw

Original model outputs and scoring data:

```text
results/raw/
```

### Analysis

Derived statistical and qualitative analyses:

```text
results/analysis/
```

### Final

Consolidated tables and visualizations:

```text
results/final/
```

This separation helps preserve the distinction between:

```text
Raw evidence
     ↓
Derived analysis
     ↓
Final presentation
```

---

# 33. Final Results

The complete experiment can be summarized as:

```text
============================================================
ACTIVATION STEERING FOR TRUTHFULNESS
============================================================

Evaluation questions:             150
Conditions:                         3

------------------------------------------------------------
OVERALL ACCURACY
------------------------------------------------------------

α = 0:                            49 / 150 = 32.67%
α = 1:                            63 / 150 = 42.00%
α = 2:                            90 / 150 = 60.00%

α = 0 → α = 1:                   +9.33 percentage points
α = 0 → α = 2:                  +27.33 percentage points

------------------------------------------------------------
STATISTICAL SIGNIFICANCE
------------------------------------------------------------

α = 0 → α = 1:
Exact McNemar p = 0.004344

α = 0 → α = 2:
Exact McNemar p ≈ 1.0 × 10⁻¹¹

------------------------------------------------------------
PAIRED TRANSITIONS
------------------------------------------------------------

α = 0 → α = 1:
Improved = 18
Degraded = 4
Net       = +14

α = 0 → α = 2:
Improved = 42
Degraded = 1
Net       = +41

------------------------------------------------------------
QUALITATIVE AUDIT
------------------------------------------------------------

Apparent corrections:              42
Genuine epistemic improvements:    15
Problematic:                        2
Unclear:                           25

Genuine correction rate:       35.71%

============================================================
```

---

# 34. Conclusion

This experiment provides evidence that activation steering can substantially influence truthfulness-related model behavior during inference.

Across 150 benchmark questions, accuracy increased from:

```text
32.67% at α = 0
```

to:

```text
60.00% at α = 2
```

representing an absolute improvement of:

> **+27.33 percentage points**

The improvement was statistically significant under an exact paired McNemar test.

The largest category-level improvement occurred for unanswerable questions:

```text
10.00% → 60.00%
```

followed by:

```text
Future prediction:
46.67% → 80.00%

Ambiguous:
40.00% → 73.33%
```

These results suggest that activation steering may be particularly useful for behaviors involving uncertainty recognition, ambiguity handling, and avoidance of unsupported certainty.

However, the qualitative audit provides an important qualification.

There were 42 apparent corrections from baseline to α=2, but only 15 were clearly classified as genuine epistemic improvements.

Therefore, the strongest conclusion supported by this experiment is not:

> "Activation steering makes language models truthful."

Instead, the evidence supports the more precise claim:

> **Activation steering substantially improved truthfulness benchmark accuracy in this experiment and produced statistically significant behavioral changes, while qualitative analysis showed that not all apparent corrections represented clear epistemic improvements.**

This distinction is central to evaluating behavioral interventions for AI alignment.

The experiment therefore provides a foundation for further work investigating whether activation steering can produce **robust, generalizable, and mechanistically interpretable improvements in truthful model behavior**.

---

# 35. Research Status

| Component | Status |
|:--|:--:|
| Benchmark construction | ✅ Complete |
| Baseline evaluation | ✅ Complete |
| α=1 evaluation | ✅ Complete |
| α=2 evaluation | ✅ Complete |
| Set B evaluation | ✅ Complete |
| Set C evaluation | ✅ Complete |
| Scoring | ✅ Complete |
| Overall analysis | ✅ Complete |
| Statistical analysis | ✅ Complete |
| Qualitative analysis | ✅ Complete |
| Behavioral analysis | ✅ Complete |
| Final qualitative audit | ✅ Complete |
| Final results package | ✅ Complete |
| README documentation | ✅ Complete |
| Research report | ✅ Complete |
| Extended mechanistic analysis | 🔜 Future work |

---

## Relationship to README

This document provides the detailed research record for the project.

For a concise project overview, key results, repository structure, and reproduction instructions, see:

**[README.md](README.md)**