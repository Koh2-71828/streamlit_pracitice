import pandas as pd
from pandas.core.reshape.concat import concat
import yfinance as yf
import altair as alt
import streamlit as st
import requests
import pandas_datareader.data as pdr
import pandas_datareader.data as DataReader
import datetime


#code ./でanaconda promptから開く
st.title("米国株価表示アプリ")

st.sidebar.write("""
# 米国株可視化
この可視化ツールを用いることで、あなたの所有している米国株のみの情報を仕入れることができます。 \n
また、持っている株価の前日時点での評価額を表示します。
""")

st.sidebar.write("""
## 表示日数選択
""")
days = st.sidebar.slider("日数",1,100,50)


st.write(f"""
### 過去**{days}**日間の株価
""")

tickers = {
    "Google":"GOOGL",
    "apple":"AAPL",
    "facebook":"FB",
    "Amazon":"AMZN",
    "Microsoft":"MSFT",
    "netflix":"NFLX",
    "Hewlett-Packard Company":"HPE",
    "NVIDIA":"NVDA",
    "AT&T":"T"
}


@st.cache
def get_data(days,tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period =f'{days}d')
        hist.index = hist.index.strftime("%d %B %Y")
        hist = hist[["Close"]]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = "Name"
        df = pd.concat([df,hist])
    return df
try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        "範囲を指定してください",
        0.0,3500.0,(0.0,3500.0)
    )


    df = get_data(days,tickers)
    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['Google', 'Amazon', 'facebook', 'apple']
    )
    if not companies:
        st.error("少なくとも一社は選択してください")
    else:
        data = df.loc[companies]
        st.write("### 株価(USD)",data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data,id_vars=["Date"]).rename(
            columns = {"value":"Stock Prices(USD)"}
        )
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8,clip=True)
            .encode(
                x = "Date:T",
                y = alt.Y("Stock Prices(USD):Q",stack = None,scale =alt.Scale(domain= [ymin,ymax])),
                color = "Name:N"
            )
        )
        st.altair_chart(chart, use_container_width = True)

except:
    st.error(
        "エラーが生じています。リロードしてください。"
    )

st.write("""
### 所有している会社の前日までの収支を計算します。
※前日の終値にて計算指定います。
""")


have_tickers = {
    "apple":"AAPL",
    "Hewlett-Packard Company":"HPE",
    "NVIDIA":"NVDA",
    "AT&T":"T"
}


have_stocks = get_data("1d",have_tickers)
have_stocks = have_stocks.set_axis(['前日終値'], axis=1)

get_stock = pd.DataFrame({
    "apple":[149.9720],
    "Hewlett-Packard Company":[14.6910],
    "NVIDIA":[206.26],
    "AT&T":[28.14]},
    index = ["取得時"]
)
get_stock = get_stock.T

count_stock = pd.DataFrame({
    "apple":[10],
    "Hewlett-Packard Company":[10],
    "NVIDIA":[10],
    "AT&T":[100]},
    index = ["所有数"]
)
count_stock  = count_stock.T

all_data = pd.concat([have_stocks,get_stock],axis = 1)


all_data = all_data.assign(差額 = all_data['前日終値'] - all_data['取得時'])
all_data = pd.concat([all_data,count_stock],axis = 1)
all_data = all_data.assign(評価額 = all_data['前日終値'] * all_data['所有数'])
all_data = all_data.assign(損益 = all_data["差額"] * all_data["所有数"])
all_data = all_data.set_axis(["APPL", "HP","NVDA","T" ], axis = 0)
st.dataframe(all_data)


d_today = datetime.date.today()
usd_yen = pdr.get_data_yahoo("JPY=X",d_today)
usd_yen = int(usd_yen["Close"][0])
sum_data = float(all_data["損益"].sum())
st.write("現在の収支")
st.write("約" + str(int(usd_yen * sum_data)) + "円")

