import requests as r
from tabulate import tabulate

api_url = "https://srb2circuit.eu/highscores/api/"

def get_leaderboard():
    # request the json for the leaderboard
    leaderboard = r.get(api_url+"leaderboard", verify=False).json()
    
    # this way the leaderboard stops at the very last score and not in the middle of one
    # the maximum sting length is 2000 max chars(of the discord message) - 6 chars(for the markup signs) - the modulus of the current result over the max chars for each line
    str_length = 2000 - 6 - ((2000 - 6) % 31)
    
    # create the table and return it
    return tabulate(leaderboard.items(), headers=["Player", "Points"])[:str_length]

def get_status():
    pass

cmd_list = {"leaderboard": get_leaderboard,
            "status": get_status
}