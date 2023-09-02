from fastapi.routing import APIRouter

route = APIRouter(prefix="/api/v1/first")


@route.get("/")
async def temp():
    return {"OK": True}


@route.get("/exc")
async def temp2():
    return {"OK": 1 / 0}


@route.get("/other")
async def temp3():
    return {"OK": True}
