from fastapi import FastAPI

from app_project.api.v1.routes import router

app = FastAPI()
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
