"""Entry point for Stage 2 direct dependency extraction."""

from pathlib import Path
import sys
from typing import Sequence

from apk_parser import (
    ApkRepositoryError,
    extract_index_from_bytes,
    fetch_apkindex_text,
    resolve_direct_dependencies,
)
from cli import AppConfig, parse_config
from validator import ConfigValidationError

EXIT_SUCCESS = 0
EXIT_ERROR = 1
GZIP_SUFFIX = ".gz"


def load_index_text(config: AppConfig) -> str:
    """Load APKINDEX content from remote repository or local file."""
    if not config.test_mode:
        return fetch_apkindex_text(config.repository)
    try:
        raw_bytes = Path(config.repository).read_bytes()
    except OSError as exc:
        raise ApkRepositoryError(f"Cannot read local index: {exc}") from exc
    if config.repository.endswith(GZIP_SUFFIX):
        return extract_index_from_bytes(raw_bytes)
    return raw_bytes.decode("utf-8")


def format_dependencies(dependencies: list[str]) -> str:
    """Format direct dependencies list for console output."""
    if not dependencies:
        return "No direct dependencies."
    return "\n".join(dependencies)


def run(argv: Sequence[str] | None = None) -> int:
    """Execute the CLI application for Stage 2."""
    try:
        config = parse_config(argv)
        index_text = load_index_text(config)
        deps = resolve_direct_dependencies(
            index_text, config.package, config.version
        )
    except (ConfigValidationError, ApkRepositoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    print(format_dependencies(deps))
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(run())
