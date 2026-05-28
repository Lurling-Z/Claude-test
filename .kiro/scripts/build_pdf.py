"""Generate 个人规则 1.0 PDF following 渊学通 internal PDF format rules."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)

# Register CJK fonts
import os
_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'fonts')
pdfmetrics.registerFont(TTFont('NotoSC', os.path.join(_FONT_DIR, 'NotoSansSC-Regular.ttf')))
pdfmetrics.registerFont(TTFont('NotoSC-Bold', os.path.join(_FONT_DIR, 'NotoSansSC-Bold.ttf')))

# Brand colors (matching the visual rules)
RED = HexColor('#D9302C')
BLACK = HexColor('#1A1A1A')
YELLOW = HexColor('#FFD835')
GRAY = HexColor('#666666')
LIGHTGRAY = HexColor('#E5E5E5')

# Styles
title_style = ParagraphStyle(
    'Title', fontName='NotoSC-Bold', fontSize=32, leading=44,
    alignment=TA_CENTER, textColor=BLACK, spaceAfter=18,
)
subtitle_style = ParagraphStyle(
    'Subtitle', fontName='NotoSC', fontSize=14, leading=22,
    alignment=TA_CENTER, textColor=GRAY, spaceAfter=12,
)
meta_style = ParagraphStyle(
    'Meta', fontName='NotoSC', fontSize=10, leading=16,
    alignment=TA_CENTER, textColor=GRAY,
)
h1_style = ParagraphStyle(
    'H1', fontName='NotoSC-Bold', fontSize=18, leading=28,
    textColor=RED, spaceBefore=8, spaceAfter=12,
)
h2_style = ParagraphStyle(
    'H2', fontName='NotoSC-Bold', fontSize=13, leading=22,
    textColor=BLACK, spaceBefore=10, spaceAfter=6,
)
body_style = ParagraphStyle(
    'Body', fontName='NotoSC', fontSize=10.5, leading=18,
    textColor=BLACK, spaceAfter=4,
)
note_style = ParagraphStyle(
    'Note', fontName='NotoSC', fontSize=9.5, leading=15,
    textColor=GRAY, leftIndent=16, spaceAfter=4,
)
toc_item_style = ParagraphStyle(
    'TOC', fontName='NotoSC', fontSize=12, leading=24, textColor=BLACK,
)
divider_style = ParagraphStyle(
    'Div', fontName='NotoSC', fontSize=10, leading=14,
    alignment=TA_CENTER, textColor=GRAY, spaceBefore=8, spaceAfter=8,
)
DIV = '———————————————————————————'


def P(text, style=body_style):
    return Paragraph(text.replace('\n', '<br/>'), style)

def divider():
    return Paragraph(DIV, divider_style)

# ============ CONTENT ============

COVER = [
    Spacer(1, 6*cm),
    P('个人规则 1.0', title_style),
    P('小红书运营 · 内部沉淀手册', subtitle_style),
    Spacer(1, 1*cm),
    P('—— 来自 渊学通杭州 主号 + Carol 矩阵号 ——', subtitle_style),
    Spacer(1, 7*cm),
    P('版本 &nbsp;&nbsp; v1.0', meta_style),
    P('日期 &nbsp;&nbsp; 2026年5月', meta_style),
    P('适用 &nbsp;&nbsp; 内部 SOP / 不对外', meta_style),
]

TOC = [
    P('目 录', h1_style),
    Spacer(1, 0.5*cm),
    P('一、品牌定位与账号矩阵', toc_item_style),
    P('二、撰文核心约束（零容忍清单）', toc_item_style),
    P('三、人设守则', toc_item_style),
    P('四、内容生产 SOP', toc_item_style),
    P('五、视觉规范', toc_item_style),
    P('六、发布与互动节奏', toc_item_style),
    P('七、技术工具栈', toc_item_style),
    P('八、拆解-复写工作流', toc_item_style),
    P('九、数据评估指标', toc_item_style),
    P('十、文档与版本管理', toc_item_style),
]

# Section 1
S1 = [
    P('一、品牌定位与账号矩阵', h1_style),
    divider(),
    P('（1）双账号定位', h2_style),
    P('主号「渊学通杭州」&nbsp;&nbsp;= 机构集体身份，"我们"口吻，已认证专业号', body_style),
    P('矩阵号「Carol的国际生观察」&nbsp;&nbsp;= 个人 IP / 观察者 / 陪跑顾问视角', body_style),
    Spacer(1, 0.3*cm),
    P('（2）品牌核心调性', h2_style),
    P('陪伴 · 结果导向 · 反鸡血 · 国际生家庭友好', body_style),
    P('核心精神（可化用，不必逐字搬）：用环境把人托起来', body_style),
    Spacer(1, 0.3*cm),
    P('（3）目标用户画像', h2_style),
    P('国际课程在读生（A-Level / IGCSE / AP / IB）', body_style),
    P('中产及以上家庭，"家长焦虑 + 孩子执行力不足"画像', body_style),
    P('地理重心：杭州本地 + 暑假封闭营全国生源', body_style),
    Spacer(1, 0.3*cm),
    P('（4）矩阵协同动线', h2_style),
    P('Carol 号涨粉 / 种草 → 自然引流主号 → 主号承接咨询与转化', body_style),
    P('两号不互相 @、不互相评论吹捧（避免被识别为关联营销号）', body_style),
]


# Section 2
S2 = [
    P('二、撰文核心约束（零容忍清单）', h1_style),
    divider(),
    P('（1）平台与字数规则', h2_style),
    P('小红书正文 ≤ 1000 字符（含话题、空行、标点）', body_style),
    P('小红书标题 ≤ 20 字，前 2 行决定打开率', body_style),
    P('公众号长文不限，首屏 200 字内必须有钩子', body_style),
    P('内部 PDF：A4 / 目录 + 章节 + 末页', body_style),
    P('对外 PDF：A4 / 封面 + 正文 + 联系页', body_style),
    Spacer(1, 0.3*cm),
    P('（2）禁用句式（零容忍）', h2_style),
    P('1. 不是……而是……（含变体：不是……，是……；不只……更是……）', body_style),
    P('2. 你以为……其实……', body_style),
    P('3. 很多人都不知道……', body_style),
    P('4. 看完这篇就够了', body_style),
    P('5. 狠狠拿捏', body_style),
    P('替代思路：用具体场景、画面、数据替代修辞反差', note_style),
    Spacer(1, 0.3*cm),
    P('（3）AI 味高频词清单（能不用就不用）', h2_style),
    P('副词类：其实 / 本身 / 往往 / 说到底 / 真正的 / 严格意义上', body_style),
    P('升华万能句：本质上 / 更像是 / 比 XX 重要得多 / 才是关键', body_style),
    P('万能转折：但同时 / 话说回来 / 与此同时 / 不仅如此', body_style),
    P('抽象黑话：赋能 / 闭环 / 抓手 / 心智 / 颗粒度 / 沉淀', body_style),
    Spacer(1, 0.3*cm),
    P('（4）结构与节奏限量', h2_style),
    P('升华句通篇 ≤ 1 处', body_style),
    P('工整四件套（4 项顿号并列堆叠）通篇 ≤ 1 处', body_style),
    P('小红书帖内 "———" 分隔线 ≤ 3 处', body_style),
    P('感叹号克制、书名号克制；问号留给真问题', body_style),
    Spacer(1, 0.3*cm),
    P('（5）表达基线', h2_style),
    P('第一人称用"我 / 我们"，不做旁观者解说', body_style),
    P('段落长短刻意不一，避免每段对称', body_style),
    P('数字优先于形容词："3 天没睡好" 比 "非常疲惫" 有力', body_style),
    P('真实素材最佳；无真实素材不要硬编', body_style),
]

# Section 3
S3 = [
    P('三、人设守则', h1_style),
    divider(),
    P('（1）矩阵号 Carol 七条语言守则', h2_style),
    P('要这样写 →&nbsp;&nbsp; 我陪过 200+ 国际生家庭', body_style),
    P('不这样写 →&nbsp;&nbsp; 我自己当年……', note_style),
    P('要这样写 →&nbsp;&nbsp; 她当时跟我说……', body_style),
    P('不这样写 →&nbsp;&nbsp; 我当时觉得……', note_style),
    P('要这样写 →&nbsp;&nbsp; 客观说，这种做法的代价是……', body_style),
    P('不这样写 →&nbsp;&nbsp; 千万别这样！', note_style),
    P('要这样写 →&nbsp;&nbsp; 陪跑第 187 天，我陪她走到考场……', body_style),
    P('不这样写 →&nbsp;&nbsp; 脱产第 187 天，我交卷……', note_style),
    Spacer(1, 0.3*cm),
    P('一句话原则：永远站在学生 / 家长 身边，不是身上', body_style),
    Spacer(1, 0.3*cm),
    P('（2）官号视角', h2_style),
    P('用 "我们带过……" "我们老师批改时……" 表达机构集体经验', body_style),
    P('避免 "我自己……" 这种过度个人化的表述', body_style),
    P('"我" 可以保留作为撰稿者口吻，但不超过 3 处', body_style),
    Spacer(1, 0.3*cm),
    P('（3）人设禁忌（写完前自查）', h2_style),
    P('同一篇文章不允许同时出现 学生视角 + 顾问视角', body_style),
    P('避免"老师 / 学员提分案例 / 免费试听"等机构宣传词', body_style),
    P('避免"早鸟价 / 限时 / 现在抢占名额"等硬广用语', body_style),
]


# Section 4
S4 = [
    P('四、内容生产 SOP', h1_style),
    divider(),
    P('（1）冷启动期（前 10 篇）铁律', h2_style),
    P('人设 / 赛道 / 视觉 三件套必须统一', body_style),
    P('赛道宁愿少，不要广。例：A-Level 国际课程 为主，雅思为辅', body_style),
    P('数据差的笔记可删，前 5 篇决定算法初始权重', body_style),
    Spacer(1, 0.3*cm),
    P('（2）选题套路（5 类轮换）', h2_style),
    P('1. 复盘叙事型：陪跑 X 天 + 数字 + 时间留白', body_style),
    P('2. 观察清单型：观察 N 个家庭 + 误区数 + 序号强调', body_style),
    P('3. 时间焦虑型：错过 X 个节点 + 反常识时间提示', body_style),
    P('4. 反常识型：A 和 B 的差距不在 C，在 D（注意句式合规改写）', body_style),
    P('5. 转化导向型：避坑清单 / 5 问 / 标准对照（前 4 篇铺信任后再发）', body_style),
    Spacer(1, 0.3*cm),
    P('（3）单篇结构', h2_style),
    P('开篇：场景钩子（具体到分钟、动作、对话）', body_style),
    P('中段：3 个真实节点 / 数字 + 操作细节 + 1 句观察', body_style),
    P('尾段：1 句核心观察 + 1 句标题钩子闭环', body_style),
    P('收尾：评论区互动钩子（三选一格式 / 关键词留资）', body_style),
    Spacer(1, 0.3*cm),
    P('（4）标题工厂', h2_style),
    P('结构：垂直品类 + 数字钩子 + 罕见 emoji（可选）+ 信任标签', body_style),
    P('优秀标题元素：具体数字、时间留白、反常识、避坑、3 件 / 5 件', body_style),
    P('避免：标题党不闭环（承诺 7 个字 → 正文必须真的是 7 个字）', body_style),
    Spacer(1, 0.3*cm),
    P('（5）标签矩阵', h2_style),
    P('每篇 10—12 个，必须三类混合：', body_style),
    P('宽词（流量池）：#国际生 #国际课程 #国际生家长', body_style),
    P('精准搜索词（搜索权重）：#A-Level #爱德思 #雅思6.5 #ALevel陪读', body_style),
    P('品牌 / 同城词（沉淀）：#渊学通 #杭州雅思 #杭州国际生', body_style),
]

# Section 5
S5 = [
    P('五、视觉规范', h1_style),
    divider(),
    P('（1）配色（4 色 + 1 底）', h2_style),
    P('主红 #D9302C&nbsp;&nbsp;&nbsp;&nbsp; 主黑 #1A1A1A', body_style),
    P('强调黄 #FFD835&nbsp;&nbsp;&nbsp;&nbsp; 灰字 #666666&nbsp;&nbsp;&nbsp;&nbsp; 白底', body_style),
    P('10 篇内不允许换色，色号即视觉锤', note_style),
    Spacer(1, 0.3*cm),
    P('（2）字体', h2_style),
    P('主标题：阿里巴巴普惠体 Heavy / 思源黑体 Heavy', body_style),
    P('正文：思源黑体 Regular', body_style),
    Spacer(1, 0.3*cm),
    P('（3）封面模板', h2_style),
    P('上：红黑大字主标题 + 副标题', body_style),
    P('中：4—6 项列表，第 3 项用 ⚠️ / 红圈强调（眼球停留点）', body_style),
    P('下：红色色块 + 白字角标，如 [建议先收藏] / [家长必看] / [避坑清单]', body_style),
    Spacer(1, 0.3*cm),
    P('（4）图卡数量与节奏', h2_style),
    P('短笔记：6 图（封面 + 4 干货 + 1 收尾）', body_style),
    P('长笔记：12 图（封面 + 总思路 + 干货群 + 中场休息 + 收尾）', body_style),
    P('中场休息卡：大留白，字号最大，单 emoji 点缀', body_style),
    Spacer(1, 0.3*cm),
    P('（5）图卡内排版', h2_style),
    P('每张卡 30—150 字最易扫读', body_style),
    P('一张卡只传一个核心点', body_style),
    P('图卡内不要用 "———" 分隔线（视觉太重，用空行代替）', body_style),
]


# Section 6
S6 = [
    P('六、发布与互动节奏', h1_style),
    divider(),
    P('（1）发布时间', h2_style),
    P('家长向：周日 / 周一 / 周三 / 周五 19:30—21:00', body_style),
    P('考生向：周二 / 周四 21:00—23:00', body_style),
    P('避开：工作日早高峰、周末上午（家长带娃没空刷）', body_style),
    Spacer(1, 0.3*cm),
    P('（2）必须打卡的位置', h2_style),
    P('地理标签强制选「杭州」或具体杭州地标', body_style),
    P('IP 属地必须显示「浙江」（确保用国内网络 / SIM 登录过）', body_style),
    Spacer(1, 0.3*cm),
    P('（3）发布后 30 分钟内三件事', h2_style),
    P('1. 主号在评论区留首条「真问题」破冰评论', body_style),
    P('2. 任何评论必回，30 分钟内响应（早期账号互动权重）', body_style),
    P('3. 私信回复必须有钩子（"评论关键词，私信发资料"）', body_style),
    Spacer(1, 0.3*cm),
    P('（4）数据观察节点', h2_style),
    P('发布 1 小时：曝光 ≥ 500 → 通过初推', body_style),
    P('发布 6 小时：互动 ≥ 10 → 进二级流量池', body_style),
    P('发布 24 小时：核心搜索词排位 → 进搜索流量池', body_style),
    Spacer(1, 0.3*cm),
    P('（5）评论区分类话术', h2_style),
    P('问 "在哪 / 怎么联系" → "主页有详细介绍，或者私信聊"', body_style),
    P('问具体备考问题 → 详细回答 + "私信发你 X 清单"', body_style),
    P('情感共鸣评论 → 用真诚陪伴语气回，不带销售', body_style),
]

# Section 7
S7 = [
    P('七、技术工具栈', h1_style),
    divider(),
    P('（1）xhs CLI（小红书命令行工具）', h2_style),
    P('安装：uv tool install xiaohongshu-cli', body_style),
    P('登录：xhs login --cookie-source chrome（或 --qrcode）', body_style),
    P('账号信息：xhs whoami --yaml', body_style),
    P('读笔记：xhs read &lt;URL 或 ID&gt;', body_style),
    P('注意：登录前完全退出 Chrome，否则 cookie 数据库被锁', note_style),
    Spacer(1, 0.3*cm),
    P('（2）目录约定', h2_style),
    P('.kiro/steering/&nbsp;&nbsp;&nbsp;&nbsp; 长期生效的规范文件（auto 加载）', body_style),
    P('.kiro/drafts/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 笔记草稿，不进 git', body_style),
    P('.kiro/scripts/&nbsp;&nbsp;&nbsp;&nbsp; 自动化脚本（PDF 生成、合规校验）', body_style),
    Spacer(1, 0.3*cm),
    P('（3）合规自动校验脚本', h2_style),
    P('扫描项：字符数 / 禁用句式 / AI 高频词 / 升华句 / 分隔线 / 工整四件套 / 标签数', body_style),
    P('使用：写完笔记保存到 .kiro/drafts/，跑脚本，全绿才输出', body_style),
    P('必须达成的硬指标：禁用句式 = 0、字符数 ≤ 1000、标签 10—12', body_style),
    Spacer(1, 0.3*cm),
    P('（4）拆解原帖的工具链', h2_style),
    P('短链解析：curl -sIL（拿真实 URL）', body_style),
    P('页面抓取：curl + UA 伪装 → 提取 meta description / title', body_style),
    P('图卡内容：xhs read（需登录）', body_style),
]


# Section 8
S8 = [
    P('八、拆解-复写工作流', h1_style),
    divider(),
    P('（1）八步法', h2_style),
    P('1. 抓取原帖（短链解析 → 真实 URL → 抓取 HTML）', body_style),
    P('2. 拆解 4 维：标题结构 / desc 段落作用 / 人设视角 / 钩子机制', body_style),
    P('3. 列「可借鉴 / 不可借鉴」对照表', body_style),
    P('4. 视角迁移（学生 → 观察者 / 个人 → 集体）', body_style),
    P('5. 起草：开篇钩子 → 中段 3 节点 → 尾段闭环 → 互动收尾', body_style),
    P('6. 跑合规校验脚本', body_style),
    P('7. 修复违约束点（必含「改了什么 + 为什么」对照表）', body_style),
    P('8. 终稿 + 配图建议 + 发布参数', body_style),
    Spacer(1, 0.3*cm),
    P('（2）视角迁移规则', h2_style),
    P('原帖学生视角 → 我们的观察 / 陪跑视角', body_style),
    P('原帖鬼畜玩梗 → 克制陪伴感（不照搬幽默风）', body_style),
    P('原帖个人体验 → 集体经验数据（"我陪过 30 个" / "我们带过几百个"）', body_style),
    Spacer(1, 0.3*cm),
    P('（3）允许借的、必须改的', h2_style),
    P('允许借：标题结构、信任钩子、用户筛选、系列预告、视觉模板', body_style),
    P('必须改：人称、玩梗强度、销售信号、与品牌冲突的调性', body_style),
]

# Section 9
S9 = [
    P('九、数据评估指标', h1_style),
    divider(),
    P('（1）健康互动率基准', h2_style),
    P('教培 KOC 个人号：3% — 8%（健康）', body_style),
    P('教培机构号：1.5% — 3%（< 2% 异常需排查）', body_style),
    P('计算公式：(赞 + 收藏 + 评论) / 曝光 × 100%', note_style),
    Spacer(1, 0.3*cm),
    P('（2）账号阶段判定', h2_style),
    P('冷启动期：< 1k 粉，重心打标签 + 视觉统一', body_style),
    P('成长期：1k — 1w 粉，重心选题测爆款 + 内容矩阵化', body_style),
    P('突破期：1w — 5w 粉，重心人格强化 + 转化路径', body_style),
    P('商业化：5w+ 粉，重心私域沉淀 + 系列产品', body_style),
    Spacer(1, 0.3*cm),
    P('（3）每 5—8 篇笔记后的 KPI 检查清单', h2_style),
    P('总粉丝增量', body_style),
    P('新笔记总赞 / 收藏 / 评论 / 私信数', body_style),
    P('哪一篇数据最好（爆款基因）', body_style),
    P('哪些标签带来最多曝光', body_style),
    P('转化笔记的留资数', body_style),
    Spacer(1, 0.3*cm),
    P('（4）调整决策树', h2_style),
    P('数据正常 → 维持节奏 + 加大产量', body_style),
    P('曝光高互动低 → 标题 / 封面 OK，内容深度不够', body_style),
    P('曝光低 → 标签 / 同城 / 发布时间出问题', body_style),
    P('两周无增长 → 必须停下来重审人设 / 赛道 / 视觉', body_style),
]

# Section 10
S10 = [
    P('十、文档与版本管理', h1_style),
    divider(),
    P('（1）规范沉淀路径', h2_style),
    P('.kiro/steering/yuanxuetong-writing-rules.md（品牌专属，auto 加载）', body_style),
    P('.kiro/steering/writing-rules-general.md（通用版，manual 调用）', body_style),
    P('.kiro/scripts/&nbsp;&nbsp; 自动化脚本目录', body_style),
    P('.kiro/drafts/&nbsp;&nbsp;&nbsp; 草稿目录（不进主分支）', body_style),
    Spacer(1, 0.3*cm),
    P('（2）输出规则', h2_style),
    P('每次出稿必带「改了什么 + 为什么」对照表', body_style),
    P('每次跑过自动校验脚本才输出终稿', body_style),
    P('草稿命名：note&lt;序号&gt;_&lt;主题&gt;_v&lt;版本&gt;.txt', body_style),
    Spacer(1, 0.3*cm),
    P('（3）版本迭代触发器', h2_style),
    P('新增禁用句式 / 新增字数规则 → 直接更新 steering 文件并升版本号', body_style),
    P('账号阶段变化（冷启动 → 成长期）→ 重审整套规则', body_style),
    P('新平台（公众号 / 视频号 / 抖音）→ 写独立 steering 文件', body_style),
    Spacer(1, 0.3*cm),
    P('（4）规范同步', h2_style),
    P('每次更新先在本仓库验证 1 周', body_style),
    P('稳定后推到团队公共 steering 库', body_style),
    P('重大变更需团队评审 + 版本号升 minor（v1.x）或 major（v2.0）', body_style),
]


# Last page
LAST = [
    Spacer(1, 4*cm),
    P('—— 末页 ——', divider_style),
    Spacer(1, 1*cm),
    P('版本历史', h2_style),
    P('v1.0 &nbsp;&nbsp; 2026.05.28 &nbsp;&nbsp; 首版沉淀（10 章，58 条规则）', body_style),
    Spacer(1, 0.6*cm),
    P('维护方式', h2_style),
    P('文件位置：.kiro/scripts/build_pdf.py', body_style),
    P('更新流程：改 build_pdf.py → 跑生成 → 替换旧 PDF → 升版本号', body_style),
    Spacer(1, 0.6*cm),
    P('使用提示', h2_style),
    P('本手册为内部文档，不对外', body_style),
    P('每次写笔记前先看 steering 文件，写完跑校验脚本', body_style),
    P('遇到新场景 → 先依规则尝试 → 不适用再加新规则 → 升级 PDF', body_style),
    Spacer(1, 1.5*cm),
    divider(),
    P('© 2026 渊学通杭州 · 内部使用', meta_style),
]

# ============ BUILD ============

def build():
    doc = SimpleDocTemplate(
        '.kiro/drafts/个人规则_v1.0.pdf',
        pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title='个人规则 1.0',
        author='渊学通杭州',
    )
    flow = []
    flow += COVER + [PageBreak()]
    flow += TOC + [PageBreak()]
    for sec in [S1, S2, S3, S4, S5, S6, S7, S8, S9, S10]:
        flow += sec + [PageBreak()]
    flow += LAST
    doc.build(flow)

if __name__ == '__main__':
    build()
    print('PDF generated: .kiro/drafts/个人规则_v1.0.pdf')
