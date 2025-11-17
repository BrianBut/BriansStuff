from peewee import *
from datetime import datetime, timezone
from config import DB_URL

db = SqliteDatabase(DB_URL)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = AutoField()
    name = CharField(unique=True)
    password = CharField()
    email = CharField()
    fullname = CharField()
    creation_date = DateField(default=datetime.now)
    last_login = DateTimeField(null=True)

    #@classmethod        # untested
    #def get_as_dict(cls, expr):
    #    query = cls.select().where(expr).dicts()
    #    return query.get()

# I've opted for a string for authorname to minimise the number of queries in the homepage
class Essay(BaseModel):
    id = AutoField()
    title = CharField()
    preamble=TextField()
    content=TextField()
    authorname = CharField()
    author_fullname=CharField()
    creation_date=DateField(default=datetime.now(timezone.utc))
    last_edited=DateField(null=True)
    published=BooleanField(default=False)

    class Meta:
        indexes = ((('title', 'authorname'), True),)

class Todo(BaseModel):
    id = AutoField()
    title = CharField(unique=True)
    description = TextField(default='?')
    comments = TextField(null=True)
    notified = DateTimeField(default=datetime.now(timezone.utc))
    done = BooleanField(default=False)

db.connect()
db.create_tables([User, Essay, Todo])

