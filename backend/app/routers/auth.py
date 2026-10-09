from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_id,
    get_current_admin
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# -------------------------
# Register
# -------------------------

@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check whether email already exists
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    }


# -------------------------
# Login
# -------------------------

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        existing_user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# -------------------------
# Protected route
# -------------------------

@router.get("/protected")
def protected_route(
    user_id: int = Depends(get_current_user_id)
):

    return {
        "message": "You are authenticated!",
        "user_id": user_id
    }


# -------------------------
# Admin test route
# -------------------------

@router.get("/admin-test")
def admin_test(
    admin: User = Depends(get_current_admin)
):

    return {
        "message": "You have admin access!",
        "user_id": admin.id,
        "role": admin.role
    }