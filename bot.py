import discord # type: ignore
import numpy as np # type: ignore
import csv # CSV Library
from PIL import Image, ImageDraw # type: ignore
import pandas as pd # type: ignore
from dataclasses import dataclass, asdict
import base64
from io import BytesIO
import requests # type: ignore

bot = discord.Bot(intents=discord.Intents.all())

registering = [] # list of players registering
manual_register = [] # list of players that are being manually registered
registered = [] # list of players registered, this does mean that the bot probably shouldn't go offline, maybe I'll fix that?

file_path = '' # String of the file path to the folder

# If you're using a website, set use_website = True then set the path variables to wherever you want to send player data to your API
# If you're using a web API, I would suggest either using the same data that is sent by the bot, or modifying the data sent by the bot to the API
# The data that is sent by the bot to the web API is what the FPU HvZ website uses
use_website = False
backend_path = '' # Link to website api main path
mod_path = '' # Extension for API to mod a player
infection_path = '' # Extension for API to infect a player
oz_path = '' # Extension for API to OZ a player
cure_path = '' # Extension for API to cure a player
player_creation_path = '' # Extension for API to create a player
player_removal_path = '' # Extension for API to remove a player
wipe_path = '' # Extension for API to clear the database

bot_id = '' # The bot ID to run the bot
registation_channel = 0 # Registration channel ID
mod_channel = 0 # Mod bot channel ID
tagging_channel = 0 # Tagging channel ID
tags_channel = 0 # Tags channel ID
human_role_id = 0 # Human role ID
zombie_role_id = 0 # Zombie role ID
player_role_id = 0 # Player role ID
oz_role_id = 0 # OZ role ID
cured_role_id = 0 # Cured role ID
hvz_guild_id = 0 # Guild ID
mod_role_id = 0 # Mod role ID

hum = 0 # Human player count
zom = 0 # Zombie player count

@bot.event
async def on_ready():

    with open(file=f'{file_path}/player_data.csv', mode="r") as f:
        csv_reader = csv.reader(f)
        # goes through each row in the player data file
        h = 0
        z = 0
        for row in csv_reader:
            if(row == []):
                # makes sure I don't get an index error
                pass
            else:
                # adds previously registered players to the registered list
                if(row[0] == "HvZ_ID"): # Skips header row
                    continue
                if(row[6] == "False"):
                    continue
                registered.append(row[1])
                if row[4] == "True":
                    z = z + 1 # Adds Z Count
                else:
                    h = h + 1 # Adds H Count
    
    with open(file=f'{file_path}/mod_data.csv', mode='r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if(row[0] != "discord_id"):
                h -= 1 # Removes from the human count for moderators that are registered as players

    global zom
    global hum
    hum = h # Dumb python bs
    zom = z # Dumb python bs
    await updatePresence()
    print(f'{hum} humans vs {zom} zombies')
    print(f'{len(registered)} accounts registered')

    print(f'We have logged in as {bot.user}') # Prints in the console once the bot is online and ready, crucial

async def updatePresence():
    global zom
    global hum
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{zom} Zs vs {hum} Humans'))

@bot.event
async def on_message(message):
    if(message.author == bot.user):
        # makes sure that the bot ignores any message it sends because I guess it's message also trigger this event?
        return

    if(message.channel.type != discord.ChannelType.private):
        if(message.content.lower().find("gun") != -1):
            await message.channel.send(f'UwU Gotta say Blasters here buckeroo.\n<@{message.author.id}> careful, you will be muted if you continue.', reference=message)
            return
        if(message.content.lower().find("bullet") != -1):
            await message.channel.send(f'UwU Gotta say Darts here buckeroo.\n<@{message.author.id}> careful, you will be muted if you continue.', reference=message)
            return
        if(message.content.lower().find("firearm") != -1):
            await message.channel.send(f'UwU Gotta say Blasters here buckeroo.\n<@{message.author.id}> careful, you will be muted if you continue.', reference=message)
            return
            

    if(message.channel.type != discord.ChannelType.private):
        if(message.guild.id != hvz_guild_id):
            # makes sure this is in the right server
            await message.channel.send('This bot is not supposed to be in this server, please remove it immediately')
            return

    channel = message.channel
    
    # checks to see if this is a message in a dm
    if(channel.type == discord.ChannelType.private):
        messages = channel.history(limit=2) # gets the last two messages in the dm channel, it should be the email question and the user responding with an email
        msgs = [] # holds the two messages
        # appends the two messages to a list
        async for msg in messages:
            msgs.append(msg)
        # checks to see if the first message is from the bot (it should be the email question)
        if(msgs[1].author == bot.user):
            # step is what step of the questioning they are on
            step = msgs[1].content
            # email question
            if(step == 'What is your student email address? (example: jsmith1234@floridapoly.edu)'):
                # makes sure the player is a poly student (non-poly students should be registered manually)
                if(not '@' in msgs[0].content):
                    await message.author.send('That is not a email address, please run the command again in the server to continue registration')
                else:
                    # Creates a player instance and adds them to the registering list
                    hvz_id = np.random.randint(100000,999999)
                    with open(file=f'{file_path}/player_data.csv', mode="r") as f:
                        csv_reader = csv.reader(f)
                        for row in csv_reader:
                            # makes sure there are no duplicate IDs
                            if(row[0] == 'HvZ_ID'): # Just don't read the header line
                                continue
                            if(row == []): # Don't read a blank line
                                continue
                            while(hvz_id == type(int(row[0]))):
                                hvz_id = np.random.randint(100000,999999)
                    player = Player(message.author.id, hvz_id, message.content)
                    registering.append(player)
                    await message.author.send('What is your first and last name? (Ex: John Smith)')
            # name question
            if(step == 'What is your first and last name? (Ex: John Smith)'):
                if(len(msgs[0].content.rsplit(' ')) == 1):
                    # makes sure it is a first and last name, no clue if I'm being racist with this one though
                    await message.author.send('That is not a first and last name, please run the command again in the server to continue registration')
                else:
                    for player in registering:
                        if(player.discord_id == message.author.id):
                            # set's the name of the player
                            player.setname(f'{message.content}')
                    await message.author.send('Please upload a picture of yourself for the paper ID')
            # picture question
            if(step == 'Please upload a picture of yourself for the paper ID'):
                if(message.attachments == []):
                    # makes sure there is an attachment
                    await message.author.send('You did not send an image, please run the command again in the server to continue registration')
                    return
                if(not message.attachments[0].content_type.startswith('image')):
                    # makes sure there is an image attachment, works with pngs and jpgs (as far as I know and tested)
                    await message.author.send('You did not send an image, please run the command again in the server to continue registration')
                    return
                else:
                    # saves the image to player_pictures
                    await message.attachments[0].save(f'{file_path}/player_pictures/{message.author.id}.png')
                    hvz_guild = bot.get_guild(hvz_guild_id) # HVZ Poly server
                    hvz_member = await hvz_guild.fetch_member(message.author.id) # Member object in the HVZ Poly server
                    await hvz_member.add_roles(hvz_guild.get_role(player_role_id)) # gives player role 1216845310425432104
                    await hvz_member.add_roles(hvz_guild.get_role(human_role_id)) # gives human role 1216845309309620256
                    global hum
                    hum += 1
                    await updatePresence()
                    # TODO: Create the image
                    for player in registering:
                        if(player.discord_id == message.author.id):
                            # dumps the player info to the CSV file as soon as they're done registering as they have uploaded their picture
                            await player.dumpToCSV()
                            await player.generateID() # generate the ID
                            break
                    print(f'{message.author.name} has registered')
                    await message.author.send('Thank you for registering. Here is your virtual ID, if you get tagged, please show this to the zombie that tagged you so they can log the tag.')
                    await message.author.send('Failure to do this will get you banned from the rest of the game.')
                    await message.author.send(file=discord.File(f'{file_path}/player_ids/{message.author.id}_id.png'))
            if(step == 'What is your first and last name? (Ex: Eli Wolfe)'):
                with open(file=f'{file_path}/mod_data.csv', mode="a", newline='') as csv_file:
                    # Create a writer object
                    csv_writer = csv.writer(csv_file)
                    # Write the new data to the file
                    csv_writer.writerow([f'{message.author.id}', f'{message.content}']) # Creates a row for the discord ID, and name
                await message.author.send('Please write out a brief description of yourself to be displayed with the whois command')
            if(step == 'Please write out a brief description of yourself to be displayed with the whois command'):
                with open(file=f'{file_path}/mod_descriptions/{message.author.id}.txt', mode='w') as file:
                    file.write(message.content) # Generates a text file with a description of each moderator that registers
                await message.author.send('Finally, please upload a picture of yourself to be displayed with the whois command')
            if(step == 'Finally, please upload a picture of yourself to be displayed with the whois command'):
                await message.attachments[0].save(f'{file_path}/player_pictures/{message.author.id}.png')
                await message.author.send('Thank you for registering as a mod!')
            if(step == 'Please upload a picture for the user you are registering.'):
                hvz_guild = bot.get_guild(hvz_guild_id)
                hvz_member_id = None
                mr_index = 0
                for mr in manual_register:
                    if(mr.get("mod") == message.author.id):
                        await message.attachments[0].save(f'{file_path}/player_pictures/{mr.get("registering").discord_id}.png')
                        await mr.get("registering").dumpToCSV()
                        await mr.get("registering").generateID()
                        hvz_member_id = mr.get("registering").discord_id
                        mr_index = manual_register.index(mr)
                        break

                if(hvz_member_id == None):
                    message.author.send('Could not find the player you are registering, oops')
                    return
                
                manual_register.pop(mr_index)

                hvz_member = await hvz_guild.fetch_member(hvz_member_id)
                await hvz_member.add_roles(hvz_guild.get_role(player_role_id)) # gives player role
                await hvz_member.add_roles(hvz_guild.get_role(human_role_id)) # gives human role
                hum += 1
                await updatePresence()
                await message.author.send(file=discord.File(f'{file_path}/player_ids/{hvz_member_id}_id.png'))

    if(channel.id == registation_channel): # If a person just types nonsense in the registration channel
        try: # have to use a try except because it'll get deleted by the bot before if the user runs a command
            await message.delete()
        except:
            pass

@bot.command(description="Shows the game map", guild_ids=[hvz_guild_id])
async def map(ctx):
    # map command, more or less for testing but useful nonetheless
    await ctx.respond(file=discord.File(f'{file_path}/map.png'), ephemeral=True)

@bot.command(description="Register for the game", guild_ids=[hvz_guild_id])
async def register(ctx):
    for role in ctx.author.roles:
        if(role == ctx.author.guild.get_role(player_role_id)): # Checks to see if a person has registered before
            await ctx.respond('You have already registered! Please see a mod if you think there is an issue.', ephemeral=True)
            return
    try:
        await ctx.author.send('What is your student email address? (example: jsmith1234@floridapoly.edu)') # Starts the registration process in the DMs
        await ctx.respond('Check the DM message from the bot for instructions to register', ephemeral=True)
    except discord.errors.Forbidden:
        print(f'The bot could not DM user {ctx.author.name}')
        await ctx.respond('The bot could not DM you, if you have DMs from non-friends turned off, please enable the setting so the bot can DM you. You are welcome to turn this setting back after registering.', ephemeral=True)

@bot.command(description="Manually register a player for the game", guild_ids=[hvz_guild_id])
async def manualregister(ctx, player: discord.SlashCommandOptionType.user, name: str, email: str):
    hvz_id = np.random.randint(100000,999999)
    with open(file=f'{file_path}/player_data.csv', mode="r") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            # makes sure there are no duplicate IDs
            if(row[0] == 'HvZ_ID'): # Just don't read the header line
                continue
            if(row == []): # Don't read a blank line
                continue
            while(hvz_id == type(int(row[0]))):
                hvz_id = np.random.randint(100000,999999)
    pl = Player(player.id, hvz_id, email)
    pl.setname(name)
    manual_register.append(dict(mod=ctx.author.id, registering=pl))
    await ctx.author.send('Please upload a picture for the user you are registering.')
    await ctx.respond('Check the DM message from the bot to finalize the registration', ephemeral=True)

@bot.command(description="Register as a mod", guild_ids=[hvz_guild_id])
async def modregister(ctx):
    await ctx.author.send('What is your first and last name? (Ex: Eli Wolfe)') # Starts the registration process in the DMs
    await ctx.respond('Check the DM message from the bot for instructions to register', ephemeral=True)

@bot.command(description="Find information about a player", guild_ids=[hvz_guild_id])
async def whois(ctx, player: discord.SlashCommandOptionType.user):
    for role in player.roles:
        if(role == player.guild.get_role(mod_role_id)): # Checks to see if the person that they are looking up is a mod
            embeded = discord.Embed(title="WhoIs Result")
            name = ''
            desc = ''
            with open(f'{file_path}/mod_data.csv', mode='r') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if(row[0] == str(player.id)):
                        name = row[1] # Sets the name value to the moderator's name
            embeded.add_field(name="Name", value=f'{name}')
            embeded.add_field(name="Faction", value="Moderator")
            with open(f'{file_path}/mod_descriptions/{player.id}.txt', mode='r') as f:
                desc = f.read() # Sets the description value to the moderator's description
            embeded.add_field(name="Mod description", value=f'{desc}', inline=False)
            file = discord.File(f'{file_path}/player_pictures/{player.id}.png')
            embeded.set_image(url=f'attachment://{player.id}.png') # Have to add the image as an attachment for embeds
            await ctx.respond(file=file, embed=embeded, ephemeral=True)
            return
    index = 0
    with open(file=f'{file_path}/player_data.csv', mode="r") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if(row[1] == str(player.id)):
                file = discord.File(f'{file_path}/player_pictures/{player.id}.png')
                embed = discord.Embed(title="WhoIs Result")
                embed.add_field(name="Player Name", value=f'{row[3]}')
                embed.set_image(url=f'attachment://{player.id}.png')
                if(type(bool(row[4])) == False):
                    embed.add_field(name="Faction", value="Human")
                else:
                    embed.add_field(name="Faction", value="Zombie")
                await ctx.respond(file=file, embeds=[embed], ephemeral=True)
                return
            index += 1
        await ctx.respond(f'They are not a registered player, sorry!', ephemeral=True) # If the person that is looked up is not a player or moderator, it returns this error

@bot.command(description="Sends the player's ID card", guild_ids=[hvz_guild_id])
async def modwhois(ctx, player: discord.SlashCommandOptionType.user):
    try:
        file = discord.File(f'{file_path}/player_ids/{player.id}_id.png') # Sends the image file of an ID
        await ctx.respond(file=file, ephemeral=True)
    except:
        await ctx.respond('They are not a registered player, sorry!', ephemeral=True)

@bot.command(description="Mod a user", guild_ids=[hvz_guild_id])
async def mod(ctx, id: int):
    with open(file=f'{file_path}/player_data.csv', mode='r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if(row[0] == str(id)):
                post_data = {
                    "player_id": int(id)
                }
                if(use_website):
                    post_request = requests.post(f'{backend_path}{mod_path}', json=post_data) # Just sends a mod player packet to the website
                    print(post_data)
                    print(post_request.status_code)
                global hum
                hum -= 1 # Removes the amount of humans left since the moderator was considered human before
                await updatePresence()
                await ctx.respond(f'Successfully modded {row[3]} on the website!', ephemeral=True)

@bot.command(description="Tag a player", guild_ids=[hvz_guild_id])
async def tag(ctx, id: int):
    index = 0
    with open(file=f'{file_path}/player_data.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        z_id = 0
        for ro in csv_reader:
            if(ro[1] == str(ctx.author.id)):
                z_id = ro[0] # Finds the ID of the player running this command
                break

    with open(file=f'{file_path}/player_data.csv', mode="r") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if(row[0] == str(id)):
                df = pd.read_csv(f'{file_path}/player_data.csv')
                if(df.at[index-1, 'Zombie'] == True): # Checks to see if the person they are tagging is already a zombie
                    await ctx.respond(f'{row[3]} is already a zombie!', ephemeral=True)
                    return
                df.at[index-1, 'Zombie'] = True # Sets the person to a zombie in the db
                hvz_guild = ctx.author.guild
                hvz_member = await hvz_guild.fetch_member(row[1])
                global zom
                global hum
                zom += 1
                hum -= 1
                await updatePresence() # Updates the bot's player count
                await hvz_member.add_roles(hvz_guild.get_role(zombie_role_id)) # Adds the respective roles
                await hvz_member.remove_roles(hvz_guild.get_role(human_role_id))
                await hvz_guild.get_channel(tags_channel).send(f'{hvz_member.name} was tagged by {ctx.author.name}, {hum} humans left!') # Sends a message in the tags channel
                df.to_csv(f'{file_path}/player_data.csv', index=False, float_format='%g') # CSV gets updated
                post_data = {
                    "human_id": int(id),
                    "zombie_id": int(z_id)
                }
                if(use_website):
                    post_request = requests.post(f'{backend_path}{infection_path}', json=post_data) # Infection packet to the website
                    print(post_data)
                    print(post_request.status_code)
                await ctx.respond(f'Successfully tagged {hvz_member.name}')
                return
            index += 1
        await ctx.respond(f'{id} is not a valid ID!', ephemeral=True)

@bot.command(description="OZ a player", guild_ids=[hvz_guild_id])
async def oz(ctx, id: int):
    index = 0
    with open(file=f'{file_path}/player_data.csv', mode="r") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if(row[0] == str(id)):
                df = pd.read_csv(f'{file_path}/player_data.csv')
                if(df.at[index-1, 'Zombie'] == True):
                    await ctx.respond(f'{row[3]} is already a zombie!', ephemeral=True)
                    return
                df.at[index-1, 'Zombie'] = True
                hvz_guild = ctx.author.guild
                hvz_member = await hvz_guild.fetch_member(row[1])
                global zom
                global hum
                zom += 1
                hum -= 1
                await updatePresence()
                await hvz_member.add_roles(hvz_guild.get_role(zombie_role_id))
                await hvz_member.remove_roles(hvz_guild.get_role(human_role_id))
                await hvz_member.add_roles(hvz_guild.get_role(oz_role_id))
                await hvz_guild.get_channel(tags_channel).send(f'{row[3]} is now an OZ, {hum} humans left!')
                df.to_csv(f'{file_path}/player_data.csv', index=False, float_format='%g')
                post_data = {
                    "player_id": int(id)
                }
                if(use_website):
                    post_request = requests.post(f'{backend_path}{oz_path}', json=post_data)
                    print(post_data)
                    print(post_request.status_code)
                await ctx.respond(f'Successfully tagged {hvz_member.name}', ephemeral=True)
                return
            index += 1
        await ctx.respond(f'{id} is not a valid ID!', ephemeral=True)

@bot.command(description="Wipe the website database (Please only do this if you are super duper sure)", guild_ids=[hvz_guild_id])
async def wipewebsite(ctx, password:str):

    post_data = {
        "password": str(password)
    }

    if(use_website):
        post_request = requests.post(f'{backend_path}{wipe_path}', json=post_data)
        print(post_data)
        print(post_request.status_code)
        await ctx.respond(f'The website data base has been cleared!', ephemeral=True)
    else:
        await ctx.respond(f'Local wiping not implemented yet, fuck you bitch', ephemeral=True)

@bot.command(description="Cure a player", guild_ids=[hvz_guild_id])
async def cure(ctx, id: int):
    index = 0
    with open(file=f'{file_path}/player_data.csv', mode="r") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if(row[0] == str(id)):
                df = pd.read_csv(f'{file_path}/player_data.csv')
                if(df.at[index-1, 'Zombie'] == False):
                    await ctx.respond(f'{row[3]} is not a zombie!', ephemeral=True)
                    return
                df.at[index-1, 'Zombie'] = False
                hvz_guild = ctx.author.guild
                hvz_member = await hvz_guild.fetch_member(row[1])
                global zom
                global hum
                zom -= 1
                hum += 1
                await updatePresence()
                await hvz_member.remove_roles(hvz_guild.get_role(zombie_role_id))
                await hvz_member.add_roles(hvz_guild.get_role(human_role_id))
                await hvz_member.add_roles(hvz_guild.get_role(cured_role_id))
                await hvz_guild.get_channel(tags_channel).send(f'{row[3]} was cured, {hum} humans left!')
                df.to_csv(f'{file_path}/player_data.csv', index=False, float_format='%g')
                post_data = {
                    "player_id": int(id)
                }
                if(use_website):
                    post_request = requests.post(f'{backend_path}{cure_path}', json=post_data)
                    print(post_data)
                    print(post_request.status_code)
                await ctx.respond(f'Successfully cured {hvz_member.name}', ephemeral=True)
                return
            index += 1
        await ctx.respond(f'{id} is not a valid ID!', ephemeral=True)

@bot.command(description="Purge a channel of text messages", guild_ids=[hvz_guild_id])
async def purgechannel(ctx):
    # Will try to remove all of the text messsages from a discord channel, it can time out if there are too many messages
    messages = ctx.channel.history()
    async for msg in messages:
        await msg.delete()
    await ctx.respond('Channel cleared!', ephemeral=True)

@bot.command(description="Remove a player from the game", guild_ids=[hvz_guild_id])
async def removeplayer(ctx, id: int):
    # Removes a player from the game count to keep an accurate count of players for each team.
    index = 0
    with open(file=f'{file_path}/player_data.csv', mode='r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if(row[0] == 'HvZ_ID'): 
                index += 1
                continue
            if(int(row[0]) == id): break
            index += 1
    
    df = pd.read_csv(f'{file_path}/player_data.csv')
    if(df.at[index-1, 'InPlay'] == False):
        await ctx.respond(f'{df.at[index-1, "Name"]} is not in play!', ephemeral=True)
        return
    else:
        df.at[index-1, 'InPlay'] = False
        if(df.at[index-1, 'Zombie'] == True):
            global zom
            zom -= 1
        else:
            global hum
            hum -= 1
        await updatePresence()
        df.to_csv(f'{file_path}/player_data.csv', index=False, float_format='%g')
        post_data = {
            "player_id": int(id)
        }
        if(use_website):
            post_request = requests.post(f'{backend_path}{player_removal_path}', json=post_data)
            print(post_data)
            print(post_request.status_code)
        await ctx.respond(f'{df.at[index-1, "Name"]} has been removed from play!', ephemeral=True)

@dataclass
class player:
    id: int
    name: str
    status: int
    tags: int
    image: str
    named_tags: str

class Player:
    def __init__(self, discord_id, hvz_id, email):
        self.discord_id = discord_id # discord ID
        self.hvz_id = hvz_id # randomized HvZ ID (100000-999999) this will be what players type in to tag someone
        self.email = email # poly email
    
    name = '' # name, not in the constructor cause you don't originally have a name when making the player instance
    zombie = False # Whether the player is a human or zombie

    def setname(self, name):
        self.name = name # sets the name of the player
    
    async def dumpToCSV(self):
        # Opens a CSV File
        with open(file=f'{file_path}/player_data.csv', mode="a", newline='') as csv_file:
            # Create a writer object
            csv_writer = csv.writer(csv_file)
            # Write the new data to the file
            csv_writer.writerow([f'{self.hvz_id}', f'{self.discord_id}', f'{self.email}', f'{self.name}', f'{self.zombie}', '0', True]) # Creates a row for the discord ID, HvZ ID, Email, and Name
            registered.append(self.discord_id) # Puts the discord ID in the registered list
        if(use_website):
            await self.dumpToWebsite()
    
    async def dumpToWebsite(self):
        img = Image.open(f'{file_path}/player_pictures/{self.discord_id}.png').resize((150,150))
        im_file = BytesIO()
        img.save(im_file, format="PNG")
        im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
        im_b64 = base64.b64encode(im_bytes).decode('utf-8')

        global player
        player_data = player(
            id = self.hvz_id,
            name = self.name,
            status = 0,
            tags = 0,
            image = f'data:image/png;base64,{im_b64}',
            named_tags = ''
        )

        post_data = asdict(player_data)

        post_request = requests.post(f'{backend_path}{player_creation_path}', json=post_data)
        print(post_request.status_code)

    async def generateID(self):
        hvz_guild = bot.get_guild(hvz_guild_id) # HVZ Poly Discord
        hvz_member = await hvz_guild.fetch_member(self.discord_id) # Gets the member in the HVZ Poly Discord
        template_image = Image.open(f'{file_path}/id_card_template.png') # Opens the ID template
        face_picture = Image.open(f'{file_path}/player_pictures/{self.discord_id}.png') # Opens the player's face image
        face_im = face_picture.copy() # Copies the face image to a seperate instance
        face_im = face_im.resize((160,160)) # Resizes the face image to 160 x 160
        back_im = template_image.copy() # Copies the template image to a seperate instance
        back_im.paste(face_im, (27,28)) # pastes the face image resized to the square
        draw = ImageDraw.Draw(back_im) # creates a draw instance for the ID picture
        draw.text((325, 52), f'{self.name}', (0,0,0), font_size=24) # Draws the player's name onto the ID picture
        draw.text((330, 103), f'{self.hvz_id}', (0,0,0), font_size=24) # Draws the player's HvZ ID onto the ID picture
        draw.text((340, 160), f'{hvz_member.name}', (0,0,0), font_size=24) # Draws the player's discord handle onto the ID picture
        back_im.save(f'{file_path}/player_ids/{self.discord_id}_id.png') # saves the edited image to a file

bot.run(bot_id) # Runs the bot with the correct token, do not put this in a github or anything like that istg