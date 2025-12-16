import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

def hedge_ratio(x, y):
    if x.nunique() <= 1 or y.nunique() <= 1:
        return np.nan
    X = sm.add_constant(x)
    model = sm.OLS(y, X).fit()
    return model.params.iloc[1]

def spread(x, y, hr):
    if pd.isna(hr):
        return pd.Series(index=x.index, dtype=float)
    return y - hr * x

def zscore(series):
    if series.std() == 0 or series.dropna().empty:
        return pd.Series(index=series.index, dtype=float)
    return (series - series.mean()) / series.std()

def rolling_corr(x, y, window=30):
    if len(x) < window:
        return pd.Series(index=x.index, dtype=float)
    return x.rolling(window).corr(y)

def adf_pvalue(series):
    s = series.dropna()
    if s.empty or s.nunique() <= 1:
        return np.nan
    try:
        return adfuller(s)[1]
    except Exception:
        return np.nan
