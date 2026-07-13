# DICT: ENTITY-NOTE
class Note:
    """A note record."""

    def __init__(self, note_id, title, body):
        self.id = note_id
        self.title = title
        self.body = body
