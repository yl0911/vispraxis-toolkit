# Migration status

This list prevents the old repository from being copied wholesale. Update it
as each script is reviewed.

## Progress snapshot

Current source-file accounting after excluding the entire `asr`, `backend`,
`baiduapi`, `test`, `work`, cache, checkpoint, and generated-output trees:

| Item | Count |
| --- | ---: |
| Legacy code/notebook files in the review pool | 113 |
| Legacy source files already migrated or merged | 49 |
| Standardized generic scripts produced | 38 |
| Shared business-call references produced | 38 |
| Legacy files reviewed and explicitly rejected/deferred | 34 |
| Remaining legacy files without a final per-file disposition | 30 |

The remaining 30 is intentionally conservative. Some files have already been
recognized at a group level as business-specific, experimental, duplicated, or
unsafe, but they stay in the unaudited count until their exact path and final
decision are recorded. This avoids reporting group-level assumptions as a
completed file review.

## Migrated generic scripts

| New script | Legacy source | Notes |
| --- | --- | --- |
| `scripts/datasets/move_images_matching_xml.py` | `move_matching_images_to_cut.py` | Business paths moved to `tests/datasets` |
| `scripts/datasets/move_md5_duplicates.py` | `similarity_comparison_md5.py` | Source mutation is preview-only by default |
| `scripts/documents/voc_to_yolo.py` | `important/voc_to_yolo.py`, `bty/voc_to_yolo.py` | Duplicate implementations merged |
| `scripts/documents/svg_to_png.py` | `svg2img.py`, `svg_to_img.go` | One Python implementation retained |
| `scripts/documents/offset_yolo_class_ids.py` | `imgdeal/change_yolo_label.py` | In-place modification is preview-only by default |
| `scripts/documents/count_annotation_labels.py` | three `statistics_yolo_label.py` files | Duplicate implementations merged |
| `scripts/vision/convert_png_to_jpg.py` | `imgdeal/png_to_jpg.py` | Destructive PNG deletion removed |
| `scripts/datasets/split_image_list.py` | `important/v_yolo_data_split.py` | Cache deletion removed; seed can be fixed |
| `scripts/datasets/organize_images_and_xml.py` | `important/move_img&xml_to_new.py` | Only known images and XML are moved; preview default |
| `scripts/datasets/rename_files_sequentially.py` | `bty/Batch_Rename.py` | Collision check and preview default added |
| `scripts/documents/create_empty_yolo_labels.py` | `important/makeYolo_no_lable.py` | Existing labels are retained |
| `scripts/vision/extract_video_frames.py` | `important/video_cut.py` | Stable numbered output replaces timestamps |
| `scripts/vision/extract_gif_frames.py` | `dingstock/gif_editor.py` | File extraction retained; debug/editor state removed |
| `scripts/documents/render_pdf_pages.py` | `ws/pdf2img.py` | Direct file input replaces temporary Base64 files |
| `scripts/documents/copy_xml_template_for_images.py` | `dingstock/xml_copy.py` | Preview default and output directory added |
| `scripts/datasets/uppercase_filename_prefix.py` | `dingstock/imgN_lower2upper.py` | Collision check and preview default added |
| `scripts/vision/crop_images_by_voc_template.py` | `dingstock/img_cut_xmlTemp.py` | Template boxes generalized and clipped to image bounds |
| `scripts/vision/inpaint_color_region.py` | `imgdeal/Inpaint.py`, `Inpaint_one.py` | Batch and single experiments merged into configurable operation |
| `scripts/vision/group_images_by_dhash.py` | `dingstock/select_similar_DH.py` | Exact dHash duplicate grouping retained |
| `scripts/datasets/split_log_embedded_images.py` | `split_log_data_images.py` | Fixed business path moved to tests |
| `scripts/datasets/select_voc_samples_by_labels.py` | duplicate `select_cats_img_xml.py` files | Selection and copy combined without temporary JSON |
| `scripts/documents/split_voc_by_label_groups.py` | duplicate `xml_getlabel_to_new.py` files | Global state bug removed |
| `scripts/datasets/rename_directories_to_pinyin.py` | `imgdeal/name_pinyin.py` | Collision check and preview default added |
| `scripts/datasets/split_paired_dataset.py` | `important/data_divided.py` | Generic ratios, seed, and paired copy layout |
| `scripts/documents/voc_to_coco.py` | `imgdeal/voc_to_coco_old.py` | Global conversion state removed; deterministic category IDs and error summary added |
| `scripts/documents/yolo_to_voc.py` | `important/txt2xml.py` | Image formats generalized; paths and classes moved to business call |
| `scripts/datasets/quarantine_unpaired_files.py` | `important/del_imgxml.py` | Destructive delete removed; quarantine is preview-only by default with collision checks |
| `scripts/datasets/copy_unique_images_by_hash.py` | three `dingstock/remove_duplicates*.py` variants | MD5 and perceptual hash paths merged; destructive moves and timestamp-based scanning removed |
| `scripts/documents/rename_voc_labels.py` | `important/Pictools.py` | One operation extracted from the legacy multipurpose class; in-place edits require execute mode |
| `scripts/documents/sync_voc_image_sizes.py` | `important/Pictools.py` | Image-size reconciliation extracted; legacy delete-on-error behavior removed |
| `scripts/datasets/download_oss_prefix.py` | `dingstock/oss_download.py` | Embedded credentials removed; prefix-relative paths, preview mode, concurrency limits, and overwrite control added |
| `scripts/automation/invoke_image_json_service.py` | root `request_batch.py` | Request construction separated from Temu response drawing and business question extraction |
| `scripts/vision/merge_fading_video_targets.py` | root `merge_frames_targets.py` | Hard-coded paths removed; standard directory runner, structured results, and parameter validation added |
| `scripts/datasets/export_image_md5_manifest.py` | `dingstock/ml_iconHash_batch.py` | Raw-image and Base64-text hashing retained; JSON, Go, and TSV output made explicit |
| `scripts/documents/coco_to_voc.py` | `imgdeal/coco_to_voc.py`, `imgdeal/COCOtoVOC.py` | Two implementations merged without pycocotools; class filtering and optional image copy retained |
| `scripts/documents/remove_voc_labels.py` | duplicate `bty/xmlTool.py`, `imgdeal/xmlTool.py` | Missing remove operation extracted; count and rename behavior are covered by existing scripts |
| `scripts/vision/crop_images_by_voc_annotations.py` | `dingstock/geetest_v4_datasets.py` | Paired VOC crop behavior extracted; fixed slots, display state, and hash grouping omitted |
| `scripts/vision/composite_rgba_foregrounds.py` | root `get_mask_final.py`, `get_mask_final_baseimg.py` | Two experiments merged into deterministic, bounded RGBA composition without per-pixel Python loops |

Each row has a corresponding business call under `tests/<domain>/` when the
legacy source contained meaningful parameters.

## Excluded

- entire `asr/`, `backend/`, and `baiduapi/` trees;
- `work/`, caches, notebook checkpoints, debug montages, logs, reports, and
  compiled output;
- empty files and copied third-party SDK source;
- account/domain analysis, remote deletion, credential-bearing calls, and
  clearly one-off crawlers unless explicitly requested later;
- old sample images, XML output, archives, and other test data.

## Deferred business-specific code

These are not assumed to be reusable merely because they are Python scripts:

- `dingstock/062325-KAUser.py` and domain-analysis variants;
- captcha request/test programs and provider-specific OCR crawlers;
- fixed Redis/MongoDB cleanup scripts and AWS cleanup operations;
- old `ws/AI_API*.py`, Flask request tests, and named customer/service calls;
- notebooks and experimental `test*.py` files.

They remain in `D:\yl\localcode` until their current business use is confirmed.

## Generic candidates still to review

- remaining archive, packaging, specialized rename, and dataset assembly code;
- COCO/VOC conversion variants and annotation rendering not already superseded;
- background removal, similarity, clustering, odd-target detection, and
  synthetic image generation whose current use is still unclear;
- current service-start and health-check helpers after provider and credential
  assumptions are separated;
- recent large scripts such as RGBA icon clustering, reviewed independently
  rather than copied as a complete historical project.

Candidates are migrated in small reviewed batches. A candidate may still be
rejected if its useful behavior cannot be separated from one historical task.

Rejected after review: the old `json_to_xml.py` is incomplete. The two historical
COCO-to-VOC implementations were later merged into a parameterized converter
rather than copied with their original directory assumptions.

Also rejected/deferred after detailed review: `labels_divided_train_val.py`,
`expand_divided_train_val.py`, and `divide_dataset_yolo_txt.py` use specialized
sampling strategies; `yolotxt_get_cats_img_label.py` contains broken coordinate
and OpenCV calls; `select_laptop_tv_img.py` is tied to one JSON/business schema.

Further reviewed without migration: root `win_cut.py` is a small interactive GUI
rather than a reusable script; `dingstock/img_cut.py` is a disabled fixed-coordinate
business crop; `dingstock/ahash_name.py` and `ahash_name_Cv.py` are import-time
experiments; `ws/unpack_glint360k.py` remains deferred because it depends on the
legacy MXNet RecordIO layout and has no confirmed current use.

`dingstock/img_clustering.py` remains deferred: it loads a deprecated pretrained
model at import time and recomputes features inside an O(n-squared) loop. The
capability should only migrate when its current model and grouping semantics are
confirmed. `dingstock/rc_rename.py` is a recaptcha-specific filename grammar and
class mapping, so it remains a business script rather than a generic capability.

`important/data_augmented.py` remains deferred because cropping, padding, noise,
and annotation changes are tightly coupled and its image lookup depends on a
module-level business path. `important/run_mutil_process.py` is excluded from
generic migration: it contains an embedded credential and private endpoint for
one retired request protocol. A future batch requester should be designed from
current service requirements instead of preserving that protocol.

The captcha-specific `dingstock/similar_shape.py` and `dingstock/grid_drop.py`
remain business solvers rather than general visual algorithms. The experimental
`dingstock/bill_pic_processing.py` is also deferred: it loads a machine-local
background-removal model during import and its no-rectangle path leaves the
result undefined. Reusable document rectification should be extracted only when
its expected inputs and failure behavior are confirmed.

Root `redis_get_cache_batch.py` is excluded from generic migration because it
contains an embedded remote credential and decodes one HCaptcha-specific cache
schema. `ws/AI_API_time.py` is an obsolete scheduler experiment whose job only
writes a test file; neither is a reusable service helper.

`ws/Plate_Landmarks_datasets.py` remains tied to one label schema and training
text format. `ws/seal_extract.py` is an unvalidated fixed-threshold experiment,
and `dingstock/z_train_dataload.py` combines model dataset code with split logic
already covered by Toolkit scripts. These three remain deferred rather than
being copied as generic capabilities.

The duplicate `bty/ocr_puttext.py` and `ws/ocr_puttext.py` remain deferred: they
parse one fixed Chinese field set from one image region and require a machine
font. Generic text drawing alone does not justify preserving that business
layout parser.

`ws/bill_correct.py` remains a historical invoice-layout heuristic with fixed
ratio tables and interactive display. `ws/ynyd_excel.py` is a one-off fuzzy
merge for two named procurement spreadsheets with fixed columns and output
paths. Neither is migrated as a generic capability. `dingstock/rc_rename.py`
remains covered by its earlier business-specific defer decision.

Root `imgTemp_augmented.py` remains a specialized three-object oriented-box
generator with coupled replacement rules. `dingstock/icon_rgba_cluster.py` is
newer and potentially valuable, but its single large module currently combines
feature extraction, distance construction, clustering, file copying, reports,
HTML preview, and label-dictionary generation. It is deferred for deliberate
decomposition rather than copied wholesale.
