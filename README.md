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

You can use maskilayer from the command line:

```
python -m maskilayer --back background.png --comp overlay.png --out output.png --masks mask1.png;mask2.png --imasks inverted_mask.png --norm 2 --verbose
```

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