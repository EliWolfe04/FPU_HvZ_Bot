import discord # type: ignore
import numpy as np # type: ignore
import csv # CSV Library
from PIL import Image, ImageDraw # type: ignore
import pandas as pd # type: ignore

intents = discord.Intents.default() # idk what the default intents are but oh well
intents.message_content = True # allows to see message content
intents.dm_messages = True # allows to dm players
intents.guild_messages = True # allows to send messages in the server (I think)

client = discord.Client(intents=intents) # Discord client with intents added

registering = [] # list of players registering
registered = [] # list of players registered, this does mean that the bot probably shouldn't go offline, maybe I'll fix that?

file_path = '' # String of the file path to the folder
client_id = '' # The bot ID to run the bot
registation_channel = 0 # Registration channel ID
mod_channel = 0 # Mod bot channel ID
tagging_channel = 0 # Tagging channel ID
tags_channel = 0 # Tags channel ID
human_role_id = 0 # Human role ID
zombie_role_id = 0 # Zombie role ID
player_role_id = 0 # Player role ID
hvz_guild_id = 0 # Guild ID

hum = 0
zom = 0

@client.event
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
                registered.append(row[1])
                if row[4] == "True":
                    z = z + 1 # Adds Z Count
                else:
                    h = h + 1 # Adds H Count
    
    global zom
    global hum
    hum = h # Dumb python bs
    zom = z # Dumb python bs
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{zom} Zs vs {hum} Humans')) # Changes the discord status
    print('These discord IDs have been registered!')
    print(f'{len(registered)} accounts registered')

    print(f'We have logged in as {client.user}') # Prints in the console once the bot is online and ready, crucial

@client.event
async def on_message(message):
    if(message.author == client.user):
        # makes sure that the bot ignores any message it sends because I guess it's message also trigger this event?
        return

    if(message.channel.type != discord.ChannelType.private):
        if(message.guild.id != hvz_guild_id):
            # makes sure this is in the right server
            await message.channel.send('This bot is not supposed to be in this server, please remove it immediately')
            return

    channel = message.channel
    # How I am adding commands because slash commands don't like me :(
    if(message.content.startswith('$')):
        cmd = message.content.replace('$','') # removes the $ from the message to give me a command
        if(cmd.startswith('map')):
            # map command, more or less for testing but useful nonetheless
            if(channel.id == registation_channel):
                await message.delete()
                return
            else:
                await channel.send(file=discord.File(f'{file_path}/map.png'))
        if(cmd.startswith('register')):
            await message.delete()
            #for reg in registered:
                # checks if the player has already been registered so that they cannot double register 
                #if(reg == message.author.id):
                #    await message.author.send('You have already registered, if you need something changed, please ask a mod')
                #    return
            await message.author.send('What is your florida poly email address?') # starts a dm with the player to get registration done
        # TODO: Add Cure Command (Just the opposite of tag)
        if(cmd.startswith('cure')): # Cure command isn't finished, too eepy to try
            arg = cmd.replace('cure ', '')
            if(channel.id != mod_channel):
                await message.delete()
                return
            if(arg == cmd):
                await channel.send('Please enter a valid ID')
                return
            args = arg.split(' ')
            pass
        if(cmd.startswith('tag')):
            arg = cmd.replace('tag ', '')
            if(channel.id == registation_channel): # Registration channel deletion
                await message.delete()
                return
            if(channel.id != tagging_channel): # Refuses to use the command in any channel other than tagging
                await message.delete()
                return
            else:
                if(arg == cmd): # They just didn't enter an ID
                    await channel.send('Please enter a valid ID')
                    return
                index = 0 # index of what row the reader is on
                with open(file=f'{file_path}/player_data.csv', mode="r") as f:
                    csv_reader = csv.reader(f)
                    for row in csv_reader:
                        if(row[0] == arg): # If the HvZ ID of the row matches the ID inputted
                            df = pd.read_csv(f'{file_path}/player_data.csv')
                            if(df.at[index-1,'Zombie'] == True): # Makes sure the player isn't a Zombie yet
                                await channel.send(f'{row[3]} is already a zombie!')
                                return
                            df.at[index-1, 'Zombie'] = True # Sets the player to a zombie
                            hvz_guild = message.author.guild
                            hvz_member = await hvz_guild.fetch_member(row[1])
                            global zom # stupid shit python makes me do
                            global hum
                            zom += 1 # changes the count
                            hum -= 1 # changes the count
                            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{zom} Zs vs {hum} Humans')) # Updates the discord status
                            await hvz_member.add_roles(hvz_guild.get_role(zombie_role_id)) # Adds the zombie role
                            await hvz_member.remove_roles(hvz_guild.get_role(human_role_id)) # Removes the human role
                            await channel.send(f'Successfully tagged {hvz_member.name}') # Gives a success response message
                            await hvz_guild.get_channel(tags_channel).send(f'{hvz_member.name} was tagged by {message.author.name}, {hum} humans left!') # Sends the message in the tags channel
                            df.to_csv(f'{file_path}/player_data.csv', index=False, float_format='%g') # Writes back to the CSV that the player is a zombie, float format is so that it doesn't add stupid fucking decimals
                            return
                        index += 1
                await channel.send(f'{arg} is not a valid ID!') # If the ID is not found in the file, it sends an invalid ID error
    
    # checks to see if this is a message in a dm
    if(channel.type == discord.ChannelType.private):
        messages = channel.history(limit=2) # gets the last two messages in the dm channel, it should be the email question and the user responding with an email
        msgs = [] # holds the two messages
        # appends the two messages to a list
        async for msg in messages:
            msgs.append(msg)
        # checks to see if the first message is from the bot (it should be the email question)
        if(msgs[1].author == client.user):
            # step is what step of the questioning they are on
            step = msgs[1].content
            # email question
            if(step == 'What is your florida poly email address?'):
                # makes sure the player is a poly student (non-poly students should be registered manually)
                if(not msgs[0].content.endswith('@floridapoly.edu')):
                    await message.author.send('That is not a florida poly email, please run the command again in the server to continue registration')
                else:
                    # Creates a player instance and adds them to the registering list
                    hvz_id = np.random.randint(10000,99999)
                    with open(file=f'{file_path}/player_data.csv', mode="r") as f:
                        csv_reader = csv.reader(f)
                        for row in csv_reader:
                            # makes sure there are no duplicate IDs
                            if(row[0] == 'HvZ_ID'): # Just don't read the header line
                                continue
                            if(row == []): # Don't read a blank line
                                continue
                            if(hvz_id == type(int(row[0]))): # If the randomized HvZ ID already exists, create a new one, surely the 2nd generated one won't already exist
                                hvz_id = np.random.randint(10000,99999)
                    player = Player(message.author.id, hvz_id, message.content)
                    registering.append(player)
                    await message.author.send('What is your first and last name?')
            # name question
            if(step == 'What is your first and last name?'):
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
                    hvz_guild = client.get_guild(hvz_guild_id) # HVZ Poly server
                    hvz_member = await hvz_guild.fetch_member(message.author.id) # Member object in the HVZ Poly server
                    await hvz_member.add_roles(hvz_guild.get_role(player_role_id)) # gives player role 1216845310425432104
                    await hvz_member.add_roles(hvz_guild.get_role(human_role_id)) # gives human role 1216845309309620256
                    # TODO: Create the image
                    for player in registering:
                        if(player.discord_id == message.author.id):
                            # dumps the player info to the CSV file as soon as they're done registering as they have uploaded their picture
                            player.dumpToCSV()
                            await player.generateID() # generate the ID
                            break
                    print(f'{message.author.name} has registered')
                    await message.author.send('Thank you for registering. We will be printing and handing out the IDs at the end of the meeting (assuming you pass the quiz)')

    if(channel.id == registation_channel): # If a person just types nonsense in the registration channel
        try: # have to use a try except because it'll get deleted by the bot before if the user runs a command
            await message.delete()
        except:
            pass

class Player:
    def __init__(self, discord_id, hvz_id, email):
        self.discord_id = discord_id # discord ID
        self.hvz_id = hvz_id # randomized HvZ ID (10000-99999) this will be what players type in to tag someone
        self.email = email # poly email
    
    name = '' # name, not in the constructor cause you don't originally have a name when making the player instance
    zombie = False # Whether the player is a human or zombie

    def setname(self, name):
        self.name = name # sets the name of the player
    
    def dumpToCSV(self):
        # Opens a CSV File
        with open(file=f'{file_path}/player_data.csv', mode="a") as csv_file:
            # Create a writer object
            csv_writer = csv.writer(csv_file)
            # Write the new data to the file
            csv_writer.writerow([f'{self.hvz_id}', f'{self.discord_id}', f'{self.email}', f'{self.name}', f'{self.zombie}']) # Creates a row for the discord ID, HvZ ID, Email, and Name
            registered.append(self.discord_id) # Puts the discord ID in the registered list
    
    async def generateID(self):
        hvz_guild = client.get_guild(hvz_guild_id) # HVZ Poly Discord
        hvz_member = await hvz_guild.fetch_member(self.discord_id) # Gets the member in the HVZ Poly Discord
        template_image = Image.open(f'{file_path}/id_card_template.png') # Opens the ID template
        face_picture = Image.open(f'{file_path}/player_pictures/{self.discord_id}.png') # Opens the player's face image
        face_im = face_picture.copy() # Copies the face image to a seperate instance
        face_im = face_im.resize((160,160)) # Resizes the face image to 160 x 160
        back_im = template_image.copy() # Copies the template image to a seperate instance
        back_im.paste(face_im, (27,28)) # pastes the face image resized to the square
        draw = ImageDraw.Draw(back_im) # creates a draw instance for the ID picture
        draw.text((325,52), f'{self.name}', (0,0,0), font_size=24) # Draws the player's name onto the ID picture
        draw.text((330,103), f'{self.hvz_id}', (0,0,0), font_size=24) # Draws the player's HvZ ID onto the ID picture
        draw.text((340, 160), f'{hvz_member.name}', (0,0,0), font_size=24) # Draws the player's discord handle onto the ID picture
        back_im.save(f'{file_path}/player_ids/{self.discord_id}_id.png') # saves the edited image to a file

client.run(client_id) # Runs the client with the correct token, do not put this in a github or anything like that istg