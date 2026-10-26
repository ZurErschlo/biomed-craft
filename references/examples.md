# Examples

Synthetic before-and-after pairs. None is taken from a real manuscript; numbers are invented. Rule IDs show what changed. The rewrites are written as quotations so that `scan.py` checks them along with the rest of the skill.

## 1. Introduction opening

```text
In recent years, antimicrobial resistance has attracted increasing attention as a multifaceted
global challenge. A growing body of evidence suggests that its burden is substantial, yet its
economic impact remains poorly understood.
```

> In 2019, an estimated 1·27 million deaths were directly attributable to bacterial antimicrobial resistance. Earlier reviews estimated hospital costs in high-income countries but did not include patients' own costs or settings in Africa and Asia. We aimed to estimate the costs borne by patients with drug-resistant infections in low-income and middle-income countries.

LEX-02, LEX-03 and LEX-07 removed; the vague gap became a named missing estimate; the aim closes the paragraph.

## 2. Contrast frames in a Discussion

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

ENG-01, ENG-02, ENG-04, HYG-01 and META-10 removed. If the change of model matters for interpretation, report the prespecified model and the sensitivity analysis, and leave out the history.

## 4. Results with interpretation

```text
Table 2 shows that costs increased substantially, highlighting the urgent need for financial
protection.
```

> Median costs rose from US$310 (IQR 120–690) to US$870 (420–1650) per patient (table 2).

META-06, LEX-07 and STR-03 removed; the implication moves to the Discussion, where it can be specific.

## 5. Defensive tails

```text
It is important to note that these estimates could potentially change and should be interpreted
with caution. We do not claim that the model captures every pathway.
```

> The estimates depend on the assumed duration of infectiousness; halving it reduced averted cases by 22% (appendix p 9).

DEF-01, DEF-02, DEF-04 and DEF-08 replaced by the fact that bounds the claim.

## 6. Limitations

```text
Despite these limitations, our study provides valuable insights. Further research is needed.
```

> Our study has several limitations. First, outcomes came from routine registers, which might miss deaths after transfer; this would bias the estimate towards the null. Second, 18% of districts had no cost data, and we imputed them from neighbouring districts with similar incidence. A cohort study that follows patients after transfer would resolve the first limitation.

DEF-10, LEX-02 and DEF-07 replaced by problem, consequence and a specific study.

## 7. Signposts and verdicts

```text
Notably, uptake was higher in women. Moreover, uptake was higher in urban districts. These
findings underscore the importance of targeted outreach.
```

> Uptake was higher in women (58% vs 44%) and in urban districts (61% vs 39%), so outreach in rural districts that reaches men could close most of the gap.

LEX-04, STR-04, STR-07 and LEX-03 removed; the implication is specific and proportionate.

## 8. Abstract Interpretation (Lancet style)

```text
Interpretation: This groundbreaking study sheds light on the pivotal role of community health
workers and paves the way for transformative policy change.
```

> Interpretation: Adherence support by community health workers increased treatment success in routine clinics. National programmes could add this support where clinic staffing allows home visits.

LEX-01 and LEX-03 removed; the recommendation matches a trial's evidence.

## 9. Figure legend

```text
Figure 2: This figure shows incidence by year from amr_rate_v2, suggesting a decline after 2015.
```

> Figure 2: Incidence of drug-resistant tuberculosis by WHO region, 2010–2022. Lines show model estimates and shaded areas show 95% uncertainty intervals. UI=uncertainty interval.

META-05, HYG-03, HYG-07 and CAP-01 removed; encodings and abbreviations defined.

## 10. Text inside a figure (ggplot2)

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

## 11. Table note

```text
Note: PREXDR_HIGH = scenario 3 (see TableS8.csv). *** p<0.001. Values from run 2.
```

> Data are n (%) or median (IQR). Pre-XDR-TB=pre-extensively drug-resistant tuberculosis. *Scenario with a 20% higher rate of fluoroquinolone resistance.

HYG-08, HYG-01 and ENG-03 removed; the statistic format, abbreviation and mark follow journal order.

## 12. Protocol

```text
Written on 13 October 2026; this version supersedes v1.1. Next steps: we may also consider a
cluster design if feasible (to do: confirm supplier, not yet confirmed).
```

> Clinics will be randomly assigned (1:1) to adherence support or usual care, stratified by province. The drug supplier will be confirmed by month 6; if it is not, the trial will use the national tender supplier.

META-08, HYG-07 and DEF-11 removed; options became decisions; the risk became a plan.

## 13. Response to reviewers

```text
We sincerely thank the reviewer for this insightful comment. We have carefully revised the
manuscript to address this important point.
```

> We agree and have added a sensitivity analysis excluding the two largest clinics; the risk ratio was 1·07 (95% CI 1·01–1·13) (Methods, lines 212–219; appendix p 11).

Thanks belong once at the top of the letter. Describing the change and its location is right in this document (`scan.py --doc response`).

## 14. Slide

```text
Projected impact (simulated; 10,000 runs). Not a cost-effectiveness claim. Illustrative only.
```

> Adherence support could avert 1 in 5 treatment failures in the four pilot provinces.

ENG-03, DEF-08 and DEF-06 removed; the model's uncertainty belongs in the speaker notes or the report.

## 15. Supplementary parameter table row

```text
p_fail_should | 0.12 | runif(0.08,0.16) | calibrated in script 04
```

> Probability of treatment failure with appropriate treatment | 0·12 | 0·08–0·16 | Uniform | Fitted to national cohort data (appendix p 14)

HYG-03 and ENG-02 removed; the row uses the public name, range, distribution and source columns.

## Leave these alone

> Smoking was associated with treatment failure (adjusted odds ratio 1·42, 95% CI 1·10–1·83).

Association wording is the correct claim for observational data.

> Incidence fell between 2010 and 2020, and the 95% uncertainty interval was 3·1–4·8.

En dashes in numeric ranges are required.

> Mortality was 9% with the new regimen and 14% with the standard regimen.

A comparison of two measured groups with both numbers is the finding.

> Participants were randomly assigned by a central computer system.

Passive voice is normal in Methods.

> Treatment success did not differ between groups (risk ratio 1·01, 95% CI 0·95–1·08).

A null result stated with its interval stays.

> To our knowledge, this is the first trial of adherence support in routine clinics in sub-Saharan Africa.

A priority claim may stay once, in a Lancet Research in context panel, when the search reported in that panel supports it (LEX-09).
