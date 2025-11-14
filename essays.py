from fasthtml.common import *
from components import common_header, logging, AifEqual, ButtonifLoggedIn, AifEqualToggle
from models import Essay
from datetime import datetime, timezone, date

rt = APIRouter(prefix='/essays')

@rt("/")
def index(session):
    logging.info("in essays session.get(auth) is {}".format(session.get('auth')))
    nav_items= ['Home', 'Essays']
    query = Essay.select().where(Essay.authorname == session['auth'])

    #TODO
    #eys= db.q("SELECT * FROM essays WHERE authorname=? ORDER BY last_edited",(session.get('auth'),))
    essay_links= [ Li(Grid(A(ey['title'], href='/essays/essay/{}'.format(ey['essay_id'])), ey['author_fullname'],
        AifEqual( session.get('auth'), ey['authorname'], 'Edit', href='/essays/edit_essay/{}'.format(ey['essay_id'])),
        AifEqualToggle(session.get('auth'), ey['authorname'], 'hide', 'publish', ey['published'], href='/essays/toggle-essay-published/{}'.format(ey['essay_id'])),
        )) for ey in query]
    logging.info("In essays/index auth is {}.".format(session.get('auth')))
    return Container(
        common_header(nav_items, 'Writings', session),
        Ul(*essay_links, cls="flex space-x-10" ),
        A(Button('New Essay'), href='/essays/new_essay'), style='text-align: right')

@rt
def new_essay(session):
    u= users[session.get('auth')]
    frm= Form(action=send_new_essay, method='post')(
        Input(type="text", name="title", placeholder="Title"),
        Input(type="hidden", name='authorname', value=u['name']),
        Input(type="hidden", name='author_fullname', value=u['fullname']),
        Textarea( name="preamble", placeholder="Preamble", rows=5 ),
        Label("Add content later"),
        Button("Create New Essay"))
    return( Titled('New Essay', frm))

# This replaces the old post route
@rt
def send_new_essay( title:str, authorname:str, author_fullname:str, preamble:str):
    logging.info('in send_new_essay')
    # need to check uniqueness of {authorname,fullname} - database constraints don't seem possible with fastlite
    query = "SELECT * FROM essays WHERE authorname = ? AND title = ? LIMIT 1 ", authorname, title
    print(query)
    ey= db.q(query)
    print(ey)
    #try:
    #    ey= essays.selectone('title=?', (title,))
    #    print(ey)
    #except:
    #    ey= 0
    #if not ey: # empty list or no list
    essays.insert(title=title, authorname=authorname, author_fullname=author_fullname, preamble=preamble, creation_date=datetime.now(timezone.utc), published=False)
    #logging.info('in send_new_essay query is {}'.format(query))
    #ey= db.q(query)[0]
    #ey=essays.selectone('title=?', (title,))
    return RedirectResponse('essays/{}'.format(ey['essay_id']))
'''
#@basic_auth
@rt('/toggle-essay-published/{essay_id}')
def get(essay_id:int):
    ess= essays[essay_id]
    ess['published'] = not int(ess['published']) # Test this
    essays.upsert(ess)
    return Redirect('/essays')

@rt('/essay/{essay_id}') # on /essays/essay/10
def get(essay_id:int, session):
    nav_items = ['Home', 'Essays']
    essay = essays[essay_id]
    if session.get('auth'):
        cts= Container(common_header(nav_items, essay['title'], session),
        Hr(Div(Small(essay['preamble']))),Hr(),
        Div(essay['content'], cls="marked"),
        Grid(A('Edit Preamble', href='/essays/edit-essay-header/{}'.format(essay_id)), A('Edit Content', href='/essays/edit-essay-content/{}'.format(essay_id))))
    else:
        cts = Container(common_header(nav_items, essay['title'], session),
        Hr(Small(essay['preamble'])),
        Hr(essay['content'], cls="marked"))
    return (cts)

@rt("/edit_essay/{essay_id}")
def get(essay_id:int):  # Dont forget to set type
    query= "SELECT * FROM essays WHERE essay_id=?",(essay_id, )
    ey = db.q(query)[0]
    logging.info("result is {}".format(ey))
    return Container(H2(ey['title']), H5(ey['preamble'],
        P(ey['content']),
        Grid(
        A('Edit Essay Header', href='/edit-essay-header/{}'.format(essay_id)),
            A('Edit Essay Content', href='/edit-essay-content/{}'.format(essay_id)),))
    )

#@basic_auth
@rt("/edit-essay-header/{essay_id}")
def get(essay_id:int):
    essay= essays[essay_id]
    return(Titled('Edit Essay Header',
        Form(Input(type="text", name="title", value=essay['title']),
        Textarea( essay['preamble'], name="preamble", rows=5 ),
        Button("Submit", type="submit", hx_post="/edit-essay-header/{}".format(essay_id)))))


#@basic_auth
@rt("/edit-essay-header/{essay_id}")
def post(essay_id:int, title:str, preamble:str):
    essay= essays[essay_id]
    essay['title']= title
    essay['preamble']= preamble
    logging.info('edit-essay-header POST, published is now {}'.format(essay['published']))
    essay['last_edited']= datetime.now(timezone.utc)
    essays.upsert(essay)
    return HttpHeader('HX-Redirect', '/essay/{}'.format(essay_id))


@basic_auth
@rt("/edit-essay-content/{essay_id}")
def get(essay_id: int):
    essay= essays[essay_id]
    logging.info('In edit_essay_header get {}'.format(essay))
    return (Titled('Edit Essay Content',
        Form(
        Textarea(essay['content'], name='content', rows=20),
        Button("Submit", type="submit", hx_post="/edit-essay-content/{}".format(essay_id)),
        Span(id="error", style="color:red"),),
        ))


@basic_auth
@rt("/edit-essay-content/{essay_id}")
def post(essay_id:int, content:str):
    ess= essays[essay_id]
    ess['content']= content
    ess['last_edited']= datetime.now(timezone.utc)
    logging.info('about to upsert essay {}'.format(ess))
    essays.upsert(ess)
    return HttpHeader('HX-Redirect', '/essay/{}'.format(essay_id))

'''

if __name__ == '__main__':
    pass