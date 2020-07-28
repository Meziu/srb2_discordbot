import requests as r
from tabulate import tabulate
import matplotlib.pyplot as plt
from PIL import Image

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
    status, players_list = get_server_info()
    
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
def get_search_result(map=None, skin=None, player=None, limit=3, all_scores="off"):    
    # search api url builder
    search_url = api_url + f"search?limit={limit}"
    
    if map:
        search_url += f"&mapname={map}"
    if skin:
        search_url += f"&skin={skin}"
    if player:
        search_url += f"&username={player}"
    if all_scores == "on":
        search_url += f"&all_scores=on"
    
    # get the search results
    search_result = r.get(search_url, verify=False).json()
    
    return search_result

def search_result_to_message(search_result):
    # filter the search results to get only the wanted columns
    search_list = filter_dict_list(search_result, ['username', 'skin', 'time_string'])

    # create an ascii table with the data
    search_str = tabulate(search_list, headers=["Player", "Skin", "Time"])
    
    try:
        # create the message
        res = f'Map: {search_result[0]["mapname"]}  (id = {search_result[0]["map_id"]})\n\n'+search_str
    except IndexError:
        return markup("No result was found, try by rearranging the search parameters in the correct order or by specifying more the names.")
    
    # return the message
    return markup(res)

def get_best_skins():
    best_skins = r.get(api_url+"bestskins", verify=False).json()
    
    return markup(tabulate(best_skins.items(), headers=["Skin", "Points"]))

def graph_builder(player, map, skin, limit):
    NO_RESULTS_FOUND = 50
    
    limit = min([limit, 50])
    search_result = get_search_result(player=player, map=map, skin=skin, limit=limit, all_scores="on")
    
    for i in search_result:
        if not i["datetime"]:
            search_result.remove(i)
    
    if len(search_result) == 0:
        return NO_RESULTS_FOUND
    
    title = f"Player: {search_result[0]['username']}, Map: {search_result[0]['mapname']}, Limit: {limit}"
    if skin:
       title += f", Skin: {search_result[0]['skin']}"
    
    fig = plt.figure()
    
    plt.plot_date(x=[i["datetime"] for i in search_result], y=[i["time"] for i in search_result], linestyle='-')
    
    plt.title(title)
    plt.ylabel("Time Score")
    plt.xlabel("Timestamp")
    plt.grid(True)
    
    res_len = len(search_result)
    
    xlocs, xlabels = plt.xticks()

    plt.xticks(xlocs, labels=["" for i in search_result])
    
    ylocs, ylabels = plt.yticks()
    plt.yticks([i['time'] for i in search_result], labels=[i['time_string'] for i in search_result])
    
    fig.canvas.draw()
    
    return fig