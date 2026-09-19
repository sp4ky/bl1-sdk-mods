"""Package mod folders in this repo as .sdkmod archives, rebuilding only changed ones."""

import hashlib
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).parent


def mod_files(mod_dir: Path) -> list[Path]:
    """List the files that go into the mod's archive."""
    sdkmod = mod_dir / f"{mod_dir.name}.sdkmod"
    return [
        path
        for path in sorted(mod_dir.rglob("*"))
        if path.is_file() and path != sdkmod and "__pycache__" not in path.parts
    ]


def mod_signature(mod_dir: Path) -> dict[str, str]:
    """Map each archive arcname to the sha256 of the folder file behind it."""
    signature: dict[str, str] = {}
    for path in mod_files(mod_dir):
        arcname = f"{mod_dir.name}/{path.relative_to(mod_dir)}"
        signature[arcname] = hashlib.sha256(path.read_bytes()).hexdigest()
    return signature


def archive_signature(sdkmod: Path) -> dict[str, str]:
    """Map each archive entry name to the sha256 of its content."""
    with zipfile.ZipFile(sdkmod) as archive:
        return {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()}


def is_up_to_date(mod_dir: Path) -> bool:
    """Return whether the mod's archive matches the mod folder contents."""
    sdkmod = mod_dir / f"{mod_dir.name}.sdkmod"
    if not sdkmod.exists():
        return False
    try:
        return archive_signature(sdkmod) == mod_signature(mod_dir)
    except (
        zipfile.BadZipFile,
        zlib.error,
        EOFError,
    ):
        return False


def build(mod_dir: Path) -> Path:
    """Zip mod_dir into mod_dir/<name>.sdkmod and return the archive path."""
    sdkmod = mod_dir / f"{mod_dir.name}.sdkmod"
    with zipfile.ZipFile(sdkmod, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in mod_files(mod_dir):
            archive.write(path, f"{mod_dir.name}/{path.relative_to(mod_dir)}")
    return sdkmod


def main() -> int:
    """Build a .sdkmod for every mod folder that has changes. Returns a process exit code."""
    built = 0
    skipped = 0
    for init in sorted(ROOT.glob("*/__init__.py")):
        mod_dir = init.parent
        if is_up_to_date(mod_dir):
            print(f"Skipped {mod_dir} (up to date)")
            skipped += 1
        else:
            print(f"Built {build(mod_dir)}")
            built += 1
    if built == 0 and skipped == 0:
        print("No mod folders found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
