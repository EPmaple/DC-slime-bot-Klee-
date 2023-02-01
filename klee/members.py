from .member_list import name_id, id_name
import discord

UNKNOWN = '0'

def get_name(member_id):
    return id_name[member_id]

def id_list():
    return _cached_id_list_sorted_by_name

def id_search(message: discord.Message, name_part: str):

    # Accepts discord @mention, but only if it is in name_part (i.e. the first word before/after @ultra; currently irrelevant for other commands)
    if len(message.raw_mentions) != 0:
        mention_id = str(message.raw_mentions[0])
        if mention_id in name_part:
            return mention_id

    # Map free text to a known user
    member_id = UNKNOWN
    name_part_lower = name_part.lower()
    if (name_part_lower == 'me') or ('me' in name_part_lower):
        member_id = str(message.author.id)
    else:
        if name_part_lower == 'dan':
            member_id = str(name_id['Dan'])
        elif name_part_lower == 'tra':
            member_id = str(name_id['tra20012'])
        else:
            for name in name_id:
                if name_part_lower in name.lower():
                    member_id = str(name_id[name])
    return member_id

def _id_list_sorted_by_name():
    sorted_name = sorted(id_name.items(), key=lambda kv: kv[1])
    return [id for id, name in sorted_name]

_cached_id_list_sorted_by_name = _id_list_sorted_by_name()

