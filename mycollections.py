from fasthtml.common import *
from components import common_header, logging, ButtonRight, Linked_label
from models import MyCollection, User
from datetime import datetime, timezone, date
from config import PICTURE_PATH

rt = APIRouter(prefix='/collections')

@rt('/') # Supplies url '/collections'
def index(session):
    nav_items= ['Home']
    mycollection = MyCollection.select()
    collection_links= [
        Li( Grid(
            A(coll.title, href='/collections/item/{}'.format(coll.id)),
            A(coll.picturepath, href='/collections/edit/picturepath/{}'.format(coll.id)),
            )
        ) for coll in mycollection
        ]
    return Container(
        common_header(nav_items, 'Collections', session),
        Hr(),
        Ul(*collection_links, cls="flex space-x-10" ),
        Div(A(ButtonRight('New Collection', href='/collections/new_collection')))
    )

#creates a new collection
@rt
def new_collection(session):
    frm= Form(action=send_new_collection, method='post')(
        Input(type="text", name="title", placeholder="Title"),
        Input(type="text", name="picturepath", placeholder=PICTURE_PATH),
        Input(type="hidden", name='owner_id', value=session.get('uid')),
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

# Find .JPG and .jpg in picture path and create photo records of them
def find_photos(picturepath):
    pathlist = Path(picturepath).glob('**/*.jpg')


if __name__ == '__main__':
    # make a list of all photos in collection.picturepath

    mycollection = MyCollection.select()
    for coll in mycollection:
        print('title: ', coll.title, coll.picturepath )
        print('owner: ', coll.owner.name )
