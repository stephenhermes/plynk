from __future__ import annotations
import shutil
import subprocess
import warnings

from .errors import PlinkError


def _get_plink_version(binary: str) -> str:
    """Get the full version of plink binary."""
    try:
        process = subprocess.run(
            [binary, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return process.stdout.decode("utf-8")
    except FileNotFoundError as e:
        raise PlinkError(*e.args)


def _validate_plink_version(binary: str, version: str) -> bool:
    """Return `True` iff plink binary matches specified major version."""
    version_string = _get_plink_version(binary)
    return version in version_string


def _get_valid_plink1_9_binary() -> str:
    """Get the full path to plink 1.9 binary."""
    plink1_9 = shutil.which("plink")
    if plink1_9 is None:
        raise PlinkError("`plink` (1.9) is not on the path.")
    if not _validate_plink_version(plink1_9, "1.9"):
        warnings.warn(
            "plink 1.X is installed, but not version 1.9. "
            "Some functionality may be missing."
        )
    return plink1_9


def _get_valid_plink2_binary() -> str:
    plink2 = shutil.which("plink2")
    if plink2 is None:
        raise PlinkError("`plink2` is not on the path.")
    if not _validate_plink_version(plink2, "2.0"):
        raise PlinkError(
            "`plink2` does not reference Plink 2.0. Check your plink installation."
        )
    return plink2
