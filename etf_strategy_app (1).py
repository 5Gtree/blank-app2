import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_qqq_data():
    try:
        qqq = yf.Ticker("QQQ")
        data = qqq.history(period="1d")
        if data.empty:
            return None, None
        qqq_price = data['Close'].iloc[-1]
        qqq_history = qqq.history(period="200d")['Close']
        if len(qqq_history) < 200:
            return None, None
        qqq_sma = qqq_history.mean()
        return qqq_price, qqq_sma
    except:
        return None, None

def get_vix_data():
    try:
        vix = yf.Ticker("^VIX")
        data = vix.history(period="1d")
        if data.empty:
            return None
        return data['Close'].iloc[-1]
    except:
        return None

def fetch_fgi():
    try:
        url = 'https://feargreedmeter.com/'
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        fgi_element = soup.find('div', class_='text-center text-4xl font-semibold mb-1 text-white')
        if fgi_element:
            fgi_text = fgi_element.text.strip()
            return int(fgi_text) if fgi_text.isdigit() else None
        return None
    except:
        return None

def fetch_pci():
    try:
        url = 'https://ycharts.com/indicators/cboe_equity_put_call_ratio'
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        td_elements = soup.find_all('td', class_='col-6')
        for td in td_elements:
            try:
                return float(td.text.strip().replace(',', ''))
            except:
                continue
        return None
    except:
        return None

def interpret_fgi(fgi):
    if fgi is None:
        return "N/A"
    if fgi <= 25:
        return "Extreme Fear (Possible Buy Signal)"
    elif fgi <= 45:
        return "Fear (Possible Buy Signal)"
    elif fgi <= 55:
        return "Neutral (Hold or Wait)"
    elif fgi <= 75:
        return "Greed (Possible Sell Signal)"
    else:
        return "Extreme Greed (Possible Sell Signal)"

def interpret_pci(pci):
    if pci is None:
        return "N/A"
    if pci > 0.95:
        return "Bearish Sentiment (Possible Buy Signal)"
    elif pci < 0.65:
        return "Bullish Sentiment (Possible Sell Signal)"
    else:
        return "Neutral Sentiment (Hold or Wait)"

def interpret_vix(vix):
    if vix is None:
        return "N/A"
    if vix < 15:
        return "Low Volatility (Bullish)"
    elif vix < 25:
        return "Moderate Volatility (Neutral)"
    else:
        return "High Volatility (Bearish)"

# --- Streamlit App ---
st.set_page_config(page_title="ETF 리밸런싱 전략", layout="centered")
st.title("📊 시장 심리 기반 ETF 전략")

qqq_price, qqq_sma = get_qqq_data()
fgi = fetch_fgi()
pci = fetch_pci()
vix = get_vix_data()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 QQQ")
    st.metric("현재가", f"{qqq_price:.2f}" if qqq_price else "N/A")
    st.metric("200일 평균", f"{qqq_sma:.2f}" if qqq_sma else "N/A")

with col2:
    st.subheader("🧠 Fear & Greed")
    st.metric("FGI", f"{fgi}" if fgi is not None else "N/A", interpret_fgi(fgi))
    st.metric("Put/Call Ratio", f"{pci:.2f}" if pci else "N/A", interpret_pci(pci))
    st.metric("VIX", f"{vix:.2f}" if vix else "N/A", interpret_vix(vix))

st.info("본 전략은 시장 심리 지표를 기반으로 ETF 리밸런싱 타이밍을 보조합니다.")
