# Maskilayer Streamlining TODO for v1.0 (MVP)

## Phase 1: Code Refinements and Bug Fixes

-   [x] **Streamline `src/maskilayer/maskilayer.py`**
    -   [x] Consolidate Image Loading Functions (`arr_from_layer`, `arr_from_mask`)
    -   [x] Enhance `normalize_mask_arr` Robustness (prevent division by zero)
-   [x] **Address Issues in `src/maskilayer/__main__.py`**
    -   [x] Fix `smask` Argument Handling (prevent `Path(None)`)

## Phase 2: Documentation and Configuration Adjustments

-   [x] **Simplify `CONTRIBUTING.md`**
-   [x] **Adjust CI Workflow (`.github/workflows/ci.yml`)**
    -   [x] Update CI to correctly install test dependencies (including `tox`)
    -   [x] Update CI to correctly execute tests (using `tox`)

## Phase 3: Record Keeping and Finalization

-   [ ] **Maintain `CHANGELOG.md`** (ongoing throughout the process)
-   [ ] **Update `TODO.md`** (ongoing, this file)

## Phase 4: Submission

-   [ ] **Final Review and Commit**
