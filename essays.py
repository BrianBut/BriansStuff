from fasthtml.common import *
from components import common_header, logging, AifEqual, ButtonifLoggedIn, AifEqualToggle
from models import Essay, User
from datetime import datetime, timezone, date

rt = APIRouter(prefix='/essays')

@rt("/")
def index(session):
    logging.info("in essays session.get(auth) is {}".format(session.get('auth')))
    nav_items= ['Home', 'Essays']
    essays = Essay.select().where(Essay.authorname == session.get('auth')) # TODO ORDER BY last_edited",
    essay_links= [ Li(Grid(A(essay.title, href='/essays/essay/{}'.format(essay.essay_id)), essay.author_fullname,
        AifEqual( session.get('auth'), essay.authorname, 'Edit', href='/essays/edit_essay/{}'.format(essay.essay_id)),
        AifEqualToggle(session.get('auth'), essay.authorname, 'hide', 'publish', essay.published, href='/essays/toggle-essay-published/{}'.format(essay.essay_id)),
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

# This replaces the old post route
@rt
def send_new_essay( title:str, authorname:str, author_fullname:str, preamble:str):
    logging.info('in send_new_essay')
    essay= Essay(title=title, preamble=preamble, content='', authorname=authorname, author_fullname=author_fullname)
    essay.save()
    # recover the id of the newly created record
    essay= Essay.select().where((Essay.title == title) and (Essay.authorname == authorname))
    assert(essay)
    logging.info('in send_new_essay, essay is {}'.format(essay.get()))
    return RedirectResponse('essay/{}'.format(essay.get()))
'''
@rt('/toggle-essay-published/{essay_id}')
def get(essay_id:int):
    ess= essays[essay_id]
    ess['published'] = not int(ess['published']) # Test this
    essays.upsert(ess)
    return Redirect('/essays')
'''
@rt('/essay/{essay_id}') # on /essays/essay/10
def get(essay_id:int, session):
    nav_items = ['Home', 'Essays']
    essay = Essay.get(essay_id=essay_id)
    logging.info('in essay, essay is {}'.format(essay))
    if session.get('auth'):
        cts= Container(common_header(nav_items, essay.title, session),
        Hr(Div(Small(essay.preamble))),Hr(),
        Div(essay.content, cls="marked"),
        Grid(A('Edit Preamble', href='/essays/edit-essay-header/{}'.format(essay_id)), A('Edit Content', href='/essays/edit-essay-content/{}'.format(essay_id))))
    else:
        cts = Container(common_header(nav_items, essay.title, session),
        Hr(Small(essay['preamble'])),
        Hr(essay['content'], cls="marked"))
    return (cts)

@rt("/edit_essay/{essay_id}")
def get(essay_id:int):  # Dont forget to set type
    ey = Essay.get(essay_id=essay_id)
    logging.info("result is {}".format(ey))
    return Container(H2(ey.title, H5(ey.preamble,
        P(ey.content),
        Grid(
        A('Edit Essay Header', href='/essays/edit-essay-header/{}'.format(essay_id)),
            A('Edit Essay Content', href='/essays/edit-essay-content/{}'.format(essay_id)),))
    ))

# Broken
@rt("/edit-essay-header/{essay_id}")
def get(essay_id:int):
    essay = Essay.get(essay_id=essay_id)
    return(Titled('Edit Essay Header',
        Form(Input(type="text", name="title", value=essay.title),
        Textarea( essay.preamble, name="preamble", rows=5 ),
        Button("Submit", type="submit",  method='post'))))

def send_edit_essay_header( essay_id:int, title:str, preamble:str):
    essay= Essay.get(essay_id=essay_id)
    essay.title= title
    essay.preamble= preamble
    logging.info('edit-essay-header POST, published is now {}'.format(essay['published']))
    essay.last_edited= datetime.now(timezone.utc)
    essay.save()
    return RedirectResponse( url='essays/essay/{}'.format(essay_id), status_code=303)

#OK
@rt("/edit-essay-content/{essay_id}")
def get(essay_id: int):
    essay = Essay.get(essay_id=essay_id)
    logging.info('In edit_essay_content get {}'.format(essay))
    form=Form(action=send_essay_content, method='post')(
        Hidden(essay_id, name='essay_id'),
        Textarea(essay.content, name='content', rows=20),
        Button("Submit Changes"),
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