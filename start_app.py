import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"


def start_backend():
    print("Starting FastAPI backend...")

    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=BACKEND_DIR,
    )


def start_frontend():
    print("Starting Next.js frontend...")

    # shell=True is useful on Windows because npm is usually npm.cmd
    return subprocess.Popen(
        "npm run dev",
        cwd=FRONTEND_DIR,
        shell=True,
    )


def main():
    print("=" * 60)
    print("Manufacturer Agent")
    print("=" * 60)

    if not BACKEND_DIR.exists():
        print(f"Backend folder not found: {BACKEND_DIR}")
        return

    if not FRONTEND_DIR.exists():
        print(f"Frontend folder not found: {FRONTEND_DIR}")
        return

    backend = None
    frontend = None

    try:
        backend = start_backend()

        time.sleep(2)

        frontend = start_frontend()

        print()
        print("=" * 60)
        print("Application started")
        print("=" * 60)
        print("Frontend: http://localhost:3000")
        print("Backend:  http://localhost:8000")
        print("Swagger:  http://localhost:8000/docs")
        print()
        print("Press Ctrl+C to stop both servers.")
        print("=" * 60)

        while True:
            # If either process unexpectedly dies,
            # exit instead of leaving the other running forever.
            if backend.poll() is not None:
                print("Backend stopped unexpectedly.")
                break

            if frontend.poll() is not None:
                print("Frontend stopped unexpectedly.")
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping application...")

    finally:
        if backend and backend.poll() is None:
            backend.terminate()

        if frontend and frontend.poll() is None:
            frontend.terminate()

        time.sleep(1)

        if backend and backend.poll() is None:
            backend.kill()

        if frontend and frontend.poll() is None:
            frontend.kill()

        print("Frontend and backend stopped.")


if __name__ == "__main__":
    main()