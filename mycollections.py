#Work in progress - not complete

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
    print("picturepath is: {}, Fullpath is: {}/".format(picturepath, fullpath))
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

def name_from_path( path:str):
    spl=path.split('/')
    return(spl[-1])

#########################################################################################

@rt('/') # Supplies url '/collections'
def index(session):
    nav_items= ['Home']
    mycollection = MyCollection.select()
    collection_links= [
        Li( Grid(
            A(coll.title, href='/collections/c_item/{}'.format(coll.id)),
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
        Input(type="text", name="picturepath", value=PICTURE_PATH),
        Input(type="hidden", name='owner_id', value=session.get('uid')),
        ButtonRight("Create New Collection", '/collections/new_collection'),)
    return( Titled('New Collection', frm))

@rt
def send_new_collection( title:str, picturepath:str, owner_id:int ):
    logging.info("In send_new_collection picturepath is {}".format(picturepath))
    my_collection= MyCollection(title=title, picturepath=picturepath, owner_id=owner_id )
    assert( my_colection.title)
    assert( my_collection.picturepath)
    try:
        my_collection.save()
    except:
        logging.error("Why the failure to save")
        return RedirectResponse('new_collection')
    logging.info('in send_new_collection, collection is {}'.format(my_collection.id))
    # update the photos table
    find_photos(my_collection.id, mycollection.picturepath)
    return Redirect('/collections')

@rt("/c_item/{collection_id}")
def c_item(collection_id:int):
    logging.info("in collections/c_item collection_id is {}".format(collection_id))
    photos= Photo.select().where(Photo.collection_id == collection_id)  # .order_by?
    c_item_links= [
        Li( Grid(
            A(photo.id, href='/collections/view/{}'.format(photo.id)),
            A(name_from_path(photo.image_url), href='/collections/view/{}'.format(collection_id)),
            A(photo.collection_id, href='/collections/edit_picturepath/{}'.format(collection_id)),
            )
        ) for photo in photos
        ]
    return Container(
        #common_header(nav_items, 'Photos', session),
        Hr(),
        Ul(*c_item_links, cls="flex space-x-10" ),
        )

# View and edit an item in the collection
@rt("/view/{photo_id}")
def view(photo_id:int, session):
    nav_items= ['Home', 'Collections']
    photo= Photo.get_by_id(photo_id)
    logging.info("photo.id is {} with url {}".format(photo.id, photo.image_url))
    return Container(
        common_header('', 'Collection Item', session),
        Hr(),
        Img(src=photo.image_url),
        #A(ButtonRight('New Image', '/essays/new_essay'))
        )


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

    find_photos(1, 'gelada')