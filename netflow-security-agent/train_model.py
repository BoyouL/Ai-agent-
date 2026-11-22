import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

def main():
    os.makedirs("data", exist_ok=True)

    # 1. 建立模擬的 NetFlow 訓練資料集 (Normal vs Botnet)
    np.random.seed(42)
    n_samples = 400

    normal_data = pd.DataFrame({
        "Flow_Duration": np.random.randint(1000, 10000, n_samples // 2),
        "Total_Fwd_Packets": np.random.randint(5, 50, n_samples // 2),
        "Total_Backward_Packets": np.random.randint(5, 50, n_samples // 2),
        "Label": 0
    })

    botnet_data = pd.DataFrame({
        "Flow_Duration": np.random.randint(10, 400, n_samples // 2),
        "Total_Fwd_Packets": np.random.randint(120, 600, n_samples // 2),
        "Total_Backward_Packets": np.random.randint(0, 5, n_samples // 2),
        "Label": 1
    })

    train_df = pd.concat([normal_data, botnet_data], ignore_index=True)
    X = train_df[["Flow_Duration", "Total_Fwd_Packets", "Total_Backward_Packets"]]
    y = train_df["Label"]

    # 2. 訓練 Random Forest 分類模型並存檔於根目錄
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X, y)
    joblib.dump(clf, "ids_model.pkl")
    print("模型訓練完成：ids_model.pkl")

    # 3. 產生正常與攻擊混合測試檔至 data/ 資料夾
    test_samples = pd.DataFrame({
        "Src_IP": ["192.168.1.55", "192.168.1.55", "192.168.1.12", "192.168.1.88"],
        "Dst_IP": ["45.33.32.156", "45.33.32.156", "8.8.8.8", "140.112.8.116"],
        "Protocol": ["TCP", "TCP", "UDP", "TCP"],
        "Flow_Duration": [85, 110, 3500, 4200],
        "Total_Fwd_Packets": [340, 415, 15, 22],
        "Total_Backward_Packets": [1, 0, 14, 20]
    })
    test_samples.to_csv("data/sample_traffic.csv", index=False)
    print("測試檔案已生成：data/sample_traffic.csv")

    # 4. 產生缺欄位失敗測試檔至 data/ 資料夾
    bad_samples = pd.DataFrame({
        "Src_IP": ["192.168.1.99"],
        "Dst_IP": ["1.1.1.1"]
    })
    bad_samples.to_csv("data/bad_traffic.csv", index=False)
    print("失敗測試檔案已生成：data/bad_traffic.csv")

if __name__ == "__main__":
    main()