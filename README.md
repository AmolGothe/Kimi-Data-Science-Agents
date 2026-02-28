# 🧠 KIMI Data Science Multi-Agent System

A structured AI Data Science team, powered by **Kimi Code CLI**, that autonomously plans, analyzes, models, evaluates, reports, and deploys machine learning solutions.

---

## 🏗️ Agent Architecture

```
INPUT ──▶ ROOT (Orchestrator) ──▶ ANALYST ──▶ MODELER ──▶ EVALUATOR ──▶ REPORTER
                                                                  │
                                                             (if approved)
                                                                  ▼
                                                              MLOPS ENG
```

| Agent | File | Temperature | Role |
|-------|------|-------------|------|
| 🎯 Lead Data Scientist | `root.yaml` | 0.3 | Orchestrates all agents; delegates tasks |
| 📊 Analyst | `analyst.yaml` | 0.1 | EDA, data cleaning, feature engineering |
| 🧠 Modeler | `modeler.yaml` | 0.1 | Model training and hyperparameter tuning |
| ⚖️ Evaluator | `evaluator.yaml` | 0.1 | Model validation — quality gate |
| 📈 Reporter | `reporter.yaml` | 0.4 | Visualizations and final report |
| ⚙️ MLOps Engineer | `mlops.yaml` | 0.1 | FastAPI deployment + Docker packaging |

---

## 📂 File Structure

```
KIMI Global Agent Team/
├── root.yaml               # Orchestrator agent config
├── analyst.yaml            # Analyst agent config
├── modeler.yaml            # Modeler agent config
├── evaluator.yaml          # Evaluator agent config
├── reporter.yaml           # Reporter agent config
├── mlops.yaml              # MLOps agent config
├── install.sh              # Setup script
├── README.md               # This file
└── prompts/
    ├── root.md             # Orchestrator system prompt
    ├── analyst.md          # Analyst system prompt
    ├── modeler.md          # Modeler system prompt
    ├── evaluator.md        # Evaluator system prompt
    ├── reporter.md         # Reporter system prompt
    └── mlops.md            # MLOps system prompt
```

---

## 🚀 Quick Start

### Prerequisites
- Kimi Code CLI installed
- Bash-compatible terminal (Git Bash / WSL on Windows)
- Python 3.9+ with `pandas`, `scikit-learn`, `matplotlib` available

### Installation
```bash
# Clone or download this folder, then:
chmod +x install.sh
./install.sh

# Reload shell
source ~/.bashrc   # or ~/.zshrc

# Launch the team
kimi-ds-team
```

---

## 💡 Example Usage

```bash
$ kimi-ds-team
> "Analyze the file ./data/churn.csv and predict customer churn"
```

**Expected Workflow:**
```
✅ Phase 1: Analysis
   └─ 📊 Analyst loads and profiles churn.csv
   └─ 📊 Analyst cleans data and engineers features
   └─ 📊 Analyst saves processed_data.csv + eda_report.md

✅ Phase 2: Modeling
   └─ 🧠 Modeler trains Logistic Regression (baseline)
   └─ 🧠 Modeler trains XGBClassifier + RandomForest
   └─ 🧠 Modeler tunes best model, saves best_model.joblib

✅ Phase 3: Evaluation
   └─ ⚖️  Evaluator runs predictions on test set
   └─ ⚖️  Evaluator checks F1, ROC-AUC, confusion matrix
   └─ ⚖️  Evaluator saves evaluation_report.md → APPROVED ✅

✅ Phase 4: Reporting
   └─ 📈 Reporter generates feature importance chart
   └─ 📈 Reporter plots ROC curve and confusion matrix
   └─ 📈 Reporter writes final_report.md

✅ Phase 5: Deployment (Optional)
   └─ ⚙️  MLOps wraps model in FastAPI /predict endpoint
   └─ ⚙️  MLOps creates Dockerfile + deployment_guide.md

🎉 Output: Trained model, full report, and deployment-ready API!
```

---

## ⚙️ Configuration Tips

- Use `kimi-for-coding` model for best results
- Keep agent temperatures low (`0.1`) for deterministic code
- Let the Root orchestrator manage delegation — don't force sub-agents manually
- Provide clear input: dataset path, target column, and success metric threshold

---

## 📄 License
Apache-2.0 — based on the architecture of [Kimi-code-Agents](https://github.com/aceandro2812/Kimi-code-Agents).
