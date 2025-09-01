# created using chatgpt

import yfinance as yf
from datetime import datetime, timedelta
target_tz = pytz.timezone('CEST')

# Lista med fonder/aktier (ticker, vanligt namn)
tickers = [
    ("0P00005U1J.ST", "Avanza Zero"),
    ("0P0001ECQR.ST", "Avanza Global"),
    ("0P00000L2Y.ST", "Länsförsäkringar Japan Index"),
    ("SGBS.MI", "WisdomTree Physical Swiss Gold"),
    ("0P0000K9E7.ST", "Länsförsäkringar USA Index"),
    ("0P0001H4TL.ST", "Avanza Emerging Markets"),
    ("0P0001J6WY.ST", "Avanza Europa"),
    ("0P00009NT9.ST", "Spiltan Räntefond Sverige"),
    ("0P00015E1M.ST", "Storebrand Obligation A SEK"),
    ("0P0001BMMY.ST", "PLUS Småbolag Sverige Index"),
]

# Funktion för att beräkna procentuell förändring
def calc_return(ticker, months):
    fund = yf.Ticker(ticker)
    hist = fund.history(period="1y")  # hämta 1 års data

    if hist.empty:
        return None

   # Ta bort tidszon för att undvika jämförelsefel
    #hist.index = hist.index.tz_localize(target_tz)
    end_price = hist["Close"].iloc[-1]
    # Skatta startdatum (ungefär months*30 dagar tillbaka)
    start_date = datetime.today(target_tz) - timedelta(days=months*30)
    hist_filtered = hist.loc[hist.index >= start_date]
   
    if hist_filtered.empty:
        return None

    start_price = hist_filtered["Close"].iloc[0]
    return (end_price / start_price - 1)

# Spara allt i en lista av dictar
results = []
for ticker, name in tickers:
    data = {
        "ticker": ticker,
        "name": name,
        "returns": {
            "3m": calc_return(ticker, 3),
            "6m": calc_return(ticker, 6),
            "12m": calc_return(ticker, 12)
        }
    }
    results.append(data)

# Skriv ut som kontroll
for r in results:
    print(f"{r['name']} ({r['ticker']})")
    for period, val in r["returns"].items():
        if val is not None:
            print(f"  {period}: {val:.2%}")
    print()

# Append:a till fil med datum
date_str = datetime.now(target_tz).strftime("%Y-%m-%d %H:%M:%S")
with open("fond_utveckling.txt", "a", encoding="utf-8") as f:
    f.write(date_str + "\n\n")
    for r in results:
        f.write(f"{r['name']} ({r['ticker']})\n")
        for period, val in r["returns"].items():
            if val is not None:
                f.write(f"  {period}: {val:.2%}\n")
        f.write("\n")
