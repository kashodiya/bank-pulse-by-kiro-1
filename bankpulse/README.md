# BankPulse: Interactive Credit Conditions Explorer

An AI-powered platform that visualizes, analyzes, and forecasts trends in U.S. commercial banking activity using the Federal Reserve H.8 dataset.

## Features

- **Dynamic Balance Sheet Visualizer**: Interactive dashboards showing weekly trends in loans, deposits, and reserves
- **Credit Stress Radar**: Anomaly detection to flag unusual shifts in lending or deposit behavior
- **Forward-Looking Lending Index (FLLI)**: Proprietary index tracking credit condition trends
- **AI Assistant**: Natural language interface powered by AWS Bedrock (Claude)
- **Advanced Analytics**: Clustering, growth rate analysis, and ML-based forecasting

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- AWS account with Bedrock access
- AWS CLI configured with appropriate profile

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bankpulse
```

2. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

3. Edit `.env` and add your AWS profile:
```
AWS_DEFAULT_PROFILE=your-aws-profile-name
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-5-20250929-v1:0
```

4. Install dependencies using uv:
```bash
uv sync
```

## Usage

### Initialize Database

```bash
uv run python main.py init
```

### Download H8 Data

Download and load the latest Federal Reserve H.8 data:

```bash
uv run python main.py download
```

### Check Status

View database status and statistics:

```bash
uv run python main.py status
```

### Start API Server

Start the FastAPI server:

```bash
uv run python main.py serve
```

Or with auto-reload for development:

```bash
uv run python main.py serve --reload
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Data Management
- `POST /data/download` - Download and update H8 data
- `GET /data/series` - Get H8 series data with filters
- `GET /data/summary` - Get summary statistics

### Analytics
- `GET /analytics/growth-rates` - Calculate WoW, MoM, YoY growth rates
- `GET /analytics/anomalies` - Detect anomalies in data
- `GET /analytics/flli` - Get Forward-Looking Lending Index
- `GET /analytics/clusters` - Cluster banks by lending behavior

### AI Assistant
- `POST /ai/query` - Ask questions about H8 data using natural language

## Project Structure

```
bankpulse/
├── bankpulse/
│   ├── __init__.py
│   ├── api.py              # FastAPI application
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database management
│   ├── data_loader.py      # H8 data downloader and parser
│   ├── analytics.py        # Analytics and ML modules
│   └── ai_assistant.py     # AWS Bedrock AI assistant
├── main.py                 # CLI entry point
├── pyproject.toml          # Project dependencies
├── .env.example            # Example environment variables
└── README.md
```

## Data Source

Data is sourced from the Federal Reserve's H.8 report:
https://www.federalreserve.gov/datadownload/Output.aspx?rel=H8&filetype=zip

The H.8 report provides weekly data on assets and liabilities of commercial banks in the United States.

## License

MIT
