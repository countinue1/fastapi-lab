import os 
import asyncio
import redis
from fastapi import FastAPI
import pymysql
import httpx, json
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi.responses import StreamingResponse





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

# @app.post("/todos",status_code=201)
# def create_todo(todo: Todo):
#     global 下一个id
#     新待办 = {"id": 下一个id, "title": todo.title, "done": todo.done}
#     todos[下一个id] = 新待办
#     下一个id += 1
#     return 新待办

# @app.get("/todos")
# def list_todos():
#     return list(todos.values())


# @app.get("/todos/{todo_id}")
# def get_todo(todo_id: int):
#     if todo_id not in todos:
#         raise HTTPException(status_code=404, detail="todo not found")
#     return todos[todo_id]
# @app.put("/todos/{todo_id}")
# def update_todo(todo_id: int, todo: Todo):
#     if todo_id not in todos:
#         raise HTTPException(status_code=404, detail="Todo not found")
#     todos[todo_id] = {"id": todo_id, "title": todo.title, "done": todo.done}
#     return todos[todo_id]

# @app.delete("/todos/{todo_id}")
# def delete_todo(todo_id: int):
#     if todo_id not in todos:
#         raise HTTPException(status_code=404, detail="Todo not fonund")
#     del todos[todo_id]
#     return {"message": "deleted"}    


os.makedirs("uploads", exist_ok=True)

# @app.post("/upload")
# async def upload(file: UploadFile):
#     内容 = await file.read()
#     with open(f"uploads/{file.filename}", "wb") as f:
#         f.write(内容)
#     return {"filename": file.filename, "size": len(内容)}



async def 假装生成():
    文本 = "你好，我是流式输出，一个字一个字来。就像打字机一眼，慢慢出现。"
    for 字 in 文本:
        yield 字
        await asyncio.sleep(0.5)


@app.get("/stream")
async def stream():
    return StreamingResponse(假装生成(), media_type="text/plain")

async def 流式问模型(问题: str):
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream(
             "POST","http://localhost:11434/api/chat",
             json={"model":"qwen2.5:7b",
                   "messages":[{"role":"user", "content": 问题}],
                   "stream":True},
                   ) as resp:
                       async for 行 in resp.aiter_lines():
                           if 行.strip():
                               数据 = json.loads(行)
                               片段 = 数据.get("message", {}).get("content", "")
                               if 片段:
                                   yield 片段


@app.get("/ask")
async def ask(q: str):
    return StreamingResponse(流式问模型(q), media_type="text/plain")
                
                                 
#数据库的连接与操作
def get_conn():
    return pymysql.connect(
        host = 'localhost',
        user = 'root',
        password = '12345678901313zk',
        database = 'fastapi_lab',
        cursorclass = pymysql.cursors.DictCursor
    )
#获取数据库连接
@app.get("/todos")
def get_todos():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("select * from todos;")
    rows = cursor.fetchall()
    conn.close()
    return rows

#在数据库上进行查找
# @app.get("/todos/{todo_id}")
# def get_todo(todo_id: int):
#     conn = get_conn()
#     cursor = conn.cursor()
#     cursor.execute("select * from todos where id = %s;", (todo_id,))
#     row = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     if not row:
#         raise HTTPException(status_code=404, detail="Todo not found")
#     return row


r = redis.Redis(host="localhost", port=6379, decode_responses=True)
#在数据里新增
@app.post("/todos",status_code=201)
def create_todo(todo: Todo):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "insert into todos(title, done) values (%s, %s)",
        (todo.title, todo.done)
    )
    new_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": new_id, "title": todo.title, "done": todo.done}

#put的作用
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: Todo):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE todos SET title = %s, done = %s WHERE id = %s;",
        (todo.title, todo.done, todo_id),
    )
    conn.commit()
    r.delete(f"todo:{todo_id}")
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"id": todo_id, "title": todo.title, "done": todo.done}

#delete的作用
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn =get_conn()
    cursor = conn.cursor()
    cursor.execute("delete from todos where id = %s;", (todo_id,))
    conn.commit()
    r.delete(f"todo:{todo_id}")
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted"}




@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    cached = r.get(f"todo:{todo_id}")
    if cached:
        return json.loads(cached)
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("select * from todos where id = %s;", (todo_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    r.set(f"todo:{todo_id}", json.dumps(row))
    return row



    













