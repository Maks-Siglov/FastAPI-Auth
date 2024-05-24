from dataclasses import dataclass

from fastapi import Query


@dataclass
class AdminQueryParams:
    user_id: int | None = Query(None, description="User ID")
    email: str | None = Query(None, description="User Email")
    is_active: bool | None = Query(None, description="User Active Status")
    order_by: str | None = Query(None, description="Order by User")
    desc: bool | None = Query(None, description="User descending order by")
