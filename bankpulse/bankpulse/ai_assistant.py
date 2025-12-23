"""AI Assistant using AWS Bedrock"""

import os
import json
import boto3
from typing import Dict, Optional

from .config import AWS_PROFILE, AWS_REGION, BEDROCK_MODEL_ID
from .database import DatabaseManager


class AIAssistant:
    """Natural language interface using AWS Bedrock"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        # Set AWS profile
        os.environ['AWS_DEFAULT_PROFILE'] = AWS_PROFILE
        
        # Initialize Bedrock client
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=AWS_REGION
        )
        self.model_id = BEDROCK_MODEL_ID
    
    def query(self, question: str) -> Dict:
        """Answer questions about H8 data using AI"""
        try:
            # Get relevant data based on the question
            context = self._get_relevant_data_context(question)
            
            # Build prompt
            prompt = self._build_prompt(question, context)
            
            # Call Bedrock
            response = self._call_bedrock(prompt)
            
            return {
                'status': 'success',
                'question': question,
                'answer': response
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'question': question,
                'error': str(e)
            }
    
    def _get_relevant_data_context(self, question: str) -> str:
        """Get relevant data context based on the question"""
        question_lower = question.lower()
        
        # Determine date range from question
        start_date = None
        if 'march 2023' in question_lower or 'since march 2023' in question_lower:
            start_date = '2023-03-01'
        elif 'last year' in question_lower or 'past year' in question_lower:
            from datetime import datetime, timedelta
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        elif 'last 6 months' in question_lower:
            from datetime import datetime, timedelta
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        # Determine bank type
        bank_type = None
        if 'small bank' in question_lower:
            bank_type = 'small'
        elif 'large bank' in question_lower:
            bank_type = 'large'
        elif 'foreign bank' in question_lower:
            bank_type = 'foreign'
        
        # Determine asset class
        asset_class = None
        if 'deposit' in question_lower:
            asset_class = 'deposits'
        elif 'loan' in question_lower:
            asset_class = 'loans'
        elif 'real estate' in question_lower:
            asset_class = 'real_estate'
        elif 'consumer' in question_lower:
            asset_class = 'consumer'
        elif 'commercial' in question_lower or 'c&i' in question_lower:
            asset_class = 'commercial_industrial'
        
        # Get filtered data
        data = self.db_manager.get_data(start_date=start_date)
        
        if data.empty:
            return "No data available for the specified criteria."
        
        # Filter by bank type if specified
        if bank_type:
            data = data[data['bank_type'] == bank_type]
        
        # Filter by asset class if specified
        if asset_class:
            data = data[data['asset_class'] == asset_class]
        
        if data.empty:
            return f"No data available for {bank_type or 'all'} banks and {asset_class or 'all asset classes'}."
        
        # Calculate statistics
        import pandas as pd
        
        # Group by date and calculate aggregates
        time_series = data.groupby('date')['value'].agg(['mean', 'sum', 'count']).reset_index()
        time_series = time_series.sort_values('date')
        
        # Calculate change
        if len(time_series) > 1:
            first_value = time_series.iloc[0]['mean']
            last_value = time_series.iloc[-1]['mean']
            change_pct = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
            change_abs = last_value - first_value
        else:
            change_pct = 0
            change_abs = 0
        
        # Get recent trends (last 10 data points)
        recent_data = time_series.tail(10)
        
        # Create detailed context
        context = f"""
Query Analysis:
- Date range: {start_date or 'All available data'} to {data['date'].max()}
- Bank type: {bank_type or 'All banks'}
- Asset class: {asset_class or 'All asset classes'}
- Total data points: {len(data)}

Key Statistics:
- First period average: ${first_value:,.2f} million
- Latest period average: ${last_value:,.2f} million
- Absolute change: ${change_abs:,.2f} million
- Percentage change: {change_pct:.2f}%

Recent Trend (last 10 periods):
{recent_data.to_string(index=False)}

Sample Series Names:
{', '.join(data['series_name'].unique()[:5])}
"""
        return context
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for Bedrock"""
        return f"""You are an expert economist analyzing U.S. commercial banking data from the Federal Reserve H.8 report.

Context about the available data:
{context}

User question: {question}

Please provide a clear, concise answer based on the available data. If you need specific data points that aren't in the context, explain what additional information would be helpful."""
    
    def _call_bedrock(self, prompt: str) -> str:
        """Call AWS Bedrock API"""
        # Prepare request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Invoke model
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Extract text from Claude response
        if 'content' in response_body and len(response_body['content']) > 0:
            return response_body['content'][0]['text']
        
        return "No response generated"
