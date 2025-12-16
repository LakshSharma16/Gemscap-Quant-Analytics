import requests
import pandas as pd

BINANCE_URL = "https://api.binance.com/api/v3/klines"

def fetch_data(symbol, interval, limit=300):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    r = requests.get(BINANCE_URL, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()
    df = pd.DataFrame(data, columns=[
        "time", "open", "high", "low", "close",
        "volume", "ct", "qv", "nt", "tb", "tq", "ignore"
    ])

    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["close"] = df["close"].astype(float)

    return df.set_index("time")[["close"]]
