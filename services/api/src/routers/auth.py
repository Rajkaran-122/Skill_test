from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.core.security import create_access_token

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Generate JWT token. 
    Accepts application/x-www-form-urlencoded credentials.
    """
    # Demo static credentials
    if form_data.username == "admin" and form_data.password == "admin":
        access_token = create_access_token(
            data={"sub": form_data.username, "role": "admin"}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
