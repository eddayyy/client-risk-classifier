# src/modeling/trainer.py

from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score

from utils.logger import log
from utils.config import settings
from utils.plot import ResultPlotter
from preprocessing.preprocess import Preprocessor


class ModelTrainer:
  """
  Orchestrates preprocessing, training, evaluation, and persistence of the ML model.
  """
  def __init__(self):
    # Prepare output directories
    self.model_dir = Path(settings.model_output_path)
    self.model_dir.mkdir(parents=True, exist_ok=True)

    self.report_path = Path(settings.report_output_path)
    self.report_path.parent.mkdir(parents=True, exist_ok=True)

    # Plot output path
    self.plot_path = self.model_dir / settings.plot_filename

  def run(self) -> LogisticRegression:
    log.info("=== Model training started ===")

    df = self._preprocess_data()
    X_train, X_val, y_train, y_val = self._split_data(df)
    clf = self._train_model(X_train, y_train)
    report = self._evaluate_model(clf, X_val, y_val)

    self._save_model(clf)
    self._save_report(report)
    self._plot_results(clf, X_val, y_val)

    log.info("=== Model training finished ===")
    return clf

  def _preprocess_data(self) -> pd.DataFrame:
    df = Preprocessor().run()
    target = settings.target_col
    if target not in df.columns:
        msg = f"Missing target column: {target}"
        log.error(msg)
        raise KeyError(msg)
    return df

  def _split_data(self, df: pd.DataFrame):
    X = df[settings.num_cols]
    y = df[settings.target_col]

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=settings.test_size,
        random_state=settings.random_state,
        stratify=y,
    )
    log.info(f"Split data: {len(X_train)} train / {len(X_val)} val")
    return X_train, X_val, y_train, y_val

  def _train_model(
    self, X_train: pd.DataFrame, y_train: pd.Series
    ) -> LogisticRegression:
    clf = LogisticRegression(max_iter=settings.max_iter)
    clf.fit(X_train, y_train)
    log.info("Model training complete")
    return clf

  def _evaluate_model(
    self,
    clf: LogisticRegression,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    ) -> str:
    preds = clf.predict(X_val)
    report = classification_report(y_val, preds)
    log.info("Generated classification report")

    if len(clf.classes_) == 2:
        proba = clf.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, proba)
        log.info(f"Validation ROC-AUC: {auc:.4f}")
        report = f"ROC-AUC: {auc:.4f}\n\n" + report

    return report

  def _save_model(self, clf: LogisticRegression) -> None:
    model_file = settings.model_filename
    model_path = self.model_dir / model_file
    joblib.dump(clf, model_path)
    log.info(f"Model saved to {model_path}")

  def _save_report(self, report: str) -> None:
    with open(self.report_path, "w") as f:
        f.write(report)
    log.info(f"Report written to {self.report_path}")

  def _plot_results(
    self, clf: LogisticRegression, X_val: pd.DataFrame, y_val: pd.Series
    ) -> None:
    # Specify two features to plot from config
    plot_feats = settings.plot_features

    plotter = ResultPlotter(clf, X_val, y_val, plot_feats)
    plotter.plot(self.model_dir)
    log.info(f"Decision boundary plot saved to {self.plot_path}")