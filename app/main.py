from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="我的代办 API")

#定义数据长啥样
class TodoCreate(BaseModel):
    title: str
    done: bool = False

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
#强制pydantic立即解析模型
TodoCreate.model_rebuild()
TodoUpdate.model_rebuild()

#用内存字典暂存数据
todos = {}
counter = 0

#路由根目录
@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API"}

#新增待办（post）
@app.post("/todos",status_code=201)
def create_todo(item: TodoCreate):
    global counter
    counter += 1
    todos[counter] = {"id": counter, "title": item.title, "done": item.done}
    return todos[counter]

#查询所有待办（get）
@app.get("/todos")
def list_todos():
    return list(todos.values())

#修改待办（put）
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, item: TodoUpdate):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    if item.title is not None:
        todos[todo_id]["title"] = item.title
    if item.done is not None:
        todos[todo_id]["done"] = item.done
    return todos[todo_id]

#删除待办（delete）
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todos.pop(todo_id)