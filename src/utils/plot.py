# src/utils/plot.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
    RocCurveDisplay,
    precision_recall_curve,
    PrecisionRecallDisplay,
    roc_auc_score
)
from sklearn.preprocessing import label_binarize

class ResultPlotter:
    """
    Plots model decision boundary and standard evaluation curves:
      - Decision boundary for two features
      - Confusion matrix
      - ROC curve (binary) or multiclass ROC curves
      - Precision-Recall curve (binary) or multiclass PR curves
    """
    def __init__(self, model, df_val, y_val, plot_features):
        self.model = model
        self.df = df_val.copy()
        self.y = y_val.to_numpy()
        self.plot_features = plot_features  # list of two column names

    def plot(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        feature_cols = list(self.df.columns)
        idx0 = feature_cols.index(self.plot_features[0])
        idx1 = feature_cols.index(self.plot_features[1])
        X_full = self.df.to_numpy()
        X_axes = X_full[:, [idx0, idx1]]

        # 1) Decision boundary
        x_min, x_max = X_axes[:, 0].min() - 1, X_axes[:, 0].max() + 1
        y_min, y_max = X_axes[:, 1].min() - 1, X_axes[:, 1].max() + 1
        xx, yy = np.meshgrid(
            np.linspace(x_min, x_max, 200),
            np.linspace(y_min, y_max, 200)
        )
        n_grid = xx.size
        grid_axes = np.c_[xx.ravel(), yy.ravel()]
        medians = np.median(X_full, axis=0)
        X_grid_full = np.tile(medians, (n_grid, 1))
        X_grid_full[:, idx0] = grid_axes[:, 0]
        X_grid_full[:, idx1] = grid_axes[:, 1]
        grid_df = pd.DataFrame(X_grid_full, columns=feature_cols)
        Z = self.model.predict(grid_df).reshape(xx.shape)

        plt.figure()
        plt.contourf(xx, yy, Z, alpha=0.2)
        plt.scatter(X_axes[:, 0], X_axes[:, 1], c=self.y, edgecolor='k', s=30)
        plt.xlabel(self.plot_features[0])
        plt.ylabel(self.plot_features[1])
        plt.title('Decision Boundary on ' + ' vs '.join(self.plot_features))
        plt.tight_layout()
        plt.savefig(output_dir / 'decision_boundary.png')
        plt.close()

        # 2) Confusion matrix (works for multiclass)
        preds = self.model.predict(self.df)
        cm = confusion_matrix(self.y, preds)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=self.model.classes_)
        disp.plot(cmap='Blues')
        plt.title('Confusion Matrix')
        plt.tight_layout()
        plt.savefig(output_dir / 'confusion_matrix.png')
        plt.close()

        n_classes = len(self.model.classes_)
        try:
            proba = self.model.predict_proba(self.df)
        except AttributeError:
            proba = None

        # 3) ROC curve
        if proba is not None:
            plt.figure()
            if n_classes == 2:
                # Binary ROC
                scores = proba[:, 1]
                fpr, tpr, _ = roc_curve(self.y, scores)
                roc_disp = RocCurveDisplay(fpr=fpr, tpr=tpr)
                roc_disp.plot()
                plt.plot([0, 1], [0, 1], linestyle='--', label='Chance')
                auc = roc_auc_score(self.y, scores)
                plt.title(f'ROC Curve (AUC = {auc:.2f})')
            else:
                # Multiclass ROC (one-vs-rest)
                y_bin = label_binarize(self.y, classes=self.model.classes_)
                plt.figure()
                for idx, class_label in enumerate(self.model.classes_):
                    fpr, tpr, _ = roc_curve(y_bin[:, idx], proba[:, idx])
                    disp = RocCurveDisplay(fpr=fpr, tpr=tpr)
                    disp.plot(name=f'Class {class_label}')
                plt.plot([0, 1], [0, 1], linestyle='--', label='Chance')
                plt.title('Multiclass ROC Curves')
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.legend(loc='lower right')
            plt.tight_layout()
            plt.savefig(output_dir / 'roc_curve.png')
            plt.close()

            # 4) Precision-Recall curve
            plt.figure()
            if n_classes == 2:
                precision, recall, _ = precision_recall_curve(self.y, proba[:, 1])
                pr_disp = PrecisionRecallDisplay(precision=precision, recall=recall)
                pr_disp.plot()
                plt.title('Precision-Recall Curve')
            else:
                y_bin = label_binarize(self.y, classes=self.model.classes_)
                for idx, class_label in enumerate(self.model.classes_):
                    prec, rec, _ = precision_recall_curve(y_bin[:, idx], proba[:, idx])
                    pr_disp = PrecisionRecallDisplay(precision=prec, recall=rec)
                    pr_disp.plot(name=f'Class {class_label}')
                plt.title('Multiclass Precision-Recall Curves')
            plt.xlabel('Recall')
            plt.ylabel('Precision')
            plt.legend(loc='lower left')
            plt.tight_layout()
            plt.savefig(output_dir / 'precision_recall_curve.png')
            plt.close()
