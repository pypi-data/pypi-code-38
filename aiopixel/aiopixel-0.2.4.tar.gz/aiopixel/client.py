from typing import List

import aiohttp

from .exceptions import (GuildNotFound, InvalidKeyException,
                         NoSessionForPlayer, PixelException, PlayerNotFound,
                         PlayerNotInGuild)
from .gametypes import GameType
from .models import stats
from .models.boosters import Booster
from .models.friends import Friend
from .models.guilds import Guild, GuildMember, GuildTag, GuildRank
from .models.leaderboards import Leaderboard, LeaderboardMember
from .models.players import (PixelAchievements, Player, PlayerAchievements,
                             PlayerRank)
from .models.sessions import PlayerSession
from .utils import clean_uuid, get_player_uuid

BASE_API_URL = "https://api.hypixel.net{}"

__all__ = ["PixelClient"]


class PixelClient:
    """
    Asynchronus client for accessing Hypixel's API
    """
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._session = aiohttp.ClientSession()
        self._achievements = PixelAchievements()

    async def _request(self, route: str, method: str, params: dict=None):
        async with self._session.request(method, BASE_API_URL.format(route), params=params) as r:
            if not r.status == 200:
                raise PixelException(
                    "An error occurred while making the request.\n"
                    "Status code: {0.status}.\n"
                    "Reason: {0.reason}".format(r)
                )
            data = await r.json()
            if not data["success"]:
                if data["cause"] == "Invalid API key!":
                    raise InvalidKeyException(data["cause"])
                else:
                    raise PixelException("Error: {}".format(data["cause"]))
            else:
                return data

    async def boosters(self) -> List[Booster]:
        """
        Get a list of all boosters

        Returns
        -------
        `list` of `Booster`
            A list of all boosters in the queue
        
        Raises
        ------
        InvalidKeyException
            If the client's API key is not valid
        
        PixelException
            If an error occurs while making the request or is present in the response json
        """
        data = await self._request(
            "/boosters", "GET", params={"key": self._api_key}
        )
        raw_boosters = data["boosters"]
        boosters = []
        for r_b in raw_boosters:
            boosters.append(Booster(
                r_b["_id"], r_b["purchaserUuid"], r_b["amount"],
                r_b["originalLength"], r_b["length"], r_b["gameType"],
                r_b["dateActivated"], stacked=r_b.get("stacked", None)
            ))
        return boosters

    async def find_guild_by_name(self, name: str) -> str:
        """
        Get the guild id for a guild with the specified name

        Parameters
        ----------
        name: str
            The guild name

        Returns
        -------
        str
            The guild id
        
        Raises
        ------
        InvalidKeyException
            If the client's API key is not valid
        
        PixelException
            If an error occurs while making the request or is present in the response json
        
        GuildNotFound
            If no guild is found
        """
        data = await self._request(
            "/findGuild", "GET", 
            params={"key": self._api_key, "byName": name}
        )
        if data["guild"] is None:
            raise GuildNotFound()
        return data["guild"]

    async def find_guild_by_uuid(self, uuid: str) -> str:
        """
        Get the guild id for the specified player's guild

        Parameters
        ----------
        uuid: str
            The player's uuid

        Returns
        -------
        str
            The guild id
        
        Raises
        ------
        InvalidKeyException
            If the client's API key is not valid
        
        PixelException
            If an error occurs while making the request or is present in the response json
        
        PlayerNotInGuild
            If no guild is found
        """
        data = await self._request(
            "/findGuild", "GET", 
            params={"key": self._api_key, "byUuid": clean_uuid(uuid)}
        )
        if data["guild"] is None:
            raise PlayerNotInGuild()
        return data["guild"]

    async def friends(self, uuid: str) -> List[Friend]:
        """
        Get friends of a player

        Parameters
        ----------
        uuid: str
            The uuid of the player to get friends of
        
        Returns
        -------
        `list` of `Friend`
            A list of objects representing the player's friendships
        
        Raises
        ------
        InvalidKeyException
            If the client's API key is not valid
        
        PixelException
            If an error occurs while making the request or if an error is returned in the response json
        """
        data = await self._request(
            "/friends", "GET", 
            params={"key": self._api_key, "uuid": clean_uuid(uuid)}
        )

        friends_list = []
        for raw_friend in data["records"]:
            friends_list.append(
                Friend(
                    raw_friend["_id"],
                    raw_friend["uuidSender"],
                    raw_friend["uuidReceiver"],
                    raw_friend["started"]
                )
            )
        return friends_list

    async def guild(self, guild_id: str) -> Guild:
        """
        Get a guild

        Parameters
        ----------
        guild_id: str
            The id of the guild to look up
        
        Returns
        -------
        Guild
            The requested guild
        
        Raises
        ------
        InvalidKeyException
            If the client's API key is not valid
        
        PixelException
            If an error occurs while making the request or is present in the response json
        
        GuildNotFound
            If no guild is found
        """
        data = await self._request(
            "/guild", "GET", 
            params={"key": self._api_key, "id": guild_id}
        )

        if data["guild"] is None:
            raise GuildNotFound()
        guild = data["guild"]
        members = []
        for m in guild["members"]:
            members.append(GuildMember(m))

        tag = GuildTag(guild.get("tag", None), guild.get("tagColor", None))
        guild_joinable = guild.get("joinable", False)
        vip_count = guild.get("vipCount", 0)
        mvp_count = guild.get("mvpCount", 0)
        discord = guild.get("discord", None)
        description = guild.get("description", None)
        ranks = guild.get("ranks", None)
        if ranks:
            ranks = [GuildRank(r) for r in ranks]
        preferred_games = guild.get("preferredGames", None)
        if preferred_games:
            preferred_games = [getattr(GameType, game) for game in preferred_games]
        # banner = GuildBanner(
        #     guild["banner"]["Base"], guild["banner"]["Patterns"]
        # )
        return Guild(
            guild["_id"], guild["created"], guild["exp"], discord, guild_joinable,
            description, members, guild["name"], tag,
            vip_count, mvp_count, ranks, preferred_games, guild.get("chatThrottle", 0),
            guild.get("publiclyListed", False), guild.get("chatMute", 0)
        )

    async def leaderboards(self) -> List[Leaderboard]:
        """
        Get all leaderboards
        
        Returns
        -------
        `list` of `Leaderboard`
            A list of all leaderboards
        
        Raises
        ------
        InvalidKeyException
            If the client's API key is not valid
        
        PixelException
            If an error occurs while making the request or is present in the response json
        """
        data = await self._request(
            "/leaderboards", "GET", 
            params={"key": self._api_key}
        )

        raw_leaderboards = data["leaderboards"]
        leaderboard_list = []
        for game, lbs in raw_leaderboards.items():
            game_type = getattr(GameType, game)
            for lb in lbs:
                leaders = []
                for l in lb["leaders"]:
                    leaders.append(LeaderboardMember(l))
                leaderboard_list.append(
                    Leaderboard(
                        lb["path"], lb["prefix"], lb["count"],
                        leaders, lb["title"], game_type
                    )
                )
        return leaderboard_list

    async def player_from_name(self, name: str) -> Player:
        """
        Gets the player represented by the specified name

        Parameters
        ----------
        name: str
            The name of the player
        
        Returns
        -------
        Player
            The specified player
        
        Raises
        ------
        InvalidKeyException
            If the client's API key is not valid
        
        PixelException
            If an error occurs while making the request or is present in the response json
        
        PlayerNotFound
            If the player doesn't exist or has never logged into the server
        """
        uuid = await get_player_uuid(name, self._session)
        if uuid is None:
            raise PlayerNotFound()
        return await self.player_from_uuid(uuid)

    async def player_from_uuid(self, uuid: str) -> Player:
        """
        Gets the player represented by the specified uuid

        Parameters
        ----------
        uuid: str
            The uuid of the player
        
        Returns
        -------
        Player
            The specified player
        
        Raises
        ------
        InvalidKeyException
            If the client's API key is not valid
        
        PixelException
            If an error occurs while making the request or is present in the response json
        
        PlayerNotFound
            If the player doesn't exist or has never logged into the server
        """
        data = await self._request(
            "/player", "GET", 
            params={"key": self._api_key, "uuid": uuid}
        )

        if not bool(data["player"]):
            raise PlayerNotFound()
        player_data = data["player"]
        player_rank = PlayerRank.from_player_data(player_data)
        player_achievements = PlayerAchievements(player_data, self._achievements)
        most_recent_game_type = getattr(GameType, player_data["mostRecentGameType"])
        player_stats = []
        for k, v in player_data["stats"].items():
            player_stats.append(getattr(stats, k + "Stats")(v))
        if "housingMeta" in player_data:
            player_stats.append(stats.HousingStats(player_data["housingMeta"]))
        return Player(
            player_data["_id"], player_data["displayname"], player_data["firstLogin"],
            player_data["lastLogin"], player_data["karma"], player_data["networkExp"],
            player_rank, player_data["lastLogout"], player_achievements,
            player_stats, most_recent_game_type
        )
    
    async def session(self, uuid: str) -> PlayerSession:
        """
        Get a player's current session

        Parameters
        ----------
        uuid: str
            The player to get a session for
        
        Returns
        -------
        PlayerSession
            The player's current session
        
        Raises
        ------
        InvalidKeyException
            If the client's API key is not valid
        
        PixelException
            If an error occurs while making the request or is present in the response json
        
        NoSessionForPlayer
            If the specified player does not have a session
        """
        data = await self._request(
            "/session", "GET", 
            params={"key": self._api_key, "uuid": uuid}
        )

        if not data["session"]:
            raise NoSessionForPlayer()
        else:
            return PlayerSession(data["session"])
