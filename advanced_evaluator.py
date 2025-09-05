import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# --- 页面基础设置 ---
st.set_page_config(
    page_title="小红书达人智能评估系统 v2.0",
    page_icon="🎯",
    layout="wide"
)

# --- 初始化Session State ---
if 'evaluation_results' not in st.session_state:
    st.session_state.evaluation_results = []
if 'batch_mode' not in st.session_state:
    st.session_state.batch_mode = False

# --- 核心评分函数（基于专业标准）---

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
    """CPE评分 (<20为优秀)"""
    if cpe <= 10: return 5
    if cpe <= 20: return 4
    if cpe <= 35: return 3
    if cpe <= 50: return 2
    return 1

def score_cpm(cpm):
    """CPM评分 (<250为优秀)"""
    if cpm <= 150: return 5
    if cpm <= 250: return 4
    if cpm <= 400: return 3
    if cpm <= 600: return 2
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

def score_data_stability(stability_coefficient):
    """数据稳定性评分 (<0.8为优秀)"""
    if stability_coefficient <= 0.5: return 5
    if stability_coefficient <= 0.8: return 4
    if stability_coefficient <= 1.2: return 3
    if stability_coefficient <= 1.8: return 2
    return 1

# 3. 粉丝维度评分
def score_audience_match(match_ratio):
    """粉丝画像重合度评分 (>70%为优秀)"""
    if match_ratio >= 0.8: return 5
    if match_ratio >= 0.7: return 4
    if match_ratio >= 0.6: return 3
    if match_ratio >= 0.5: return 2
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

# 4. 商业维度评分
def score_brand_level(high_end_ratio):
    """历史合作品牌调性评分 (>50%高端品牌为优秀)"""
    if high_end_ratio >= 0.7: return 5
    if high_end_ratio >= 0.5: return 4
    if high_end_ratio >= 0.3: return 3
    if high_end_ratio >= 0.1: return 2
    return 1

def score_commercialization(commercial_ratio):
    """商业化比例评分 (<30%为优秀)"""
    if commercial_ratio <= 0.15: return 5
    if commercial_ratio <= 0.3: return 4
    if commercial_ratio <= 0.45: return 3
    if commercial_ratio <= 0.6: return 2
    return 1

# 5. 成长性维度评分
def score_growth_trend(growth_type):
    """粉丝增长趋势评分"""
    if growth_type == "平稳上扬": return 5
    if growth_type == "缓慢增长": return 4
    if growth_type == "波动增长": return 3
    if growth_type == "停滞": return 2
    return 1

def score_fan_source(search_ratio, recommend_ratio):
    """粉丝来源评分 (搜索+推荐占比高为优秀)"""
    total_quality_ratio = search_ratio + recommend_ratio
    if total_quality_ratio >= 0.7: return 5
    if total_quality_ratio >= 0.5: return 4
    if total_quality_ratio >= 0.3: return 3
    if total_quality_ratio >= 0.15: return 2
    return 1

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

# --- 侧边栏：评估模式选择 ---
st.sidebar.title("🎯 评估系统设置")
evaluation_mode = st.sidebar.selectbox(
    "选择评估模式",
    ["单个达人评估", "批量达人评估", "数据分析对比"]
)

# --- 权重配置 ---
st.sidebar.markdown("### ⚖️ 评估权重配置")
w_content = st.sidebar.slider("内容维度", 0, 100, 25, 5)
w_data = st.sidebar.slider("数据维度", 0, 100, 25, 5)
w_audience = st.sidebar.slider("粉丝维度", 0, 100, 20, 5)
w_business = st.sidebar.slider("商业维度", 0, 100, 15, 5)
w_growth = st.sidebar.slider("成长性维度", 0, 100, 15, 5)

# 权重归一化
total_weight = w_content + w_data + w_audience + w_business + w_growth
if total_weight > 0:
    weights = {
        "content": w_content / total_weight,
        "data": w_data / total_weight,
        "audience": w_audience / total_weight,
        "business": w_business / total_weight,
        "growth": w_growth / total_weight
    }
    st.sidebar.success(f"权重总和: {total_weight}%")

# --- 主界面 ---
st.title("🎯 小红书达人智能评估系统 v2.0")
st.markdown("**基于专业筛选标准的科学评估工具**")

# --- 评估标准说明 ---
with st.expander("📖 专业评估标准说明", expanded=False):
    st.markdown("""
    ### 🎯 五维度专业评估体系
    
    #### 1️⃣ **内容维度** (25%)
    - **垂类专注度**: >70%专注某一领域
    - **爆文率**: >10%的笔记互动量超过1000
    - **视频完播率**: 视频占比>50%且完播率>30%
    
    #### 2️⃣ **数据维度** (25%)
    - **CPE**: 单次互动成本<20为优秀
    - **CPM**: 千次曝光成本<250为优秀
    - **互动健康度**: 收藏占比>25%，评论占比5%-15%
    - **数据稳定性**: 波动系数<0.8
    
    #### 3️⃣ **粉丝维度** (20%)
    - **画像重合度**: 与目标群体重合率>70%
    - **真实互动率**: 真实互动占比>80%
    - **粉丝活跃度**: 活跃度>90%
    
    #### 4️⃣ **商业维度** (15%)
    - **品牌调性**: 高端品牌合作占比>50%
    - **商业化比例**: <30%为优秀
    
    #### 5️⃣ **成长性维度** (15%)
    - **增长趋势**: 平稳上扬最佳
    - **粉丝来源**: 搜索+推荐占比>70%
    """)

if evaluation_mode == "单个达人评估":
    # --- 单个达人评估界面 ---
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        st.header("📝 达人数据输入")
        
        # 基础信息
        with st.expander("基础信息", expanded=True):
            kol_name = st.text_input("达人昵称", placeholder="请输入达人昵称")
            kol_url = st.text_input("主页链接", placeholder="https://www.xiaohongshu.com/user/profile/...")
            followers = st.number_input("粉丝数", min_value=0, value=50000, step=1000)
        
        # 内容维度
        with st.expander("内容维度数据"):
            col_a, col_b = st.columns(2)
            with col_a:
                vertical_ratio = st.slider("垂类专注度 (%)", 0, 100, 75) / 100
                viral_ratio = st.slider("爆文率 (%)", 0, 50, 12) / 100
            with col_b:
                video_ratio = st.slider("视频占比 (%)", 0, 100, 60) / 100
                completion_rate = st.slider("平均完播率 (%)", 0, 100, 35) / 100
        
        # 数据维度
        with st.expander("数据维度"):
            col_a, col_b = st.columns(2)
            with col_a:
                cpe = st.number_input("CPE (单次互动成本)", min_value=0.0, value=15.0, step=0.5)
                cpm = st.number_input("CPM (千次曝光成本)", min_value=0.0, value=200.0, step=10.0)
            with col_b:
                collect_ratio = st.slider("收藏占比 (%)", 0, 100, 30) / 100
                comment_ratio = st.slider("评论占比 (%)", 0, 50, 8) / 100
            
            stability_coefficient = st.slider("数据稳定性系数", 0.0, 3.0, 0.6, 0.1)
        
        # 粉丝维度
        with st.expander("粉丝维度"):
            col_a, col_b = st.columns(2)
            with col_a:
                audience_match = st.slider("粉丝画像重合度 (%)", 0, 100, 75) / 100
                real_interaction = st.slider("真实互动率 (%)", 0, 100, 85) / 100
            with col_b:
                fan_activity = st.slider("粉丝活跃度 (%)", 0, 100, 92) / 100
        
        # 商业维度
        with st.expander("商业维度"):
            col_a, col_b = st.columns(2)
            with col_a:
                high_end_ratio = st.slider("高端品牌合作占比 (%)", 0, 100, 40) / 100
            with col_b:
                commercial_ratio = st.slider("商业化比例 (%)", 0, 100, 25) / 100
        
        # 成长性维度
        with st.expander("成长性维度"):
            col_a, col_b = st.columns(2)
            with col_a:
                growth_trend = st.selectbox("粉丝增长趋势", 
                    ["平稳上扬", "缓慢增长", "波动增长", "停滞", "异常陡增"])
            with col_b:
                search_ratio = st.slider("搜索发现占比 (%)", 0, 100, 30) / 100
                recommend_ratio = st.slider("首页推荐占比 (%)", 0, 100, 40) / 100
        
        # 风险评估
        with st.expander("风险评估"):
            has_negative = st.radio("是否存在负面舆情", ["否", "是"]) == "是"
            update_frequency = st.selectbox("更新频率", ["稳定", "偶尔断更", "经常断更"])
    
    # 计算评分
    if kol_name:
        # 计算各维度得分
        content_scores = {
            "垂类专注度": score_content_focus(vertical_ratio),
            "爆文率": score_viral_rate(viral_ratio),
            "完播率": score_completion_rate(video_ratio, completion_rate)
        }
        content_score = sum(content_scores.values()) / len(content_scores)
        
        data_scores = {
            "CPE": score_cpe(cpe),
            "CPM": score_cpm(cpm),
            "互动健康度": score_interaction_health(0, collect_ratio, comment_ratio),
            "数据稳定性": score_data_stability(stability_coefficient)
        }
        data_score = sum(data_scores.values()) / len(data_scores)
        
        audience_scores = {
            "画像重合度": score_audience_match(audience_match),
            "真实互动率": score_real_interaction(real_interaction),
            "粉丝活跃度": score_fan_activity(fan_activity)
        }
        audience_score = sum(audience_scores.values()) / len(audience_scores)
        
        business_scores = {
            "品牌调性": score_brand_level(high_end_ratio),
            "商业化比例": score_commercialization(commercial_ratio)
        }
        business_score = sum(business_scores.values()) / len(business_scores)
        
        growth_scores = {
            "增长趋势": score_growth_trend(growth_trend),
            "粉丝来源": score_fan_source(search_ratio, recommend_ratio)
        }
        growth_score = sum(growth_scores.values()) / len(growth_scores)
        
        # 综合评分
        dimension_scores = {
            "content": content_score,
            "data": data_score,
            "audience": audience_score,
            "business": business_score,
            "growth": growth_score
        }
        
        final_score = comprehensive_evaluation(dimension_scores, weights)
        recommendation = get_recommendation(final_score, has_negative)
        
        with col2:
            st.header("📊 评估结果")
            
            # 核心指标展示
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("综合评分", f"{final_score:.2f}", f"{(final_score-3)/2*100:+.1f}%")
            with metric_col2:
                st.metric("粉丝数", f"{followers:,}", "")
            
            st.markdown(f"### {recommendation}")
            st.markdown("---")
            
            # 五维雷达图
            st.subheader("五维能力雷达图")
            categories = ['内容维度', '数据维度', '粉丝维度', '商业维度', '成长性维度']
            values = [content_score, data_score, audience_score, business_score, growth_score]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=kol_name,
                line_color='rgb(255, 100, 100)'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                showlegend=True,
                height=400,
                title="达人能力五维分析"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 详细评分表
            with st.expander("📋 详细评分明细", expanded=True):
                detail_data = {
                    "维度": ["内容维度", "数据维度", "粉丝维度", "商业维度", "成长性维度"],
                    "得分": [f"{score:.1f}" for score in values],
                    "权重": [f"{weights['content']*100:.1f}%", f"{weights['data']*100:.1f}%", 
                            f"{weights['audience']*100:.1f}%", f"{weights['business']*100:.1f}%", 
                            f"{weights['growth']*100:.1f}%"],
                    "加权得分": [f"{values[i] * list(weights.values())[i]:.2f}" for i in range(5)]
                }
                df_detail = pd.DataFrame(detail_data)
                st.dataframe(df_detail, use_container_width=True, hide_index=True)
            
            # 保存到评估列表
            if st.button("💾 保存评估结果", use_container_width=True):
                result_data = {
                    "达人昵称": kol_name,
                    "综合评分": round(final_score, 2),
                    "推荐等级": recommendation,
                    "粉丝数": followers,
                    "内容得分": round(content_score, 2),
                    "数据得分": round(data_score, 2),
                    "粉丝得分": round(audience_score, 2),
                    "商业得分": round(business_score, 2),
                    "成长得分": round(growth_score, 2),
                    "评估时间": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.evaluation_results.append(result_data)
                st.success("✅ 评估结果已保存！")

elif evaluation_mode == "批量达人评估":
    # --- 批量评估界面 ---
    st.header("📊 批量达人评估")
    
    # 文件上传
    uploaded_file = st.file_uploader("上传达人数据文件", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        # 读取文件
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.write("预览上传的数据：")
        st.dataframe(df.head())
        
        if st.button("🚀 开始批量评估"):
            progress_bar = st.progress(0)
            results = []
            
            for idx, row in df.iterrows():
                # 这里可以根据实际CSV列名进行调整
                # 简化版批量评估逻辑
                mock_score = np.random.uniform(2.5, 4.8)  # 示例随机评分
                mock_recommendation = get_recommendation(mock_score)
                
                result = {
                    "达人昵称": row.get('达人昵称', f'达人{idx+1}'),
                    "综合评分": round(mock_score, 2),
                    "推荐等级": mock_recommendation,
                    "粉丝数": row.get('粉丝数', 0),
                }
                results.append(result)
                progress_bar.progress((idx + 1) / len(df))
            
            st.success("✅ 批量评估完成！")
            
            # 显示结果
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            # 导出功能
            csv = results_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下载评估结果",
                data=csv,
                file_name=f"批量评估结果_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    else:
        st.info("请上传包含达人数据的CSV或Excel文件进行批量评估")
        
        # 提供模板下载
        template_data = {
            "达人昵称": ["示例达人A", "示例达人B"],
            "粉丝数": [50000, 120000],
            "垂类专注度": [0.75, 0.80],
            "爆文率": [0.12, 0.15],
            "CPE": [15.0, 18.0],
            "CPM": [200.0, 180.0]
        }
        template_df = pd.DataFrame(template_data)
        template_csv = template_df.to_csv(index=False).encode('utf-8-sig')
        
        st.download_button(
            label="📋 下载数据模板",
            data=template_csv,
            file_name="达人数据模板.csv",
            mime="text/csv"
        )

elif evaluation_mode == "数据分析对比":
    # --- 数据分析对比界面 ---
    st.header("📈 达人数据分析对比")
    
    if st.session_state.evaluation_results:
        df_results = pd.DataFrame(st.session_state.evaluation_results)
        
        # 概览统计
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("评估达人总数", len(df_results))
        with col2:
            st.metric("平均评分", f"{df_results['综合评分'].mean():.2f}")
        with col3:
            high_quality = len(df_results[df_results['综合评分'] >= 4.0])
            st.metric("优质达人数", high_quality)
        with col4:
            st.metric("推荐合作率", f"{high_quality/len(df_results)*100:.1f}%")
        
        # 评分分布图
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(df_results, x='综合评分', nbins=20, 
                                  title="评分分布直方图")
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            fig_scatter = px.scatter(df_results, x='粉丝数', y='综合评分',
                                   hover_data=['达人昵称'], title="粉丝数vs评分散点图")
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # 多维对比雷达图
        if len(df_results) >= 2:
            st.subheader("🔍 达人多维对比")
            selected_kols = st.multiselect("选择要对比的达人", 
                                         df_results['达人昵称'].tolist(),
                                         default=df_results['达人昵称'].tolist()[:3])
            
            if selected_kols:
                fig_compare = go.Figure()
                
                for kol in selected_kols:
                    kol_data = df_results[df_results['达人昵称'] == kol].iloc[0]
                    values = [kol_data['内容得分'], kol_data['数据得分'], 
                             kol_data['粉丝得分'], kol_data['商业得分'], kol_data['成长得分']]
                    
                    fig_compare.add_trace(go.Scatterpolar(
                        r=values,
                        theta=['内容维度', '数据维度', '粉丝维度', '商业维度', '成长性维度'],
                        fill='toself',
                        name=kol
                    ))
                
                fig_compare.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                    showlegend=True,
                    height=500,
                    title="达人多维能力对比"
                )
                st.plotly_chart(fig_compare, use_container_width=True)
        
        # 数据表格
        st.subheader("📋 评估结果汇总")
        st.dataframe(df_results, use_container_width=True)
        
        # 清空数据选项
        if st.button("🗑️ 清空所有评估数据"):
            st.session_state.evaluation_results = []
            st.experimental_rerun()
    
    else:
        st.info("暂无评估数据，请先完成单个达人评估或批量评估")

# --- 页面底部 ---
st.markdown("---")
st.markdown("**小红书达人智能评估系统 v2.0** | 基于专业筛选标准的科学评估工具")
