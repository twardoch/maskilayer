# Changelog

## Version 0.2.0 (Upcoming)

### Streamlining and Fixes
- **Core Logic (`maskilayer.py`):**
  - Consolidated image and mask loading functions (`arr_from_layer`, `arr_from_mask`) into a unified helper `_load_image_to_array` to reduce redundancy.
  - Improved robustness of `normalize_mask_arr` by handling potential division-by-zero errors when processing flat or near-flat masks, ensuring more stable behavior with varied mask inputs.
- **CLI (`__main__.py`):**
  - Fixed a bug in `smask` (save mask path) argument handling where providing no path could lead to an error. Ensured that `None` is passed correctly to the core function if the path is empty.
- **Documentation:**
  - Simplified `CONTRIBUTING.md` to better suit the MVP stage of the project.
- **CI/CD:**
  - Updated GitHub Actions workflow to install `tox` and use it for running tests, ensuring the test environment defined in `tox.ini` is utilized.
- Preparing for MVP v1.0 by streamlining code and addressing minor issues.
  (Further details will be added as tasks are completed)

## Version 0.1.0 (2024-06-24)

- Initial release
- Implemented basic image compositing functionality
- Added support for multiple masks and inverted masks
- Implemented mask normalization with adjustable levels
- Added asynchronous image writing
- Created command-line interface