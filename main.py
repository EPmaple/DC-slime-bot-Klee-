from klee import const, members, kommands, helpers
from klee.helpers import is_any_word_in_string, utcTimestamp, checkHistory
from klee.logging import log, handleError
from klee.stats import AGE_members
from keep_alive import keep_alive

from datetime import datetime, timezone
from discord.ext import commands, tasks
from replit import db, database
import discord
import nest_asyncio
import os

######################################################
# INIT PART 1 #
######################################################

nest_asyncio.apply()

client = commands.Bot(command_prefix='!')

# HELPER METHODS #

#check whether the author's id is the same as the specified user's id
def is_bot_admin(ctx):
    return ctx.author.id in const.BOT_ADMINS

def is_slime_admin(ctx):
    return ctx.author.id in const.DATA_ADMINS

#check whether it's in the specified channel
def in_slime_channel(ctx):
    return ctx.channel.id in const.BOT_CHANNELS


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
        log('INFO Bot is ready.')
        await checkHistory(client)

        failed_msg = helpers.read_txt()
        #if the failed_msg text is not empty, sends the msg to the corresponding channel, and then erase the txt file
        if len(failed_msg) != 0:
            channel = client.get_channel(const.MAIN_CHANNEL)
            for msg in failed_msg:
                await channel.send(f'{msg}')
            open('failed_msg.txt', 'w').close()

    except Exception as err:
        log(f'{utcTimestamp()} ERROR in on_ready(): {err}')
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
        log(f'{utcTimestamp()} ERROR in on_command_error(): {err}')
        handleError(err)


#listens to @ultra role mention
@client.listen('on_message')
async def message(message):
    try:
        if message.channel.id in const.BOT_CHANNELS:  #make sure the @ is from the right channel
            db["timeOfLastMessage"] = str(message.created_at)
            log(f'[chat] {message.author.display_name}: {message.content}')
            if message.author == client.user:  #make sure is not responding to message from the bot
                return
            
            # '.u' or '.u user'
            if message.content == '.u' or message.content.startswith('.u '):

                words = message.content.split(' ', 1)  #split into two words max
                username = 'me' if len(words) == 1 else words[1]
                await kommands.slime_ping(message, username)

            # @ultra or @altra
            elif is_any_word_in_string(const.PING_MENTIONS, message.content):

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
                        reply_msg = f'Woah! It is a slime!  (ﾉ>ω<)ﾉ  Klee has counted {AGE_members[member_id]["slimes"]} slimes for {members.get_name(member_id)}!'
                    except KeyError:
                        reply_msg = f'Klee has added the slime on {utcTimestamp()}.  ( ๑>ᴗ<๑ )  Please private message maple to have this member added.'

                await message.reply(reply_msg, mention_author=False)

    except Exception as err:
        log(f'ERROR in message(): {err}')
        handleError(err)


######################################################
# BOT COMMANDS #
######################################################

#test function for banning by per-member denies
@client.command()
async def ban(ctx, username):
  await kommands.ban(ctx, username, client)

@client.command()
async def unban(ctx, username):
  await kommands.unban(ctx, username, client)

#method name doubleping, simply wrapper for minus_slime
@client.command()
async def doubleping(ctx, username):
  await kommands.doubleping(ctx, username)

#returns who are in first, second and third in slime spawns for the current season
@client.command(aliases=['top_three', 'rank', 'srank'])
async def slimerank(ctx):
  await kommands.slimerank(ctx)

#use to check number of slime counts for self
@client.command(aliases=['sself', 'me', 'sinfo'])
async def seasoninfo(ctx):
    await kommands.seasoninfo(ctx)

#use to get the approximate number of slimes summoned in the past 24 hours
#not working correctly
@client.command(aliases=['daily', 'sdaily'])
async def slimedaily(ctx):
    await kommands.slimedaily(ctx)

#wrapper for add_slime method
@client.command(aliases=['add', 'sadd'])
async def slimeadd(ctx, number, username):
    await kommands.slimeadd(ctx, number, username)

"""
ex.) !slimeadd 5 john doe
number parameter will be "5" and the *username parameter 
will be a tuple containing the strings "john" and "doe"
"""

@client.command(aliases=['u'])
async def ultra(ctx, username='me'):
  await kommands.slime_ping(ctx.message, username)

#for the specified member, add 1 zoom and store the time this zoom was reported
@client.command()
async def zoom(ctx, member='me'):
    await kommands.zoom(ctx, member)

#for the specified member, send the number of times the player has zoomed along w/ the timelog of zooms
@client.command(aliases=['zinfo'])
async def zoominfo(ctx, member='me'):
    await kommands.zoominfo(ctx, member)

#to increment or decrement the number of times the member has zoomed, and change the timelog of zooms accordingly
@client.command(aliases=['zadd'])
async def zoomadd(ctx, number, username):
    await kommands.zoomadd(ctx, number, username)

@client.command(aliases=['zooms', 'ztotal'])
async def zoomseason(ctx):
    await kommands.zoomseason(ctx)

#method for sending no-talking gif
@client.command(aliases=['silence'])
async def gif(ctx):
    await kommands.gif(ctx)

#only allow Maple, Gun, Var, Traf to reset data (by setting slime counts to 0)
@client.command()
@commands.check(is_slime_admin)
async def clear(ctx):
    await kommands.clear(ctx)

#command to restart bot to try to reclaim new IP. WIP, not working yet.
@client.command()
async def restart(ctx):
    await kommands.restart(ctx)

#test bot response
@client.command()
@commands.check(in_slime_channel)
async def ping(ctx):
    await kommands.ping(ctx)

#the function is limited to be used in slime related channels only
#and whereever the command is requested, the message is send back
#to that specific channel only
@client.command(aliases=['slimes', 'total', 'stotal'])
@commands.check(in_slime_channel)
async def slimeseason(ctx):
  await kommands.slimeseason(ctx)

######################################################
# TASKS #
######################################################

#for a time loop, sends out the dictionary representing the replit db with names and slime counts
@tasks.loop(hours=12)
async def called_once_every12hour():
    try:
        daily_slime_result_channel = client.get_channel(const.REPORT_CHANNEL)

        zoom_sum, zoom_message = helpers.total_zoom()
        slime_sum, slime_message = helpers.list_member_slime_count()
        timestamp = datetime.now(timezone.utc)

        await daily_slime_result_channel.send(
            f'-------\nUTC time: {timestamp}, \nSeasonal Slime Count: {slime_sum}, and Seasonal Slime Record: {slime_message},'
        )
        await daily_slime_result_channel.send(
            f'Seasonal Zoom Count: {zoom_sum}, and Seasonal Zoom Record: {zoom_message}\n-------'
        )

        failed_msg = helpers.read_txt()
        if len(failed_msg) != 0:
            channel = client.get_channel(const.MAIN_CHANNEL)
            for msg in failed_msg:
                await channel.send(f'{msg}')
            open('failed_msg.txt', 'w').close()

    except Exception as err:
        log(f'{utcTimestamp()} ERROR in called_once_every12hour(): {err}')
        raise err


@called_once_every12hour.before_loop
async def before():
    try:
        await client.wait_until_ready()
        #print('Finished waiting')

    except Exception as err:
        log(f'ERROR in called_once_every12hour.before_loop(): {err}'
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
    log(f'ERROR on client.run(): {err}')
    log(f'ERROR initializing discord bot.')
    handleError(err)
    if isinstance(err, discord.errors.HTTPException):
        log('FATAL - BLOCKED BY RATE LIMITS, RESTARTING NOW...')
        os.system('kill 1')
        os.system("python restarter.py")

# END #
