"""
run_all.py — start every FastAPI backend in this project at once, each on
its own port, from one command. Press Ctrl+C to stop all of them.

Usage:
    uv run python run_all.py
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# appm2m's login rate limit keeps its counters in Redis (appm2m/rate_limit.py)
REDIS_CONTAINER = "my-radis"
REDIS_PORT = 6379

# (import string, port, what it's for)
# Note: keep these notes plain ASCII - some Windows terminals use a codepage
# (e.g. Thai cp874) that can't print em-dashes/middle-dots and would crash here.
SERVERS = [
    ("crud_basics.main:app", 8000, "students, in-memory list - frontend: /"),
    ("crud_basics.student_db:app", 8004, "students, SQLite, no relations"),
    ("crud_basics.product_db:app", 8001, "products, SQLite - frontend: /products"),
    ("appv.main:app", 8003, "students <-> phones, one-to-many"),
    ("appm2m.main:app", 8002, "products <-> categories, many-to-many - frontend: /catalog"),
    ("graphql_demo.main:app", 8005, "products via GraphQL + SQLite - frontend: /graphql-shop"),
]


def redis_is_up() -> bool:
    # Send a real PING: Docker Desktop keeps the port open even while the
    # container is stopped, so "can connect" alone isn't enough.
    try:
        with socket.create_connection(("127.0.0.1", REDIS_PORT), timeout=1) as conn:
            conn.sendall(b"PING\r\n")
            return conn.recv(16).startswith(b"+PONG")
    except OSError:
        return False


def ensure_redis() -> None:
    """Start the Redis container if it's stopped. Never fatal: only login on 8002 needs it."""
    if redis_is_up():
        print(f"Redis: already running on port {REDIS_PORT}\n", flush=True)
        return

    print(f"Redis: not running, trying `docker start {REDIS_CONTAINER}`...", flush=True)
    try:
        result = subprocess.run(
            ["docker", "start", REDIS_CONTAINER], capture_output=True, text=True, timeout=60
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        result = None

    for _ in range(10):  # give the container a few seconds to open the port
        if redis_is_up():
            print(f"Redis: started ({REDIS_CONTAINER})\n", flush=True)
            return
        time.sleep(0.5)

    reason = result.stderr.strip() if result and result.stderr else "Docker not available - is Docker Desktop open?"
    print(f"[!] Redis could not start: {reason}", flush=True)
    print("    Everything else runs, but login on port 8002 will answer 503.\n", flush=True)


def main():
    processes = []
    ensure_redis()
    print("Starting all backends...\n", flush=True)

    for module, port, note in SERVERS:
        cmd = [
            sys.executable, "-m", "uvicorn", module,
            "--reload", "--port", str(port),
        ]
        proc = subprocess.Popen(
            cmd,
            cwd=ROOT,
            env={**os.environ, "PYTHONUTF8": "1"},
        )
        processes.append((module, port, proc))
        print(f"  http://127.0.0.1:{port}  ->  {module:<22} ({note})", flush=True)

    print("\nAll running. Press Ctrl+C to stop everything.\n", flush=True)

    try:
        while True:
            time.sleep(1)
            for module, port, proc in processes:
                if proc.poll() is not None:
                    print(
                        f"\n[!] {module} (port {port}) exited with code {proc.returncode}",
                        flush=True,
                    )
    except KeyboardInterrupt:
        pass
    finally:
        print("\nStopping all backends...", flush=True)
        for module, port, proc in processes:
            if proc.poll() is None:
                proc.terminate()
        for module, port, proc in processes:
            proc.wait()
        print("All stopped.", flush=True)


if __name__ == "__main__":
    main()
