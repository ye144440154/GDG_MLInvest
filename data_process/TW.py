# %pip install yfinance pandas requests beautifulSoup4 json
import pandas as pd
import requests
import os
import json
import time
import warnings
from bs4 import BeautifulSoup
from datetime import datetime


warnings.filterwarnings("ignore")


################################################################
def log(message):
    log_path = "data_process/TW_log.txt"
    with open(log_path, "a", encoding="utf-8") as file:
        file.write(f"{message}\n")


################################################################
def patch(message):
    patch_path = "data_process/TW_patch.txt"
    with open(patch_path, "a", encoding="utf-8") as file:
        file.write(f"{message}\n")


################################################################
def data_clean(data, df, sheet_type, season):

    if sheet_type == "I" or sheet_type == "B":
        if season == 1 or data.empty:
            data["會計項目"] = df.iloc[:, 0]
            data["Q1金額"] = ""
            data["Q1百分比(%)"] = ""
            data["Q2金額"] = ""
            data["Q2百分比(%)"] = ""
            data["Q3金額"] = ""
            data["Q3百分比(%)"] = ""
            data["Q4金額"] = ""
            data["Q4百分比(%)"] = ""
            data[f"Q{season}金額"] = df.iloc[:, 1]
            data[f"Q{season}百分比(%)"] = df.iloc[:, 2]
        else:
            data[f"Q{season}金額"] = df.iloc[:, 1]
            data[f"Q{season}百分比(%)"] = df.iloc[:, 2]

    elif sheet_type == "S":

        if season == 1 or data.empty:
            data["會計項目"] = df.iloc[:, 0]
            data["Q1金額"] = ""
            data["Q2金額"] = ""
            data["Q3金額"] = ""
            data["Q4金額"] = ""
            data["會計項目"] = df.iloc[:, 0]
            data[f"Q{season}金額"] = df.iloc[:, 1]
        else:
            data["會計項目"] = df.iloc[:, 0]
            data[f"Q{season}金額"] = df.iloc[:, 1]

    return data


################################################################
def get_financial_statement(sheet_type, co_id, year, season):

    while True:
        """
        sheet_type 會計表類型 = I(income statement) B(Balance sheet) S(Statement of cash flows)
        co_id="" #四位數公司代碼
        year="" #國歷年分
        season="" #1~4
        """
        sheet_code = ""
        if sheet_type == "I":
            sheet_code = "4"
        elif sheet_type == "B":
            sheet_code = "3"
        elif sheet_type == "S":
            sheet_code = "5"
        else:
            print("Invalid sheet_type!")
            log("Invalid sheet_type!")
            return pd.DataFrame()
        year = str(year)
        season = str(season)

        url = f"https://mopsov.twse.com.tw/mops/web/t164sb0{sheet_code}?encodeURIComponent=1&step=1&firstin=1&off=1&keyword4=&code1=&TYPEK2=&checkbtn=&queryName=co_id&inpuType=co_id&TYPEK=all&isnew=false&co_id={co_id}&year={year}&season=0{season}"
        headers = {"User-Agent": "Mozilla/5.0"}
        sleep_time = 0.5
        timeout = 5
        try_out = 10
        response = requests.get(url, headers=headers, timeout=timeout)
        response.encoding = "utf8"  # 根據網頁編碼設定，若非 Big5 可調整

        for _ in range(try_out):
            try:

                html_content = response.text

                # 使用 BeautifulSoup 解析 HTML

                soup = BeautifulSoup(html_content, "html.parser")

                # 找到 <div id="table01">
                div_table = soup.find("div", id="table01")

                # 將 <div id="table01"> 中的 HTML 轉換為字串，再用 pandas 讀取表格
                table_html = str(div_table)

                tables = pd.read_html(table_html)

                for table in tables:
                    if (
                        table.shape[0] > 10
                    ):  # 因為tables裡面有其他東西ex.說明文字 故只取長度比較長的目標資料

                        print(
                            f"TW_{co_id}_{year}_{season}_{sheet_type}  爬蟲完成,休眠{sleep_time}秒"
                        )
                        log(
                            f"TW_{co_id}_{year}_{season}_{sheet_type}  爬蟲完成,休眠{sleep_time}秒"
                        )
                        time.sleep(sleep_time)
                        return table

                print(f"no data about TW_{co_id}_{year}_{season}_{sheet_type} ")
                log(f"no data about TW_{co_id}_{year}_{season}_{sheet_type} ")
                return pd.DataFrame()

            except:

                print(f"狀態碼:{response.status_code} ")
                log(f"狀態碼:{response.status_code}")

                log("伺服器拒絕回應 睡個5秒 ZZzzzz...")
                time.sleep(5)
                log("重新嘗試")

                continue

        if response.status_code == 200:
            patch(
                f"下次啟動將從 {co_id} 開始(中止檔案:TW_{co_id}_{year}_{season}_{sheet_type}時間:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")})"
            )
            os._exit()
        log(f"no data about TW_{co_id}_{year}_{season}_{sheet_type} ")
        return pd.DataFrame()


################################################################
def get_annual_financial(sheet_type, co_id, industry, year, base_dir):

    save_path = os.path.join(base_dir, industry, co_id, str(year))
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    data = pd.DataFrame()
    for season in range(1, 5):
        df = get_financial_statement(sheet_type, co_id, year, season)
        if not (df.empty):
            data_clean(data, df, sheet_type, season)

    data.to_csv(
        os.path.join(save_path, f"TW_{co_id}_{year}_{sheet_type}.csv"),
        index=False,
        encoding="utf-8-sig",
    )  # 第一個table1是目錄 需要的是第二個
    # data.to_csv("Test.csv", index=False, encoding="utf-8-sig")


################################################################
def fetch_fundamental_data():

    # 讀取 JSON 檔案
    json_path = "data_process/TW_stock.json"
    with open(json_path, "r", encoding="utf-8") as f:
        tw_stock = json.load(f)

    # 讀取log檔
    next_stock = ""
    patch_path = "data_process/TW_patch.txt"
    with open(patch_path, "r", encoding="utf-8") as file:
        line = file.read()
        if (line == "") or ("完整執行完畢" in line):
            file.close()
            f = open(patch_path, "w", encoding="utf-8")
            f.close()
        else:
            _, next_stock, _, _ = f.readline().split(" ")

    log_path = "data_process/TW_log.txt"
    with open(log_path, "w", encoding="utf-8") as file:
        file.write(f"TW.py於{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}啟動\n")

    # 檔案儲存根目錄
    base_dir = "data_process/TW"

    # 確保目錄存在
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    end_year = 112
    year_range = 1

    for company_code, info in tw_stock.items():
        code = info.get("代號")
        industry = info.get("產業別")

        if len(code) == 4 and industry != "" and next_stock in code:  # 過濾非公司股票
            # print(code,"  ",industry)
            next_stock = ""
            for year in range(end_year - year_range, end_year):
                get_annual_financial("I", code, industry, year, base_dir)  # 取得損益表
                get_annual_financial(
                    "B", code, industry, year, base_dir
                )  # 取得資產負債表
                get_annual_financial(
                    "S", code, industry, year, base_dir
                )  # 取得現金流量表

    log(f"程式已於{datetime.now().strftime("%Y-%m-%d %H:%M:%S") }完整執行完畢")
    patch(f"程式已於{datetime.now().strftime("%Y-%m-%d %H:%M:%S") }完整執行完畢")

    return 0


if __name__ == "__main__":
    fetch_fundamental_data()
