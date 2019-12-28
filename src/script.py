import requests
import json

data = requests.get('https://assets.breatheco.de/apis/fake/zips.php').json()
    
new = []

for zip in data:
    new.append({
        'zip_code': zip['_id'],
        'longitude': zip['loc'][0],
        'latitude': zip['loc'][1]
    })


with open('src/zip_codes.json', 'w') as f:
    json.dump(new, f)
    

print('ok')