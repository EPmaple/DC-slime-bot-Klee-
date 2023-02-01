from .member_list import name_id, id_name
import discord
import re

UNKNOWN = '0'

def get_name(member_id):
    return id_name[member_id]

def id_list():
    return _cached_id_list_sorted_by_name

def id_search(message_ctx: discord.Message, text: str):

    # Accepts discord @mention from message_ctx, but only if it is in searched text
    if len(message_ctx.raw_mentions) != 0:
        mention_id = str(message_ctx.raw_mentions[0])
        if mention_id in text:
            return mention_id

    # Empty check
    name_parts = text.split()
    if len(name_parts) == 0:
        return UNKNOWN

    # Map free text to a known user

    # consider first word of searched text only, for now
    name_part = name_parts[0]

    # consider name part after any special character as irrelevant
    name_part_cleaned = re.sub('[^a-zA-Z0-9].*', '', name_part)
    name_part_lower = name_part_cleaned.lower()

    if name_part_lower == '' or name_part_lower.isspace():
        return UNKNOWN

    # map 'me'
    if name_part_lower == 'me':
        return str(message_ctx.author.id)

    # map if name matches the part
    for name in name_id:
        if name_part_lower == name.lower():
            return str(name_id[name])

    # map if name begins with the part
    for name in name_id:
        if name.lower().startswith(name_part_lower):
            return str(name_id[name])

    # map if name contains the part
    for name in name_id:
        if name_part_lower in name.lower():
            return str(name_id[name])

    return UNKNOWN

def _id_list_sorted_by_name():
    sorted_name = sorted(id_name.items(), key=lambda kv: kv[1])
    return [id for id, name in sorted_name]

_cached_id_list_sorted_by_name = _id_list_sorted_by_name()

