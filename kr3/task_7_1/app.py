from enum import Enum

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

app = FastAPI()
security = HTTPBearer()


class Role(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"


ROLE_PERMISSIONS: dict[Role, list[str]] = {
    Role.admin: ["read", "create", "update", "delete"],
    Role.user:  ["read", "update"],
    Role.guest: ["read"],
}

# Simplified in-memory users with static tokens for demo purposes
users_db = {
    "alice": {"username": "alice", "role": Role.admin, "token": "alice-token"},
    "bob":   {"username": "bob",   "role": Role.user,  "token": "bob-token"},
    "carol": {"username": "carol", "role": Role.guest, "token": "carol-token"},
}


class LoginRequest(BaseModel):
    username: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    for user in users_db.values():
        if user["token"] == token:
            return user
    raise HTTPException(status_code=401, detail="Invalid token")


def require_permission(permission: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        role: Role = user["role"]
        if permission not in ROLE_PERMISSIONS.get(role, []):
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' denied for role '{role}'",
            )
        return user
    return checker


@app.post("/login")
def login(request: LoginRequest):
    user = users_db.get(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"access_token": user["token"], "role": user["role"]}


@app.get("/protected_resource")
def read_resource(user: dict = Depends(require_permission("read"))):
    return {
        "message": f"Hello {user['username']}, you can read this resource",
        "role": user["role"],
    }


@app.post("/admin/resource")
def create_resource(user: dict = Depends(require_permission("create"))):
    return {"message": f"Resource created by {user['username']}"}


@app.delete("/admin/resource")
def delete_resource(user: dict = Depends(require_permission("delete"))):
    return {"message": f"Resource deleted by {user['username']}"}
