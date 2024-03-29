import requests as r
from tabulate import tabulate
import matplotlib.pyplot as plt
from PIL import Image
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta
from urllib import parse as urlparser

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

def tics_to_string(time):
    minutes = time//(60*35)
    seconds = time//35%60
    centiseconds = (time%35) * (100//35)
    return f"{minutes}:"+f"{seconds}".zfill(2)+f".{centiseconds}".zfill(2)

def list_grouper(array):
    if len(array) == 1:
        return [array]
    array.sort()

    diff = [array[i+1]-array[i] for i in range(len(array)-1)]
    
    avg = sum(diff) / len(diff)

    m = [[array[0]]]

    for x in array[1:]:
        if x - m[-1][-1] < avg:
            m[-1].append(x)
        else:
            m.append([x])
            
    return m

def group_simplifier(group):
    res = []
    for i in group:
        res.append(i[round(len(i)/2)])
    return res


def date_converter(year, month, day):
    return "{:02}-{:02}-{:02}".format(year, month, day)

# Leaderboard API retriever
def get_leaderboard(monthly=False):
    url = api_url+"leaderboard?"
    if monthly:
        start_date = date.today()
        end_date = start_date + relativedelta(months=1)
        
        url+="start_date="+date_converter(start_date.year, start_date.month, 1)
        url+="&end_date="+date_converter(start_date.year, end_date.month, 1)

        print(url)
    
    # Request the json for the leaderboard
    leaderboard = r.get(url, verify=False).json()
    
    # This way the leaderboard stops at the very last score and not in the middle of one
    # The maximum sting length is 2000 max chars(of the discord message) - 6 chars(for the markup signs) - the modulus of the current result over the max chars for each line
    str_length = 2000 - 6 - ((2000 - 6) % 31)

    table = []

    for player in leaderboard:
        table.append((player['username'], player['total']))
    
    # Create the table and return it
    return markup(tabulate(table, headers=["Player", "Points"])[:str_length])

def get_server_info():
    # Request the json for the server status
    status = r.get(api_url+"server_info", verify=False).json()
    
    # Filter the player fdate to get only the wanted columns
    players_list = filter_dict_list(status['players'], ['name', 'skin'])
    
    return status, players_list

# Status api converter in text
def get_status_message():
    status, players_list = get_server_info()
    
    # Create an ascii table with the players data
    players_str = tabulate(players_list, headers=["Username", "Skin"])
    
    # Create the message
    res = (f"Server: {status['servername']}\n\n" 
           f"Number of Players: {status['number_of_players']}/{status['max_players']}\n"
           f"Map: {status['map']['name']} (id = {status['map']['id']})\n"
           f"Level Time: {status['leveltime_string']}\n\n"
           f"Players: \n{players_str}"
    )

    # Return the message
    return markup(res)

# Return a list of the currently active mods in the server
def get_mods():
    status, _ = get_server_info()
    print(status)
    res = ""
    assets = ["srb2.pk3", "zones.pk3", "player.dta", "patch.pk3"]
    for f in status['filesneeded']:
        if f['filename'] not in assets:
            res += f"- {f['filename']}\n"
    return res

# Search api retriever
def get_search_result(parameters: dict):    
    # search api url builder
    search_url = api_url + f"search?"
            
    search_url += urlparser.urlencode(parameters, quote_via=urlparser.quote)

    print(search_url)
    
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

def graph_builder(parameters: dict):
    NO_RESULTS_FOUND = 50

    print(parameters)
    
    search_result = get_search_result(parameters=parameters)
    
    for i in search_result:
        # if the datetime is null or the time is more than 6 minutes
        if (not i["datetime"]) or i['time'] >= 12600:
            search_result.remove(i)
    
    if len(search_result) == 0:
        return NO_RESULTS_FOUND
    
    title = f"Player: {search_result[0]['username']}, Map: {search_result[0]['mapname']}"

    # If the key exists, then the user specified the character to filter
    if parameters.get("skin"):
        title += f", Skin: {search_result[0]['skin']}"
    
    fig = plt.figure()
    
    plt.plot_date(x=[i["datetime"] for i in search_result], y=[i["time"] for i in search_result], linestyle='-')
    
    plt.title(title)
    plt.xlabel("Over Time")
    plt.grid(True)
    
    
    xlocs, xlabels = plt.xticks()

    plt.xticks(xlocs, labels=["" for i in search_result])
    
    
    ylocs = group_simplifier(list_grouper([i['time'] for i in search_result]))
    
    plt.yticks(ylocs, labels=[tics_to_string(i) for i in ylocs])
    
    
    fig.canvas.draw()
    
    return fig
