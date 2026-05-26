#!/usr/bin/env python3
"""
xhs_note_enrich.py
==================

读 ``notes.csv``（由 ``xhs_account_dump.py`` 生成），对每条笔记调用
``XhsClient.get_note_by_id_from_html`` 拉详细数据（正文/tag/完整互动数）。

走的是 HTML SSR，**不需要签名服务**。

用法:
    # 默认: out/<user_id>/notes.csv -> out/<user_id>/notes_enriched.csv
    python3 tools/xhs_note_enrich.py out/<user_id>/notes.csv

    # 自定义输出
    python3 tools/xhs_note_enrich.py notes.csv -o notes_enriched.csv

    # 限速（默认 2 秒/条；过快易被风控）
    python3 tools/xhs_note_enrich.py notes.csv --delay 3

    # 注入 cookie（强烈建议）
    XHS_COOKIE='a1=...; web_session=...' python3 tools/xhs_note_enrich.py notes.csv

特性:
    - 断点续跑: 输出已存在时，跳过已 enriched 的 note_id
    - 软失败: 单条出错只打印告警、继续下一条；最终汇总失败数
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from pathlib import Path
from typing import Any

# 让脚本能在 repo 根目录直接 python3 tools/xhs_note_enrich.py 运行
try:
    from xhs import XhsClient
    from xhs.exception import DataFetchError, IPBlockError
except ImportError:
    print("❌ 未安装 xhs 包，先 `pip install xhs`")
    sys.exit(1)


EXTRA_COLUMNS = [
    "desc",
    "ip_location",
    "publish_time",
    "last_update_time",
    "tag_list",
    "image_count",
    "video_duration",
    "enrich_status",
]


def load_existing(path: Path) -> dict[str, dict]:
    """已 enriched 的输出，按 note_id 索引。"""
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            nid = row.get("note_id")
            if nid and row.get("enrich_status") == "ok":
                out[nid] = row
    return out


def fmt_tags(note: dict) -> str:
    tags = note.get("tag_list") or note.get("tagList") or []
    names = []
    for t in tags:
        if isinstance(t, dict):
            n = t.get("name") or t.get("tagName") or t.get("title")
            if n:
                names.append(n)
        elif isinstance(t, str):
            names.append(t)
    return "|".join(names)


def enrich_one(client: XhsClient, note_id: str) -> dict[str, Any]:
    note = client.get_note_by_id_from_html(note_id)
    interact = note.get("interact_info") or note.get("interactInfo") or {}
    image_list = note.get("image_list") or note.get("imageList") or []
    video = note.get("video") or {}
    duration = ""
    if isinstance(video, dict):
        cap = video.get("capa") or video.get("media", {}).get("video", {})
        if isinstance(cap, dict):
            duration = cap.get("duration", "")

    return {
        "desc": (note.get("desc") or "").replace("\r", " ").replace("\n", " ").strip(),
        "ip_location": note.get("ip_location") or note.get("ipLocation") or "",
        "publish_time": note.get("time") or "",
        "last_update_time": note.get("last_update_time") or note.get("lastUpdateTime") or "",
        "tag_list": fmt_tags(note),
        "image_count": len(image_list) if isinstance(image_list, list) else "",
        "video_duration": duration,
        # 可选: 用 detail 接口的更准互动数覆盖（如果上一阶段拿到的是 0/空）
        "_liked_count_detail": interact.get("liked_count") or interact.get("likedCount", ""),
        "_collected_count_detail": interact.get("collected_count") or interact.get("collectedCount", ""),
        "_comment_count_detail": interact.get("comment_count") or interact.get("commentCount", ""),
        "_share_count_detail": interact.get("share_count") or interact.get("shareCount", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_csv", help="xhs_account_dump 输出的 notes.csv 路径")
    parser.add_argument("-o", "--out", default=None, help="输出 CSV（默认同目录 notes_enriched.csv）")
    parser.add_argument("--delay", type=float, default=2.0, help="每条之间的间隔秒数（默认 2）")
    parser.add_argument("--limit", type=int, default=0, help="最多处理多少条（0=不限）")
    args = parser.parse_args()

    in_path = Path(args.input_csv)
    if not in_path.exists():
        sys.exit(f"❌ 输入文件不存在: {in_path}")

    out_path = Path(args.out) if args.out else in_path.with_name("notes_enriched.csv")

    # 读输入
    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        in_rows = list(reader)
        in_fields = reader.fieldnames or []
    print(f"输入: {in_path}  共 {len(in_rows)} 行")

    # 续跑：已有的 enriched 行
    existing = load_existing(out_path)
    if existing:
        print(f"  断点续跑: 跳过已完成 {len(existing)} 行")

    cookie = os.environ.get("XHS_COOKIE")
    client = XhsClient(cookie=cookie, timeout=20)
    print(f"  cookie: {'是' if cookie else '否（匿名，更易被风控）'}")
    print(f"  延时:   {args.delay}s/条")
    print()

    # 准备输出
    fieldnames = list(dict.fromkeys(in_fields + EXTRA_COLUMNS))
    out_rows: list[dict] = []

    n_ok = n_skip = n_fail = 0
    for i, row in enumerate(in_rows, 1):
        note_id = row.get("note_id", "").strip()
        if not note_id:
            row["enrich_status"] = "no_note_id"
            out_rows.append(row)
            continue

        if note_id in existing:
            out_rows.append(existing[note_id])
            n_skip += 1
            continue

        if args.limit and (n_ok + n_fail) >= args.limit:
            row["enrich_status"] = "limit_skipped"
            out_rows.append(row)
            continue

        print(f"[{i}/{len(in_rows)}] {note_id}  {(row.get('title') or '')[:40]}")
        try:
            extra = enrich_one(client, note_id)
            row.update({k: v for k, v in extra.items() if not k.startswith("_")})
            row["enrich_status"] = "ok"
            n_ok += 1
        except IPBlockError:
            print(f"   ❌ IP 被风控，提前停止。已完成 {n_ok}，失败 {n_fail}。")
            row["enrich_status"] = "ip_block"
            n_fail += 1
            out_rows.append(row)
            break
        except DataFetchError as e:
            print(f"   ⚠️  解析失败: {str(e)[:120]}")
            row["enrich_status"] = "data_fetch_error"
            n_fail += 1
        except Exception as e:
            print(f"   ⚠️  {type(e).__name__}: {e}")
            row["enrich_status"] = f"err:{type(e).__name__}"
            n_fail += 1

        out_rows.append(row)
        if args.delay > 0 and i < len(in_rows):
            time.sleep(args.delay)

    # 写输出
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out_rows)

    print()
    print("=" * 60)
    print(f"✅ 输出: {out_path.resolve()}")
    print(f"   成功: {n_ok}   续跑跳过: {n_skip}   失败: {n_fail}")


if __name__ == "__main__":
    main()
