# File for reusable FastHtml components
from fasthtml.common import *
from datetime import datetime, timezone
from functools import wraps
import hashlib
#from database import db, users
from config import SALT
import logging

logging.basicConfig(filename='/home/brian/briansstuff.log', level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

def get_password_hash(plain_password):
    pwd_salt = plain_password + SALT
    hashed_password = hashlib.sha256(pwd_salt.encode())
    return hashed_password.hexdigest()

# Creating a basic authentication decorator
def basic_auth(f):
    @wraps(f)
    def wrapper(session, *args, **kwargs):
        if "auth" not in session:
            return Response('Not Authorized', status_code=401)
        return f(session, *args, **kwargs)
    return wrapper

# comvert a datetime string in iso format to a date string
def datestring(dts):
    dt= datetime.fromisoformat(dts)
    date=dt.date()
    return date.strftime("%a %d %b %Y")

# The original common header
def common_header1(nav_items: list[str], title, session):
    if session.get('auth'):
        pass
        #current_user=users[session.get('auth')]
    else:
        current_user=None
    #logger.info("in 'common header' current user is {}".format(current_user))
    buttons= [(A(Button(item), href=f"/{item}/".lower())) for item in nav_items]
    if current_user:
        buttons.append(A(Button(current_user['username']), href='/logout'))
    else:
        buttons.append(A(Button('Login'), href='/login'))
    return Container( # for margins
        Nav( *buttons ),
        #Br(),
        Header(style='text-align: center')( H1(title) )
    )

# Version with title in the nav
def common_header(nav_items: list[str], title, session):
    buttons= [(A(Button(item), href=f"/{item}/".lower())) for item in nav_items]
    if session.get('auth'):
        try:
            current_user = users[session.get('auth')]
        except:
            current_user = '?'
        buttons.append(A(Button(current_user['name']), href='/logout'))
    else:
        buttons.append(A(Button('Login'), href='/login'))
    buttons.insert(0, H1(title))
    return Container( Nav( *buttons ),)

def AifEqual( var1, var2, title, href ):
    logging.info("var1 is {}, var2 is {}".format(var1,var2))
    if var1 and  var2:
        if var1 == var2:
            return A(title, href=href)

def AifEqualToggle( var1, var2, title1, title2, toggle_value, href):
    if var1 and var2:
        if var1 == var2:
            if toggle_value:
                return A(title1, href=href)
            else:
                return A(title2, href=href)

'''
def AifNE( var1, var2, title, href ):
    if var1 != var2:
        return A(title, href=href)

def AifExists(var, title, target):
    if var:
        return A( title, href=target)
    return
'''

def ButtonifLoggedIn( var1, style, title, href):
    logging.info("In ButtonifEqual var1 is {}".format(var1))
    if var1:
        return A(Button(title), href=href)

    

if __name__ == '__main__':
    dt = datetime.now(timezone.utc)
    logging.info("datetime is {}".format(dt))
    logging.info("date is {}".format(dt.date()))
    print(dt.strftime("%a %d %b %Y"))

    print(datestring('2025-11-05 02:31:14.620199+00:00'))
