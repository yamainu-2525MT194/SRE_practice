#!/usr/bin/env python3
"""
サービス再起動 CLI
- Linux: systemctl restart <name>
- macOS: brew services restart <name> or launchctl kickstart
"""
import argparse, logging, platform, subprocess, sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "restart.log"

def setup_logger() -> logging.Logger:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=500_000, backupCount=3)
    fmt = "%(asctime)s %(levelname)s %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger = logging.getLogger("restart")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

def build_command(service: str, dry: bool) -> list[str]:
    os_name = platform.system()
    if os_name == "Linux":
        cmd = ["systemctl", "restart", service]
    elif os_name == "Darwin":          # macOS
        # Homebrew 経由の nginx などを想定
        cmd = ["brew", "services", "restart", service]
    else:
        raise RuntimeError(f"Unsupported OS: {os_name}")
    if dry:
        cmd.insert(0, "echo")          # 動作確認用
    return cmd

def main() -> None:
    parser = argparse.ArgumentParser(description="Restart a service safely.")
    parser.add_argument("service", help="Service name (e.g., nginx)")
    parser.add_argument("-d", "--dry-run", action="store_true",
                        help="Show command only, do not execute")
    args = parser.parse_args()

    logger = setup_logger()
    cmd = build_command(args.service, args.dry_run)
    logger.info(f"Execute: {' '.join(cmd)}")

    try:
        completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Success: returncode={completed.returncode}")
        if completed.stdout:
            logger.info(f"stdout: {completed.stdout.strip()}")
        if completed.stderr:
            logger.warning(f"stderr: {completed.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed: returncode={e.returncode}")
        logger.error(e.stderr.strip() if e.stderr else "no stderr")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
