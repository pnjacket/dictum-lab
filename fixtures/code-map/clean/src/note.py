import os

DB_PATH = os.environ.get("NOTES_DB_PATH", "notes.db")


# DICT: ENTITY-NOTE
class Note:
    """A note record."""

    def __init__(self, note_id, title, body):
        self.id = note_id
        self.title = title
        self.body = body
