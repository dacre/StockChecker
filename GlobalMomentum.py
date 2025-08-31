# created using chatgpt

import requests
from datetime import datetime

# Ange Avanza-fond ID
fond_id = "4075"  # LF Global Indexnära

# Avanza API URL
url = f"https://www.avanza.se/_api/fund-guide/fund/{fond_id}"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"Fel vid hämtning av data: {e}")
    exit(1)

try:
    fond_namn = data.get("name", "Okänd fond")
    three_months = data.get("development", {}).get("threeMonths")
    six_months = data.get("development", {}).get("sixMonths")
    one_year = data.get("development", {}).get("oneYear")
    
    # Skapa textblock
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = f"""{date_str}
    
    Fond: {fond_namn}
    3 mån: {three_months:.2%}
    6 mån: {six_months:.2%}
    12 mån: {one_year:.2%}
    """
    
    # Append till fil
    with open("fond_utveckling.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")
    
    print("Data har sparats till fond_utveckling.txt")
except Exception as e:
    print(f"Fel vid skrivning av data: {e}")
    exit(1)
