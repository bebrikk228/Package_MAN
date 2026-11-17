"""Parser for Alpine Linux APKINDEX archives and direct dependencies."""

import io
import tarfile
import urllib.error
import urllib.request

INDEX_FILENAME = "APKINDEX"
ARCHIVE_NAME = "APKINDEX.tar.gz"
DEFAULT_ARCH = "x86_64"
HTTP_TIMEOUT = 30
CONFLICT_PREFIX = "!"
VERSION_SEPARATORS = ("<=", ">=", "!=", "=", "<", ">", "~")


class ApkRepositoryError(Exception):
    """Raised when APKINDEX cannot be fetched, parsed, or matched."""


def strip_version_constraint(token: str) -> str:
    """Remove version constraint operators from a dependency token."""
    result = token
    for sep in VERSION_SEPARATORS:
        if sep in result:
            result = result.split(sep, 1)[0]
    return result


def parse_provides_entry(raw_provides: str) -> list[str]:
    """Extract provided virtual or shared names from a p: field."""
    items: list[str] = []
    for token in raw_provides.split():
        cleaned = strip_version_constraint(token)
        if cleaned:
            items.append(cleaned)
    return items


def parse_depends_entry(raw_depends: str) -> list[str]:
    """Extract raw dependency names, ignoring conflict entries."""
    items: list[str] = []
    for token in raw_depends.split():
        if token.startswith(CONFLICT_PREFIX):
            continue
        cleaned = strip_version_constraint(token)
        if cleaned:
            items.append(cleaned)
    return items


def parse_record_block(block: str) -> dict[str, str]:
    """Parse a single package block from APKINDEX into key-value pairs."""
    record: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        record[key] = value
    return record


def build_index_data(
    index_text: str,
) -> tuple[dict[tuple[str, str], list[str]], dict[str, str]]:
    """Parse APKINDEX text into package dependencies and provides maps."""
    pkg_deps: dict[tuple[str, str], list[str]] = {}
    provides_map: dict[str, str] = {}
    for block in index_text.strip().split("\n\n"):
        record = parse_record_block(block)
        name = record.get("P", "")
        version = record.get("V", "")
        if not name or not version:
            continue
        pkg_deps[(name, version)] = parse_depends_entry(record.get("D", ""))
        for item in parse_provides_entry(record.get("p", "")):
            provides_map.setdefault(item, name)
    return pkg_deps, provides_map


def resolve_direct_dependencies(
    index_text: str, package: str, version: str
) -> list[str]:
    """Return ordered unique direct dependencies for package and version."""
    pkg_deps, provides_map = build_index_data(index_text)
    key = (package, version)
    if key not in pkg_deps:
        raise ApkRepositoryError(
            f"Package '{package}' version '{version}' not found."
        )
    resolved: list[str] = []
    for raw_dep in pkg_deps[key]:
        target = provides_map.get(raw_dep, raw_dep)
        if target != package and target not in resolved:
            resolved.append(target)
    return resolved


def extract_index_from_bytes(archive_bytes: bytes) -> str:
    """Extract and decode the APKINDEX file from APKINDEX.tar.gz bytes."""
    try:
        with tarfile.open(
            fileobj=io.BytesIO(archive_bytes), mode="r:gz"
        ) as archive:
            member = archive.extractfile(INDEX_FILENAME)
            if member is None:
                raise ApkRepositoryError("APKINDEX entry missing in archive.")
            return member.read().decode("utf-8")
    except (tarfile.TarError, OSError, UnicodeDecodeError) as exc:
        raise ApkRepositoryError(
            f"Failed to read APKINDEX archive: {exc}"
        ) from exc


def download_bytes(url: str) -> bytes:
    """Download raw bytes from the given HTTP or HTTPS URL."""
    request = urllib.request.Request(
        url, headers={"User-Agent": "apk-dep-visualizer/1.0"}
    )
    try:
        with urllib.request.urlopen(
            request, timeout=HTTP_TIMEOUT
        ) as response:
            return response.read()
    except (urllib.error.URLError, OSError) as exc:
        raise ApkRepositoryError(f"Failed to fetch '{url}': {exc}") from exc


def fetch_apkindex_text(repo_url: str) -> str:
    """Fetch and extract APKINDEX text from an Alpine repository URL."""
    base = repo_url.rstrip("/")
    primary_url = f"{base}/{ARCHIVE_NAME}"
    try:
        data = download_bytes(primary_url)
        return extract_index_from_bytes(data)
    except ApkRepositoryError:
        fallback_url = f"{base}/{DEFAULT_ARCH}/{ARCHIVE_NAME}"
        data = download_bytes(fallback_url)
        return extract_index_from_bytes(data)
