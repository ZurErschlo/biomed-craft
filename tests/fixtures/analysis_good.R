# Purpose: estimate the trend in notifications (plan: Analysis, trend model)
# Input:   data/output/notifications_clean.csv
# Output:  tables/table2_trend.xlsx

pacman::p_load(
  here,
  MASS
)

set.seed(20261027)

# 1. Load data ----
notifications <- read.csv(here::here("data", "output", "notifications_clean.csv"))
stopifnot("duplicate notification IDs" = !anyDuplicated(notifications$id))

# 2. Fit the model ----
# Negative binomial because the counts are overdispersed (deviance ratio above 1.5).
fit <- glm.nb(cases ~ year + offset(log(population)), data = notifications)
draws <- sample(nrow(notifications), 100, replace = TRUE)
