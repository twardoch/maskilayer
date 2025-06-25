#!/usr/bin/env python3
"""
Image compositing tool using numpy and PIL.
"""

import asyncio
import io
import logging
from collections.abc import Sequence
from pathlib import Path

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


def _load_image_to_array(
    path: Path, is_mask: bool, description: str, idx: int = 0
) -> np.ndarray:
    """Load an image or mask from path into a numpy array."""
    log(f"Opening {description} {idx}: [blue]{path}[/]", 1)
    image = Image.open(path)
    if is_mask:
        return np.array(image.convert("L")).astype(float) / 255.0
    return np.array(image)


def arr_from_layer(path: Path, idx: int = 0) -> np.ndarray:
    """Load an image from path into a numpy array."""
    return _load_image_to_array(path, is_mask=False, description="layer", idx=idx)


def arr_from_mask(path: Path, idx: int = 0) -> np.ndarray:
    """Load a mask image into a float numpy array."""
    return _load_image_to_array(path, is_mask=True, description="mask", idx=idx)


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

    mask_min_orig, mask_max_orig = mask.min(), mask.max()
    log(f"Mask {idx} original range: [blue]{mask_min_orig:.2f} - {mask_max_orig:.2f}[/]", 2)

    # Initial normalization to 0-1 range
    if (mask_max_orig - mask_min_orig) > np.finfo(float).eps:
        mask = (mask - mask_min_orig) / (mask_max_orig - mask_min_orig)
    else:
        # If flat, (mask - mask_min_orig) results in all zeros.
        # This is a safe state for a flat mask after this conceptual step.
        mask = np.zeros_like(mask)

    if level == 1:
        return mask

    # Truncate by luminance cutoff
    # Cutoff approaches 0.5 from below as level increases.
    # For level=2, cutoff = 0.5 - 0.25*exp(0) = 0.25
    # For level=3, cutoff = 0.5 - 0.25*exp(-0.5) approx 0.5 - 0.25*0.606 = 0.348
    # For level=inf, cutoff approaches 0.5
    cutoff = 0.5 - 0.25 * np.exp(-(level - 2.0) * 0.5)
    log(f"Mask {idx} luminance cutoff: [blue]{cutoff:.2f}[/]", 2)

    mask = np.clip(mask, cutoff, 1.0 - cutoff)

    # Re-scale after clip: [cutoff, 1-cutoff] -> [0,1]
    denominator_cutoff = 1.0 - 2.0 * cutoff
    if abs(denominator_cutoff) > np.finfo(float).eps:
        mask = (mask - cutoff) / denominator_cutoff
    else:
        # This implies cutoff is 0.5 (or very close).
        # The mask was clipped to [0.5, 0.5], so it's flat at 0.5.
        # (mask - 0.5) would be all zeros. Division by zero.
        # So, the mask is effectively flat at 0.5 after clipping.
        mask.fill(0.5)

    # Apply gamma correction
    # Gamma approaches 0.25 from above as level increases (for level >=1)
    # For level=1, gamma = 1.0 - 0.75*(1-exp(0)) = 1.0
    # For level=2, gamma = 1.0 - 0.75*(1-exp(-2)) approx 1.0 - 0.75*(1-0.135) = 1.0 - 0.75*0.865 = 0.351
    # For level=inf, gamma approaches 0.25
    gamma = 1.0 - 0.75 * (1.0 - np.exp(-(level - 1.0) * 2.0))
    log(f"Mask {idx} gamma: [blue]{gamma:.2f}[/]", 2)
    mask = np.power(mask, gamma)

    # Final normalization to 0-1 range
    mask_min_final, mask_max_final = mask.min(), mask.max()
    log(f"Mask {idx} final range before re-stretch: [blue]{mask_min_final:.2f} - {mask_max_final:.2f}[/]", 2)

    if (mask_max_final - mask_min_final) > np.finfo(float).eps:
        mask = (mask - mask_min_final) / (mask_max_final - mask_min_final)
    else:
        # If flat at this stage, (mask - mask_min_final) makes it all zeros.
        # This is a consistent state for a flat mask.
        # Example: if mask became all 0.5, then min_final=0.5, (mask-0.5)=0.
        # If the goal is to preserve the flat value (e.g. 0.5), then use mask.fill(mask_min_final)
        # However, making it 0 is consistent with (X-min)/(max-min) when max-min=0 and X=min.
        # Let's choose to preserve the value if it's flat here.
        mask.fill(mask_min_final)


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

    path.parent.mkdir(parents=True, exist_ok=True)

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
