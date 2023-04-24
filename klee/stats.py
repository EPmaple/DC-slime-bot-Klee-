from . import members

from replit import db

######################################################
# INIT PART 1 #
######################################################

# initialize AGE_members slime count to 0
AGE_members = {}
for x in members.id_list():
    AGE_members[x] = 0

# member_count is a dictionary containing all ids (string) of the members
member_count = db.keys()

for member_id in AGE_members:
    for db_member_id in member_count:
        if member_id == db_member_id:  #if both ids match
            AGE_members[member_id] = db[
                db_member_id]  #AGE_members is now a dictionary with keys(ids) to values(slimes counts)
        elif member_id not in member_count:
            db[member_id] = 0

# zoom_dictionaries INIT construction
zoom_member = {}  # key=member_id, value=# of times zoomed
zoom_time = {}  # key=member_id, value=specific time for when the player zoomed

# to initialize both zoom dictionaries from data store in replit db
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
