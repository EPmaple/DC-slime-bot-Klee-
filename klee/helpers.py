from . import members, const, kommands
from .logging import log, handleError
from .stats import AGE_members, seasonal_slimesum_f, slime_records

from datetime import datetime, timedelta
from operator import itemgetter
from replit import db, database

#########################################################################
#reads the failed_msg.txt and stores it in a list called failed_msg
def read_txt():
  failed_msg = []
  #opens the txt, which stores msg that failed to be send, and stores each line of the txt into the list created above
  #txt is automatically closed by 'with open'
  with open("failed_msg.txt") as f:
    for line in f:
      failed_msg.append(line.strip())
  return failed_msg

#########################################################################

#helper method
def list_member_slime_count():
  slime_sum = seasonal_slimesum_f()

  slime_msg = {}
  for member_id in members.id_list():
    # set name:slime_count to message dict
    slime_msg[members.get_name(member_id)] = AGE_members[member_id]['slimes']

  return (slime_sum, slime_msg)

#########################################################################

def add_slime(member_id, number, message):
  try:
    # Time object stringified
    summoned_time = str(message.created_at)
    current_slimesum = seasonal_slimesum_f()

    #POSITIVE
    if int(number) > 0:
      for i in range(int(number)):
        slime_id = str(current_slimesum + i)
        AGE_members[member_id]['slimelist'].append(slime_id)
        slime_records[slime_id] = {'time': summoned_time, 'member_id': member_id}
          
    #NEGATIVE
    elif int(number) < 0:
      for i in range(abs(int(number))):
        slime_id = AGE_members[member_id]['slimelist'].pop()
        #db[member_id]['slimelist'].pop()
        del slime_records[slime_id]

    #To update db
    AGE_members[member_id]['slimes'] += int(number)
    db[member_id]['slimes'] += int(number)
    db[member_id]['slimelist'] = AGE_members[member_id]['slimelist']
    db['slime_records'] = slime_records

    saved = db[member_id]['slimelist']
  
  except Exception as err:
    log(f'ERROR in add_slime(): {err}')
    handleError(err)

#########################################################################

#helper method, takes in member id and the number of zooms want to be added
def add_zoom(member_id, number):
  if member_id == 0:
    return 'Uh, Klee does not know this name...(◕︿◕✿)'

  #retrieves the data dictionaries related to this member, if none is found, return {}
  member_data = AGE_members.get(member_id, {})
  original_count = member_data.get('zooms', 0)
  original_zoom_times = member_data.get('zoomtime', [])

  try:
    # clamp to 0 if subtracting more than the actual current count
    new_count = max(0, original_count + number)

    # database.to_primitive will convert an ObservedList to a list
    # and leave a list as a list
    new_zoom_times = database.to_primitive(original_zoom_times).copy()

    # add timestamps if new zooms were added
    while len(new_zoom_times) < new_count:
      new_zoom_times += [f'{utcTimestamp()}']
    # remove timestamps if zooms were subtracted
    while len(new_zoom_times) > new_count:
      del new_zoom_times[-1]

    #perform the actual updates
    db[member_id]['zooms'] = new_count
    AGE_members[member_id]['zooms'] = db[member_id]['zooms']
    if member_id in db:
      # If the value is in the db, it is of type ObservedList.
      # The type we are setting is a list. In order to override
      # the underlying list of an ObservedList, we must call
      # ObservedList.set_value
      db[member_id]['zoomtime'].set_value(new_zoom_times)
    else:
      db[member_id]['zoomtime'] = new_zoom_times
    AGE_members[member_id]['zoomtime'] = db[member_id]['zoomtime']

  except Exception as err:
    log(f'ERROR in add_zoom(): {err}')
    handleError(err)

    # update failed, reset back to original
    db[member_id]['zooms'] = original_count
    AGE_members[member_id]['zooms'] = db[member_id]['zooms']
    if member_id in db:
      # If the value is in the db, it is of type ObservedList.
      # The type we are setting is a list. In order to override
      # the underlying list of an ObservedList, we must call
      # ObservedList.set_value
      db[member_id]['zoomtime'].set_value(original_zoom_times)
    else:
      db[member_id]['zoomtime'] = original_zoom_times
    AGE_members[member_id]['zoomtime'] = db[member_id]['zoomtime']

    return f'Klee failed to modify zoom count (◕︿◕✿), {members.get_name(member_id)} remains at {original_count} zooms.'
    
  # rolling 7 day window for punish-ability
  days = 7
  window = datetime.utcnow().replace(microsecond=0) - timedelta(days=days)
  count_in_window = sum(dt_from_timestamp(d) >= window for d in AGE_members[member_id]['zoomtime'])

  ret = f'The number of times {members.get_name(member_id)} zoomed has been changed from {original_count} to {new_count}.'
  ret += f'\nZooms in the last {days} days: {count_in_window}.'
  if new_count == 0:
    ret += '\nGood job not zooming this season!! ヾ(๑ㆁᗜㆁ๑)ﾉ”'
  elif count_in_window == 0:
    ret += '\nYou\'re remedying your zooming ways, way to go!! ヾ(๑ㆁᗜㆁ๑)ﾉ”'
  else:
    ret += '\nヽ( `д´*)ノ Why did you zoom ?!'

  return ret

#########################################################################

#helper function
#return zoom_sum [int], total # of zoom
#       zoom_message [dict], list the top zoomers along with their corresponding # of zooms
def total_zoom():
  # transform to list of tuples of the form (name, count)
  name_transform = []
  for member_id in AGE_members:
    tuple = (members.get_name(member_id), AGE_members[member_id]['zooms'])
    name_transform.append(tuple)

  # secondary key sort: sort by name
  name_sort = sorted(name_transform, key=itemgetter(0))

  # primary key sort: sort by count, descending
  value_sort = sorted(name_sort, key=itemgetter(1), reverse=True)

  # at this point the list will be sorted by count first.
  # for any members with matching counts, the members will be in alphabetical order.
  # for example: [('traffyboi', 3), ('aile', 2), ('vent', 2)]

  # back to dictionary
  zoom_message = {k: v for k, v in value_sort}
  zoom_sum = sum(zoom_message.values())

  return (zoom_sum, zoom_message)
    
""" Previous version by Traf
def total_zoom():
    # transform to list of tuples of the form (name, count)
    name_transform = ((members.get_name(k), v) for k, v in zoom_member.items() if k[:-1] != '0')
    
    # secondary key sort: sort by name
    name_sort = sorted(name_transform, key=itemgetter(0))

    # primary key sort: sort by count, descending
    value_sort = sorted(name_sort, key=itemgetter(1), reverse=True)

    # at this point the list will be sorted by count first.
    # for any members with matching counts, the members will be in alphabetical order.
    # for example: [('traffyboi', 3), ('aile', 2), ('vent', 2)]

    # back to dictionary
    zoom_message = {k: v for k, v in value_sort}
    zoom_sum = sum(zoom_message.values())

    return (zoom_sum, zoom_message)
"""
#########################################################################

def is_any_word_in_string(wordlist, string):
    return any(word in string for word in wordlist)

#########################################################################

#return formatted timestamp

def utcTimestamp():
    return f'{datetime.utcnow().replace(microsecond=0).isoformat()}Z'

def dt_from_timestamp(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')

#########################################################################

# import os; os.getcwd(); to find out current relative directory
#default relative path is: '/home/runner/Slime-bot-for-DC'
file_path = "timestamp.py"

def read_timestamp():
  try:
    with open(file_path, "r") as file:
      timestamp = file.read()
      #log(f"the following is an attempt to get timestamp: {timestamp}")
    return timestamp
  except Exception as err:
    log(f'{utcTimestamp()} ERROR read_timestamp(): {err}')
    handleError(err)

# Input timestamp is: str(msg.created_at)
def update_timestamp(timestamp='current'):
  try:
    # Meaning default to current, and no string timestamp is passed in
    if timestamp == 'current':
      timestamp = str(datetime.utcnow()) # Time object of format "%Y-%m-%d %H:%M:%S.%f", stringified

    with open(file_path, "w") as file:
      file.write(timestamp)
  except Exception as err:
    log(f'{utcTimestamp()} ERROR update_timestamp(): {err}')
    handleError(err)
#########################################################################

######
#Potential issue resolved: let's say that right after Klee has processed the histories and she gets disconnected, we may need to worry about Klee re-processing those same histories again. But since Klee itself will await a message to discord to show that those histories are taken care of, db["timeOfLastMessage"] is updated, so we have updated our considering range and avoid the issue of double counting those messages again
######
#because we want to access a channel of which the client is in, thus take in a parameter, the client object, as an argument
async def checkHistory(client):
  try:
    timeOfLastMessage = read_timestamp()
    
    # Convert the string to a datetime object
    # "%Y-%m-%d %H:%M:%S.%f" is the format specifier that matches the string representation of UTC time
    time_obj = datetime.strptime(timeOfLastMessage, "%Y-%m-%d %H:%M:%S.%f")
    
    current = datetime.utcnow()

    #change to slimeping channel after testing
    #CID_SLIMEPING_CHANNEL
    #CID_BOTTESTING_CHANNEL
    channel = client.get_channel(const.CID_BOTTESTING_CHANNEL)
    if channel:
      async for message in channel.history(limit=300, after=time_obj, before=current):
          #for now, only set to catch all pings
          #may expand to catch zooms as well
        if is_any_word_in_string(const.PING_MENTIONS, message.content):

          #because we only have the message, we can get_context(message) to obtain ctx
          ctx = await client.get_context(message)

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
                  add_slime(member_id, 1, message)
                  reply_msg = f"(ﾉ>ω<)ﾉ  Klee has counted {AGE_members[member_id]['slimes']} slimes for {members.get_name(member_id)}! Sorry for not responding earlier, Klee stayed up late watching the circus' midnight show and feels a bit tired."

              except KeyError:
                  reply_msg = f'Klee has added the slime on {utcTimestamp()}.  ( ๑>ᴗ<๑ )  Please private message maple to have this member added.'

          update_timestamp()
          await ctx.message.reply(reply_msg, mention_author=False)

    else:
      # Handle the case when the channel was not found
      log(f"Channel with ID {channel_id} not found")
    
  except Exception as err:
    log(f'ERROR in checkHistory(): {err}')
    handleError(err)

