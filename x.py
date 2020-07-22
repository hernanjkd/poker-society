# import requests
import re
from datetime import datetime as dt, timedelta

j = {"tournament_id": 884, "tournament_buyin": "$200", "users": {
    "neal_corcoran@yahoo.com": 
        {"pokersociety_id": 7, "place": "1st", "winnings": 20000, "total_winning_swaps": 1}, 
    "hoang28974@gmail.com": 
        {"pokersociety_id": 2, "place": "2nd", "winnings": 12000, "total_winning_swaps": 1}, 
    "perry1830@msn.com": 
        {"pokersociety_id": 5, "place": "3rd", "winnings": 10000, "total_winning_swaps": 1}, 
    "leff1117@aol.com": 
        {"pokersociety_id": 6, "place": "4th", "winnings": 5000, "total_winning_swaps": 1}, 
    "katz234@gmail.com": 
        {"pokersociety_id": 3, "place": "5th", "winnings": 4000, "total_winning_swaps": 1}, 
    "brooklynbman@yahoo.com": 
        {"pokersociety_id": 8, "place": "6th", "winnings": 3000, "total_winning_swaps": 1}, 
    "123": 
        {"pokersociety_id": 1, "place": "7th", "winnings": 1200, "total_winning_swaps": 1}, 
    "mikitapoker@gmail.com": 
        {"pokersociety_id": 4, "place": "8th", "winnings": 500, "total_winning_swaps": 1}
}}

# requests.post( "http://localhost:3000/results",
#     json=j )

# regex = r'\$\s*(\d+)'

# print('piki')

# x = '$ 300'
# x = re.search( regex, x )
# print(x.group(1) if x is not None else 0)
# x = '$200'
# x = re.search( regex, x )
# print(x.group(1) if x is not None else 0)
# x = '$0++'
# x = re.search( regex, x )
# print(x.group(1) if x is not None else 0)
# x = 'Day 2'
# x = re.search( regex, x )
# print(x.group(1) if x is not None else 0)


to_int = lambda x: int(x) if str(x).isnumeric() else 0

k = '345'
j = 'osdifj'
piki = 556

# print( '${:,}'.format(4567897534) )

# print( '{:,.2f}'.format( abs(-11342344.40595872) ) )

# print( dt.utcnow().strftime('%A, %B %d, %Y - %I:%M %p') )
# x = {'3':'','4':'3'}
# print( len(x) )


now = dt.utcnow()
tmrw = now + timedelta(days=1)
yesterday = now - timedelta(days=1)

print( (tmrw - now) < timedelta(days=2) )