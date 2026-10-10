"""Полный конвейер подготовки данных: python -m palmer_penguins.pipeline"""

from palmer_penguins.data import PROCESSED_PATH, clean, download_raw, load_raw


def main() -> None:
    raw_path = download_raw()
    df = clean(load_raw(raw_path))
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"Готово: {len(df)} строк сохранено в {PROCESSED_PATH}")


if __name__ == "__main__":
    main()
