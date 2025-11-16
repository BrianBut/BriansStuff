from fasthtml.common import *
from datetime import datetime
from components import logging, common_header
from models import Todo

rt = APIRouter()

@rt("/todos")
def todos(session):
    assert(session.get('auth') == 'Admin')
    nav_items=["Home"]
    todo_links= [ Li(Grid(A(todo.title, href='/edit_todo/{}'.format(todo.id)), todo.description,
        #AifEqual( session.get('auth'), essay.authorname, 'Edit', href='/essays/edit_essay/{}'.format(essay.essay_id)),
        #AifEqualToggle(session.get('auth'), essay.authorname, 'hide', 'publish', essay.published, href='/essays/toggle-essay-published/{}'.format(essay.essay_id)),
        )) for todo in Todo.select().where(Todo.done == datetime.min)]

    return Container(
        common_header(nav_items, 'Todos', session),
        Hr(),
        Ul(*todo_links, cls="flex space-x-10" ),
        A(Button('New Todo'), href='/todos/new_todo'), style='text-align: right')

@rt("/new_todo")
def new_todo():
    frm = Form(action=send_todo, method='post')(
        Input(type="text", name="title", placeholder="Title"),
        Textarea(name="description", placeholder="Description", rows=5),
        Button("Create New Todo"))
    return (Titled('New Todo', frm))

@rt
def send_todo(title:str, description:str, comments:str):
    logging.info("in send_new_todo: title is {}, description is {}, comments are is {}".format(title, description, comments ))
    todo= Todo( title=title, description=description, comments=comments,)
    todo.save()
    logging.info("todo should be saved {}".format(todo.description))
    return RedirectResponse('/', status_code=303)

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

