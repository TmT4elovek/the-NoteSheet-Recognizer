from fastapi import FastAPI
from backend.back_route import back



app = FastAPI()
app.include_router(back)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)

    ##! Swagger
    ##! http://(adress)/docs
