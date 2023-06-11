from fastapi.routing import APIRouter

route = APIRouter(prefix="/api/t1/test")


@route.get("/")
async def temp():
    return {"OK": True}
