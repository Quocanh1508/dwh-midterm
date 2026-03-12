"""
run_dbt.py
==========
Helper script to run dbt commands while automatically injecting 
the `.env` variables (like GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS)
into the environment.

Usage:
    python scripts/run_dbt.py run
    python scripts/run_dbt.py test
    python scripts/run_dbt.py compile
"""

import os
import sys
import subprocess
import pathlib
from dotenv import load_dotenv

def main():
    # Print the command being passed to dbt
    dbt_args = sys.argv[1:]
    if not dbt_args:
        print("Please provide a dbt command (e.g., 'run', 'test').")
        sys.exit(1)

    # 1. Load .env variables into the environment
    root_dir = pathlib.Path(__file__).parent.parent
    env_path = root_dir / ".env"
    load_dotenv(env_path)

    # Ensure GOOGLE_APPLICATION_CREDENTIALS is an absolute path
    # since dbt will run from a different working directory
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds and not os.path.isabs(creds):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(root_dir / creds)

    # 2. Append the profiles-dir flag so dbt finds profiles.yml in the dbt folder
    # Assuming this script is run from the project root.
    dbt_dir = pathlib.Path(__file__).parent.parent / "dbt"
    
    cmd = ["dbt"] + dbt_args + ["--profiles-dir", str(dbt_dir)]
    print(f"🚀 Running: {' '.join(cmd)}")

    # 3. Execute dbt from within the root or dbt directory
    # We set cwd to dbt_dir so dbt_project.yml is naturally found
    result = subprocess.run(cmd, cwd=dbt_dir)

    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
