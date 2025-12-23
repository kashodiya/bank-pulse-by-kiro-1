"""Check data categorization"""

from bankpulse.database import DatabaseManager

db = DatabaseManager()
data = db.get_data()

print('Asset classes:')
print(data['asset_class'].value_counts())

print('\nBank types:')
print(data['bank_type'].value_counts())

print('\nSample series names:')
for name in data['series_name'].unique()[:15]:
    print(f'  {name}')
