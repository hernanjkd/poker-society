import requests

j = {"tournament_id": 884, "tournament_buyin": "$200", "users": {
    "neal_corcoran@yahoo.com": 
        {"pokersociety_id": 7, "place": "1st", "winnings": 20000, "total_winning_swaps": 0}, 
    "hoang28974@gmail.com": 
        {"pokersociety_id": 2, "place": "2nd", "winnings": 12000, "total_winning_swaps": 0}, 
    "perry1830@msn.com": 
        {"pokersociety_id": 5, "place": "3rd", "winnings": 10000, "total_winning_swaps": 0}, 
    "leff1117@aol.com": 
        {"pokersociety_id": 6, "place": "4th", "winnings": 5000, "total_winning_swaps": 0}, 
    "katz234@gmail.com": 
        {"pokersociety_id": 3, "place": "5th", "winnings": 4000, "total_winning_swaps": 0}, 
    "brooklynbman@yahoo.com": 
        {"pokersociety_id": 8, "place": "6th", "winnings": 3000, "total_winning_swaps": 0}, 
    "123": 
        {"pokersociety_id": 1, "place": "7th", "winnings": 1200, "total_winning_swaps": 0}, 
    "mikitapoker@gmail.com": 
        {"pokersociety_id": 4, "place": "8th", "winnings": 500, "total_winning_swaps": 0}
}}

requests.post( "http://localhost:3000/results",
    json=j )