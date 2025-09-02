# created using chatgpt

import yfinance as yf
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# List of funds (ticker, regular name)
tickers = [
    ("0P00005U1J.ST", "Avanza Zero"),
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
    tie_breaker = "MA"

    for period in periods + [tie_breaker]:
        sorted_res = sorted(
            results,
            key=lambda r: (r["returns"][period] is not None, r["returns"][period]),
            reverse=True
        )
        for rank, r in enumerate(sorted_res, start=1):
            if "rankings" not in r:
                r["rankings"] = {}
            r["rankings"][period] = rank

    for r in results:
        r["rankings"]["total"] = sum(
            r["rankings"][p] for p in periods if p in r["rankings"]
        )

    results_sorted = sorted(
        results,
        key=lambda r: (r["rankings"]["total"], r["rankings"][tie_breaker])
    )
    return results_sorted


def calc_ma_higher_then_price(ticker, days):
    if days > 250:
        raise ValueError("too many days")
    fund = yf.Ticker(ticker)
    hist = fund.history(period="1y")
    
    # Calculate x days moving average (reference: 12 months (≈ 252 trading days))
    hist["MA12m"] = hist["Close"].rolling(window=days).mean()

    latest_date = hist.index[-1].strftime("%Y-%m-%d")
    latest_price = hist["Close"].iloc[-1]
    latest_ma12 = hist["MA12m"].iloc[-1]
    
    return (latest_price - latest_ma12) / latest_price

def calc_return(ticker, months):
    fund = yf.Ticker(ticker)
    hist = fund.history(period="1y")  

    if hist.empty:
        return None

   # Handle timezone
    if hist.index.tz is None:
        hist.index = hist.index.tz_localize("Europe/Stockholm")
    else:
        hist.index = hist.index.tz_convert("Europe/Stockholm")

    end_price = hist["Close"].iloc[-1]
    # Estimate start date: months*30 days
    start_date = datetime.now(ZoneInfo("Europe/Stockholm")) - timedelta(days=months*30)
    hist_filtered = hist.loc[hist.index >= start_date]
   
    if hist_filtered.empty:
        return None

    start_price = hist_filtered["Close"].iloc[0]
    return (end_price / start_price - 1)

results = []
days = 200
for ticker, name in tickers:
    data = {
        "ticker": ticker,
        "name": name,
        "returns": {
            "3m": calc_return(ticker, 3),
            "6m": calc_return(ticker, 6),
            "12m": calc_return(ticker, 12),
            "MA": calc_ma_higher_then_price(ticker, days)
        },
        
    }
    results.append(data)

results = add_and_sort_rankings(results)

print("Rankinglista (bäst först):")
for r in results:
    print(f"{r['name']} ({r['ticker']})")
    print(f"  Returns:", {k: f"{v:.2%}" if v is not None else "–" for k, v in r["returns"].items()})
    print(f"  Moving average for {days} over price: {r['returns']['MA']:.2%}")
    print(f"  Rankings:", r['rankings'])
    print()

timestamp = datetime.now(ZoneInfo("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M:%S")
with open("fond_utveckling.txt", "w", encoding="utf-8") as f:  
    f.write(f"Fondrapport {timestamp} (Stockholm-tid)\n")
    f.write("="*50 + "\n\n")

    for r in results:
        f.write(f"{r['name']} ({r['ticker']})\n")
        f.write(f"  Total ranking: {r['rankings']['total']}  "
                f"(3m={r['rankings']['3m']}, 6m={r['rankings']['6m']}, 12m={r['rankings']['12m']})\n")
        f.write(f"  MA-status: {r['returns']['MA']}\n\n")
