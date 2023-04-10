from klee import const, members, helpers

import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta
from replit import db, database
from keep_alive import keep_alive
import nest_asyncio
import requests
import traceback
from operator import itemgetter

######################################################
# INIT PART 1 #
######################################################

nest_asyncio.apply()

client = commands.Bot(command_prefix='!')

reply_msg = ''

#creates a list for failed_msg
failed_msg = []

# initialize AGE_members slime count to 0
AGE_members = {}
for x in members.id_list():
    AGE_members[x] = 0

#valid_INIT_construction
member_count = db.keys(
)  #member_count is a dictionary containing all ids (string) of the members
for member_id in AGE_members:
    for db_member_id in member_count:
        if member_id == db_member_id:  #if both ids match
            AGE_members[member_id] = db[
                db_member_id]  #AGE_members is now a dictionary with keys(ids) to values(slimes counts)
        elif member_id not in member_count:
            db[member_id] = 0

#zoom_dictionaries INIT construction
zoom_member = {}  # key=member_id, value=# of times zoomed
zoom_time = {}  # key=member_id, value=specific time for when the player zoomed

#to initialize both zoom dictionaries from data store in replit db
for db_member_id in member_count:
    #for member_id that were from replit db
    if db_member_id.endswith('z'):
        #if the member_id ends with substring z
        zoom_member[db_member_id] = db[db_member_id]
        #initialize a key-value pair for that member_id to the number of times s/he zoomed

for member_idz in zoom_member:
    #going off the zoom dictionary that was created above, which has all who have zoomed
    member_idzt = member_idz + 't'
    #add a substring t for different condition check
    for db_member_id in member_count:
        if member_idzt == db_member_id:
            zoom_time[member_idzt] = db[db_member_id]
            #the value in this case is an array, which stores the specific times a player was reported zooming; and the key is the member_id + zt

# HELPER METHODS #

#check whether the author's id is the same as the specified user's id
def is_bot_admin(ctx):
    return ctx.author.id in const.BOT_ADMINS

def is_slime_admin(ctx):
    return ctx.author.id in const.DATA_ADMINS

#check whether it's in the specified channel
def in_slime_channel(ctx):
    return ctx.channel.id in const.BOT_CHANNELS

def is_any_word_in_string(wordlist, string):
    return any(word in string for word in wordlist)

#return formatted timestamp
def utcTimestamp():
    return f'{datetime.utcnow().replace(microsecond=0).isoformat()}Z'

def dt_from_timestamp(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')


#logging
logfileTimestamp = utcTimestamp()
logfile = f'log/{logfileTimestamp}_main.log'


#chatlogfile = f'log/{logfileTimestamp}_chat.log'
def log(logMessage, consoleMessage=None):
    timestamp = utcTimestamp()
    if consoleMessage is not None:
        print(f'{timestamp} {consoleMessage}')
    try:
        with open(f'{logfile}', 'a') as outfile:
            outfile.write(f'{timestamp} {logMessage}\n')
    except Exception as err:
        print(f'{timestamp} ERROR in log(): {err}')
    return timestamp


#error handler helper
def handleError(e):
    try:
        logTimestamp = log(
            f'ERROR TRACE:\n{traceback.format_exc()}# TRACE END\n')
        sendWebhook(
            f'Klee encountered an error :( Please check {logfile} at {logTimestamp} -> {type(e).__name__}.'
        )
    except Exception as err:
        print(f'{utcTimestamp()} ERROR in handleError(): {err}')


#helper to call discord webhook API
def sendWebhook(msg):
    webhookUrl = 'https://discord.com/api/webhooks/' + os.getenv(
        'WEBHOOK_ID_TOKEN')
    r = requests.post(webhookUrl, data={'content': msg})
    print(f'{utcTimestamp()} DEBUG Webhook response code: {r.status_code}')
    r.raise_for_status()  #raise error if response status_code is 4XX or 5XX



######################################################
# BOT EVENTS #
######################################################

#gets the bot online
@client.event
async def on_ready():
    try:
        await client.change_presence(status = discord.Status.online, \
                            activity = discord.Game(f'counting slimes since {utcTimestamp()} (UTC)'))
        #print(f'{utcTimestamp()} INFO Bot is ready.')
        log('Bot is ready.', 'INFO Bot is ready.')

        #if the failed_msg text is not empty, sends the msg to the corresponding channel, and then erase the txt file
        if len(failed_msg) != 0:
            channel = client.get_channel(const.MAIN_CHANNEL)
            for msg in failed_msg:
                await channel.send(f'{msg}')
            open('failed_msg.txt', 'w').close()

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in on_ready(): {err}')
        handleError(err)


@client.event
async def on_command_error(ctx, error):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            if isinstance(error, commands.CommandNotFound):
                await ctx.send(
                    'Klee does not know this command... ヾ(⌒(_´･ㅅ･`)_ ')
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(
                    'Klee thinks you are missing one or more arguments... ヾ(⌒(_´･ㅅ･`)_ ')

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in on_command_error(): {err}')
        handleError(err)


#listens to @ultra role mention
@client.listen('on_message')
async def message(message):
    try:
        if message.channel.id in const.BOT_CHANNELS:  #make sure the @ is from the right channel
            log(f'[chat] {message.author.display_name}: {message.content}')
            if message.author == client.user:  #make sure is not responding to message from the bot
                return

            #@ultra or @altra
            if is_any_word_in_string(const.PING_MENTIONS, message.content):

                member_id = members.UNKNOWN

                # Accepts message in the form '@ultra user', or 'user @ultra'; where 'user' can also be in the form of 'me', or @mention
                words = message.content.split()
                if len(words) > 1:
                    name_part = words[1] if is_any_word_in_string(const.PING_MENTIONS, words[0]) else words[0]
                    member_id = members.id_search(message, name_part)

                reply_msg = ''
                if member_id == members.UNKNOWN:
                    reply_msg = 'Uh, Klee does not know this name, and therefore cannot add this slime to anyone...'
                else:
                    try:
                        helpers.add_slime(member_id, 1)
                        reply_msg = f'Woah! It is a slime!  (ﾉ>ω<)ﾉ  Klee has counted {AGE_members[member_id]} slimes for {members.get_name(member_id)}!'
                    except KeyError:
                        reply_msg = f'Klee has added the slime on {utcTimestamp()}.  ( ๑>ᴗ<๑ )  Please private message maple to have this member added.'

                try:
                    await message.channel.send(reply_msg)
                except discord.errors.HTTPException:
                    with open(f"failed_msg.txt", "a") as f:
                        f.write(f"{reply_msg}\n")
                    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
                    os.system('kill 1')
                    os.system("python restarter.py")

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in message(): {err}')
        handleError(err)



######################################################
# BOT COMMANDS #
######################################################

#method name doubleping, simply wrapper for minus_slime
@client.command()
async def doubleping(ctx, *, username):
  await commands.doubleping(ctx, *username)

#returns who are in first, second and third in slime spawns for the current season
@client.command(aliases=['top_three', 'rank'])
async def slimerank(ctx):
  await commands.slimerank(ctx)

#use to check number of slime counts for self
@client.command(aliases=['sself', 'me'])
async def slimeinfo(ctx):
    await commands.slimeinfo(ctx)

#use to get the approximate number of slimes summoned in the past 24 hours
#not working correctly
@client.command(aliases=['daily'])
async def slimedaily(ctx):
    await commands.slimedaily(ctx)

#wrapper for add_slime method
@client.command(aliases=['add', 'sadd'])
async def slimeadd(ctx, number, *, username):
    await commands.slimeadd(ctx, number, *username)

"""
ex.) !slimeadd 5 john doe
number parameter will be "5" and the *username parameter 
will be a tuple containing the strings "john" and "doe"
"""
#for the specified member, add 1 zoom and store the time this zoom was reported
@client.command()
async def zoom(ctx, *, member):
    await commands.zoom(ctx, *member)

#for the specified member, send the number of times the player has zoomed along w/ the timelog of zooms
@client.command()
async def zoominfo(ctx, member='me'):
    await commands.zoominfo(ctx, member)

#to increment or decrement the number of times the member has zoomed, and change the timelog of zooms accordingly
@client.command(aliases=['zadd'])
async def zoomadd(ctx, number, *, username):
    await commands.zoomadd(ctx, number, *username)

@client.command(aliases=['zooms'])
async def zoomseason(ctx):
    await commands.zoomseason(ctx)

#method for sending no-talking gif
@client.command()
async def gif(ctx):
    await commands.gif(ctx)

#only allow Maple, Gun, Var, Traf to reset data (by setting slime counts to 0)
@client.command()
@commands.check(is_slime_admin)
async def clear(ctx):
    await commands.clear(ctx)

#command to restart bot to try to reclaim new IP. WIP, not working yet.
@client.command()
async def restart(ctx):
    await commands.restart(ctx)

#test bot response
@client.command()
@commands.check(in_slime_channel)
async def ping(ctx):
    await commands.ping(ctx)

@client.command()
@commands.check(in_slime_channel)
async def test(ctx):
    await commands.test(ctx)

#the function is limited to be used in slime related channels only
#and whereever the command is requested, the message is send back
#to that specific channel only
@client.command()
@commands.check(in_slime_channel)
async def total(ctx):
  await commands.total(ctx)

    
######################################################
# TASKS #
######################################################

#for a time loop, sends out the dictionary representing the replit db with names and slime counts
@tasks.loop(hours=12)
async def called_once_every12hour():
    try:
        daily_slime_result_channel = client.get_channel(const.REPORT_CHANNEL)

        zoom_sum, zoom_message = total_zoom()
        slime_sum, slime_message = helpers.list_member_slime_count()
        timestamp = datetime.now(timezone.utc)

        await daily_slime_result_channel.send(
            f'-------\nUTC time: {timestamp}, \nSeasonal Slime Count: {slime_sum}, and Seasonal Slime Record: {slime_message}, \n\nSeasonal Zoom Count: {zoom_sum}, and Seasonal Zoom Record: {zoom_message}\n-------'
        )

        helpers.read_txt()
        if len(failed_msg) != 0:
            channel = client.get_channel(const.MAIN_CHANNEL)
            for msg in failed_msg:
                await channel.send(f'{msg}')
            open('failed_msg.txt', 'w').close()

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in called_once_every12hour(): {err}')
        raise err


@called_once_every12hour.before_loop
async def before():
    try:
        await client.wait_until_ready()
        #print('Finished waiting')

    except Exception as err:
        print(
            f'{utcTimestamp()} ERROR in called_once_every12hour.before_loop(): {err}'
        )
        raise err


# INIT PART 2 #

log('Bot is starting up...')

# Scheduled task for #daily-slime-results
called_once_every12hour.start()

# Run simple web server to be called by uptime-robot. See: keep_alive.py
keep_alive()

# Initialize discord bot
try:
    client.run(os.getenv('TOKEN'))
except Exception as err:
    print(f'{utcTimestamp()} ERROR on client.run(): {err}')
    print(f'{utcTimestamp()} ERROR initializing discord bot.')
    handleError(err)
    if isinstance(err, discord.errors.HTTPException):
        log('FATAL - BLOCKED BY RATE LIMITS, RESTARTING NOW...')
        print(
            f'{utcTimestamp()} FATAL - BLOCKED BY RATE LIMITS, RESTARTING NOW...'
        )
        os.system('kill 1')
        os.system("python restarter.py")

# END #
