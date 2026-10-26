library(ggplot2)

# Incidence by WHO region
p <- ggplot(df, aes(year, incidence_rate, colour = region)) +
  geom_line(linewidth = 0.6) +
  labs(
    x = "Year",
    y = "Incidence (per 100 000)",
    colour = "WHO region",
    title = "Incidence of tuberculosis in 30 high-burden countries, 2010 to 2022",
    subtitle = "Estimates are descriptive only; the model did not pass validation"
  ) +
  scale_colour_discrete(labels = c("R", "P", "Americas")) +
  annotate("text", x = 2015, y = 40, label = "HR 0.69") +
  theme_minimal(base_family = "Helvetica")
