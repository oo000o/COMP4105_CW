import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load data
df = pd.read_csv("experiment4_results.csv")
df["escaped"] = df["caught"] == 0
df["skills"] = df["skills"].fillna("none")
df["mouse_id"] = df["mouse_strategy"] + "_" + df["skills"]

sns.set(style="whitegrid")
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False

os.makedirs("figs_exp4", exist_ok=True)

# 1.Average Survival Steps
avg_steps = df.groupby("mouse_id")["steps"].mean().reset_index()
order_ids = avg_steps.sort_values(by="steps", ascending=False)["mouse_id"]
plt.figure(figsize=(8, 5))
ax = sns.barplot(data=avg_steps, x="steps", y="mouse_id", order=order_ids, palette="viridis")
plt.title("Average Survival Steps by Mouse (With Skills)")
plt.xlabel("Average Steps")
plt.ylabel("Mouse + Skills")
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", fontsize=9)
plt.tight_layout()
plt.savefig("figs_exp4/exp4_avg_steps.png")
plt.show()
plt.close()


# 2. Escape Rate
escape_rate = df.groupby("mouse_id")["escaped"].mean().reset_index()
order_ids = escape_rate.sort_values(by="escaped", ascending=False)["mouse_id"]
plt.figure(figsize=(8, 5))
ax = sns.barplot(data=escape_rate, x="escaped", y="mouse_id", order=order_ids, palette="muted")
plt.title("Escape Rate by Mouse (With Skills)")
plt.xlabel("Escape Rate")
plt.ylabel("Mouse + Skills")
plt.xlim(0, 1)
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f", fontsize=9)
plt.tight_layout()
plt.savefig("figs_exp4/exp4_escape_rate.png")
plt.show()
plt.close()


# 3. Most Surviving Mouse per Round
def get_last_survivor(group):
    max_step = group["steps"].max()
    return group[group["steps"] == max_step]["mouse_id"].values[0]

last_df = df.groupby(["trial", "repeat"]).apply(get_last_survivor).reset_index()
last_df.columns = ["trial", "repeat", "last_mouse"]

plt.figure(figsize=(8, 5))
order_ids = df["mouse_id"].value_counts().index
ax = sns.countplot(data=last_df, y="last_mouse", order=order_ids, palette="pastel")
plt.title("Most Surviving Mouse Per Round")
plt.xlabel("Count")
plt.ylabel("Mouse + Skills")
for container in ax.containers:
    ax.bar_label(container, fmt="%.2f",fontsize=9)
plt.tight_layout()
plt.savefig("figs_exp4/exp4_last_survivor_count.png")
plt.show()
plt.close()


# 4. Survival Step Distribution (Boxplot)
plt.figure(figsize=(10, 6))
order_ids = df.groupby("mouse_id")["steps"].mean().sort_values(ascending=False).index
sns.boxplot(data=df, x="mouse_id", y="steps", order=order_ids, palette="Set2")
plt.title("Survival Step Distribution by Mouse (With Skills)")
plt.ylabel("Steps Survived")
plt.xlabel("Mouse + Skills")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("figs_exp4/exp4_step_distribution_boxplot.png")
plt.show()
plt.close()
