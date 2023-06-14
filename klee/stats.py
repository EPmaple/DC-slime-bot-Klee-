from . import members

from replit import db

######################################################
# INIT PART 1 #
######################################################

# initialize AGE_members slime counts and zoom counts to 0
AGE_members = {}

for member_id in members.id_list():
  AGE_members[member_id]['slimes'] = 0
  AGE_members[member_id]['zooms'] = 0
  AGE_members[member_id]['zoomtime'] = []

# member_count is a dictionary containing all ids (string) of the members
member_data = db.keys()

#member_id and db_member_id are strings of id, ex. "12345124124"
#beware of KeyError, as db['zooms'][something] requires db['zooms'] = {} to be established beforehand in replit db
for member_id in members.id_list():
  #to handle the case when a new member is added to the member_list but has not been registered by replit db yet, thus initialize the new member's data in replit db
  if member_id not in member_data:
    db[member_id]['slimes'] = 0
    db[member_id]['zooms'] = 0
    db[member_id]['zoomtime'] = []
    
  else:
    AGE_members[member_id]['slimes'] = db[member_id]['slimes']
    AGE_members[member_id]['zooms'] = db[member_id]['zooms']
    AGE_members[member_id]['zoomtime'] = db[member_id]['zoomtime']

# zoom_dictionaries INIT construction
zoom_member = {}  # key=member_id, value=# of times zoomed
zoom_time = {}  # key=member_id, value=specific time for when the player zoomed

# to initialize both zoom dictionaries from data store in replit db
for member_id in AGE_members:
  #for member_id that were from replit db
  zoom_member[member_id] = AGE_members[member_id]['zooms']
  #initialize a key-value pair for that member_id to the number of times s/he zoomed

for member_id in zoom_member:
    #going off the zoom dictionary that was created above, which has all who have zoomed
  zoom_time[member_id] = AGE_members[member_id]['zoomtime']
            #the value in this case is an array, which stores the specific times a player was reported zooming; and the key is the member_id + zt