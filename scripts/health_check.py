#!/usr/bin/env python3
"""
最小構成のヘルスチェック:
60秒ごとにURLを叩き、結果をカラー表示してログにも残す
"""
import time, logging, requests, subprocess, sys
from pathlib import Path
from rich.console import Console

# === 監視設定 ===
URL   = "http://localhost:8080/health"   # ← 後で自分のサービスURLに置換
INTERVAL = 30                              #秒
THRESHOLD     = 5                                 # 連続失敗で再起動
SERVICE_NAME  = "nginx"                    # restart_service.py へ渡す

# === ログ設定 ===
LOG_DIR  = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(filename=LOG_DIR / "health.log",
                    format="%(asctime)s %(levelname)s %(message)s",
                    level=logging.INFO)
console = Console()

# === restart_service.py のパス ===
SCRIPT_ROOT     = Path(__file__).resolve().parents[1]
RESTART_SCRIPT  = SCRIPT_ROOT / "scripts" / "restart_service.py"

fails = 0

while True:
    try:
        r = requests.get(URL, timeout=3)
        healthy = (r.status_code == 200)
    except requests.RequestException as e:
        healthy = False
        logging.error(f"request failed: {e}")

    if healthy:
        fails = 0
        console.print(f"[green]UP[/green] {URL}")
        logging.info("UP")
    else:
        fails += 1
        console.print(f"[red]DOWN ({fails}/{THRESHOLD})[/red] {URL}")
        logging.warning("DOWN")

    # ----------- 自動再起動ロジック -----------
    if fails >= THRESHOLD:
        console.print(f"[yellow]Restarting {SERVICE_NAME}...[/yellow]")
        logging.warning(f"Trigger restart ({SERVICE_NAME})")

        completed = subprocess.run(
            [sys.executable, RESTART_SCRIPT, SERVICE_NAME],
            capture_output=True, text=True
        )

        if completed.returncode == 0:
            console.print(f"[cyan]Restart success[/cyan]")
            logging.info(f"Restart OK: {completed.stdout.strip()}")
            fails = 0          # 成功したのでカウンタをリセット
        else:
            console.print(f"[bold red]Restart failed[/bold red]")
            logging.error(f"Restart NG rc={completed.returncode}")
            logging.error(completed.stderr.strip())

    time.sleep(INTERVAL)
