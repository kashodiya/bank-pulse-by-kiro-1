"""Main entry point for BankPulse application"""

import sys
import argparse
import uvicorn

from bankpulse.database import DatabaseManager
from bankpulse.data_loader import H8DataLoader


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='BankPulse: Interactive Credit Conditions Explorer')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Server command
    server_parser = subparsers.add_parser('serve', help='Start the API server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    server_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    server_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    # Init database command
    subparsers.add_parser('init', help='Initialize the database')
    
    # Download data command
    subparsers.add_parser('download', help='Download and load H8 data')
    
    # Status command
    subparsers.add_parser('status', help='Show database status')
    
    args = parser.parse_args()
    
    if args.command == 'serve':
        print(f"Starting BankPulse API server on {args.host}:{args.port}")
        uvicorn.run(
            "bankpulse.api:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    
    elif args.command == 'init':
        print("Initializing database...")
        db_manager = DatabaseManager()
        db_manager.init_database()
        print("Database initialized successfully!")
    
    elif args.command == 'download':
        print("Downloading H8 data...")
        db_manager = DatabaseManager()
        db_manager.init_database()
        loader = H8DataLoader(db_manager)
        result = loader.load_and_update()
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
    
    elif args.command == 'status':
        db_manager = DatabaseManager()
        latest_date = db_manager.get_latest_date()
        data = db_manager.get_data()
        
        print("\n=== BankPulse Database Status ===")
        print(f"Latest data date: {latest_date or 'No data'}")
        print(f"Total records: {len(data)}")
        
        if not data.empty:
            print(f"Date range: {data['date'].min()} to {data['date'].max()}")
            print(f"Unique series: {data['series_name'].nunique()}")
            print(f"Asset classes: {', '.join(data['asset_class'].unique())}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
