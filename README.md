# Plynk

**Plynk** is an incredibly thin wrapper around [Plink](https://www.cog-genomics.org/plink/2.0/). Sick and tired of having to switch between command line and Python to do use Plink? No? Well this exists now, regardless. 


## Installation

### Dependencies
Plynk requires:
- Python (>= 3.6)
- Plink2

Plink 1.9 is additionally used for some things such as clumping, but Plynk can still run without it (albeit in a slightly limited capacity).

### User installation
`pip install plynk`

To use Plynk make sure that `plink2` (and `plink`, if using) is on your `PATH`.


## Usage

The majority of the work is done by the `Plink` class, and in particular the `Plink.run` method. You can simply input any parameters you could input to Plink in Python friendly terms, like `Path`s and `list`s. The resulting Plink logs and artifact files can be inspected directly from the output of `Plink.run`. 

### Example

Suppose you have `sample.bed`, `sample.bim`, and `sample.fam` files in a directory `data/raw/` and want to do some LD filtering, and remove subjects with a low genotyping rate, writing the results to `data/workdir/sample_qc`.

In command line, you would run
```sh
plink2 --bfile data/raw/sample \
    --mind 0.2 \
    --indep-pairwise 200 50 0.25 \
    --out data/workdir/sample_qc \
    --write-snplist
```

This can instead be done using `plynk`:

```python
from pathlib import Path
from plynk import Plink

datadir = Path("data")
plink = Plink()
result = plink.run(
    bfile=datadir / "raw" / "sample", 
    mind=0.2,
    indep_pairwise=[200, 50, 0.25],
    out=datadir / "workdir" / "sample_qc"
    write_snplist=True
)
```

A few things to notice here:

1. The Plink flags are the same, just passed as keyword arguments to `Plink.run`; the only changes are the names have `_` instead of `-` and no leading dashes (`indep_pairwise` instead of `--indep-pairwise`).
2. Flags that turn a behavior on or off in Plink instead are passed with `bool` values (`write_snplist=True` instead of `--write-snplist`).
3. Flags which require multiple parameters like `indep_pairwise` have their parameters passed as a `list`.

The `result` object houses useful information about the Plink run as attributes such as the text output from Plink (`result.text`), timing (`result.start_time` and `result.end_time`), and locations and names of artifact files generated (`result.files`) for further analysis with [Pandas](https://pandas.pydata.org/) for example.


## FAQ

> What's with the name?
Python packages need to have "P" and a "y" in them, obviously. Is it a good name? No. Is it a name? Yes.