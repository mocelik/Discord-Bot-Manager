# botmanager.py
# manages other discord bots
# TODO: Add instructions

import os
import sys
import subprocess

from dotenv import load_dotenv

import discord
from discord.ext import commands

# Set the constants to be used throughout the program
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('DISCORD_PREFIX')
PYTHON_EXE = sys.executable
PATH_PREF = sys.path[0] + "/"
AUTHORIZED_SCRIPTS = {"hello_world": PATH_PREF + "hello_world.py", "sleepy": PATH_PREF + "sleep.py"}

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
except AttributeError:
    print("Invalid token supplied (check .env file)")

