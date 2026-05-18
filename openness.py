#!/usr/bin/env python3
"""迅优 MZ803 国际连通性测试 - 并行检测国际网站可访问性"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
import time
import sys
import os
import json
import configparser
import ssl

# 连通性测试忽略证书验证（不是安全审查）
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

SITES = [
    ("Google",      "google.com"),
    ("YouTube",     "youtube.com"),
    ("Gmail",       "mail.google.com"),
    ("X/Twitter",   "x.com"),
    ("Instagram",   "instagram.com"),
    ("Facebook",    "facebook.com"),
    ("WhatsApp",    "whatsapp.com"),
    ("Telegram",    "telegram.org"),
    ("Signal",      "signal.org"),
    ("维基百科",    "wikipedia.org"),
    ("Reddit",      "reddit.com"),
    ("BBC",         "bbc.com"),
    ("CNN",         "cnn.com"),
    ("NY Times",    "nytimes.com"),
    ("GitHub",      "github.com"),
    ("StackOverflow","stackoverflow.com"),
    ("Cloudflare",  "cloudflare.com"),
    ("jsDelivr",    "cdn.jsdelivr.net"),
    ("React",       "react.dev"),
    ("Python",      "pypi.org"),
    ("NPM",         "npmjs.com"),
    ("Docker",      "docker.com"),
    ("Amazon S3",   "s3.amazonaws.com"),
    ("Microsoft",   "microsoft.com"),
    ("Netflix",     "netflix.com"),
]

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def test(name, domain):
    start = time.time()
    req = urllib.request.Request(
        f"https://{domain}/",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        urllib.request.urlopen(req, timeout=8, context=_ssl_ctx)
        elapsed = int((time.time() - start) * 1000)
        if elapsed > 3000:
            return (name, f"{YELLOW}⚠️ 慢{RESET}", elapsed)
        return (name, f"{GREEN}✅ 正常{RESET}", elapsed)
    except Exception:
        return (name, f"{RED}❌ 阻断{RESET}", None)


def router_req(path, data=None):
    """发送请求到路由器"""
    cfg = configparser.ConfigParser()
    cfg.read(os.path.join(os.path.dirname(__file__), "config.ini"))
    base = cfg.get("router", "url", fallback="http://192.168.100.1")
    req = urllib.request.Request(f"{base}{path}",
        data=data.encode() if data else None,
        headers={"Content-Type": "application/x-www-form-urlencoded"} if data else {})
    with urllib.request.urlopen(req, timeout=5) as f:
        return json.loads(f.read())


def get_current_apn():
    try:
        # 从 config.ini 读取密码
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(os.path.dirname(__file__), "config.ini"))
        pwd_plain = cfg.get("router", "password", fallback="")

        import base64
        pwd = base64.b64encode(pwd_plain.encode()).decode()
        router_req("/reqproc/proc_post", f"goformId=LOGIN&password={pwd}")
        # 查 APN
        data = router_req("/reqproc/proc_get?cmd=wan_apn,apn_mode&multi_data=1")
        return data.get("wan_apn", "")
    except Exception:
        return ""


def main():
    cur_apn = get_current_apn()

    print(f"\n{BOLD}国际连通性测试{RESET}")
    print("════════════════════════════════════════")
    display_apn = cur_apn if cur_apn else "未知"
    apn_color = GREEN if cur_apn else YELLOW
    print(f"当前 APN:   {apn_color}{display_apn}{RESET}")
    print()

    print(f"  {'站点':<16} {'结果':<10} {'耗时'}")
    print(f"  {'------------------------------------------'}")

    results = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(test, n, d): (n, d) for n, d in SITES}
        for f in as_completed(futures):
            results.append(f.result())

    results.sort(key=lambda x: (1 if "阻断" in x[1] else 0, x[2] or 9999))

    passed = slow = blocked = 0
    for name, status, elapsed in results:
        if "阻断" in status:
            blocked += 1
        elif "慢" in status:
            slow += 1
        else:
            passed += 1
        t = f"{elapsed}ms" if elapsed else ">8s"
        print(f"  {name:<16} {status:<8} {t}")

    print()
    print("════════════════════════════════════════")
    print(f"  {GREEN}正常{RESET} {passed}  {YELLOW}缓慢{RESET} {slow}  {RED}阻断{RESET} {blocked}  / 共 {len(results)}")

    total = len(results)
    if blocked == 0: score = 100
    elif blocked <= total * 0.1: score = 90
    elif blocked <= total * 0.25: score = 75
    elif blocked <= total * 0.4: score = 50
    elif blocked <= total * 0.6: score = 30
    elif blocked < total: score = 10
    else: score = 0

    if score >= 80: level = f"{GREEN}较开放{RESET}"
    elif score >= 50: level = f"{YELLOW}中等{RESET}"
    elif score >= 30: level = f"{RED}较严{RESET}"
    else: level = f"{RED}严格封锁{RESET}"

    print(f"  开放度评分: {score}/100 — {level}")
    print()


if __name__ == "__main__":
    main()
