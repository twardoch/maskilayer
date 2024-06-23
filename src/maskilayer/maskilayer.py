#!/usr/bin/env python3
"""
Image compositing tool using numpy and PIL.
"""

import asyncio
import io
import logging
from pathlib import Path
from typing import Sequence

import aiofiles
import numpy as np
from PIL import Image
from rich.logging import RichHandler

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool) -> None:
    """Configure logging using rich."""
    level = logging.INFO if verbose else logging.WARN
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


def log(msg: str, indent: int = 0):
    if indent == 0:
        msg = f"[green]{msg}[/]"
    else:
        msg = f"""{" " * indent * 2}{msg}"""
    logger.info(msg, extra={"markup": True})


def arr_from_layer(path: Path, idx: int = 0) -> np.ndarray:
    """Load an image from path into a numpy array."""
    log(f"Opening layer {idx}: [blue]{path}[/]", 1)
    return np.array(Image.open(path))


def arr_from_mask(path: Path, idx: int = 0) -> np.ndarray:
    """Load a mask image into a float numpy array."""
    log(f"Opening mask {idx}:  [blue]{path}[/]", 1)
    return np.array(Image.open(path).convert("L")).astype(float) / 255.0


def normalize_mask_arr(mask: np.ndarray, level: float, idx: int = 0) -> np.ndarray:
    """
    Normalize a mask array.

    Args:
        mask (np.ndarray): The input mask array.
        level (float): Normalization level between 0 and 3.

    Returns:
        np.ndarray: The normalized mask array.
    """
    if level <= 0:
        return mask

    log(f"Normalizing mask {idx} level [blue]{level}[/]", 1)

    # Normalize min to 0, max to 1
    mask_min, mask_max = mask.min(), mask.max()
    log(f"Mask {idx} found range: [blue]{mask_min:.2f} - {mask_max:.2f}[/]", 2)

    mask = (mask - mask_min) / (mask_max - mask_min)

    if level == 1:
        return mask

    # Truncate by luminance cutoff
    cutoff = 0.5 - 0.25 * np.exp(-(level - 2) * 0.5)
    log(f"Mask {idx} luminance: [blue]{cutoff:.2f}[/]", 2)

    mask = np.clip(mask, cutoff, 1 - cutoff)
    mask = (mask - cutoff) / (1 - 2 * cutoff)

    # Apply gamma correction
    gamma = 1.0 - 0.75 * (1 - np.exp(-(level - 1) * 2.0))
    log(f"Mask {idx} gamma: [blue]{gamma:.2f}[/]", 2)

    mask = np.power(mask, gamma)

    # Normalize again
    mask_min, mask_max = mask.min(), mask.max()
    log(f"Mask {idx} final range: [blue]{mask_min:.2f} - {mask_max:.2f}[/]", 2)

    mask = (mask - mask_min) / (mask_max - mask_min)

    return mask


def composite_arrs(
    background: np.ndarray,
    overlay: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    """
    Composite an overlay image onto a background using a mask.

    Args:
        background (np.ndarray): The background image array.
        overlay (np.ndarray): The overlay image array.
        mask (np.ndarray): The compositing mask array.

    Returns:
        np.ndarray: The composite image array.
    """
    log("Compositing layers")
    return background * (1 - mask[..., np.newaxis]) + overlay * mask[..., np.newaxis]


def blend_mask_arrs(masks: Sequence[np.ndarray]) -> np.ndarray:
    """
    Blend multiple mask arrays by averaging.

    Args:
        masks (Sequence[np.ndarray]): The input mask arrays.

    Returns:
        np.ndarray: The blended mask array.
    """
    log(f"Blending {len(masks)} masks")
    return np.mean(masks, axis=0)


async def write_image(image: Image.Image, path: Path, fast: bool = False) -> None:
    """
    Write an image to a file asynchronously.

    Args:
        image (Image.Image): The image to write.
        path (Path): The output file path.
        fast (bool): Whether to optimize for speed vs size. Defaults to False.
    """
    log(f"Saving image: [blue]{path}[/]", 1)
    output = io.BytesIO()

    if fast:
        image.save(output, format="PNG", optimize=False, compress_level=0)
    else:
        image.save(output, format="PNG", optimize=True)

    output.seek(0)
    async with aiofiles.open(path, "wb") as f:
        await f.write(output.getvalue())


async def write_images(images: Sequence[tuple[Image.Image, Path, bool]]) -> None:
    """
    Write multiple images concurrently.

    Args:
        images (Sequence[tuple[Image.Image, Path, bool]]): Images to write.
    """
    await asyncio.gather(*[write_image(img, path, fast) for img, path, fast in images])


def normalize_paths(
    paths: str | Path | Sequence[str | Path] | None = None,
) -> Sequence[Path]:
    if not paths:
        return []

    if isinstance(paths, str):
        if ";" in paths:
            paths = [Path(p) for p in paths.split(";")]
        elif "," in paths:
            paths = [Path(p) for p in paths.split(",")]
        else:
            paths = [Path(paths)]
    elif isinstance(paths, Path):
        paths = [paths]

    return [p for p in paths if Path(p).is_file()]


def check_arrs_dim(arrays: Sequence[np.ndarray]) -> None:
    """
    Check that all arrays have the same dimensions.

    Args:
        arrays (Sequence[np.ndarray]): Input arrays.

    Raises:
        ValueError: If the array dimensions don't match.
    """
    if not arrays:
        return

    reference = arrays[0].shape[:2]

    for array in arrays[1:]:
        if array.shape[:2] != reference:
            raise ValueError(
                f"Input array dimensions must match, got {array.shape[:2]} and {reference}"
            )


def comp_images(
    background: Path | None = None,
    overlay: Path | None = None,
    output: Path | None = None,
    masks: Sequence[Path] = [],
    invert_masks: Sequence[Path] = [],
    save_mask: Path | None = None,
    normalize_level: int = 0,
    verbose: bool = False,
    fast: bool = False,
) -> None:
    setup_logging(verbose)
    log("Opening layers")
    background_arr = arr_from_layer(Path(background), 0)
    overlay_arr = arr_from_layer(Path(overlay), 1)

    log("Opening positive masks")
    mask_paths = normalize_paths(masks)
    mask_arrs = [arr_from_mask(p, pi) for pi, p in enumerate(mask_paths)]

    log("Opening negative masks")
    invert_mask_paths = normalize_paths(invert_masks)
    invert_mask_arrs = [
        1 - arr_from_mask(p, pi + len(mask_arrs))
        for pi, p in enumerate(invert_mask_paths)
    ]
    mask_arrs.extend(invert_mask_arrs)

    check_arrs_dim([background_arr, overlay_arr] + mask_arrs)

    if not mask_arrs:
        log("Will composite at 50%")
        mask_arr = np.full(background_arr.shape[:2], 0.5)
    else:
        log("Normalizing masks")
        mask_arrs = [
            normalize_mask_arr(m, normalize_level, mi) for mi, m in enumerate(mask_arrs)
        ]
        mask_arr = blend_mask_arrs(mask_arrs)

    composite = composite_arrs(background_arr, overlay_arr, mask_arr)

    writes = []

    if save_mask:
        mask_img = Image.fromarray((mask_arr * 255).astype(np.uint8))
        writes.append((mask_img, Path(save_mask), fast))

    composite_img = Image.fromarray(composite.astype(np.uint8))
    writes.append((composite_img, Path(output), fast))

    log("Saving outputs")
    asyncio.run(write_images(writes))
    log("Finished")
