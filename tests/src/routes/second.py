from fastapi.routing import APIRouter

route = APIRouter(prefix="/api/t1/second")


@route.get("/")
async def temp():
    return {"OK": True}
