import re
from unidecode import unidecode
from resolver.database import db

SLUG_MAX = 64
TITLE_MAX = 512

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
_clean_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|}]+')

def slugify(text):
    """Generates an ASCII-only slug.
       Written by Armin Ronacher."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode('-'.join(result))

def cleanID(ID):
    """Adapted from slugify, but allows [,.]"""
    result = []
    for word in _clean_re.split(ID):
        result.extend(unidecode(word).split())
    return unicode(''.join(result))

# TODO: make types a property of Entity?
entity_types = ('work', 'agent', 'concept', 'event')

class Entity(db.Model):
    __tablename__ = 'entity'
    id = db.Column(db.String(64), primary_key=True)
    type = db.Column(db.Enum(*entity_types, name='EntityType'))
    _title =  db.Column('title', db.String(TITLE_MAX))
    slug = db.Column(db.String(SLUG_MAX))

    documents = db.relationship("Document",
                                cascade='all,delete',
                                backref="entity")

    def __init__(self, id, type='work', title=None):
        # TODO: error if id != cleanID(id) ?
        self.id = cleanID(id)
        self.type = type
        self.title = title
        self.slug = slugify(title)[:64] if title else "untitled"

    def __repr__(self):
        return '<Entity(%s), id=%s, title=%s>' %\
            (self.type, self.id, self.title)

    @property
    def active_types(self):
        types = []
        for doc in self.documents:
            if doc.enabled and doc.url:
                types.append(doc.type)

        return types

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.slug = slugify(value)[:64] if value else ""

    title = db.synonym('_title', descriptor=title)
