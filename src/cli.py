"""Command-line interface argument parser and configuration model."""

import argparse
from dataclasses import dataclass
from typing import Sequence

from validator import (
    validate_output_file,
    validate_package_name,
    validate_repository,
    validate_version,
)


@dataclass(frozen=True)
class AppConfig:
    """Immutable configuration parameters for the visualizer."""

    package: str
    repository: str
    test_mode: bool
    version: str
    output: str


def build_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="apk-dep-visualizer",
        description="Dependency graph visualizer for Alpine Linux (apk).",
    )
    parser.add_argument(
        "-p",
        "--package",
        required=True,
        help="Name of the target package to analyze.",
    )
    parser.add_argument(
        "-r",
        "--repo",
        required=True,
        help="Repository URL or path to test repository file.",
    )
    parser.add_argument(
        "-t",
        "--test-mode",
        action="store_true",
        help="Enable test repository mode using a local file.",
    )
    parser.add_argument(
        "-v",
        "--version",
        required=True,
        help="Target version of the package.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="graph.png",
        help="Output PNG filename for the rendered graph.",
    )
    return parser


def parse_config(argv: Sequence[str] | None = None) -> AppConfig:
    """Parse and validate CLI arguments into an AppConfig instance."""
    parser = build_parser()
    args = parser.parse_args(argv)
    package = validate_package_name(args.package)
    repository = validate_repository(args.repo, args.test_mode)
    version = validate_version(args.version)
    output = validate_output_file(args.output)
    return AppConfig(
        package=package,
        repository=repository,
        test_mode=args.test_mode,
        version=version,
        output=output,
    )
