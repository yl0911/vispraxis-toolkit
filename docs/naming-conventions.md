# Naming conventions

## Script files

Use lowercase `snake_case` and name a capability with an explicit verb and
object. Add the source, destination, or algorithm only when it distinguishes
the behavior.

Preferred patterns:

```text
<verb>_<object>.py
<verb>_<object>_<source>.py
<verb>_<source>_to_<destination>.py
```

Examples include `move_images_matching_annotations.py`,
`download_dataset_oss.py`, `convert_voc_to_yolo.py`,
`cluster_images_by_rgba.py`, and `start_model_service.py`.

Do not introduce names such as `tools.py`, `utils.py`, `process.py`, `final.py`,
`new.py`, or `v2.py`. A meaningful behavioral difference belongs in the name;
an implementation revision belongs in version control.

## Python API

Every standardized script defines:

- a clear `run(...)` function with explicit arguments;
- `build_parser()` for the local CLI;
- `main(argv=None) -> int` as a thin CLI adapter.

Request/result dataclasses are optional and local to the script. Do not add a
shared framework merely to make two scripts look identical. Extract shared
implementation only after stable, meaningful duplication is demonstrated.

## Documentation

The module docstring must explain the function boundary, Python call shape,
CLI invocation, and migrated legacy sources. Comments explain non-obvious
algorithmic decisions rather than narrating assignments.

## Business tests

Machine-specific paths, fixed providers, and business parameters belong under
`tests/<domain>/`. Name the file for the scenario and operation, for example
`geetest_voc_to_yolo.py`; do not use generic names such as `test.py`.

The test file should expose a clearly marked parameter preset and a `main()`.
It is a runnable business call rather than a collection of assertion functions.

## Catalog entries

New generic scripts must be added to `docs/function-catalog.md` under their
primary domain. Use the actual repository path, a one-sentence behavioral
description, and the matching business-call path. Do not maintain a second
detailed feature table in the root README.
