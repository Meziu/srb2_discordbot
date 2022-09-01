import discord
from discord import Embed, Colour, Game, File, Intents
from discord.ext import commands, tasks
import api_connector as con
from credentials import TOKEN
from itertools import cycle
from io import BytesIO

# implementation of a Client subclass
class CircuitBot(discord.Client):
    def __init__(self):
        super().__init__(intents=Intents.default())
        self.synced = False

    async def on_ready(self):
        # Sync the bot's data to the current Guild
        await tree.sync()
        self.synced = True
        print("Bot has successfully synced to the Discord Server")
        status_changer.start()

bot = CircuitBot()
tree = discord.app_commands.CommandTree(bot)


# setup the various status to loop through
activities = cycle(["srb2circuit.eu", "_current_map_", "_current_online_players_", "not with Fang"])

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


@tree.command(description="Show the current global leaderboard")
async def leaderboard(interaction: discord.Interaction, monthly: bool = False):
    await interaction.response.defer()
    result = con.get_leaderboard(monthly=monthly)
    await interaction.followup.send(result)

@tree.command(description="Show the current status of the game server")
async def info(interaction: discord.Interaction):
    await interaction.response.defer()
    result = con.get_status_message()
    await interaction.followup.send(result)

@tree.command(description="Search for related highscores based on your filters")
async def search(interaction: discord.Interaction, map: str, player: str = None, skin: str = None,
            all_scores: bool = False, all_skins: bool = False, order: str = "time", limit: int = 3):
    params = command_arguments_to_search_parameters(player=player, map=map, skin=skin, all_scores=all_scores,
                                                all_skins=all_skins, order=order, limit=limit)
    await interaction.response.defer()
    result = con.search_result_to_message(con.get_search_result(parameters=params))
    await interaction.followup.send(result)
        
@tree.command(description="Show the current character leaderboard")
async def bestskins(interaction: discord.Interaction):
    await interaction.response.defer()
    result = con.get_best_skins()
    await interaction.followup.send(result)

@tree.command(description="Show a graph of a player's performance on a specific map")
async def graph(interaction: discord.Interaction, player: str, map: str, skin: str = None, all_skins: bool = False, limit: int = 50):
    # Parse the command parameters for the search API
    params = command_arguments_to_search_parameters(player=player, map=map, skin=skin, all_scores=True,
                                                all_skins=all_skins, order="datetime", limit=limit)

    await interaction.response.defer()
    # Get the PIL image of the graph
    graph_figure = con.graph_builder(parameters=params)

    if graph_figure == 50:
        await interaction.response.send_message(con.markup("Couldn't build graph. Try checking the parameters and how they are written"))
        
    # Setup the buffer
    output_buffer = BytesIO()
    
    # Save the image as binary
    graph_figure.savefig(output_buffer, format="png")
    
    # Set the offset
    output_buffer.seek(0)

    # Send the image
    await interaction.followup.send(file=File(fp=output_buffer, filename="srb2_circuit_graph.png"))

@tree.command(description="Show the list of currently active mods on the game server")
async def modlist(interaction: discord.Interaction):
    await interaction.response.defer()
    result = con.markup(con.get_mods())
    await interaction.followup.send(result)

@tree.command(description="Long help command with all the information for this Discord Bot's usage")
async def help(interaction: discord.Interaction):
    # create an embed message
    embed = Embed(colour=Colour.orange())
    
    # set the title
    embed.set_author(name="SRB2 Circuit Race - Help")
    
    # set the commands with descriptions
    embed.add_field(name="help", value="Shows this message")
    embed.add_field(name="info", value="Shows the server status")
    embed.add_field(name="leaderboard", value="Shows the player leaderboard, monthly or of all time")
    embed.add_field(name="search", value="Search for scores using a multitude of filters")
    embed.add_field(name="bestskins", value="Shows the character leaderboard")
    embed.add_field(name="graph", value="Renders a graph of a player\'s achievements in a specific map")
    embed.add_field(name="modlist", value="Shows the active mods on the server")
    embed.add_field(name="Parameters List", value="For `graph` and `search` you can input some more parameters. This is what they do:\n\n"\
                                                  "*all_scores* : get multiple scores from the same Player/Skin combination\n"\
                                                  "*all_skins*  : get scores for modded skins as well as standard ones\n"\
                                                  "*player*     : get scores for a specific player, only for `search`\n"\
                                                  "*skin*       : get scores for a specific skin, modded skins specified here require `all_skins`\n"\
                                                  "*order*      : get scores with a specific order, the default is by \"time\" \n"\
                                                  "*limit*      : get a limited number of scores, the max value is 50"
                                                  , inline=False)
    
    
    # get the command sender
    member = interaction.user
    
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

def command_arguments_to_search_parameters(player: str = None, map: str = None, skin: str = None,
            all_scores: bool = False, all_skins: bool = False, order: str = "time", limit: int = 50):
    # Basic initialization with default-able values
    arg_dict = {"order": order,
                "limit": limit}

    # Checks for non-default-able values
    if player:
        arg_dict["username"] = player
    if map:
        arg_dict["mapname"] = map
    if skin:
        arg_dict["skin"] = skin
    
    # The API requires `on` and `off` for boolean values, not a pretty solution here
    if all_scores:
        arg_dict["all_scores"] = "on"
    else:
        arg_dict["all_scores"] = "off"
    
    if all_skins:
        arg_dict["all_skins"] = "on"
    else:
        arg_dict["all_skins"] = "off"

    return arg_dict

# run
if __name__== "__main__":
    # connect the client to the bot
    bot.run(TOKEN)
