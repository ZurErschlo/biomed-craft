# Examples

Synthetic before-and-after pairs; numbers are invented. Rule IDs show what changed. The rewrites are quotations so that `scan.py` checks them with the rest of the skill.

Contents: 1. Introduction opening; 2. Contrast frames; 3. Methods written as engineering; 4. Results with interpretation; 5. Limitations; 6. Figure legend; 7. Text inside a figure; 8. Reply to reviewers; Leave these alone.

## 1. Introduction opening

```text
In recent years, antimicrobial resistance has attracted increasing attention as a multifaceted
global challenge. A growing body of evidence suggests that its burden is substantial, yet its
economic impact remains poorly understood.
```

> In 2019, an estimated 1·27 million deaths were directly attributable to bacterial antimicrobial resistance. Earlier reviews estimated hospital costs in high-income countries but did not include patients' own costs or settings in Africa and Asia. We aimed to estimate the costs borne by patients with drug-resistant infections in low-income and middle-income countries.

LEX-02, LEX-03 and LEX-07 removed; the vague gap became a named missing estimate; the aim closes the paragraph.

## 2. Contrast frames

```text
The central gap is not cost. It is coverage. Uptake fell not because of drug prices but because
of staffing, not demand.
```

> Coverage was the main constraint: uptake fell from 64% to 41% in districts that lost more than a quarter of their nurses, and drug prices did not change during the study.

CON-01, CON-03 and CON-04 replaced by the measured comparison.

## 3. Methods written as engineering

```text
Our pipeline cleaned and merged the records, and we ran the script for each country with
seed = 2024 (see 02_model.R). We initially tried a logistic model, but after several iterations
we switched to a Poisson model.
```

> We linked notification and laboratory records by national identifier, removed duplicates, and fitted Poisson regression models for each country with an offset for population.

ENG-01, ENG-02, ENG-04, HYG-01 and META-10 removed. If the change of model matters, report the prespecified model and the sensitivity analysis, not the history.

## 4. Results with interpretation

```text
Notably, costs increased substantially (Table 2 shows this), highlighting the urgent need for
financial protection. These findings underscore the importance of targeted support.
```

> Median costs rose from US$310 (IQR 120–690) to US$870 (420–1650) per patient (table 2).

LEX-04, LEX-07, META-06, STR-03 and STR-07 removed; the implication moves to the Discussion, where it can be specific.

## 5. Limitations

```text
It is important to note that these estimates should be interpreted with caution. Despite these
limitations, our study provides valuable insights. Further research is needed.
```

> Our study has several limitations. First, outcomes came from routine registers, which might miss deaths after transfer; this would bias the estimate towards the null. Second, 18% of districts had no cost data, and we imputed them from neighbouring districts with similar incidence. A cohort study that follows patients after transfer would resolve the first limitation.

DEF-01, DEF-04, DEF-10, LEX-02 and DEF-07 replaced by problem, consequence and a specific study.

## 6. Figure legend

```text
Figure 2: This figure shows incidence by year from amr_rate_v2, suggesting a decline after 2015.
```

> Figure 2: Incidence of drug-resistant tuberculosis by WHO region, 2010–2022. Lines show model estimates and shaded areas show 95% uncertainty intervals. UI=uncertainty interval.

META-05, HYG-03, HYG-07 and CAP-01 removed; encodings and abbreviations defined.

## 7. Text inside a figure

```text
labs(title = "Incidence of tuberculosis in 30 high-burden countries, 2010 to 2022",
     subtitle = "Estimates are descriptive only; the model did not pass validation") +
scale_colour_discrete(labels = c("R", "P"))
```

The title and the caveat move to the legend (FIG-01, FIG-02, FIG-03); the single letters become short names (FIG-05):

```text
labs(x = "Year", y = "Incidence (per 100 000)", colour = NULL) +
scale_colour_discrete(labels = c("RR-TB", "Pre-XDR-TB"))
```

> Legend: Estimates for 2021–2022 are descriptive; the model did not reproduce notifications in the validation period. RR-TB=rifampicin-resistant tuberculosis. Pre-XDR-TB=pre-extensively drug-resistant tuberculosis.

## 8. Reply to reviewers

```text
We sincerely thank the reviewer for this insightful comment. We have carefully revised the
manuscript to address this important point.
```

> We agree and have added a sensitivity analysis excluding the two largest clinics; the risk ratio was 1·07 (95% CI 1·01–1·13) (Methods, lines 212–219; appendix p 11).

Thanks belong once at the top of the letter (DEF-12). Describing the change and its location is right here (`scan.py --doc response`).

## Leave these alone

> Smoking was associated with treatment failure (adjusted odds ratio 1·42, 95% CI 1·10–1·83).

> Treatment success did not differ between groups (risk ratio 1·01, 95% CI 0·95–1·08).

> Mortality was 9% with the new regimen and 14% with the standard regimen.

> Participants were randomly assigned by a central computer system.

Association wording for observational data, a null result with its interval, a comparison of two measured groups, and the passive in Methods are correct as written. A priority claim may stay once, in a Lancet Research in context panel, when the reported search supports it (LEX-09).
