from . import members
from .logging import log, handleError
from collections import deque

from replit import db

######################################################
# INIT PART 1 #
######################################################

# Define the keys and their corresponding default values
keys = {
    'slimes': 0,
    'slimelist': [],
    'zooms': 0,
    'zoomtime': []
}

######################################################

# Can handle the case: new member_id in member_list but not in replit db
def local_db():
  try:
    # Initialization
    AGE_members = {}
    # member_data is a dictionary containing all ids (string) of the members
    member_data = db.keys()
    
    for member_id in members.id_list():
      AGE_members[member_id] = {}
      # keys.items() returns an iterable containing tuples, 1st element of tuple is key, 2nd element of tuple is value

      # No data in replit db, set data to default
      if member_id not in member_data:
        for key, value in keys.items():
          AGE_members[member_id][key] = value
          db[member_id][key] = value
      # There is data in db
      else: 
        for key, value in keys.items():
          try:
            AGE_members[member_id][key] = db[member_id][key]
          #beware of KeyError, as db['zooms'][something] requires db['zooms'] = {} to be established beforehand in replit db
          except KeyError:
            AGE_members[member_id][key] = value
            db[member_id][key] = value

    return AGE_members

  except Exception as err:
    log(f'ERROR in local_db(): {err}')
    handleError(err)

AGE_members = local_db()

######################################################

def seasonal_slimesum_f():
  slime_sum = 0
  for member_id in AGE_members:
    ind_slimes = AGE_members[member_id]['slimes']
    slime_sum += ind_slimes

  return slime_sum

######################################################

#secondkeys = ['time', 'member_id']

def get_slime_records():
  try:
    slime_records = {} # Initialization
    slime_dbrecords = db['slime_records'] # Of format Observed Dictionary
    #log(slime_dbrecords) ObservedDict(value={'1': ObservedDict(value={'time': '1237123', 'member_id': '1242132'})})
    
    for key, value in slime_dbrecords.items():
      slime_records[key] = dict(value) # convert from ObservedDict to dict
      #log(slime_records) # {'1': {'time': '1237123', 'member_id': '1242132'}}

    return slime_records
    
  except Exception as err:
    log(f'ERROR in get_slime_records(): {err}')
    handleError(err)

slime_records = get_slime_records()

######################################################
