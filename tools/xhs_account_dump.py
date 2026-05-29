#!/usr/bin/env python3
"""
xhs_account_dump.py
===================

拉取小红书账号主页公开数据，输出 CSV 报表（无需签名服务）。

原理:
    访问 https://www.xiaohongshu.com/user/profile/<user_id>
    页面 HTML 内嵌 ``window.__INITIAL_STATE__``，包含:
      - userPageData : 昵称/简介/粉丝数/获赞收藏数/IP 属地/标签
      - notes        : 当前用户主页 5 个 tab 的笔记列表
                       (笔记 / 合集 / 收藏 / 赞过 / 私密)
    全程走 SSR HTML，无需 x-s/x-t 签名。

用法:
    # 1) 用 user_id
    python3 tools/xhs_account_dump.py 5e1666c20000000001008cb6

    # 2) 直接贴主页 URL（带 query 参数也行，会自动提取 user_id）
    python3 tools/xhs_account_dump.py "https://www.xiaohongshu.com/user/profile/5e1666c20000000001008cb6?xsec_token=..."

    # 3) 自定义输出目录
    python3 tools/xhs_account_dump.py 5e1666c2... -o reports/yxt-2026-05

    # 4) 注入 cookie 减少风控（强烈建议；从浏览器 DevTools 复制完整 cookie 串）
    XHS_COOKIE='a1=...; web_session=...' python3 tools/xhs_account_dump.py <user_id>

输出:
    out/<user_id>/
      account_raw.json   完整结构化数据，便于后续二次分析
      account_summary.txt 一眼能看的账号概览
      notes.csv          平铺笔记表（可直接 Excel 打开）

说明 / 局限:
    - HTML SSR 通常只携带每个 tab 的"第一屏"（约 30 条）。继续翻页需要走签名 API。
    - 部分字段命名是 camelCase（前端原始字段），不同小红书前端版本可能微变。
      本脚本对每个字段都做兜底，无值时留空。
    - 仅用于您**自有账号**或**公开数据**复盘；批量爬他人数据请遵守平台规则与法规。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# 5 个 tab 的语义猜测（小红书前端固定顺序，2024 起未变动）
NOTE_TAB_NAMES = ["posted", "tab1", "collected", "liked", "private"]


# ---------------------------------------------------------------------------
# input parsing
# ---------------------------------------------------------------------------
USER_ID_RE = re.compile(r"^[0-9a-f]{16,32}$", re.IGNORECASE)


def extract_user_id(arg: str) -> str:
    """支持纯 user_id 或完整 profile URL。"""
    arg = arg.strip()
    if USER_ID_RE.match(arg):
        return arg
    parsed = urlparse(arg)
    if parsed.netloc and "xiaohongshu.com" in parsed.netloc:
        m = re.search(r"/user/profile/([0-9a-fA-F]{16,32})", parsed.path)
        if m:
            return m.group(1)
    raise SystemExit(
        f"无法识别 user_id。请传入纯 ID（24 位 hex）或完整主页 URL。\n"
        f"原始输入: {arg!r}"
    )


# ---------------------------------------------------------------------------
# HTTP fetch + INITIAL_STATE parsing
# ---------------------------------------------------------------------------
def fetch_profile_html(user_id: str, cookie: str | None) -> tuple[int, str]:
    url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    headers = {
        "user-agent": DEFAULT_UA,
        "referer": "https://www.xiaohongshu.com/",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    if cookie:
        headers["cookie"] = cookie

    print(f"GET {url}")
    resp = requests.get(url, headers=headers, timeout=20)
    print(f"  status={resp.status_code}, bytes={len(resp.content)}")
    return resp.status_code, resp.text


INITIAL_STATE_RE = re.compile(
    r"window\.__INITIAL_STATE__\s*=\s*({.*?})\s*</script>",
    re.DOTALL,
)


def parse_initial_state(html: str) -> dict[str, Any]:
    m = INITIAL_STATE_RE.search(html)
    if not m:
        raise SystemExit(
            "未在 HTML 里找到 window.__INITIAL_STATE__。可能原因:\n"
            "  - 被风控或重定向到登录页（建议注入 XHS_COOKIE）\n"
            "  - 小红书前端结构变更（脚本需更新）"
        )
    raw = m.group(1).replace("undefined", "null")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        snippet = raw[max(0, e.pos - 80) : e.pos + 80]
        raise SystemExit(
            f"INITIAL_STATE JSON 解析失败: {e}\n"
            f"附近内容: ...{snippet}..."
        )


# ---------------------------------------------------------------------------
# Note record flattening (defensive: try multiple key variants)
# ---------------------------------------------------------------------------
def _g(d: dict | None, *keys, default: Any = "") -> Any:
    """安全多键回退取值: _g(d, 'displayTitle', 'title', 'note_title')。"""
    if not isinstance(d, dict):
        return default
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


def _interact(card: dict) -> dict:
    """interactInfo 在不同前端版本下命名各异，先兜底。"""
    info = (
        _g(card, "interactInfo", "interact_info", default=None)
        or _g(card, "noteAttributes", default=None)
        or {}
    )
    if isinstance(info, list):
        # 极少数版本会是 list of {type,count}
        info = {item.get("type", ""): item.get("count", "") for item in info if isinstance(item, dict)}
    return info or {}


def flatten_note(card: dict, tab: str, owner_id: str) -> dict:
    """把一个 noteCard 元素 flatten 成 CSV 行（field 名都为 snake_case）。"""
    if not isinstance(card, dict):
        return {}
    # 部分接口包了一层 noteCard
    if "noteCard" in card and isinstance(card["noteCard"], dict):
        inner = card["noteCard"]
        # 上层可能仍持有 id / xsec_token
        merged = {**inner, **{k: v for k, v in card.items() if k != "noteCard"}}
        card = merged

    note_id = _g(card, "noteId", "note_id", "id")
    title = _g(card, "displayTitle", "title", "note_title")
    type_ = _g(card, "type", "noteType")
    cover = _g(card, "cover", default={})
    if isinstance(cover, dict):
        cover_url = _g(cover, "urlDefault", "url_default", "url", "infoList", default="")
        if isinstance(cover_url, list) and cover_url:
            cover_url = _g(cover_url[0], "url", default="")
    else:
        cover_url = cover or ""

    interact = _interact(card)
    user = _g(card, "user", default={}) or {}

    row = {
        "tab": tab,
        "note_id": note_id,
        "type": type_,
        "title": (title or "").replace("\n", " ").strip(),
        "url": f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else "",
        "liked_count": _g(interact, "likedCount", "liked_count", "liked"),
        "collected_count": _g(interact, "collectedCount", "collected_count", "collected"),
        "comment_count": _g(interact, "commentCount", "comment_count"),
        "share_count": _g(interact, "shareCount", "share_count"),
        "cover_url": cover_url,
        "owner_user_id": owner_id,
        "owner_nickname": _g(user, "nickname", "nickName", "name"),
        "xsec_token": _g(card, "xsecToken", "xsec_token"),
    }
    return row


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def write_summary(out_dir: Path, user_id: str, page_data: dict, notes_by_tab: dict[str, list]) -> Path:
    basic = page_data.get("basicInfo") or {}
    interactions = page_data.get("interactions") or []
    tags = page_data.get("tags") or []

    def find_interaction(name_suffix: str) -> str:
        for it in interactions:
            if not isinstance(it, dict):
                continue
            if name_suffix in (it.get("type", ""), it.get("name", "")):
                return str(it.get("count", ""))
        return ""

    lines = [
        f"# 小红书账号速览  (生成于 {datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')})",
        "",
        f"user_id      : {user_id}",
        f"profile_url  : https://www.xiaohongshu.com/user/profile/{user_id}",
        f"昵称         : {basic.get('nickname', '')}",
        f"小红书号     : {basic.get('redId', '')}",
        f"性别         : {basic.get('gender', '')}",
        f"IP 属地      : {basic.get('ipLocation', '')}",
        f"简介         : {(basic.get('desc') or '').strip()[:120]}",
        "",
        "互动数据:",
    ]
    if interactions:
        for it in interactions:
            if isinstance(it, dict):
                lines.append(f"  - {it.get('name','?')}: {it.get('count','')}")
    else:
        lines.append("  (无 interactions 字段，可能是匿名访问被限流)")

    lines.append("")
    lines.append("标签:")
    for t in tags:
        if isinstance(t, dict):
            lines.append(f"  - {t.get('tagType','?')}: {t.get('name','')}")
    if not tags:
        lines.append("  (无)")

    lines.append("")
    lines.append("各 tab 抓到的笔记数:")
    for tab, items in notes_by_tab.items():
        lines.append(f"  - {tab}: {len(items)}")

    summary_path = out_dir / "account_summary.txt"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return summary_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("user", help="user_id 或完整主页 URL")
    parser.add_argument("-o", "--out-dir", default=None, help="输出目录（默认 out/<user_id>）")
    args = parser.parse_args()

    user_id = extract_user_id(args.user)
    cookie = os.environ.get("XHS_COOKIE")

    out_dir = Path(args.out_dir or f"out/{user_id}")
    out_dir.mkdir(parents=True, exist_ok=True)

    status, html = fetch_profile_html(user_id, cookie)
    if status >= 400:
        print(f"⚠️  HTTP {status}（账号不存在/已注销/被风控均会落到 4xx）。仍尝试解析 INITIAL_STATE …")

    state = parse_initial_state(html)
    user_state = state.get("user") or {}
    page_data = user_state.get("userPageData") or {}

    # 整体保存原始数据
    raw_path = out_dir / "account_raw.json"
    raw_path.write_text(
        json.dumps(
            {
                "_meta": {
                    "user_id": user_id,
                    "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "http_status": status,
                    "cookie_attached": bool(cookie),
                },
                "userPageData": page_data,
                "notes": user_state.get("notes"),
                "noteQueries": user_state.get("noteQueries"),
                "follow": user_state.get("follow"),
                "userInfo": user_state.get("userInfo"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # 平铺 notes -> CSV
    notes_root = user_state.get("notes") or []
    notes_by_tab: dict[str, list] = {}

    for idx, sub in enumerate(notes_root):
        if not isinstance(sub, list):
            continue
        tab = NOTE_TAB_NAMES[idx] if idx < len(NOTE_TAB_NAMES) else f"tab{idx}"
        notes_by_tab[tab] = sub

    csv_path = out_dir / "notes.csv"
    fieldnames = [
        "tab",
        "note_id",
        "type",
        "title",
        "url",
        "liked_count",
        "collected_count",
        "comment_count",
        "share_count",
        "cover_url",
        "owner_user_id",
        "owner_nickname",
        "xsec_token",
    ]
    total = 0
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:  # utf-8-sig: Excel 友好
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for tab, items in notes_by_tab.items():
            for card in items:
                row = flatten_note(card, tab, user_id)
                if row.get("note_id"):
                    writer.writerow(row)
                    total += 1

    # 摘要
    summary_path = write_summary(out_dir, user_id, page_data, notes_by_tab)

    print()
    print("=" * 60)
    print(f"✅ 完成。输出目录: {out_dir.resolve()}")
    print(f"  - {raw_path.name:25s}  完整结构化数据")
    print(f"  - {summary_path.name:25s}  账号概览（人读）")
    print(f"  - {csv_path.name:25s}  {total} 条笔记")
    if total == 0:
        print()
        print("⚠️  CSV 为空。可能原因:")
        print("   1) 该账号没有公开笔记")
        print("   2) 被风控 / 需要登录态 → 设置 XHS_COOKIE 后重试")
        print("   3) 前端结构变了 → 检查 account_raw.json 看 notes 字段实际形态")


if __name__ == "__main__":
    main()
