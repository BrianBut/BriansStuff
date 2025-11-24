from fasthtml.common import *
from datetime import datetime, timezone
from components import logging, common_header, AifEqualToggle
from models import Todo, User

rt = APIRouter(prefix='/todos')

@rt('/')
def todos(session):
    assert(session.get('auth') == 'Admin')
    nav_items=["Home"]
    # List only shows not dones ordered by date notified
    todo_links= [ Grid(A(todo.title, todo.comments, href='/todos/edit_todo/{}'.format(todo.id)),
        A('Mark Done', href='/todos/mark_done/{}'.format(todo.id), style='text-align: right'),
        style='text-align: left'
        ) for todo in Todo.select().order_by(Todo.notified).where(Todo.done == datetime.min)]
    done_links= [ Grid(A(todo.title, todo.comments, href='/todos/edit_todo/{}'.format(todo.id)),
        A('Mark Not Done', href='/todos/mark_not_done/{}'.format(todo.id), style='text-align: right'),
        A('Delete', href='/todos/delete/{}'.format(todo.id), style='text-align: right'),
        style='text-align: left'
        ) for todo in Todo.select().order_by(Todo.notified).where(Todo.done > datetime.min)]
    return Container(
        common_header(nav_items,'Todos', session),
        Hr(),
        Ul(*todo_links),
        A(Button('New Todo'), href='/todos/new_todo', style='text-align: right'),
        Hr(),
        Ul(*done_links),
        )


@rt
def new_todo(session):
    assert(session.get('auth') == 'Admin')
    frm = Form(action=send_todo, method='post')(
        Input(type="text", name="title", placeholder="Title"),
        Textarea(name="comments", placeholder="comments", rows=5),
        Hidden(name="owner", value=session),
        Button("Create New Todo"))
    return (Titled('New Todo', frm))

@rt
def send_todo(session, title:str, comments:str):
    username= session.get('auth')
    user= User.get(User.name==session.get('auth'))
    logging.info("UserId is {}".format(user.id))
    logging.info("in send_new_todo: title is '{}', comments are '{}', owner is {}".format(title, comments, user.id ))
    try:
        todo= Todo.get(title=title)
    except:
        todo= Todo( title=title, comments=comments, owner_id=user.id, last_edited=datetime.utcnow())
    logging.info("todo.title is '{}'".format(todo.title))
    todo.comments= comments
    todo.save()
    logging.info("todo should be saved and redirected to {}".format('/todos/'))
    return RedirectResponse('/todos/', status_code=303)

# correct definition of route with parameter
@rt("/edit_todo/{id}")
def edit_todo(id:int):
    logging.info("in edit_todo/{}".format(id))
    todo = Todo.get(id=id)
    logging.info("todo title is {}".format(todo.title))
    logging.info("todo comments are {}".format(todo.comments))
    frm = Form(action=send_todo, method='post')(
        Hidden(name="title", value=todo.title),
        # Note the way textareas are set
        Textarea( todo.comments, id='comments', rows=5),
        Button("Submit")
    )
    return( Titled('todo',
        H3(U(todo.title)),
        frm))

@rt('/mark_done/{id}')
def get(id:int):
    todo = Todo.get(id)
    todo.done= datetime.utcnow()
    todo.save()
    return RedirectResponse('/todos')


@rt('/mark_not_done/{id}')
def get(id:int):
    todo = Todo.get(id)
    todo.done= datetime.min
    todo.save()
    return RedirectResponse('/todos')

@rt('/delete/{id}')
def get(id:int):
    todo = Todo.get(id)
    todo.delete_instance()
    return RedirectResponse('/todos')



