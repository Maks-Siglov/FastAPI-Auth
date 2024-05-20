from pydantic import BaseModel


class UserBalanceSchema(BaseModel):
    user_id: int
    balance: int


class AmountSchema(BaseModel):
    amount: int
