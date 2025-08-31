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

with open("fond_utveckling.txt", "a", encoding="utf-8") as f:
    f.write(text + "\n")

print("Data sparad!")
