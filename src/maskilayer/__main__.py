#!/usr/bin/env python3

from pathlib import Path

import fire
from rich.console import Console

from .maskilayer import comp_images, normalize_paths


def cli_help():
    fire.Fire(main, command=["--help"])


def main(
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
    """
    Composite two images using mask(s).

    Args:
        back: layer 0 (background image path)
        comp: layer 1 (overlay image path that will be composited via masks)
        out: output composite image
        smask: path to save the final mask (optional)
        masks: ;-separated mask image paths (optional)
        imasks: ;-separated negative mask image paths (optional)
        norm: perform mask normalization with level 0-5
        verbose: print additional output
        fast: save fast but larger files
    """
    if back:
        back = Path(back)
    else:
        cli_help()
    if comp:
        comp = Path(comp)
    else:
        cli_help()
    if out:
        out = Path(out)
    else:
        cli_help()

    # smask is the string argument from CLI (default "")
    save_mask_for_comp_images: Path | None = None
    if smask:  # True if smask is not an empty string
        save_mask_for_comp_images = Path(smask)

    comp_images(
        background=back,
        overlay=comp,
        output=out,
        masks=normalize_paths(masks),
        invert_masks=normalize_paths(imasks),
        save_mask=save_mask_for_comp_images, # Pass the Path object or None
        normalize_level=int(norm),
        verbose=verbose,
        fast=fast,
    )


def cli():
    console = Console(highlight=False, markup=True)
    fire.core.Display = lambda lines, out: console.print(*lines)
    fire.Fire(main)


if __name__ == "__main__":
    cli()
