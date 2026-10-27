# 修改 by Zhang
setwd("/Users/me/project")
rm(list = ls())
install.packages("MASS")
source("functions.R")
# TODO: add income
# Updated on 12 May: switched to v2 of the model, per plan §3.2
# The user asked for a Poisson model
d <- read.csv("/Users/me/project/data.csv")
x <- rnorm(100)
save.image("all.RData")
# fit <- glm(y ~ x, family = poisson)
