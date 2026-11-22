import os
import joblib
import pandas as pd
from langchain_core.tools import tool

REQUIRED_COLUMNS = [
    "Src_IP", "Dst_IP", "Protocol",
    "Flow_Duration", "Total_Fwd_Packets", "Total_Backward_Packets"
]
FEATURE_COLUMNS = ["Flow_Duration", "Total_Fwd_Packets", "Total_Backward_Packets"]
MODEL_PATH = os.getenv("MODEL_PATH", "ids_model.pkl")

@tool
def csv_validator_tool(file_path: str) -> str:
    """
    檢查網路流量 CSV 檔案是否存在，並驗證是否包含模型所需的必要特徵欄位。
    輸入參數 file_path: CSV 檔案的路徑（例如 data/sample_traffic.csv）。
    """
    try:
        if not os.path.exists(file_path):
            return f"[Error] 找不到指定的檔案：{file_path}，請確認檔案路徑是否正確。"
        if not file_path.endswith(".csv"):
            return "[Error] 檔案格式錯誤，僅支援 .csv 格式。"

        df = pd.read_csv(file_path)
        if df.empty:
            return "[Error] CSV 檔案內容為空，無法進行分析。"

        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            return f"[Error] 檔案缺少必要特徵欄位：{', '.join(missing_cols)}。"

        return (
            f"[Success] CSV 驗證通過！共 {len(df)} 筆流量紀錄，欄位完整。"
            f"請繼續呼叫 ml_inference_tool 進行異常偵測。"
        )
    except Exception as e:
        return f"[Error] 讀取 CSV 時發生錯誤：{str(e)}"


@tool
def ml_inference_tool(file_path: str) -> str:
    """
    載入訓練好的 Random Forest 入侵偵測模型 (ids_model.pkl)，對已驗證的 NetFlow CSV 進行異常流量分類預測。
    輸入參數 file_path: 已通過驗證的 CSV 檔案路徑。
    """
    try:
        if not os.path.exists(MODEL_PATH):
            return f"[Error] 找不到模型檔案 {MODEL_PATH}，請先執行 train_model.py。"

        df = pd.read_csv(file_path)

        for col in FEATURE_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="raise")

        model = joblib.load(MODEL_PATH)
        X_test = df[FEATURE_COLUMNS]
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)

        df["Prediction"] = preds
        attack_df = df[df["Prediction"] == 1]
        total_count = len(df)
        attack_count = len(attack_df)

        if attack_count > 0:
            avg_conf = probs[preds == 1][:, 1].mean() * 100
            top_ip = attack_df["Src_IP"].mode()[0]
            return (
                f"[Prediction Result] 偵測到高風險異常流量！\n"
                f"- 總流量筆數：{total_count} 筆\n"
                f"- 異常攻擊筆數：{attack_count} 筆（佔比 {attack_count/total_count*100:.1f}%）\n"
                f"- 判定攻擊類別：Botnet（殭屍網路活動）\n"
                f"- 模型平均信心水準：{avg_conf:.1f}%\n"
                f"- 主要可疑來源 IP：{top_ip}"
            )
        else:
            avg_conf = probs[:, 0].mean() * 100
            return (
                f"[Prediction Result] 所有流量皆為正常（Normal）。\n"
                f"- 總流量筆數：{total_count} 筆，平均信心水準：{avg_conf:.1f}%。"
            )
    except ValueError:
        return "[Error] 特徵欄位中包含非數值字串（如 N/A），導致模型推論失敗，請清理數據後重試。"
    except Exception as e:
        return f"[Error] 模型推論過程發生例外錯誤：{str(e)}"