from fastapi import FastAPI, WebSocket, Depends, HTTPException, Request, BackgroundTasks, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_login import LoginManager #Loginmanager Class
from fastapi_login.exceptions import InvalidCredentialsException #Exception class

from sqlalchemy.orm import Session

import funcs
from model import models, schemas
from model.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
#------------------------security-------------------
SECRET = "secret-key"

manager = LoginManager(SECRET,token_url="/auth/login",use_cookie=True)
manager.cookie_name = "some-name"

DB = {"username":{"password":"qwertyuiop"},
      "tabish":{"password":"hello"},
      "ashish":{"password":"manish"}
    }# unhashed
@manager.user_loader()
def load_user(username:str):
    user = DB.get(username)
    return user

@app.post("/auth/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password
    user = load_user(username)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(
        data={"sub":username}
    )
    resp = RedirectResponse(url="/chat",status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp,access_token)
    return resp

@app.get("/private")
def getPrivateendpoint(_=Depends(manager)):
    return "You are an authentciated user"

@app.get("/",response_class=HTMLResponse)
def loginwithCreds(#request:Request
):
    with open("html/login.html") as f:
        return HTMLResponse(content=f.read())


#---------------security------------------------

# Dependency
def get_db():
    db = SessionLocal()
    try:
        print("updated db")
        yield db
    finally:
        db.close()

def get_sr(i):

    while i < 100:
        i =i+1
        yield i




@app.get("/chat")
def getPrivateendpoint(_=Depends(manager)):
    with open("html/index.html") as f:
        return HTMLResponse(content=f.read())
    






class Notifier:

    def __init__(self,count:int):
        self.connections: list = []
        self.generator = self.get_notification_generator()
        self.count = self.counter(count)
    async def get_notification_generator(self):
        while True:
            message = yield
            msg = message["message"]
            await self._notify(msg)

    def get_members(self):
        try:
            return self.connections
        except Exception:
                return None
    
    async def push(self, msg:str):
        message_body = {"meaage":msg}
        await self.generator.asend(message_body)
    
    
    async def connect(self, websocket: WebSocket,db:Session):
        await websocket.accept()
        init_data = funcs.get_messages(db=db)
        #i =1
        for r in init_data:
            #i= i+1
            mess = r.message
            #print("message    ",mess)
            await websocket.send_text(f"message text was: {mess}")
        if len(self.connections) == 0:
            self.connections =[]
        self.connections.append(websocket)
        print(f"CONNECTIONS : {self.connections}")
    
    
    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)
        print(
            f"CONNECTION REMOVED\nREMAINING CONNECTIONS: {self.connections}"
        )
    
    
    async def _notify(self,message: str):
        living_connections = []
        while len(self.connections) > 0:

            websocket = self.connections.pop()
            await websocket.send_text(message)
            living_connections.append(websocket)
        self.connections = living_connections
    
    def counter(self,i:int|None):
        if i == None:
            i = 0
        while True:
            i = i+1
            yield i


db1 = SessionLocal()
notifier = Notifier(funcs.get_count(db1))
print("notifier")

@app.websocket("/ws2")
async def web_socket_endpoint(
    websocket: WebSocket, background_tasks: BackgroundTasks,db:Session=Depends(get_db),data_set=schemas.data_set,
    #_=Depends(manager),
):
    await notifier.connect(websocket,db)
    try:
        while True:
            data = await websocket.receive_text()
            sr = notifier.count.__next__()
            final_data=data_set(sr=sr,message=data)
            funcs.create_message(db=db, data_mess=final_data)
            
            await notifier._notify((f"{data}"))
    except :
        notifier.remove(websocket)
