from fastapi.routing import APIRouter

route = APIRouter(prefix="/api/t1/second")


@route.get("/")
async def temp():
    return {"OK": True}


@route.get("/exc")
async def temp2():
    return {"OK": 1 / 0}
