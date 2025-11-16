from fasthtml.common import *
from components import common_header, logging, AifEqual, ButtonifLoggedIn, AifEqualToggle
from models import Essay, User
from datetime import datetime, timezone, date

rt = APIRouter(prefix='/essays')

@rt("/") # Supplies url '/essays'
def index(session):
    logging.info("in essays session.get(auth) is {}".format(session.get('auth')))
    nav_items= ['Home', 'Essays']
    essays = Essay.select().where(Essay.authorname == session.get('auth')) # TODO ORDER BY last_edited",
    essay_links= [ Li(Grid(A(essay.title, href='/essays/essay/{}'.format(essay.id)), essay.author_fullname,
        #AifEqual( session.get('auth'), essay.authorname, 'Edit', href='/essays/edit_essay/{}'.format(essay.essay_id)),
        AifEqualToggle(session.get('auth'), essay.authorname, 'hide', 'publish', essay.published, href='/essays/toggle-essay-published/{}'.format(essay.id)),
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
    return Redirect('essay/{}'.format(essay.id))

@rt('/toggle-essay-published/{id}')
def get(id:int):
    essay= Essay.get_by_id(id)
    essay.published= not(essay.published)
    essay.save() #OK
    return RedirectResponse('/essays')

@rt('/essay/{id}')
def get(id:int, session):
    nav_items = ['Home', 'Essays']
    essay = Essay.get(id=id)
    logging.info('in essay, essay is {}'.format(essay))
    if session.get('auth'):
        cts= Container(common_header(nav_items, essay.title, session),
        Hr(Div(Small(essay.preamble))),Hr(),
        Div(essay.content, cls="marked"),
        Grid(A('Edit Preamble', href='/essays/edit-essay-header/{}'.format(essay.id)), A('Edit Content', href='/essays/edit-essay-content/{}'.format(essay.id))))
    else:
        cts = Container(common_header(nav_items, essay.title, session),
        Hr(Small(essay['preamble'])),
        Hr(essay['content'], cls="marked"))
    return (cts)

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

if __name__ == '__main__':
    pass