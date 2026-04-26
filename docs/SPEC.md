# 小探索家（KidsExplorer）— docs/SPEC.md
> 支持三大类：食物 🍎 · 动物 🐼 · 花草 🌸  
> 原型文件：docs/prototype_v2.html（14页主流程）· docs/detail_prototype.html（四面图/八方图/视角标注）  
> 本文档为 Claude Code 完整开发规范，严格按里程碑顺序实现，每个 M 完成并测试后再进入下一个。

---

## 一、产品概述

| 项目 | 内容 |
|------|------|
| 产品名称 | 小探索家（KidsExplorer） |
| 目标用户 | 3～10 岁儿童（由家长协助） |
| 平台 | 微信小程序（uni-app 开发） |
| 核心体验 | 选择分类 → 语音说名称 → AI 生成图像 → 拆解部位标注 → 四面/八方多视角探索 |

---

## 二、分类系统

| 分类 | key | 主色 | 浅色 | 深色 | 部位知识维度 |
|------|-----|------|------|------|------------|
| 食物 | `food`   | `#FFB347` | `#FFF3CC` | `#E65100` | 颜色 / 口感 / 吃法 |
| 动物 | `animal` | `#66BB6A` | `#E8F5E9` | `#2E7D32` | 颜色 / 习性 / 趣味 |
| 花草 | `plant`  | `#EC407A` | `#FCE4EC` | `#880E4F` | 颜色 / 气味 / 特征 |

分类影响：首页背景渐变、麦克风颜色、探索页 pill、特写 tag、图鉴列表卡片颜色、AI Prompt 风格、部位知识卡图标。

---

## 三、技术栈

### 前端
| 项目 | 选型 |
|------|------|
| 框架 | uni-app + Vue3 + TypeScript |
| 状态管理 | Pinia |
| 样式 | SCSS（颜色通过 props / CSS 变量注入，禁止硬编码） |
| 构建 | HBuilderX / Vite |
| 目标平台 | 微信小程序（mp-weixin） |

### 后端
| 项目 | 选型 |
|------|------|
| 语言 | Python 3.11+ |
| Web 框架 | FastAPI |
| 服务器 | Uvicorn（开发）/ Gunicorn + Uvicorn workers（生产） |
| ORM | SQLAlchemy 2.0（异步，async session） |
| 数据库 | MySQL 8.0 |
| 数据库驱动 | aiomysql |
| 数据迁移 | Alembic |
| 数据校验 | Pydantic v2 |
| 部署 | Railway（开发）/ 腾讯云轻量服务器（生产） |
| 协议 | HTTPS（微信小程序强制要求） |

### AI API
| 功能 | API |
|------|-----|
| 语音识别 | 微信同声传译插件（wx.plugin） |
| 意图提取 | Anthropic Claude 3.5 Haiku |
| 图像生成 | OpenAI gpt-image-1 |
| 图像拆解 | OpenAI GPT-4o Vision |
| 语音播报 | OpenAI TTS-1（后端中转） |

---

## 四、完整页面列表

| # | 页面 | 路由 | 原型参考 |
|---|------|------|---------|
| 1 | 首页总览 | pages/index | prototype_v2.html · PAGE 1 |
| 2 | 食物首页 | pages/food/index | prototype_v2.html · PAGE 2 |
| 3 | 动物首页 | pages/animal/index | prototype_v2.html · PAGE 3 |
| 4 | 花草首页 | pages/plant/index | prototype_v2.html · PAGE 4 |
| 5 | 生成中 | pages/generating | prototype_v2.html · PAGE 5 |
| 6 | 食物探索页 | pages/food/explore | prototype_v2.html · PAGE 6 |
| 7 | 动物探索页 | pages/animal/explore | prototype_v2.html · PAGE 7 |
| 8 | 花草探索页 | pages/plant/explore | prototype_v2.html · PAGE 8 |
| 9 | 食物特写页 | pages/food/detail | prototype_v2.html · PAGE 9 |
| 10 | 动物特写页 | pages/animal/detail | prototype_v2.html · PAGE 10 |
| 11 | 花草特写页 | pages/plant/detail | prototype_v2.html · PAGE 11 |
| 12 | 食物图鉴列表 | pages/food/list | prototype_v2.html · PAGE 12 |
| 13 | 动物图鉴列表 | pages/animal/list | prototype_v2.html · PAGE 13 |
| 14 | 花草图鉴列表 | pages/plant/list | prototype_v2.html · PAGE 14 |
| A | 四面图 | pages/multiview | detail_prototype.html · PAGE A |
| B | 八方罗盘 | pages/multiview | detail_prototype.html · PAGE B |
| C | 视角标注特写 | pages/multiview/detail | detail_prototype.html · PAGE C |

> 食物/动物/花草三类的首页、探索页、特写页、列表页结构对称，  
> 通过 `category.ts` 配置驱动，禁止重复写逻辑与硬编码颜色。

---

## 五、目录结构

```
KidsExplorer/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index/                   # PAGE 1 首页总览
│   │   │   │   └── index.vue
│   │   │   ├── generating/              # PAGE 5 生成中
│   │   │   │   └── index.vue
│   │   │   ├── multiview/               # PAGE A/B/C 多视角
│   │   │   │   ├── index.vue            # 四面图 / 八方图
│   │   │   │   └── detail.vue           # 视角标注特写
│   │   │   ├── food/
│   │   │   │   ├── index/index.vue      # PAGE 2 食物首页
│   │   │   │   ├── explore/index.vue    # PAGE 6 食物探索
│   │   │   │   ├── detail/index.vue     # PAGE 9 食物特写
│   │   │   │   └── list/index.vue       # PAGE 12 食物图鉴
│   │   │   ├── animal/
│   │   │   │   ├── index/index.vue      # PAGE 3 动物首页
│   │   │   │   ├── explore/index.vue    # PAGE 7 动物探索
│   │   │   │   ├── detail/index.vue     # PAGE 10 动物特写
│   │   │   │   └── list/index.vue       # PAGE 13 动物图鉴
│   │   │   └── plant/
│   │   │       ├── index/index.vue      # PAGE 4 花草首页
│   │   │       ├── explore/index.vue    # PAGE 8 花草探索
│   │   │       ├── detail/index.vue     # PAGE 11 花草特写
│   │   │       └── list/index.vue       # PAGE 14 花草图鉴
│   │   │
│   │   ├── components/
│   │   │   ├── CategorySelector/index.vue   # 三分类切换卡
│   │   │   ├── MicButton/index.vue          # 录音按钮
│   │   │   ├── HistoryScroll/index.vue      # 历史横滚列表
│   │   │   ├── QuickCards/index.vue         # 推荐三格卡
│   │   │   ├── GuideBox/index.vue           # 底部引导框
│   │   │   ├── SubjectCanvas/index.vue      # 图像 + 标注点
│   │   │   ├── PartChipGrid/index.vue       # 部位标签网格
│   │   │   ├── InfoRow/index.vue            # 三格知识横排
│   │   │   ├── ActionBar/index.vue          # 底部操作栏
│   │   │   ├── PartDetailSheet/index.vue    # 部位特写弹出层
│   │   │   ├── FactCards/index.vue          # 三格知识卡
│   │   │   ├── RelatedParts/index.vue       # 相关部位列表
│   │   │   ├── SearchBar/index.vue          # 图鉴搜索框
│   │   │   ├── FilterRow/index.vue          # 图鉴过滤标签
│   │   │   ├── SubjectGrid/index.vue        # 图鉴 2×2 卡片
│   │   │   ├── GeneratingProgress/index.vue # 生成进度五步
│   │   │   ├── Compass4/index.vue           # 四面方向选择器
│   │   │   └── Compass8/index.vue           # 八方罗盘
│   │   │
│   │   ├── store/
│   │   │   └── explorerStore.ts
│   │   │
│   │   ├── utils/
│   │   │   ├── request.ts               # uni.request 封装
│   │   │   ├── speech.ts                # 同声传译封装
│   │   │   └── category.ts              # 分类配置工具（见第十章）
│   │   │
│   │   ├── static/sounds/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── pages.json
│   │   └── manifest.json
│   └── package.json
│
└── backend/
    ├── app/
    │   ├── main.py                      # FastAPI 入口，注册路由和中间件
    │   ├── config.py                    # 读取 .env，暴露 Settings 对象
    │   ├── database.py                  # SQLAlchemy 异步 engine + session
    │   │
    │   ├── models/                      # SQLAlchemy ORM 模型
    │   │   ├── __init__.py
    │   │   ├── subject.py               # subjects 表
    │   │   ├── part.py                  # parts 表
    │   │   ├── image.py                 # images 表
    │   │   └── history.py               # history 表
    │   │
    │   ├── schemas/                     # Pydantic 请求/响应模型
    │   │   ├── parse.py
    │   │   ├── image.py
    │   │   ├── vision.py
    │   │   └── tts.py
    │   │
    │   ├── routers/                     # FastAPI 路由
    │   │   ├── parse.py                 # POST /api/parse
    │   │   ├── image.py                 # POST /api/image
    │   │   ├── vision.py                # POST /api/vision
    │   │   └── tts.py                   # POST /api/tts
    │   │
    │   ├── services/                    # 业务逻辑层
    │   │   ├── ai_parse.py              # 调用 Claude 提取意图
    │   │   ├── ai_image.py              # 调用 OpenAI 生成图像
    │   │   ├── ai_vision.py             # 调用 GPT-4o Vision 拆解
    │   │   └── ai_tts.py                # 调用 OpenAI TTS
    │   │
    │   └── middleware/
    │       └── auth.py                  # Bearer Token 鉴权
    │
    ├── alembic/                         # 数据库迁移
    │   ├── versions/
    │   └── env.py
    ├── alembic.ini
    ├── requirements.txt
    ├── .env.example
    ├── .env
    └── .gitignore
```

---

## 六、设计规范（Design Tokens）

```scss
// ── 全局 ──
$bg:       #FFFBF0;
$text:     #3D2C00;
$text-sub: #A07840;
$font:     "PingFang SC", "Microsoft YaHei", sans-serif;

// ── 分类主题（通过 props 或 CSS var 注入，禁止硬编码）──
// food
$food-primary: #FFB347;  $food-light: #FFF3CC;  $food-dark: #E65100;
$food-bg:      linear-gradient(160deg, #FFF8E7, #FFF1CC, #FFE0A3);

// animal
$animal-primary: #66BB6A;  $animal-light: #E8F5E9;  $animal-dark: #2E7D32;
$animal-bg:      linear-gradient(160deg, #F1FFF1, #E8F5E9, #DCEDC8);

// plant
$plant-primary: #EC407A;  $plant-light: #FCE4EC;  $plant-dark: #880E4F;
$plant-bg:      linear-gradient(160deg, #FFF0F5, #FCE4EC, #F8BBD0);

// ── 尺寸 ──
$size-base: 28rpx;  $size-title: 40rpx;  $size-tag: 22rpx;
$r-card: 24rpx;  $r-button: 999rpx;  $r-chip: 14rpx;

// ── 交互 ──
// 最小点击区域：80×80rpx
// 按压反馈：scale(0.92) + wx.vibrateShort
// 等待状态：卡通动效 + 禁止重复点击
// 页面深度：最多 2 层（弹出层不计）
```

---

## 七、页面功能详细说明

### PAGE 1 — 首页总览（pages/index）
三类卡片 CategorySelector，选中高亮，未选中 opacity:0.6；MicButton 颜色跟随分类；按住录音 → 识别完成 → 跳转 generating；底部 QuickCards、HistoryScroll（混合三类，带颜色 tag）、GuideBox。

**分类切换动效：** 背景渐变 transition 0.4s，麦克风颜色 transition 0.3s，提示语同步变化。

**识别分类不符时：** 弹提示「我听到的是 🐼 动物，帮你切换过去了～」并自动切换。

---

### PAGE 2/3/4 — 各分类首页（对称，仅颜色与内容不同）

| 分类 | QuickCards 推荐 |
|------|----------------|
| 食物 | 🍌 香蕉/看果皮果肉 · 🍉 西瓜/看瓜皮和籽 · 🥕 胡萝卜/看根部叶子 |
| 动物 | 🐼 熊猫/看黑眼圈爪子 · 🦁 狮子/看鬃毛尾巴 · 🦋 蝴蝶/看翅膀花纹 |
| 花草 | 🌸 樱花/看花瓣花蕊 · 🌻 向日葵/看花盘种子 · 🎍 竹子/看竹节叶片 |

HistoryScroll 只展示当前分类历史记录。

---

### PAGE 5 — 生成中（pages/generating）
禁止返回；五步进度卡片实时更新；四面图完成后自动跳转探索页；后台继续生成八方图；底部缩略预览四格（完成/生成中）；等待文案每 3 秒轮换一句（5 条）。

---

### PAGE 6/7/8 — 各分类探索页（对称）
SubjectCanvas（Canvas 2D 标注点）+ PartChipGrid（2×2）+ InfoRow（三格）+ ActionBar（介绍/再来/多角度）。

| 分类 | InfoRow 三格 |
|------|-------------|
| 食物 | 🎨 颜色 · 👅 口感 · 🍽️ 吃法 |
| 动物 | 🎨 颜色 · 🐾 习性 · 💡 趣味 |
| 花草 | 🎨 颜色 · 👃 气味 · 🍃 特征 |

标注点颜色轮转：`['#FFB347','#4FC3F7','#66BB6A','#F06292']`，点击打开 PartDetailSheet。

---

### PAGE 9/10/11 — 各分类特写页（对称）
TopBar + DetailCard（特写图 + karaoke 文字 + TTS 进度条）+ FactCards（三格）+ RelatedParts（横滑切换）+ NextButton。karaoke 最多 3 句，关键词最多 3 种高亮色。

---

### PAGE 12/13/14 — 各分类图鉴列表（对称）
SearchBar（本地过滤）+ FilterRow（子分类）+ SubjectGrid（2×2，已探索/开始探索 badge）。

| 分类 | FilterRow 子分类 |
|------|----------------|
| 食物 | 全部 · 水果 · 蔬菜 · 主食 · 甜品 |
| 动物 | 全部 · 陆地 · 海洋 · 天空 · 昆虫 |
| 花草 | 全部 · 花朵 · 树木 · 叶子 · 草本 |

---

### PAGE A/B/C — 多视角（pages/multiview）
- **PAGE A 四面图**：四方向卡片选择器 + 主图 + 四图缩略 + 操作栏
- **PAGE B 八方罗盘**：圆形罗盘 8 按钮 + 颜色图例 + 八图横滑缩略 + 视角描述卡
- **PAGE C 视角标注特写**：视角切换横滑标签 + Canvas 标注图 + 部位横滑标签 + 特写卡片 + FactCards + NextButton

---

## 八、数据库设计（MySQL 8.0）

### subjects 表（探索对象）
```sql
CREATE TABLE subjects (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(50)  NOT NULL COMMENT '中文名，如 熊猫',
  name_en     VARCHAR(100) NOT NULL COMMENT '英文名，如 giant panda',
  emoji       VARCHAR(10)  NOT NULL,
  category    ENUM('food','animal','plant') NOT NULL,
  sub_category VARCHAR(20) NOT NULL COMMENT '子分类，如 陆地',
  seed        INT UNSIGNED NOT NULL COMMENT '图像生成随机种子',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_category (category),
  INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### images 表（生成图像）
```sql
CREATE TABLE images (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  subject_id  BIGINT UNSIGNED NOT NULL,
  view_type   ENUM('single','front','back','left','right',
                   'front_left','front_right','back_left','back_right') NOT NULL,
  image_url   TEXT NOT NULL COMMENT '图像 URL 或 Base64',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
  INDEX idx_subject (subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### parts 表（部位标注）
```sql
CREATE TABLE parts (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  subject_id  BIGINT UNSIGNED NOT NULL,
  image_id    BIGINT UNSIGNED NOT NULL COMMENT '对应哪张视角图',
  part_key    VARCHAR(50)  NOT NULL COMMENT '部位标识，如 eye_patch',
  name        VARCHAR(50)  NOT NULL COMMENT '中文部位名，如 黑眼圈',
  short_name  VARCHAR(5)   NOT NULL COMMENT '1字简称，如 眼',
  color       VARCHAR(10)  NOT NULL COMMENT '标注颜色，如 #4FC3F7',
  pos_x       DECIMAL(4,3) NOT NULL COMMENT '标注点 x 坐标（0~1）',
  pos_y       DECIMAL(4,3) NOT NULL COMMENT '标注点 y 坐标（0~1）',
  description TEXT         NOT NULL COMMENT '部位介绍文字',
  facts       JSON         NOT NULL COMMENT '{"颜色":"黑色","习性":"...","趣味":"..."}',
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
  FOREIGN KEY (image_id)   REFERENCES images(id)   ON DELETE CASCADE,
  INDEX idx_subject (subject_id),
  INDEX idx_image   (image_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### history 表（探索历史）
```sql
CREATE TABLE history (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  subject_id  BIGINT UNSIGNED NOT NULL,
  category    ENUM('food','animal','plant') NOT NULL,
  explored_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
  INDEX idx_category    (category),
  INDEX idx_explored_at (explored_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 九、后端 API 接口规范

### 公共约定
```
Base URL:     https://your-domain.com
Headers:      Authorization: Bearer <APP_TOKEN>
Content-Type: application/json
超时:          15000ms
```

---

### POST /api/parse

**Request：**
```json
{ "text": "熊猫长什么样" }
```

**Response：**
```json
{
  "success": true,
  "name": "熊猫",
  "name_en": "giant panda",
  "emoji": "🐼",
  "category": "animal",
  "sub_category": "陆地"
}
```

**services/ai_parse.py Claude Prompt：**
```python
PARSE_PROMPT = """
从用户语音文字中提取探索目标，返回严格 JSON，不含任何多余文字：
{
  "name": "中文名",
  "name_en": "英文名",
  "emoji": "最合适的单个emoji",
  "category": "food | animal | plant",
  "sub_category": "对应子分类"
}
子分类对照：
  food   → 水果 | 蔬菜 | 主食 | 甜品
  animal → 陆地 | 海洋 | 天空 | 昆虫
  plant  → 花朵 | 树木 | 叶子 | 草本
若无法识别则 category 为 "unknown"
"""
```

---

### POST /api/image

**Request：**
```json
{
  "name": "熊猫",
  "name_en": "giant panda",
  "category": "animal",
  "mode": "4view",
  "seed": 67890
}
```

**Response：**
```json
{
  "success": true,
  "subject_id": 42,
  "images": [
    { "view": "front",  "url": "https://...", "label": "正面" },
    { "view": "back",   "url": "https://...", "label": "背面" },
    { "view": "left",   "url": "https://...", "label": "左面" },
    { "view": "right",  "url": "https://...", "label": "右面" }
  ]
}
```

**services/ai_image.py Prompt 模板：**
```python
IMAGE_PROMPTS = {
    "food": lambda name, view: (
        f"a cute cartoon {name}, {view} view, pure white background, "
        "flat illustration for kids, bright vivid colors, educational food illustration style"
    ),
    "animal": lambda name, view: (
        f"a cute cartoon {name}, {view} view, pure white background, "
        "flat illustration for kids, friendly expression, bright colors, nature education style"
    ),
    "plant": lambda name, view: (
        f"a cute cartoon {name} flower or plant, {view} view, pure white background, "
        "flat illustration for kids, bright vivid colors, botanical education style"
    ),
}

FOUR_VIEWS  = ["front", "back", "left side", "right side"]
EIGHT_EXTRA = ["front-left diagonal", "front-right diagonal",
               "back-left diagonal",  "back-right diagonal"]
```

**并发生成（asyncio）：**
```python
import asyncio
tasks = [generate_one(name, view, category) for view in views]
results = await asyncio.gather(*tasks)   # 禁止串行
```

---

### POST /api/vision

**Request：**
```json
{
  "image_url": "https://...",
  "name": "熊猫",
  "name_en": "giant panda",
  "category": "animal",
  "view": "front",
  "subject_id": 42
}
```

**Response：**
```json
{
  "success": true,
  "parts": [
    {
      "id": "eye_patch",
      "name": "黑眼圈",
      "short_name": "眼",
      "color": "#4FC3F7",
      "x": 0.42,
      "y": 0.35,
      "description": "熊猫的黑眼圈是最有名的外貌特点，每只熊猫眼圈形状都有点不一样。",
      "facts": {
        "颜色": "黑色",
        "习性": "帮助识别同伴",
        "趣味": "每只都不一样"
      }
    }
  ],
  "view_description": "从正面看熊猫，能看到它圆圆的大脸和可爱的黑眼圈～",
  "info_row": {
    "颜色": "黑白相间",
    "习性": "爱吃竹子",
    "趣味": "眼圈都不同"
  }
}
```

**facts_keys 规范（services/ai_vision.py）：**
```python
FACTS_KEYS = {
    "food":   ["颜色", "口感", "吃法"],
    "animal": ["颜色", "习性", "趣味"],
    "plant":  ["颜色", "气味", "特征"],
}
```

识别结果写入 `parts` 表，`facts` 字段存为 JSON。

---

### POST /api/tts

**Request：**
```json
{ "text": "熊猫的黑眼圈是最有名的外貌特点，每只熊猫眼圈形状都有点不一样。" }
```

**Response：**
```json
{ "success": true, "audio_base64": "data:audio/mp3;base64,..." }
```

---

## 十、Pinia 状态设计（explorerStore.ts）

```typescript
type Category = 'food' | 'animal' | 'plant'

interface ViewImage  { view: string; url: string; label: string }
interface SubjectPart {
  id: string; name: string; shortName: string; color: string
  x: number; y: number; description: string; facts: Record<string, string>
}
interface HistoryItem {
  id: string; name: string; emoji: string; category: Category
  imageUrl: string; timestamp: number
}

interface ExplorerState {
  currentCategory:  Category

  currentSubject: {
    name: string; nameEn: string; emoji: string
    category: Category; subCategory: string
    seed: number; subjectId: number | null
  } | null

  images: { single: string; four: ViewImage[]; eight: ViewImage[] }
  parts:  SubjectPart[]

  generating: {
    step:          number    // 0~5
    fourProgress:  number    // 0~100
    fourDone:      boolean
    eightDone:     boolean
    visionDone:    boolean
  }

  currentPartId: string | null
  history:       HistoryItem[]   // 最多 20 条，持久化
}
```

---

## 十一、category.ts（完整实现）

```typescript
// utils/category.ts
export type Category = 'food' | 'animal' | 'plant'

export const CATEGORY_CONFIG = {
  food: {
    label: '食物', emoji: '🍎',
    primary: '#FFB347', light: '#FFF3CC', dark: '#E65100',
    bgGradient: 'linear-gradient(160deg,#FFF8E7,#FFF1CC,#FFE0A3)',
    micShadow:  'rgba(255,179,71,0.52)',
    hintText:    '说出你想认识的食物吧！',
    hintExample: '试试说"香蕉长什么样"',
    guideTitle:  '食物探索重点',
    guideText:   '更适合展示颜色、口感、果皮、果核等结构。',
    factsKeys:   ['颜色', '口感', '吃法'],
    factsIcons:  ['🎨', '👅', '🍽️'],
    filterTags:  ['全部', '水果', '蔬菜', '主食', '甜品'],
    quickCards: [
      { emoji: '🍌', name: '香蕉',   desc: '看看果皮和果肉' },
      { emoji: '🍉', name: '西瓜',   desc: '看看瓜皮和籽' },
      { emoji: '🥕', name: '胡萝卜', desc: '看看根部和叶子' },
    ],
  },
  animal: {
    label: '动物', emoji: '🐼',
    primary: '#66BB6A', light: '#E8F5E9', dark: '#2E7D32',
    bgGradient: 'linear-gradient(160deg,#F1FFF1,#E8F5E9,#DCEDC8)',
    micShadow:  'rgba(102,187,106,0.5)',
    hintText:    '说出你想认识的动物吧！',
    hintExample: '试试说"熊猫长什么样"',
    guideTitle:  '动物探索重点',
    guideText:   '更适合展示耳朵、眼睛、尾巴、花纹和习性知识。',
    factsKeys:   ['颜色', '习性', '趣味'],
    factsIcons:  ['🎨', '🐾', '💡'],
    filterTags:  ['全部', '陆地', '海洋', '天空', '昆虫'],
    quickCards: [
      { emoji: '🐼', name: '熊猫', desc: '看黑眼圈和爪子' },
      { emoji: '🦁', name: '狮子', desc: '看鬃毛和尾巴' },
      { emoji: '🦋', name: '蝴蝶', desc: '看翅膀花纹' },
    ],
  },
  plant: {
    label: '花草', emoji: '🌸',
    primary: '#EC407A', light: '#FCE4EC', dark: '#880E4F',
    bgGradient: 'linear-gradient(160deg,#FFF0F5,#FCE4EC,#F8BBD0)',
    micShadow:  'rgba(236,64,122,0.45)',
    hintText:    '说出你想认识的花草吧！',
    hintExample: '试试说"樱花长什么样"',
    guideTitle:  '花草探索重点',
    guideText:   '更适合展示花瓣、叶子、花蕊、枝干和香味特点。',
    factsKeys:   ['颜色', '气味', '特征'],
    factsIcons:  ['🎨', '👃', '🍃'],
    filterTags:  ['全部', '花朵', '树木', '叶子', '草本'],
    quickCards: [
      { emoji: '🌸', name: '樱花',   desc: '看花瓣和花蕊' },
      { emoji: '🌻', name: '向日葵', desc: '看花盘和种子' },
      { emoji: '🎍', name: '竹子',   desc: '看竹节和叶片' },
    ],
  },
} as const

export const getCategoryConfig = (cat: Category) => CATEGORY_CONFIG[cat]
```

---

## 十二、pages.json 路由配置

```json
{
  "pages": [
    { "path": "pages/index/index",         "style": { "navigationBarTitleText": "小探索家" } },
    { "path": "pages/generating/index",    "style": { "navigationBarTitleText": "生成中", "navigationStyle": "custom" } },
    { "path": "pages/multiview/index",     "style": { "navigationBarTitleText": "多角度探索" } },
    { "path": "pages/multiview/detail",    "style": { "navigationBarTitleText": "部位特写" } },
    { "path": "pages/food/index/index",    "style": { "navigationBarTitleText": "食物探索" } },
    { "path": "pages/food/explore/index",  "style": { "navigationBarTitleText": "食物探索" } },
    { "path": "pages/food/detail/index",   "style": { "navigationBarTitleText": "部位特写" } },
    { "path": "pages/food/list/index",     "style": { "navigationBarTitleText": "食物图鉴" } },
    { "path": "pages/animal/index/index",  "style": { "navigationBarTitleText": "动物探索" } },
    { "path": "pages/animal/explore/index","style": { "navigationBarTitleText": "动物探索" } },
    { "path": "pages/animal/detail/index", "style": { "navigationBarTitleText": "部位特写" } },
    { "path": "pages/animal/list/index",   "style": { "navigationBarTitleText": "动物图鉴" } },
    { "path": "pages/plant/index/index",   "style": { "navigationBarTitleText": "花草探索" } },
    { "path": "pages/plant/explore/index", "style": { "navigationBarTitleText": "花草探索" } },
    { "path": "pages/plant/detail/index",  "style": { "navigationBarTitleText": "部位特写" } },
    { "path": "pages/plant/list/index",    "style": { "navigationBarTitleText": "花草图鉴" } }
  ],
  "tabBar": {
    "color": "#A07840",
    "selectedColor": "#FFB347",
    "backgroundColor": "#FFFBF0",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "探索",
        "iconPath": "static/tab/explore.png",
        "selectedIconPath": "static/tab/explore-active.png"
      },
      {
        "pagePath": "pages/food/list/index",
        "text": "图鉴",
        "iconPath": "static/tab/book.png",
        "selectedIconPath": "static/tab/book-active.png"
      }
    ]
  }
}
```

---

## 十三、manifest.json

```json
{
  "mp-weixin": {
    "appid": "YOUR_APPID",
    "plugins": {
      "WechatSI": {
        "version": "0.3.5",
        "provider": "wx069ba97219f66d99"
      }
    },
    "permission": {
      "scope.record": {
        "desc": "需要录音权限来听你说的食物、动物、花草名称哦～"
      }
    }
  }
}
```

---

## 十四、后端环境配置

### requirements.txt
```
fastapi==0.111.0
uvicorn[standard]==0.29.0
gunicorn==22.0.0
sqlalchemy==2.0.30
aiomysql==0.2.0
alembic==1.13.1
pydantic==2.7.1
pydantic-settings==2.2.1
anthropic==0.26.0
openai==1.30.1
python-multipart==0.0.9
python-jose[cryptography]==3.3.0
httpx==0.27.0
```

### .env.example
```
# 数据库
DB_HOST=localhost
DB_PORT=3306
DB_NAME=kids_explorer
DB_USER=root
DB_PASSWORD=your_password

# AI
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...

# 鉴权
APP_TOKEN=your-random-secret-token

# 服务
PORT=8000
ENV=development
```

### app/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host:     str
    db_port:     int = 3306
    db_name:     str
    db_user:     str
    db_password: str

    openai_api_key: str
    claude_api_key: str
    app_token:      str

    port: int = 8000
    env:  str = "development"

    @property
    def db_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"

settings = Settings()
```

### app/database.py
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.db_url, echo=False, pool_size=10)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## 十五、里程碑开发顺序（共 7 个）

### M1 — 项目骨架
**前端**
- [ ] uni-app Vue3+TypeScript 初始化，安装 Pinia
- [ ] 按目录结构创建全部页面 / 组件文件（空文件 + 注释占位）
- [ ] 完整实现 `utils/category.ts`（第十一章内容）
- [ ] 完整实现 `utils/request.ts`（baseURL + token + timeout + 错误处理）
- [ ] 完整实现 `store/explorerStore.ts`（第十章类型与状态）
- [ ] 配置 `pages.json`（全部 16 路由）和 `manifest.json`

**后端**
- [ ] Python 项目初始化，安装 requirements.txt
- [ ] 实现 `app/config.py`、`app/database.py`
- [ ] 创建 MySQL 数据库及 4 张表（直接执行 SQL 或 Alembic 迁移）
- [ ] 4 个路由全部返回 mock 数据，配置 CORS
- [ ] 实现 Bearer Token 鉴权中间件 `app/middleware/auth.py`

**验证：** 前端调通所有 mock 接口，各路由可跳转（空页面）

---

### M2 — 首页 UI（静态）
- [ ] PAGE 1 首页总览（CategorySelector + MicButton + QuickCards + HistoryScroll + GuideBox）
- [ ] PAGE 2/3/4 三个分类首页对称实现，颜色 / 文案全由 category.ts 驱动
- [ ] 分类切换动效：背景渐变 + 麦克风颜色 + 提示语（transition 动画）
- [ ] HistoryScroll mock 数据，混合三类带颜色 tag
- [ ] 验证：视觉与 prototype_v2.html PAGE 1~4 完全一致

---

### M3 — 录音 + 意图提取
- [ ] `utils/speech.ts` 封装微信同声传译，长按录音，松开结束
- [ ] 录音期间麦克风三圈脉冲动效
- [ ] 接入真实 `/api/parse`（后端调 Claude API）
- [ ] 分类自动校正弹提示逻辑
- [ ] PAGE 5 生成中页面 UI（五步进度，mock 自动推进演示）
- [ ] 探索历史写入 MySQL `history` 表

---

### M4 — 图像生成
- [ ] 后端 `/api/image`：按 category 选 Prompt，asyncio.gather 并发生成四面图
- [ ] 图像 URL 写入 MySQL `images` 表
- [ ] PAGE 5 进度页对接真实状态（轮询 /api/image/status）
- [ ] 四面图完成自动跳转对应分类探索页；后台继续生成八方图
- [ ] 图像 URL 同步写入 explorerStore

---

### M5 — 探索页 + 标注 + 特写
- [ ] 后端 `/api/vision`：GPT-4o Vision 拆解图像，按 category 返回 facts，写入 `parts` 表
- [ ] SubjectCanvas：Canvas 2D 绘图 + 脉冲标注点（坐标 0~1 换算）
- [ ] PAGE 6/7/8 探索页对接真实数据
- [ ] PartDetailSheet 弹出层（半屏上滑关闭）
- [ ] PAGE 9/10/11 特写页 UI，RelatedParts 点击切换部位
- [ ] 数据从 MySQL `parts` 表读取

---

### M6 — TTS 语音播报
- [ ] 后端 `/api/tts`（OpenAI TTS-1）
- [ ] PartDetailSheet 打开自动触发 TTS，audio-bar 进度动效
- [ ] 卡拉 OK 逐词高亮（空格分词，监听 audio currentTime）
- [ ] ActionBar「🔊 介绍」依次朗读各部位
- [ ] 多视角切换时 TTS 播报当前视角描述

---

### M7 — 图鉴 + 多视角 + 打磨
- [ ] PAGE 12/13/14 图鉴列表 UI，SearchBar 本地过滤，FilterRow 子分类过滤
- [ ] SubjectGrid badge 根据 MySQL `history` 表判断是否已探索
- [ ] pages/multiview：Compass4 + Compass8，对接 images.four / images.eight
- [ ] PAGE C 视角标注特写（detail_prototype.html PAGE C）
- [ ] 八方图 Tab 根据 eightDone 解锁
- [ ] 全部按钮 `wx.vibrateShort` 震动反馈
- [ ] 错误处理：API 失败弹可爱提示 + 重试按钮
- [ ] 微信图片安全审核（security.imgSecCheck）
- [ ] 服务器域名白名单配置
- [ ] 隐私政策声明页
- [ ] 提审材料整理

---


