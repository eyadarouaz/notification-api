from fastapi import Header, HTTPException
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings

ALGORITHM = "HS256"


class TokenData(BaseModel):
    user_id: int


async def get_current_user(authorization: str = Header(...)) -> TokenData:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token missing user ID")
        return TokenData(user_id=int(user_id))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
