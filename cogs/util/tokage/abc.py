"""Base Classes for the API."""


class Anime:
    """Represents a MAL Anime

    Attributes
    ----------
    id : int
        The Anime's ID.

    title : str
        The Series title.

    type : str
       The Anime's type. Can be `ONA`/`OVA`/`TV`/`Movie`.

    synonyms : list[str]
       Alternative names for the Anime.

    image : str
        The cover image URL for the Anime.

    japanese_title : str
        Japanese title of the Anime.

    status : str
        Airing status of the Manga.

    episodes : int
        Episode count of the Manga.

    air_start : str
        Airing start date.

    air_end : str
        Airing end date.

    synopsis : str
        Description of the Anime.

    producers : list[list]
        WIP - List of the Anime's producers.

    licensors : list[list]
        WIP - List of the Anime's licensors.

    studios : list[list]
        WIP - List of the Anime's studios

    premiered : str
        Premier season.

    broadcast : str
        Broadcast times.

    genres : list[str]
        List of the Anime's genres.

    link : str
        Link to the Anime on MAL.

    score : tuple(int)
        Tuple of (score, voters).

    duration : str
        Duration of the Anime (may be per episode).

    rank : int
        Anime's rank on the MAL board.

    popularity : int
        Popularity rank of the Anime.

    members : int
        Amount of members which have the Anime in their list.

    favorites : int
        Amount of favorites given to the Anime.

    source : str
        Type of source material. Can be `Manga` `Novel` or `Original`.

    related : dict
        WIP - May include :attr:`adaptation`, :attr:`prequel` and :attr:`sequel`. Can also be None.

    adaptation : list[dict]
        WIP - Adaptations of the Anime. May be None.

    sequel : list[dict]
        WIP - Sequels to the Anime, if any. May be None.

    prequel : list[dict]
        WIP - Prequels to the Anime, if any. May be None.

    """

    def __init__(self, anime_id, **kwargs):
        self.id = anime_id
        self.title = kwargs.pop('title', None)
        self.type = kwargs.pop('type', None)
        self.synonyms = kwargs.pop('synonyms', None)
        self.image = kwargs.pop('image', None)
        self.japanese_title = kwargs.pop('japanese', None)
        self.status = kwargs.pop('status', None)
        self.episodes = kwargs.pop('episodes', None)
        self._air_time = kwargs.pop('aired', None)
        if " to " not in self._air_time:
            self.air_start = self._air_time
            self.air_end = None
        else:
            self.air_start, self.air_end = self._air_time.split(" to ")
        self.premiered = kwargs.pop('premiered', None)
        self.broadcast = kwargs.pop('broadcast', None)
        self.synopsis = kwargs.pop('synopsis', None)
        self.producers = kwargs.pop('producer', None)
        self.licensors = kwargs.pop('licensor', None)
        self.studios = kwargs.pop('studio', None)
        self.source = kwargs.pop('source', None)
        self._raw_genres = kwargs.pop('genre', None)
        if self._raw_genres is None:
            self._raw_genres = kwargs.pop('genres', None)
        self.genres = [g[1] for g in self._raw_genres] if self._raw_genres else None
        self.duration = kwargs.pop('duration', None)
        self.link = kwargs.pop('link-canonical', None)
        self.rating = kwargs.pop('rating', None)
        self.score = kwargs.pop('score', None)
        self.rank = kwargs.pop('ranked', None)
        self.popularity = kwargs.pop('popularity', None)
        self.members = kwargs.pop('members', None)
        self.favorites = kwargs.pop('favorites', None)
        self.related = kwargs.pop('related', None)
        if self.related is not None:
            self.adaptation = self.related.get("Adaptation", None)
            self.sequel = self.related.get("Sequel", None)
            self.prequel = self.related.get("Prequel", None)


class Manga:
    """Represents a MAL Manga (Includes Novels)

    Attributes
    ----------
    id : int
        The Manga's ID.

    title : str
        The Series title.

    type : str
       The Manga's type. Can be either "Novel" or "Manga".

    synonyms : list[str]
       Alternative names for the Manga.

    image : str
        The cover image URL for the Manga.

    japanese_title : str
        Japanese title of the Manga.

    status : str
        Publishing status of the Manga.

    volumes : int
        Volume count of the Manga.

    chapters : int
        Chapter count of the Manga.

    publish_start : str
        Publication start date.

    publish_end : str
        Publication end date.

    synopsis : str
        Description of the Manga.

    author : str
        Name of the Manga author.

    serialization : str
        The Manga's serialization.

    genres : list[str]
        List of the Manga's genres.

    link : str
        Link to the Manga on MAL.

    score : tuple(int)
        Tuple of (score, voters).

    rank : int
        Manga's rank on the MAL board.

    popularity : int
        Popularity rank of the Manga.

    members : int
        Amount of members which have the Manga in their list.

    favorites : int
        Amount of favorites given to the Manga.

    related : dict
        WIP - May include :attr:`adaptation`, :attr:`prequel` and :attr:`sequel`. Can also be None.

    adaptation : list[dict]
        WIP - Adaptations of the Manga. May be None.

    sequel : list[dict]
        WIP - Sequels to the Manga, if any. May be None.

    prequel : list[dict]
        WIP - Prequels to the Manga, if any. May be None.

    """

    def __init__(self, manga_id, **kwargs):
        self.id = manga_id
        self.title = kwargs.pop('title', None)
        self.type = kwargs.pop('type', None)
        self.synonyms = kwargs.pop('synonyms', None)
        self.image = kwargs.pop('image', None)
        self.japanese_title = kwargs.pop('japanese', None)
        self.status = kwargs.pop('status', None)
        self.volumes = kwargs.pop('volumes', None)
        self.chapters = kwargs.pop('chapters', None)
        self._publish_time = kwargs.pop('published', None)
        if " to " not in self._publish_time:
            self.publish_start = self._publish_time
            self.publish_end = None
        else:
            self.publish_start, self.publish_end = self._publish_time.split(" to ")
        self.synopsis = kwargs.pop('synopsis', None)
        self.author = kwargs.pop('author', None)[0]["name"]  # TODO: Person
        self.serialization = kwargs.pop('serialization', None)[0]  # TODO: add serializations
        self._raw_genres = kwargs.pop('genre', None)
        if self._raw_genres is None:
            self._raw_genres = kwargs.pop('genres', None)
        self.genres = [g[1] for g in self._raw_genres] if self._raw_genres else None
        self.link = kwargs.pop('link-canonical', None)
        self.score = kwargs.pop('score', None)
        self.rank = kwargs.pop('ranked', None)
        self.popularity = kwargs.pop('popularity', None)
        self.members = kwargs.pop('members', None)
        self.favorites = kwargs.pop('favorites', None)
        self.related = kwargs.pop('related', None)  # TODO: SOMETHING.
        if self.related is not None:
            self.adaptation = self.related.get("Adaptation", None)
            self.sequel = self.related.get("Sequel", None)
            self.prequel = self.related.get("Prequel", None)


class Character:
    """Represents a MAL Character

    Attributes
    ----------
    id : int
        The Character's ID.

    name : str
        Character's name.

    link : str
        Link to the Character on MAL.

    image : str
        Image URL of the Character.

    favorites : int
        Amount of favorites the Character has.

    animeography : list[dict]
        Anime the Character is featured in.

    mangaography : list[dict]
        Manga the Character is featured in.

    japanese : str
        Japanese name of the character.

    about : str
        WIP - Information about the character. As of now, spoilers are unformatted and will appear.

    voice_actors : list[dict]
        WIP - List of voice actors who played this Character.

    """

    def __init__(self, char_id, **kwargs):
        self.id = char_id
        self.link = kwargs.pop('link-canonical', None)
        self.name = kwargs.pop('name', None)
        self.image = kwargs.pop('image', None)
        self.favorites = kwargs.pop('member-favorites', None)
        self.animeography = kwargs.pop('animeography', None)  # TODO: Handle
        self.mangaography = kwargs.pop('mangaography', None)  # TODO: Handle
        self.japanese = kwargs.pop('name-japanese', None)
        self.about = kwargs.pop('about', None)
        self.voice_actors = kwargs.pop('voice-actors', None)  # TODO: Handle


class Person:
    """Represents a MAL Person (Voice Actors, Staff, etc.)

    Attributes
    ----------
    id : int
        The Person's ID.

    name : str
        The Person's name.

    link : str
        Link to the Person on MAL.

    image : str
        Image URL of the Person.

    favorites : int
        Amount of favorites the Person has.

    anime : list[dict]
        WIP - Staff positions in Anime.

    manga : list[dict]
        WIP - Published Manga.

    more : str
        Additional info about the Person.

    website : str
        Link to the Person's website

    voice_acting : list[dict]
        WIP - List of voice acting roles the Person has.

    """

    def __init__(self, person_id, **kwargs):
        self.id = person_id
        self.link = kwargs.pop('link-canonical', None)
        self.name = kwargs.pop('name', None)
        self.image = kwargs.pop('image', None)
        self.favorites = kwargs.pop('member-favorites', None)
        self.anime = kwargs.pop('anime-staff-position', None)  # TODO: Handle
        self.manga = kwargs.pop('published-manga', None)  # TODO: Handle
        self.birthday = kwargs.pop('birthday', None)
        self.more = kwargs.pop('more', None)
        self.website = kwargs.pop('website', None)
        self.voice_acting = kwargs.pop('voice-acting-role', None)  # TODO: Handle
 