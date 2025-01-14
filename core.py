import json
import yfinance as yf
import pandas as pd
import plotly.utils
import plotly.graph_objects as go
from pandas_datareader import data as pdr


# Yahoo 데이터 크롤링
def get_yahoo_data(stock_code):
    yf.pdr_override()
    data = pdr.get_data_yahoo(stock_code)
    return data


# 데이터 전처리
def remove_outlier(data):
    # Adj Close 열만 남기기
    data = data.loc[:, ["Adj Close"]]
    # 결측 데이터 제거
    data.dropna(inplace=True)
    # 윤년 데이터 제거
    original_data = data[~((data.index.month == 2) & (data.index.day == 29))]
    return original_data


# 매년 첫 거래일의 종가(Adj Close) 찾기
def get_first_value(data):
    data["year"] = data.index.year
    data["month"] = data.index.month
    data["day"] = data.index.day
    data = data.groupby("year").first()
    data.rename(columns={"Adj Close": "first"}, inplace=True)
    return data.loc[:, ["first"]]


# 매년 최고 종가(Adj Close) 찾기
def get_max_value(data):
    data["year"] = data.index.year
    data["month"] = data.index.month
    data["day"] = data.index.day
    data = data.groupby("year").max()
    data.rename(columns={"Adj Close": "max"}, inplace=True)
    return data.loc[:, ["max"]]


# 매년 최저 종가(Adj Close) 찾기
def get_min_value(data):
    data["year"] = data.index.year
    data["month"] = data.index.month
    data["day"] = data.index.day
    data = data.groupby("year").min()
    data.rename(columns={"Adj Close": "min"}, inplace=True)
    return data.loc[:, ["min"]]


# Max % 계산: (최고 종가/첫 거래일 종가 - 1) * 100
def get_max_diff(data):
    data["max_diff"] = round((data["max"] / data["first"] - 1) * 100, 2)
    return data


# MDD % 계산: (최저 종가/첫 거래일 종가 - 1) * 100 -> 소수점 둘째자리까지
def get_min_diff(data):
    data["min_diff"] = round((data["min"] / data["first"] - 1) * 100, 2)
    return data


# 가장 마지막 종가 DD % 계산
def get_last_diff(data):
    last_value = data.iloc[-1]["Adj Close"]
    first_value = get_first_value(data).iloc[-1]["first"]
    last_diff = round((last_value / first_value - 1) * 100, 2)
    return last_diff



def mdd(stock_code):
    stock_code = stock_code.upper()
    data = get_yahoo_data(stock_code)
    original_data = remove_outlier(data)
    first_data = get_first_value(original_data)
    max_data = get_max_value(original_data)
    min_data = get_min_value(original_data)
    merged_data = pd.merge(first_data, max_data, left_index=True, right_index=True, how="left")
    merged_data = pd.merge(merged_data, min_data, left_index=True, right_index=True, how="left")
    max_diff = get_max_diff(merged_data)
    min_diff = get_min_diff(max_diff)
    last_diff = get_last_diff(original_data)
    final_data = min_diff.loc[:, ["max_diff", "min_diff"]]
    final_data.rename(columns={"max_diff": "Max%", "min_diff": "MDD%"}, inplace=True)
    fig = go.Figure(
        data=[
            go.Bar(
                x=final_data.index,
                y=final_data["Max%"],
                text=final_data["Max%"],
                textfont=dict(
                    # size=12,
                    color="#01B150",
                ),
                name="Max%",
                marker=dict(
                    color="#01B150",
                ),
                textposition="outside",
                # width=0.2,
            ),
            go.Bar(
                x=final_data.index,
                y=final_data["MDD%"],
                text=final_data["MDD%"],
                textangle=0,
                cliponaxis=False,
                textfont=dict(
                    # size=12,
                    color="#FF0000",
                ),
                name="MDD%",
                marker=dict(
                    color="#FF0000",
                ),
                textposition="outside",
                # width=0.2,
            )
        ],
        layout=go.Layout(
            # barmode="group",
            height=600,
        )
    )
    fig.update_layout(
        title={
            "text": f"{stock_code} Max, MDD",
            "xanchor": "center",
            "x": 0.5,
            "yanchor": "top",
            "y": 1.0,
            "font": dict(size=24),
        },
        title_pad_t=5,
        xaxis={"title": None},
        yaxis={"title": None},
        coloraxis={"showscale": False},
        margin=dict(l=30, r=30, t=30, b=30),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.1,
            xanchor="right",
            x=1.0,
            title=None,
        ),
        annotations=[
            dict(
                text=f"가장 마지막 거래일의 DD는 {last_diff}% 입니다.",
                x=0.5,
                y=1.06,
                xref="paper",
                yref="paper",
                showarrow=False,
                bgcolor="#ff7f0e",
                borderpad=4,
                font=dict(
                    color="#ffffff"
                )
            )
        ],
    )
    fig.update_xaxes(tickmode="linear")
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graph_json
