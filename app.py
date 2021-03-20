from discord import Embed, Colour, Game, File
from discord.ext import commands, tasks
import api_connector as con
from credentials import TOKEN
from itertools import cycle
from io import BytesIO

# initialize a Client instance
bot = commands.Bot(command_prefix="!", help_command=None)

# setup the various status to loop through
activities = cycle(["srb2circuit.eu", "_current_map_", "_current_online_players_", "not with Fang"])

# when the bot starts running
@bot.event
async def on_ready():
    # print the bot's username
    print('Logged in as '+ bot.user.name)

    status_changer.start()


@tasks.loop(seconds=15, count=None)
async def status_changer():
    # get the next status
    game_name = activities_picker()
    
    # change the status
    await bot.change_presence(activity=Game(name=game_name))
        
def activities_picker():
    item = next(activities)
    
    # if the item isn't the "current played map"
    if item == "_current_map_":
        # get the current map
        game_name = con.get_server_info()[0]['map']['name']
    elif item == "_current_online_players_":
        # get the number of players
        players = con.get_server_info()[0]['number_of_players']
        game_name = f"with {players} racers"
    else:
        game_name = item
    
    return game_name


# leaderboard command received
@bot.command(aliases=["scoreboard"])
async def leaderboard(ctx, monthly=None):
    mon_leaderboard = False
    if monthly == "m":
        mon_leaderboard = True
    
    await ctx.send(con.get_leaderboard(monthly=mon_leaderboard))
    
# status command received
@bot.command(aliases=["server", "serverstatus", "info"])
async def status(ctx):
    await ctx.send(con.get_status_message())

# search command received
@bot.command()
async def search(ctx, map=None, *args):
    # if no map was specified
    if not map:
        # give error message
        await ctx.send(con.markup("No map was specified. Retry by specifying a map."))
    else:
        await ctx.send(con.search_result_to_message(con.get_search_result(parameters=["-mapname", map ,"-limit", "3"]+list(args))))
        
# bestskins command received
@bot.command()
async def bestskins(ctx):
    await ctx.send(con.get_best_skins())

# graph command received
@bot.command()
async def graph(ctx, player=None, map=None, *args):
    if player and map:
        # get the PIL image of the graph
        graph_figure = con.graph_builder(player=player, map=map, limit=50, params=args)

        if graph_figure == 50:
            await ctx.send(con.markup("Couldn't build graph. Try checking the parameters and how they are written"))
        
        # setup the buffer
        output_buffer = BytesIO()
    
        # save the image as binary
        graph_figure.savefig(output_buffer, format="png")
    
        # set the offset
        output_buffer.seek(0)

        # send the image
        await ctx.send(file=File(fp=output_buffer, filename="srb2_circuit_graph.png"))
    else:
        await ctx.send(con.markup("Required parameters not given"))

@bot.command()
async def mods(ctx):
    await ctx.send(con.markup(con.get_mods()))

# help command received
@bot.command(aliases=["h"])
async def help(ctx):
    # create an embed message
    embed = Embed(colour=Colour.orange())
    
    # set the title
    embed.set_author(name="SRB2 Circuit Race - Help")
    
    embed.add_field(name="Command Prefix", value=bot.command_prefix)
    
    # set the commands with descriptions
    embed.add_field(name="help (alias: h)", value="Returns this message")
    embed.add_field(name="status (alias: server, serverstatus, info)", value="Returns the server status", inline=False)
    embed.add_field(name="leaderboard (alias: scoreboard)", value=f'Returns the player leaderboard, monthly or of all time\nUsage: {bot.command_prefix}leaderboard [m]', inline=False)
    embed.add_field(name="search", value=(f'Usage: {bot.command_prefix}search <map name> [PARAMETERS]\n'), inline=False)
    embed.add_field(name="bestskins", value="Returns the skin leaderboard", inline=False)
    embed.add_field(name="graph", value=f'Usage: {bot.command_prefix}graph <player> <map name> [PARAMETERS]')
    embed.add_field(name="mods", value="Returns the active mods on the server")
    embed.add_field(name="Parameters List", value="When [PARAMETERS] is usable in a command, you are able to put any of these optional parameters in whatever order you like, by using them like: *-label value*.\n"\
                                                  'All parameters can be submitted with no "" if they '"don't require spaces.\n\n"\
                                                  "*-all_scores*  : to get multiple scores from same circumstances, must use value 'on'\n"\
                                                  "*-all_skins*   : to get scores from modded skins, must use value 'on'\n"\
                                                  "*-username*       : to get scores from a specific player\n"\
                                                  "*-skin*       : to get scores from a specific skin\n"\
                                                  "*-order*      : to get scores with a specific order, default 'time'\n"\
                                                  "*-limit*      : to get a limited number of scores, max 50"
                                                  , inline=False)
    
    # get the command sender
    member = ctx.message.author
    
    # if it exists
    if member:
        # get the bot - user dm channel
        channel = member.dm_channel
        # if the dm channel hasn't yet been created
        if not channel:
            # create the dm channel
            channel = await member.create_dm()
        # send the message
        await channel.send(embed=embed)

# run
if __name__== "__main__":
    # connect the client to the bot
    bot.run(TOKEN)
