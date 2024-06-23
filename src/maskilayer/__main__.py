#!/usr/bin/env python3

from pathlib import Path

import fire
from rich.console import Console

from .maskilayer import comp_images, normalize_paths


def cli(
    back: str = "",
    comp: str = "",
    out: str = "",
    smask: str = "",
    masks: str | None = None,
    imasks: str | None = None,
    norm: int = 0,
    verbose: bool = False,
    fast: bool = False,
) -> None:
    comp_images(
        background=Path(back),
        overlay=Path(comp),
        output=Path(out),
        masks=normalize_paths(masks),
        invert_masks=normalize_paths(imasks),
        save_mask=Path(smask),
        normalize_level=int(norm),
        verbose=verbose,
        fast=fast,
    )


if __name__ == "__main__":
    console = Console(highlight=False, markup=True)
    fire.core.Display = lambda lines, out: console.print(*lines)
    fire.Fire(cli)
