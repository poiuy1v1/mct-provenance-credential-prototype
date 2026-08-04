#!/usr/bin/env python3
"""Execute and sanitise the committed demonstration notebook.

The preferred backend is nbclient.  A deterministic standard-library backend
is retained for constrained offline audit hosts; it executes every code cell in
one clean Python namespace and records stdout as Jupyter stream outputs.  The
fallback is explicit in the command report and is not represented as nbclient.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import io
import json
import os
import re
import sys
import traceback
import warnings
from pathlib import Path
from typing import Any

PRIVATE_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z])(?:[A-Za-z]:[\\/]|\\\\|"
    r"/(?:home|Users|root|tmp|private/var(?:/folders)?)/)"
)
SECRET_PATTERN = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)


def source_text(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def sanitize_notebook(notebook: dict[str, Any]) -> dict[str, Any]:
    clean = copy.deepcopy(notebook)
    clean["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3"},
    }
    for cell in clean.get("cells", []):
        metadata = cell.get("metadata", {})
        metadata.pop("execution", None)
        metadata.pop("collapsed", None)
        metadata.pop("scrolled", None)
        cell["metadata"] = metadata
        if cell.get("cell_type") != "code":
            continue
        for output in cell.get("outputs", []):
            output.pop("execution_count", None)
            output.pop("metadata", None)
            if output.get("output_type") == "error":
                output["traceback"] = [
                    PRIVATE_PATH_PATTERN.sub("<private-path>/", line)
                    for line in output.get("traceback", [])
                ]
    return clean


def execute_with_stdlib(
    notebook: dict[str, Any], workdir: Path
) -> dict[str, Any]:
    """Execute code cells in one isolated namespace and capture deterministic IO."""

    executed = copy.deepcopy(notebook)
    namespace: dict[str, Any] = {"__name__": "__main__"}
    previous_cwd = Path.cwd()
    previous_path = list(sys.path)
    previous_dont_write = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(workdir))
    os.chdir(workdir)
    execution_count = 0
    try:
        for cell_index, cell in enumerate(executed.get("cells", []), start=1):
            if cell.get("cell_type") != "code":
                continue
            execution_count += 1
            stdout = io.StringIO()
            stderr = io.StringIO()
            outputs: list[dict[str, Any]] = []
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(
                    stderr
                ):
                    exec(
                        compile(
                            source_text(cell),
                            f"<notebook-cell-{cell_index}>",
                            "exec",
                        ),
                        namespace,
                        namespace,
                    )
            except Exception as error:
                if stdout.getvalue():
                    outputs.append(
                        {
                            "name": "stdout",
                            "output_type": "stream",
                            "text": stdout.getvalue(),
                        }
                    )
                if stderr.getvalue():
                    outputs.append(
                        {
                            "name": "stderr",
                            "output_type": "stream",
                            "text": stderr.getvalue(),
                        }
                    )
                outputs.append(
                    {
                        "ename": type(error).__name__,
                        "evalue": str(error),
                        "output_type": "error",
                        "traceback": traceback.format_exception(error),
                    }
                )
                cell["execution_count"] = execution_count
                cell["outputs"] = outputs
                raise RuntimeError(
                    f"Notebook execution failed in code cell {execution_count}"
                ) from error

            if stdout.getvalue():
                outputs.append(
                    {
                        "name": "stdout",
                        "output_type": "stream",
                        "text": stdout.getvalue(),
                    }
                )
            if stderr.getvalue():
                outputs.append(
                    {
                        "name": "stderr",
                        "output_type": "stream",
                        "text": stderr.getvalue(),
                    }
                )
            cell["execution_count"] = execution_count
            cell["outputs"] = outputs
    finally:
        os.chdir(previous_cwd)
        sys.path[:] = previous_path
        sys.dont_write_bytecode = previous_dont_write
    return executed


def execute_with_nbclient(
    notebook_path: Path, workdir: Path, timeout: int
) -> dict[str, Any]:
    import nbformat  # type: ignore[import-not-found]
    from nbclient import NotebookClient  # type: ignore[import-not-found]

    notebook = nbformat.read(notebook_path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name="python3",
        allow_errors=False,
        record_timing=False,
        resources={"metadata": {"path": str(workdir)}},
        extra_arguments=["--IPKernelApp.log_level=ERROR"],
    )
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r"Proactor event loop does not implement add_reader.*",
            category=RuntimeWarning,
        )
        executed = client.execute()
    return json.loads(nbformat.writes(executed, version=4))


def backend_available(name: str) -> bool:
    if name != "nbclient":
        return True
    try:
        import nbclient  # noqa: F401
        import nbformat  # noqa: F401
    except ImportError:
        return False
    return True


def write_notebook(notebook: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(notebook, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
        )


def assert_snapshot_safe(notebook: dict[str, Any]) -> None:
    serialized = json.dumps(notebook, ensure_ascii=False)
    if PRIVATE_PATH_PATTERN.search(serialized):
        raise ValueError("Executed notebook contains a private absolute path")
    if SECRET_PATTERN.search(serialized):
        raise ValueError("Executed notebook contains a credential-like secret")
    code_cells = [
        cell for cell in notebook.get("cells", []) if cell.get("cell_type") == "code"
    ]
    if not code_cells:
        raise ValueError("Executed notebook contains no code cells")
    if any(cell.get("execution_count") is None for cell in code_cells):
        raise ValueError("Executed notebook contains a null execution count")
    counts = [cell.get("execution_count") for cell in code_cells]
    if any(type(count) is not int or count <= 0 for count in counts):
        raise ValueError("Executed notebook contains an invalid execution count")
    if counts != list(range(1, len(code_cells) + 1)):
        raise ValueError(f"Executed notebook counts are not sequential: {counts}")
    if any(not cell.get("outputs") for cell in code_cells):
        raise ValueError("Executed notebook contains a code cell with no retained output")
    if any(
        output.get("output_type") == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    ):
        raise ValueError("Executed notebook contains an error output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("output")
    parser.add_argument(
        "--backend", choices=("auto", "nbclient", "stdlib"), default="auto"
    )
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--workdir")
    parser.add_argument(
        "--acceptance",
        action="store_true",
        help="Require the nbclient backend used by release acceptance and CI",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.timeout <= 0:
        raise SystemExit("Notebook timeout must be positive")
    source = Path(arguments.source).resolve()
    output = Path(arguments.output).resolve()
    workdir = (
        Path(arguments.workdir).resolve()
        if arguments.workdir
        else source.parent.resolve()
    )
    notebook = json.loads(source.read_text(encoding="utf-8"))

    backend = arguments.backend
    if backend == "auto":
        backend = "nbclient" if backend_available("nbclient") else "stdlib"
    if backend == "nbclient" and not backend_available("nbclient"):
        raise SystemExit("nbclient backend requested but nbclient is unavailable")
    if arguments.acceptance and backend != "nbclient":
        raise SystemExit(
            "Release acceptance requires nbclient; the stdlib backend is diagnostic only"
        )

    if backend == "nbclient":
        executed = execute_with_nbclient(source, workdir, arguments.timeout)
    else:
        executed = execute_with_stdlib(notebook, workdir)
    clean = sanitize_notebook(executed)
    assert_snapshot_safe(clean)
    write_notebook(clean, output)
    code_cells = [
        cell for cell in clean["cells"] if cell.get("cell_type") == "code"
    ]
    print(
        json.dumps(
            {
                "backend": backend,
                "release_acceptance_backend": backend == "nbclient",
                "code_cells_executed": len(code_cells),
                "execution_counts": [
                    cell["execution_count"] for cell in code_cells
                ],
                "kernel_name": "python3",
                "output": output.name,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
