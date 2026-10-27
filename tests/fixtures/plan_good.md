# Research plan

Aim: to estimate the trend in tuberculosis notifications in Example Province from 2010 to 2022.

## Data

We will use the provincial notification register (release of March 2024, obtained from the provincial health office), restricted to bacteriologically confirmed cases. Each variable is defined in the data dictionary that accompanies the input data.

## Analysis

We will fit a Poisson regression of monthly notifications on calendar year, with the population as an offset, because notifications are counts with a known denominator. If the ratio of residual deviance to degrees of freedom exceeds 1.5, we will fit a negative binomial model.

## Outputs

Figure 1 will show monthly notifications with the fitted trend. Table 2 will give the rate ratio per year with its 95% CI.
