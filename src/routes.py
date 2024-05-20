from fastapi import APIRouter

from admin.views import admin_router
from auth.views import auth_router
from balance.views import balance_router

api_router_v1 = APIRouter(prefix="/v1")

api_routers_v1 = (auth_router, admin_router, balance_router)

for router in api_routers_v1:
    api_router_v1.include_router(router)
