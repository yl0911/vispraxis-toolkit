# Script taxonomy

The repository has four script domains. Keep them shallow:
add clearly named modules first and create a second-level group only after
several related scripts make the flat directory difficult to scan.

## `datasets`

Operations on a collection of data files: URL/OSS/MinIO/database acquisition,
scanning, pairing, selection, rename, deduplication, splitting, packaging,
unpacking, statistics, and generated dataset management.

A provider client is extracted only when several scripts genuinely reuse it;
the complete download or export task remains directly visible in `datasets`.

## `documents`

Pure, reusable content operations for annotation and other documents. This
includes VOC/COCO/YOLO conversion, XML/JSON/text modification, label changes,
spreadsheet processing, and PDF or Word content transformation.

The former standalone `annotations` domain is represented by document modules
such as `convert_voc_to_yolo.py`.

## `vision`

Visual transformations and algorithms: background removal, detection,
clustering, classification, recognition, comparison, restoration, feature
extraction, and generation. Dataset-wide organization stays in `datasets`, and
annotation document writing stays in `documents` even when a vision algorithm
produces the source values.

## `automation`

Service and automation helpers: start or stop a model, wait for health, invoke
a service, batch requests, or perform a complete third-party client operation.

## Business tests

`tests/<domain>/` contains business-specific parameters and runnable calls for
the corresponding reusable scripts. These files are expected to change more
often than `scripts/`; that separation prevents business changes from creating
copies or versions of the generic implementation.

If a future business process combines several scripts into a maintained
pipeline, it may be promoted to `workflows/`. A single parameterized call does
not need a workflow abstraction.

## Orthogonal metadata

Provider, old project, maturity, risk, and supported formats may be documented
in the script header or migration inventory; they do not need extra directory
levels. Every migrated script has one primary domain and one canonical file.
