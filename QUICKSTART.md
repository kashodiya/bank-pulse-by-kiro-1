# BankPulse Quick Start Guide

## Step 1: Setup Environment

1. Copy the example environment file:
```bash
cd bankpulse
cp .env.example .env
```

2. Edit `.env` and update with your AWS profile:
```
AWS_DEFAULT_PROFILE=your-aws-profile
```

## Step 2: Install Dependencies

```bash
uv sync
```

## Step 3: Initialize Database

```bash
uv run python main.py init
```

## Step 4: Download H8 Data

```bash
uv run python main.py download
```

**Note**: This will download real Federal Reserve H.8 data. The download may take several minutes depending on your internet connection.

## Step 5: Start the Server

```bash
uv run python main.py serve
```

## Step 6: Access the Application

Open your browser and go to:
- **Dashboard**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Using the Dashboard

### Quick Actions
1. **Download H8 Data**: Click to download/update the latest Federal Reserve data
2. **Refresh Status**: Update the database statistics
3. **Calculate FLLI**: Compute the Forward-Looking Lending Index

### Data Visualization
- **Growth Rates**: View year-over-year, month-over-month, and week-over-week changes
- **Detect Anomalies**: Identify unusual patterns in the data
- **Bank Clusters**: See how banks group by lending behavior

### AI Assistant
Ask questions in natural language, such as:
- "How have small bank deposits changed since March 2023?"
- "What's the trend in real estate lending over the past 6 months?"
- "Which asset class shows the most volatility?"

## CLI Commands

```bash
# Check database status
uv run python main.py status

# Download/update data
uv run python main.py download

# Start server with auto-reload (for development)
uv run python main.py serve --reload

# Start server on custom port
uv run python main.py serve --port 8080
```

## API Examples

### Get Data Summary
```bash
curl http://localhost:8000/data/summary
```

### Calculate FLLI
```bash
curl http://localhost:8000/analytics/flli
```

### Detect Anomalies
```bash
curl http://localhost:8000/analytics/anomalies
```

### Ask AI Assistant
```bash
curl -X POST "http://localhost:8000/ai/query?question=What%20is%20the%20trend%20in%20C%26I%20loans"
```

## Troubleshooting

### AWS Credentials Error
Make sure your AWS profile is configured correctly:
```bash
aws configure list-profiles
```

### Database Not Found
Run the init command:
```bash
uv run python main.py init
```

### No Data Available
Download the H8 data:
```bash
uv run python main.py download
```

### Port Already in Use
Use a different port:
```bash
uv run python main.py serve --port 8080
```

## Next Steps

1. Explore the interactive dashboard
2. Try the AI assistant with different questions
3. Analyze growth rates and anomalies
4. Set up automated data updates (cron job or scheduled task)
5. Customize the analytics for your specific use case

## Data Updates

The H8 data is released weekly by the Federal Reserve. To keep your data current:

```bash
# Run this weekly to update your database
uv run python main.py download
```

Consider setting up a scheduled task (Windows Task Scheduler) or cron job (Linux/Mac) to automate this.
