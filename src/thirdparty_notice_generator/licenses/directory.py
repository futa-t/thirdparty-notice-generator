from pathlib import Path


def get_license_text(path: Path | str) -> str | None:
    p = Path(path).expanduser()
    if license_file := list(p.glob("license*", case_sensitive=False)):
        try:
            return license_file[0].read_text("utf-8")
        except Exception:
            return None
