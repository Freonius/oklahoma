from fastapi.routing import APIRouter

route = APIRouter(prefix="/api/v1/first")


@route.get("/")
async def temp():
    return {"OK": True}


@route.get("/other")
async def temp2():
    return {"OK": True}
