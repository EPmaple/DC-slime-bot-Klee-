from .member_list import name_id, id_name
from typing import Union
import discord
from discord.ext import commands

def get_name(member_id):
    return id_name[member_id]

def id_search(ctx: Union[commands.Context, discord.Message], name_part: str):
    member_id = 0
    name_part_lower = name_part.lower()
    if (name_part_lower == 'me') or ('me' in name_part_lower):
        member_id = str(ctx.author.id)
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

