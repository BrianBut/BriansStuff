from peewee import *
from datetime import datetime
from config import DB_URL

db = SqliteDatabase(DB_URL)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id= IntegerField()
    name = CharField(unique=True,primary_key=True)
    password= CharField()
    email= CharField()
    fullname= CharField()
    creation_date = DateField(default=datetime.now)
    last_login= DateTimeField(null=True)
        
db.connect()
db.create_tables([User])
