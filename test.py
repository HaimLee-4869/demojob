from typing import Union

from fastapi import FastAPI

app = FastAPI()


# API 서버 상태 확인
@app.get("/status")
def read_root():
    return {"Status": "정상 작동 중입니다!"}


# 회원 가입
@app.post("/auth/register")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# 로그인
@app.post("/auth/login")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# 토큰 갱신
@app.post("/auth/refresh")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# 회원 정보 수정
@app.put("/auth/profile")
def set_item():
    return {}


# 공고 목록 조회
@app.get("/jobs")
def read_item():
    return {}


# 지원하기
@app.post("/applications")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# 지원 내역 조회
@app.get("/applications")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# 지원 취소
@app.delete("/applications/:id")
def delete_item():
    return {}


# 북마크 추가 및 제거
@app.post("/bookmarks")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# 북마크 목록 조회
@app.get("/bookmarks")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


# 공고 상세 조회
@app.get("/jobs/:id")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/eunjung/{score}")
def read_root(score: str):
    return {"은정이의 점수는?!": score}
