# botmanager.py
# This is a Discord Bot capable of monitoring the status of other python scripts
# One possible use case is to manage other discord bots.
# 
# Choose a name for your scripts and add it to AUTHORIZED_SCRIPTS below.
# Also change the DISCORD_TOKEN in your .env file, and you will be good to go.
# Start this bot, and the bot will start your other scripts. 
# 
# You will be able to use the following commands:
# status  (check the status alive/dead of your scripts)
# start   (start a python script)
# kill    (kill a running python script)
# restart (restart a python script)
# 
# Good luck!

import os
import sys
import subprocess

from dotenv import load_dotenv
import csv

import discord
from discord.ext import commands

# Set the constants to be used throughout the program
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('DISCORD_PREFIX')
PYTHON_EXE = sys.executable
PATH_PREF = sys.path[0] + "/"
AUTHORIZED_SCRIPTS_FILE = os.getenv('SCRIPT_LOCATION')
AUTHORIZED_SCRIPTS = {}

def getScriptLocations():
    with open(AUTHORIZED_SCRIPTS_FILE, 'r') as scriptFile:
        reader = csv.reader(scriptFile,delimiter=":")
        for line in reader:
            name = line[0]
            filepath = line[1]
            if os.path.isfile(filepath):
                AUTHORIZED_SCRIPTS[line[0]] = line[1]
            else:
                print("For key [", name, "], could not find matching file [", filepath, "]. Ignoring.")

getScriptLocations()

print("Authorized scripts:")
for name,script in AUTHORIZED_SCRIPTS.items():
    print("Key [", name, "] for script [", script, "]")
print("")

# Class to define the operations allowed on scripts
class BotProcess:
    def __init__(self, script_key : str):
        if script_key in AUTHORIZED_SCRIPTS:
            self.cmd = AUTHORIZED_SCRIPTS[script_key]
            self.name = script_key
            self.subproc = None
            self.start()
        else:
            self.cmd = ""
            self.name = "unauthorized script"
            self.subproc = None
    
    def __str__(self):
        return self.name

    def isRunning(self):
        if self.subproc is None:
            return False
        self.subproc.poll()
        return self.subproc.returncode is None
    
    def start(self):
        if self.isRunning():
            return
        self.subproc = subprocess.Popen(args=[PYTHON_EXE, self.cmd], shell=False)

    def kill(self):
        if self.subproc is None:
            return
        if self.isRunning():
            self.subproc.kill()

    def restart(self):
        if self.subproc is None:
            self.start()
        else:
            self.kill()
            self.start()        

# Create BotProcess's for each authorized script
bots = {}
for name,script in AUTHORIZED_SCRIPTS.items():
    bots[name] = BotProcess(name)

async def sendStatus(channel : discord.TextChannel):
    runningProcs = "```"
    for bot in bots.values():
        if bot.isRunning():
            runningProcs = runningProcs + "Alive:\t"
        else:
            runningProcs = runningProcs + "Dead: \t"
        runningProcs = runningProcs + str(bot) + "\n"
    runningProcs = runningProcs + "```"
    await channel.send(runningProcs)

# Create this discord bot
dbot = discord.ext.commands.Bot(command_prefix=PREFIX, description="A bot manager to start, stop and restart bots")

@dbot.event
async def on_ready():
    pass
    # Do nothing when connected

@dbot.command(name="status", brief="Shows which bots are running", 
    help="Prints a message for each bot indicating whether it is alive or not.")
async def status(ctx):
    await ctx.message.add_reaction('✅')
    await sendStatus(ctx.channel)

@dbot.command(name="kill", brief="Kills the specified bot")
async def kill(ctx):
    botname = ctx.message.content.replace(PREFIX+"kill ","")
    try:
        bots[botname].kill()
        await ctx.message.add_reaction('💣')
        await ctx.message.add_reaction('✅')
    except KeyError:
        await ctx.send("No bot matching [" + botname + "] was found.")

@dbot.command(name="start", brief="Starts the specified bot")
async def start(ctx):
    botname = ctx.message.content.replace(PREFIX+"start ","")
    try:
        bots[botname].start()
        await ctx.message.add_reaction('🫀')
        await ctx.message.add_reaction('✅')
    except KeyError:
        await ctx.send("No bot matching [" + botname + "] was found.")

@dbot.command(name="restart", brief="Restarts the specified bot")
async def restart(ctx):
    botname = ctx.message.content.replace(PREFIX+"restart ","")
    try:
        bots[botname].restart()
        await ctx.message.add_reaction('🫀')
        await ctx.message.add_reaction('✅')
    except KeyError:
        await ctx.send("No bot matching [" + botname + "] was found.")

try:
    dbot.run(TOKEN)
except (AttributeError, discord.errors.LoginFailure) as err:
    print("Invalid token supplied (check .env file)")
except Exception as err:
    print("Exception when trying to start the bot: [", type(err).__name__, "]")

print("Killing bots")
for bot in bots.values():
    print("\tKilling ", bot, "... ", end="")
    bot.kill()
    print(" done.")

print("Goodbye")
