"""FastAPI application for BankPulse"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import pandas as pd

from .database import DatabaseManager
from .data_loader import H8DataLoader
from .analytics import CreditAnalytics
from .ai_assistant import AIAssistant

# Initialize FastAPI app
app = FastAPI(
    title="BankPulse API",
    description="Interactive Credit Conditions Explorer for U.S. Commercial Banking Activity",
    version="0.1.0"
)

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
data_loader = H8DataLoader(db_manager)
analytics = CreditAnalytics(db_manager)
ai_assistant = AIAssistant(db_manager)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    db_manager.init_database()


@app.get("/")
async def root():
    """Serve the main dashboard"""
    static_file = Path(__file__).parent.parent / "static" / "index.html"
    if static_file.exists():
        return FileResponse(static_file)
    return {
        "name": "BankPulse API",
        "version": "0.1.0",
        "description": "Interactive Credit Conditions Explorer"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    latest_date = db_manager.get_latest_date()
    return {
        "status": "healthy",
        "database": "connected",
        "latest_data_date": latest_date
    }


@app.post("/data/download")
async def download_data():
    """Download and update H8 data"""
    result = data_loader.load_and_update()
    return result


@app.get("/data/series")
async def get_series_data(
    series_name: Optional[str] = Query(None, description="Series name to filter"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(1000, description="Maximum number of records")
):
    """Get H8 series data"""
    try:
        df = db_manager.get_data(series_name, start_date, end_date)
        
        if df.empty:
            return {"data": [], "count": 0}
        
        # Limit results
        df = df.head(limit)
        
        return {
            "data": df.to_dict(orient='records'),
            "count": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/summary")
async def get_data_summary():
    """Get summary statistics of available data"""
    try:
        df = db_manager.get_data()
        
        if df.empty:
            return {"status": "no_data"}
        
        return {
            "total_records": len(df),
            "date_range": {
                "min": df['date'].min(),
                "max": df['date'].max()
            },
            "series_count": df['series_name'].nunique(),
            "asset_classes": df['asset_class'].unique().tolist(),
            "bank_types": df['bank_type'].unique().tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/growth-rates")
async def get_growth_rates(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    asset_class: Optional[str] = Query("commercial_industrial", description="Asset class to analyze"),
    max_series: int = Query(3, description="Maximum number of series to return")
):
    """Calculate growth rates (WoW, MoM, YoY) for top series"""
    try:
        # Get data for specific asset class only
        df = db_manager.get_data(start_date=start_date, end_date=end_date)
        
        if df.empty:
            return {"data": [], "count": 0}
        
        # Filter by asset class
        if asset_class:
            df = df[df['asset_class'] == asset_class]
        
        if df.empty:
            return {"data": [], "count": 0}
        
        # Get top series by data points
        series_counts = df['series_name'].value_counts().head(max_series)
        top_series = series_counts.index.tolist()
        
        # Filter to only top series
        df = df[df['series_name'].isin(top_series)]
        
        # Limit to 1000 most recent records per series
        df = df.sort_values('date').groupby('series_name').tail(1000)
        
        df_with_growth = analytics.calculate_growth_rates(df)
        
        # Only return records with valid YoY data
        df_with_growth = df_with_growth[df_with_growth['yoy_change'].notna()]
        
        # Convert to dict and clean up NaN/inf values
        records = df_with_growth.to_dict(orient='records')
        
        # Clean each record
        import math
        cleaned_records = []
        for record in records:
            cleaned = {}
            for key, value in record.items():
                if isinstance(value, float):
                    if math.isnan(value) or math.isinf(value):
                        cleaned[key] = None
                    else:
                        cleaned[key] = value
                else:
                    cleaned[key] = value
            cleaned_records.append(cleaned)
        
        return {
            "data": cleaned_records,
            "count": len(cleaned_records),
            "series": top_series
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/anomalies")
async def detect_anomalies(
    threshold: float = Query(2.5, description="Z-score threshold for anomaly detection"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Detect anomalies in H8 data"""
    try:
        df = db_manager.get_data(start_date=start_date, end_date=end_date)
        
        if df.empty:
            return {"anomalies": [], "count": 0}
        
        df_with_anomalies = analytics.detect_anomalies(df, threshold)
        anomalies = df_with_anomalies[df_with_anomalies['is_anomaly'] == True]
        
        return {
            "anomalies": anomalies.to_dict(orient='records'),
            "count": len(anomalies)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/flli")
async def get_flli(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get Forward-Looking Lending Index (FLLI)"""
    try:
        result = analytics.calculate_flli(start_date, end_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/clusters")
async def get_bank_clusters(
    n_clusters: int = Query(3, description="Number of clusters", ge=2, le=10)
):
    """Cluster banks by lending behavior"""
    try:
        result = analytics.cluster_banks(n_clusters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/query")
async def ai_query(question: str):
    """Ask AI assistant about H8 data"""
    try:
        result = ai_assistant.query(question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
