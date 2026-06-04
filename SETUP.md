# 홈앤쇼핑 교육 현황 대시보드 - 환경 세팅 가이드

이 문서는 Streamlit 앱과 Supabase 데이터베이스 연결 과정을 단계별로 설명합니다.

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [사전 요구사항](#사전-요구사항)
3. [Supabase 설정](#supabase-설정)
4. [데이터 마이그레이션](#데이터-마이그레이션)
5. [Streamlit 설정](#streamlit-설정)
6. [앱 실행](#앱-실행)
7. [트러블슈팅](#트러블슈팅)

---

## 프로젝트 개요

**목표**: CSV 파일의 교육 현황 데이터를 Supabase 데이터베이스에 저장하고, Streamlit 대시보드에서 시각화

**기술 스택**:
- **Frontend**: Streamlit
- **Database**: Supabase (PostgreSQL)
- **데이터**: CSV → SQL 마이그레이션
- **API**: Supabase REST API

---

## 사전 요구사항

### 필수 설치
```powershell
# Python 3.10 이상
python --version

# pip 업그레이드
python -m pip install --upgrade pip setuptools wheel
```

### 필수 패키지
```powershell
pip install streamlit pandas plotly requests
```

### 선택 (시각화 강화)
```powershell
pip install plotly-express
```

---

## Supabase 설정

### 1. Supabase 프로젝트 생성

1. [Supabase](https://supabase.com) 방문
2. 새 프로젝트 생성
3. 프로젝트 설정에서 다음 정보 확인:
   - **Project URL** (예: `https://lxctrbmrjeypvctkpckl.supabase.co`)
   - **Project Ref** (예: `lxctrbmrjeypvctkpckl`)

### 2. API 키 가져오기

**Supabase 콘솔** → **Settings** → **API** → **Project API Keys**

필요한 키:
- `anon` (공개 키) - REST API 호출용
- 또는 `sb_publishable_...` (최신 Publishable Key)

---

## 데이터 마이그레이션

### 1. 데이터베이스 테이블 생성

Supabase MCP 도구 사용:

```sql
CREATE TABLE ethics_training (
  id SERIAL PRIMARY KEY,
  month VARCHAR(10) NOT NULL,
  department VARCHAR(50) NOT NULL,
  course_name VARCHAR(100) NOT NULL,
  total_employees INTEGER NOT NULL,
  completed INTEGER NOT NULL,
  not_completed INTEGER NOT NULL,
  enrollment_rate DECIMAL(5, 2) NOT NULL,
  completion_rate DECIMAL(5, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. CSV 데이터 삽입

CSV 파일 형식:
```
월,부서,교육과정명,전사인원,이수자,미이수자,수강진도율,완료율
1월,임원급,윤리경영기초,45,43,2,95.6%,95.6%
...
```

SQL INSERT 문:
```sql
INSERT INTO ethics_training (month, department, course_name, total_employees, completed, not_completed, enrollment_rate, completion_rate) 
VALUES 
('1월', '임원급', '윤리경영기초', 45, 43, 2, 95.6, 95.6),
...
```

**참고**: 백분율 기호(%) 제거 후 숫자만 저장

---

## Streamlit 설정

### 1. Streamlit 디렉토리 구조 생성

```
project_root/
├── app.py
├── .streamlit/
│   └── secrets.toml
├── ethics_training_data.csv
└── requirements.txt
```

### 2. Streamlit 설정 파일 생성

**`.streamlit/config.toml`** (선택사항):
```toml
[theme]
primaryColor = "#FF6B9D"
backgroundColor = "#FFF0F5"
secondaryBackgroundColor = "#F0F2F6"

[client]
showErrorDetails = false
toolbarMode = "minimal"
```

### 3. Secrets 파일 생성

**`.streamlit/secrets.toml`** (필수):

```toml
[supabase]
url = "https://lxctrbmrjeypvctkpckl.supabase.co"
key = "sb_publishable_TE-_PjBSvTMK3wJmB8aL9w_OUM-FUCM"
```

⚠️ **보안 주의**: 이 파일은 `.gitignore`에 포함시켜 Git에 올리지 않기

```bash
echo ".streamlit/secrets.toml" >> .gitignore
```

---

## 앱 실행

### 1. 필수 패키지 설치

```powershell
cd project_directory
pip install -r requirements.txt
```

### 2. Streamlit 앱 실행

```powershell
streamlit run app.py
```

또는 특정 포트에서 실행:

```powershell
streamlit run app.py --server.port 8501
```

### 3. 브라우저 접근

```
http://localhost:8501
```

---

## 앱 기능

### 메인 대시보드
- **필터**: 월별, 직급별 선택
- **KPI 카드**:
  - 전체 대상 인원
  - 총 이수자
  - 총 미이수자
  - 평균 완료율

### 시각화
1. **교육 현황 상세**: 데이터 테이블 (미이수자 강조)
2. **직급별 이수 현황**: 3개 파이 차트
3. **월별 평균 완료율**: 라인 차트

---

## 데이터 흐름

```
CSV 파일
   ↓
Supabase Database (ethics_training 테이블)
   ↓
Streamlit App (REST API)
   ↓
브라우저 시각화
```

### Streamlit에서 데이터 로드

```python
import streamlit as st
import requests

@st.cache_data
def load_data():
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]

    headers = {
        'apikey': supabase_key,
        'Content-Type': 'application/json'
    }

    response = requests.get(
        f'{supabase_url}/rest/v1/ethics_training',
        headers=headers,
        timeout=10
    )
    
    df = pd.DataFrame(response.json())
    return df
```

---

## 트러블슈팅

### 문제 1: "ModuleNotFoundError: No module named 'streamlit'"

**해결책**:
```powershell
pip install -r requirements.txt
```

### 문제 2: Supabase 연결 오류

**확인 항목**:
- `.streamlit/secrets.toml` 파일 존재 여부
- Supabase URL과 Key 정확성
- 네트워크 연결 상태

**폴백 동작**: CSV 파일에서 자동으로 데이터 로드

### 문제 3: "404 Not Found" - REST API 오류

**확인 항목**:
- `ethics_training` 테이블 존재 여부
- 데이터 삽입 완료 여부

Supabase 콘솔에서 확인:
```
Table Editor → ethics_training → 데이터 확인
```

### 문제 4: Streamlit 포트 이미 사용 중

**해결책**:
```powershell
# 다른 포트 사용
streamlit run app.py --server.port 8502

# 또는 기존 프로세스 종료
Get-Process python | Stop-Process -Force
```

---

## 배포 시 주의사항

### 1. Environment Variables 설정

Supabase 키를 환경 변수로 관리:

```powershell
# Windows (PowerShell)
$env:SUPABASE_URL = "your_url"
$env:SUPABASE_KEY = "your_key"
```

또는 배포 플랫폼(Heroku, Railway, Streamlit Cloud)의 Secrets 기능 사용

### 2. .gitignore 확인

```
.streamlit/secrets.toml
.env
__pycache__/
*.pyc
```

### 3. requirements.txt 최신화

```powershell
pip freeze > requirements.txt
```

---

## 참고 문서

- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Supabase 공식 문서](https://supabase.com/docs)
- [Supabase REST API](https://supabase.com/docs/reference/rest/introduction)
- [Plotly 시각화](https://plotly.com/python/)

---

## 작업 이력

| 날짜 | 작업 | 상태 |
|------|------|------|
| 2026-06-04 | CSV → Supabase 데이터 마이그레이션 | ✅ |
| 2026-06-04 | Streamlit 앱 Supabase 연결 | ✅ |
| 2026-06-04 | Streamlit Secrets 설정 | ✅ |
| 2026-06-04 | 대시보드 시각화 완성 | ✅ |

---

## 문의 및 피드백

- GitHub Issues: [프로젝트 이슈](https://github.com/mitybomb-cloud/cloud)
- 작성자: Claude Code
