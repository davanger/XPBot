import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
import configparser
from tinydb import TinyDB, Query

# Read client secret from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
discordConfig = config['Discord']

# Set up the database

db = TinyDB("xpBotDB.json")
playersDB = Query()

# Here you can modify the bot's prefix and description and wether it sends help in direct messages or not.
client = Bot(description="XP bot by Davanger", command_prefix="$", pm_help = True)

# Console greeting message.

@client.event
async def on_ready():
	print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
	print('--------')
	print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
	print('--------')
	print('Use this link to invite {}:'.format(client.user.name))
	print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))

# Game info functions

def dbAddXp(playerName, xp):
	dbPlayer = db.search(playersDB.name == playerName)
	if len(dbPlayer) == 1:
		dbXP = dbPlayer[0]['xp']
		dbXP = dbXP + xp
		db.update({'xp': dbXP}, playersDB.name == playerName)
	elif len(dbPlayer) == 0:
		db.insert({'type': 'player', 'name': playerName, 'xp': xp})
	else:
		print("Duplicate user error")

#def addXp(player, xp):
#	if player in players:
#		players[player] = players[player] + xp
#	else:
#		players[player] = xp

def dbClearXp(playerName):
	db.remove(playersDB.name == playerName)

#def clearXp(player):
#	try:
#		players[player] = 0
#	except:
#		print("Player {} doesn't exist!".format(player))

def dbSetXp(playerName, xp):
	dbPlayer = db.search(playersDB.name == playerName)
	if len(dbPlayer) == 1:
		db.update({'xp': xp}, playersDB.name == playerName)
	elif len(dbPlayer) == 0:
		db.insert({'type': 'player', 'name': playerName, 'xp': xp})
	else:
		print("Duplicate user error: {}".format(playerName))

# Discord commands

@client.command(pass_context=True)
async def fail(ctx):
	await client.say("Failed throw, adding 1 XP to {}.".format(ctx.message.author.mention))
	dbAddXp(ctx.message.author.mention,1)
	await asyncio.sleep(3)
		
@client.command(pass_context=True)
async def gainxp(ctx, *args):
	if(len(args) == 1):
		try:
			await client.say("Adding " + str(int(args[0])) + " XP to {}".format(ctx.message.author.mention))
			dbAddXp(ctx.message.author.mention,int(args[0]))
			await asyncio.sleep(3) 
		except: #user didn't pass an int
			await client.say("The XP you're adding must be a number.")
			await asyncio.sleep(3)
	else:
		await client.say("The XP you're adding must be a number.")
		await asyncio.sleep(3)

@client.command(pass_context=True)
async def remxp(ctx, *args):
	if(len(args) == 1):
		try:
			await client.say("Removing " + str(int(args[0])) + " XP from {}".format(ctx.message.author.mention))
			dbAddXp(ctx.message.author.mention,-int(args[0]))
			await asyncio.sleep(3) 
		except: #user didn't pass an int
			await client.say("The XP you're removing must be a number.")
			await asyncio.sleep(3)
	else:
		await client.say("The XP you're adding must be a number.")
		await asyncio.sleep(3)

@client.command(pass_context=True)
async def listxp():
	playersList = db.search(playersDB.type == 'player')
	if len(playersList) > 0:
		output = "Current XP table:"
		for player in playersList:
			output = output + "\n" + "{}: {} XP".format(player['name'], str(player['xp']))
#			await client.say("{}: {} XP".format(player, str(players[player])))
#			await asyncio.sleep(3)
		await client.say(output)
		await asyncio.sleep(3)
	else:
		await client.say("There haven't been any registered XP.")
		await asyncio.sleep(3)

@client.command(pass_context=True)
async def resetxp(ctx):
	playersList = db.search(playersDB.type == 'player')
	if len(playersList) > 0:
		await client.say("Resetting XP for {}".format(ctx.message.author.mention))
		dbClearXp(ctx.message.author.mention)
		await asyncio.sleep(3)
	else:
		await client.say("There haven't been any registered XP.")
		await asyncio.sleep(3)

@client.command(pass_context=True)
async def resetallplayerxp():
	playersList = db.search(playersDB.type == 'player')
	if len(playersList) > 0:
		output = "Resetting XP table:"
		for player in playersList:
			dbClearXp(player)
			#output = output + "{}: {} XP".format(player, str(players[player]))
			#await client.say(output)
			#await asyncio.sleep(3)
		listxp() # shouldn't return anything since the player table should be empty by this point
	else:
		await client.say("There arent any players with registered XP.")
		await asyncio.sleep(3)

@client.command(pass_context=True)
async def setxp(ctx, *args):
	if(len(args) == 1):
		try:
			await client.say("Setting {}'s XP to ".format(ctx.message.author.mention) + str(int(args[0])) + " XP.")
			dbSetXp(ctx.message.author.mention, int(args[0]))
			await asyncio.sleep(3) 
		except: #user didn't pass an int
			await client.say("The XP must be a number.")
			await asyncio.sleep(3)
	else:
		await client.say("The XP must be a number.")
		await asyncio.sleep(3)

@client.command()
async def helpxp():
	output = "XP Helper Bot \n"
	output = output + "Available commands: \n"
	output = output + "$fail: Failed throw, add 1 XP to player.\n"
	output = output + "$gainxp: Gain the number of XP passed to the command. i.e.: $gainxp 2 \n"
	output = output + "$setxp: Set player's XP to an specific amount. i.e.: $setxp 5 \n"
	output = output + "$remxp: Remove the number of XP passed to the command. i.e.: $remxp 2 \n"
	output = output + "$resetxp: Set player's XP to 0.\n"
	output = output + "$resetallplayerxp: Set ALL player's XP to 0.\n"
	output = output + "$listxp: Lists the current XP table for all players.\n"
	output = output + "$helpxp: Lists the available commands and their description."
	await client.say(output)
	await asyncio.sleep(3)
	
client.run(discordConfig["ClientSecret"])
