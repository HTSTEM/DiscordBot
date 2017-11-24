import re
import asyncio
from urllib.parse import parse_qs
from lxml import etree

import aiohttp

from .abc import Anime, Manga, Person, Character
from .errors import *  # noqa

BASE_URL = 'https://jikan.me/api/v1.2/'
ANIME_URL = BASE_URL + 'anime/'
MANGA_URL = BASE_URL + 'manga/'
PERSON_URL = BASE_URL + 'person/'
CHARACTER_URL = BASE_URL + 'character/'


class Client:
    """Client connection to the MAL API.
    This class is used to interact with the API.

    :param Optional[aiohttp.ClientSession] session:
        The session to use for aiohttp requests.
        Defaults to creating a new one.

    Attributes
    ----------
    session : aiohttp.ClientSession

        The session used for aiohttp requests.

    """
    def __init__(self, session=None, *, loop=None):
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.session = aiohttp.ClientSession(loop=self.loop) if session is None else session

    async def cleanup(self):
        await self.session.close()

    async def request(self, url):
        async with self.session.get(url) as resp:
            return await resp.json()

    async def get_anime(self, target_id):
        """Retrieves an :class:`Anime` object from an ID

        Raises a :class:`AnimeNotFound` Error if an Anime was not found corresponding to the ID.
        """
        response_json = await self.request(ANIME_URL + str(target_id))
        if response_json is None:
            raise AnimeNotFound("Anime with the given ID was not found")
        result = Anime(target_id, **response_json)
        return result

    async def get_manga(self, target_id):
        """Retrieves a :class:`Manga` object from an ID

        Raises a :class:`MangaNotFound` Error if a Manga was not found corresponding to the ID.
        """
        response_json = await self.request(MANGA_URL + str(target_id))
        if response_json is None:
            raise MangaNotFound("Manga with the given ID was not found")
        result = Manga(target_id, **response_json)
        return result

    async def get_character(self, target_id):
        """Retrieves a :class:`Character` object from an ID

        Raises a :class:`CharacterNotFound` Error if a Character was not found corresponding to the ID.
        """
        response_json = await self.request(CHARACTER_URL + str(target_id))
        if response_json is None:
            raise CharacterNotFound("Character with the given ID was not found")
        result = Character(target_id, **response_json)
        return result

    async def get_person(self, target_id):
        """Retrieves a :class:`Person` object from an ID

        Raises a :class:`PersonNotFound` Error if a Person was not found corresponding to the ID.
        """
        response_json = await self.request(PERSON_URL + str(target_id))
        if response_json is None:
            raise PersonNotFound("Person with the given ID was not found")
        result = Person(target_id, **response_json)
        return result

    async def search_id(self, type_, query: str):
        """Parse a google query and return the ID.

        Raises a :class:`TokageNotFound` Error if an ID was not found.
        """
        query = "site:myanimelist.net/{}/ {}".format(type_, query)
        params = {
            'q': query,
            'safe': 'on'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'
        }

        url = 'https://www.google.com/search'
        async with self.session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError('Google somehow failed to respond.')

            root = etree.fromstring(await resp.text(), etree.HTMLParser())
            nodes = root.findall(".//div[@class='g']")
            for node in nodes:
                url_node = node.find('.//h3/a')
                if url_node is None:
                    continue

                url = url_node.attrib['href']
                if not url.startswith('/url?'):
                    continue

                url = parse_qs(url[5:])['q'][0]
                id = self.parse_id(url)
                if id is None:
                    raise TokageNotFound("An ID corresponding to the given query was not found")
                return id

    @staticmethod
    def parse_id(link):
        """Get ID from a myanimelist link."""
        pattern = r'(?:\/([\d]+)\/)'
        match = re.search(pattern, link)
        if match:
            target_id = match.group(1)
            return target_id
        else:
            None
