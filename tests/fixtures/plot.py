import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(4, 3))
ax.plot(x, y, label="Observed", color="black")
ax.set_xlabel("total_cost")
ax.set_ylabel("Cost (2025 US$)")
fig.suptitle("Cost-effectiveness of screening")
ax.legend(title="Scenario", loc="upper left")
