#!/usr/bin/env python3
"""
Startup script for UNTANGLE backend.
Handles migrations, seeding, and server startup gracefully.
"""
import subprocess
import sys
import os

def run_command(description, command, allow_failure=False):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"{description}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠ {description} failed:")
        print(e.stdout)
        print(e.stderr)
        if not allow_failure:
            print(f"✗ Critical error in {description}")
            sys.exit(1)
        else:
            print(f"⚠ Continuing despite {description} failure...")
            return False

def main():
    print("\n" + "="*50)
    print("UNTANGLE Backend Startup")
    print("="*50)

    # Step 1: Run migrations
    run_command(
        "Step 1: Database Migrations",
        "alembic upgrade head",
        allow_failure=True  # Don't fail if already migrated
    )

    # Step 2: Seed database
    run_command(
        "Step 2: Seed Database",
        "python seed_data.py",
        allow_failure=True  # Don't fail if already seeded
    )

    # Step 3: Start server (this must succeed)
    print("\n" + "="*50)
    print("Step 3: Starting Uvicorn Server")
    print("="*50)

    port = os.getenv("PORT", "8000")
    cmd = f"uvicorn app.main:app --host 0.0.0.0 --port {port}"

    print(f"Running: {cmd}")
    os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port])

if __name__ == "__main__":
    main()
