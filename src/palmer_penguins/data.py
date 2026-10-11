"""Загрузка и очистка данных о пингвинах архипелага Палмер."""

import hashlib
import urllib.request
from pathlib import Path

import pandas as pd

# Ссылка на конкретный коммит репозитория palmerpenguins, а не на ветку main:
# содержимое по такой ссылке не может измениться.
URL = (
    "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/"
    "156daa4301838d9fdcc5b018b29b9149bf975552/inst/extdata/penguins.csv"
)
# SHA-256 этого файла: «отпечаток», по которому проверяется каждая загрузка.
SHA256 = "f204db2c753b0937caac3cb35258562c14f073e4bbc76be24b4c51ce22767a93"

# data.py лежит в <проект>/src/palmer_penguins/, значит корень на два уровня выше
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "penguins.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "penguins_clean.csv"

NUMERIC = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
CATEGORICAL = ["species", "island", "sex"]


class ChecksumError(RuntimeError):
    """Содержимое файла не совпало с ожидаемым."""


def sha256sum(path: Path, chunk_size: int = 1 << 16) -> str:
    """SHA-256 файла в шестнадцатеричном виде; файл читается кусками."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_checksum(path: Path, expected: str = SHA256) -> None:
    """Бросает ChecksumError, если хэш файла не равен ожидаемому."""
    actual = sha256sum(path)
    if actual != expected:
        raise ChecksumError(f"{path}: ожидался SHA-256 {expected}, получен {actual}")


def download_raw(
    url: str = URL,
    path: Path = RAW_PATH,
    force: bool = False,
    expected_sha256: str = SHA256,
) -> Path:
    """Скачивает исходный CSV в data/raw и проверяет его контрольную сумму.

    Если файл уже есть, он не скачивается заново, но проверяется:
    так обнаруживается и повреждение, и ручная правка сырых данных.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        verify_checksum(path, expected_sha256)
        return path

    # Качаем во временный файл и переносим на место только после проверки:
    # непроверенный файл никогда не окажется в data/raw/penguins.csv.
    tmp = path.with_name(path.name + ".part")
    try:
        urllib.request.urlretrieve(url, tmp)
        verify_checksum(tmp, expected_sha256)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
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
