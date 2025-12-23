"""Analytics and ML modules for BankPulse"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from .database import DatabaseManager


class CreditAnalytics:
    """Advanced analytics for credit conditions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def calculate_growth_rates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate YoY, MoM, and WoW growth rates"""
        df = df.sort_values('date')
        df['value_lag_1w'] = df.groupby('series_name')['value'].shift(1)
        df['value_lag_4w'] = df.groupby('series_name')['value'].shift(4)
        df['value_lag_52w'] = df.groupby('series_name')['value'].shift(52)
        
        df['wow_change'] = ((df['value'] - df['value_lag_1w']) / df['value_lag_1w'] * 100)
        df['mom_change'] = ((df['value'] - df['value_lag_4w']) / df['value_lag_4w'] * 100)
        df['yoy_change'] = ((df['value'] - df['value_lag_52w']) / df['value_lag_52w'] * 100)
        
        # Replace inf and -inf with None, and fill NaN with None
        df = df.replace([np.inf, -np.inf], None)
        df = df.where(pd.notna(df), None)
        
        return df
    
    def detect_anomalies(self, df: pd.DataFrame, threshold: float = 2.5) -> pd.DataFrame:
        """Detect anomalies using z-score method"""
        df = df.copy()
        
        for series in df['series_name'].unique():
            series_data = df[df['series_name'] == series]['value']
            mean = series_data.mean()
            std = series_data.std()
            
            z_scores = np.abs((series_data - mean) / std)
            df.loc[df['series_name'] == series, 'z_score'] = z_scores
            df.loc[df['series_name'] == series, 'is_anomaly'] = z_scores > threshold
        
        return df
    
    def calculate_flli(self, start_date: str = None, end_date: str = None) -> Dict:
        """Calculate Forward-Looking Lending Index (FLLI)"""
        # Get relevant data
        loan_data = self.db_manager.get_data(start_date=start_date, end_date=end_date)
        
        if loan_data.empty:
            return {'flli_score': 0, 'status': 'no_data'}
        
        # Filter for key indicators
        loan_growth = loan_data[loan_data['asset_class'].isin(['commercial_industrial', 'real_estate', 'consumer'])]
        deposits = loan_data[loan_data['asset_class'] == 'deposits']
        reserves = loan_data[loan_data['asset_class'] == 'reserves']
        
        # Calculate components
        loan_momentum = self._calculate_momentum(loan_growth)
        deposit_volatility = self._calculate_volatility(deposits)
        reserve_trend = self._calculate_trend(reserves)
        
        # Combine into FLLI score (-100 to +100)
        flli_score = (loan_momentum * 0.5 - deposit_volatility * 0.3 + reserve_trend * 0.2) * 100
        flli_score = max(-100, min(100, flli_score))
        
        return {
            'flli_score': round(flli_score, 2),
            'loan_momentum': round(loan_momentum, 3),
            'deposit_volatility': round(deposit_volatility, 3),
            'reserve_trend': round(reserve_trend, 3),
            'status': 'calculated'
        }
    
    def _calculate_momentum(self, df: pd.DataFrame) -> float:
        """Calculate loan growth momentum"""
        if df.empty:
            return 0.0
        
        df = df.sort_values('date')
        recent_values = df.tail(12)['value'].values
        
        if len(recent_values) < 2:
            return 0.0
        
        # Simple momentum: (recent avg - older avg) / older avg
        mid_point = len(recent_values) // 2
        recent_avg = np.mean(recent_values[mid_point:])
        older_avg = np.mean(recent_values[:mid_point])
        
        if older_avg == 0:
            return 0.0
        
        return (recent_avg - older_avg) / older_avg
    
    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        """Calculate deposit volatility"""
        if df.empty:
            return 0.0
        
        df = df.sort_values('date')
        recent_values = df.tail(12)['value'].values
        
        if len(recent_values) < 2:
            return 0.0
        
        return np.std(recent_values) / np.mean(recent_values) if np.mean(recent_values) != 0 else 0.0
    
    def _calculate_trend(self, df: pd.DataFrame) -> float:
        """Calculate reserve trend"""
        if df.empty:
            return 0.0
        
        df = df.sort_values('date')
        recent_values = df.tail(12)['value'].values
        
        if len(recent_values) < 2:
            return 0.0
        
        # Linear trend
        x = np.arange(len(recent_values))
        slope = np.polyfit(x, recent_values, 1)[0]
        
        return slope / np.mean(recent_values) if np.mean(recent_values) != 0 else 0.0
    
    def cluster_banks(self, n_clusters: int = 3) -> Dict:
        """Cluster banks by lending behavior"""
        data = self.db_manager.get_data()
        
        if data.empty:
            return {'status': 'no_data', 'clusters': []}
        
        # Pivot data for clustering
        pivot_data = data.pivot_table(
            index='series_name',
            columns='date',
            values='value',
            aggfunc='mean'
        ).fillna(0)
        
        if len(pivot_data) < n_clusters:
            return {'status': 'insufficient_data', 'clusters': []}
        
        # Standardize and cluster
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(pivot_data)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        
        # Organize results
        cluster_results = []
        for i in range(n_clusters):
            cluster_series = pivot_data.index[clusters == i].tolist()
            cluster_results.append({
                'cluster_id': i,
                'series_count': len(cluster_series),
                'series_names': cluster_series[:10]  # Limit to first 10
            })
        
        return {
            'status': 'success',
            'n_clusters': n_clusters,
            'clusters': cluster_results
        }
