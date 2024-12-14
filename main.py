from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
import bcrypt
from fastapi.openapi.utils import get_openapi
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# In-memory database simulation
users_db = {}
jobs_db = []  # 기존 예제 코드에선 사용했지만, 이번에는 외부 페이지에서 크롤링

# Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class JobPost(BaseModel):
    title: str
    description: str
    company: str
    location: str
    salary: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    company: str
    location: str
    salary: Optional[str]

class Settings(BaseModel):
    authjwt_secret_key: str = "your_secret_key_here"
    authjwt_access_token_expires: int = 3600  # 1 hour

@app.on_event("startup")
def setup_openapi():
    openapi_schema = get_openapi(
        title="Job Board API",
        version="1.0.0",
        description="API documentation for the Job Board application",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema

@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    return app.openapi_schema


@AuthJWT.load_config
def get_config():
    return Settings()

# Custom exception handling for JWT errors
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.get("/status")
def status():
    return {"status": "API is running"}

@app.post("/auth/register")
def register_user(user: UserRegister):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    users_db[user.email] = {"password": hashed_password}
    return {"message": "User registered successfully"}

@app.post("/auth/login")
def login_user(user: UserLogin, Authorize: AuthJWT = Depends()):
    if user.email not in users_db:
        raise HTTPException(status_code=400, detail="User does not exist")

    if not bcrypt.checkpw(user.password.encode('utf-8'), users_db[user.email]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = Authorize.create_access_token(subject=user.email)
    return {"access_token": access_token}

@app.post("/jobs")
def create_job(job: JobPost, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    job_id = len(jobs_db) + 1
    job_entry = {"id": job_id, **job.dict()}
    jobs_db.append(job_entry)
    return job_entry

@app.get("/jobs", response_model=List[JobResponse])
def list_jobs(page: int = Query(1, gt=0)):
    # 이 URL은 예시로 주어졌으며, 현재 페이지에서 모든 공고를 가져온 뒤 
    # 서버에서 페이지네이션(20개씩)을 수행
    url = "https://www.saramin.co.kr/zf_user/jobs/public/list?srsltid=AfmBOoq_qDEU1lEjmXmkoKi3-ISVAOBc1olIy8tinObVIXkG56nHoieT"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch job listings")

    soup = BeautifulSoup(response.text, "html.parser")
    
    # 사라민 공고 목록 파싱 (아래는 실제 페이지 구조에 맞게 조정 필요)
    # 여기서는 예시로 'li' 태그 중 class='job_item'인 요소를 공고 하나로 가정
    job_items = soup.select("div.item_recruit")  # 실제 페이지에 맞게 선택자 수정 필요
    # 실제 사라민 페이지 구조에 맞는 selector를 찾아야 함.
    # 예: 사라민 공고 리스트는 대략 다음과 같은 구조임:
    # div.item_recruit(공고블록)
    #   div.area_job
    #       h2.job_tit > a  (공고 타이틀)
    #       div.job_condition (회사, 위치, 연봉 등의 정보)
    #       div.job_desc (공고 요약정보)
    # 여기서는 가상의 selector를 예로 듦.
    
    jobs_data = []
    job_id = 1
    for item in job_items:
        title_el = item.select_one(".job_tit a")
        title = title_el.get_text(strip=True) if title_el else "No Title"
        
        company_el = item.select_one(".area_corp .corp_name a")
        company = company_el.get_text(strip=True) if company_el else "No Company"
        
        location_el = item.select_one(".job_condition span[class*=loc]")
        location = location_el.get_text(strip=True) if location_el else "No Location"
        
        salary_el = item.select_one(".job_condition span.pay")
        salary = salary_el.get_text(strip=True) if salary_el else None

        desc_el = item.select_one(".job_desc")
        description = desc_el.get_text(strip=True) if desc_el else ""

        jobs_data.append({
            "id": job_id,
            "title": title,
            "description": description,
            "company": company,
            "location": location,
            "salary": salary
        })
        job_id += 1

    # 페이지네이션: 20개씩 나누기
    page_size = 20
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paged_jobs = jobs_data[start_index:end_index]

    return paged_jobs

@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int):
    # 이전 코드상 jobs_db에 저장된 데이터를 가져오는 로직
    # 지금은 외부 사이트에서 불러오는 구조이므로 jobs_db에 따로 저장한 공고를 가져옴
    for job in jobs_db:
        if job["id"] == job_id:
            return job
    raise HTTPException(status_code=404, detail="Job not found")

@app.delete("/jobs/{job_id}")
def delete_job(job_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    for job in jobs_db:
        if job["id"] == job_id:
            jobs_db.remove(job)
            return {"message": "Job deleted successfully"}

    raise HTTPException(status_code=404, detail="Job not found")
