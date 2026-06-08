import requests
import pandas as pd
import json
from datetime import datetime

# 1. 定義你的板塊分類（你可以自己無限延伸增加個股）
SECTORS = {
    "AI伺服器組裝": ["2317", "3231", "2382", "6669"],
    "核心被動元件": ["2327", "2492", "3026"],
    "記憶體模組": ["2408", "3260", "2344", "8299"],
    "晶圓代工": ["2330", "2303", "5347"]
}

def get_legal_person_data():
    print("正在從證交所抓取三大法人買賣超資料...")
    
    # 這是證交所官方的免費個股日本人買賣超 API (以今日為例，實務上日期要自動帶當天)
    today_str = datetime.today().strftime('%Y%m%d')
    url = f"https://www.twse.com.tw/rwd/zh/fund/T86KJ7?date={today_str}&response=json"
    
    try:
        response = requests.get(url).json()
        if 'data' not in response:
            print("今日尚未開盤或資料未更新")
            return None
            
        # 整理成 Pandas 表格方便計算
        df = pd.DataFrame(response['data'], columns=response['fields'])
        return df
    except Exception as e:
        print(f"抓取失敗: {e}")
        return None

def calculate_sectors(df):
    if df is None: return
    
    # 清洗資料：把證交所的證券代號、買賣超金額拿出來，並去掉逗號轉成數字
    df['代號'] = df['證券代號'].str.strip()
    df['三大法人買賣超金額'] = df['三大法人買賣超股數'].str.replace(',', '').astype(float) # 這裡簡化用股數或自行乘以股價
    
    result_data = []
    
    # 依照我們定義的板塊去統計
    for sector_name, stocks in SECTORS.items():
        # 篩選出屬於該板塊的股票
        sector_df = df[df['代號'].isin(stocks)]
        total_money = sector_df['三大法人買賣超金額'].sum() / 100000000 # 換算成「億元」
        
        # 加速度計算：(今日買賣超 - 昨日買賣超) 
        # 註：初學者剛開始可以先設固定值，或是把每天數據存下來相減，這就是 Y 軸的「抄底力道」
        acceleration = total_money * 0.2 # 範例模擬值
        
        # 氣泡大小：用該板塊內股票的總成交量
        bubble_size = len(stocks) * 20 
        
        result_data.append([total_money, acceleration, bubble_size, sector_name])
    
    # 存成網頁讀得懂的 json 檔案
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False)
    print("資料計算完畢，已更新 data.json")

if __name__ == "__main__":
    df_data = get_legal_person_data()
    calculate_sectors(df_data)