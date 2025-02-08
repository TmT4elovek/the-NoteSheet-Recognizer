from fastapi import FastAPI

from front.front_route import front


app = FastAPI()

app.include_router(front)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True)

    ##! Swagger
    ##! http://(adress)/docs
