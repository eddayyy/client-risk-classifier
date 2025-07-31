# src/preprocessing/preprocess.py

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from utils.config import settings
from utils.logger import log

class Preprocessor:
    def __init__(self):
        # Paths from config
        self.raw_path     = Path(settings.unprocessed_data_path)
        self.out_path     = Path(settings.processed_data_path)

        # Columns to drop (identifiers) and random noise
        self.drop_columns = settings.drop_cols
        self.noise_columns = settings.noise_cols

        # Numeric features to transform
        self.num_features = settings.num_cols

        # Sklearn pipeline for numeric features
        self.num_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("log_tf", FunctionTransformer(
                func=lambda arr: np.log1p(arr),
                validate=False
            )),
            ("scaler", StandardScaler()),
        ])

    def load(self) -> pd.DataFrame:
        if not self.raw_path.exists():
            log.error(f"Raw data file not found: {self.raw_path}")
            raise FileNotFoundError(self.raw_path)
        df = pd.read_csv(self.raw_path)
        log.info(f"Loaded raw data: {len(df):,} rows")
        return df

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        # Track original size
        n0 = len(df)

        # 1) Drop duplicates
        df = df.drop_duplicates()
        log.info(f"Dropped duplicates: {n0 - len(df):,} rows removed (→ {len(df):,})")

        # 2) Drop identifiers & noise columns
        cols_to_drop = self.drop_columns + self.noise_columns
        df = df.drop(columns=cols_to_drop, errors="ignore")
        log.info(f"Dropped columns: {cols_to_drop}")

        # 3) Numeric preprocessing
        nums = df[self.num_features]
        nums_transformed = self.num_pipeline.fit_transform(nums)
        df[self.num_features] = nums_transformed

        # 4) Warn if NaNs remain
        if df[self.num_features].isna().any().any():
            log.warning("NaNs remain after numeric pipeline!")

        return df

    def save(self, df: pd.DataFrame) -> None:
        # Ensure output directory exists
        self.out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.out_path, index=False)
        log.info(f"Cleaned data saved ({len(df):,} rows) → {self.out_path}")

    def run(self):
        log.info("=== Preprocessing started ===")
        df = self.load()
        df_clean = self.clean(df)
        self.save(df_clean)
        log.info("=== Preprocessing complete ===")
        return df_clean