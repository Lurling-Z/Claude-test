# tools/ — 小红书账号数据脚本

围绕 [`xhs`](https://github.com/ReaJason/xhs) Python SDK 写的一组**免签**脚本，用于
"渊学通杭州"账号的复盘与选题分析。

> **免签 = 不需要 headless Chromium / 不需要逆向 `x-s` `x-t` 签名算法。**
> 走的是小红书页面 HTML 里内嵌的 `window.__INITIAL_STATE__`（服务端渲染数据），缺点是
> 单次只能拿到"第一屏"（约 30 条），翻页就需要走签名 API 了。

---

## 脚本一览

| 脚本 | 作用 | 是否需 cookie |
|------|------|---------------|
| `xhs_smoke.py` | 环境/连通性自检 | ❌ 否 |
| `xhs_account_dump.py` | 拉某账号主页 → 输出 CSV/JSON 报表 | ⚠️ 强烈建议有 |
| `xhs_note_enrich.py` | 给 dump 出来的 notes.csv 补全正文/标签/详情 | ⚠️ 强烈建议有 |

---

## 0. 环境准备

```bash
pip install xhs
```

仓库根目录运行 `python3 tools/xhs_smoke.py`，看到 `✅ 冒烟测试结束` 即环境就绪。

---

## 1. 拿 cookie（强烈建议）

匿名调用极易被风控。在浏览器里登录小红书，再复制 cookie：

1. Chrome / Edge 打开 [https://www.xiaohongshu.com](https://www.xiaohongshu.com)，登录
2. F12 → **Network** → 刷新页面 → 点任意一个对 `xiaohongshu.com` 的请求
3. **Headers → Request Headers → cookie**，整段复制
4. 在终端 `export XHS_COOKIE='复制的整段'`（值里有空格和分号，记得带单引号）

⚠️ Cookie 有时效（约几天到几周），过期后重新复制即可。

---

## 2. 拉账号数据

```bash
# 用 user_id（24 位 hex）
python3 tools/xhs_account_dump.py 5e1666c20000000001008cb6

# 直接贴主页 URL（带 query 参数也行）
python3 tools/xhs_account_dump.py "https://www.xiaohongshu.com/user/profile/xxxxx?xsec_token=..."

# 自定义输出目录
python3 tools/xhs_account_dump.py <user_id> -o reports/yxt-2026-05
```

输出（默认 `out/<user_id>/`）：

```
out/<user_id>/
├── account_raw.json        # 完整结构化数据，便于二次分析
├── account_summary.txt     # 人读速览（昵称/粉丝/IP 属地/简介/标签…）
└── notes.csv               # 平铺笔记表，可直接 Excel 打开
```

`notes.csv` 字段：

| 字段 | 说明 |
|------|------|
| `tab` | 来自哪个主页 tab：`posted`(笔记) / `collected`(收藏) / `liked`(赞过) / `private` |
| `note_id` | 笔记 ID |
| `type` | `normal`(图文) / `video` |
| `title` | 标题 |
| `url` | 笔记网址 |
| `liked_count`, `collected_count`, `comment_count`, `share_count` | 互动数 |
| `cover_url` | 封面图 URL |
| `xsec_token` | 笔记访问令牌（后续接口可能要用） |

---

## 3. 补全详情（可选）

`notes.csv` 里只有"主页卡片"上的简略字段。要正文、标签、IP 属地、发布时间这些，
跑 enrich：

```bash
python3 tools/xhs_note_enrich.py out/<user_id>/notes.csv
# 输出 out/<user_id>/notes_enriched.csv
```

参数：

- `--delay 2`（默认）每条之间间隔秒数，太快会被风控
- `--limit 10` 只处理前 10 条（先验证一下）
- 断点续跑：再跑同一条命令会跳过已 `enrich_status=ok` 的行

新增列：`desc`（正文）/ `ip_location` / `publish_time` / `tag_list`（`|` 分隔）/
`image_count` / `video_duration` / `enrich_status`

---

## 4. 局限

| 局限 | 说明 |
|------|------|
| **只拿首屏** | HTML SSR 给的是首屏 ~30 条，更多笔记需走签名 API（即另搭 sign server） |
| **依赖前端结构** | 小红书改前端就可能解析失败。脚本对每个字段都做了多键兜底，但不可能完全规避 |
| **风控** | 同 IP 短时间多次请求会触发 471/461 验证码或 IP 拉黑。务必带 cookie + 限速 |
| **xsec_token 时效** | 主页带的 token 是临时的，几小时后失效；要长期用得每次重新 dump |

---

## 5. 合规与法律

- 仅用于您**自有账号**或**公开数据**复盘；勿批量爬他人账号
- 抓取频率和总量谨慎控制；不得用于商业贩卖、二次分发
- 如平台规则更新，本脚本不再适用，请停用
