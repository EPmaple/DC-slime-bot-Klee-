from .member_list import name_id, id_name
import discord
import re

def get_name(member_id):
    return id_name[member_id]

def id_list():
    return _cached_id_list_sorted_by_name

def id_search(message: discord.Message):
    member_id = 0
    # '@ultra @user1'
    if len(message.raw_mentions) != 0:
        member_id = str(message.raw_mentions[0])
    else:
        normalized_separators = re.sub('[\s;,]+', ' ', message.content)
        without_at_prefix = re.sub('(^| )@', ' ', normalized_separators)
        normalized_message = re.sub('[^ a-zA-Z0-9][^ ]*', '', without_at_prefix)
        words = normalized_message.split()
        if len(words) > 0:
            name_part = words[0]
            name_part_lower = name_part.lower()
            # '@ultra me'
            if name_part_lower == 'me':
                member_id = str(message.author.id)
            # '@ultra user1'
            else:
                if name_part_lower == 'dan':
                    member_id = str(name_id['Dan'])
                elif name_part_lower == 'moon':
                    member_id = str(name_id['Moon'])
                else:
                    for name in name_id:
                        if name_part_lower in name.lower():
                            member_id = str(name_id[name])
    return member_id

def _id_list_sorted_by_name():
    sorted_name = sorted(id_name.items(), key=lambda kv: kv[1])
    return [id for id, name in sorted_name]

_cached_id_list_sorted_by_name = _id_list_sorted_by_name()

