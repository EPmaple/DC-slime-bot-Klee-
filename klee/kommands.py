from . import const, members, helpers
from .helpers import is_any_word_in_string, utcTimestamp
from .logging import log, handleError
from .stats import AGE_members, zoom_member, zoom_time

from datetime import datetime, timedelta
from replit import db
import discord

#########################################################################
async def slimerank(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:

      #dict is made up of pairs of id:count
      dictionary = {}
      for member_id in AGE_members:
        dictionary[member_id] = AGE_members[member_id]['slimes']
        
# Sort the dictionary by values in descending order
      sorted_dict = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)

# Get the ids for the top three values
      first = []
      second = []
      third = []
      topValues = 0
      recordValue = max(count for (id, count) in sorted_dict)

      for (id, count) in sorted_dict:
          if topValues == 0:
              if recordValue != count:
                  topValues += 1
                  recordValue = count
                  second += [id]
              else:
                  first += [id]
          elif topValues == 1:
              if recordValue != count:
                  topValues += 1
                  recordValue = count
                  third += [id]
              else:
                  second += [id]
          elif topValues == 2:
              if recordValue != count:
                  topValues += 1
                  recordValue = count
                  break
              else:
                  third += [id]

      first_name = []
      for x in first:
        first_name += [members.get_name(x)]

      second_name = []
      for y in second:
        second_name += [members.get_name(y)]

      third_name = []
      for z in third:
        third_name += [members.get_name(z)]

      await ctx.send(f'The current first is {first_name} with {AGE_members[x]["slimes"]} slimes! Second is {second_name} with {AGE_members[y]["slimes"]} slimes, and third is {third_name} with {AGE_members[z]["slimes"]} slimes! They are the best! ⁽⁽٩(๑˃̶͈̀ ᗨ ˂̶͈́)۶⁾⁾')
      
  except Exception as err:
    log(f'ERROR in slimerank(): {err}')
    handleError(err)

#########################################################################

async def doubleping(ctx, username):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            log(f'[add] {ctx.message.author.display_name}: {-1} {username}')
            member = username.strip()
            member_id = members.id_search(ctx.message, member)

            if member_id == members.UNKNOWN:
                await ctx.send(
                    'Uh, Klee does not know this name, and therefore cannot subtract this slime from anyone... (๑•̆ ૩•̆)'
                )
                return

            original = AGE_members[member_id]['slimes']
            helpers.add_slime(member_id, -1)
            reply_msg = f'The number of slimes {members.get_name(member_id)} has summoned has been subtracted by Klee (๑‵●‿●‵๑), going from {original} to {AGE_members[member_id]["slimes"]}'
            
            await ctx.send(reply_msg)

    except Exception as err:
        log(f'ERROR in doubleping(): {err}')
        handleError(err)

#########################################################################

async def seasoninfo(ctx):
  try: 
    if ctx.channel.id in const.BOT_CHANNELS:
      self_member_id = str(ctx.author.id)
      slime_msg = f'{AGE_members[self_member_id]["slimes"]} slimes'
      """
      if AGE_members[self_member_id]["zooms"] == 0:
        zoom_msg = f'zoomed {AGE_members[self_member_id]["zooms"]} time/s'
      else:
        zoom_msg = f'zoomed {AGE_members[self_member_id]["zooms"]} time/s at the following time: {list(AGE_members[self_member_id]["zoomtime"])}'
"""
      await ctx.send(f'Klee\'s best friend, Dodoco knows you have summoned {slime_msg}.')

  except Exception as err:
    log(f'ERROR in sself(): {err}')
    handleError(err)

#########################################################################

async def slimedaily(ctx):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            current = datetime.utcnow()

            hour_ago = timedelta(hours=24)

            hour = current - hour_ago

            counter = 0

            async for message in ctx.channel.history(limit=300,
                                                     after=hour,
                                                     before=current):
                if is_any_word_in_string(const.PING_MENTIONS, message.content):
                    counter += 1
            await ctx.send(
                f'Klee has counted hand by hand, in the past 24 hours, we have summoned {counter} slimes! ٩(๑❛ᴗ❛๑)۶ '
            )
    except Exception as err:
        log(f'ERROR in daily(): {err}')
        handleError(err)

#########################################################################

async def slimeadd(ctx, number, username):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            log(f'[add] {ctx.message.author.display_name}: {number} {username}'
                )
            member = username.strip()
            member_id = members.id_search(ctx.message, member)

            if member_id == members.UNKNOWN:
                await ctx.send(
                    'Uh, Klee does not know this name, and therefore cannot add this slime from anyone... (๑•̆ ૩•̆)'
                )
                return

            original = AGE_members[member_id]['slimes']
            helpers.add_slime(member_id, number)

            reply_msg = f'The number of slimes {members.get_name(member_id)} has summoned has been added by Klee (⋆˘ᗜ˘⋆✿), going from {original} to {AGE_members[member_id]["slimes"]}'

            await ctx.send(reply_msg)

    except Exception as err:
        log(f'ERROR in add(): {err}')
        handleError(err)

#########################################################################

async def zoom(ctx, member):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            member_id = members.id_search(ctx.message, member)
            reply_msg = helpers.add_zoom(member_id, 1)
            await ctx.send(reply_msg)

    except Exception as err:
        log(f'ERROR in zoom(): {err}')
        handleError(err)

#########################################################################
async def zoominfo(ctx, member='me'):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      member_id = members.id_search(ctx.message, member)

      if member == 'me' or member_id == str(ctx.author.id):
        pronoun = 'you have'
      else:
        pronoun = members.get_name(member_id) + ' has'

      if zoom_member[member_id] == 0:
        replymsg = f'Klee knows {pronoun} not zoomed yet this season! Keep it up ヾ(๑ㆁᗜㆁ๑)ﾉ”'
        await ctx.send(replymsg)
      else:
        replymsg = f'Klee has written down with my crayolas that {pronoun} zoomed {zoom_member[member_id]} times this season, and at the following times:\n'
        for i in zoom_time[member_id]:
          replymsg += f'{i} \n'
        replymsg += 'щ(゜ロ゜щ) Wahh! Why you zoomed!'
        await ctx.send(replymsg)

  except KeyError:
    await ctx.send('Klee knows you have not zoomed yet this season! Keep it up ヾ(๑ㆁᗜㆁ๑)ﾉ”')
    
  except Exception as err:
    log(f'ERROR in zoominfo(): {err}')
    handleError(err)

#########################################################################

async def zoomadd(ctx, number, username):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            member = username.strip()
            member_id = members.id_search(ctx.message, member)
            reply_msg = helpers.add_zoom(member_id, int(number))
            await ctx.send(reply_msg)

    except Exception as err:
        log(f'ERROR in zoomadd(): {err}')
        handleError(err)

#########################################################################

async def zoomseason(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      zoom_sum, zoom_message = helpers.total_zoom()
      await ctx.send(f'Seasonal zoom count: {zoom_sum}.\n\nMember zoom counts: {zoom_message}')
      
  except Exception as err:
    log(f'ERROR in zoomseason(): {err}')
    handleError(err)

#########################################################################

async def gif(ctx):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            embed = discord.Embed(title='Channel not for talking',
                                  color=discord.Colour.blue())
            embed.set_image(
                url='https://c.tenor.com/EwX63Uf2_x0AAAAC/sml-jackie-chu.gif')
            await ctx.send(embed=embed)

    except Exception as err:
        log(f'ERROR in gif(): {err}')
        handleError(err)

#########################################################################

async def clear(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      #clear slime counts
      for member_id in AGE_members:
        db[member_id]['slimes'] = 0
        AGE_members[member_id]['slimes'] = 0

      #clear zoom counts
      for member_id in zoom_member:
        db[member_id]['zooms'] = 0
        AGE_members[member_id]['zooms'] = 0

      #clear zoom times
      for member_id in zoom_time:
        db[member_id]['zoomtime'] = []
        AGE_members[member_id]['zoomtime'] = []

      await ctx.send('All slime related records cleared (❁๑ᵒ◡ᵒ๑)')
  except Exception as err:
    log(f'ERROR in clear(): {err}')
    handleError(err)

#########################################################################

async def restart(ctx):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            log(f'INFO restart() is initiated...?')
            await ctx.send(
                'command accepted, but Klee does not know what to do with this command... ヾ(⌒(_´･ㅅ･`)_ '
            )

    except Exception as err:
        log(f'ERROR in restart(): {err}')
        handleError(err)

#########################################################################

async def ping(ctx):
    try:
        await ctx.send('pong!')
    except Exception as err:
        log(f'ERROR in ping(): {err}')
        handleError(err)

#########################################################################

async def slimeseason(ctx):
  try:
    #slime_sum refers to the current total number of slimes summoned
    #slime_message consists of a dictionary having pairs of string:int, 
    #string is the player's name 
    #int is the number of slimes the corresponding player has summoned and recorded
    slime_sum, slime_message = helpers.list_member_slime_count()
    await ctx.send(f'Seasonal Slime Count: {slime_sum}, and Seasonal Slime Record: {slime_message}')
    
  except Exception as err:
    log(f'ERROR in total(): {err}')
    raise err
    
"""
AGE_members = {}
for member_id in members.id_list():
  AGE_members[member_id] = {}
  AGE_members[member_id]['slimes'] = 0
  AGE_members[member_id]['zooms'] = 0
  AGE_members[member_id]['zoomtime'] = []

for member_id in db:
    if member_id.endswith('z'):
      if member_id[:-1] in AGE_members:
        zooms = db[member_id]
        AGE_members[member_id[:-1]]['zooms'] = zooms
    elif member_id.endswith('zt'):
      if member_id[:-2] in AGE_members:
        zoom_time = db[member_id]
        AGE_members[member_id[:-2]]['zoomtime'] = list(zoom_time)
    elif member_id[-1].isdigit():
      if member_id in AGE_members:
        slimes = db[member_id]
        AGE_members[member_id]['slimes'] = slimes

for member_id in AGE_members:
  db[member_id] = {}
  db[member_id]['slimes'] = AGE_members[member_id]['slimes']
  db[member_id]['zooms'] = AGE_members[member_id]['zooms']
  db[member_id]['zoomtime'] = AGE_members[member_id]['zoomtime']
  """