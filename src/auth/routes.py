from fastapi import APIRouter, Depends,status
from .schemas import UserCreateModel,UserModel,UserLoginModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token,decode_token,verify_password
from fastapi.responses import JSONResponse
from datetime import timedelta,datetime
from .dependencies import RefreshTokenBearer


REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()
user_service = UserService()

@auth_router.post('/signp',response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data: UserCreateModel, session: AsyncSession= Depends(get_session)):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with email already exists")
    new_user = await user_service.create_user(user_data, session)

    return new_user

@auth_router.post('/login')
async def login_users(login_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user_by_email(email, session)
    print("user==============>",user)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid)
                }
            )

            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
                content ={
                    "message": "Login successfully!",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )
        
    raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Invalid Email or Password")

@auth_router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):

    expiry_timestamp = token_details['exp']

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})
    
    raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail="Invalid or expired token")



