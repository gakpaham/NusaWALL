#!/usr/bin/env python
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"


def get_venv_python() -> Path:
    if sys.platform.startswith("win"):
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_environment() -> Path:
    if not VENV_DIR.exists():
        print("[NusaWall] Membuat virtual environment di .venv...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)

    python_path = get_venv_python()
    if not python_path.exists():
        raise FileNotFoundError(f"Virtual environment tidak ditemukan di {python_path}")
    return python_path


def install_project(python_path: Path) -> None:
    print("[NusaWall] Menginstal dependency project...")
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(python_path), "-m", "pip", "install", "-e", "."], cwd=str(ROOT), check=True)


def cmd_setup() -> None:
    python_path = ensure_environment()
    install_project(python_path)
    print("\n[NusaWall] Setup selesai.")
    print(f"Gunakan environment aktif dengan: {VENV_DIR}\n")
    print(f"Atau jalankan cek kesehatan dengan: {python_path} manage.py doctor")


def cmd_doctor() -> None:
    print("NusaWall scaffold is healthy.")
    try:
        import nusawall  # noqa: F401
        print("Package import: OK")
    except Exception as exc:  # pragma: no cover - diagnostic command
        print(f"Package import: FAIL ({exc})")
        raise


def cmd_status() -> None:
    print("NusaWall command runner ready.")
    print(f"Project root: {ROOT}")
    print(f"Virtual environment: {VENV_DIR}")


def cmd_run() -> None:
    python_path = ensure_environment()
    install_project(python_path)
    print("\n[NusaWall] Project siap digunakan.")
    print(f"Lanjutkan dengan: {python_path} manage.py doctor")


def main() -> None:
    parser = argparse.ArgumentParser(prog="manage.py", description="NusaWall project CLI")
    parser.add_argument(
        "command",
        nargs="?",
        default="run",
        choices=["run", "start", "setup", "doctor", "status"],
        help="Perintah untuk menjalankan project atau mengecek status.",
    )
    args = parser.parse_args()

    command = args.command
    if command in {"run", "start", "setup"}:
        cmd_setup() if command == "setup" else cmd_run()
    elif command == "doctor":
        cmd_doctor()
    else:
        cmd_status()


if __name__ == "__main__":
    main()
