from fasthtml.common import *
from components import common_header, logging
from models import MyCollection, User
from datetime import datetime, timezone, date

rt = APIRouter(prefix='/collections')

@rt('/') # Supplies url '/collections'
def index(session):
    logging.info("in collections session.get(auth) is {}".format(session.get('auth')))
    nav_items= ['Home']
    mycollection = MyCollection.select()
    collection_links= [ Li(Grid(coll.title)) for coll in mycollection ]
    return Container(
        common_header(nav_items, 'Collections', session),
        Hr(),
        Ul(*collection_links, cls="flex space-x-10" ),
        A(Button('New Collection'), href='/collections/new_collection'))

@rt
def new_collection(session):
    assert(session.get('auth'))
    owner = User.select().where(User.name == session.get('auth')).get()
    assert(owner)
    frm= Form(action=send_new_collection, method='post')(
        Input(type="text", name="title", placeholder="Title"),
        Input(type="hidden", name='owner_id', value=owner.id),
        Button("Create New Collection"),)
    return( Titled('New Collection', frm))

@rt
def send_new_collection( title:str, owner_id:int ):
    my_collection= MyCollection(title=title, owner_id=owner_id )
    try:
        my_collection.save()
    except:
        logging.error("Possibly a duplicate collection title or owner_id")
        return RedirectResponse('new_collection')
    logging.info('in send_new_collection, collection is {}'.format(my_collection.id))
    return Redirect('/collections')