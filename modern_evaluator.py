import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# --- 页面基础设置 ---
st.set_page_config(
    page_title="小红书达人智能评估系统 v3.0",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 全局样式 */
    .main-header {
        background: linear-gradient(135deg, #ff6b6b, #feca57);
        color: white;
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* 使用更精确的Streamlit选择器 */
    .stContainer {
        background: white !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        border: 1px solid #e1e5e9 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
        margin-bottom: 1rem !important;
        transition: transform 0.2s ease !important;
    }
    
    .stContainer:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1) !important;
    }
    
    /* Streamlit border容器样式 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border-radius: 15px !important;
        border: 1px solid #e1e5e9 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
        margin-bottom: 1.5rem !important;
        padding: 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(0,0,0,0.1) !important;
        border-color: #ff6b6b !important;
    }
    
    /* 标签样式 */
    .dimension-label {
        font-weight: bold !important;
        color: #2c3e50 !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }
    
    /* 分数显示样式 */
    .score-display {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    
    .score-s { color: #ff6b6b; }
    .score-a { color: #ff9f43; }
    .score-b { color: #10ac84; }
    .score-c { color: #feca57; }
    .score-d { color: #808e9b; }
    
    /* 权重控制器样式 */
    .weight-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ff6b6b;
        margin-bottom: 1rem;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem 0.5rem;
        }
        .stContainer {
            margin-bottom: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 初始化Session State ---
if 'evaluation_results' not in st.session_state:
    st.session_state.evaluation_results = []
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "单个评估"
if 'weights' not in st.session_state:
    st.session_state.weights = {
        "content": 0.25,
        "data": 0.25,
        "audience": 0.20,
        "business": 0.15,
        "growth": 0.15
    }

# --- 核心评分函数（保持原有逻辑）---

# 1. 内容维度评分
def score_content_focus(vertical_ratio):
    """内容垂类专注度评分 (>70%为优秀)"""
    if vertical_ratio >= 0.8: return 5
    if vertical_ratio >= 0.7: return 4
    if vertical_ratio >= 0.5: return 3
    if vertical_ratio >= 0.3: return 2
    return 1

def score_viral_rate(viral_ratio):
    """爆文率评分 (>10%为优秀)"""
    if viral_ratio >= 0.15: return 5
    if viral_ratio >= 0.1: return 4
    if viral_ratio >= 0.05: return 3
    if viral_ratio >= 0.02: return 2
    return 1

def score_completion_rate(video_ratio, completion_rate):
    """视频完播率评分"""
    if video_ratio >= 0.5 and completion_rate >= 0.4: return 5
    if video_ratio >= 0.5 and completion_rate >= 0.3: return 4
    if video_ratio >= 0.3 and completion_rate >= 0.25: return 3
    if completion_rate >= 0.2: return 2
    return 1

# 2. 数据维度评分
def score_cpe(cpe):
    """CPE评分 (低成本高价值)"""
    if cpe <= 8: return 5
    if cpe <= 15: return 4
    if cpe <= 25: return 3
    if cpe <= 40: return 2
    return 1

def score_cpm(cpm):
    """CPM评分"""
    if cpm <= 100: return 5
    if cpm <= 200: return 4
    if cpm <= 350: return 3
    if cpm <= 500: return 2
    return 1

def score_interaction_health(like_ratio, collect_ratio, comment_ratio):
    """互动健康度评分"""
    score = 0
    # 收藏占比评分 (>25%为优秀)
    if collect_ratio >= 0.25: score += 2
    elif collect_ratio >= 0.15: score += 1.5
    elif collect_ratio >= 0.1: score += 1
    
    # 评论占比评分 (5%-15%为健康)
    if 0.05 <= comment_ratio <= 0.15: score += 2
    elif 0.03 <= comment_ratio <= 0.2: score += 1.5
    elif comment_ratio >= 0.03: score += 1
    
    # 整体健康度
    if score >= 3.5: return 5
    if score >= 2.5: return 4
    if score >= 1.5: return 3
    if score >= 0.5: return 2
    return 1

def score_real_interaction(real_ratio):
    """真实互动率评分 (>80%为优秀)"""
    if real_ratio >= 0.9: return 5
    if real_ratio >= 0.8: return 4
    if real_ratio >= 0.7: return 3
    if real_ratio >= 0.6: return 2
    return 1

def score_fan_activity(activity_ratio):
    """粉丝活跃度评分 (>90%为优秀)"""
    if activity_ratio >= 0.95: return 5
    if activity_ratio >= 0.9: return 4
    if activity_ratio >= 0.85: return 3
    if activity_ratio >= 0.8: return 2
    return 1

def score_data_stability(stability_coefficient):
    """数据稳定性评分"""
    if stability_coefficient <= 0.3: return 5
    if stability_coefficient <= 0.5: return 4
    if stability_coefficient <= 0.8: return 3
    if stability_coefficient <= 1.2: return 2
    return 1

# 3. 粉丝维度评分
def score_audience_match(audience_match):
    """粉丝画像匹配度评分"""
    if audience_match >= 0.8: return 5
    if audience_match >= 0.7: return 4
    if audience_match >= 0.6: return 3
    if audience_match >= 0.5: return 2
    return 1

def score_fan_quality(real_interaction, fan_activity):
    """粉丝质量综合评分"""
    real_score = score_real_interaction(real_interaction)
    activity_score = score_fan_activity(fan_activity)
    return (real_score + activity_score) / 2

# 4. 商业维度评分
def score_brand_level(high_end_ratio):
    """品牌层级评分"""
    if high_end_ratio >= 0.6: return 5
    if high_end_ratio >= 0.4: return 4
    if high_end_ratio >= 0.25: return 3
    if high_end_ratio >= 0.15: return 2
    return 1

def score_commercial_balance(commercial_ratio):
    """商业化比例评分 (<30%为优秀)"""
    if commercial_ratio <= 0.15: return 5
    if commercial_ratio <= 0.3: return 4
    if commercial_ratio <= 0.45: return 3
    if commercial_ratio <= 0.6: return 2
    return 1

# 5. 成长性维度评分
def score_growth_trend(growth_trend):
    """增长趋势评分"""
    trend_scores = {
        "平稳上扬": 5,
        "缓慢增长": 3,
        "波动增长": 2,
        "停滞": 1,
        "异常陡增": 1
    }
    return trend_scores.get(growth_trend, 1)

def score_fan_source(search_ratio, recommend_ratio):
    """粉丝来源评分 (搜索+推荐占比高为优秀)"""
    total_quality_ratio = search_ratio + recommend_ratio
    if total_quality_ratio >= 0.7: return 5
    if total_quality_ratio >= 0.5: return 4
    if total_quality_ratio >= 0.3: return 3
    if total_quality_ratio >= 0.15: return 2
    return 1

def score_traffic_quality(search_ratio, recommend_ratio):
    """流量来源质量评分 (兼容性函数)"""
    return score_fan_source(search_ratio, recommend_ratio)

# --- 综合评估函数 ---
def comprehensive_evaluation(scores_dict, weights_dict):
    """计算综合评分"""
    final_score = sum(scores_dict[key] * weights_dict[key] for key in scores_dict.keys())
    return final_score

def get_recommendation(final_score, has_risk=False):
    """生成合作建议"""
    if has_risk:
        return "❌ 高风险 - 不建议合作"
    
    if final_score >= 4.5:
        return "💎 S级 - 顶级人选，立即签约"
    elif final_score >= 4.0:
        return "🏆 A+级 - 优质人选，优先合作"
    elif final_score >= 3.5:
        return "✅ A级 - 良好人选，推荐合作"
    elif final_score >= 3.0:
        return "👍 B级 - 备选人选，考虑合作"
    elif final_score >= 2.5:
        return "⚠️ C级 - 谨慎考虑"
    else:
        return "❌ D级 - 不建议合作"

# --- 主页面标题 ---
st.markdown("""
<div class="main-header">
    <h1>🎯 小红书达人智能评估系统 v3.0</h1>
    <p style="margin-bottom: 0; opacity: 0.9;">基于5维度专业评估模型，为您的营销决策提供数据支撑</p>
</div>
""", unsafe_allow_html=True)

# --- 模式选择区域 ---
st.markdown("### 📋 选择评估模式")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎯 单个评估", use_container_width=True):
        st.session_state.current_mode = "单个评估"

with col2:
    if st.button("📊 批量评估", use_container_width=True):
        st.session_state.current_mode = "批量评估"

with col3:
    if st.button("📈 数据对比", use_container_width=True):
        st.session_state.current_mode = "数据对比"

with col4:
    if st.button("⚙️ 系统设置", use_container_width=True):
        st.session_state.current_mode = "系统设置"

st.markdown("---")

# --- 权重配置区域（简化版，始终可见）---
if st.session_state.current_mode != "系统设置":
    with st.expander("⚖️ 快速权重调整", expanded=False):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            w_content = st.slider("内容", 0, 50, int(st.session_state.weights["content"] * 100), 5, key="w_content")
        with col2:
            w_data = st.slider("数据", 0, 50, int(st.session_state.weights["data"] * 100), 5, key="w_data")
        with col3:
            w_audience = st.slider("粉丝", 0, 50, int(st.session_state.weights["audience"] * 100), 5, key="w_audience")
        with col4:
            w_business = st.slider("商业", 0, 30, int(st.session_state.weights["business"] * 100), 5, key="w_business")
        with col5:
            w_growth = st.slider("成长", 0, 30, int(st.session_state.weights["growth"] * 100), 5, key="w_growth")
        
        # 权重归一化
        total_weight = w_content + w_data + w_audience + w_business + w_growth
        if total_weight > 0:
            st.session_state.weights = {
                "content": w_content / total_weight,
                "data": w_data / total_weight,
                "audience": w_audience / total_weight,
                "business": w_business / total_weight,
                "growth": w_growth / total_weight
            }

# --- 主要内容区域 ---
if st.session_state.current_mode == "单个评估":
    
    # 基本信息卡片
    st.markdown("### 👤 达人基本信息")
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            influencer_name = st.text_input("达人昵称", placeholder="请输入达人昵称")
        with col2:
            followers = st.number_input("粉丝数", min_value=0, value=50000, step=1000, format="%d")
        with col3:
            evaluation_date = st.date_input("评估日期", value=datetime.now())
    
    # 数据输入区域 - 使用卡片式布局
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        # 内容维度卡片
        st.markdown("### 📝 内容维度")
        with st.container(border=True):
            
            st.markdown('<span class="dimension-label">垂类专注度</span>', unsafe_allow_html=True)
            vertical_ratio = st.slider("垂类专注度", 0, 100, 75, key="vertical_ratio", 
                                     help="该达人在特定垂类领域的内容占比", label_visibility="collapsed") / 100
            
            st.markdown('<span class="dimension-label">爆文率</span>', unsafe_allow_html=True)
            viral_ratio = st.slider("爆文率", 0, 50, 12, key="viral_ratio",
                                   help="获得高互动量内容的比例", label_visibility="collapsed") / 100
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<span class="dimension-label">视频占比</span>', unsafe_allow_html=True)
                video_ratio = st.slider("视频占比", 0, 100, 60, key="video_ratio", label_visibility="collapsed") / 100
            with col_b:
                st.markdown('<span class="dimension-label">平均完播率</span>', unsafe_allow_html=True)
                completion_rate = st.slider("平均完播率", 0, 100, 35, key="completion_rate", label_visibility="collapsed") / 100
        
        # 粉丝维度卡片
        st.markdown("### 👥 粉丝维度")
        with st.container(border=True):
            
            st.markdown('<span class="dimension-label">粉丝画像重合度</span>', unsafe_allow_html=True)
            audience_match = st.slider("粉丝画像重合度", 0, 100, 75, key="audience_match",
                                     help="目标粉丝与品牌用户画像的匹配程度", label_visibility="collapsed") / 100
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<span class="dimension-label">真实互动率</span>', unsafe_allow_html=True)
                real_interaction = st.slider("真实互动率", 0, 100, 85, key="real_interaction", label_visibility="collapsed") / 100
            with col_b:
                st.markdown('<span class="dimension-label">粉丝活跃度</span>', unsafe_allow_html=True)
                fan_activity = st.slider("粉丝活跃度", 0, 100, 92, key="fan_activity", label_visibility="collapsed") / 100
        
        # 成长性维度卡片
        st.markdown("### 📈 成长性维度")
        with st.container(border=True):
            
            st.markdown('<span class="dimension-label">粉丝增长趋势</span>', unsafe_allow_html=True)
            growth_trend = st.selectbox("粉丝增长趋势", 
                ["平稳上扬", "缓慢增长", "波动增长", "停滞", "异常陡增"],
                key="growth_trend", help="分析近期粉丝增长的趋势模式", label_visibility="collapsed")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<span class="dimension-label">搜索发现占比</span>', unsafe_allow_html=True)
                search_ratio = st.slider("搜索发现占比", 0, 100, 30, key="search_ratio", label_visibility="collapsed") / 100
            with col_b:
                st.markdown('<span class="dimension-label">首页推荐占比</span>', unsafe_allow_html=True)
                recommend_ratio = st.slider("首页推荐占比", 0, 100, 40, key="recommend_ratio", label_visibility="collapsed") / 100
    
    with col_right:
        # 数据维度卡片
        st.markdown("### 📊 数据维度")
        with st.container(border=True):
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<span class="dimension-label">CPE (单次互动成本)</span>', unsafe_allow_html=True)
                cpe = st.number_input("CPE (单次互动成本)", min_value=0.0, value=15.0, step=0.5, key="cpe", label_visibility="collapsed")
            with col_b:
                st.markdown('<span class="dimension-label">CPM (千次曝光成本)</span>', unsafe_allow_html=True)
                cpm = st.number_input("CPM (千次曝光成本)", min_value=0.0, value=200.0, step=10.0, key="cpm", label_visibility="collapsed")
            
            col_c, col_d = st.columns(2)
            with col_c:
                st.markdown('<span class="dimension-label">收藏占比</span>', unsafe_allow_html=True)
                collect_ratio = st.slider("收藏占比", 0, 100, 30, key="collect_ratio", label_visibility="collapsed") / 100
            with col_d:
                st.markdown('<span class="dimension-label">评论占比</span>', unsafe_allow_html=True)
                comment_ratio = st.slider("评论占比", 0, 50, 8, key="comment_ratio", label_visibility="collapsed") / 100
            
            st.markdown('<span class="dimension-label">数据稳定性系数</span>', unsafe_allow_html=True)
            stability_coefficient = st.slider("数据稳定性系数", 0.0, 3.0, 0.6, 0.1, key="stability_coefficient",
                                             help="数据波动程度，越低越稳定", label_visibility="collapsed")
        
        # 商业维度卡片
        st.markdown("### 💼 商业维度")
        with st.container(border=True):
            
            st.markdown('<span class="dimension-label">高端品牌合作占比</span>', unsafe_allow_html=True)
            high_end_ratio = st.slider("高端品牌合作占比", 0, 100, 40, key="high_end_ratio",
                                     help="与知名/高端品牌的合作比例", label_visibility="collapsed") / 100
            
            st.markdown('<span class="dimension-label">商业化比例</span>', unsafe_allow_html=True)
            commercial_ratio = st.slider("商业化比例", 0, 100, 25, key="commercial_ratio",
                                        help="广告内容占总内容的比例", label_visibility="collapsed") / 100
        
        # 风险评估卡片
        st.markdown("### ⚠️ 风险评估")
        with st.container(border=True):
            
            st.markdown('<span class="dimension-label">负面舆情风险</span>', unsafe_allow_html=True)
            has_negative = st.radio("负面舆情风险", ["否", "是"], key="has_negative", label_visibility="collapsed") == "是"
            
            st.markdown('<span class="dimension-label">更新频率</span>', unsafe_allow_html=True)
            update_frequency = st.selectbox("更新频率", ["稳定", "偶尔断更", "经常断更"], key="update_frequency", label_visibility="collapsed")
    
    # 评估按钮和结果展示
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 开始评估", use_container_width=True, type="primary"):
            # 计算各维度得分
            content_score = (
                score_content_focus(vertical_ratio) * 0.35 +
                score_viral_rate(viral_ratio) * 0.35 +
                score_completion_rate(video_ratio, completion_rate) * 0.3
            )
            
            data_score = (
                score_cpe(cpe) * 0.3 +
                score_cpm(cpm) * 0.25 +
                score_interaction_health(0, collect_ratio, comment_ratio) * 0.25 +
                score_data_stability(stability_coefficient) * 0.2
            )
            
            audience_score = (
                score_audience_match(audience_match) * 0.5 +
                score_fan_quality(real_interaction, fan_activity) * 0.5
            )
            
            business_score = (
                score_brand_level(high_end_ratio) * 0.6 +
                score_commercial_balance(commercial_ratio) * 0.4
            )
            
            growth_score = (
                score_growth_trend(growth_trend) * 0.6 +
                score_fan_source(search_ratio, recommend_ratio) * 0.4
            )
            
            scores = {
                "content": content_score,
                "data": data_score,
                "audience": audience_score,
                "business": business_score,
                "growth": growth_score
            }
            
            # 计算综合评分
            final_score = comprehensive_evaluation(scores, st.session_state.weights)
            recommendation = get_recommendation(final_score, has_negative)
            
            # 结果展示区域
            st.markdown("### 🎯 评估结果")
            
            # 主要评分展示
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                # 获取评分等级和颜色
                if final_score >= 4.5:
                    level = "S级"
                    score_class = "score-s"
                elif final_score >= 4.0:
                    level = "A+级"
                    score_class = "score-a"
                elif final_score >= 3.5:
                    level = "A级"
                    score_class = "score-b"
                elif final_score >= 3.0:
                    level = "B级"
                    score_class = "score-c"
                elif final_score >= 2.5:
                    level = "C级"
                    score_class = "score-d"
                else:
                    level = "D级"
                    score_class = "score-d"
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="score-display {score_class}">
                        {final_score:.1f}/5.0
                    </div>
                    <h3 style="text-align: center; margin: 0;">{level}</h3>
                    <p style="text-align: center; margin: 0.5rem 0 0 0; color: #666;">{recommendation}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 详细分数展示
            st.markdown("#### 📊 各维度得分详情")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            dimensions = [
                ("内容维度", content_score, "📝"),
                ("数据维度", data_score, "📊"),
                ("粉丝维度", audience_score, "👥"),
                ("商业维度", business_score, "💼"),
                ("成长性维度", growth_score, "📈")
            ]
            
            for i, (dim_name, score, icon) in enumerate(dimensions):
                with [col1, col2, col3, col4, col5][i]:
                    score_color = "score-s" if score >= 4.5 else "score-a" if score >= 4.0 else "score-b" if score >= 3.0 else "score-c" if score >= 2.0 else "score-d"
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div style="font-size: 1.5rem;">{icon}</div>
                        <div class="score-display {score_color}" style="font-size: 1.8rem; margin: 0.5rem 0;">
                            {score:.1f}
                        </div>
                        <div style="font-size: 0.9rem; color: #666;">{dim_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 雷达图展示
            st.markdown("#### 📈 维度分析雷达图")
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=[content_score, data_score, audience_score, business_score, growth_score],
                theta=['内容维度', '数据维度', '粉丝维度', '商业维度', '成长性维度'],
                fill='toself',
                name='当前达人',
                line_color='rgb(255, 107, 107)',
                fillcolor='rgba(255, 107, 107, 0.3)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )),
                showlegend=True,
                title="五维度评估雷达图",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 保存评估结果
            result = {
                "达人昵称": influencer_name,
                "粉丝数": followers,
                "评估日期": evaluation_date.strftime("%Y-%m-%d"),
                "综合评分": final_score,
                "评级": level,
                "建议": recommendation,
                "内容维度": content_score,
                "数据维度": data_score,
                "粉丝维度": audience_score,
                "商业维度": business_score,
                "成长性维度": growth_score
            }
            
            st.session_state.evaluation_results.append(result)

elif st.session_state.current_mode == "批量评估":
    st.markdown("### 📊 批量达人评估")
    
    # 文件上传卡片
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 📁 上传评估数据")
        
        uploaded_file = st.file_uploader(
            "选择CSV文件",
            type=['csv'],
            help="请上传包含达人数据的CSV文件"
        )
        
        # 数据模板下载
        st.markdown("#### 📋 数据模板")
        template_data = {
            "达人昵称": ["示例达人A", "示例达人B"],
            "粉丝数": [50000, 120000],
            "垂类专注度": [0.75, 0.80],
            "爆文率": [0.12, 0.15],
            "视频占比": [0.6, 0.7],
            "完播率": [0.35, 0.4],
            "CPE": [15.0, 18.0],
            "CPM": [200.0, 180.0],
            "收藏占比": [0.3, 0.25],
            "评论占比": [0.08, 0.1],
            "数据稳定性": [0.6, 0.5],
            "粉丝画像重合度": [0.75, 0.8],
            "真实互动率": [0.85, 0.9],
            "粉丝活跃度": [0.92, 0.88],
            "高端品牌占比": [0.4, 0.6],
            "商业化比例": [0.25, 0.2],
            "增长趋势": ["平稳上扬", "缓慢增长"],
            "搜索占比": [0.3, 0.35],
            "推荐占比": [0.4, 0.45],
            "负面舆情": [False, False]
        }
        template_df = pd.DataFrame(template_data)
        template_csv = template_df.to_csv(index=False, encoding='utf-8-sig')
        
        st.download_button(
            label="📥 下载批量评估模板",
            data=template_csv,
            file_name="达人批量评估模板.csv",
            mime="text/csv",
            help="下载包含所有必要字段的数据模板"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"成功上传文件，包含 {len(df)} 个达人数据")
                
                # 显示数据预览
                st.markdown("#### 📋 数据预览")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("🚀 开始批量评估", type="primary"):
                    # 批量评估逻辑
                    progress_bar = st.progress(0)
                    results = []
                    
                    for i, row in df.iterrows():
                        # 实际评估逻辑
                        try:
                            # 从CSV读取数据（需要根据实际列名调整）
                            vertical_ratio = row.get('垂类专注度', 0.75)
                            viral_ratio = row.get('爆文率', 0.12)
                            video_ratio = row.get('视频占比', 0.6)
                            completion_rate = row.get('完播率', 0.35)
                            cpe = row.get('CPE', 15.0)
                            cpm = row.get('CPM', 200.0)
                            collect_ratio = row.get('收藏占比', 0.3)
                            comment_ratio = row.get('评论占比', 0.08)
                            stability = row.get('数据稳定性', 0.6)
                            audience_match = row.get('粉丝画像重合度', 0.75)
                            real_interaction = row.get('真实互动率', 0.85)
                            fan_activity = row.get('粉丝活跃度', 0.92)
                            high_end_ratio = row.get('高端品牌占比', 0.4)
                            commercial_ratio = row.get('商业化比例', 0.25)
                            growth_trend = row.get('增长趋势', '平稳上扬')
                            search_ratio = row.get('搜索占比', 0.3)
                            recommend_ratio = row.get('推荐占比', 0.4)
                            has_negative = row.get('负面舆情', False)
                            
                            # 计算各维度分数
                            content_score = (
                                score_content_focus(vertical_ratio) * 0.4 +
                                score_viral_rate(viral_ratio) * 0.3 +
                                score_completion_rate(video_ratio, completion_rate) * 0.3
                            )
                            
                            data_score = (
                                score_cpe(cpe) * 0.25 +
                                score_cpm(cpm) * 0.25 +
                                score_interaction_health(0, collect_ratio, comment_ratio) * 0.25 +
                                score_data_stability(stability) * 0.25
                            )
                            
                            audience_score = (
                                score_audience_match(audience_match) * 0.4 +
                                score_real_interaction(real_interaction) * 0.3 +
                                score_fan_activity(fan_activity) * 0.3
                            )
                            
                            business_score = (
                                score_brand_level(high_end_ratio) * 0.6 +
                                score_commercial_balance(commercial_ratio) * 0.4
                            )
                            
                            growth_score = (
                                score_growth_trend(growth_trend) * 0.6 +
                                score_fan_source(search_ratio, recommend_ratio) * 0.4
                            )
                            
                            scores = {
                                "content": content_score,
                                "data": data_score,
                                "audience": audience_score,
                                "business": business_score,
                                "growth": growth_score
                            }
                            
                            final_score = comprehensive_evaluation(scores, st.session_state.weights)
                            recommendation = get_recommendation(final_score, has_negative)
                            
                            # 获取评级
                            if final_score >= 4.5:
                                level = "S级"
                            elif final_score >= 4.0:
                                level = "A+级"
                            elif final_score >= 3.5:
                                level = "A级"
                            elif final_score >= 3.0:
                                level = "B级"
                            elif final_score >= 2.5:
                                level = "C级"
                            else:
                                level = "D级"
                                
                        except Exception as e:
                            # 如果数据不完整，使用默认评估
                            final_score = 3.0
                            level = "B级"
                            recommendation = "⚠️ 数据不完整，建议补充信息后重新评估"
                        
                        progress_bar.progress((i + 1) / len(df))
                        
                        result = {
                            "达人昵称": row.get("达人昵称", f"达人{i+1}"),
                            "粉丝数": row.get("粉丝数", 0),
                            "综合评分": round(final_score, 2),
                            "评级": level,
                            "建议": recommendation,
                            "内容维度": round(content_score, 2) if 'content_score' in locals() else 0,
                            "数据维度": round(data_score, 2) if 'data_score' in locals() else 0,
                            "粉丝维度": round(audience_score, 2) if 'audience_score' in locals() else 0,
                            "商业维度": round(business_score, 2) if 'business_score' in locals() else 0,
                            "成长性维度": round(growth_score, 2) if 'growth_score' in locals() else 0,
                            "评估时间": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        results.append(result)
                        
                        # 同时保存到session_state
                        st.session_state.evaluation_results.append(result)
                    
                    # 显示批量结果
                    st.markdown("#### 🎯 批量评估结果")
                    results_df = pd.DataFrame(results)
                    st.dataframe(results_df, use_container_width=True)
                    
                    # 导出功能
                    csv = results_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 下载评估结果",
                        data=csv,
                        file_name=f"批量评估结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            except Exception as e:
                st.error(f"文件处理出错: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_mode == "数据对比":
    st.markdown("### 📈 达人数据对比分析")
    
    if st.session_state.evaluation_results:
        # 添加概览统计
        df_results = pd.DataFrame(st.session_state.evaluation_results)
        
        # 概览指标
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("评估达人总数", len(df_results))
        with col2:
            st.metric("平均评分", f"{df_results['综合评分'].mean():.2f}")
        with col3:
            high_quality = len(df_results[df_results['综合评分'] >= 4.0])
            st.metric("优质达人数", high_quality)
        with col4:
            if len(df_results) > 0:
                st.metric("推荐合作率", f"{high_quality/len(df_results)*100:.1f}%")
            else:
                st.metric("推荐合作率", "0%")
        
        # 评分分布图
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(df_results, x='综合评分', nbins=20, 
                                  title="评分分布直方图",
                                  color_discrete_sequence=['#ff6b6b'])
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            fig_scatter = px.scatter(df_results, x='粉丝数', y='综合评分',
                                   hover_data=['达人昵称'], title="粉丝数vs评分散点图",
                                   color_discrete_sequence=['#4ecdc4'])
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            
            # 选择要对比的达人
            selected_influencers = st.multiselect(
                "选择要对比的达人",
                options=[result["达人昵称"] for result in st.session_state.evaluation_results],
                default=[result["达人昵称"] for result in st.session_state.evaluation_results[:3]]
            )
            
            if selected_influencers:
                # 筛选选中的达人数据
                selected_data = [
                    result for result in st.session_state.evaluation_results 
                    if result["达人昵称"] in selected_influencers
                ]
                
                # 对比图表
                if len(selected_data) > 1:
                    # 雷达图对比
                    fig = go.Figure()
                    
                    for data in selected_data:
                        fig.add_trace(go.Scatterpolar(
                            r=[
                                data["内容维度"],
                                data["数据维度"],
                                data["粉丝维度"],
                                data["商业维度"],
                                data["成长性维度"]
                            ],
                            theta=['内容维度', '数据维度', '粉丝维度', '商业维度', '成长性维度'],
                            fill='toself',
                            name=data["达人昵称"]
                        ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 5]
                            )),
                        showlegend=True,
                        title="达人多维度对比",
                        height=600
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # 对比表格
                st.markdown("#### 📊 详细数据对比")
                compare_df = pd.DataFrame(selected_data)
                st.dataframe(compare_df, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("暂无评估数据，请先进行达人评估")

elif st.session_state.current_mode == "系统设置":
    st.markdown("### ⚙️ 系统设置")
    
    # 权重配置卡片
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### ⚖️ 评估权重配置")
        
        st.markdown("**各维度权重设置**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            w_content = st.slider("📝 内容维度权重", 0, 50, int(st.session_state.weights["content"] * 100), 1)
            w_data = st.slider("📊 数据维度权重", 0, 50, int(st.session_state.weights["data"] * 100), 1)
            w_audience = st.slider("👥 粉丝维度权重", 0, 50, int(st.session_state.weights["audience"] * 100), 1)
        
        with col2:
            w_business = st.slider("💼 商业维度权重", 0, 30, int(st.session_state.weights["business"] * 100), 1)
            w_growth = st.slider("📈 成长性维度权重", 0, 30, int(st.session_state.weights["growth"] * 100), 1)
        
        # 权重归一化和更新
        total_weight = w_content + w_data + w_audience + w_business + w_growth
        if total_weight > 0:
            new_weights = {
                "content": w_content / total_weight,
                "data": w_data / total_weight,
                "audience": w_audience / total_weight,
                "business": w_business / total_weight,
                "growth": w_growth / total_weight
            }
            
            # 实时显示权重分布
            st.markdown("**当前权重分布:**")
            weight_col1, weight_col2, weight_col3, weight_col4, weight_col5 = st.columns(5)
            
            with weight_col1:
                st.metric("内容", f"{new_weights['content']:.1%}")
            with weight_col2:
                st.metric("数据", f"{new_weights['data']:.1%}")
            with weight_col3:
                st.metric("粉丝", f"{new_weights['audience']:.1%}")
            with weight_col4:
                st.metric("商业", f"{new_weights['business']:.1%}")
            with weight_col5:
                st.metric("成长", f"{new_weights['growth']:.1%}")
            
            if st.button("💾 保存权重设置", type="primary"):
                st.session_state.weights = new_weights
                st.success("权重设置已保存！")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 数据管理卡片
    with st.container():
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 📚 数据管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 清空评估记录", use_container_width=True):
                st.session_state.evaluation_results = []
                st.success("评估记录已清空")
        
        with col2:
            if st.session_state.evaluation_results:
                csv_data = pd.DataFrame(st.session_state.evaluation_results).to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 导出所有记录",
                    data=csv_data,
                    file_name=f"评估记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 底部信息 ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"💾 历史记录: {len(st.session_state.evaluation_results)} 条")

with col2:
    st.info(f"🎯 当前模式: {st.session_state.current_mode}")

with col3:
    st.info("🔄 版本: v3.0")
