# Source disposition

Functional classification answers **where a useful capability belongs**.
Source disposition answers the earlier question: **whether the source should be
migrated at all**.

Do not assign a functional domain until a source has passed the disposition
filter.

## Confirmed exclusions

The following directories are excluded from the Toolkit migration by project
decision:

| Source | Disposition | Reason |
| --- | --- | --- |
| `asr/` | `exclude-unused` | Standalone ASR model download and benchmark work for another production service |
| `backend/` | `exclude-unused` | Small Flask application and frontend templates, not a reusable script capability |
| `baiduapi/` | `exclude-unused` | Retired provider project containing an old copied SDK, provider examples, and project-specific processing |

Exclusion applies to the source directory, including apparently generic files
inside it. If equivalent functionality is still needed, select or reimplement
it from another maintained source rather than importing this retired tree. For
example, annotation conversion should use candidates from `important/` or
`imgdeal/`, not `baiduapi/baidu_coco_voc/`.

## Generated and local-only exclusions

These are not capabilities and should never enter the migration inventory as
implementation candidates:

| Source pattern | Disposition |
| --- | --- |
| `work/` | Generated local run output |
| `**/__pycache__/`, `*.pyc` | Python bytecode cache |
| `.ipynb_checkpoints/` | Generated notebook checkpoints |
| `.git/`, `.vscode/`, `.claude/`, `.agents/` | Repository or local tool state |
| `dingstock/icon_rgba_cluster/debug_montages/` | Visual debug output |
| `*_out.txt`, logs, reports | Generated execution output unless explicitly required as a fixture |

## Legacy tests, business calls, and sample data

Legacy test files remain deferred unless their parameters are useful as a
business call for a migrated generic script. The new repository's `tests`
directory is not a copy of the old test tree and is not a unit-test suite:

- `tests/<domain>/` stores runnable business calls with real paths, classes,
  provider settings, or other frequently changed parameters;
- every migrated generic script should receive a corresponding business call
  when the legacy source contains meaningful invocation parameters;
- machine-only variants belong in Git-ignored `local/`, not in `tests`;
- old test programs are not migrated merely because their path or name contains
  `test`.

The historical test tree is handled conservatively:

- `test/locustfile.py` and `test/seal/TY_batch_fwreq.py` are preserved in the
  old repository without modification for now;
- root, `ws`, `bty`, `dingstock`, and other `test*.py` files are also deferred;
- `test/` images, XML output, and `hc_select.rar` are historical sample or
  generated data, not Toolkit source code;
- empty test files are excluded rather than copied.

When a real automated test suite is created, fixtures should be selected
deliberately and reduced to the smallest non-sensitive examples. The old test
tree should not be copied wholesale.

## Directories requiring file-level review

These historical directories contain a mixture of useful and obsolete code.
Their directory name does not decide migration:

| Source | Default treatment | Notes |
| --- | --- | --- |
| `important/` | High-priority review | Contains newer annotation and dataset utilities, but still needs side-effect review |
| `imgdeal/` | Selective salvage | Contains useful converters plus older, duplicate, and data-bound scripts |
| `dingstock/` | Selective salvage | Contains recent reusable image tools mixed with crawlers, account analysis, remote cleanup, tests, and generated output |
| repository root | Selective salvage | Several newer self-contained tools, plus experiments and one-off integrations |
| `bty/` | Duplicate/legacy review | Mostly older project code; several files are exact duplicates of `imgdeal` or `ws` |
| `ws/` | Legacy review | Mostly 2021-2023 document/API experiments with hard-coded service assumptions |

Nothing in these directories is migrated merely because it can be assigned to
one of the four functional domains.

## Decision states

Use these states in the future migration inventory:

| State | Meaning |
| --- | --- |
| `migrate` | Useful, in scope, and selected for refactoring |
| `merge` | Useful behavior must be consolidated with another implementation |
| `duplicate` | Byte-identical or behaviorally superseded by a selected source |
| `defer-test` | Test or experiment intentionally left unchanged for now |
| `legacy-review` | Possible value, but applicability or safety is unclear |
| `exclude-unused` | Known project or capability is no longer needed |
| `exclude-generated` | Cache, output, sample dump, or local tooling state |
| `exclude-vendor` | Copied dependency that should not be owned by Toolkit |

## Admission questions

A source becomes `migrate` only when all of these questions have a satisfactory
answer:

1. Does VisPraxis still need the behavior?
2. Is it more than a one-time data repair or historical experiment?
3. Is there no newer canonical implementation elsewhere?
4. Can its inputs and outputs be described without the old project directory?
5. Can credentials, endpoints, and machine paths be removed from the code?
6. Can file and remote-system side effects be made explicit and controllable?
7. Is the dependency cost reasonable for this capability?

Failure on the first two questions means exclusion. Failure on later questions
usually means `legacy-review` until the capability is worth the refactoring
cost.
