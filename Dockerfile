FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt /app/
COPY app_secure.py /app/
COPY src /app/src

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "app_secure.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
