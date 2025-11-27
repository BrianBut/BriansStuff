# File for shared functions and reusable FastHtml components
from fasthtml.common import *
from datetime import date, datetime, timezone
from functools import wraps
import hashlib
from models import User
from config import SALT, LOGFILE
import logging

logging.basicConfig(filename=LOGFILE, level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

def get_password_hash(plain_password):
    pwd_salt = plain_password + SALT
    hashed_password = hashlib.sha256(pwd_salt.encode())
    return hashed_password.hexdigest()

# comvert a datetime string in iso format to a date string
def datestring(dts):
    dt= date.strftime(dts)
    return dt.strftime("%a %d %b %Y")

def common_header(nav_items: list[str], title, session):
    buttons= [(A(Button(item), href=f"/{item}/".lower())) for item in nav_items]
    query = User.select().where(User.name == session.get('auth'))
    if query.exists():
        buttons.append(A(Button(session.get('auth')), href='/logout'))
    else:
        buttons.append(A(Button('Login'), href='/login'))
    buttons.insert(0, H1(title))
    #logging.info("In common_header buttons are {}".format(buttons))
    return Container( Nav( *buttons ),)

#preceeds and interposes hrs between items in a list
def hr_separated( items):
    list= [Hr()]
    for item in items:
        list.append(item)
        list.append(Hr())
    return list

#fixed width link. Text within is left justified - see mystyles.css
def Linked_label( text, href):
    return( Div(A(text, href='{}'.format(href)), id='title_box'))

def AifEqual( var1, var2, title, href ):
    logging.info("var1 is {}, var2 is {}".format(var1,var2))
    if var1 or var2:
        if var1 == var2:
            return A(title, href=href)

def AifEqualAND( var1, var2, condition, title, href):
    logging.info("in AifEqualAND, href is {}".format(href))
    if condition:
        return AifEqual( var1, var2, title, href)

def AifNEAND( var1, var2, condition, title, href):
    if not condition:
        return AifEqualAND( var1, var2, True, title, href)

def AifEqualToggle( var1, var2, title1, title2, toggle_value, href):
    if var1 and var2:
        if var1 == var2:
            if toggle_value:
                return A(title1, href=href)
            else:
                return A(title2, href=href)

def AifNE( var1, var2, title, href ):
    if var1 != var2:
        return A(title, href=href)
'''
def AifExists(var, title, target):
    if var:
        return A( title, href=target)
    return
'''

def ButtonifLoggedIn( var1, style, title, href):
    logging.info("In ButtonifEqual var1 is {}".format(var1))
    if var1:
        return A(Button(title), href=href)

def ButtonRight(title, href):
    return Div(A( Button(title, href='#'), href=href), id='label_right')

if __name__ == '__main__':
    dt = datetime.now(timezone.utc)
    logging.info("datetime is {}".format(dt))
    logging.info("date is {}".format(dt.date()))
    print(dt.strftime("%a %d %b %Y"))

    #print(datestring('2025-11-05 02:31:14.620199+00:00'))
