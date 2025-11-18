#!/usr/bin/env python3
"""
Fetch a Wix page JSON manifest by capturing network traffic via Selenium + Chrome DevTools Protocol.

It opens the target page, listens for Network.responseReceived events, finds the JSON
matching a provided substring (e.g., "_115.json" or full filename), and saves its body to disk.

Usage:
  python scripts/fetch_wix_page_json.py \
    --url https://1803153.wixsite.com/grfilmphotography/121-collective-community-brain \
    --match 28d3f2_7bbb447a886c40dc2e26a6d6458cf32d_115.json \
    --out guy/page-data/121-collective-community-brain.json

Requires: selenium>=4.6 (uses Selenium Manager for chromedriver automatically)

On macOS, ensure Chrome is installed. Runs headless by default.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

from selenium import webdriver as selenium_webdriver
try:
    # Prefer selenium-wire if available (easier to read response bodies)
    from seleniumwire import webdriver as wire_webdriver  # type: ignore
    HAVE_SELENIUM_WIRE = True
except Exception:
    HAVE_SELENIUM_WIRE = False
    wire_webdriver = None  # type: ignore
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def fetch_json(url: str, match_substring: str, out_path: str, timeout: float = 40.0) -> None:
    # Enable performance logging to capture Network.* events
    # Selenium 4: set capability via Options
    # Enable performance logging to capture Network.* events
    # https://www.selenium.dev/documentation/webdriver/bidirectional/bidi_api/#capture-browser-logs

    chrome_options = Options()
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1366,850")

    driver = None
    try:
        if HAVE_SELENIUM_WIRE and wire_webdriver is not None:
            driver = wire_webdriver.Chrome(options=chrome_options)
        else:
            driver = selenium_webdriver.Chrome(options=chrome_options)
            # Enable Network domain so we can later call getResponseBody (CDP path)
            driver.execute_cdp_cmd("Network.enable", {})

        driver.get(url)
        # Give the SPA time to boot and fire network requests
        time.sleep(5)
        driver.refresh()
        time.sleep(5)

        deadline = time.time() + timeout
        response_url = None
        content = None

        if HAVE_SELENIUM_WIRE:
            # Poll selenium-wire's captured requests
            while time.time() < deadline and content is None:
                requests = getattr(driver, "requests", [])
                for req in requests:
                    try:
                        if req.response and (match_substring in (req.url or "")):
                            response_url = req.url
                            body_bytes = req.response.body or b""
                            content = body_bytes.decode("utf-8", errors="replace")
                            break
                    except Exception:
                        continue
                if content is None:
                    time.sleep(1)
            if content is None:
                raise RuntimeError(f"Did not capture a response containing '{match_substring}' within timeout")
        else:
            # CDP/performance logs path
            request_id = None
            while time.time() < deadline and request_id is None:
                # Pull performance logs incrementally
                for entry in driver.get_log("performance"):
                    try:
                        message = json.loads(entry["message"])  # str -> dict
                        msg = message.get("message", {})
                        method = msg.get("method")
                        params = msg.get("params", {})

                        if method == "Network.responseReceived":
                            resp = params.get("response", {})
                            url_seen = resp.get("url", "")
                            if match_substring in url_seen:
                                request_id = params.get("requestId")
                                response_url = url_seen
                                break
                    except Exception:
                        # Ignore malformed entries
                        continue

                if request_id is None:
                    time.sleep(1)

            if not request_id:
                raise RuntimeError(f"Did not see a response containing '{match_substring}' within timeout")

            # Fetch the response body via CDP
            body_result = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
            body = body_result.get("body", "")
            base64_encoded = body_result.get("base64Encoded", False)
            if base64_encoded:
                import base64
                body_bytes = base64.b64decode(body)
                content = body_bytes.decode("utf-8", errors="replace")
            else:
                content = body

        # Try to pretty-validate as JSON
        try:
            parsed = json.loads(content)
            content_to_write = json.dumps(parsed, indent=2, ensure_ascii=False)
        except Exception:
            # Not strict JSON? Still write whatever we captured
            content_to_write = content

        out_file = Path(out_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(content_to_write, encoding="utf-8")

        print(f"Saved JSON from {response_url} -> {out_file}")

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="Page URL to open")
    ap.add_argument("--match", required=True, help="Substring to match in response URL")
    ap.add_argument("--out", required=True, help="Output file path for the JSON body")
    ap.add_argument("--timeout", type=float, default=40.0, help="Timeout in seconds")
    args = ap.parse_args()

    try:
        fetch_json(args.url, args.match, args.out, timeout=args.timeout)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
