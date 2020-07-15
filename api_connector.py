import requests as r
from tabulate import tabulate

api_url = "https://srb2circuit.eu/highscores/api/"

def markup(txt):
    return "```"+txt+"```"

def get_leaderboard():
    # request the json for the leaderboard
    leaderboard = r.get(api_url+"leaderboard", verify=False).json()
    
    # this way the leaderboard stops at the very last score and not in the middle of one
    # the maximum sting length is 2000 max chars(of the discord message) - 6 chars(for the markup signs) - the modulus of the current result over the max chars for each line
    str_length = 2000 - 6 - ((2000 - 6) % 31)
    
    # create the table and return it
    return markup(tabulate(leaderboard.items(), headers=["Player", "Points"])[:str_length])

def get_status():
    # request the json for the server status
    status = r.get(api_url+"server_info", verify=False).json()
    
    players_list = []
    
    for player in status['players']:
        temp = []
        
        temp.append(player['num'])
        temp.append(player['name'])
        temp.append(player['skin'])
        
        players_list.append(temp)

    players_str = tabulate(players_list, headers=["ID", "Username", "Skin"])
    
    res = (f"Server: {status['servername']}\n\n" 
           f"Number of Players: {status['number_of_players']}/{status['max_players']}\n"
           f"Map: {status['map']['name']} (id = {status['map']['id']})\n"
           f"Level Time: {status['leveltime_string']}\n\n"
           f"Players: \n{players_str}"
    )

    return markup(res)
