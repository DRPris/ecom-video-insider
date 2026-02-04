"""
E-Com Video Insider - Streamlit Web App
Sprint 3: 完整的 Web 界面
"""

import streamlit as st
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# 导入 Sprint 1 和 Sprint 2 的核心模块
from src.tiktok_fetcher import TikTokFetcher
from src.video_analyzer import VideoAnalyzer

# 加载环境变量
load_dotenv()

# ---------------------------------------------------------
# 0. Password Protection (访问密码保护)
# ---------------------------------------------------------
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets.get("APP_PASSWORD", "admin123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 删除密码，避免存储
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 首次运行，显示密码输入框
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>🛍️ E-Com Video Insider</h1>
            <p style='color: #666;'>请输入访问密码</p>
        </div>
        """, unsafe_allow_html=True)
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # 密码错误
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>🛍️ E-Com Video Insider</h1>
            <p style='color: #666;'>请输入访问密码</p>
        </div>
        """, unsafe_allow_html=True)
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 密码错误，请重试")
        return False
    else:
        # 密码正确
        return True

# 检查密码
if not check_password():
    st.stop()  # 如果密码不正确，停止执行后续代码

# ---------------------------------------------------------
# 1. Page Configuration (设置页面基础风格)
# ---------------------------------------------------------
st.set_page_config(
    page_title="E-Com Video Insider",
    page_icon="🛍️",
    layout="wide",  # 宽屏模式，方便左右对比
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. Custom CSS (注入 Vibe，让界面看起来像 SaaS 产品)
# ---------------------------------------------------------
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF004E; /* TikTok/Lazada Red mix */
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        border-left: 5px solid #FF004E;
    }
    .script-box {
        background-color: #1e1e1e;
        color: #00ff41;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
    }
    .engagement-metric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 15px;
    }
    .engagement-value {
        font-size: 32px;
        font-weight: bold;
        color: #FF004E;
    }
    .engagement-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Session State 初始化
# ---------------------------------------------------------
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

if 'current_result' not in st.session_state:
    st.session_state.current_result = None

# ---------------------------------------------------------
# 4. Sidebar (侧边栏 - 设置与历史)
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key 配置
    apify_token = st.text_input(
        "Apify API Token", 
        type="password",
        value=os.getenv('APIFY_API_TOKEN', ''),
        help="从 https://console.apify.com/ 获取"
    )
    
    gemini_key = st.text_input(
        "Gemini API Key", 
        type="password",
        value=os.getenv('GEMINI_API_KEY', ''),
        help="API Key 或 KIE API Token"
    )
    
    gemini_base = st.text_input(
        "Gemini API Base URL (可选)",
        value=os.getenv('GEMINI_API_BASE', ''),
        placeholder="https://your-kie-api-endpoint.com/v1",
        help="如果使用 KIE API 或其他代理服务，请输入完整的 API Base URL"
    )
    
    st.info("💡 Tip: Use a video under 2 minutes for best results.")
    
    st.divider()
    
    # 历史记录
    st.subheader("🕒 History")
    if st.session_state.analysis_history:
        for i, item in enumerate(reversed(st.session_state.analysis_history[-5:])):
            st.text(f"• {item['author']} - {item['timestamp']}")
    else:
        st.text("No analysis yet")

# ---------------------------------------------------------
# 5. Main Content (主界面逻辑)
# ---------------------------------------------------------
st.title("🛍️ E-Com Video Insider")
st.markdown("### 逆向工程竞品视频，生成 Lazada 爆款脚本")

# 输入区域
col1, col2 = st.columns([3, 1])
with col1:
    video_url = st.text_input(
        "Paste TikTok/Shorts URL here:", 
        placeholder="https://www.tiktok.com/@user/video/...",
        key="video_url_input"
    )
with col2:
    st.write("")  # Spacer
    st.write("")  # Spacer
    analyze_btn = st.button("🚀 Analyze Now")

# ---------------------------------------------------------
# 6. 核心分析逻辑
# ---------------------------------------------------------
if analyze_btn:
    if not video_url:
        st.error("❌ 请输入 TikTok 视频 URL")
    elif not apify_token:
        st.error("❌ 请在侧边栏配置 Apify API Token")
    elif not gemini_key and not gemini_base:
        st.error("❌ 请至少配置 Gemini API Key 或 API Base URL 之一")
    else:
        try:
            # 创建统一进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 阶段 1: 获取视频元数据（点赞、评论等）
            status_text.info("🔍 分析中... 正在获取视频元数据")
            progress_bar.progress(10)
            
            fetcher = TikTokFetcher(api_token=apify_token)
            video_data = fetcher.fetch_video_data(video_url)
            
            progress_bar.progress(25)
            status_text.success(f"✅ 元数据获取成功: {video_data['author']} | {video_data['views']:,} 次观看")
            time.sleep(0.3)
            
            # 阶段 2: 下载视频并分析
            status_text.info("🔍 分析中... 正在下载视频")
            progress_bar.progress(30)
            
            # 传入 api_base 参数（如果提供）
            analyzer = VideoAnalyzer(
                api_key=gemini_key if gemini_key else None,
                api_base=gemini_base if gemini_base else None
            )
            
            # 使用 yt-dlp 下载视频并分析
            video_path = analyzer.download_video_with_ytdlp(video_url)
            progress_bar.progress(50)
            status_text.success("✅ 视频下载完成")
            time.sleep(0.3)
            
            # 上传到 Gemini 并分析
            status_text.info("🔍 分析中... 正在上传到 Gemini API")
            progress_bar.progress(60)
            video_file = analyzer.upload_to_gemini(video_path)
            progress_bar.progress(70)
            
            # 调用 Gemini 进行分析
            status_text.info("🤖 分析中... AI 正在分析视频内容")
            progress_bar.progress(75)
            # 组合系统提示词和用户提示词
            combined_prompt = f"""{analyzer.system_prompt}

---

Now, please analyze the following video according to the framework above.
Return your analysis in valid JSON format.
"""
            response = analyzer.model.generate_content([video_file, combined_prompt])
            
            # 解析 JSON 响应
            # Gemini 可能返回的格式:
            # 1. 纯 JSON: {"video_structure": ...}
            # 2. Markdown 代码块: ```json\n{...}\n```
            # 3. 带文字说明: Here is the analysis:\n{...}
            
            response_text = response.text.strip()
            
            # 尝试提取 JSON
            try:
                # 方法 1: 直接解析
                analysis_result = json.loads(response_text)
            except json.JSONDecodeError:
                # 方法 2: 提取 Markdown 代码块中的 JSON
                import re
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', response_text, re.DOTALL)
                if json_match:
                    analysis_result = json.loads(json_match.group(1))
                else:
                    # 方法 3: 查找第一个 { 和最后一个 }
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        json_str = response_text[start_idx:end_idx+1]
                        analysis_result = json.loads(json_str)
                    else:
                        # 如果都失败，显示原始响应
                        st.error("❌ AI 返回的内容不是有效的 JSON 格式")
                        st.text_area("原始响应", response_text, height=300)
                        st.stop()
            
            progress_bar.progress(90)
            status_text.success("✅ AI 分析完成")
            time.sleep(0.3)
            
            # 阶段 3: 保存结果
            status_text.info("📊 分析中... 正在生成报告")
            progress_bar.progress(95)
            
            # 构建完整报告
            full_report = {
                'video_data': video_data,
                'analysis': analysis_result,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 保存到 session state
            st.session_state.current_result = full_report
            st.session_state.analysis_history.append({
                'author': video_data['author'],
                'timestamp': full_report['timestamp']
            })
            
            progress_bar.progress(100)
            status_text.success("✅ 分析完成！报告已生成")
            time.sleep(0.5)
            
            # 清除进度条
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ 分析失败: {str(e)}")
            st.exception(e)

# ---------------------------------------------------------
# 7. Result Dashboard (核心展示区)
# ---------------------------------------------------------
if st.session_state.current_result:
    result = st.session_state.current_result
    video_data = result['video_data']
    analysis = result['analysis']
    
    st.divider()
    st.header("📊 Analysis Results")
    
    # ---------------------------------------------------------
    # 左侧：原始视频数据
    # ---------------------------------------------------------
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        st.subheader("📹 Original Video Data")
        
        # 视频基本信息
        st.markdown(f"""
        <div class="metric-card">
            <b>Author:</b> @{video_data['author']}<br>
            <b>Description:</b> {video_data['description'][:100]}...<br>
            <b>Duration:</b> {video_data['duration']}s<br>
            <b>Published:</b> {datetime.fromtimestamp(video_data['publish_time']).strftime('%Y-%m-%d')}
        </div>
        """, unsafe_allow_html=True)
        
        # 互动数据
        st.markdown("#### 📊 Engagement Metrics")
        
        st.markdown(f"""
        <div class="engagement-metric">
            <div class="engagement-value">{video_data['views']:,}</div>
            <div class="engagement-label">👁️ Views</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="engagement-metric">
            <div class="engagement-value">{video_data['likes']:,}</div>
            <div class="engagement-label">❤️ Likes</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="engagement-metric">
            <div class="engagement-value">{video_data['comments']:,}</div>
            <div class="engagement-label">💬 Comments</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="engagement-metric">
            <div class="engagement-value">{video_data['shares']:,}</div>
            <div class="engagement-label">🔄 Shares</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 计算互动率
        engagement_rate = ((video_data['likes'] + video_data['comments']) / video_data['views'] * 100) if video_data['views'] > 0 else 0
        st.markdown(f"""
        <div class="engagement-metric">
            <div class="engagement-value">{engagement_rate:.2f}%</div>
            <div class="engagement-label">📈 Engagement Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # 右侧：AI 分析结果
    # ---------------------------------------------------------
    with right_col:
        st.subheader("🤖 AI Analysis Results")
        
        # Top Row: Metrics
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        with meta_col1:
            st.markdown(f"""<div class="metric-card"><b>Sentiment:</b><br>{analysis['video_metadata']['estimated_sentiment']}</div>""", unsafe_allow_html=True)
        with meta_col2:
            st.markdown(f"""<div class="metric-card"><b>Hook Type:</b><br>{analysis['structure_breakdown']['hook_type']}</div>""", unsafe_allow_html=True)
        with meta_col3:
            st.markdown(f"""<div class="metric-card"><b>Difficulty:</b><br>{analysis['lazada_adaptation_brief']['remake_difficulty']}</div>""", unsafe_allow_html=True)
        
        st.divider()
        
        # Tabs for detailed view
        tab1, tab2, tab3 = st.tabs(["🎬 Remake Brief (执行脚本)", "🧠 Logic Breakdown (逻辑拆解)", "🔍 Raw Data"])
        
        with tab1:
            st.subheader("🎥 Ready-to-Shoot Script")
            st.markdown("把这个脚本发给你的拍摄团队或剪辑师：")
            st.markdown(f"""<div class="script-box"><pre>{analysis['lazada_adaptation_brief']['script_template']}</pre></div>""", unsafe_allow_html=True)
            
            st.info(f"🌏 **Localization Tip:** {analysis['lazada_adaptation_brief']['localization_tip']}")
        
        with tab2:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### The Hook (0-3s)")
                st.write(analysis['structure_breakdown']['hook_description'])
                
                st.markdown("#### The Pain Point")
                st.write(analysis['structure_breakdown']['pain_point_addressed'])
                
            with col_b:
                st.markdown("#### The Product Reveal")
                st.write(f"**Timestamp:** {analysis['structure_breakdown']['product_reveal_timestamp']}")
                st.write(f"**Selling Point:** {analysis['structure_breakdown']['key_selling_proposition']}")
                
                st.markdown("#### Why It Works")
                st.write(analysis['creative_insight']['why_it_works'])
                
                st.markdown("#### Visual Style")
                st.write(analysis['creative_insight']['visual_style'])
        
        with tab3:
            st.json(result)
    
    # ---------------------------------------------------------
    # 导出功能
    # ---------------------------------------------------------
    st.divider()
    st.subheader("📥 Export Report")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        # 导出 JSON
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"analysis_{video_data['author']}_{int(time.time())}.json",
            mime="application/json"
        )
    
    with export_col2:
        # 导出 Markdown 脚本
        markdown_script = f"""# Video Analysis Report

## Original Video
- **Author**: @{video_data['author']}
- **Views**: {video_data['views']:,}
- **Likes**: {video_data['likes']:,}
- **Engagement Rate**: {engagement_rate:.2f}%

## AI Analysis

### Hook Strategy
{analysis['structure_breakdown']['hook_description']}

### Remake Script
{analysis['lazada_adaptation_brief']['script_template']}

### Localization Tip
{analysis['lazada_adaptation_brief']['localization_tip']}
"""
        st.download_button(
            label="📝 Download Script (MD)",
            data=markdown_script,
            file_name=f"script_{video_data['author']}_{int(time.time())}.md",
            mime="text/markdown"
        )
    
    with export_col3:
        st.button("🔄 Analyze Another Video", on_click=lambda: st.session_state.update({'current_result': None}))

# ---------------------------------------------------------
# 8. Footer
# ---------------------------------------------------------
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p>E-Com Video Insider v1.0.0 | Created by DorisP</p>
    <p>Powered by Apify + Google Gemini 1.5 Pro</p>
</div>
""", unsafe_allow_html=True)
