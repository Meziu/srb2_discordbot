import discord
from commands import cmd_list
from credentials import TOKEN

# initialize a Client instance
bot_client = discord.Client()

# when the bot starts running
@bot_client.event
async def on_ready():
    # print the bot's username
    print('Logged in as '+ bot_client.user.name)

# when a message is received
@bot_client.event
async def on_message(message):
    # if the message is from the bot or the channel isn't "bot_commands"
    if message.author == bot_client.user or message.channel.name != "bot_commands":
        # don't do anything
        return
    
    # if the message starts with "!hello"
    if message.content.startswith('race!'):
        # create a message that mentions the message sender
        received_cmd = message.content.split('race!')[1].split(" ")
        cmd = received_cmd[0]
        args = received_cmd[1::1]
        
        msg = None
        
        for t in cmd_list.keys():
            if cmd == t:
                msg = cmd_list[t]()

        if msg:
            await message.channel.send("```"+msg+"```")
                
# run
if __name__== "__main__":
    # connect the client to the bot
    bot_client.run(TOKEN)
