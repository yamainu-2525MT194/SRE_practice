#!/usr/bin/env python3
"""
最小構成のヘルスチェック:
60秒ごとにURLを叩き、結果をカラー表示してログにも残す
"""
import time, logging, requests
from rich.console import Console

URL   = "https://httpbin.org/status/200"   # ← 後で自分のサービスURLに置換
INTERVAL = 60

# ロガー設定
logging.basicConfig(filename="health.log",
                    format="%(asctime)s %(levelname)s %(message)s",
                    level=logging.INFO)
console = Console()

while True:
    try:
        r = requests.get(URL, timeout=3)
        ok = (r.status_code == 200)
    except requests.RequestException as e:
        ok = False
        logging.error(f"request failed: {e}")

    if ok:
        console.print(f"[green]UP[/green] {URL}")
        logging.info("UP")
    else:
        console.print(f"[red]DOWN[/red] {URL}")
        logging.warning("DOWN")

    time.sleep(INTERVAL)
