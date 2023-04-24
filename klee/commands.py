from main import AGE_members, utcTimestamp, handleError, members, log, is_any_word_in_string, zoom_member, zoom_time
import const
import helpers
from datetime import datetime, timezone, timedelta
from helpers import total_zoom
import discord
from replit import db, database

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
      recordValue = max(sorted_dict.values())

      while topValues < 3:
          for (id, count) in sorted_dict:
              if topValues == 0:
                  if recordValue != count:
                      topValues += 1
                      recordValue = count
                      second += id
                  else:
                      first += id
              elif topValues == 1:
                  if recordValue != count:
                      topValues += 1
                      recordValue = count
                      third += id
                  else:
                      second += id
              elif topValues == 2:
                  if recordValue != count:
                      topValues += 1
                      recordValue = count
                      break
                  else:
                      third += id

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
    print(f'{utcTimestamp()} ERROR in slimerank(): {err}')
    handleError(err)

#########################################################################

async def doubleping(ctx, *, username):
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

            """except discord.errors.HTTPException:
            with open(f"failed_msg.txt", "a") as f:
                    f.write(f"{reply_msg}\n")
                print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
                os.system('kill 1')
                os.system("python restarter.py")"""

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in doubleping(): {err}')
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
        print(f'{utcTimestamp()} ERROR in sself(): {err}')
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
        print(f'{utcTimestamp()} ERROR in daily(): {err}')
        handleError(err)

#########################################################################

async def slimeadd(ctx, number, *, username):
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

            await ctx.send(reply_msg)

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in add(): {err}')
        handleError(err)

#########################################################################

async def zoom(ctx, *, member):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            member_id = members.id_search(ctx.message, member)
            reply_msg = helpers.add_zoom(member_id, 1)
            await ctx.send(reply_msg)

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in message(): {err}')
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
        print(f'{utcTimestamp()} ERROR in message(): {err}')
        handleError(err)

#########################################################################

async def zoomadd(ctx, number, *, username):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            member = username.strip()
            member_id = members.id_search(ctx.message, member)
            reply_msg = helpers.add_zoom(member_id, int(number))
            await ctx.send(reply_msg)

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in add(): {err}')
        handleError(err)

#########################################################################

async def zoomseason(ctx):
  try:
    if ctx.channel.id in const.BOT_CHANNELS:
      zoom_sum, zoom_message = total_zoom()
      await ctx.send(f'Seasonal zoom count: {zoom_sum}.\n\nMember zoom counts: {zoom_message}')
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in add(): {err}')
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
        print(f'{utcTimestamp()} ERROR in gif(): {err}')
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
        print(f'{utcTimestamp()} ERROR in clear(): {err}')
        handleError(err)

#########################################################################

async def restart(ctx):
    try:
        if ctx.channel.id in const.BOT_CHANNELS:
            print(f'{utcTimestamp()} INFO restart() is initiated...?')
            await ctx.send(
                'command accepted, but Klee does not know what to do with this command... ヾ(⌒(_´･ㅅ･`)_ '
            )

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in restart(): {err}')
        handleError(err)

#########################################################################

async def ping(ctx):
    try:
        await ctx.send('pong!')
    except Exception as err:
        print(f'{utcTimestamp()} ERROR in ping(): {err}')
        handleError(err)

#########################################################################

async def total(ctx):
  try:
    #slime_sum refers to the current total number of slimes summoned
    #slime_message consists of a dictionary having pairs of string:int, 
    #string is the player's name 
    #int is the number of slimes the corresponding player has summoned and recorded
    slime_sum, slime_message = helpers.list_member_slime_count()
    await ctx.send(f'Seasonal Slime Count: {slime_sum}, and Seasonal Slime Record: {slime_message}')
    
  except Exception as err:
    print(f'{utcTimestamp()} ERROR in total(): {err}')
    raise err
