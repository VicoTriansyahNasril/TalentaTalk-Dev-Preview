from pydantic import BaseModel, EmailStr
from typing import List, Optional

# --- Stats & Activity ---
class DashboardStats(BaseModel):
    totalTalent: int
    totalPronunciationMaterial: int
    totalExamPhonemMaterial: int
    totalInterviewQuestion: int

class RecentActivityItem(BaseModel):
    talentId: int
    talentName: str
    activityType: str
    category: Optional[str] = "General"
    score: str
    date: str

# --- Leaderboards ---
class LearnerItem(BaseModel):
    no: int
    id: int
    talentName: str
    email: str
    # Untuk Top Active
    highestStreak: Optional[str] = None
    currentStreak: Optional[str] = None
    # Untuk Highest Scoring
    overallCompletion: Optional[str] = None
    overallPercentage: Optional[str] = None
    completionRate: Optional[str] = None
    # Untuk Conversation/Interview
    wpm: Optional[str] = None
    grammer: Optional[str] = None
    feedback: Optional[str] = None
    date: Optional[str] = None
    totalAttempts: Optional[int] = None

class PaginationInfo(BaseModel):
    currentPage: int
    totalPages: int
    totalRecords: int
    showing: str

class PaginatedListResponse(BaseModel):
    learners: List[LearnerItem]
    pagination: PaginationInfo

# --- Admin Profile ---
class AdminProfile(BaseModel):
    idUser: str
    name: str
    email: str
    role: str
    createdAt: Optional[str] = None
    lastLogin: Optional[str] = None

class AdminUpdate(BaseModel):
    nama: str
    email: EmailStr

class AdminPasswordUpdate(BaseModel):
    new_password: str

class DashboardResponse(BaseModel):
    statistics: DashboardStats
    recentActivities: List[RecentActivityItem]