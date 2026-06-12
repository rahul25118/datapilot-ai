import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import os
import json

class DataProcessingEngine:
    @staticmethod
    def inspect_and_profile(file_path: str) -> dict:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported data file matrix format configuration.")

        row_count, col_count = df.shape
        missing_matrix = df.isnull().sum().to_dict()
        duplicate_count = int(df.duplicated().sum())

        schema = {}
        descriptive_stats = {}
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                schema[col] = "numerical"
                clean_col = df[col].dropna()
                descriptive_stats[col] = {
                    "mean": float(clean_col.mean()) if not clean_col.empty else 0.0,
                    "median": float(clean_col.median()) if not clean_col.empty else 0.0,
                    "std": float(clean_col.std()) if len(clean_col) > 1 else 0.0,
                    "min": float(clean_col.min()) if not clean_col.empty else 0.0,
                    "max": float(clean_col.max()) if not clean_col.empty else 0.0
                }
            elif pd.api.types.is_datetime64_any_dtype(df[col]) or DataProcessingEngine._can_parse_date(df[col]):
                schema[col] = "datetime"
            else:
                schema[col] = "categorical"

        total_cells = row_count * col_count
        total_missing = sum(missing_matrix.values())
        missing_ratio = (total_missing / total_cells) if total_cells > 0 else 0
        duplicate_ratio = (duplicate_count / row_count) if row_count > 0 else 0
        quality_score = max(0.0, min(100.0, 100.0 * (1.0 - (0.6 * missing_ratio + 0.4 * duplicate_ratio))))

        return {
            "dimensions": {"rows": row_count, "columns": col_count},
            "data_quality_score": round(quality_score, 2),
            "missing_values": {k: int(v) for k, v in missing_matrix.items()},
            "duplicate_rows": duplicate_count,
            "schema": schema,
            "descriptive_stats": descriptive_stats
        }

    @staticmethod
    def execute_advanced_forecast(file_path: str, date_col: str, target_col: str, periods: int = 12) -> dict:
        df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
        df[date_col] = pd.to_datetime(df[date_col])
        
        prophet_df = df[[date_col, target_col]].rename(columns={date_col: 'ds', target_col: 'y'})
        prophet_df = prophet_df.groupby('ds', as_index=False).mean()

        m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True)
        m.fit(prophet_df)
        
        future = m.make_future_dataframe(periods=periods, freq='D')
        forecast = m.predict(future)

        output = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
        output['ds'] = output['ds'].dt.strftime('%Y-%m-%d')
        return output.to_dict(orient='records')

    @staticmethod
    def isolate_anomalies(file_path: str, numerical_cols: list) -> list:
        df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
        clean_df = df[numerical_cols].dropna()
        if clean_df.empty:
            return []
            
        iso = IsolationForest(contamination=0.05, random_state=42)
        preds = iso.fit_predict(clean_df)
        anomaly_indices = clean_df.index[preds == -1].tolist()
        return anomaly_indices

    @staticmethod
    def _can_parse_date(series: pd.Series) -> bool:
        try:
            pd.to_datetime(series.dropna().head(10), errors='raise')
            return True
        except (ValueError, TypeError):
            return False
