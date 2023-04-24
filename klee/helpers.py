from main import db, AGE_members, zoom_member, zoom_time, utcTimestamp, handleError, members, dt_from_timestamp
from datetime import datetime, timezone, timedelta
from replit import database
from operator import itemgetter
import discord

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

def add_slime(member_id, number):
    if member_id in db:  #if member id already in replit database,
        db[member_id] += int(number)
        AGE_members[member_id] += int(number)
    else:  #if member id was not in replit database
        db[member_id] = int(number)
        AGE_members[member_id] = int(number)

#########################################################################

#helper method, takes in member id and the number of slimes want to be added
#can use negative numbers to subtract slimes
def add_zoom(member_id, number):
    if member_id == 0:
        return 'Uh, Klee does not know this name...(◕︿◕✿)'

    member_idz = member_id + 'z'
    member_idzt = member_idz + 't'

    original_count = zoom_member.get(member_idz, 0)
    original_zoom_times = zoom_time.get(member_idzt, [])

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

        # perform the actual updates
        db[member_idz] = new_count
        zoom_member[member_idz] = db[member_idz]
        if member_idzt in db:
          # If the value is in the db, it is of type ObservedList.
          # The type we are setting is a list. In order to override
          # the underlying list of an ObservedList, we must call
          # ObservedList.set_value
          db[member_idzt].set_value(new_zoom_times)
        else:
          db[member_idzt] = new_zoom_times
        zoom_time[member_idzt] = db[member_idzt]

    except Exception as err:
        print(f'{utcTimestamp()} ERROR in message(): {err}')
        handleError(err)

        # update failed, reset back to original
        db[member_idz] = original_count
        zoom_member[member_idz] = db[member_idz]
        if member_idzt in db:
          # If the value is in the db, it is of type ObservedList.
          # The type we are setting is a list. In order to override
          # the underlying list of an ObservedList, we must call
          # ObservedList.set_value
          db[member_idzt].set_value(original_zoom_times)
        else:
          db[member_idzt] = original_zoom_times
        zoom_time[member_idzt] = db[member_idzt]

        return f'Klee failed to modify zoom count (◕︿◕✿), {members.get_name(member_id)} remains at {original_count} zooms.'

    # rolling 7 day window for punish-ability
    days = 7
    window = datetime.utcnow().replace(microsecond=0) - timedelta(days=days)
    count_in_window = sum(dt_from_timestamp(d) >= window for d in zoom_time[member_idzt])

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

#helper method
def list_member_slime_count():
    slime_sum = sum(AGE_members.values())
    slime_message = {}
    for member_id in members.id_list():
        # set name:slime_count to message dict
        slime_message[members.get_name(member_id)] = AGE_members[member_id]
    return (slime_sum, slime_message)

#########################################################################

#helper function
#return zoom_sum [int], total # of zoom
#       zoom_message [dict], list the top zoomers along with their corresponding # of zooms
def total_zoom():
    # transform to list of tuples of the form (name, count)
    name_transform = ((members.get_name(k[:-1]), v) for k, v in zoom_member.items() if k[:-1] != '0')
    
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
