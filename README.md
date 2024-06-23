# maskilayer

## Python tool to composite two images using multiple mask images

Maskilayer is a simple image compositing tool that allows you to blend two images using multiple mask images. It provides a flexible and efficient way to create complex image compositions using numpy and PIL.

## Features

- Composite two images using one or more mask images
- Support for both positive and negative masks
- Mask normalization with adjustable levels
- Asynchronous image writing for improved performance
- Command-line interface for easy use

## Installation

You can install maskilayer using pip:

```
pip install maskilayer
```

## Usage

### CLI usage

You can use maskilayer from the command line:

```bash
maskilayer --back background.png --comp overlay.png --out output.png --masks mask1.png;mask2.png --imasks inverted_mask.png --norm 2 --verbose
```

CLI docs

```text
maskilayer
INFO: Showing help with the command 'maskilayer -- --help'.

NAME
    maskilayer - Composite two images using mask(s).

SYNOPSIS
    maskilayer <flags>

DESCRIPTION
    Composite two images using mask(s).

FLAGS
    -b, --back=BACK
        Type: str
        Default: ''
        layer 0 (background image path)
    -c, --comp=COMP
        Type: str
        Default: ''
        layer 1 (overlay image path that will be composited via masks)
    -o, --out=OUT
        Type: str
        Default: ''
        output composite image
    -s, --smask=SMASK
        Type: str
        Default: ''
        path to save the final mask (optional)
    -m, --masks=MASKS
        Type: Optional
        Default: None
        ;-separated mask image paths (optional)
    -i, --imasks=IMASKS
        Type: Optional
        Default: None
        ;-separated negative mask image paths (optional)
    -n, --norm=NORM
        Type: int
        Default: 0
        perform mask normalization with level 0-4
    -v, --verbose=VERBOSE
        Type: bool
        Default: False
        print additional output
    -f, --fast=FAST
        Type: bool
        Default: False
        save fast but larger files
```

### Code usage

Or import it in your Python code:

```python
from pathlib import Path
from maskilayer import comp_images

comp_images(
    background=Path("background.png"),
    overlay=Path("overlay.png"),
    output=Path("output.png"),
    masks=[Path("mask1.png"), Path("mask2.png")],
    invert_masks=[Path("inverted_mask.png")],
    normalize_level=2,
    verbose=True
)
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE.txt) file for details.