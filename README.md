# maskilayer

`maskilayer` is a Python tool for compositing two images using one or more mask images. 

- Composite two images (background + overlay) using one or more mask images
- Supply positive masks (overlay is preferred in bright areas of the mask) or negative masks (overlay is preferred in dark mask areas)
- Normalize masks with adjustable levels (0-5)

## 1. Installation

Install `maskilayer` using pip:

```bash
pip install --upgrade maskilayer
```

or the development version in a specific Python:

```bash
python3.11 -m pip install --upgrade git+https://github.com/twardoch/maskilayer
```

## 2. Rationale

### 2.1. Selective image sharpening

Combine a sharpened image with its original version using a segmentation mask:

1. Process an original image with an automatic sharpening method.
2. Use a segmentation model to generate a segmentation mask that isolates a specific subject.
3. Use `maskilayer` to composite:
   - background: original image
   - overlay: sharpened version
   - mask: segmentation mask

`maskilayer` will save a result, which will be a composite image where only the subject is sharpened, while the rest remains as in the original.

### 2.2. Creative upscaling with depth based compositing

Blend two differently upscaled versions of an image using a depth mask:

1. Upscale an image using a conservative upscaler like [Codeformer](https://replicate.com/sczhou/codeformer) to get predictable details for the background areas of the image. Supply the conservative upscale as background to `maskilayer`. 
2. Upscale the same image using a creative upscaler like [Ultimate SD Upscale](https://replicate.com/fewjative/ultimate-sd-upscale) to get additional details for foreground (subject) areas of the image. Supply the creative upscale as overlay (compositing image) to `maskilayer`.
3. Generate a depth mask using [Depth Anything](https://replicate.com/cjwbw/depth-anything) or [Midas](https://replicate.com/cjwbw/midas) (where the far areas are dark, and the close areas are bright). Supply the result as the (positive) mask to `maskilayer`. Or use a model like [Marigold](https://replicate.com/adirik/marigold) (where the close subjects are dark), and supply the resulting mask as inverted (negative) mask. 
4. Use `maskilayer` to composite:
   - background: conservative upscale
   - overlay: creative upscale
   - mask: depth mask (inverted mask if close areas are dark)

`maskilayer` will save a result, which will be a composite image with creative details for close subjects, and more conservative rendering for distant areas.

## 3. Usage

### 3.1. Command Line Interface

```bash
maskilayer --back background.png --comp overlay.png --out output.png --masks mask1.png;mask2.png --imasks inverted_mask.png --norm 2 --verbose
```

#### 3.1.1. CLI documentation

```text
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
        perform mask normalization with level 0-5
    -v, --verbose=VERBOSE
        Type: bool
        Default: False
        print additional output
    -f, --fast=FAST
        Type: bool
        Default: False
        save fast but larger files
```

### 3.2. Python API

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

## 4. Mask handling

- If you supply multiple masks, `maskilayer` averages them for the final composition.
- If you supply a mormalization level, `maskilayer` will adjust the mask contrast:
  - Level 0 uses masks as-is
  - Level 1 stretches grayscale range to full black-white spectrum
  - Levels 2-5 progressively increase contrast for more abrupt transitions between bright and dark

## 5. License

- Idea & Copyright (c) 2024 Adam Twardoch
- [Python code](https://github.com/twardoch/maskilayer) written with assistance from OpenAI GPT-4o and Anthropic Claude 3
- Licensed under the [Apache License 2.0](./LICENSE.txt)
