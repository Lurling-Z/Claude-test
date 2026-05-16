"""
麦当劳选址打分工具
=================

功能：
- 输入候选点位（中文地名 / 关键词）
- 调用高德地图 API 拉取周边 POI
- 按麦当劳选址逻辑打分输出

依赖：
- requests, pandas
- 高德地图 Web 服务 API Key

用法：
    python analyzer.py
"""

from __future__ import annotations

import os
import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import requests
import pandas as pd

from config import (
    AMAP_KEY,
    SEARCH_RADIUS,
    BENCHMARK_BRANDS,
    TRAFFIC_SOURCES,
    OUTPUT_DIR,
)


AMAP_GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"
AMAP_PLACE_TEXT_URL = "https://restapi.amap.com/v3/place/text"
AMAP_PLACE_AROUND_URL = "https://restapi.amap.com/v3/place/around"


# ---------------------------------------------------------------------------
# 一、API 调用层
# ---------------------------------------------------------------------------

def geocode(address: str, city: str = "") -> Optional[Tuple[float, float]]:
    """地名 → 经纬度。优先用 place/text，能拿到具体 POI 的中心点。"""
    params = {
        "key": AMAP_KEY,
        "keywords": address,
        "city": city,
        "citylimit": "true",
        "offset": 1,
        "page": 1,
    }
    resp = requests.get(AMAP_PLACE_TEXT_URL, params=params, timeout=10)
    data = resp.json()
    if data.get("status") == "1" and data.get("pois"):
        loc = data["pois"][0]["location"]
        lng, lat = loc.split(",")
        return float(lng), float(lat)

    # 兜底：用 geocode 接口
    params = {"key": AMAP_KEY, "address": address, "city": city}
    resp = requests.get(AMAP_GEOCODE_URL, params=params, timeout=10)
    data = resp.json()
    if data.get("status") == "1" and data.get("geocodes"):
        loc = data["geocodes"][0]["location"]
        lng, lat = loc.split(",")
        return float(lng), float(lat)
    return None


def search_around(lng: float, lat: float, keyword: str, radius: int = SEARCH_RADIUS) -> List[Dict]:
    """搜索某个点周边 N 米内的指定 POI。"""
    all_pois: List[Dict] = []
    page = 1
    while True:
        params = {
            "key": AMAP_KEY,
            "location": f"{lng},{lat}",
            "keywords": keyword,
            "radius": radius,
            "offset": 25,
            "page": page,
            "extensions": "base",
        }
        resp = requests.get(AMAP_PLACE_AROUND_URL, params=params, timeout=10)
        data = resp.json()
        if data.get("status") != "1":
            break
        pois = data.get("pois", [])
        if not pois:
            break
        all_pois.extend(pois)
        if len(pois) < 25:
            break
        page += 1
        if page > 4:  # 最多取 100 个
            break
        time.sleep(0.1)
    return all_pois


# ---------------------------------------------------------------------------
# 二、单点位调研
# ---------------------------------------------------------------------------

def survey_location(name: str, city: str, keyword: str) -> Dict:
    """对一个候选点位拉全数据。"""
    print(f"\n=== {name} ({city} - {keyword}) ===")

    coord = geocode(keyword, city)
    if coord is None:
        print("  ✗ 未找到该地点经纬度")
        return {"name": name, "city": city, "keyword": keyword, "found": False}

    lng, lat = coord
    print(f"  经纬度: {lng}, {lat}")

    result: Dict = {
        "name": name,
        "city": city,
        "keyword": keyword,
        "lng": lng,
        "lat": lat,
        "found": True,
        "benchmark_brands": {},
        "traffic_sources": {},
    }

    # 1) 标杆品牌（最重要）
    print("  [先行指标] 周边连锁餐饮：")
    for brand in BENCHMARK_BRANDS:
        pois = search_around(lng, lat, brand)
        result["benchmark_brands"][brand] = {
            "count": len(pois),
            "pois": [
                {
                    "name": p.get("name"),
                    "address": p.get("address"),
                    "distance": p.get("distance"),
                }
                for p in pois
            ],
        }
        if pois:
            print(f"    {brand:6s} × {len(pois)}  最近: {pois[0].get('name')} ({pois[0].get('distance')}m)")

    # 2) 客流来源
    print("  [客流来源]")
    for category, kws in TRAFFIC_SOURCES.items():
        total = 0
        items: List[Dict] = []
        for kw in kws:
            pois = search_around(lng, lat, kw)
            total += len(pois)
            items.extend(
                [{"name": p.get("name"), "type": kw, "distance": p.get("distance")} for p in pois]
            )
        # 去重（同名）
        seen = set()
        unique = []
        for it in items:
            if it["name"] in seen:
                continue
            seen.add(it["name"])
            unique.append(it)
        result["traffic_sources"][category] = {
            "count": len(unique),
            "items": unique[:20],
        }
        print(f"    {category:6s} × {len(unique)}")

    return result


# ---------------------------------------------------------------------------
# 三、打分逻辑
# ---------------------------------------------------------------------------

def score_location(survey: Dict) -> Dict:
    """根据 survey 数据按麦当劳选址逻辑打分。"""
    if not survey.get("found"):
        return {"total": 0, "verdict": "未找到该地点", "details": {}}

    bm = survey["benchmark_brands"]
    ts = survey["traffic_sources"]

    details = {}

    # ------ 1. 先行指标得分（满分 30）------
    # KFC 最关键
    kfc_count = bm.get("肯德基", {}).get("count", 0)
    if kfc_count >= 2:
        s_kfc = 15
    elif kfc_count == 1:
        s_kfc = 10
    else:
        s_kfc = 0
    details["KFC 已开门店"] = (s_kfc, 15, f"{kfc_count} 家")

    # 已经有麦当劳？直接淘汰
    mcd_count = bm.get("麦当劳", {}).get("count", 0)
    if mcd_count > 0:
        details["⚠️ 麦当劳已存在"] = (0, 0, f"{mcd_count} 家")

    # 中产消费力（星巴克 / 瑞幸 / 必胜客）
    starbucks = bm.get("星巴克", {}).get("count", 0)
    luckin = bm.get("瑞幸咖啡", {}).get("count", 0)
    pizza_hut = bm.get("必胜客", {}).get("count", 0)
    s_consumer = min(15, starbucks * 5 + luckin * 2 + pizza_hut * 5)
    details["中产消费力（星/瑞/必）"] = (s_consumer, 15, f"星×{starbucks} 瑞×{luckin} 必×{pizza_hut}")

    # ------ 2. 客流叠加得分（满分 40）------
    schools = ts.get("学校", {}).get("count", 0)
    s_school = min(15, schools * 3)
    details["学校"] = (s_school, 15, f"{schools} 所")

    homes = ts.get("住宅", {}).get("count", 0)
    s_home = min(15, homes // 2)
    details["住宅小区"] = (s_home, 15, f"{homes} 个")

    malls = ts.get("购物中心", {}).get("count", 0)
    s_mall = min(5, malls * 2)
    details["商场/广场"] = (s_mall, 5, f"{malls} 个")

    cinemas = ts.get("影院", {}).get("count", 0)
    s_cinema = min(5, cinemas * 3)
    details["影院"] = (s_cinema, 5, f"{cinemas} 个")

    # ------ 3. 配套设施得分（满分 10）------
    hospitals = ts.get("医院", {}).get("count", 0)
    s_hospital = min(5, hospitals)
    details["医院"] = (s_hospital, 5, f"{hospitals} 个")

    supers = ts.get("超市", {}).get("count", 0)
    s_super = min(5, supers)
    details["超市"] = (s_super, 5, f"{supers} 个")

    # ------ 4. 下沉品牌密度（满分 20）------
    # 华莱士、塔斯汀多 = 客单偏低，是负向 / 持平指标
    # 但同时也说明商圈快餐需求成立
    wallace = bm.get("华莱士", {}).get("count", 0)
    tastien = bm.get("塔斯汀", {}).get("count", 0)
    bk = bm.get("汉堡王", {}).get("count", 0)
    s_competitor = min(20, (wallace + tastien) * 3 + bk * 5)
    details["快餐竞争密度"] = (s_competitor, 20, f"华×{wallace} 塔×{tastien} BK×{bk}")

    total = sum(v[0] for v in details.values())

    # 判语
    if mcd_count > 0:
        verdict = f"❌ 麦当劳已开店，无需评估（已有 {mcd_count} 家）"
    elif kfc_count == 0 and starbucks == 0 and luckin == 0:
        verdict = f"⬜ {total}/100  商圈尚未成熟，麦当劳进店窗口期较远"
    elif kfc_count >= 1 and (starbucks + luckin) >= 1:
        verdict = f"🟥 {total}/100  先行指标齐全，麦当劳进店概率高"
    elif kfc_count >= 1:
        verdict = f"🟧 {total}/100  KFC 已开但中产指标弱，需观察"
    else:
        verdict = f"🟨 {total}/100  KFC 未开但中产指标存在，可能性中等"

    return {"total": total, "verdict": verdict, "details": details}


# ---------------------------------------------------------------------------
# 四、主流程
# ---------------------------------------------------------------------------

def main():
    if AMAP_KEY.startswith("在这里"):
        print("⚠️  请先在 config.py 里填入你的高德 API Key")
        return

    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(exist_ok=True)

    locations = pd.read_csv("locations.csv")
    surveys: List[Dict] = []
    scores: List[Dict] = []

    for _, row in locations.iterrows():
        survey = survey_location(row["name"], row["city"], row["keyword"])
        score = score_location(survey)
        surveys.append(survey)

        print(f"\n  >>> {score['verdict']}")
        for k, (got, full, note) in score["details"].items():
            bar = "█" * int(got / max(full, 1) * 10) if full else ""
            print(f"      {k:25s} {got:3d}/{full:<3d} {bar:10s} {note}")

        scores.append({
            "name": row["name"],
            "city": row["city"],
            "keyword": row["keyword"],
            "note": row["note"],
            "total": score["total"],
            "verdict": score["verdict"],
            "kfc_nearby": survey.get("benchmark_brands", {}).get("肯德基", {}).get("count", 0),
            "mcd_nearby": survey.get("benchmark_brands", {}).get("麦当劳", {}).get("count", 0),
            "starbucks_nearby": survey.get("benchmark_brands", {}).get("星巴克", {}).get("count", 0),
            "luckin_nearby": survey.get("benchmark_brands", {}).get("瑞幸咖啡", {}).get("count", 0),
            "wallace_nearby": survey.get("benchmark_brands", {}).get("华莱士", {}).get("count", 0),
            "tastien_nearby": survey.get("benchmark_brands", {}).get("塔斯汀", {}).get("count", 0),
            "schools": survey.get("traffic_sources", {}).get("学校", {}).get("count", 0),
            "homes": survey.get("traffic_sources", {}).get("住宅", {}).get("count", 0),
            "malls": survey.get("traffic_sources", {}).get("购物中心", {}).get("count", 0),
        })

    # 保存原始数据
    with open(out_dir / "raw_survey.json", "w", encoding="utf-8") as f:
        json.dump(surveys, f, ensure_ascii=False, indent=2)

    # 保存打分表
    df = pd.DataFrame(scores).sort_values("total", ascending=False)
    df.to_csv(out_dir / "scores.csv", index=False, encoding="utf-8-sig")
    df.to_markdown(out_dir / "scores.md", index=False)

    print("\n" + "=" * 70)
    print("汇总：")
    print("=" * 70)
    print(df[["name", "city", "total", "verdict"]].to_string(index=False))
    print(f"\n详细数据已写入: {out_dir.absolute()}/")
    print(f"  - raw_survey.json   原始 POI 数据")
    print(f"  - scores.csv        打分表（Excel 可打开）")
    print(f"  - scores.md         Markdown 表格")


if __name__ == "__main__":
    main()
