from fasthtml.common import *
from components import common_header, logging, AifEqual, ButtonifLoggedIn, AifEqualToggle, AifNEAND, AifEqualAND, Linked_label
from models import Essay, User
from datetime import datetime, timezone, date

rt = APIRouter(prefix='/essays')

@rt('/') # Supplies url '/essays'
def index(session):
    logging.info("in essays session.get(auth) is {}".format(session.get('auth')))
    nav_items= ['Home', 'Essays']
    essays = Essay.select().where(Essay.authorname == session.get('auth')).order_by(Essay.last_edited.desc())
    essay_links= [ Li(Grid( Linked_label(essay.title, href='/essays/essay/{}'.format(essay.id)), essay.author_fullname,
        AifEqualToggle(session.get('auth'), essay.authorname, 'hide', 'publish', essay.published,  href='/essays/toggle_essay_published/{}'.format(essay.id)),
        AifNEAND(session.get('auth'), essay.authorname, essay.published, title='delete', href='/essays/delete_essay/{}'.format(essay.id)),
        id='essay_link'
        )) for essay in essays]
    return Container(
        common_header(nav_items, 'My Writings', session),
        Hr(),
        Ul(*essay_links, cls="flex space-x-10" ),
        A(Button('New Essay'), href='/essays/new_essay'), style='text-align: right')


@rt
def new_essay(session):
    assert(session.get('auth'))
    author = User.select().where(User.name == session.get('auth')).get()
    assert(author)
    logging.info('author.fullname is {}'.format(author.fullname))
    frm= Form(action=send_new_essay, method='post')(
        Input(type="text", name="title", placeholder="Title"),
        Input(type="hidden", name='authorname', value=author.name),
        Input(type="hidden", name='author_fullname', value=author.fullname),
        Textarea( name="preamble", placeholder="Preamble", rows=5 ),
        Label("Add content later"),
        Button("Create New Essay"))
    return( Titled('New Essay', frm))

@rt
def send_new_essay( title:str, authorname:str, author_fullname:str, preamble:str):
    logging.info('in send_new_essay')
    essay= Essay(title=title, preamble=preamble, content='', authorname=authorname, author_fullname=author_fullname)
    try:
        essay.save()
    except:
        logging.error("Possibly a duplicate title and authorname")
        return RedirectResponse('new_essay')
    logging.info('in send_new_essay, essay is {}'.format(essay.id))
    return Redirect('edit-essay-content/{}'.format(essay.id))

@rt('/delete_essay/{essay_id}')
def delete_essay(essay_id:int):
      logging.info('in delete_essay id is {}'.format(essay_id))
      essay= Essay.get_by_id(essay_id)
      logging.info('in delete_essay essay is {}'.format(essay.title))
      msg= "DELETING '{}'".format(essay.title)
      frm = Form(action=send_delete_essay, method='post')(
        Hidden(essay_id, name='essay_id'),
        Button('Delete'),
        Span(id="error", style="color:red")
      )
      return Titled(msg, frm)

@rt
def send_delete_essay(essay_id:int):
    logging.info("in send_delete_essay essay_id is {}".format(essay_id))
    essay= Essay.get_by_id(essay_id)
    if essay.delete_instance():
          logging.info('Essay has been deleted')
    return RedirectResponse('/essays')

@rt
def toggle_essay_published(id:int):
    essay= Essay.get_by_id(id)
    essay.published= not(essay.published)
    essay.save()
    return RedirectResponse('/essays')

#OK
@rt("/edit-essay-header/{essay_id}")
def get(essay_id:int):
    essay = Essay.get_by_id(essay_id)
    form = Form(action=send_edit_essay_header, method='post')(
        Hidden(essay_id, name='essay_id'),
        Input(type="text", name="title", value=essay.title),
        Textarea( essay.preamble, name="preamble", rows=5 ),
        Button("Apply Changes"),
        Span(id="error", style="color:red"),
        )
    return (Titled('Edit Essay Title or Header', form))

#OK
@rt
def send_edit_essay_header( essay_id:int, title:str, preamble:str):
    essay= Essay.get_by_id(essay_id)
    essay.title= title
    essay.preamble= preamble
    logging.info('edit-essay-header POST, published is now {}'.format(essay.published))
    essay.last_edited= datetime.now(timezone.utc)
    essay.save()
    return RedirectResponse( '/essays/essay/{}'.format(essay_id), status_code=303)

#OK
@rt("/edit-essay-content/{essay_id}")
def get(essay_id: int):
    essay = Essay.get_by_id(essay_id)
    logging.info('In edit_essay_content get {}'.format(essay))
    form=Form(action=send_essay_content, method='post')(
        Hidden(essay_id, name='essay_id'),
        Textarea(essay.content, name='content', rows=20),
        Button("Apply Changes"),
        Span(id="error", style="color:red"),
        )
    return (Titled('Edit Essay Content', form))

#OK
@rt
def send_essay_content(essay_id:int, content:str):
    essay = Essay.get_by_id(essay_id)
    essay.content= content
    essay.last_edited= datetime.now(timezone.utc)
    logging.info('about to save essay {}'.format(essay_id))
    essay.save()
    return RedirectResponse('/essays/essay/{}'.format(essay_id), status_code=303)

@rt('/essay/{id}')
def get(id:int, session):
    nav_items = ['Home', 'Essays']
    essay = Essay.get(id=id)
    return( Container(common_header(nav_items, essay.title, session),
        Hr(Small(essay.preamble)),
        Hr(),
        Div(essay.content, cls="marked"),
        A('Edit Content', href="/essays/edit-essay-content/{}".format(essay.id)))
        )

if __name__ == '__main__':
    pass