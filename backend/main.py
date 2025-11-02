from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
from datetime import timedelta
from models import get_db, User, get_password_hash, verify_password, init_db
from auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
import os

# --- Initialize app ---
app = FastAPI(title="Chat Backend with JWT")

# --- Load environment variables ---
load_dotenv()


# --- Database initialization on startup ---
@app.on_event("startup")
def on_startup():
    """Initialize database schema when app starts."""
    try:
        init_db()
    except Exception as e:
        raise RuntimeError(f"Database initialization failed: {e}") from e


# --- CORS configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- OpenAI client ---
client = AsyncOpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
)


# --- Pydantic models ---
class ChatMessage(BaseModel):
    message: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


# --- User registration ---
@app.post("/register")
def register(user: UserCreate, db=Depends(get_db)):
    """Register a new user."""
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "User created"}


# --- User login ---
@app.post("/login")
def login(user: UserLogin, db=Depends(get_db)):
    """Authenticate user and return a JWT token."""
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer", "role": db_user.role}


# --- Chat endpoint ---
@app.post("/chat")
async def chat_endpoint(msg: ChatMessage, current_user=Depends(get_current_user)):
    """Chat with the AI model (requires valid JWT)."""
    if not msg.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        response = await client.chat.completions.create(
            model="gemini-2.5-pro",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": msg.message},
            ],
            stream=False,
        )

        # Handle multiple possible response formats
        ai_reply = None
        try:
            ai_reply = response.choices[0].message.content
        except Exception:
            ai_reply = getattr(response.choices[0], "text", str(response))

        return {"reply": ai_reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {e}")


# --- Local dev run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)