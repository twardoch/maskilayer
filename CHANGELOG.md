# Changelog

## Version 1.0.6 (2025-06-25)

- Minor code formatting improvements
- Updated import statements for better compatibility
- Enhanced code documentation

## Version 1.0.5 (2025-06-25)

- Bug fixes and stability improvements

## Version 1.0.4 (2025-06-25)

- Performance optimizations

## Version 1.0.3 (2025-06-25)

- Updated dependencies

## Version 1.0.2 (2025-06-25)

- Minor bug fixes

## Version 1.0.1 (2025-06-25)

- Documentation improvements
- Fixed packaging issues

## Version 1.0.0 (2025-06-25)

### Major Release - MVP v1.0

- **Core Logic (`maskilayer.py`):**
  - Consolidated image and mask loading functions (`arr_from_layer`, `arr_from_mask`) to reduce redundancy
  - Improved robustness of `normalize_mask_arr` by handling potential division-by-zero errors when processing flat or near-flat masks
  - Enhanced error handling throughout the compositing pipeline
  
- **CLI (`__main__.py`):**
  - Fixed a bug in `smask` (save mask path) argument handling where providing no path could lead to an error
  - Improved argument validation and user feedback
  
- **Documentation:**
  - Simplified `CONTRIBUTING.md` to better suit the MVP stage of the project
  - Updated README with clearer examples and use cases
  
- **CI/CD:**
  - Added GitHub Actions workflow for automated testing
  - Updated workflow to install `tox` and use it for running tests
  - Added support for Python 3.11 and 3.12

- **General Improvements:**
  - Streamlined codebase for better maintainability
  - Enhanced logging with rich formatting
  - Improved async image writing performance
  - Better cross-platform compatibility

## Version 0.1.0 (2024-06-24)

- Initial release
- Implemented basic image compositing functionality
- Added support for multiple masks and inverted masks
- Implemented mask normalization with adjustable levels
- Added asynchronous image writing
- Created command-line interface