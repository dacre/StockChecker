# created using chatgpt

# Filename: fetch_fund_yahoo.py
import yfinance as yf
from datetime import datetime

ticker = "0P0000YVZ3.ST"  # Länsförsäkringar Global Indexnära
fund = yf.Ticker(ticker)

# Vi hämtar historisk data och beräkna 3-månars utveckling manuellt
hist = fund.history(period="3mo")
if len(hist) < 2:
    raise ValueError("För lite historisk data")

start_price = hist['Close'].iloc[0]
end_price = hist['Close'].iloc[-1]
pct_change = (end_price / start_price - 1) * 100

date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
text = f"""{date_str}

Fond: {ticker}
3 mån utveckling: {pct_change:.2f}%

"""

import yfinance as yf
from datetime import datetime

ticker = "0P0000YVZ3.ST"  # LF Global Aktiefond A på Yahoo
fund = yf.Ticker(ticker)

# Hämta 2 års historik (daglig data)
hist = fund.history(period="2y")

# Räkna 12-månaders (≈ 252 handelsdagar) glidande medelvärde
hist["MA12m"] = hist["Close"].rolling(window=252).mean()

# Senaste värde
latest_date = hist.index[-1].strftime("%Y-%m-%d")
latest_price = hist["Close"].iloc[-1]
latest_ma12 = hist["MA12m"].iloc[-1]

print(f"Senaste datum: {latest_date}")
print(f"Senaste stängningskurs: {latest_price:.2f}")
print(f"12 mån glidande medelvärde: {latest_ma12:.2f}")

with open("fond_utveckling.txt", "a", encoding="utf-8") as f:
    f.write(text + "\n")

print("Data sparad!")
