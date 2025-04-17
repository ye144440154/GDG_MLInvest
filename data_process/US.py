# %pip install sec-edgar-downloader pandas lxml edgar requests

import sys
import requests  # type: ignore
import json
import pandas as pd  # type: ignore


def search_cik(ticker_id: str):
    headers = {"User-Agent": "email@address.com"}
    cik_ticker = requests.get(
        "https://www.sec.gov/files/company_tickers.json", headers=headers
    )
    cik_ticker_dict = cik_ticker.json()

    ticker_df = pd.DataFrame.from_dict(cik_ticker_dict, orient="index")
    ticker_df["cik_str"] = (
        ticker_df["cik_str"].astype(str).str.zfill(10)
    )  # for the reqirement about url

    cik = ticker_df.loc[ticker_df["ticker"] == ticker_id.upper(), "cik_str"].values[0]

    return cik


def get_ticker_df():
    headers = {"User-Agent": "email@address.com"}
    cik_ticker = requests.get(
        "https://www.sec.gov/files/company_tickers.json", headers=headers
    )
    cik_ticker_dict = cik_ticker.json()
    print("number of recorded securities:", len(cik_ticker_dict))

    ticker_df = pd.DataFrame.from_dict(cik_ticker_dict, orient="index")
    ticker_df["cik_str"] = (
        ticker_df["cik_str"].astype(str).str.zfill(10)
    )  # for the reqirement about url

    return ticker_df


def download_acc_data(cik, acc_type: str):

    if type(cik) == str:
        cik = cik.zfill(10)
    else:
        cik = cik.astype(str).str.zfill(10)

    acc_list = get_acc_list(cik)
    if acc_type in acc_list:

        headers = {"User-Agent": "andy144440154@gmail.com"}
        companyConcept = requests.get(
            (
                f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}"
                f"/us-gaap/{acc_type}.json"
            ),
            headers=headers,
        )
        # get all filings data
        acc_df = pd.DataFrame.from_dict(companyConcept.json()["units"]["USD"])

        # get assets from 10Q forms and reset index
        acc_df = acc_df[acc_df["form"] == "10-K"]
        acc_df = acc_df.reset_index(drop=True)
        acc_df = (
            acc_df[["end", "val"]]
            .drop_duplicates(subset=["val"])
            .reset_index(drop=True)
        )
        acc_df.to_csv("./us_test.csv", index=False)
        return True
    else:
        print("download_acc_data : acc_type worng or data not exist.")
        return False


def get_acc_list(cik: int):

    if type(cik) == str:
        cik = cik.zfill(10)
    else:
        cik = cik.astype(str).str.zfill(10)

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    headers = {"User-Agent": "andy144440154@gmail.com"}

    company_facts = requests.get(url, headers=headers)
    df = pd.DataFrame(company_facts.json())
    # print(df)
    accounting_data = company_facts.json()["facts"]["us-gaap"]
    return accounting_data


def main():

    ticker_df = get_ticker_df()
    cik = "0000320193"
    print(type(cik))
    acc_type = "AccountsPayableCurrent"
    download_acc_data(cik, acc_type)


if __name__ == "__main__":
    main()
