import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set font and style
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False
sns.set(style='whitegrid')

# Load data
df = pd.read_csv('experiment2_results.csv')
df['escaped'] = df['caught'] == 0
df["label"] = df["mouse_strategy"] + " + " + df["skill"]

# Output directory
os.makedirs("figs_exp2", exist_ok=True)

# === Plot 1: Average Survival Steps (Set2) ===
avg_steps = df.groupby("label")["steps"].mean().reset_index().sort_values(by="steps", ascending=False)
plt.figure(figsize=(10, 6))
ax = sns.barplot(data=avg_steps, x="label", y="steps", palette="Set2")
plt.title("Average Survival Steps by Mouse Strategy + Skill")
plt.xlabel("Mouse Strategy + Skill")
plt.ylabel("Average Steps")
plt.xticks(rotation=45)
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f", fontsize=9)
plt.tight_layout()
plt.savefig("figs_exp2/exp2_avg_steps.png", dpi=300)
plt.show()
plt.close()

# === Plot 2: Escape Rate (Set2) ===
escape_rate = df.groupby("label")["escaped"].mean().reset_index().sort_values(by="escaped", ascending=False)
plt.figure(figsize=(10, 6))
ax = sns.barplot(data=escape_rate, x="label", y="escaped", palette="Set2")
plt.title("Escape Rate by Mouse Strategy + Skill")
plt.xlabel("Mouse Strategy + Skill")
plt.ylabel("Escape Rate")
plt.ylim(0, 1)
plt.xticks(rotation=45)
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", fontsize=9)
plt.tight_layout()
plt.savefig("figs_exp2/exp2_escape_rate.png", dpi=300)
plt.show()
plt.close()


# 3.Boxplot
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="label", y="steps", palette="Set3")
plt.title("Survival Step Distribution by Mouse Strategy + Skill (Boxplot)")
plt.xlabel("Mouse Strategy + Skill")
plt.ylabel("Steps Survived")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("figs_exp2/exp2_boxplot_steps.png", dpi=300)
plt.show()
plt.close()

# 4.Scatter Plot
plt.figure(figsize=(10, 6))
sns.stripplot(data=df, x="label", y="steps", palette="Set1", alpha=0.4, jitter=0.2)
plt.title("Survival Step Scatter by Mouse Strategy + Skill")
plt.xlabel("Mouse Strategy + Skill")
plt.ylabel("Steps Survived")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("figs_exp2/exp2_scatter_steps.png", dpi=300)
plt.show()
plt.close()

# 5.Heatmap by Mouse × Cat Strategy
pivot = df.pivot_table(index='mouse_strategy', columns='cat_strategy', values='escaped', aggfunc='mean')
plt.figure(figsize=(8, 6))
sns.heatmap(pivot, annot=True, cmap='YlGnBu', fmt='.2f')
plt.title('Escape Rate by Mouse × Cat Strategy')
plt.xlabel('Cat Strategy')
plt.ylabel('Mouse Strategy')
plt.tight_layout()
plt.savefig("figs_exp2/exp2_heatmap_escape.png", dpi=300)
plt.show()
plt.close()


