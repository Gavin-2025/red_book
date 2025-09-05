# 小红书达人智能评估系统

> 基于行业标准的专业KOL评估工具

## 🌟 系统概述

小红书达人智能评估系统是一款专为品牌方和MCN机构设计的KOL评估工具，基于行业权威标准，提供科学、准确的达人价值评估。

## 📁 项目结构

```
小红书达人评估系统/
├── evaluator.py           # 基础版评估系统
├── advanced_evaluator.py  # 专业版评估系统（推荐）
├── requirements.txt       # 项目依赖
├── 示例数据模板.csv       # 批量评估数据模板
├── 使用指南.md            # 详细使用说明
├── README.md              # 项目说明文档
└── venv/                  # Python虚拟环境
```

## 🚀 系统版本

### 🎯 **v1.0 基础版本** (`evaluator.py`)
- **适用场景**: 快速评估、简单筛选
- **核心功能**: 基础四维度评估（影响力、内容质量、互动表现、商业契合度）
- **使用方式**: `streamlit run evaluator.py`

### 🚀 **v2.0 专业版本** (`advanced_evaluator.py`) - **推荐使用**
- **适用场景**: 专业筛选、批量处理、深度分析
- **核心功能**: 五维度专业评估体系 + 批量处理 + 数据分析
- **使用方式**: `streamlit run advanced_evaluator.py`

## 🛠️ 快速开始

### 1. 环境准备
```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动系统
```bash
# 启动专业版（推荐）
streamlit run advanced_evaluator.py

# 或启动基础版
streamlit run evaluator.py
```

### 3. 使用说明
- 打开浏览器访问显示的本地地址（通常是 http://localhost:8501）
- 详细使用说明请参考 `使用指南.md`

## 📊 评估体系

### v2.0 专业版评估维度
1. **内容专业度** (25%) - 垂类专注度、内容深度
2. **数据表现** (25%) - CPE、CPM等关键指标
3. **受众匹配度** (20%) - 粉丝画像与品牌契合度
4. **商业价值** (20%) - 合作案例、商业化能力
5. **成长潜力** (10%) - 增长趋势、发展空间

## 📝 批量评估

使用 `示例数据模板.csv` 文件进行批量评估：
1. 下载模板文件
2. 填入达人数据
3. 在系统中上传文件
4. 获得批量评估结果
