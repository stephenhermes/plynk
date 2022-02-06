from __future__ import annotations
import os
from pathlib import Path
import subprocess
from typing import Any

from .errors import PlinkError
from .inspect import InspectionView
from .utils import _get_valid_plink2_binary, _get_valid_plink1_9_binary


class Plink:

    PLINK1: str | None = _get_valid_plink1_9_binary()
    PLINK2: str = _get_valid_plink2_binary()

    def __init__(self, workdir: Path | str | None):
        """Entrypoint to plink.

        Parameters
        ----------
        workdir : Pathlike or None
            The directory in which plink should run. If None, then will
            use the current working directory.

        """
        if workdir:
            workdir = Path(workdir)
            if not workdir.exists():
                raise ValueError(f"No such directory: {workdir}")
        self.workdir = workdir
        self._workdir = self.workdir if self.workdir else Path(os.getcwd())

    def __repr__(self) -> str:
        workdir = self.workdir.as_posix() if self.workdir else None  # type: ignore
        return f"{self.__class__.__name__}(wordir={workdir})"

    def run(
        self,
        bfile: str | Path | None = None,
        out: str | Path | None = None,
        _version: str = "2",
        **kwargs: Any,
    ) -> InspectionView:
        """Runs a plink command with the parameters passed."""

        plink = self.PLINK1 if _version != "2" else self.PLINK2
        if plink is None:
            raise ValueError("Cannot use plink v{_version} if not installed.")

        cmd = [plink]
        params = kwargs.copy()

        # Set bfile:
        if bfile:
            bfile = Path(bfile)
            cmd += ["--bfile", bfile.as_posix()]
            params["bfile"] = bfile
        # Set output
        if out and self.workdir:
            out = (self._workdir / out).as_posix()  # type: ignore
            cmd += ["--out", out]
            params["out"] = out

        for key, val in kwargs.items():
            key = key.replace("_", "-")
            # Set boolean flags
            if isinstance(val, bool) and val:
                cmd += [f"--{key}"]
            # Keywords with multiple parameters
            elif isinstance(val, (tuple, list)):
                cmd += [f"--{key}"] + [str(x) for x in val]
            # Keywords with single parameters
            else:
                cmd += [f"--{key}", str(val)]

        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode != 0:
            raise PlinkError(process.stderr.decode("utf-8"))

        return InspectionView(process.stdout, params)
