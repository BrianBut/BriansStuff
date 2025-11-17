from fasthtml.common import *
from datetime import datetime
from components import logging, common_header, AifEqualToggle
from models import Todo

rt = APIRouter(prefix='/todos')

@rt('/')
def todos(session):
    assert(session.get('auth') == 'Admin')
    nav_items=["Home"]
    todo_links= [ Grid(A(todo.title, todo.description, todo.comments, href='/todos/edit_todo/{}'.format(todo.id)),
        AifEqualToggle(todo.done, False, 'hide', 'publish', todo.done, href='/essays/toggle-essay-published/{}'.format(todo.id)),
        A('Testing'),
        style='text-align: left'
        ) for todo in Todo.select().where(Todo.done == False)]
    return Container(
        common_header(nav_items,'Todos', session),
        Hr(),
        Ul(*todo_links),
        A(Button('New Todo'), href='/todos/new_todo'), style='text-align: right')

@rt
def new_todo(session):
    assert(session.get('auth') == 'Admin')
    frm = Form(action=send_todo, method='post')(
        Input(type="text", name="title", placeholder="Title"),
        Textarea(name="description", placeholder="Description", rows=5),
        Textarea(name="comments", placeholder="comments", rows=2),
        Button("Create New Todo"))
    return (Titled('New Todo', frm))

@rt
def send_todo(title:str, description:str, comments:str):
    logging.info("in send_new_todo: title is {}, description is {}, comments are is {}".format(title, description, comments ))
    todo= Todo( title=title, description=description, comments=comments,)
    todo.save()
    logging.info("todo should be saved and redirected to {}".format('/todos/'))
    return RedirectResponse('/todos/', status_code=303)

# correct definition of route with parameter
@rt("/edit_todo/{id}")
def edit_todo(id:int):
    logging.info("in edit_todo/{}".format(id))
    todo = Todo.get(id=id)
    frm = Form(action=send_todo, method='post')(
        Input(type="text", name="title", value=todo.title),
        Textarea(name="description", value=todo.description, rows=5),
        Textarea(name="comments", value=todo.comments, rows=5),
        Button("Submit")
    )
    return( Titled('todo', frm))

@rt('/toggle-todo-done/{id}')
def get(id:int):
    todo = Todo.get(id)
    todo.published= not(todo.published)
    todo.save()
    return RedirectResponse('/essays')

