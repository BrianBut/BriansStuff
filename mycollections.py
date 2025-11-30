from fasthtml.common import *
from components import common_header, logging, ButtonRight, Linked_label
from models import MyCollection, User, Photo
from datetime import datetime, timezone, date
from config import PICTURE_PATH
from os import path

rt = APIRouter(prefix='/collections')

# routines concerning image handling

# prepend PICTURE_PATH to pp
def full_picturepath(pp:str):
    print(PICTURE_PATH)
    res=PICTURE_PATH + pp
    logging.info('Joined path is {}'.format(res))
    return( res )

# Return a list of image files with in path by suffix (e.g) '*.JPG'
def list_image_files(path, suffix):
    fullpath= full_picturepath(path)
    pathgen= Path(fullpath).glob( suffix)
    filelist=[]
    for f in pathgen:
        filelist.append(f)
    return filelist

#Find and store images in the database
def find_photos(collection_id:int, picturepath:str):
    fullpath= full_picturepath(picturepath)
    print("Fullpath: {}/".format(fullpath))
    l=list_image_files(picturepath, '*.JPG') + list_image_files(picturepath, '*.jpg')
    print(l)
    for path in l:
        print(path)
        photos = Photo.select().where(Photo.image_url== path) #FIXME
        name=str(path).split('/')[-1]
        print(name)
        try: # New image url
            photo=Photo(image_url=path, collection=collection_id, caption='', comment='')
            photo.save()
        except:
           pass

#########################################################################################

@rt('/') # Supplies url '/collections'
def index(session):
    nav_items= ['Home']
    mycollection = MyCollection.select()
    collection_links= [
        Li( Grid(
            A(coll.title, href='/collections/item/{}'.format(coll.id)),
            A(coll.picturepath, href='/collections/edit_picturepath/{}'.format(coll.id)),
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

@rt("/edit_picturepath/{collection_id}")
def edit_picturepath(collection_id:int):
    logging.info("in edit_picturepath collection_id is {}".format(collection_id))
    my_collection= MyCollection.get_by_id(collection_id)
    frm= Form(action=send_picturepath, method='post')(
        Hidden(collection_id, name='collection_id'),
        Input(type="text", name="picturepath", value= my_collection.picturepath),
        Button("Apply Changes"),
    )
    return (Titled('Edit Picture Path', frm))

@rt
def send_picturepath(collection_id:int, picturepath:str):
    logging.info("in send_picturepath collection_id is {}".format(collection_id))
    my_collection= MyCollection.get_by_id(collection_id)
    my_collection.picturepath= picturepath
    my_collection.save()
    return Redirect('/collections')


if __name__ == '__main__':

    find_photos(1, '/bodb/gelada')