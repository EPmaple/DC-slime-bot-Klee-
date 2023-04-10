from main import AGE_members, utcTimestamp, handleError, members, log
import const
import helpers
"""@bot.command()
async def hello(ctx):
    await commands.hello_world(ctx)"""

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