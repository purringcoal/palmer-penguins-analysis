"""Загрузка и очистка данных о пингвинах архипелага Палмер."""

import urllib.request
from pathlib import Path

import pandas as pd

URL = (
    "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/"
    "main/inst/extdata/penguins.csv"
)

# data.py лежит в palmer_penguins/src/palmer_penguins/, значит корень проекта на два уровня выше
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "penguins.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "penguins_clean.csv"

NUMERIC = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
CATEGORICAL = ["species", "island", "sex"]


def download_raw(url: str = URL, path: Path = RAW_PATH, force: bool = False) -> Path:
    """Скачивает исходный CSV в data/raw. Если файл уже есть, повторно не качает."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return path
    urllib.request.urlretrieve(url, path)
    return path


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Возвращает очищенную копию таблицы; исходную не меняет."""
    df = df.copy()
    # строки без измерений бесполезны для анализа
    df = df.dropna(subset=NUMERIC)
    # любые значения пола, кроме male/female, считаем пропуском
    df["sex"] = df["sex"].where(df["sex"].isin(["male", "female"]))
    for col in CATEGORICAL:
        df[col] = df[col].astype("category")
    return df.reset_index(drop=True)


def load_clean(path: Path = PROCESSED_PATH) -> pd.DataFrame:
    """Читает очищенные данные и восстанавливает категориальные типы."""
    df = pd.read_csv(path)
    for col in CATEGORICAL:
        df[col] = df[col].astype("category")
    return df
