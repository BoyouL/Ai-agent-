import os
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from src.tools import csv_validator_tool, ml_inference_tool

ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

llm = ChatOllama(
    model=ollama_model,
    base_url=ollama_url,
    temperature=0
)

tools = [csv_validator_tool, ml_inference_tool]

system_prompt = """你是一位專業的企業網路安全營運中心（SOC）資安分析 Agent。
當使用者提供網路流量 CSV 檔案要求診斷時，請嚴格依照以下 ReAct 步驟執行：
1. 第一步必須先呼叫 `csv_validator_tool` 檢查檔案是否存在及欄位是否齊全。
2. 如果工具回傳 `[Error]`，請立刻停止後續動作，直接向使用者解釋錯誤原因與修正方式，絕對不要呼叫 `ml_inference_tool`。
3. 如果驗證 `[Success]`，接著呼叫 `ml_inference_tool` 取得機器學習模型的推論結果。
4. 最後根據模型推論的觀察結果（Observation），以繁體中文產出結構清晰的資安診斷報告與初步防護建議。
"""

agent = create_react_agent(llm, tools, prompt=system_prompt)

def run_test(query: str):
    print("=" * 60)
    print(f"👤 使用者輸入：{query}")
    print("=" * 60)
    for step in agent.stream({"messages": [("user", query)]}, stream_mode="values"):
        last_msg = step["messages"][-1]
        last_msg.pretty_print()

if __name__ == "__main__":
    run_test("請幫我分析 data/sample_traffic.csv 這份網路流量紀錄，判斷是否有資安攻擊？")
    run_test("請幫我檢查 data/bad_traffic.csv 的流量狀態。")