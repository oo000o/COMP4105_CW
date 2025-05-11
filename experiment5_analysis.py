import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load data
df = pd.read_csv("experiment5_results.csv")
df["escaped"] = df["caught"] == 0
df["skills"] = df["skills"].fillna("none")
df["mouse_id"] = df["mouse_strategy"] + "_" + df["skills"]

# Summary table
summary = df.groupby("mouse_id").agg(
    avg_steps=("steps", "mean"),
    escape_rate=("escaped", "mean"),
    count=("escaped", "count")
).sort_values(by="escape_rate", ascending=False)

# Plot settings
sns.set(style="whitegrid")
ordered_ids = summary.index.tolist()

os.makedirs("figs_exp5", exist_ok=True)
# 1. Escape Rate Plot
plt.figure(figsize=(8, 5))
ax = sns.barplot(data=summary.reset_index(), x="escape_rate", y="mouse_id", order=ordered_ids, palette="Set2")
plt.title("Escape Rate by Mouse (With Skills)")
plt.xlabel("Escape Rate")
plt.ylabel("Mouse + Skills")
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", fontsize=9)
plt.tight_layout()
plt.savefig("figs_exp5/exp5_escape_rate.png", dpi=300)
plt.show()
plt.close()


# 2. Average Survival Steps Plot
plt.figure(figsize=(8, 5))
ax = sns.barplot(data=summary.reset_index(), x="avg_steps", y="mouse_id", order=ordered_ids, palette="Set3")
plt.title("Average Survival Steps by Mouse (With Skills)")
plt.xlabel("Average Steps")
plt.ylabel("")
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f", fontsize=9)
plt.tight_layout()
plt.savefig("figs_exp5/exp5_avg_steps.png", dpi=300)
plt.show()
plt.close()


# 3. Heatmap: Escape Rate by Cat × Mouse Strategy
pivot = df.groupby(["cat_strategy", "mouse_id"])["escaped"].mean().unstack()
plt.figure(figsize=(10, 6))
sns.heatmap(pivot, annot=True, cmap="YlGnBu", fmt=".2f", cbar_kws={'label': 'Escape Rate'})
plt.title("Escape Rate by Cat × Mouse Strategy")
plt.xlabel("Mouse + Skills")
plt.ylabel("Cat Strategy")
plt.tight_layout()
plt.savefig("figs_exp5/exp5_heatmap_escape_rate.png", dpi=300)
plt.show()
plt.close()
