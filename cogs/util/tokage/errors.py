class TokageNotFound(Exception):
    """This Error is the base class of all Errors in Tokage.
    Usually you wont recive this error, but some functions may raise it.
    """
    pass


class AnimeNotFound(TokageNotFound):
    """This Error is raised when an Anime was not found."""
    pass


class MangaNotFound(TokageNotFound):
    """This Error is raised when a Manga was not found."""
    pass


class PersonNotFound(TokageNotFound):
    """This Error is raised when a Person was not found."""
    pass


class CharacterNotFound(TokageNotFound):
    """This Error is raised when a Character was not found."""
    pass
