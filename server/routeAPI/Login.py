from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import os
from dotenv import load_dotenv

import pymongo
from fastapi import APIRouter
apiLogin = APIRouter()

load_dotenv()
mongodb = os.getenv("MONGODB")
client = pymongo.MongoClient(mongodb)
database = client["WebMovie"]
collectionUserData = database["UserData"]

# อ่านค่า secret key จาก environment variable

# เก็บรหัสผ่านเป็นแบบเข้ารหัส
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ตั้งค่าเรียกใช้งานของ OAuth2 Password Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# สร้างฟังก์ชันสำหรับสร้าง JWT token
def createAccessToken(data: dict, expiresDelta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expiresDelta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ["SECRETS_KEY"], algorithm="HS256")
    return encoded_jwt

# สร้าง route สำหรับการล็อกอิน
@apiLogin.post("/login")
async def login_for_accessToken(formData: OAuth2PasswordRequestForm = Depends()):
    user =  collectionUserData.find_one({"username": formData.username})
    if not user or not pwd_context.verify(formData.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    accessTokenExpires = timedelta(minutes=3)
    accessToken = createAccessToken(
        data={"subject": user["username"]}, expiresDelta=accessTokenExpires
    )
    return {"accessToken": accessToken, "tokenType": "bearer","message":"Registration successful."}

# สร้าง route สำหรับเทสการป้องกันสำหรับ route ที่ต้องการ authentication
# @apiLogin.get("/users/me")
# async def read_users_me(token: str = Depends(oauth2_scheme)):
#     payload = jwt.decode(token, os.environ["SECRETS_KEY"], algorithms=["HS256"])
#     username: str = payload.get("subject")
#     if username not in fake_users_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"username": username}

# @apiLogin.get("/users/me")
# async def read_users_me(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, os.environ["SECRETS_KEY"], algorithms=["HS256"])
#         username: str = payload.get("subject")
#         user = collectionUserData.find_one({"username": username})
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#         return {"username": username}
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except jwt.JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
