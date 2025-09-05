import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 页面基础设置 ---
st.set_page_config(
    page_title="小红书达人智能评估工具",
    page_icon="🎯",
    layout="wide"
)

# --- 初始化Session State ---
# 用于跨页面刷新存储已评估的达人列表
if 'shortlist' not in st.session_state:
    st.session_state.shortlist = []

# --- 核心计算函数 ---

# 根据粉丝数计算得分 (1-5分)
def score_followers(followers):
    if followers >= 500000: return 5
    if followers >= 100000: return 4
    if followers >= 50000: return 3
    if followers >= 10000: return 2
    return 1

# 根据互动率计算得分 (1-5分)
def score_engagement_rate(rate):
    rate_percent = rate * 100
    if rate_percent >= 5: return 5
    if rate_percent >= 3: return 4
    if rate_percent >= 1: return 3
    if rate_percent >= 0.5: return 2
    return 1
    
# 根据广告笔记占比计算风险分 (1-5分，分数越高风险越低)
def score_ad_ratio(ratio):
    ratio_percent = ratio * 100
    if ratio_percent <= 10: return 5
    if ratio_percent <= 20: return 4
    if ratio_percent <= 40: return 3
    if ratio_percent <= 60: return 2
    return 1

# --- 侧边栏：权重配置 ---
st.sidebar.title("🎯 评估模型权重配置")
st.sidebar.markdown("---")
st.sidebar.info("请根据当前市场活动的目标，调整各个维度的权重。权重总和应为100%。")

w_influence = st.sidebar.slider("影响力 (粉丝数、曝光)", 0, 100, 20, 5, key="w_influence")
w_content = st.sidebar.slider("内容质量 (垂直、专业)", 0, 100, 25, 5, key="w_content")
w_engagement = st.sidebar.slider("互动表现 (互动率、评论)", 0, 100, 30, 5, key="w_engagement")
w_fit = st.sidebar.slider("商业契合度 (粉丝画像、调性)", 0, 100, 25, 5, key="w_fit")

# 权重归一化处理，确保总和为1
total_weight = w_influence + w_content + w_engagement + w_fit
if total_weight == 0:
    st.sidebar.error("权重总和不能为0！")
    st.stop()
else:
    weights = {
        "influence": w_influence / total_weight,
        "content": w_content / total_weight,
        "engagement": w_engagement / total_weight,
        "fit": w_fit / total_weight,
    }
    st.sidebar.success(f"当前权重总和: {int(total_weight/total_weight*100)}%")


# --- 主界面 ---
st.title("👩‍💻 小红书达人智能评估工具")
st.markdown("填入达人的各项数据，系统将根据侧边栏配置的权重模型，自动生成评估结果。")

# --- 评估方法说明 ---
with st.expander("📖 评估方法与计算逻辑说明", expanded=False):
    st.markdown("""
    ### 🎯 评估维度与评分标准
    
    #### 1️⃣ **影响力评分** (基于粉丝数)
    - 50万+ 粉丝 → 5分
    - 10-50万 粉丝 → 4分  
    - 5-10万 粉丝 → 3分
    - 1-5万 粉丝 → 2分
    - <1万 粉丝 → 1分
    
    #### 2️⃣ **内容质量评分** (三项平均)
    - 内容垂直度 (1-5分，人工评估)
    - 图文/视频质量 (1-5分，人工评估)  
    - 文案专业度 (1-5分，人工评估)
    - **最终得分 = (垂直度 + 质量 + 专业度) ÷ 3**
    
    #### 3️⃣ **互动表现评分** (基于互动率)
    - ≥5% 互动率 → 5分
    - 3-5% 互动率 → 4分
    - 1-3% 互动率 → 3分
    - 0.5-1% 互动率 → 2分
    - <0.5% 互动率 → 1分
    
    #### 4️⃣ **商业契合度评分** (两项平均)
    - 粉丝画像匹配度 (1-5分，人工评估)
    - 品牌调性匹配度 (1-5分，人工评估)
    - **最终得分 = (粉丝匹配 + 调性匹配) ÷ 2**
    
    #### 5️⃣ **风险评分** (基于广告笔记占比)
    - ≤10% 广告占比 → 5分 (低风险)
    - 10-20% 广告占比 → 4分
    - 20-40% 广告占比 → 3分
    - 40-60% 广告占比 → 2分
    - >60% 广告占比 → 1分 (高风险)
    
    ---
    
    ### ⚖️ **综合评分计算公式**
    
    ```
    最终得分 = 影响力得分 × 影响力权重 
             + 内容质量得分 × 内容权重
             + 互动表现得分 × 互动权重  
             + 商业契合度得分 × 契合度权重
    ```
    
    **注意：** 风险评分用于展示但不参与最终加权计算
    
    ---
    
    ### 🏆 **合作建议分级标准**
    
    | 得分范围 | 等级 | 建议 |
    |---------|------|------|
    | **4.2-5.0** | 💎 A+级 | 顶尖人选，优先合作 |
    | **3.8-4.2** | ✅ A级 | 优质人选，强烈推荐 |
    | **3.0-3.8** | 👍 B级 | 备选考虑，有潜力 |
    | **<3.0** | 🤔 C级 | 暂不考虑 |
    
    ⚠️ **特殊情况：** 如存在负面舆情，无论得分多高都标记为"高风险-不建议合作"
    """)

st.markdown("---")


# --- 布局：输入区 & 结果区 ---
col1, col2 = st.columns([0.55, 0.45])

with col1:
    st.header("👤 达人数据输入")
    
    # --- 基础信息 ---
    with st.expander("基础信息", expanded=True):
        kol_name = st.text_input("达人昵称或小红书号", placeholder="例如：时尚博主A")
        kol_url = st.text_input("主页链接 (选填)", placeholder="https://www.xiaohongshu.com/user/profile/...")

    # --- 数据指标 ---
    with st.expander("核心数据指标", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            followers = st.number_input("粉丝数", min_value=0, value=50000, step=1000)
        with c2:
            avg_engagement_rate = st.number_input("近30天平均互动率 (%)", min_value=0.0, value=2.5, step=0.1, format="%.2f") / 100

    # --- 主观评价 ---
    with st.expander("主观评估 (请滑动打分)", expanded=True):
        # 内容质量
        st.subheader("🎨 内容质量")
        c1, c2, c3 = st.columns(3)
        with c1:
            content_verticality = st.slider("内容垂直度", 1, 5, 4, help="内容是否聚焦特定领域")
        with c2:
            content_quality = st.slider("图文/视频质量", 1, 5, 4, help="视觉呈现是否精美、专业")
        with c3:
            content_professionalism = st.slider("文案专业度", 1, 5, 3, help="文案是否流畅、有深度")
        
        # 商业契合度
        st.subheader("🤝 商业契合度")
        c1, c2 = st.columns(2)
        with c1:
            fan_profile_fit = st.slider("粉丝画像匹配度", 1, 5, 4)
        with c2:
            brand_style_fit = st.slider("品牌调性匹配度", 1, 5, 3)

    # --- 风险评估 ---
    with st.expander("风险与成本评估"):
        c1, c2 = st.columns(2)
        with c1:
            ad_note_ratio = st.number_input("广告笔记占比 (%)", min_value=0.0, value=20.0, step=1.0, format="%.1f") / 100
        with c2:
            has_negative_pr = st.radio("是否有负面舆情?", ("否", "是"), index=0)

# --- 在所有输入完成后，进行计算 ---
if kol_name:
    # 1. 计算各维度得分
    influence_score = score_followers(followers)
    content_score = (content_verticality + content_quality + content_professionalism) / 3
    engagement_score = score_engagement_rate(avg_engagement_rate)
    fit_score = (fan_profile_fit + brand_style_fit) / 2
    risk_score = score_ad_ratio(ad_note_ratio)

    # 2. 计算加权总分
    final_score = (
        influence_score * weights["influence"] +
        content_score * weights["content"] +
        engagement_score * weights["engagement"] +
        fit_score * weights["fit"]
    )
    
    # 3. 生成合作建议
    recommendation = ""
    if has_negative_pr == "是":
        recommendation = "❌ 高风险-不建议合作"
    elif final_score >= 4.2:
        recommendation = "💎 A+级 - 顶尖人选，优先合作"
    elif final_score >= 3.8:
        recommendation = "✅ A级 - 优质人选，强烈推荐"
    elif final_score >= 3.0:
        recommendation = "👍 B级 - 备选考虑，有潜力"
    else:
        recommendation = "🤔 C级 - 暂不考虑"
    
    # --- 右侧结果展示区 ---
    with col2:
        st.header("📈 评估结果")
        st.metric(label="**综合推荐指数**", value=f"{final_score:.2f}", 
                  delta=f"{round((final_score/5-0.6)*100, 1)}%", 
                  delta_color="normal", help="分数范围1-5分，越高越好")
        
        st.markdown(f"#### 合作建议: **{recommendation}**")
        st.markdown("---")
        
        # --- 雷达图 ---
        st.subheader("能力雷达图")
        categories = ['影响力', '内容质量', '互动表现', '商业契合度', '风险规避']
        values = [influence_score, content_score, engagement_score, fit_score, risk_score]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=kol_name
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )),
            showlegend=True,
            height=350,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # --- 详细计算过程 ---
        with st.expander("🧮 详细计算过程", expanded=False):
            st.markdown("### 📊 各维度得分明细")
            
            # 创建得分明细表格
            score_details = pd.DataFrame({
                "评估维度": ["影响力", "内容质量", "互动表现", "商业契合度", "风险规避"],
                "原始数据": [
                    f"{followers:,} 粉丝",
                    f"垂直度:{content_verticality} 质量:{content_quality} 专业度:{content_professionalism}",
                    f"{avg_engagement_rate*100:.1f}% 互动率",
                    f"粉丝匹配:{fan_profile_fit} 调性匹配:{brand_style_fit}",
                    f"{ad_note_ratio*100:.1f}% 广告占比"
                ],
                "计算得分": [
                    f"{influence_score:.1f}",
                    f"{content_score:.1f}",
                    f"{engagement_score:.1f}",
                    f"{fit_score:.1f}",
                    f"{risk_score:.1f}"
                ],
                "权重占比": [
                    f"{weights['influence']*100:.1f}%",
                    f"{weights['content']*100:.1f}%",
                    f"{weights['engagement']*100:.1f}%",
                    f"{weights['fit']*100:.1f}%",
                    "不参与加权"
                ],
                "加权得分": [
                    f"{influence_score * weights['influence']:.2f}",
                    f"{content_score * weights['content']:.2f}",
                    f"{engagement_score * weights['engagement']:.2f}",
                    f"{fit_score * weights['fit']:.2f}",
                    "—"
                ]
            })
            
            st.dataframe(score_details, use_container_width=True, hide_index=True)
            
            st.markdown("### 🧮 最终得分计算")
            st.code(f"""
最终得分 = 影响力得分 × 影响力权重 + 内容质量得分 × 内容权重 + 互动表现得分 × 互动权重 + 商业契合度得分 × 契合度权重

最终得分 = {influence_score:.1f} × {weights['influence']:.2f} + {content_score:.1f} × {weights['content']:.2f} + {engagement_score:.1f} × {weights['engagement']:.2f} + {fit_score:.1f} × {weights['fit']:.2f}

最终得分 = {influence_score * weights['influence']:.2f} + {content_score * weights['content']:.2f} + {engagement_score * weights['engagement']:.2f} + {fit_score * weights['fit']:.2f} = {final_score:.2f}
            """)
            
            st.markdown("### 🎯 决策逻辑")
            if has_negative_pr == "是":
                st.warning("⚠️ **风险判断：** 存在负面舆情，直接标记为高风险，不建议合作")
            else:
                if final_score >= 4.2:
                    st.success("🏆 **A+级判断：** 得分 ≥ 4.2，顶尖人选")
                elif final_score >= 3.8:
                    st.success("✅ **A级判断：** 得分 3.8-4.2，优质人选")
                elif final_score >= 3.0:
                    st.info("👍 **B级判断：** 得分 3.0-3.8，备选考虑")
                else:
                    st.warning("🤔 **C级判断：** 得分 < 3.0，暂不考虑")

    # --- 添加到待选列表功能 ---
    st.markdown("---")
    if st.button(f"🚀 将 {kol_name} 添加到待选列表", use_container_width=True):
        new_entry = {
            "达人昵称": kol_name,
            "综合指数": round(final_score, 2),
            "合作建议": recommendation,
            "粉丝数": followers,
            "互动率(%)": round(avg_engagement_rate * 100, 2),
            "影响力分": round(influence_score, 2),
            "内容分": round(content_score, 2),
            "互动分": round(engagement_score, 2),
            "契合度分": round(fit_score, 2),
            "风险分": round(risk_score, 2),
            "有无负面": has_negative_pr,
            "主页链接": kol_url
        }
        st.session_state.shortlist.append(new_entry)
        st.success(f"✅ {kol_name} 已成功添加！")

# --- 显示待选列表 ---
if st.session_state.shortlist:
    st.markdown("## 📋 待选达人列表")
    
    df_shortlist = pd.DataFrame(st.session_state.shortlist)
    st.dataframe(df_shortlist, use_container_width=True)
    
    # --- 导出功能 ---
    csv = df_shortlist.to_csv(index=False).encode('utf-8-sig') # 使用utf-8-sig确保中文在Excel中不乱码
    
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="📥 下载待选列表 (CSV)",
            data=csv,
            file_name="xiaohongshu_shortlist.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        if st.button("清空列表", use_container_width=True, type="secondary"):
            st.session_state.shortlist = []
            st.experimental_rerun() # 重新运行刷新页面