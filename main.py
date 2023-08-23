import uvicorn
from fastapi import FastAPI
from src.routes import userAuth as user_main
from src.routes import event as event_main
from mongoengine import connect, disconnect
import os
from dotenv import load_dotenv
from src.services.userAuth import signup, NewUser

load_dotenv()

app = FastAPI()

connect(os.environ.get("DATABASE_NAME"), host=os.environ.get("MONGODB_URL"))
app.include_router(user_main.router)
app.include_router(event_main.router)

def admin_signup():
    try:
        admin = NewUser(email = os.environ.get("ADMIN_EMAIL"), username = os.environ.get("ADMIN_USERNAME"), password = os.environ.get("ADMIN_PASSWORD"))
        result_admin = signup(admin)
    except Exception as e:
        print(e)

@app.on_event("startup")
async def on_startup():
    admin_signup()

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
    print("running")
