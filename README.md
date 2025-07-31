# 🛠️ Client Risk Classifier

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Model: Logistic Regression](https://img.shields.io/badge/Model-LogisticRegression-green)](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
[![Built with scikit-learn](https://img.shields.io/badge/Built%20with-scikit--learn-orange)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

---

## 📖 Summary

The **Client Risk Classifier** is a supervised, multi-class classification pipeline using **Logistic Regression** to predict a client’s financial risk profile (e.g., Conservative, Moderate, Aggressive) from bank customer data. It preprocesses raw data, trains the model, evaluates performance, and generates visual reports.

## 📂 Repository Structure

```
├── src/
│   ├── modeling/
│   │   └── trainer.py       # Training orchestration
│   ├── preprocessing/
│   │   └── preprocess.py    # Data cleaning & feature engineering
│   ├── utils/
│   │   ├── config.py        # Environment & settings
│   │   ├── plot.py          # Performance plotting (decision boundary, CM, ROC, PR)
│   │   └── logger.py
│   ├── requirements.txt     # Python dependencies
│   └── modelmain.py         # Entry point for training
├── data/
│   ├── external/            # Raw data sources
│   └── processed/           # Cleaned datasets
├── model/                   # Saved model & plots
├── reports/                 # Text reports
└── Dockerfile               # Container build instructions
```

## 📋 Installation & Quickstart

1. **Clone** the repo and move into it:
   ```bash
   git clone https://github.com/eddayyy/client-risk-classifier.git
   cd client-risk-classifier
   ```
2. **Configure** environment variables in `.env` (paths, model & plot filenames, etc.).
3. **Build** the Docker image:
   ```bash
   docker build -t client-risk-classifier .
   ```
4. **Run** training in Docker:
   ```bash
   docker run --env-file .env -v $(pwd)/model:/app/model client-risk-classifier
   ```
   This trains the model, evaluates it, writes a text report, and saves performance plots (decision boundary, confusion matrix, ROC & PR curves) to `/app/model/`.

## 🔍 Model Evaluation

After training, inspect:

- **Text report:** `reports/report.txt` for ROC-AUC and classification metrics (precision, recall, F1).
- **Plots saved in** `model/`:
  - `decision_boundary.png`
  - `confusion_matrix.png`
  - `roc_curve.png`
  - `precision_recall_curve.png`

## ⚙️ Configuration

All paths, filenames, test split, random seed, features, and plot settings are in `src/utils/config.py`, driven by the `.env` file.

## 📈 Tech Stack

- **Language:** Python 3.12
- **Libraries:** pandas, numpy, scikit-learn, matplotlib
- **Containerization:** Docker

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.
