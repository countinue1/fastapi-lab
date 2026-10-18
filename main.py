from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException

app = FastAPI()

@app.get("/")
def hello():
    return{"msg":"hello"}
@app.get("/user/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

@app.get("/search")
def search(q: str, limit: int = 10):
    return {"q": q,"limit": limit}

@app.post("/items")
def create_item(item: Item):
    return item

fake_db = {1:{"name":"键盘","price": 299.0}}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not fonud")
    return fake_db[item_id]

class Todo(BaseModel):
    title: str
    done: bool = False

todos= {}
下一个id = 1

@app.post("/todos",status_code=201)
def create_todo(todo: Todo):
    global 下一个id
    新待办 = {"id": 下一个id, "title": todo.title, "done": todo.done}
    todos[下一个id] = 新待办
    下一个id += 1
    return 新待办

@app.get("/todos")
def list_todos():
    return list(todos.values())


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="todo not found")
    return todos[todo_id]
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: Todo):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    todos[todo_id] = {"id": todo_id, "title": todo.title, "done": todo.done}
    return todos[todo_id]

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not fonund")
    del todos[todo_id]
    return {"message": "deleted"}    
