from peewee import *
from datetime import datetime
from config import DB_URL, ADMIN_EMAIL, ADMIN_PASSWORD

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

db.connect()
db.create_tables([User])

#create admin user if he does not exist
#try:
#    User.create(name='Admin', email=ADMIN_EMAIL, password=ADMIN_PASSWORD, fullname='Administrator')
#except:
#    pass
