from . import const, members, helpers
from .helpers import is_any_word_in_string, utcTimestamp, add_slime
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
        dictionary[member_id] = AGE_members[member_id]
        
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

      await ctx.send(
                f'The current first is {first_name} with {AGE_members[x]} slimes! Second is {second_name} with {AGE_members[y]} slimes, and third is {third_name} with {AGE_members[z]} slimes! They are the best! ⁽⁽٩(๑˃̶͈̀ ᗨ ˂̶͈́)۶⁾⁾'
            )
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

            original = AGE_members[member_id]
            helpers.add_slime(member_id, -1)
            reply_msg = f'The number of slimes {members.get_name(member_id)} has summoned has been subtracted by Klee (๑‵●‿●‵๑), going from {original} to {AGE_members[member_id]}'

            
            await ctx.send(reply_msg)


    except Exception as err:
        log(f'ERROR in doubleping(): {err}')
        handleError(err)

#########################################################################

async def slimeinfo(ctx):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            self_member_id = str(ctx.author.id)
            await ctx.send(
                f'Klee knows that you have summoned {AGE_members[self_member_id]} slimes so far this season! You are the best!'
            )

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

            original = AGE_members[member_id]
            helpers.add_slime(member_id, number)

            reply_msg = f'The number of slimes {members.get_name(member_id)} has summoned has been added by Klee (⋆˘ᗜ˘⋆✿), going from {original} to {AGE_members[member_id]}'

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
            member_mention = f'<@{member_id}>'
            reply_msg = helpers.add_zoom(member_id, 1)
            reply_msg = f'{reply_msg} {member_mention}>'
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
            member_idz = member_id + 'z'
            member_idzt = member_id + 'zt'

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
        await ctx.send(
            'Klee knows you have not zoomed yet this season! Keep it up ヾ(๑ㆁᗜㆁ๑)ﾉ”'
        )
    except Exception as err:
        log(f'ERROR in zoominfo(): {err}')
        handleError(err)

#########################################################################

async def zoomadd(ctx, number, username):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            member = username.strip()
            member_id = members.id_search(ctx.message, member)
            member_mention = f'<@{member_id}>'
            reply_msg = helpers.add_zoom(member_id, int(number))
            reply_msg = f'{reply_msg} {member_mention}>'
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

async def slime_ping(ctx, username):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      channel = ctx.channel
      member_id = members.UNKNOWN
      
      member = username.strip()
      member_id = members.id_search(ctx.message, member)

      if member_id == members.UNKNOWN:
        reply_msg = 'Uh, Klee does not know this name, and therefore cannot add this slime to anyone...'
      else:
        member_mention = f'<@{member_id}>'
        try:
          helpers.add_slime(member_id, 1)
          reply_msg = f'{const.MENTION_ULTRA_ROLE} {member_mention} Woah! It is a slime!  (ﾉ>ω<)ﾉ  Klee has counted {AGE_members[member_id]} slimes for {members.get_name(member_id)}!'
        except KeyError:
          reply_msg = f'{const.MENTION_ULTRA_ROLE} {member_mention} Klee has added the slime on {utcTimestamp()}.  ( ๑>ᴗ<๑ )  Please private message maple to have this member added.'

      await ctx.message.reply(reply_msg, mention_author=False)

      
  except Exception as err:
    log(f'ERROR in total(): {err}')
    raise err

#########################################################################

#add in number 
async def ban(ctx, username, client):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:  #make sure tempremove could only be executed from certain channels
      
      channel = client.get_channel(const.MAIN_CHANNEL)
      
      username = username.strip()
      member_id = members.id_search(ctx.message, username)
      if member_id == members.UNKNOWN:
        await ctx.send('Uh, Klee does not know this name, and therefore cannot tempremove this person... (๑•̆ ૩•̆)')
        return

      # Get the member object from the member ID
      member = ctx.guild.get_member(member_id)
      # Get the existing channel permissions
      overwrites = channel.overwrites
      # Create or modify the permission overwrite for the member
      overwrites[member] = discord.PermissionOverwrite(view_channel=False)
      log(f'{member_id},{member}')
      # Apply the updated channel permissions
      await channel.edit(overwrites=overwrites)
      log('passed3')

      await ctx.send(f"The view_channel permission for {member.name} has been removed.")
  except Exception as err:
    log(f'ERROR in ban(): {err}')
    raise err



async def unban(ctx, username, client):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:  #make sure tempremove could only be executed from certain channels
      channel = client.get_channel(const.CID_SLIMEPING_CHANNEL)

      username = username.strip()
      member_id = members.id_search(ctx.message, username)

      if member_id == members.UNKNOWN:
        await ctx.send('Uh, Klee does not know this name, and therefore cannot tempremove this person... (๑•̆ ૩•̆)')
        return

      # Get the member object from the member ID
      member = ctx.guild.get_member(member_id)
      # Get the existing channel permissions
      overwrites = channel.overwrites
      # Create or modify the permission overwrite for the member
      overwrites[member] = discord.PermissionOverwrite(view_channel=True)
      # Apply the updated channel permissions
      await channel.edit(overwrites=overwrites)

      await ctx.send(f"The view_channel permission for {member.name} has been restored.")
  except Exception as err:
    log(f'ERROR in unban: {err}')
    raise err
