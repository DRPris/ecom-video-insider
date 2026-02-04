"""
查询 Google AI Studio API 支持的模型列表
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# 配置 API Key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ 请在 .env 文件中配置 GEMINI_API_KEY")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 80)
print("🔍 查询可用的 Gemini 模型")
print("=" * 80)
print()

# 列出所有支持 generateContent 的模型
print("支持 generateContent 的模型：")
print("-" * 80)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description}")
        print(f"   Supported Methods: {', '.join(model.supported_generation_methods)}")
        print()

print("=" * 80)
print("💡 提示: 使用上面列出的模型名称（不包含 'models/' 前缀）")
print("=" * 80)
