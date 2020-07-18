import requests as r
from tabulate import tabulate

# base api url
api_url = "https://srb2circuit.eu/highscores/api/"

def markup(txt):
    return "```"+txt+"```"

def filter_dict_list(dict_list, allowed_keys):
    res = []
    
    for dictionary in dict_list:
        temp = []
        for key in allowed_keys:
            temp.append(dictionary[key])
        res.append(temp)
    
    return res
        
# leaderboard api retriever
def get_leaderboard():
    # request the json for the leaderboard
    leaderboard = r.get(api_url+"leaderboard", verify=False).json()
    
    # this way the leaderboard stops at the very last score and not in the middle of one
    # the maximum sting length is 2000 max chars(of the discord message) - 6 chars(for the markup signs) - the modulus of the current result over the max chars for each line
    str_length = 2000 - 6 - ((2000 - 6) % 31)
    
    # create the table and return it
    return markup(tabulate(leaderboard.items(), headers=["Player", "Points"])[:str_length])

def get_server_info():
    # request the json for the server status
    status = r.get(api_url+"server_info", verify=False).json()
    
    # filter the player fdate to get only the wanted columns
    players_list = filter_dict_list(status['players'], ['name', 'skin'])
    
    return status, players_list

# status api converter in text
def get_status_message():
    server_info = get_server_info()
    
    status = server_info[0]
    players_list = server_info[1]
    
    # create an ascii table with the players data
    players_str = tabulate(players_list, headers=["Username", "Skin"])
    
    # create the message
    res = (f"Server: {status['servername']}\n\n" 
           f"Number of Players: {status['number_of_players']}/{status['max_players']}\n"
           f"Map: {status['map']['name']} (id = {status['map']['id']})\n"
           f"Level Time: {status['leveltime_string']}\n\n"
           f"Players: \n{players_str}"
    )

    # return the message
    return markup(res)

# search api retriever
def get_search_result(map, skin=None, player=None):
    # if no map was specified
    if not map:
        # give error message
        return markup("No map was found. Retry by specifying a map.")
    
    # search api url builder
    search_url = api_url + f"search?limit=3&mapname={map}"
    
    if skin:
        search_url += f"&skin={skin}"
    if player:
        search_url += f"&username={player}"
    
    # get the search results
    search_result = r.get(search_url, verify=False).json()

    # filter the search results to get only the wanted columns
    search_list = filter_dict_list(search_result, ['username', 'skin', 'time_string'])

    # create an ascii table with the data
    search_str = tabulate(search_list, headers=["Player", "Skin", "Time"])
    
    # create the message
    res = f'Map: {search_result[0]["mapname"]}  (id = {search_result[0]["map_id"]})\n\n'+search_str

    # return the message
    return markup(res)

def get_best_skins():
    best_skins = r.get(api_url+"bestskins", verify=False).json()
    
    return markup(tabulate(best_skins.items(), headers=["Skin", "Points"]))
