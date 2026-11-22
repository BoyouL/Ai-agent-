# 網路資安流量異常診斷與防護建議 Agent（指定作業 2）

本專案為「AI Agent 系統實作」課程之指定作業 2 雛形系統，延續作業 1 專案規劃，實作具備 **ReAct 推理架構**、**自訂外部工具（Tool Use）** 與 **Podman 容器化部署** 之資安流量診斷 Agent。

## 1. 系統環境與安裝執行

### 前置需求
- **Python**: 3.11+
- **Container Engine**: Podman
- **LLM Server**: Ollama（預載 `qwen2.5:7b` 模型）

### 方式 A：使用 Podman 容器執行（推薦）
```bash
# 1. 於本機生成測試用 CSV 資料集 (data/sample_traffic.csv 與 data/bad_traffic.csv)
python train_model.py

# 2. 建置 Podman Image（建置過程會自動訓練 Random Forest 模型並封裝進映像檔）
podman build -t netflow-security-agent:v1 .

# 3. 啟動本機 Ollama 並允許容器連線（Windows PowerShell 範例）
# $env:OLLAMA_HOST="0.0.0.0"; ollama serve

# 4. 啟動 Podman 容器並掛載 data 資料夾執行測試
podman run --rm \
  -e OLLAMA_BASE_URL="[http://host.containers.internal:11434](http://host.containers.internal:11434)" \
  -v ./data:/app/data:Z \
  netflow-security-agent:v1