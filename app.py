from discord.ext import commands
import api_connector as con
from credentials import TOKEN

# initialize a Client instance
bot = commands.Bot(command_prefix="race!")

# when the bot starts running
@bot.event
async def on_ready():
    # print the bot's username
    print('Logged in as '+ bot.user.name)

# race!leaderboard command received
@bot.command()
async def leaderboard(ctx):
    await ctx.send(con.get_leaderboard())
    
# race!status command received
@bot.command()
async def status(ctx):
    await ctx.send(con.get_status())
 
# run
if __name__== "__main__":
    # connect the client to the bot
    bot.run(TOKEN)
