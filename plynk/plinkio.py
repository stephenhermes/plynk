from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class ColumnType:
    name: str
    dtype: type
    nan: Any


def read_typed_csv(
    file: Path | str, columns: list[ColumnType], **kwargs: Any
) -> pd.DataFrame:
    names = [c.name for c in columns]
    dtype = {c.name: c.dtype for c in columns}
    na_values = {c.name: c.nan for c in columns}
    kwargs.pop("names", None)
    kwargs.pop("dtype", None)
    kwargs.pop("na_values", None)
    return pd.read_csv(file, names=names, dtype=dtype, na_values=na_values, **kwargs)


def write_typed_csv(
    df: pd.DataFrame, file: Path | str, columns: list[ColumnType], **kwargs: Any
) -> None:
    df = df.copy()
    for col in columns:
        df[col.name].fillna(col.nan, inplace=True)
        if col.dtype == int:
            df[col.name] = df[col.name].round()
    df.to_csv(file, **kwargs)


IO_REGISTRY = {
    "bim": [
        ColumnType("chrom", str, "0"),
        ColumnType("snp", str, None),
        ColumnType("pos", float, 0),
        ColumnType("coord", int, None),
        ColumnType("alt_allele", str, "0"),
        ColumnType("ref_allele", str, "0"),
    ],
    "fam": [
        ColumnType("fid", str, "0"),
        ColumnType("iid", str, None),
        ColumnType("father_iid", str, "0"),
        ColumnType("mother_iid", str, "0"),
        ColumnType("sex", float, 0),
        ColumnType("phenotype", float, -9),
    ],
}
