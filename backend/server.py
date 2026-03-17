from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
import os
import logging
from pathlib import Path
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

app = FastAPI()
api_router = APIRouter(prefix="/api")

# =============== MODELS ===============

class UserSignup(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    batch: Optional[str] = None
    reason: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    full_name: str
    email: str
    role: str
    status: str
    mentorship_access: bool
    advanced_access: bool = False
    batch: Optional[str] = None
    last_login: Optional[str] = None
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class LeadershipMember(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    position: str
    photo_url: Optional[str] = None
    order_number: int
    archived: bool = False
    created_at: str

class LeadershipCreate(BaseModel):
    name: str
    position: str
    photo_url: Optional[str] = None
    order_number: int

class Course(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    description: str
    outline: str
    course_type: str
    photo_url: Optional[str] = None
    archived: bool = False
    order_number: int
    created_at: str

class CourseCreate(BaseModel):
    title: str
    description: str
    outline: str
    course_type: str
    photo_url: Optional[str] = None
    order_number: int

class Module(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    course_id: str
    title: str
    duration: Optional[str] = None
    video_link: Optional[str] = None
    pdf_link: Optional[str] = None
    order_number: int
    archived: bool = False
    created_at: str

class ModuleCreate(BaseModel):
    course_id: str
    title: str
    duration: Optional[str] = None
    video_link: Optional[str] = None
    pdf_link: Optional[str] = None
    order_number: int

class Progress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    module_id: str
    completed: bool
    completed_at: Optional[str] = None

class ProgressUpdate(BaseModel):
    module_id: str
    completed: bool

class Announcement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    content: str
    image_url: Optional[str] = None
    date: Optional[str] = None
    created_at: str
    archived: bool = False

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None
    date: Optional[str] = None

class SuccessEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    description: str
    image_url: Optional[str] = None
    date: str
    archived: bool = False
    created_at: str

class SuccessEventCreate(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None
    date: str

class HomepageContent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    section: str
    content: str
    updated_at: str

class HomepageContentUpdate(BaseModel):
    section: str
    content: str

class CoachInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    bio: str
    achievements: str
    image_url: Optional[str] = None
    updated_at: str

class CoachInfoUpdate(BaseModel):
    name: str
    bio: str
    achievements: str
    image_url: Optional[str] = None

# =============== NEW MODELS FOR ALUMNI, EVENTS, MEMBERSHIP ===============

class Alumni(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    designation: str
    batch: str
    current_occupation: str
    photo_url: Optional[str] = None
    order_number: int
    archived: bool = False
    created_at: str

class AlumniCreate(BaseModel):
    name: str
    designation: str
    batch: str
    current_occupation: str
    photo_url: Optional[str] = None
    order_number: int

class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    date: str
    photo_url: Optional[str] = None
    video_link: Optional[str] = None
    note_link: Optional[str] = None
    details: str
    archived: bool = False
    created_at: str

class EventCreate(BaseModel):
    name: str
    date: str
    photo_url: Optional[str] = None
    video_link: Optional[str] = None
    note_link: Optional[str] = None
    details: str

class MembershipContent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    photo_url: Optional[str] = None
    description: str
    form_link: str
    updated_at: str

class MembershipContentUpdate(BaseModel):
    photo_url: Optional[str] = None
    description: str
    form_link: str

class FlagshipEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    title: str
    photo_url: Optional[str] = None
    details: str
    event_link: Optional[str] = None
    preregister_link: Optional[str] = None
    active: bool = True
    archived: bool = False
    created_at: str

class FlagshipEventCreate(BaseModel):
    title: str
    photo_url: Optional[str] = None
    details: str
    event_link: Optional[str] = None
    preregister_link: Optional[str] = None

class FlagshipAnnouncement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    flagship_event_id: str
    title: str
    photo_url: Optional[str] = None
    details: str
    archived: bool = False
    created_at: str

class FlagshipAnnouncementCreate(BaseModel):
    title: str
    photo_url: Optional[str] = None
    details: str

class SystemSetup(BaseModel):
    is_setup_complete: bool

class SetupAdmin(BaseModel):
    full_name: str
    email: EmailStr
    password: str

# =============== HELPER FUNCTIONS ===============

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def require_approved(current_user: dict = Depends(get_current_user)):
    if current_user.get("status") != "approved":
        raise HTTPException(status_code=403, detail="Account approval required")
    return current_user

def generate_id():
    from uuid import uuid4
    return str(uuid4())

# =============== AUTH ROUTES ===============

@api_router.post("/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup):
    # Check if email exists
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_doc = {
        "id": generate_id(),
        "full_name": user_data.full_name,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "role": "student",
        "status": "pending",
        "mentorship_access": False,
        "advanced_access": False,
        "batch": user_data.batch,
        "reason": user_data.reason,
        "last_login": datetime.now(timezone.utc).isoformat(),
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    # Create token
    access_token = create_access_token({"sub": user_doc["id"]})
    
    # Return response
    user_response = UserResponse(
        id=user_doc["id"],
        full_name=user_doc["full_name"],
        email=user_doc["email"],
        role=user_doc["role"],
        status=user_doc["status"],
        mentorship_access=user_doc["mentorship_access"],
        advanced_access=user_doc.get("advanced_access", False),
        batch=user_doc.get("batch"),
        last_login=user_doc["last_login"],
        created_at=user_doc["created_at"]
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email}, {"_id": 0})
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
    )
    user["last_login"] = datetime.now(timezone.utc).isoformat()
    
    # Create token
    access_token = create_access_token({"sub": user["id"]})
    
    user_response = UserResponse(
        id=user["id"],
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"],
        status=user["status"],
        mentorship_access=user["mentorship_access"],
        batch=user.get("batch"),
        last_login=user["last_login"],
        created_at=user["created_at"]
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)

# =============== SYSTEM SETUP ===============

@api_router.get("/setup/status")
async def check_setup_status():
    setup = await db.system_setup.find_one({}, {"_id": 0})
    if setup and setup.get("is_setup_complete"):
        return {"is_setup_complete": True}
    return {"is_setup_complete": False}

@api_router.post("/setup/initialize")
async def initialize_system(admin_data: SetupAdmin):
    # Check if already setup
    setup = await db.system_setup.find_one({})
    if setup and setup.get("is_setup_complete"):
        raise HTTPException(status_code=400, detail="System already initialized")
    
    # Check if email exists
    existing = await db.users.find_one({"email": admin_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create admin user
    admin_doc = {
        "id": generate_id(),
        "full_name": admin_data.full_name,
        "email": admin_data.email,
        "password_hash": hash_password(admin_data.password),
        "role": "admin",
        "status": "approved",
        "mentorship_access": True,
        "batch": None,
        "reason": None,
        "last_login": datetime.now(timezone.utc).isoformat(),
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(admin_doc)
    
    # Initialize default content
    await initialize_default_content()
    
    # Mark system as setup
    await db.system_setup.delete_many({})
    await db.system_setup.insert_one({"is_setup_complete": True, "created_at": datetime.now(timezone.utc).isoformat()})
    
    # Create token
    access_token = create_access_token({"sub": admin_doc["id"]})
    
    user_response = UserResponse(
        id=admin_doc["id"],
        full_name=admin_doc["full_name"],
        email=admin_doc["email"],
        role=admin_doc["role"],
        status=admin_doc["status"],
        mentorship_access=admin_doc["mentorship_access"],
        batch=admin_doc.get("batch"),
        last_login=admin_doc["last_login"],
        created_at=admin_doc["created_at"]
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

async def initialize_default_content():
    # Homepage content
    homepage_sections = [
        {"section": "hero_title", "content": "Welcome to BUTEX Debating Club", "updated_at": datetime.now(timezone.utc).isoformat()},
        {"section": "hero_subtitle", "content": "Empowering voices, shaping leaders", "updated_at": datetime.now(timezone.utc).isoformat()},
        {"section": "about_university", "content": "Bangladesh University of Textiles (BUTEX) is a premier institution dedicated to textile education and research in Bangladesh.", "updated_at": datetime.now(timezone.utc).isoformat()},
        {"section": "about_club", "content": "BUTEX Debating Club is a platform for students to develop critical thinking, public speaking, and leadership skills through debate.", "updated_at": datetime.now(timezone.utc).isoformat()},
        {"section": "mission", "content": "To foster intellectual discourse and develop confident, articulate leaders.", "updated_at": datetime.now(timezone.utc).isoformat()},
        {"section": "vision", "content": "To be the leading debating platform in Bangladesh, nurturing world-class debaters.", "updated_at": datetime.now(timezone.utc).isoformat()},
    ]
    await db.homepage_content.delete_many({})
    await db.homepage_content.insert_many(homepage_sections)
    
    # Leadership (sample data)
    leadership_members = [
        {"id": generate_id(), "name": "President Name", "position": "President", "photo_url": None, "order_number": 1, "archived": False, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": generate_id(), "name": "General Secretary Name", "position": "General Secretary", "photo_url": None, "order_number": 2, "archived": False, "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": generate_id(), "name": "Chief of English Wing Name", "position": "Chief of English Wing", "photo_url": None, "order_number": 3, "archived": False, "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    await db.leadership.delete_many({})
    await db.leadership.insert_many(leadership_members)
    
    # Coach info
    coach_doc = {
        "name": "Abrar Fahad Zaman",
        "bio": "Expert debate coach with extensive experience in training national and international champions.",
        "achievements": "1. Coached the Pre-worlds Champions of 2019 - Scholastica\n2. Grand Final Chair and Cap of BDC Digital Discourse 2020 - Bangladesh's first real time international debate tournament in English\n3. Worked as the Content Curator of Bitorko Matter Training after the former chair of BDC Fardeen Ameen passed the torch\n4. World Bank IFC TOT (online) acquired under Master Trainer Quazi M. Ahmed\n5. Trained under Don Sumdany, Coach Kamrul and Mashahed Hassan Simanta in their training programs\n6. Completed NLD which was a pioneering coaching program by Sajid Khandaker and Adi Mehedi Adi\n7. Coach of ULAB, Trainer of Scholastica Debate Team, Mentor at BRAC.",
        "image_url": None,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.coach_info.delete_many({})
    await db.coach_info.insert_one(coach_doc)
    
    # Create courses with modules
    await create_beginner_course()
    await create_advanced_course()
    await create_mentorship_course()

async def create_beginner_course():
    course_doc = {
        "id": generate_id(),
        "title": "Beginner Course",
        "description": "This course is designed to introduce participants to the fundamentals of parliamentary debate formats, focusing on the Asian Parliamentary (AP) and British Parliamentary (BP) styles. It covers the roles of speakers, types of motions, and essential argumentation techniques.",
        "outline": "Master the fundamentals of debate including AP & BP formats, speaker roles, motion analysis, framing, impact analysis, principled and utility arguments, and rebuttal techniques.",
        "course_type": "beginner",
        "archived": False,
        "order_number": 1,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.courses.insert_one(course_doc)
    
    modules = [
        {"title": "Introduction to AP & BP Debate Formats", "duration": "45 min", "video_link": "https://www.youtube.com/watch?v=example1", "order": 1},
        {"title": "Roles of Speakers", "duration": "60 min", "video_link": "https://www.youtube.com/watch?v=example2", "order": 2},
        {"title": "Types of Motion and Their Demand", "duration": "50 min", "video_link": "https://www.youtube.com/watch?v=example3", "order": 3},
        {"title": "Debates to Watch (AP)", "duration": "90 min", "video_link": "https://www.youtube.com/playlist?list=PLJKCyUsDFuAX5wRnTm3ipGQ9WPvXYD6Cn", "order": 4},
        {"title": "Framing", "duration": "55 min", "video_link": "https://www.youtube.com/watch?v=example5", "order": 5},
        {"title": "Impact Analysis & Comparative", "duration": "50 min", "video_link": "https://www.youtube.com/watch?v=example6", "order": 6},
        {"title": "Principal Argument", "duration": "60 min", "video_link": "https://www.youtube.com/watch?v=example7", "order": 7},
        {"title": "Utility Argument", "duration": "55 min", "video_link": "https://www.youtube.com/watch?v=example8", "order": 8},
        {"title": "Rebuttal", "duration": "65 min", "video_link": "https://www.youtube.com/watch?v=example9", "order": 9},
    ]
    
    for mod in modules:
        module_doc = {
            "id": generate_id(),
            "course_id": course_doc["id"],
            "title": mod["title"],
            "duration": mod["duration"],
            "video_link": mod["video_link"],
            "pdf_link": None,
            "order_number": mod["order"],
            "archived": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.modules.insert_one(module_doc)

async def create_advanced_course():
    course_doc = {
        "id": generate_id(),
        "title": "Advanced Course",
        "description": "This course delves into more sophisticated debate strategies, focusing on advanced weighing techniques, effective use of evidence and illustrations, constructing extensions, and top-tier strategic thinking.",
        "outline": "Develop advanced skills including sophisticated weighing, strategic illustration usage, lower house extensions, and top house strategies for competitive debate.",
        "course_type": "advanced",
        "archived": False,
        "order_number": 2,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.courses.insert_one(course_doc)
    
    modules = [
        {"title": "Weighing", "duration": "70 min", "video_link": "https://www.youtube.com/watch?v=example10", "order": 1},
        {"title": "Illustration and How to Use Matter in Debate", "duration": "80 min", "video_link": "https://www.youtube.com/watch?v=example11", "order": 2},
        {"title": "Extensions for Lower House and Connecting It", "duration": "75 min", "video_link": "https://www.youtube.com/watch?v=example12", "order": 3},
        {"title": "Top House Strategies", "duration": "85 min", "video_link": "https://www.youtube.com/watch?v=example13", "order": 4},
    ]
    
    for mod in modules:
        module_doc = {
            "id": generate_id(),
            "course_id": course_doc["id"],
            "title": mod["title"],
            "duration": mod["duration"],
            "video_link": mod["video_link"],
            "pdf_link": None,
            "order_number": mod["order"],
            "archived": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.modules.insert_one(module_doc)

async def create_mentorship_course():
    course_doc = {
        "id": generate_id(),
        "title": "Mentorship with AFZ",
        "description": "Exclusive mentorship program with Abrar Fahad Zaman, designed for advanced debaters seeking personalized coaching and elite-level training.",
        "outline": "One-on-one mentorship sessions, personalized feedback, advanced strategy development, and preparation for international competitions.",
        "course_type": "mentorship",
        "archived": False,
        "order_number": 3,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.courses.insert_one(course_doc)

# =============== USER MANAGEMENT (ADMIN) ===============

@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    current_user: dict = Depends(require_admin),
    filter_status: Optional[str] = None,
    filter_mentorship: Optional[bool] = None
):
    query = {"archived": False}
    if filter_status:
        query["status"] = filter_status
    if filter_mentorship is not None:
        query["mentorship_access"] = filter_mentorship
    
    users = await db.users.find(query, {"_id": 0, "password_hash": 0}).to_list(1000)
    return [UserResponse(**user) for user in users]

@api_router.patch("/admin/users/{user_id}/approve")
async def approve_user(user_id: str, current_user: dict = Depends(require_admin)):
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"status": "approved"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User approved"}

@api_router.patch("/admin/users/{user_id}/mentorship")
async def toggle_mentorship(user_id: str, grant: bool, current_user: dict = Depends(require_admin)):
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"mentorship_access": grant}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"Mentorship access {'granted' if grant else 'revoked'}"}

@api_router.patch("/admin/users/{user_id}/archive")
async def archive_user(user_id: str, current_user: dict = Depends(require_admin)):
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"archived": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User archived"}

# =============== LEADERSHIP ===============

@api_router.get("/leadership", response_model=List[LeadershipMember])
async def get_leadership():
    members = await db.leadership.find({"archived": False}, {"_id": 0}).sort("order_number", 1).to_list(1000)
    return [LeadershipMember(**member) for member in members]

@api_router.post("/admin/leadership", response_model=LeadershipMember)
async def create_leadership_member(member_data: LeadershipCreate, current_user: dict = Depends(require_admin)):
    member_doc = {
        "id": generate_id(),
        "name": member_data.name,
        "position": member_data.position,
        "photo_url": member_data.photo_url,
        "order_number": member_data.order_number,
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.leadership.insert_one(member_doc)
    return LeadershipMember(**member_doc)

@api_router.put("/admin/leadership/{member_id}", response_model=LeadershipMember)
async def update_leadership_member(member_id: str, member_data: LeadershipCreate, current_user: dict = Depends(require_admin)):
    result = await db.leadership.update_one(
        {"id": member_id},
        {"$set": {
            "name": member_data.name,
            "position": member_data.position,
            "photo_url": member_data.photo_url,
            "order_number": member_data.order_number
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Member not found")
    
    member = await db.leadership.find_one({"id": member_id}, {"_id": 0})
    return LeadershipMember(**member)

@api_router.patch("/admin/leadership/{member_id}/archive")
async def archive_leadership_member(member_id: str, current_user: dict = Depends(require_admin)):
    result = await db.leadership.update_one(
        {"id": member_id},
        {"$set": {"archived": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"message": "Member archived"}

@api_router.post("/admin/leadership/reorder")
async def reorder_leadership(order: List[dict], current_user: dict = Depends(require_admin)):
    for item in order:
        await db.leadership.update_one(
            {"id": item["id"]},
            {"$set": {"order_number": item["order_number"]}}
        )
    return {"message": "Order updated"}

# =============== COURSES ===============

@api_router.get("/courses", response_model=List[Course])
async def get_courses():
    courses = await db.courses.find({"archived": False}, {"_id": 0}).sort("order_number", 1).to_list(1000)
    return [Course(**course) for course in courses]

@api_router.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    course = await db.courses.find_one({"id": course_id, "archived": False}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return Course(**course)

@api_router.post("/admin/courses", response_model=Course)
async def create_course(course_data: CourseCreate, current_user: dict = Depends(require_admin)):
    course_doc = {
        "id": generate_id(),
        "title": course_data.title,
        "description": course_data.description,
        "outline": course_data.outline,
        "course_type": course_data.course_type,
        "archived": False,
        "order_number": course_data.order_number,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.courses.insert_one(course_doc)
    return Course(**course_doc)

@api_router.put("/admin/courses/{course_id}", response_model=Course)
async def update_course(course_id: str, course_data: CourseCreate, current_user: dict = Depends(require_admin)):
    result = await db.courses.update_one(
        {"id": course_id},
        {"$set": {
            "title": course_data.title,
            "description": course_data.description,
            "outline": course_data.outline,
            "course_type": course_data.course_type,
            "order_number": course_data.order_number
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    return Course(**course)

@api_router.patch("/admin/courses/{course_id}/archive")
async def archive_course(course_id: str, current_user: dict = Depends(require_admin)):
    result = await db.courses.update_one(
        {"id": course_id},
        {"$set": {"archived": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course archived"}

# =============== MODULES ===============

@api_router.get("/courses/{course_id}/modules", response_model=List[Module])
async def get_course_modules(course_id: str):
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    modules = await db.modules.find({"course_id": course_id, "archived": False}, {"_id": 0}).sort("order_number", 1).to_list(1000)
    return [Module(**module) for module in modules]

@api_router.post("/admin/modules", response_model=Module)
async def create_module(module_data: ModuleCreate, current_user: dict = Depends(require_admin)):
    module_doc = {
        "id": generate_id(),
        "course_id": module_data.course_id,
        "title": module_data.title,
        "duration": module_data.duration,
        "video_link": module_data.video_link,
        "pdf_link": module_data.pdf_link,
        "order_number": module_data.order_number,
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.modules.insert_one(module_doc)
    return Module(**module_doc)

@api_router.put("/admin/modules/{module_id}", response_model=Module)
async def update_module(module_id: str, module_data: ModuleCreate, current_user: dict = Depends(require_admin)):
    result = await db.modules.update_one(
        {"id": module_id},
        {"$set": {
            "title": module_data.title,
            "duration": module_data.duration,
            "video_link": module_data.video_link,
            "pdf_link": module_data.pdf_link,
            "order_number": module_data.order_number
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Module not found")
    
    module = await db.modules.find_one({"id": module_id}, {"_id": 0})
    return Module(**module)

@api_router.patch("/admin/modules/{module_id}/archive")
async def archive_module(module_id: str, current_user: dict = Depends(require_admin)):
    result = await db.modules.update_one(
        {"id": module_id},
        {"$set": {"archived": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Module not found")
    return {"message": "Module archived"}

@api_router.post("/admin/modules/reorder")
async def reorder_modules(order: List[dict], current_user: dict = Depends(require_admin)):
    for item in order:
        await db.modules.update_one(
            {"id": item["id"]},
            {"$set": {"order_number": item["order_number"]}}
        )
    return {"message": "Order updated"}

# =============== PROGRESS ===============

@api_router.get("/progress", response_model=List[Progress])
async def get_user_progress(current_user: dict = Depends(get_current_user)):
    progress_list = await db.progress.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(1000)
    return [Progress(**p) for p in progress_list]

@api_router.post("/progress", response_model=Progress)
async def update_progress(progress_data: ProgressUpdate, current_user: dict = Depends(require_approved)):
    # Check if progress exists
    existing = await db.progress.find_one({
        "user_id": current_user["id"],
        "module_id": progress_data.module_id
    }, {"_id": 0})
    
    if existing:
        # Update existing
        update_data = {
            "completed": progress_data.completed,
            "completed_at": datetime.now(timezone.utc).isoformat() if progress_data.completed else None
        }
        await db.progress.update_one(
            {"id": existing["id"]},
            {"$set": update_data}
        )
        existing.update(update_data)
        return Progress(**existing)
    else:
        # Create new
        progress_doc = {
            "id": generate_id(),
            "user_id": current_user["id"],
            "module_id": progress_data.module_id,
            "completed": progress_data.completed,
            "completed_at": datetime.now(timezone.utc).isoformat() if progress_data.completed else None
        }
        await db.progress.insert_one(progress_doc)
        return Progress(**progress_doc)

# =============== ANNOUNCEMENTS ===============

@api_router.get("/announcements", response_model=List[Announcement])
async def get_announcements():
    announcements = await db.announcements.find({"archived": False}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Announcement(**ann) for ann in announcements]

@api_router.post("/admin/announcements", response_model=Announcement)
async def create_announcement(announcement_data: AnnouncementCreate, current_user: dict = Depends(require_admin)):
    ann_doc = {
        "id": generate_id(),
        "title": announcement_data.title,
        "content": announcement_data.content,
        "image_url": announcement_data.image_url,
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.announcements.insert_one(ann_doc)
    return Announcement(**ann_doc)

@api_router.put("/admin/announcements/{announcement_id}", response_model=Announcement)
async def update_announcement(announcement_id: str, announcement_data: AnnouncementCreate, current_user: dict = Depends(require_admin)):
    result = await db.announcements.update_one(
        {"id": announcement_id},
        {"$set": {
            "title": announcement_data.title,
            "content": announcement_data.content,
            "image_url": announcement_data.image_url
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    ann = await db.announcements.find_one({"id": announcement_id}, {"_id": 0})
    return Announcement(**ann)

@api_router.patch("/admin/announcements/{announcement_id}/archive")
async def archive_announcement(announcement_id: str, current_user: dict = Depends(require_admin)):
    result = await db.announcements.update_one(
        {"id": announcement_id},
        {"$set": {"archived": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement archived"}

# =============== SUCCESS EVENTS ===============

@api_router.get("/success-events", response_model=List[SuccessEvent])
async def get_success_events():
    events = await db.success_events.find({"archived": False}, {"_id": 0}).sort("date", -1).to_list(1000)
    return [SuccessEvent(**event) for event in events]

@api_router.post("/admin/success-events", response_model=SuccessEvent)
async def create_success_event(event_data: SuccessEventCreate, current_user: dict = Depends(require_admin)):
    event_doc = {
        "id": generate_id(),
        "title": event_data.title,
        "description": event_data.description,
        "image_url": event_data.image_url,
        "date": event_data.date,
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.success_events.insert_one(event_doc)
    return SuccessEvent(**event_doc)

@api_router.put("/admin/success-events/{event_id}", response_model=SuccessEvent)
async def update_success_event(event_id: str, event_data: SuccessEventCreate, current_user: dict = Depends(require_admin)):
    result = await db.success_events.update_one(
        {"id": event_id},
        {"$set": {
            "title": event_data.title,
            "description": event_data.description,
            "image_url": event_data.image_url,
            "date": event_data.date
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = await db.success_events.find_one({"id": event_id}, {"_id": 0})
    return SuccessEvent(**event)

@api_router.patch("/admin/success-events/{event_id}/archive")
async def archive_success_event(event_id: str, current_user: dict = Depends(require_admin)):
    result = await db.success_events.update_one(
        {"id": event_id},
        {"$set": {"archived": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event archived"}

# =============== HOMEPAGE CONTENT ===============

@api_router.get("/homepage-content", response_model=List[HomepageContent])
async def get_homepage_content():
    content = await db.homepage_content.find({}, {"_id": 0}).to_list(1000)
    return [HomepageContent(**item) for item in content]

@api_router.put("/admin/homepage-content", response_model=HomepageContent)
async def update_homepage_content(content_data: HomepageContentUpdate, current_user: dict = Depends(require_admin)):
    result = await db.homepage_content.update_one(
        {"section": content_data.section},
        {"$set": {
            "content": content_data.content,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )
    
    content = await db.homepage_content.find_one({"section": content_data.section}, {"_id": 0})
    return HomepageContent(**content)

# =============== COACH INFO ===============

@api_router.get("/coach-info", response_model=CoachInfo)
async def get_coach_info():
    coach = await db.coach_info.find_one({}, {"_id": 0})
    if not coach:
        raise HTTPException(status_code=404, detail="Coach info not found")
    return CoachInfo(**coach)

@api_router.put("/admin/coach-info", response_model=CoachInfo)
async def update_coach_info(coach_data: CoachInfoUpdate, current_user: dict = Depends(require_admin)):
    await db.coach_info.delete_many({})
    coach_doc = {
        "name": coach_data.name,
        "bio": coach_data.bio,
        "achievements": coach_data.achievements,
        "image_url": coach_data.image_url,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.coach_info.insert_one(coach_doc)
    return CoachInfo(**coach_doc)

# =============== ANALYTICS ===============

@api_router.get("/admin/analytics")
async def get_analytics(current_user: dict = Depends(require_admin)):
    total_users = await db.users.count_documents({"archived": False})
    approved_users = await db.users.count_documents({"status": "approved", "archived": False})
    pending_users = await db.users.count_documents({"status": "pending", "archived": False})
    mentorship_users = await db.users.count_documents({"mentorship_access": True, "archived": False})
    
    # Active users (logged in within last 30 days)
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    active_users = await db.users.count_documents({
        "last_login": {"$gte": thirty_days_ago},
        "archived": False
    })
    
    # Course completion rates
    courses = await db.courses.find({"archived": False}, {"_id": 0}).to_list(1000)
    course_stats = []
    for course in courses:
        modules = await db.modules.find({"course_id": course["id"], "archived": False}).to_list(1000)
        total_modules = len(modules)
        
        if total_modules > 0:
            # Get users who completed all modules
            completed_count = 0
            enrolled_users = await db.progress.distinct("user_id", {"module_id": {"$in": [m["id"] for m in modules]}})
            
            for user_id in enrolled_users:
                user_progress = await db.progress.count_documents({
                    "user_id": user_id,
                    "module_id": {"$in": [m["id"] for m in modules]},
                    "completed": True
                })
                if user_progress == total_modules:
                    completed_count += 1
            
            completion_rate = (completed_count / len(enrolled_users) * 100) if enrolled_users else 0
            course_stats.append({
                "course_id": course["id"],
                "course_title": course["title"],
                "enrolled": len(enrolled_users),
                "completed": completed_count,
                "completion_rate": round(completion_rate, 2)
            })
    
    return {
        "total_users": total_users,
        "approved_users": approved_users,
        "pending_users": pending_users,
        "active_users": active_users,
        "mentorship_users": mentorship_users,
        "course_stats": course_stats
    }

# =============== IMAGE UPLOAD ===============

@api_router.post("/admin/upload-image")
async def upload_image(file: UploadFile = File(...), current_user: dict = Depends(require_admin)):
    # Read file content
    content = await file.read()
    
    # Convert to base64 for storage (simple approach for MVP)
    base64_data = base64.b64encode(content).decode('utf-8')
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    data_url = f"data:image/{file_extension};base64,{base64_data}"
    
    return {"url": data_url}

# =============== ALUMNI ROUTES ===============

@api_router.get("/alumni", response_model=List[Alumni])
async def get_alumni():
    alumni_list = await db.alumni.find({"archived": False}, {"_id": 0}).sort("order_number", 1).to_list(1000)
    return [Alumni(**alum) for alum in alumni_list]

@api_router.post("/admin/alumni", response_model=Alumni)
async def create_alumni(alumni_data: AlumniCreate, current_user: dict = Depends(require_admin)):
    alumni_doc = {
        "id": generate_id(),
        "name": alumni_data.name,
        "designation": alumni_data.designation,
        "batch": alumni_data.batch,
        "current_occupation": alumni_data.current_occupation,
        "photo_url": alumni_data.photo_url,
        "order_number": alumni_data.order_number,
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.alumni.insert_one(alumni_doc)
    return Alumni(**alumni_doc)

@api_router.put("/admin/alumni/{alumni_id}", response_model=Alumni)
async def update_alumni(alumni_id: str, alumni_data: AlumniCreate, current_user: dict = Depends(require_admin)):
    result = await db.alumni.update_one(
        {"id": alumni_id},
        {"$set": {
            "name": alumni_data.name,
            "designation": alumni_data.designation,
            "batch": alumni_data.batch,
            "current_occupation": alumni_data.current_occupation,
            "photo_url": alumni_data.photo_url,
            "order_number": alumni_data.order_number
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alumni not found")
    
    alumni = await db.alumni.find_one({"id": alumni_id}, {"_id": 0})
    return Alumni(**alumni)

@api_router.patch("/admin/alumni/{alumni_id}/archive")
async def archive_alumni(alumni_id: str, current_user: dict = Depends(require_admin)):
    result = await db.alumni.update_one(
        {"id": alumni_id},
        {"$set": {"archived": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alumni not found")
    return {"message": "Alumni archived"}

# =============== EVENTS ROUTES ===============

@api_router.get("/events", response_model=List[Event])
async def get_events():
    events = await db.events.find({"archived": False}, {"_id": 0}).sort("date", -1).to_list(1000)
    return [Event(**event) for event in events]

@api_router.post("/admin/events", response_model=Event)
async def create_event(event_data: EventCreate, current_user: dict = Depends(require_admin)):
    event_doc = {
        "id": generate_id(),
        "name": event_data.name,
        "date": event_data.date,
        "photo_url": event_data.photo_url,
        "video_link": event_data.video_link,
        "note_link": event_data.note_link,
        "details": event_data.details,
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.events.insert_one(event_doc)
    return Event(**event_doc)

@api_router.put("/admin/events/{event_id}", response_model=Event)
async def update_event(event_id: str, event_data: EventCreate, current_user: dict = Depends(require_admin)):
    result = await db.events.update_one(
        {"id": event_id},
        {"$set": {
            "name": event_data.name,
            "date": event_data.date,
            "photo_url": event_data.photo_url,
            "video_link": event_data.video_link,
            "note_link": event_data.note_link,
            "details": event_data.details
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = await db.events.find_one({"id": event_id}, {"_id": 0})
    return Event(**event)

@api_router.patch("/admin/events/{event_id}/archive")
async def archive_event(event_id: str, current_user: dict = Depends(require_admin)):
    result = await db.events.update_one(
        {"id": event_id},
        {"$set": {"archived": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event archived"}

# =============== MEMBERSHIP ROUTES ===============

@api_router.get("/membership-content", response_model=MembershipContent)
async def get_membership_content():
    content = await db.membership_content.find_one({}, {"_id": 0})
    if not content:
        # Return default content if not set
        return MembershipContent(
            photo_url=None,
            description="Join BUTEX Debating Club and be part of our community!",
            form_link="",
            updated_at=datetime.now(timezone.utc).isoformat()
        )
    return MembershipContent(**content)

@api_router.put("/admin/membership-content", response_model=MembershipContent)
async def update_membership_content(content_data: MembershipContentUpdate, current_user: dict = Depends(require_admin)):
    await db.membership_content.delete_many({})
    content_doc = {
        "photo_url": content_data.photo_url,
        "description": content_data.description,
        "form_link": content_data.form_link,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.membership_content.insert_one(content_doc)
    return MembershipContent(**content_doc)

# =============== USER MANAGEMENT UPDATES ===============

@api_router.patch("/admin/users/{user_id}/advanced")
async def toggle_advanced_access(user_id: str, grant: bool, current_user: dict = Depends(require_admin)):
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"advanced_access": grant}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": f"Advanced course access {'granted' if grant else 'revoked'}"}

# =============== FLAGSHIP EVENTS ===============

@api_router.get("/flagship-events", response_model=List[FlagshipEvent])
async def get_flagship_events():
    events = await db.flagship_events.find({"archived": False}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [FlagshipEvent(**e) for e in events]

@api_router.get("/flagship-events/active", response_model=List[FlagshipEvent])
async def get_active_flagship_events():
    events = await db.flagship_events.find({"archived": False, "active": True}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [FlagshipEvent(**e) for e in events]

@api_router.get("/flagship-events/{event_id}")
async def get_flagship_event(event_id: str):
    event = await db.flagship_events.find_one({"id": event_id, "archived": False}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Flagship event not found")
    announcements = await db.flagship_announcements.find({"flagship_event_id": event_id, "archived": False}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return {**FlagshipEvent(**event).model_dump(), "announcements": [FlagshipAnnouncement(**a).model_dump() for a in announcements]}

@api_router.post("/admin/flagship-events", response_model=FlagshipEvent)
async def create_flagship_event(data: FlagshipEventCreate, current_user: dict = Depends(require_admin)):
    doc = {
        "id": generate_id(),
        "title": data.title,
        "photo_url": data.photo_url,
        "details": data.details,
        "event_link": data.event_link,
        "preregister_link": data.preregister_link,
        "active": True,
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.flagship_events.insert_one(doc)
    return FlagshipEvent(**doc)

@api_router.put("/admin/flagship-events/{event_id}", response_model=FlagshipEvent)
async def update_flagship_event(event_id: str, data: FlagshipEventCreate, current_user: dict = Depends(require_admin)):
    result = await db.flagship_events.update_one(
        {"id": event_id},
        {"$set": {
            "title": data.title,
            "photo_url": data.photo_url,
            "details": data.details,
            "event_link": data.event_link,
            "preregister_link": data.preregister_link,
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Flagship event not found")
    event = await db.flagship_events.find_one({"id": event_id}, {"_id": 0})
    return FlagshipEvent(**event)

@api_router.patch("/admin/flagship-events/{event_id}/archive")
async def archive_flagship_event(event_id: str, current_user: dict = Depends(require_admin)):
    result = await db.flagship_events.update_one({"id": event_id}, {"$set": {"archived": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Flagship event not found")
    return {"message": "Flagship event archived"}

@api_router.patch("/admin/flagship-events/{event_id}/toggle")
async def toggle_flagship_event(event_id: str, current_user: dict = Depends(require_admin)):
    event = await db.flagship_events.find_one({"id": event_id}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Flagship event not found")
    new_active = not event.get("active", True)
    await db.flagship_events.update_one({"id": event_id}, {"$set": {"active": new_active}})
    return {"message": f"Flagship event {'activated' if new_active else 'deactivated'}", "active": new_active}

@api_router.get("/flagship-events/{event_id}/announcements", response_model=List[FlagshipAnnouncement])
async def get_flagship_announcements(event_id: str):
    announcements = await db.flagship_announcements.find({"flagship_event_id": event_id, "archived": False}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [FlagshipAnnouncement(**a) for a in announcements]

@api_router.post("/admin/flagship-events/{event_id}/announcements", response_model=FlagshipAnnouncement)
async def create_flagship_announcement(event_id: str, data: FlagshipAnnouncementCreate, current_user: dict = Depends(require_admin)):
    event = await db.flagship_events.find_one({"id": event_id}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Flagship event not found")
    doc = {
        "id": generate_id(),
        "flagship_event_id": event_id,
        "title": data.title,
        "photo_url": data.photo_url,
        "details": data.details,
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.flagship_announcements.insert_one(doc)
    return FlagshipAnnouncement(**doc)

@api_router.put("/admin/flagship-announcements/{ann_id}", response_model=FlagshipAnnouncement)
async def update_flagship_announcement(ann_id: str, data: FlagshipAnnouncementCreate, current_user: dict = Depends(require_admin)):
    result = await db.flagship_announcements.update_one(
        {"id": ann_id},
        {"$set": {"title": data.title, "photo_url": data.photo_url, "details": data.details}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    ann = await db.flagship_announcements.find_one({"id": ann_id}, {"_id": 0})
    return FlagshipAnnouncement(**ann)

@api_router.patch("/admin/flagship-announcements/{ann_id}/archive")
async def archive_flagship_announcement(ann_id: str, current_user: dict = Depends(require_admin)):
    result = await db.flagship_announcements.update_one({"id": ann_id}, {"$set": {"archived": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement archived"}

# =============== MAIN APP ===============

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
