from klee import const, members

import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta
from replit import db
from keep_alive import keep_alive
import nest_asyncio
import requests
import traceback

# INIT PART 1 #

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
member_count = db.keys() #member_count is a dictionary containing all ids (string) of the members
for member_id in AGE_members:
    for db_member_id in member_count:
        if member_id == db_member_id: #if both ids match
            AGE_members[member_id] = db[db_member_id] #AGE_members is now a dictionary with keys(ids) to values(slimes counts)
        elif member_id not in member_count:
            db[member_id] = 0


          
#zoom_dictionaries INIT construction
zoom_member = {} # key=member_id, value=# of times zoomed
zoom_time = {} # key=member_id, value=specific time for when the player zoomed

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

#reads the failed_msg.txt and stores it in a list called failed_msg
def read_txt():
#opens the txt, which stores msg that failed to be send, and stores each line of the txt into the list created above
  with open("failed_msg.txt") as f:
    for line in f:
      failed_msg.append(line.strip())
#txt is automatically closed by 'with open'

#helper method, takes in member id and the number of slimes want to be added
#can use negative numbers to subtract slimes
def add_slime(member_id, number):
    if member_id in db:  #if member id already in replit database,
        db[member_id] += int(number)
        AGE_members[member_id] += int(number)
    else:  #if member id was not in replit database
        db[member_id] = int(number)
        AGE_members[member_id] = int(number)


#helper method, knowing this member id is already in db, subtract one slime count
def minus_slime(member_id):
    db[member_id] -= 1
    AGE_members[member_id] -= 1


#helper method, in case there are multiple greatest key-value pairs with the same value
def multiple_max(dictionary):
    max_key = max(dictionary, key=dictionary.get)
    first = [max_key]

    for x in dictionary:
        if x != max_key:
            if dictionary[x] == dictionary[max_key]:
                first += [x]
    return first


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
    logTimestamp = log(f'ERROR TRACE:\n{traceback.format_exc()}# TRACE END\n')
    sendWebhook(f'Klee encountered an error :( Please check {logfile} at {logTimestamp} -> {type(e).__name__}.')
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in handleError(): {err}')


#helper to call discord webhook API
def sendWebhook(msg):
    webhookUrl = 'https://discord.com/api/webhooks/' + os.getenv('WEBHOOK_ID_TOKEN')
    r = requests.post(webhookUrl, data = {'content': msg})
    print(f'{utcTimestamp()} DEBUG Webhook response code: {r.status_code}')
    r.raise_for_status() #raise error if response status_code is 4XX or 5XX


# BOT EVENTS #

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
            await ctx.send('Klee does not know this command... ヾ(⌒(_´･ㅅ･`)_ ')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Klee thinks you are missing one or more arguments... ヾ(⌒(_´･ㅅ･`)_ ')

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

            member_id = 0

            #if the message is '@ultra @user'
            if len(message.raw_mentions) != 0:
                member_id = str(message.raw_mentions[0])

            #if the message is '@ultra me', or '@ultra user'
            else:
                words = message.content.split()
                if len(words) > 1:
                    second_word = words[1]
                    member_id = members.id_search(message, second_word)

            reply_msg = ''
            if member_id == 0:
                reply_msg = 'Uh, Klee does not know this name, and therefore cannot add this slime to anyone...'
            else:
                try:
                    add_slime(member_id, 1)
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


# BOT COMMANDS #

#method name doubleping, simply wrapper for minus_slime
@client.command()
async def doubleping(ctx, *, username):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      log(f'[add] {ctx.message.author.display_name}: {-1} {username}')
      member = username.strip()
      member_id = members.id_search(ctx, member)

      if member_id == 0:
        await ctx.send('Uh, Klee does not know this name, and therefore cannot subtract this slime from anyone... (๑•̆ ૩•̆)')
        return

      original = AGE_members[member_id]
      add_slime(member_id, -1)
      reply_msg = f'The number of slimes {members.get_name(member_id)} has summoned has been subtracted by Klee (๑‵●‿●‵๑), going from {original} to {AGE_members[member_id]}'

      try: 
        await ctx.send(reply_msg)
          
      except discord.errors.HTTPException:
        with open(f"failed_msg.txt", "a") as f:
          f.write(f"{reply_msg}\n")
        print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
        os.system('kill 1')
        os.system("python restarter.py")


  except Exception as err:
    print(f'{utcTimestamp()} ERROR in doubleping(): {err}')
    handleError(err)



#returns who are in first, second and third in slime spawns for the current season
@client.command(aliases=['top_three','rank'])
async def slimerank(ctx):  
  try:
    if ctx.channel.id in const.BOT_CHANNELS:

        dictionary = {}
        for member_id in AGE_members:
            dictionary[member_id] = AGE_members[member_id]

        copy = dict(dictionary)

        first = multiple_max(copy)

        copy1 = dict(dictionary)
        for x in copy1:
            for y in first:
                if x == y:
                    del copy[x]

        second = multiple_max(copy)

        copy2 = dict(copy1)
        for x in copy2:
            for y in second:
                if x == y:
                    del copy[x]

        third = multiple_max(copy)

        first_name = []
        for x in first:
            first_name += [members.get_name(x)]

        second_name = []
        for y in second:
            second_name += [members.get_name(y)]

        third_name = []
        for z in third:
            third_name += [members.get_name(z)]

        await ctx.send(
            f'The current first is {first_name} with {AGE_members[x]} slimes! Second is {second_name} with {AGE_members[y]} slimes, and third is {third_name} with {AGE_members[z]} slimes! They are the best! ⁽⁽٩(๑˃̶͈̀ ᗨ ˂̶͈́)۶⁾⁾'
        )

  except Exception as err:
    print(f'{utcTimestamp()} ERROR in first(): {err}')
    handleError(err)


#helper method
def list_member_slime_count():
    slime_sum = sum(AGE_members.values())
    slime_message = {}
    for member_id in members.id_list():
        # set name:slime_count to message dict
        slime_message[members.get_name(member_id)] = AGE_members[member_id]
    return (slime_sum, slime_message)


#use to check number of slime counts for self
@client.command(aliases=['sself','me'])
async def slimeinfo(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
        self_member_id = str(ctx.author.id)
        await ctx.send(
            f'Klee knows that you have summoned {AGE_members[self_member_id]} slimes so far this season! You are the best!'
        )

  except Exception as err:
    print(f'{utcTimestamp()} ERROR in sself(): {err}')
    handleError(err)


#use to get the approximate number of slimes summoned in the past 24 hours
#not working correctly
@client.command(aliases=['daily'])
async def slimedaily(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
        current = datetime.utcnow()

        hour_ago = timedelta(hours=24)

        hour = current - hour_ago

        counter = 0

        async for message in ctx.channel.history(limit=300, after=hour, before=current):
            if is_any_word_in_string(const.PING_MENTIONS, message.content):
                counter += 1
        await ctx.send(f'Klee has counted hand by hand, in the past 24 hours, we have summoned {counter} slimes! ٩(๑❛ᴗ❛๑)۶ ')
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in daily(): {err}')
    handleError(err)


#wrapper for add_slime method
@client.command(aliases=['add','sadd'])
async def slimeadd(ctx, number, *, username):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      log(f'[add] {ctx.message.author.display_name}: {number} {username}')
      member = username.strip()
      member_id = members.id_search(ctx, member)

      if member_id == 0:
        await ctx.send('Uh, Klee does not know this name, and therefore cannot add this slime from anyone... (๑•̆ ૩•̆)')
        return

      original = AGE_members[member_id]
      add_slime(member_id, number)

      reply_msg = f'The number of slimes {members.get_name(member_id)} has summoned has been added by Klee (⋆˘ᗜ˘⋆✿), going from {original} to {AGE_members[member_id]}'

      try:
        await ctx.send(reply_msg)
          
      except discord.errors.HTTPException:
        with open(f"failed_msg.txt", "a") as f:
          f.write(f"{reply_msg}\n")
        print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
        os.system('kill 1')
        os.system("python restarter.py")

  except Exception as err:
    print(f'{utcTimestamp()} ERROR in add(): {err}')
    handleError(err)


#for the specified member, add 1 zoom and store the time this zoom was reported
@client.command()
async def zoom(ctx, *, member):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      member_id = str(members.id_search(ctx, member))

      if member_id == 0:
        await ctx.send ('Uh, Klee does not know this name, and therefore cannot subtract this slime from anyone...')

      #member_id has been gotten, added z at the end to distinguish from normal key values use for slime counting
      member_idz = member_id + 'z'
      #if member has zoomed before
      if member_idz in zoom_member:
        db[member_idz] += 1
        zoom_member[member_idz] += 1

        member_idzt = member_idz + 't'
        #append to the specific key's value array the time of which the zoom was reported
        db[member_idzt] += [f'{utcTimestamp()}']
        zoom_time[member_idzt] += [f'{utcTimestamp()}']
      else:
        #user has not zoomed before
        db[member_idz] = 1
        zoom_member[member_idz] = 1

        member_idzt = member_idz + 't'
        #append to the specific key's value array the time of which the zoom was reported
        db[member_idzt] = [f'{utcTimestamp()}']
        zoom_time[member_idzt] = [f'{utcTimestamp()}']

      replymsg = f'Klee has noticed {members.get_name(member_id)} zoomed a slime at {utcTimestamp()}! (◕︿◕✿) Zooming is bad. Please do not zoom again'
      await ctx.send(replymsg)

  except Exception as err:
    print(f'{utcTimestamp()} ERROR in message(): {err}')
    handleError(err)

    
#for the specified member, send the number of times the player has zoomed along w/ the timelog of zooms
@client.command()
async def zoominfo(ctx, member = 'me'):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      member_id = str(members.id_search(ctx, member))
      member_idz = member_id +'z'
      member_idzt = member_id +'zt'

      if zoom_member[member_idz] == 0:
        replymsg = 'Klee knows you have not zoomed yet this season! Keep it up ヾ(๑ㆁᗜㆁ๑)ﾉ”'
        await ctx.send(replymsg)
      #after checking that the member has zoomed
      else:
        replymsg = f'Klee has written down with my crayolas that {members.get_name(member_id)} has zoomed {zoom_member[member_idz]} times this season, and at the following times:\n'
        for i in zoom_time[member_idzt]:
          replymsg += f'{i} \n'
        replymsg += 'щ(゜ロ゜щ) Wahh! Why you zoomed!'
        await ctx.send(replymsg)

  except KeyError:
    await ctx.send('Klee knows you have not zoomed yet this season! Keep it up ヾ(๑ㆁᗜㆁ๑)ﾉ”')
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in message(): {err}')
    handleError(err)


    
#to increment or decrement the number of times the member has zoomed, and change the timelog of zooms accordingly    
@client.command(aliases=['zadd'])
async def zoomadd(ctx, number, *, username):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      member = username.strip() 
      member_id = members.id_search(ctx, member)

      if member_id == 0:
        await ctx.send('Uh, Klee does not know this name, and therefore cannot add this slime from anyone... (๑•̆ ૩•̆)')
        return

      member_idz = member_id + 'z'
      member_idzt = member_idz + 't'
      original = zoom_member[member_idz]

      #to decrement number of times zoomed
      if int(number) < 0:
        # clamp to 0 if subtracting more than the actual current count
        new_count = max(0, zoom_member[member_idz] + int(number))
        zoom_member[member_idz] = new_count
        db[member_idz] = new_count
        #first-in, last-out; deleting the last zoom info
        while len(zoom_time) > zoom_member[member_idz]:
          del zoom_time[member_idzt][-1]
          del db[member_idzt][-1]
      #to increment number of times zoomed
      else:
        zoom_member[member_idz] += int(number)
        db[member_idz] += int(number)
        #using the current time to add onto the timelog of zooms
        for i in range(int(number)):
          db[member_idzt] += [f'{utcTimestamp()}']
          zoom_time[member_idzt] += [f'{utcTimestamp()}']

      reply_msg = f'The number of times {members.get_name(member_id)} zoomed has been changed from {original} to {zoom_member[member_idz]} (っ＾▿＾)っ'

      await ctx.send(reply_msg)

  except Exception as err:
    print(f'{utcTimestamp()} ERROR in add(): {err}')
    handleError(err)
    
    
    
#helper function
#return zoom_sum [int], total # of zoom
#       zoom_message [dict], list the top zoomers along with their corresponding # of zooms
def total_zoom():
  zoom_sum = sum(zoom_member.values())

  #to get the top zoomer(s)
  top_zoom_ids = multiple_max(zoom_member)

  #to get second highest zoomer(s)
  copy = dict(zoom_member)
  for x in zoom_member:
    for y in top_zoom_ids:
      if x == y:
        del copy[x]
  top_zoom_ids += multiple_max(copy)

  #to get third highest zoomer(s)
  copy1 = dict(zoom_member)
  for x in zoom_member:
    for y in top_zoom_ids:
      if x == y:
        del copy1[x]
  top_zoom_ids += multiple_max(copy1)

  zoom_message = {}
  #for the zoomer_id's we got from above, iterate through them to produce a dict of [zoomer_name: # of times zoomed] (key:value)
  for member_idz in top_zoom_ids:
    member_id = member_idz[0:-1]
    zoom_message[members.get_name(member_id)] = zoom_member[member_idz]
  
  return (zoom_sum, zoom_message)

  
#method for sending no-talking gif
@client.command()
async def gif(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
        embed = discord.Embed(title='Channel not for talking',
                              color=discord.Colour.blue())
        embed.set_image(
            url='https://c.tenor.com/EwX63Uf2_x0AAAAC/sml-jackie-chu.gif')
        await ctx.send(embed=embed)

  except Exception as err:
    print(f'{utcTimestamp()} ERROR in gif(): {err}')
    handleError(err)


#only allows me and gunther to clear slime records (by setting slime counts to 0)
@client.command()
@commands.check(is_slime_admin)
async def clear(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:

      for member_id in AGE_members:
        #clear slime counts
        db[member_id] = 0
        AGE_members[member_id] = 0

      for member_id in zoom_member:
        #clear zoom counts
        db[member_id] = 0
        zoom_member[member_id] = 0

      for member_id in zoom_time:
        #clear zoom times
        db[member_id] = []
        zoom_time[member_id] = []
          
      await ctx.send('All slime related records cleared (❁๑ᵒ◡ᵒ๑)')

  except Exception as err:
    print(f'{utcTimestamp()} ERROR in clear(): {err}')
    handleError(err)


#command to restart bot to try to reclaim new IP. WIP, not working yet.
@client.command()
async def restart(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
        print(f'{utcTimestamp()} INFO restart() is initiated...?')
        await ctx.send('command accepted, but Klee does not know what to do with this command... ヾ(⌒(_´･ㅅ･`)_ ')

  except Exception as err:
    print(f'{utcTimestamp()} ERROR in restart(): {err}')
    handleError(err)


#test bot response
@client.command()
@commands.check(in_slime_channel)
async def ping(ctx):
  try:
    await ctx.send('pong!')
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in ping(): {err}')
    handleError(err)

@client.command()
@commands.check(in_slime_channel)
async def test(ctx):
  try:
    #if msg_id is not None:
    #    print(f'{utcTimestamp()} DEBUG msg_id is not None')
    #    print(f'{utcTimestamp()} DEBUG msg_id = {msg_id}')
    #    partialMsg = ctx.channel.get_partial_message(msg_id)
    #else:
    #print(f'{utcTimestamp()} DEBUG msg_id is None')
    print(f'{utcTimestamp()} DEBUG ctx.id = {ctx.message.id}')
    msgId = ctx.message.id
    print(f'{utcTimestamp()} DEBUG ctx.channel.id = {ctx.channel.id}')
    channelId = ctx.channel.id
    channelObj = client.get_channel(channelId)
    print(f'{utcTimestamp()} DEBUG channelObj = {channelObj}')
    partialMsg = channelObj.get_partial_message(msgId)
    print(f'{utcTimestamp()} DEBUG partialMsg = {partialMsg}')
    await ctx.send('ok', reference = partialMsg)
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in test(): {err}')
    handleError(err)


# TASKS #

#for a time loop, sends out the dictionary representing the replit db with names and slime counts
@tasks.loop(hours=12)
async def called_once_every12hour():
  try:
    daily_slime_result_channel = client.get_channel(const.REPORT_CHANNEL)

    zoom_sum, zoom_message = total_zoom()
    slime_sum, slime_message = list_member_slime_count()
    timestamp = datetime.now(timezone.utc)
    
    await daily_slime_result_channel.send(f'-------\nUTC time: {timestamp}, \nSeasonal Slime Count: {slime_sum}, and Seasonal Slime Record: {slime_message}, \n\nSeasonal Zoom Count: {zoom_sum}, and Seasonal Top Zoomers:{zoom_message}\n-------')

    read_txt()
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
    print(f'{utcTimestamp()} ERROR in called_once_every12hour.before_loop(): {err}')
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
        print(f'{utcTimestamp()} FATAL - BLOCKED BY RATE LIMITS, RESTARTING NOW...')
        os.system('kill 1')
        os.system("python restarter.py")


# END #