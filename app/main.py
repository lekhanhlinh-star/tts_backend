import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from utils.database import Base,engine
from fastapi import FastAPI
from routes.user import user_router
from routes.voice import voice_router
from routes.story import story_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các origin
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các method
    allow_headers=["*"],  # Cho phép tất cả các headers
)
app.include_router(user_router)
app.include_router(story_router)
app.include_router(voice_router)
@app.on_event("startup")
def startup():
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__=="__main__":
    import uvicorn
    uvicorn.run(app=app)