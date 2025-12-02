from models import User, Essay
from config import ADMIN_PASSWORD, ADMIN_EMAIL
from essays import rt as rt_essay
from todos import rt as rt_todo
from mycollections import rt as rt_mycollections
from fasthtml.common import *
from datetime import datetime, timezone
from components import common_header, logging, datestring, get_password_hash

#create an admin user if he does not exist
try:
    User.create(name='Admin', email=ADMIN_EMAIL, password=get_password_hash(ADMIN_PASSWORD), fullname='Administrator')
except:
    pass

# The `before` function is a *Beforeware* function. These are functions that run before a route handler is called.
def before(req, sess):
    auth = req.scope['auth'] = sess.get('auth', None)
    if not auth:
        return login_redir

# Beforeware objects require the function itself, and optionally a list of regexes to skip.
bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', '/', '/login', '/send_login', '/register', '/send_register', r'/essay/.*'])

app, rt = fast_app(
    pico=True,
    hdrs= (MarkdownJS(), HighlightJS(langs=['python', 'javascript', 'html', 'css']), Link(rel='stylesheet', href='/static/mystyles.css', type='text/css')),
    before= bware,
    title= "Brian's Stuff",
    )

rt_essay.to_app(app)
rt_todo.to_app(app)
#rt_mycollections.to_app(app)

# Any Starlette response class can be returned by a FastHTML route handler.
login_redir = RedirectResponse('/login', status_code=303)

# FastHTML uses Starlette's path syntax, and adds a `static` type which matches standard static file extensions.
@rt("/{fname:path}.{ext:static}", methods=['GET'])
def static_handler(fname:str, ext:str): return FileResponse(f'{fname}.{ext}')

@rt
def login():
    frm = Form(action=send_login, method='post')(
        Input(id='name', placeholder='Name'),
        Input(id='pwd', type='password', placeholder='Password'),
        Button('login'))
    return Titled("Login", frm, Hr(),
        P("Want to create an Account? ",
        A("Register", href="/register"), cls="mw-480 mx-auto"))


@rt
def send_login(name:str, pwd:str, sess):
    query = User.select().where(User.name == name)
    if not query.exists():
        logging.info("name {} not recognised".format(name))
        return Redirect('/register') # name not recognised
    u= query.get()
    if not u.password == get_password_hash(pwd):
        logging.info("incorrect password for {}".format(u.name))
        return RedirectResponse('/login') # password incorrect
    u.last_login= datetime.now(timezone.utc)
    res = (User.update({User.last_login: datetime.now(timezone.utc)}).where(User.name == name).execute())
    sess['auth'] = name
    sess['uid'] = u.id
    #logging.info("set sess to 'auth': {}, 'uid': {}".format(sess['auth'], sess['uid']))
    return RedirectResponse('/', status_code=303)

@rt
def register():
    frm= Form(action=send_register, method='post')(
        Input(id="name", type="string", placeholder="Username", required=True),
        Input(id="email", type="email", placeholder="Email", required=True),
        Input(id="pword", type="password", placeholder="Password", required=True),
        Input(id="fullname", type="string", placeholder= "Full Name (which will be displayed on your work)"),
        Button('register'))
    return Titled("Register", frm, Hr(),
        P("Already have an account? ",
        A("Login", href="/login")),
    )

@rt
def send_register(name:str, pword:str, email:str, fullname:str):
    if not name or not pword or not email or not fullname:
        return login_redir
    query = User.select().where(User.name == name)
    if query.exists():
        print("We already have a user with that name")
        return RedirectResponse('/login', status_code=303)
    else:
        User.create(name=name, email=email, password=get_password_hash(pword), fullname=fullname, creationDate=datetime.now(timezone.utc))
        logging.info('user {} inserted to database'.format(name))
    return login_redir

@rt("/home")
@rt("/") 
def index(session):
    nav_items=['Essays']
    try:
        if session['auth'] == 'Admin':
            nav_items.append('Todos')
    except:
        session['auth'] = ''

    essays = Essay.select().where(Essay.published).order_by(Essay.last_edited)
    essay_links = [Li( Grid(A(essay.title, href='/essay/{}'.format(essay.id)), essay.author.fullname )) for essay in essays ]
    return Container(
        common_header(nav_items, "Brian's Stuff", session),
        Hr(),
        Ul(*essay_links, cls="flex space-x-10"))

@rt('/essay/{id}')
def get(id:int, session):
    nav_items = ['Home', 'Essays']
    essay = Essay.get(id=id)
    return( Container(common_header(nav_items, "Brian's Stuff", session),
        Hr(),
        Titled(essay.title),
        Hr(Small(essay.preamble)),
        Hr(),
        Div(essay.content, cls="marked"))
        )

@app.get("/logout")
def logout(session):
    if session:
        session['auth'] = ''
    return RedirectResponse('/', status_code=303)

serve()