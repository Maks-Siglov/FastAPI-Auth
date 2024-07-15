from dataclasses import dataclass

from fastapi import Query


@dataclass
class AdminQueryParams:
    user_id: int | None = Query(None, description="User ID")
    email: str | None = Query(None, description="User Email")
    first_name: str | None = Query(None, description="First Name")
    last_name: str | None = Query(None, description="Last Name")
    is_active: bool | None = Query(None, description="User Active Status")
    order_by: str | None = Query(
        None, description="Field to order by (id, balance, last_activity_at)"
    )
    order_type: str | None = Query("asc", description="Order type (asc, desc)")
