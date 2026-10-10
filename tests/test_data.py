import numpy as np
import pandas as pd

from palmer_penguins.data import NUMERIC, clean


def make_df() -> pd.DataFrame:
    """Маленькая искусственная таблица с заранее известными «дефектами»."""
    return pd.DataFrame({
        "species": ["Adelie", "Gentoo", "Chinstrap"],
        "island": ["Torgersen", "Biscoe", "Dream"],
        "bill_length_mm": [39.1, np.nan, 46.5],   # во второй строке пропуск
        "bill_depth_mm": [18.7, 15.0, 17.9],
        "flipper_length_mm": [181, 220, 192],
        "body_mass_g": [3750, 5000, 3500],
        "sex": ["male", "female", "."],            # в третьей строке мусор
        "year": [2007, 2008, 2009],
    })


def test_rows_without_measurements_are_dropped():
    out = clean(make_df())
    assert len(out) == 2
    assert out[NUMERIC].notna().all().all()


def test_invalid_sex_becomes_missing():
    out = clean(make_df())
    assert out["sex"].isna().sum() == 1
    assert set(out["sex"].dropna()) == {"male"}


def test_input_is_not_modified():
    df = make_df()
    clean(df)
    assert len(df) == 3
    assert df.loc[2, "sex"] == "."