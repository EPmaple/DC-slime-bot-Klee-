from . import const, members, helpers
from .helpers import is_any_word_in_string, utcTimestamp, add_slime, update_timestamp
from .logging import log, handleError
from .stats import AGE_members, slime_records

from datetime import datetime, timedelta
from replit import db
import discord
import re

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
            helpers.add_slime(member_id, -1, ctx.message)
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
      await ctx.send(f'Klee\'s best friend, Dodoco ૮꒰ ˶• ༝ •˶꒱ა knows you have summoned {slime_msg}.')

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
            helpers.add_slime(member_id, number, ctx.message)

            reply_msg = f'The number of slimes {members.get_name(member_id)} has summoned has been added by Klee (⋆˘ᗜ˘⋆✿), going from {original} to {AGE_members[member_id]["slimes"]}'

            await ctx.message.reply(reply_msg, mention_author=False)
            #await ctx.send(reply_msg)

    except Exception as err:
        log(f'ERROR in add(): {err}')
        handleError(err)


#########################################################################

async def zoom(ctx, member):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      member_id = members.id_search(ctx.message, member)
      member_mention = f'<@{member_id}>' if not member_id.startswith('alt') else ''
      reply_msg = helpers.add_zoom(member_id, 1)
      reply_msg = f'{reply_msg} {member_mention}'
      is_ping_member = member_id != str(ctx.author.id)
      mentionsFlag = discord.AllowedMentions(users=is_ping_member, replied_user=False)
      await ctx.message.reply(reply_msg, allowed_mentions=mentionsFlag)

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

      if AGE_members[member_id]['zooms'] == 0:
        replymsg = f'Klee knows {pronoun} not zoomed yet this season! Keep it up ヾ(๑ㆁᗜㆁ๑)ﾉ”'
        await ctx.send(replymsg)
      else:
        replymsg = f'Klee has written down with my crayolas that {pronoun} zoomed {AGE_members[member_id]["zooms"]} times this season, and at the following times:\n'
        for i in AGE_members[member_id]["zoomtime"]:
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
      member_mention = f'<@{member_id}>' if not member_id.startswith('alt') else ''
      reply_msg = helpers.add_zoom(member_id, int(number))
      reply_msg = f'{reply_msg} {member_mention}'
      is_ping_member = member_id != str(ctx.author.id)
      mentionsFlag = discord.AllowedMentions(users=is_ping_member, replied_user=False)
      await ctx.message.reply(reply_msg, allowed_mentions=mentionsFlag)

  except Exception as err:
    log(f'ERROR in zoomadd(): {err}')
    handleError(err)

#########################################################################

async def zoomseason(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      zoom_sum, zoom_message = helpers.total_zoom()
      await ctx.send(f'Seasonal zoom count: {zoom_sum}.\nMember zoom counts: {zoom_message}')
      
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
      first_keys = {
        'slimes': 0,
        'slimelist': [],
        'zooms': 0,
        'zoomtime': []
      }
      for member_id in AGE_members:
        for key, value in first_keys.items():
          AGE_members[member_id][key] = value
          db[member_id][key] = value

      slime_records = {}
      db['slime_records'] = {}

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

#########################################################################

async def slime_ping(message_ctx, username):
  try:
    channel_id = message_ctx.channel.id
    if channel_id in const.BOT_CHANNELS:

      role_mention = f'{const.MENTION_ULTRA_ROLE}' if channel_id != const.CID_BOTTESTING_CHANNEL else f'{const.MENTION_SLIMEPINGTEST_ROLE}'
      
      member_text = username.strip()
      member_id = members.id_search(message_ctx, member_text)

      if member_id == members.UNKNOWN:
        echo_msg = f'{role_mention} {member_text}'
        klee_response = 'Uh, Klee does not know this name, and therefore cannot add this slime to anyone...'
      else:

        if re.match('^me\\b', member_text, re.IGNORECASE):
          try:
            author_name = members.get_name(member_id)
          except KeyError:
            author_name = message_ctx.author.display_name
          echo_msg = f'{role_mention} {author_name}: {member_text}'
        else:
          echo_msg = f'{role_mention} {member_text}'

        helpers.add_slime(member_id, 1, message_ctx)
        klee_response = f'Woah! It is a slime!  (ﾉ>ω<)ﾉ  Klee has counted {AGE_members[member_id]["slimes"]} slimes for {members.get_name(member_id)}!'

      reply_msg = f'{echo_msg} \n{klee_response} '
      mentionsFlag = discord.AllowedMentions(users=False, roles=True, replied_user=False)
      await message_ctx.reply(reply_msg, allowed_mentions=mentionsFlag)

  except Exception as err:
    log(f'ERROR in slime_ping(): {err}')
    handleError(err)

#########################################################################

async def update_timestamp(ctx):
  try:
    helpers.update_timestamp()
    await ctx.send("Klee has dutifully updated timestamp.py! (๑˘︶˘๑)")
  except Exception as err:
    log(f'ERROR in update_timestamp(): {err}')
    handleError(err)

#########################################################################

#outputs replymsg/ragna_data to console
async def website_data(ctx):
  try:
    channel_id = ctx.channel.id
    if channel_id in const.BOT_CHANNELS:

      slime_lists = '{\n'
      season_data = '[\n'
      id = 0
      for member_id in AGE_members:
        #if not(AGE_members[member_id]['slimes'] == 0 and AGE_members[member_id]['zooms'] == 0):
        ############## to initialize season_data ##################
        member_dict = {}
        id += 1
        member_dict['id'] = id
        member_dict['name'] = members.get_name(member_id)
        member_dict['slimes'] = AGE_members[member_id]['slimes']
        member_dict['zooms'] = AGE_members[member_id]['zooms']
        season_data += f'{member_dict},\n'
        ############## to initialize season_data ##################
      
        ############## to initialize slime_lists ##################
        #to turn ObservedList into normal list
        slime_list = list(AGE_members[member_id]['slimelist'])
        slime_lists += f'"{member_dict["name"]}": {slime_list},\n'
        ############## to initialize slime_lists ##################
      
      slime_lists += '}'
      season_data += ']'
      
      ############## to initialize slime_records ##################
      function_slime_records = '{\n'
      for key, value in slime_records.items():
        # to escape '{' and '}', do '{{' and '}}'
        function_slime_records += f'{key}: {value},\n'
      function_slime_records += '}'
      ############## to initialize slime_records ##################

      output_msg = f'season_data = {season_data}\n'
      output_msg += '\n################################################################\n################################################################\n\n'
      output_msg += f'slime_lists = {slime_lists}\n'
      output_msg += '\n################################################################\n################################################################\n\n'
      output_msg += f'slime_records = {function_slime_records}'
      
      file_path = 'info/website_data.py'
      with open(file_path, "w") as file:
        file.write(output_msg)
      
      await ctx.send('Website data successfully printed in replit console.')
      
  except Exception as err:
    log(f'ERROR in website_data(): {err}')
    handleError(err)

#########################################################################

async def ban(ctx, message_obj, username, client_obj):
  try:
    if ctx.channel.id in {const.MAIN_CHANNEL}:  #make sure ban/unban can only be executed from specific channel
      slimeping_channel = client_obj.get_channel(const.MAIN_CHANNEL)
      username = username.strip()
      member_id = members.id_search(ctx.message, username)
      if member_id == members.UNKNOWN:
        await message_obj.reply('Uh, Klee does not know this name, and therefore cannot timeout this person... (๑•̆ ૩•̆)')
        return
      member_name = members.get_name(member_id)
      # Get the member object from the member ID
      member_obj = ctx.guild.get_member(int(member_id)) or await ctx.guild.fetch_member(int(member_id))
      # Set channel permission
      log(f'Banning {ctx.guild} :: {member_name} :: {member_obj} ...')
      await message_obj.reply(f'ヽ( `д´*)ノ Klee thinks {member_name} deserves a timeout!!!')
      if ctx.channel.id != slimeping_channel.id:
        await slimeping_channel.send(f'ヽ( `д´*)ノ Klee thinks {member_name} deserved a timeout!!!')
      await slimeping_channel.set_permissions(member_obj, view_channel=False, reason='Klee-timeout-ban')
  except Exception as err:
    log(f'ERROR in ban(): {err}')
    handleError(err)


async def unban(ctx, message_obj, username, client_obj):
  try:
    if ctx.channel.id in {const.MAIN_CHANNEL}:  #make sure ban/unban can only be executed from specific channel
      slimeping_channel = client_obj.get_channel(const.MAIN_CHANNEL)
      username = username.strip()
      member_id = members.id_search(ctx.message, username)
      if member_id == members.UNKNOWN:
        await message_obj.reply('Uh, Klee does not know this name, and therefore cannot untimeout this person... (๑•̆ ૩•̆)')
        return
      member_name = members.get_name(member_id)
      # Get the member object from the member ID
      member_obj = ctx.guild.get_member(int(member_id)) or await ctx.guild.fetch_member(int(member_id))
      # Set channel permission
      log(f'Unbanning {ctx.guild} :: {member_name} :: {member_obj} ...')
      await slimeping_channel.set_permissions(member_obj, overwrite=None, reason='Klee-timeout-unban')
      await message_obj.reply(f'Klee hopes you\'re remedying your zooming ways, {member_name}!! ヾ(๑ㆁᗜㆁ๑)ﾉ”')
      if ctx.channel.id != slimeping_channel.id:
        await slimeping_channel.send(f'Klee hopes you\'re remedying your zooming ways, {member_name}!! ヾ(๑ㆁᗜㆁ๑)ﾉ”')
  except Exception as err:
    log(f'ERROR in unban: {err}')
    handleError(err)
