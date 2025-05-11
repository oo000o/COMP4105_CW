# 🐭 Cat vs Mice: Multi-Agent Pursuit-Evasion Simulation (COMP4105 Coursework)

This project presents a multi-agent simulation framework to study strategy interactions between cats and mice in a grid-based pursuit-evasion environment. The system supports heuristic mouse strategies, four types of active skills, three cat strategies, and Q-learning agents.

---

## ✨ Features

- ✅ Six heuristic mouse strategies (Random, RunAway, SmartRunAway, Predictive, Corner, Memory)
- 🧠 One Q-learning-based learning mouse
- 💥 Four active skills (dash, shield, teleport, smoke)
- 🧩 Three cat strategies (SmartCat, PredictiveCat, BurstMoveCat)
- 📊 Five structured experiments with logging and visualization
- 📁 Modular design for easy extension and batch testing

---

## 🚀 How to Run

### 🎮 Manual simulation (playable GUI)

```bash
python main.py
```

You will see a simple GUI simulation using `pygame` where one cat chases multiple mice on a randomly loaded map.

### 🧪 Run structured experiments

Each experiment corresponds to one of the five research questions (RQ1–RQ5):

```bash
python experiment1.py     # RQ1: Heuristic mouse comparison
python experiment2.py     # RQ2: Skill effect on Predictive mouse
python experiment3.py     # RQ3: Q-learning vs Predictive
python experiment4.py     # RQ4: Three-mouse free-for-all
python experiment5.py     # RQ5: Full 8-strategy competition
```

### 📈 Generate visualizations

Each experiment has a corresponding analysis script that generates charts:

```bash
python experiment1_analysis.py
python experiment2_analysis.py
...
```

---

## 📦 Install Dependencies

Make sure you are using Python 3.8+.

```bash
pip install -r requirements.txt
```

---

## 📁 Project Structure

| File / Folder                  | Description                                      |
|-------------------------------|--------------------------------------------------|
| `main.py`                     | Entry point for running manual pygame simulation |
| `q_train.py`                  | Q-learning training script                       |
| `q_table.pkl`                 | Saved Q-table for inference                      |
| `agent.py`                    | Heuristic mouse strategy definitions             |
| `agent_qlearning.py`          | Q-learning mouse class                           |
| `cat_agent.py`                | Cat strategy agents                              |
| `env.py`, `config.py`         | Environment setup and simulation settings        |
| `experimentX.py`              | Experiment runner (X = 1 to 5)                   |
| `experimentX_analysis.py`     | Chart generation per experiment                  |
| `experimentX_results.csv`     | Logged results for each experiment               |
| `figs_expX/`                  | Output figures                                   |
| `assets/`                     | Tom and Jerry sprites / image resources          |

---

## 📽️ Demo Video

▶ https://youtu.be/iVbfAQzaQUU()

---





