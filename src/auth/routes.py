from fastapi import APIRouter, Depends,status, BackgroundTasks
from .schemas import UserCreateModel,UserModel,UserLoginModel,UserBooksModel,EmailModel,PasswordResetRequestModel,PasswordResetConfirmModel
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from .utils import create_access_token,decode_token,verify_password, create_url_safe_token, decode_url_safe_token
from fastapi.responses import JSONResponse
from datetime import timedelta,datetime
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist
from typing import List
from src.db.models import User
from src.errors import UserAlreadyExists, InvalidCredentials, InvalidToken,UserNotFound
from src.mail import mail,create_message
from src.config import Config


REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin','user'])

@auth_router.post('/send_mail')
async def send_mail(emails: EmailModel):
    emails = emails.addresses

    html ="<h1>Welcome to bookly application</h1>"

    message = create_message(
        recipients=emails,
        subject="This is a test message",
        body=html
    )

    await mail.send_message(message)

    return { "message": "Email send successfully"}



@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def create_user_Account(user_data: UserCreateModel, session: AsyncSession= Depends(get_session)):
    email = user_data.email

    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()
    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email":email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your Bookly Account</h1>
    <p> Please click this <a href="{link}">Link</a> to verify your accont</p>
    """

    message = create_message(
        recipients=[email],
        subject="Bookly Account Verification Mail",
        body=html_message
    )

    await mail.send_message(message)

    return {
        "message": "Account Created ! Check email to verify your accont",
        "user": new_user
    }

@auth_router.get('/verify/{token}')
async def verify_user_account(token:str, session: AsyncSession = Depends(get_session)):

    token_data = decode_url_safe_token(token)
    user_email = token_data.get('email')

    if user_email:
        user = await user_service.get_user_by_email(user_email,session)

        if not user:
            raise UserNotFound()
        
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"message": "Error occured during verification!!"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

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
                    'user_uid': str(user.uid),
                    'role': user.role
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
        
    raise InvalidCredentials()

@auth_router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):

    expiry_timestamp = token_details['exp']

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})
    
    raise InvalidToken()

@auth_router.get('/me', response_model=UserBooksModel)
async def get_current_user(user = Depends(get_current_user), _: bool = Depends(role_checker)):
    return user



@auth_router.get('/logout')
async def revoke_token(token_details: dict= Depends(AccessTokenBearer())):

    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message": "Logged Out Successfully!!"
        },
        status_code=status.HTTP_200_OK
    )

@auth_router.post('/password-reset-request')
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">Link</a> to reset your password</p>
    """

    message = create_message(
        recipients=[email], subject="Reset Your Password", body=html_message
    )

    await mail.send_message(message)

    return JSONResponse(
        content={
            "message": "Please check your email for instructios to reset your password"
        },
        status_code=status.HTTP_200_OK
    )


@auth_router.get('/passwod-reset-confirm/{token}')
async def reset_account_password(token:str,passwords: PasswordResetConfirmModel ,session: AsyncSession = Depends(get_session)):

    token_data = decode_url_safe_token(token)
    user_email = token_data.get('email')

    if user_email:
        user = await user_service.get_user_by_email(user_email,session)

        if not user:
            raise UserNotFound()
        
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully"},status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"message": "Error occured during verification!!"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
