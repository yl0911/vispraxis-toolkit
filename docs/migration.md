# Migration from `D:\yl\localcode`

Apply the [source disposition rules](source-disposition.md) before this process.
The goal is not to preserve every old file in the new repository; it is to
identify the smaller set of capabilities that VisPraxis still needs.

## Current observations

The source tree mixes functional categories with historical project folders.
It also contains copied SDK code, notebooks, a small web application, test
scripts, generated cache files, exact duplicates, and different scripts that
share a filename.

The first inventory found 173 code or notebook files: 168 Python files, two Go
files, two notebooks, and one JavaScript file. A conservative name/path scan
identified 21 test-like files; this is only a preservation filter, not a claim
that the remaining files are production-ready.

Confirmed exact duplicate groups include:

| Canonical candidate | Duplicate locations |
| --- | --- |
| `statistics_yolo_label.py` | `bty`, `imgdeal` |
| `select_cats_img_xml.py` | `bty`, `imgdeal` |
| `xml_getlabel_to_new.py` | `bty`, `ws` |
| `json_to_xml.py` | `bty`, `imgdeal` |
| `ocr_puttext.py` | `bty`, `ws` |
| `COCOtoVOC.py` | `baiduapi/baidu_coco_voc`, `imgdeal` |

This table records duplication discovered in the source tree; it does not make
every listed path a migration candidate. In particular, `baiduapi` remains
excluded, so the `imgdeal` copy is the only possible source in that pair.

Empty files with the same hash are not useful duplicates and should not be
migrated as capabilities. Notebook checkpoints and `__pycache__` are generated
artifacts and are excluded.

The same filename does not imply the same implementation. In particular,
`rename.py`, `test.py`, `test_simple.py`, `voc_to_yolo.py`, `xmlTool.py`, and
`z_geticon_v3_shein.py` require semantic comparison before consolidation.

## Migration states

Every in-scope source file receives exactly one migration state. Files already
marked `exclude-unused` or `exclude-generated` by the source disposition are
not carried into capability classification.

| State | Meaning |
| --- | --- |
| `canonical` | Selected implementation to refactor into a capability |
| `duplicate` | Byte-identical to a selected canonical source |
| `merge` | Overlapping implementation whose useful behavior must be combined |
| `legacy` | Preserved but not safe or general enough to publish |
| `defer-test` | Old test or experiment left unchanged until its business use is confirmed |
| `vendor` | Third-party code, preferably replaced by a declared dependency |
| `exclude-generated` | Cache, checkpoint, output, or other generated artifact |

No source file is deleted during migration. Selected scripts record their old
paths in the module description; hashes may be kept in a migration inventory
when duplicate provenance needs to be proven.

## Recommended migration order

1. Inventory paths, hashes, dependencies, entry points, hard-coded paths,
   credentials, network access, and source mutation behavior.
2. Exclude retired source trees and generated/local-only files.
3. Defer unclear tests and experiments. Move confirmed business calls into the
   matching `tests/<domain>/` directory and keep their real parameters there.
4. Identify copied dependencies and other vendor source.
5. Choose a canonical implementation for each exact or semantic duplicate set.
6. Move low-risk, self-contained capabilities first: document conversion,
   visual conversion, statistics, and dataset selection.
7. Refactor service automation only after credential and configuration
   injection is defined.
8. Migrate destructive file operations after dry-run, output isolation, and
   cancellation behavior are available.
9. Expose only reviewed scripts to VisPraxis; do not migrate uncertain scripts
   merely to complete the old directory inventory.

## Duplicate policy

- Byte-identical copies become one canonical capability with multiple
  `legacy_sources` entries.
- Similar scripts are not silently overwritten. Compare public functions,
  CLI behavior, defaults, side effects, and supported formats first.
- Date-suffixed scripts are treated as versions until a diff proves otherwise.
- Provider SDK files are not merged with Toolkit logic.
- A deprecated alias may be provided at the command layer, but duplicate source
  modules are not retained in the functional package.

## First migration batch

Start with scripts that already have a clear command boundary and limited
external state:

- `move_matching_images_to_cut.py` -> `datasets`;
- `split_log_data_images.py` -> `datasets` after separating reusable decoding
  from its historical log convention;
- `svg2img.py` and `svg_to_img.go` -> candidate implementations of one
  `documents` conversion capability until parity is established;
- `merge_frames_targets.py` -> `vision`;
- annotation document converters -> `documents`, beginning with confirmed
  duplicates.

Defer database deletion, cloud cleanup, crawler, service benchmark, and scripts
with embedded endpoint or credential assumptions until their side effects are
explicitly modeled.

Do not select candidates from the excluded `asr/`, `backend/`, or `baiduapi/`
trees, even when a file appears to fit a functional domain.
