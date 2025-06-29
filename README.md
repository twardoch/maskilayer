# Maskilayer: Advanced Image Compositing

[![PyPI version](https://img.shields.io/pypi/v/maskilayer.svg)](https://pypi.org/project/maskilayer/)
[![Python Version](https://img.shields.io/pypi/pyversions/maskilayer.svg)](https://pypi.org/project/maskilayer/)
[![License](https://img.shields.io/pypi/l/maskilayer.svg)](https://github.com/twardoch/maskilayer/blob/main/LICENSE.txt)
<!-- Add other badges like build status, coverage etc. if available -->

`maskilayer` is a powerful Python-based command-line tool and library for compositing two images using one or more masks. It offers fine-grained control over the blending process, including advanced mask normalization techniques.

## Table of Contents

- [Overview](#overview)
  - [What is Maskilayer?](#what-is-maskilayer)
  - [Who is it for?](#who-is-it-for)
  - [Why is it useful?](#why-is-it-useful)
  - [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Interface (CLI)](#command-line-interface-cli)
  - [Programmatic Usage (Python Library)](#programmatic-usage-python-library)
- [Technical Details](#technical-details)
  - [Core Image Processing Workflow](#core-image-processing-workflow)
  - [Mask Normalization In-Depth](#mask-normalization-in-depth)
  - [Underlying Libraries](#underlying-libraries)
- [Contributing](#contributing)
- [License](#license)
- [Authors](#authors)
- [Changelog](#changelog)

## Overview

### What is Maskilayer?

Maskilayer is a tool designed to perform alpha compositing, where a foreground image (overlay) is blended with a background image based on the transparency data from one or more mask images. It allows for complex image manipulations by precisely controlling how different parts of the overlay image are merged with the background.

### Who is it for?

*   **Photographers & Digital Artists:** For creating composite images, photomontages, or applying localized adjustments.
*   **Graphic Designers:** Useful for blending textures, graphics, or creating layered visual effects.
*   **Computer Vision Developers & Researchers:** For tasks involving image segmentation, object insertion, or data augmentation where precise blending is required.
*   **Anyone needing to combine images with mask-based control.**

### Why is it useful?

Standard image editing software can perform compositing, but Maskilayer offers:

*   **Batch Processing:** Easily scriptable for processing multiple images via the CLI.
*   **Advanced Mask Control:** Sophisticated mask normalization algorithms to enhance mask quality and achieve desired blending effects.
*   **Flexibility:** Combine multiple masks, invert masks, and save the final computed mask.
*   **Reproducibility:** Define complex compositing operations programmatically or via CLI for consistent results.
*   **Extensibility:** As a Python library, it can be integrated into larger image processing pipelines.

### Key Features

*   **Multi-Mask Blending:** Combine several masks (e.g., from different segmentation algorithms) into a single effective mask.
*   **Mask Inversion:** Use masks to define areas to *exclude* from the overlay.
*   **Advanced Mask Normalization:** A multi-level normalization process to improve mask contrast and definition.
*   **CLI and Library Access:** Use it as a standalone tool or import its functions into your Python scripts.
*   **Asynchronous Output:** Efficiently saves output images, especially useful for larger files.
*   **Verbose Logging:** Optional detailed output of processing steps using `rich` for clear console messages.

## Installation

You can install `maskilayer` using pip. It is recommended to install it in a virtual environment.

```bash
pip install maskilayer
```

This will also install its necessary dependencies:

*   `Pillow`: For image loading, manipulation, and saving.
*   `numpy`: For numerical operations on image arrays.
*   `python-fire`: For creating the command-line interface.
*   `rich`: For enhanced terminal output and logging.
*   `aiofiles`: For asynchronous file operations.

To install from source, clone the repository and install using pip:
```bash
git clone https://github.com/twardoch/maskilayer.git
cd maskilayer
pip install .
```

## Usage

Maskilayer can be used both as a command-line tool and as a Python library.

### Command-Line Interface (CLI)

The basic command structure is:

```bash
maskilayer --back <background_image> --comp <overlay_image> --out <output_image> [OPTIONS]
```

**Required Arguments:**

*   `--back STR`: Path to the background image (layer 0).
*   `--comp STR`: Path to the overlay image (layer 1) that will be composited.
*   `--out STR`: Path to save the resulting composite image.

**Optional Arguments:**

*   `--smask STR`: Path to save the final combined and normalized mask image (optional).
*   `--masks STR`: Semicolon-separated list of paths to mask images. These define the areas where the overlay is opaque.
*   `--imasks STR`: Semicolon-separated list of paths to inverted mask images. These define areas where the overlay is transparent.
*   `--norm INT`: Mask normalization level (0-5, default: 0).
    *   `0`: No normalization. Mask values are used as-is (after conversion to 0-1 float).
    *   `1`: Basic range normalization. Stretches mask values to the full 0-1 range.
    *   `2-5`: Advanced normalization. Higher levels apply increasingly strong contrast enhancement, including luminance cutoff and gamma correction, to create sharper, more defined masks. Level 5 is the strongest.
*   `--verbose BOOL`: Print additional detailed output during processing (default: `False`).
*   `--fast BOOL`: Save output PNG images faster but with larger file sizes (less compression) (default: `False`).

**Examples:**

1.  **Basic compositing with one mask:**
    ```bash
    maskilayer --back background.png --comp overlay.png --masks mask1.png --out result.png
    ```

2.  **Compositing with multiple masks, an inverted mask, and saving the final mask:**
    ```bash
    maskilayer --back bg.jpg --comp fg.png \
               --masks "mask_alpha.png;mask_detail.png" \
               --imasks "exclude_area.png" \
               --smask final_mask.png \
               --out final_composite.png
    ```

3.  **Using mask normalization (level 3) and verbose output:**
    ```bash
    maskilayer --back path/to/bg.tif --comp path/to/fg.tif \
               --masks path/to/primary_mask.png \
               --norm 3 \
               --verbose \
               --out output_image.png
    ```
    If no masks (`--masks` or `--imasks`) are provided, the tool will perform a 50% alpha blend of the overlay onto the background.

### Programmatic Usage (Python Library)

You can use the core compositing function `comp_images` directly in your Python scripts.

```python
from pathlib import Path
from maskilayer import comp_images

# Define paths to your images
background_path = Path("path/to/your/background.jpg")
overlay_path = Path("path/to/your/overlay.png")
output_path = Path("path/to/your/result.png")

# Define paths to masks (optional)
mask_paths = [Path("path/to/mask1.png"), Path("path/to/mask2.png")]
inverted_mask_paths = [Path("path/to/inverted_mask1.png")]

# Path to save the final mask (optional)
save_mask_path = Path("path/to/final_mask_output.png")

# Perform compositing
comp_images(
    background=background_path,
    overlay=overlay_path,
    output=output_path,
    masks=mask_paths,
    invert_masks=inverted_mask_paths,
    save_mask=save_mask_path,
    normalize_level=2,  # Example normalization level
    verbose=True,
    fast=False
)

print(f"Composite image saved to {output_path}")
if save_mask_path:
    print(f"Final mask saved to {save_mask_path}")
```

**`comp_images` Function Parameters:**

*   `background: Path | None`: Path to the background image.
*   `overlay: Path | None`: Path to the overlay image.
*   `output: Path | None`: Path for the output composite image.
*   `masks: Sequence[Path] = []`: A list or tuple of `Path` objects for positive masks.
*   `invert_masks: Sequence[Path] = []`: A list or tuple of `Path` objects for negative masks.
*   `save_mask: Path | None = None`: Path to save the final computed mask.
*   `normalize_level: int = 0`: Mask normalization level (0-5).
*   `verbose: bool = False`: Enable verbose logging.
*   `fast: bool = False`: Enable fast saving for PNGs.

**Important Note:** All input images (background, overlay, and all masks) must have the exact same dimensions (width and height). The tool will raise an error if dimensions mismatch.

## Technical Details

### Core Image Processing Workflow

1.  **Setup Logging:** If `verbose` is true, `rich` logging is configured for detailed output.
2.  **Load Images:**
    *   Background and overlay images are loaded using Pillow and converted to NumPy arrays. Color images are typically loaded as RGB (or RGBA, but alpha channel is not directly used from input layers).
    *   Mask images are loaded, converted to grayscale ("L" mode in Pillow), and then to NumPy float arrays with values scaled to the `0.0` to `1.0` range.
3.  **Process Masks:**
    *   **Positive Masks:** All masks provided via `masks` are loaded.
    *   **Negative Masks:** All masks provided via `invert_masks` are loaded and their values inverted (`1.0 - value`).
    *   **Combine Masks:** All positive and processed negative masks are collected.
    *   **Dimension Check:** Verifies that all loaded images (background, overlay, masks) have identical height and width.
4.  **Handle No-Mask Scenario:** If no masks are provided, a default mask is created where all pixels have a value of `0.5`, resulting in a 50% blend.
5.  **Normalize Masks (if `normalize_level > 0`):**
    *   Each individual mask array (after potential inversion) is processed by the `normalize_mask_arr` function if `normalize_level` is greater than 0. (See [Mask Normalization In-Depth](#mask-normalization-in-depth)).
6.  **Blend Masks:** If multiple masks were provided (and processed), they are blended into a single final mask array by taking the pixel-wise mean of all mask arrays.
7.  **Composite Images:** The final composite image is calculated using the formula:
    `Composite = Background * (1 - FinalMask) + Overlay * FinalMask`
    This operation is performed element-wise for each color channel. The `FinalMask` is expanded to have the same number of channels as the images for broadcasting.
8.  **Save Outputs:**
    *   The composite image is converted from a NumPy array back to a Pillow `Image` object (uint8 format) and saved to the specified `output` path.
    *   If `save_mask` path is provided, the final (potentially normalized and blended) mask array is converted to a Pillow `Image` (uint8 grayscale) and saved.
    *   Image saving is done asynchronously using `aiofiles` for better performance, especially with `fast=False` (which involves more CPU for compression).

### Mask Normalization In-Depth (`normalize_mask_arr`)

The `normalize_mask_arr` function enhances masks based on the `level` parameter:

*   **`level == 0`**: No normalization is applied. The mask (already scaled 0-1) is returned as is.
*   **`level == 1`**:
    1.  **Initial Range Stretch**: The mask's values are stretched to fill the entire `0.0` to `1.0` range. If the mask is flat (all pixels same value), it becomes all `0.0`.

*   **`level >= 2`**: Involves a more complex, multi-stage process:
    1.  **Initial Range Stretch**: Same as for `level == 1`.
    2.  **Luminance Cutoff**: A `cutoff` value is calculated. This `cutoff` approaches `0.5` from below as `level` increases.
        *   `cutoff = 0.5 - 0.25 * np.exp(-(level - 2.0) * 0.5)`
        *   The mask's values are then clipped to the range `[cutoff, 1.0 - cutoff]`. This effectively discards pixel values near the extremes, aiming to increase definition.
    3.  **Re-scale after Cutoff**: The values from the clipped range `[cutoff, 1.0 - cutoff]` are re-scaled to fill the `0.0` to `1.0` range.
    4.  **Gamma Correction**: A `gamma` value is calculated. This `gamma` value approaches `0.25` from above as `level` increases.
        *   `gamma = 1.0 - 0.75 * (1.0 - np.exp(-(level - 1.0) * 2.0))`
        *   The mask values are then raised to the power of `gamma` (`mask ** gamma`). This non-linear transformation further adjusts contrast. For `gamma < 1.0`, it tends to brighten mid-tones and increase contrast.
    5.  **Final Range Stretch**: The mask values are again stretched to ensure they span the full `0.0` to `1.0` range. This accounts for any shifts caused by the gamma correction.

The goal of levels 2 and above is to create a more binary-like mask from a gradient mask, making the transitions sharper. Higher levels apply these effects more aggressively. Robust handling for flat or near-flat masks is implemented at each stage to prevent division-by-zero errors.

### Underlying Libraries

*   **Pillow (PIL Fork):** Used for all image file I/O (reading and writing various formats) and basic image manipulations like mode conversion.
*   **NumPy:** The core of image data representation and manipulation. Images are converted to NumPy arrays for efficient pixel-wise calculations (normalization, blending, compositing).
*   **Python Fire:** Powers the command-line interface, automatically generating CLI arguments from function signatures in `src/maskilayer/__main__.py`.
*   **Rich:** Used for prettier and more informative logging output in the console when `--verbose` is enabled.
*   **aiofiles:** Enables asynchronous writing of output images, which can improve performance by not blocking the main thread during I/O operations.

## Contributing

Contributions are welcome! Please refer to `CONTRIBUTING.md` for initial guidelines. At a high level:

*   **Reporting Bugs:** Please open an issue on the [GitHub repository](https://github.com/twardoch/maskilayer/issues), providing as much detail as possible.
*   **Suggesting Enhancements:** Open an issue to discuss your ideas.
*   **Code Contributions:**
    1.  Fork the repository.
    2.  Create a new branch for your feature or bugfix.
    3.  Make your changes.
    4.  Ensure your code passes tests and linting.
    5.  Submit a pull request.

### Development Setup

1.  Clone the repository:
    ```bash
    git clone https://github.com/twardoch/maskilayer.git
    cd maskilayer
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  Install dependencies, including development tools:
    ```bash
    pip install -e ".[testing,dev]"
    ```
    (Note: Ensure `setup.cfg` or `pyproject.toml` defines these extras. Assuming `testing` for `pytest` and `dev` for linters/formatters if not covered by pre-commit.)

4.  Install pre-commit hooks:
    ```bash
    pre-commit install
    ```
    This will ensure that your code is formatted with `black` and `isort`, and linted with `flake8` before each commit.

### Running Tests

Tests are managed using `tox` and run with `pytest`.
To run all tests as defined in `tox.ini`:
```bash
tox
```
To run `pytest` directly (e.g., for a specific test file or with specific options):
```bash
pytest tests/
```

### Coding Style

*   Follow PEP 8 guidelines.
*   Code is formatted using `black`.
*   Imports are sorted using `isort`.
*   `flake8` is used for linting.
    These are enforced by pre-commit hooks.

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE.txt](LICENSE.txt) file for details.

## Authors

*   Adam Twardoch ([@twardoch](https://github.com/twardoch))

See also the list of [contributors](https://github.com/twardoch/maskilayer/graphs/contributors) who participated in this project. (This link will show GitHub contributors over time). For a static list, refer to `AUTHORS.md`.

## Changelog

For a history of changes and upcoming features, please see [CHANGELOG.md](CHANGELOG.md).
