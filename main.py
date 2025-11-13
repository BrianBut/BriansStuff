from peewee import *
from models import User
#from database import db, users, get_password_hash
from config import ADMIN_PASSWORD, ADMIN_EMAIL
from essays import rt as rt_essay
#from todos import todos, rt as rt_todo
from fasthtml.common import *
from datetime import datetime, timezone
from components import common_header, basic_auth, logging, datestring, get_password_hash

#create admin user if he does not exist
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
bware = Beforeware(before, skip=[r'/favicon\.ico', r'/static/.*', r'.*\.css', '/', '/login', '/send_login', '/register', '/send_register', '/essays'])

app, rt = fast_app(
    pico=True,
    hdrs= (MarkdownJS(), HighlightJS(langs=['python', 'javascript', 'html', 'css']), Link(rel='stylesheet', href='/mystyles.css', type='text/css')),
    before= bware,
    )

rt_essay.to_app(app)
#rt_todo.to_app(app)

# Any Starlette response class can be returned by a FastHTML route handler.
login_redir = RedirectResponse('/login', status_code=303)

# FastHTML uses Starlette's path syntax, and adds a `static` type which matches standard static file extensions. You can define your own regex path specifiers -- for instance this is how `static` is defined in FastHTML `reg_re_param("static", "ico|gif|jpg|jpeg|webm|css|js|woff|png|svg|mp4|webp|ttf|otf|eot|woff2|txt|xml|html")`
# Provide param to `rt` to use full Starlette route syntax.
@rt("/{fname:path}.{ext:static}", methods=['GET'])
def static_handler(fname:str, ext:str): return FileResponse(f'{fname}.{ext}')

@rt
def login():
    frm = Form(action=send_login, method='post')(
        # Tags with a `name` attr will have `name` auto-set to the same as `id` if not provided
        Input(id='name', placeholder='Name'),
        Input(id='pwd', type='password', placeholder='Password'),
        Button('login'))
    return Titled("Login", frm, Hr(),
        P("Want to create an Account? ",
        A("Register", href="/register"), cls="mw-480 mx-auto"))


@rt
def send_login(name:str, pwd:str, sess):
    logging.info("in send_login: name is {}, pwd is {}".format(name,pwd))
    if not name or not pwd: return login_redir
    query = User.select().where(User.name == name)
    if not query.exists():
        return Redirect('/register') # name not recognised
    logging.info("query is {}".format(query))
    u= query.get()
    logging.info("u is {}".format(u.name))
    if not u.password == get_password_hash(pwd):
        logging.info("incorrect password for {}".format(u.name))
        return RedirectResponse('/login') # password incorrect
    u.last_login= datetime.now(timezone.utc)
    res = (User
           .update({User.last_login: datetime.now(timezone.utc)})
           .where(User.name == name)
           .execute())

    logging.info("res is {}".format(res))
    #sess['auth'] = u['name']
    return RedirectResponse('/', status_code=303)

'''
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
    try: u= users[name]
    except NotFoundError: (
        users.insert(name=name, password=get_password_hash(pword), email=email, fullname=fullname, creation_date=datetime.now(timezone.utc), last_login=datetime.min),
        logging.info('user {} inserted to database'.format(name))
    )
    return RedirectResponse('/login', status_code=303)
'''
@rt("/home")
@rt("/") 
def index(session):
    nav_items=['Essays'] # also 'Birds' etc
    title="Brian's Stuff"
    logging.info("in index session.get('auth') is {}".format(session.get('auth')))
    if session.get('auth') == 1:
        nav_items.append('Todos')
    #eys = db.q("SELECT * FROM essays WHERE published=1 ORDER BY last_edited")
    eys= []
    essay_links= []
    for ey in eys:
        essay_links.append(
        Li(
            Grid(
            A(ey['title'], href='/essay/{}'.format(ey['essay_id'])),
            I(ey['author_fullname']),
            Sub(datestring(ey['creation_date']))
            )
        )
        )
    #logging.info("essay_links is {}".format(essay_links))
    #logging.info("result is {}".format(eys))
    logging.info('nav_items is {}'.format(nav_items))
    cts = Container(
        common_header(nav_items, title, session ),
        Ul(
            *essay_links,
            cls="flex space-x-10"
        )
    )
    return cts
'''
'''
@app.get("/logout")
def logout(session):
    if session:
        session['auth'] = ''
    return RedirectResponse('/', status_code=303)

serve()