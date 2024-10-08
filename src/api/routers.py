from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from src.api.v1.admin.routes import router as admin_router
from src.api.v1.balance.routes import router as balance_router
from src.api.v1.users.routes import router as auth_router
from src.db.session import handle_session

http_bearer = HTTPBearer(auto_error=False)

api_router_v1 = APIRouter(
    prefix="/v1", dependencies=[Depends(http_bearer), Depends(handle_session)]
)

api_routers_v1 = (auth_router, admin_router, balance_router)

for router in api_routers_v1:
    api_router_v1.include_router(router)
