from fastapi.routing import APIRouter

route = APIRouter(prefix="/first")


@route.get("/")
async def temp():
    return {"OK": True}
