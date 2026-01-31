# Skip performance benchmarks by default because they can be extremely slow / resource intensive.
#
# Enable them explicitly with:
#
#     pytest --tight_loop_performance
#
# This is implemented as a path-based skip so we don't need to add markers to every profiling test.

import pathlib

import pytest


_TIGHT_LOOP_DIR_FRAGMENT = str(pathlib.Path("profiling") / "tight_loop_performance")
_EXCEPTION_PERF_DIR_FRAGMENT = str(pathlib.Path("profiling") / "exception_performance")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--tight_loop_performance",
        action="store_true",
        default=False,
        help=(
            "Include performance benchmarks under profiling/tight_loop_performance and profiling/exception_performance "
            "(skipped by default)."
        ),
    )


def pytest_configure(config: pytest.Config) -> None:
    # Register marker so --strict-markers doesn't complain when/if we use it.
    config.addinivalue_line(
        "markers",
        "performance_test: performance benchmarks (skipped unless --tight_loop_performance)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--tight_loop_performance"):
        return

    skip_marker = pytest.mark.skip(
        reason="Skipped by default; enable with --tight_loop_performance",
    )

    for item in items:
        # item.path is a pathlib.Path in newer pytest, but can be a py.path in older versions.
        path_str = str(getattr(item, "path", getattr(item, "fspath", "")))
        if _TIGHT_LOOP_DIR_FRAGMENT in path_str or _EXCEPTION_PERF_DIR_FRAGMENT in path_str:
            item.add_marker(skip_marker)
            item.add_marker(pytest.mark.performance_test)
