# Script call convention

This repository is a script collection, not an execution framework. Standards
exist to keep scripts understandable and callable without coupling them to a
shared runtime.

## Required shape

Each migrated script should provide:

1. A module docstring describing its function, Python call, CLI call, side
   effects, and legacy source.
2. A `run(...)` function with explicit inputs and a useful return value.
3. A `main(argv=None) -> int` CLI adapter.
4. An `if __name__ == "__main__"` guard that only calls `main()`.

```python
def run(source_dir: Path, output_dir: Path, *, recursive: bool = False):
    """Perform the reusable operation."""
    ...


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run(args.source_dir, args.output_dir, recursive=args.recursive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

There is no required common request class, result class, context object,
manifest, event system, or base class. A script may add local types when they
make that script easier to understand.

## Separation rule

- Reusable operation: `scripts/<domain>/`.
- Fixed paths, business parameters, and real task calls: `tests/<domain>/`.
- Machine-specific variants and frequently edited local adaptations: `local/`.
- Multi-script production workflows may use `workflows/` when they actually
  appear; do not create that layer for a single script call.
- Unconfirmed or one-off code: leave in `D:\yl\localcode` until reviewed.

Importing a script must not start work, connect to services, or modify files.
Destructive behavior must be explicit; preview or dry-run should be the default
when practical.

Standalone scripts run by file path. Business tests import those scripts and
run as modules from the repository root, for example
`python -m tests.datasets.business_case_name`.

## Business tests

`tests` here does not mean a generic unit-test suite. A business test records:

- the real scenario and expected purpose;
- frequently changed paths, classes, provider options, or other parameters;
- a runnable `main()` that prints the operation result;
- optional CLI overrides for using the same call on another machine.

Business tests do not need pytest, fixtures, mocks, or assertions. They may be
high-churn remote copies of useful calls. Destructive calls should still default
to preview/dry-run where the underlying script supports it.

`local/` may contain several variants for different projects or environments.
Its contents are Git-ignored except for `local/README.md`. Promote reusable
logic to `scripts/` and shareable business references to `tests/`.
