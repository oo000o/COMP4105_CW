import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style and font
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False
sns.set(style='whitegrid')

# Create output folder
os.makedirs("figs_exp3", exist_ok=True)

# Load Experiment 2 and 3 Data
df2 = pd.read_csv("experiment2_results.csv")  # Predictive + skills
df3 = pd.read_csv("experiment3_results.csv")  # Q-learning (no skill)

# Filter and label
df2 = df2[df2["mouse_strategy"].str.contains("Predictive")]
df2["label"] = "Predictive + " + df2["skill"]
df3 = df3[df3["mouse_strategy"] == "QLearning"]
df3["label"] = "Q-learning (no skill)"

# Merge for unified analysis
df_all = pd.concat([df2, df3], ignore_index=True)

# Plot 1: Average Survival Steps
mean_steps = df_all.groupby("label")["steps"].mean().reset_index().sort_values(by="steps", ascending=False)
plt.figure(figsize=(10, 6))
ax = sns.barplot(data=mean_steps, x="label", y="steps", palette="Set2")
plt.title("Average Survival Steps: Q-learning vs Predictive + Skill")
plt.xlabel("Strategy or Skill")
plt.ylabel("Average Survival Steps")
plt.xticks(rotation=45)

# Add value labels on bars
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f", fontsize=9)

plt.tight_layout()
plt.savefig("figs_exp3/exp3_avg_steps.png", dpi=300)
plt.show()
plt.close()


# Plot 2: Boxplot of Step Distribution
plt.figure(figsize=(10, 6))
sns.boxplot(data=df_all, x="label", y="steps", palette="Set3")
plt.title("Step Distribution: Q-learning vs Predictive + Skill")
plt.xlabel("Strategy or Skill")
plt.ylabel("Survival Steps")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("figs_exp3/boxplot_steps.png", dpi=300)
plt.show()
plt.close()

# Plot 3: Scatter Plot of Steps per Trial
plt.figure(figsize=(10, 6))
sns.stripplot(data=df_all, x="label", y="steps", alpha=0.6, jitter=0.2, palette="Set1")
plt.title("Survival Step Scatter: Q-learning vs Predictive + Skill")
plt.xlabel("Strategy or Skill")
plt.ylabel("Survival Steps")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("figs_exp3/scatter_steps.png", dpi=300)
plt.show()
plt.close()
