# Third-party component notice — ppt-master (SVG → PPTX engine)

The `ppt-master-scripts/` directory bundles the SVG→PPTX conversion engine from the
**ppt-master** skill, used by PPT Pro Studio's optional Premium path ⑥-B
(`ppt_master_hifi.py`).

- **Component**: ppt-master (SVG authoring → native editable .pptx)
- **License**: MIT
- **Bundled scope**: the `scripts/` engine only (`svg_to_pptx.py`, `svg_to_pptx/`,
  `pptx_shapes/`, `pptx_to_svg/`, `pptx_animations.py`, `pptx_transitions.py`,
  `console_encoding.py`, `resource_paths.py`, and supporting modules).

This bundled copy is provided under the terms of the MIT License. PPT Pro Studio's
own code remains MIT-0 (see `../../LICENSE`). No code was modified from the upstream
engine; only the directory layout was flattened so the wrapper can locate it offline.

If you prefer to use a system-installed ppt-master instead of this bundled copy,
set `PPT_MASTER_DIR` or pass `--ppt-master <dir>` to `ppt_master_hifi.py`.
