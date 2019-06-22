from datetime import datetime
from typing import List
from enum import Enum

from ..utils import get_player_name
from ..gametypes import GameType

__all__ = ["Guild", "GuildMember", "GuildRank", "GuildTag"]

"""
class GuildPermissions(Enum):
    # Format:
    # Some name         ID   Name                    Description
    MODIFY_GUILD_NAME = (0,  "Modify Guild Name",    "Change the guild's name.")
    MODIFY_GUILD_MOTD = (1,  "Modify Guild MOTD",    "Change the guild's message of the day.")
    MODIFY_GUILD_TAG  = (2,  "Modify Guild Tag",     "Change the guild's tag.")
    MANAGE_RANKS      = (3,  "Change Ranks",         "Promote or demote members (up to their own rank).")
    CHANGE_VISIBILITY = (4,  "Guild Finder options", "Change how the guild is shown in the Guild Finder, if at all.")
    OFFICER_CHAT      = (5,  "Officer Chat",         "Send and receive messages in the officer chat.")
    KICK_MEMBERS      = (6,  "Kick Members",         "Kick members from the guild.")
    MUTE_MEMBERS      = (7,  "Mute Members",         "Mute guild members.")
    INVITE_MEMBERS    = (8,  "Invite Members",       "Invite members to the guild.")
    VIEW_AUDIT_LOG    = (9,  "View Audit Log",       "View the audit log.")
    VIEW_STATS        = (10, "View Stats",           "View a guild member's stats.")
    START_PARTY       = (11, "Guild Party",          "Start a guild party")
    CHANGE_SETTINGS   = (12, "Guild Settings",       "Change the guild settings.")
    CHANGE_DISCORD    = (13, "Change Guild Discord", "Change the guild's Discord join link.")

    def __init__(self, _id: int, name: str, description: str):
        self.id = _id
        self.perm_name = name
        self.description = description
    
    @classmethod
    def from_id(cls, _id: int):
        for _, data in cls.__members__.items():
            if _id == data.id:
                return data
        return None


class GuildBanner:
    def __init__(self, base, patterns):
        self.base = base
        self.patterns = []
        for pattern in patterns:
            self.patterns.append(
                BannerPattern(
                    pattern["Pattern"], pattern["Color"]
                )
            )


class BannerPattern:
    def __init__(self, pattern, color):
        self.pattern = pattern
        self.color = color

"""

class GuildRank:
    def __init__(self, rank: dict):
        self.name = rank["name"]
        # self.permissions = [GuildPermissions.from_id(p) for p in rank["permissions"]]
        self.default = rank["default"]
        self.tag = rank["tag"]
        self.created = datetime.utcfromtimestamp(rank["created"]/1000)
        self.priority = rank["priority"]


class GuildMember:
    """
    A guild member
    """
    
    def __init__(self, member: dict):
        self.uuid = member["uuid"]
        self.rank = member["rank"]
        self.joined = datetime.utcfromtimestamp(member["joined"]/1000)

    async def name(self):
        """
        Gets the current username for this guild member

        Returns
        -------
        str
           The guild member's username
        """
        return await get_player_name(self.uuid)


class GuildTag:
    """
    A guild tag
    """
    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color


class Guild:
    """
    A guild
    """
    def __init__(self, _id: str, created: int, exp: int, discord: str, joinable: bool,
                 description: str, members: List[GuildMember], name: str, tag: GuildTag,
                 vip_count: int, mvp_count: int, ranks: List[GuildRank],
                 preferred_games: List[GameType], chat_throttle: int, is_listed: bool,
                 chat_muted_until: datetime):
        self._id = _id
        self.created = datetime.utcfromtimestamp(created/1000)
        self.exp = exp
        self.discord = discord
        self.joinable = joinable
        self.description = description
        self.members = members
        self.name = name
        self.tag = tag
        # self.banner = banner
        self.vip_count = vip_count
        self.mvp_count = mvp_count
        self.ranks = ranks
        self.preferred_games = preferred_games
        self.chat_throttle = chat_throttle
        self.is_listed = is_listed
        self.chat_muted_until = chat_muted_until
