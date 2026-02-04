"""
E-Com Video Insider - 安全版本前端
使用后端 API，不暴露任何第三方 API Keys
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="E-Com Video Insider (Secure)",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. Custom CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF004E;
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
# 4. 配置
# ---------------------------------------------------------
BACKEND_API_URL = "http://localhost:8000"  # 后端 API 地址

# ---------------------------------------------------------
# 5. Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 用户只需要输入访问令牌
    user_token = st.text_input(
        "Your Access Token", 
        type="password",
        help="从管理员处获取你的个人访问令牌"
    )
    
    # 显示用户信息和配额
    if user_token:
        try:
            headers = {"Authorization": f"Bearer {user_token}"}
            response = requests.get(f"{BACKEND_API_URL}/api/user", headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                st.success(f"✅ 已登录: {user_info['username']}")
                
                # 显示配额信息
                quota_used = user_info['quota_used']
                quota_total = user_info['quota_monthly']
                quota_remaining = user_info['quota_remaining']
                
                st.metric("剩余配额", f"{quota_remaining} / {quota_total}")
                st.progress(quota_used / quota_total)
                
            else:
                st.error("❌ 无效的访问令牌")
        except Exception as e:
            st.warning(f"⚠️ 无法连接到后端服务器")
    
    st.info("💡 Tip: Use a video under 2 minutes for best results.")
    
    st.divider()
    
    # 历史记录
    st.subheader("🕒 History")
    if st.session_state.analysis_history:
        for item in reversed(st.session_state.analysis_history[-5:]):
            st.text(f"• {item['author']} - {item['timestamp']}")
    else:
        st.text("No analysis yet")

# ---------------------------------------------------------
# 6. Main Content
# ---------------------------------------------------------

st.markdown("<h1 style='text-align: center;'>🛍️ E-Com Video Insider</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>逆向工程竞品视频，生成 Lazada 爆款脚本</p>", unsafe_allow_html=True)

st.divider()

# 输入框
video_url = st.text_input(
    "Paste TikTok/Shorts URL here:",
    placeholder="https://www.tiktok.com/@5.minute.recipes/video/7588608011745250591"
)

# 分析按钮
if st.button("🚀 Analyze Now"):
    if not user_token:
        st.error("❌ 请先在侧边栏输入你的访问令牌")
    elif not video_url:
        st.error("❌ 请输入视频 URL")
    else:
        try:
            # 调用后端 API
            headers = {"Authorization": f"Bearer {user_token}"}
            payload = {"video_url": video_url}
            
            # 阶段 1: 发送请求
            with st.spinner("📥 Step 1/3: Fetching video data..."):
                response = requests.post(
                    f"{BACKEND_API_URL}/api/analyze",
                    json=payload,
                    headers=headers,
                    timeout=180  # 3 分钟超时
                )
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("✅ Analysis complete!")
                
                # 保存结果
                st.session_state.current_result = result
                st.session_state.analysis_history.append({
                    'author': result['metadata'].get('author', 'Unknown'),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                
                # 显示结果
                st.divider()
                
                # 左右两栏
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📊 Video Metadata")
                    metadata = result['metadata']
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>👤 {metadata.get('author', 'N/A')}</h4>
                        <p><strong>Description:</strong> {metadata.get('description', 'N/A')[:100]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 互动数据
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("👍 Likes", f"{metadata.get('likes', 0):,}")
                        st.metric("💬 Comments", f"{metadata.get('comments', 0):,}")
                    with col_b:
                        st.metric("👁️ Views", f"{metadata.get('views', 0):,}")
                        st.metric("🔄 Shares", f"{metadata.get('shares', 0):,}")
                
                with col2:
                    st.subheader("🤖 AI Analysis")
                    
                    analysis = result['analysis']
                    
                    # Tab 页面
                    tab1, tab2, tab3 = st.tabs(["翻拍脚本", "逻辑拆解", "原始数据"])
                    
                    with tab1:
                        if 'lazada_adaptation_brief' in analysis:
                            st.markdown(analysis['lazada_adaptation_brief'])
                    
                    with tab2:
                        if 'structure_breakdown' in analysis:
                            st.json(analysis['structure_breakdown'])
                    
                    with tab3:
                        st.json(analysis)
                
                # 下载按钮
                st.divider()
                col_d1, col_d2 = st.columns(2)
                
                with col_d1:
                    st.download_button(
                        label="📥 Download JSON Report",
                        data=json.dumps(result, indent=2, ensure_ascii=False),
                        file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                with col_d2:
                    if 'lazada_adaptation_brief' in analysis:
                        st.download_button(
                            label="📄 Download Script (Markdown)",
                            data=analysis['lazada_adaptation_brief'],
                            file_name=f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
            
            elif response.status_code == 401:
                st.error("❌ 无效的访问令牌，请检查你的 Access Token")
            elif response.status_code == 429:
                st.error("❌ 已达到配额限制，请联系管理员升级")
            else:
                st.error(f"❌ 分析失败: {response.text}")
                
        except requests.exceptions.Timeout:
            st.error("❌ 请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            st.error("❌ 无法连接到后端服务器，请确保后端正在运行")
        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")

# ---------------------------------------------------------
# 7. Footer
# ---------------------------------------------------------
st.divider()
st.markdown(
    "<p style='text-align: center; color: gray;'>E-Com Video Insider v0.3.0 (Secure) | Built with ❤️ by Manus AI</p>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: gray;'>Powered by Apify + Google Gemini 1.5 Pro</p>",
    unsafe_allow_html=True
)
