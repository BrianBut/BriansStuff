from fasthtml.common import *
from components import common_header, logging, ButtonRight, Linked_label
from models import MyCollection, User
from datetime import datetime, timezone, date
from config import PICTURE_PATH

rt = APIRouter(prefix='/collections')

@rt('/') # Supplies url '/collections'
def index(session):
    #logging.info("in collections session.get(auth) is {}".format(session.get('auth')))
    nav_items= ['Home']
    mycollection = MyCollection.select()
    collection_links= [
        Li(Grid(Linked_label(coll.title, href='/collection/item/{}'.format(coll.id)), coll.picturepath))
        for coll in mycollection
        ]
    return Container(
        common_header(nav_items, 'Collections', session),
        Hr(),
        Ul(*collection_links, cls="flex space-x-10" ),
        Div(A(ButtonRight('New Collection', href='/collections/new_collection')))
    )
@rt
def new_collection(session):
    assert(session.get('auth'))
    owner = User.select().where(User.name == session.get('auth')).get()
    assert(owner)
    frm= Form(action=send_new_collection, method='post')(
        Input(type="text", name="title", placeholder="Title"),
        Input(type="text", name="picturepath", placeholder=PICTURE_PATH),
        Input(type="hidden", name='owner_id', value=owner.id),
        ButtonRight("Create New Collection", '/collections/new_collection'),)
    return( Titled('New Collection', frm))

@rt
def send_new_collection( title:str, picturepath:str, owner_id:int ):
    my_collection= MyCollection(title=title, picturepath=picturepath, owner_id=owner_id )
    try:
        my_collection.save()
    except:
        logging.error("Possibly a duplicate collection title or owner_id")
        return RedirectResponse('new_collection')
    logging.info('in send_new_collection, collection is {}'.format(my_collection.id))
    return Redirect('/collections')

if __name__ == '__main__':
    ph = photo_list(BODB_URL)