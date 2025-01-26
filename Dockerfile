# 使用 NVIDIA CUDA 基礎映像
FROM nvidia/cuda:11.8.0-base-ubuntu22.04

# 安裝基礎工具
RUN apt-get update && apt-get install -y \
    python3 python3-pip git curl wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 安裝 Jupyter Notebook 和 Python 套件
RUN pip3 install --no-cache-dir notebook jupyterlab numpy pandas matplotlib

# 安裝 VS Code Server
RUN wget -O vscode-server.tar.gz "https://update.code.visualstudio.com/latest/server-linux-x64/stable" && \
    mkdir -p /root/.vscode-server && \
    tar -xzvf vscode-server.tar.gz --strip-components=1 -C /root/.vscode-server && \
    rm vscode-server.tar.gz

# 設置工作目錄
WORKDIR /workspace

# 暴露必要的端口
EXPOSE 8888 8080

# 啟動 Jupyter Notebook 和 VS Code Server
CMD ["sh", "-c", "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root & /root/.vscode-server/bin/code-server --host 0.0.0.0 --port 8080"]

