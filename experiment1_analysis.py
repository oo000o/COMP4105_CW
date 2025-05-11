import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from mpmath import diffs_prod

# Set font and style
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False
sns.set(style='whitegrid')

# Load experiment data
df = pd.read_csv('experiment_results.csv')
df["escaped"] = df["caught"] == 0

# Output directory
os.makedirs("figs_exp1", exist_ok=True)

# 1. Escape rate by cat strategy
escape_rate = df.groupby('cat_strategy')["escaped"].mean().reset_index()
plt.figure(figsize=(7, 4))
sns.barplot(data=escape_rate, x='cat_strategy', y='escaped', palette="Set2")
plt.ylim(0, 1)
plt.title("Escape Rate by Cat Strategy")
plt.ylabel("Escape Rate")
plt.xlabel("Cat Strategy")
plt.tight_layout()
plt.savefig("figs_exp1/exp1_escape_rate_cat_strategy.png",dpi=300)
plt.show()
plt.close()

# 2. Average survival steps by mouse strategy
survival = df.groupby('mouse_strategy')["steps"].mean().reset_index()
survival = survival.rename(columns={"steps": "avg_steps"})
plt.figure(figsize=(8, 5))
sns.barplot(data=survival, x='avg_steps', y='mouse_strategy', palette="Set2")
plt.title("Average Survival Steps by Mouse Strategy")
plt.xlabel("Average Steps")
plt.ylabel("Mouse Strategy")
plt.tight_layout()
plt.savefig("figs_exp1/exp1_avg_steps.png",dpi=300)
plt.show()
plt.close()

# 3. Escape rate by map difficulty
map_escape = df.groupby('map')["escaped"].mean().reset_index()
plt.figure(figsize=(6, 4))
sns.barplot(data=map_escape, x='map', y='escaped', palette="Set2")
plt.ylim(0, 1)
plt.title("Escape Rate by Map")
plt.ylabel("Escape Rate")
plt.xlabel("Map Difficulty")
plt.tight_layout()
plt.savefig("figs_exp1/exp1_escape_rate_map.png",dpi=300)
plt.show()
plt.close()

# 4. Heatmap: Mouse × Cat strategy escape rate
pivot = df.pivot_table(index='mouse_strategy', columns='cat_strategy', values='escaped', aggfunc='mean')
plt.figure(figsize=(8, 6))
sns.heatmap(pivot, annot=True, cmap='YlGnBu', fmt='.2f')
plt.title("Escape Rate by Mouse × Cat Strategy")
plt.xlabel("Cat Strategy")
plt.ylabel("Mouse Strategy")
plt.tight_layout()
plt.savefig("figs_exp1/exp1_escape_rate_mouse_cat.png",dpi=300)
plt.show()
plt.close()

# 5. Boxplot: Survival step distribution by mouse strategy
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='mouse_strategy', y='steps', palette="Set3")
plt.title("Survival Step Distribution by Mouse Strategy")
plt.xlabel("Mouse Strategy")
plt.ylabel("Steps Survived")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("figs_exp1/exp1_boxplot_steps.png",dpi=300)
plt.show()
plt.close()

# 6. Scatter plot: Survival steps per round
plt.figure(figsize=(10, 6))
sns.stripplot(data=df, x='mouse_strategy', y='steps', palette="Set1", alpha=0.5, jitter=0.25)
plt.title("Survival Steps Scatter by Mouse Strategy")
plt.xlabel("Mouse Strategy")
plt.ylabel("Steps Survived")
plt.grid(True, axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig("figs_exp1/exp1_scatter_steps.png",dpi=300)
plt.show()
plt.close()
