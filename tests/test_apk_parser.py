"""Unit tests for Stage 2 APKINDEX parsing and dependency extraction."""

import io
from pathlib import Path
import tarfile
import tempfile
import unittest

from apk_parser import (
    ApkRepositoryError,
    extract_index_from_bytes,
    resolve_direct_dependencies,
)
from main import run

SAMPLE_INDEX = (
    "P:musl\n"
    "V:1.2.5-r0\n"
    "p:so:libc.musl-x86_64.so.1=1\n"
    "\n"
    "P:libcurl\n"
    "V:8.9.1-r1\n"
    "D:ca-certificates-bundle so:libc.musl-x86_64.so.1\n"
    "p:so:libcurl.so.4=4.8.0\n"
    "\n"
    "P:curl\n"
    "V:8.9.1-r1\n"
    "D:ca-certificates-bundle so:libc.musl-x86_64.so.1 so:libcurl.so.4\n"
    "p:cmd:curl=8.9.1-r1\n"
)

EXIT_SUCCESS = 0
EXIT_ERROR = 1


def build_sample_tar_gz(content: str) -> bytes:
    """Create an in-memory APKINDEX.tar.gz archive from text."""
    buffer = io.BytesIO()
    encoded = content.encode("utf-8")
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        info = tarfile.TarInfo(name="APKINDEX")
        info.size = len(encoded)
        archive.addfile(info, io.BytesIO(encoded))
    return buffer.getvalue()


class TestApkParser(unittest.TestCase):
    """Test suite for APKINDEX archive extraction and dependency lookup."""

    def test_resolve_direct_dependencies(self) -> None:
        """Verify direct dependencies resolution including provides."""
        deps = resolve_direct_dependencies(SAMPLE_INDEX, "curl", "8.9.1-r1")
        self.assertEqual(
            deps, ["ca-certificates-bundle", "musl", "libcurl"]
        )

    def test_package_without_dependencies(self) -> None:
        """Verify empty list returned for base packages without D: field."""
        deps = resolve_direct_dependencies(SAMPLE_INDEX, "musl", "1.2.5-r0")
        self.assertEqual(deps, [])

    def test_missing_version_raises_error(self) -> None:
        """Verify error when package version does not match index."""
        with self.assertRaises(ApkRepositoryError):
            resolve_direct_dependencies(SAMPLE_INDEX, "curl", "0.0.1-r0")

    def test_extract_from_tar_gz_and_run_cli(self) -> None:
        """Verify archive extraction and Stage 2 CLI execution."""
        archive_bytes = build_sample_tar_gz(SAMPLE_INDEX)
        extracted = extract_index_from_bytes(archive_bytes)
        self.assertIn("P:curl", extracted)
        with tempfile.NamedTemporaryFile(
            suffix=".tar.gz", delete=False
        ) as tmp:
            tmp.write(archive_bytes)
            tmp_path = tmp.name
        try:
            argv = [
                "-p",
                "curl",
                "-r",
                tmp_path,
                "-t",
                "-v",
                "8.9.1-r1",
            ]
            self.assertEqual(run(argv), EXIT_SUCCESS)
            bad_argv = [
                "-p",
                "curl",
                "-r",
                tmp_path,
                "-t",
                "-v",
                "9.9.9-r0",
            ]
            self.assertEqual(run(bad_argv), EXIT_ERROR)
        finally:
            Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
