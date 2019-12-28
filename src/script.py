import requests
import json

data = requests.get('https://assets.breatheco.de/apis/fake/zips.php').json()
    
new = {}

for zip in data:
    new[zip['_id']] = {
        'longitude': zip['loc'][0],
        'latitude': zip['loc'][1]
    }


with open('src/zip_codes.json', 'w') as f:
    json.dump(new, f)
    

print('ok')

# with open('src/zip_codes.json') as f:
#     print(json.load(f)['33185'])
