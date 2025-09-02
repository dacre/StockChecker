# created using chatgpt

import yfinance as yf
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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

def add_and_sort_rankings(results):
    periods = ["3m", "6m", "12m"]

    # Sätt ranking för varje period
    for period in periods:
        # Sortera resultat med högst avkastning först
        sorted_res = sorted(
            results,
            key=lambda r: (r["returns"][period] is not None, r["returns"][period]),
            reverse=True
        )
        # Tilldela ranking (1 = bäst)
        for rank, r in enumerate(sorted_res, start=1):
            if "rankings" not in r:
                r["rankings"] = {}
            r["rankings"][period] = rank

    # Summera rankingar
    for r in results:
        r["rankings"]["total"] = sum(
            r["rankings"][p] for p in periods if p in r["rankings"]
        )

    # Sortera efter total ranking
    results_sorted = sorted(results, key=lambda r: r["rankings"]["total"])
    return results_sorted

def calc_ma_higher_then_price(ticker, days):
    if days > 250:
        raise ValueError("too many days")
    fund = yf.Ticker(ticker)
    
    # Hämta 1 års historik (daglig data)
    hist = fund.history(period="1y")
    
    # Räkna 200 dagars glidande medelvärde (referens: 12-månaders (≈ 252 handelsdagar))
    hist["MA12m"] = hist["Close"].rolling(window=days).mean()
    
    # Senaste värde
    latest_date = hist.index[-1].strftime("%Y-%m-%d")
    latest_price = hist["Close"].iloc[-1]
    latest_ma12 = hist["MA12m"].iloc[-1]
    
    print(f"pris: {latest_price:.2f}")
    print(f"12 mån glidande medelvärde: {latest_ma12:.2f}")
    return latest_ma12 > latest_price

# Funktion för att beräkna procentuell förändring
def calc_return(ticker, months):
    fund = yf.Ticker(ticker)
    hist = fund.history(period="1y")  # hämta 1 års data

    if hist.empty:
        return None

   # Ta bort tidszon för att undvika jämförelsefel
    if hist.index.tz is None:
        hist.index = hist.index.tz_localize("Europe/Stockholm")
    else:
        hist.index = hist.index.tz_convert("Europe/Stockholm")

    end_price = hist["Close"].iloc[-1]
    # Skatta startdatum (ungefär months*30 dagar tillbaka)
    start_date = datetime.now(ZoneInfo("Europe/Stockholm")) - timedelta(days=months*30)
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
        },
        "MA": calc_ma_higher_then_price(ticker, 200)
    }
    results.append(data)

# lägg till rankingar och sortera
results = add_and_sort_rankings(results)

# === Utskrift ===
print("Rankinglista (bäst först):")
for r in results:
    print(f"{r['name']} ({r['ticker']})")
    print("  Returns:", {k: f"{v:.2%}" if v is not None else "–" for k, v in r["returns"].items()})
    print("  MA200 över pris:", r["MA"])
    print("  Rankings:", r["rankings"])
    print()

from datetime import datetime
from zoneinfo import ZoneInfo

# === Skriv resultat till fil ===
timestamp = datetime.now(ZoneInfo("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M:%S")
with open("fond_utveckling.txt", "w", encoding="utf-8") as f:  # "w" = ersätt allt
    f.write(f"Fondrapport {timestamp} (Stockholm-tid)\n")
    f.write("="*50 + "\n\n")

    for r in results:
        f.write(f"{r['name']} ({r['ticker']})\n")
        f.write(f"  Total ranking: {r['rankings']['total']}  "
                f"(3m={r['rankings']['3m']}, 6m={r['rankings']['6m']}, 12m={r['rankings']['12m']})\n")

        ma_text = "Pris ÖVER MA200 ✅" if r["MA"] else "Pris UNDER MA200 ❌"
        f.write(f"  MA-status: {ma_text}\n\n")
