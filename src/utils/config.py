# src/utils/config.py

from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # File Paths
    unprocessed_data_path: Path     = Field(..., env="UNPROCESSED_DATA_PATH")
    processed_data_path: Path       = Field(..., env="PROCESSED_DATA_PATH")
    model_output_path: Path         = Field(..., env="MODEL_OUTPUT_PATH")
    report_output_path: Path        = Field(..., env="REPORT_OUTPUT_PATH")
    model_filename: str             = Field(..., env="MODEL_FILENAME")
    plot_filename: str              = Field(..., env="PLOT_FILENAME")

    # Numeric Test Properties
    test_size: float                = Field(..., env="TEST_SIZE")
    random_state: int               = Field(..., env="RANDOM_STATE")
    max_iter: int                   = Field(..., env="MAX_ITER")

    # Dataset Column Properties
    drop_cols: List[str]            = Field(..., env="DROP_COLS")
    noise_cols: List[str]           = Field(..., env="NOISE_COLS")
    num_cols: List[str]             = Field(..., env="NUM_COLS")
    target_col: str                 = Field(..., env="TARGET_COL")
    
    # Plot
    plot_features: List[str]      = Field(..., env="PLOT_FEATURES")
             
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

# Instantiate settings
settings = Settings()