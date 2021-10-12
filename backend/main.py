import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.events import createStartAppHandler, createStopAppHandler
from app.config import PORT, DEBUG, FRONTEND_URL, LOGGING_LEVEL, RELOAD
from app.logging import setup_logging

from routes.auth import router as member_router
from routes.bot import router as bot_router
from routes.api import router as api_router

from app.auth import Authorization

apiAuthHandler = Authorization(type="jwt")
botAuthHandler = Authorization(type="bot")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=RELOAD, debug=DEBUG)

app = FastAPI(debug=True, logging_level=LOGGING_LEVEL)

origins = [FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(member_router, tags=["auth"], prefix="/auth")
app.include_router(
    bot_router,
    tags=["bot"],
    prefix="/bot",
    dependencies=[Depends(botAuthHandler.authenticateUser)],
)
app.include_router(
    api_router,
    tags=["Api"],
    prefix="/api",
    dependencies=[Depends(apiAuthHandler.authenticateUser)],
)

app.add_event_handler("startup", createStartAppHandler(app))
app.add_event_handler("shutdown", createStopAppHandler(app))


@app.get("/", tags=["Root"], response_description="Hello World")
async def read_root():
    return {"message": "Hello World"}
