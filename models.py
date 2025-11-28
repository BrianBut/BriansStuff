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

# I've opted to use a string for authorname to minimise the number of queries in the homepage
# It would be possible, but probably pointless, to use author_id field as a foreign key to the User table
# Change this!
class Essay(BaseModel):
    id = AutoField()
    title = CharField()
    preamble=TextField()
    content=TextField()
    author=ForeignKeyField(User, backref='essays')
    creation_date=DateField(default=datetime.now(timezone.utc))
    last_edited=DateField(null=True)
    published=BooleanField(default=False)

# The point of the following constraint is that it should permit two essays written by different people to share the same title.
# It should also allow one author to write many essays. But it raises an error if one author tries to create an essay with the same title as an earlier one.
    class Meta:
        indexes = ((('title', 'author'), True),)

class Todo(BaseModel):
    id = AutoField()
    title = CharField(unique=True)
    comments = TextField(null=True)
    notified = DateTimeField(default=datetime.now(timezone.utc))
    done = DateTimeField(default=datetime.min)
    owner = ForeignKeyField(User, backref='todos')

# Collections of photographs
class MyCollection(BaseModel):
    title = CharField(unique=True)
    owner = ForeignKeyField(User, backref='mycollections')
    picturepath = TextField()

class Photo(BaseModel):
    id = AutoField()
    image_url = TextField(unique=True)
    collection = ForeignKeyField(MyCollection, backref='photos')


db.connect()
db.create_tables([User, Essay, Todo, MyCollection, Photo])

