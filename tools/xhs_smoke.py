#!/usr/bin/env python3
"""
xhs SDK 冒烟测试脚本
====================

用法:
    # 1) 仅做环境/连通性自检（不抓真实笔记，最安全）
    python3 tools/xhs_smoke.py

    # 2) 抓取指定笔记的免签 HTML 数据，打印摘要
    python3 tools/xhs_smoke.py <note_id>

    # 3) 同上，但额外用 cookie（避免风控、拿到完整字段）
    XHS_COOKIE="a1=...; web_session=..." python3 tools/xhs_smoke.py <note_id>

note_id 是小红书笔记 URL 中 /explore/ 后那一段，例如:
    https://www.xiaohongshu.com/explore/64xxxxxxxxxxx
                                         ^^^^^^^^^^^^^
"""

from __future__ import annotations

import json
import os
import sys
from textwrap import shorten


def banner(title: str) -> None:
    bar = "=" * 60
    print(f"\n{bar}\n{title}\n{bar}")


def step1_import() -> str:
    banner("STEP 1 / 导入 xhs 模块")
    import xhs

    version = getattr(xhs, "__version__", "unknown")
    print(f"  xhs 版本     : {version}")
    print(f"  模块路径     : {xhs.__file__}")
    return version


def step2_init():
    banner("STEP 2 / 初始化 XhsClient")
    from xhs import XhsClient

    cookie = os.environ.get("XHS_COOKIE")
    client = XhsClient(cookie=cookie, timeout=15)
    print(f"  cookie 注入  : {'是' if cookie else '否（匿名模式，仅免签接口可用）'}")
    print(f"  user-agent  : {shorten(client.user_agent or '<default>', width=80)}")
    return client


def step3_connectivity(client) -> None:
    banner("STEP 3 / 网络连通性自检")
    try:
        resp = client.session.get(
            "https://www.xiaohongshu.com/",
            headers={"user-agent": client.user_agent},
            timeout=10,
        )
        print(f"  GET https://www.xiaohongshu.com/  ->  {resp.status_code}")
        print(f"  响应字节数  : {len(resp.content)}")
        if resp.status_code >= 400:
            print("  ⚠️  状态码异常，可能被风控或网络不通。")
    except Exception as e:
        print(f"  ❌ 连通性失败: {type(e).__name__}: {e}")
        sys.exit(2)


def step4_fetch_note(client, note_id: str) -> None:
    banner(f"STEP 4 / 抓取笔记 {note_id}（免签 HTML 路径）")
    from xhs import DataFetchError, IPBlockError

    try:
        note = client.get_note_by_id_from_html(note_id)
    except IPBlockError:
        print("  ❌ 被风控（IP block）。建议挂代理 / 注入有效 cookie 后重试。")
        sys.exit(3)
    except DataFetchError as e:
        print(f"  ❌ 解析失败: {shorten(str(e), width=200)}")
        sys.exit(4)
    except Exception as e:
        print(f"  ❌ 未知异常: {type(e).__name__}: {e}")
        sys.exit(5)

    title = note.get("title") or "(无标题)"
    desc = note.get("desc") or ""
    interact = note.get("interact_info") or {}
    user = note.get("user") or {}

    print(f"  标题        : {shorten(title, width=80)}")
    print(f"  作者        : {user.get('nickname')} (id={user.get('user_id')})")
    print(f"  发布时间    : {note.get('time')}")
    print(f"  类型        : {note.get('type')}")
    print(f"  点赞 / 收藏 / 评论 / 分享:")
    print(
        f"              {interact.get('liked_count')} / "
        f"{interact.get('collected_count')} / "
        f"{interact.get('comment_count')} / "
        f"{interact.get('share_count')}"
    )
    print(f"  正文摘要    : {shorten(desc, width=120)}")
    print()
    print("  完整字段（前 800 字符）:")
    print("  " + shorten(json.dumps(note, ensure_ascii=False), width=800))


def main() -> None:
    step1_import()
    client = step2_init()
    step3_connectivity(client)

    if len(sys.argv) >= 2:
        step4_fetch_note(client, sys.argv[1])
    else:
        banner("跳过 STEP 4（未传入 note_id）")
        print("  用法: python3 tools/xhs_smoke.py <note_id>")

    banner("✅ 冒烟测试结束")


if __name__ == "__main__":
    main()
