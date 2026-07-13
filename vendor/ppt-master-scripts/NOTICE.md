# Third-party component notice — ppt-master (SVG → PPTX engine)

The `ppt-master-scripts/` directory bundles the SVG→PPTX conversion engine from the
**ppt-master** skill, used by PPT Pro Studio's optional Premium path ⑥-B
(`ppt_master_hifi.py`).

- **Component**: ppt-master (SVG authoring → native editable .pptx)
- **Upstream**: hugohe3/ppt-master (MIT, ~16.6k★)
- **Bundled version**: **v3.1.0** (upgraded 2026-07-14 from the previous bundled build)
- **License**: MIT
- **Bundled scope**: the engine under `skills/ppt-master/scripts/` of upstream v3.1.0
  (`svg_to_pptx.py`, `svg_to_pptx/`, `pptx_shapes/`, `pptx_to_svg/`,
  `pptx_animations.py`, `pptx_transitions.py`, `console_encoding.py`,
  `resource_paths.py`, and supporting modules), flattened so the wrapper can
  locate it offline.

## Notes on the v3.1.0 upgrade
- Upstream v3.1.0 restructured into a multi-agent `skills/` layout; the offline
  engine was re-flattened into this directory.
- `pptx_transitions.py` is **carried forward from the prior bundled build**:
  upstream v3.1.0 no longer ships it at this path, but PPT Pro Studio's own
  `add_transitions.py` (in `scripts/`) depends on it to inject random page-flip
  transitions. It is MIT-compatible and retained intentionally.

This bundled copy is provided under the terms of the MIT License. PPT Pro Studio's
own code remains MIT-0 (see `../../LICENSE`). No code was modified from the upstream
engine beyond the directory flattening so the wrapper can locate it offline.

If you prefer to use a system-installed ppt-master instead of this bundled copy,
set `PPT_MASTER_DIR` or pass `--ppt-master <dir>` to `ppt_master_hifi.py`.
