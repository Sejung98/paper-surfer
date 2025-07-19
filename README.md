# Paper Surfer 📚

PubMed API를 활용한 자동 논문 수집 및 분석 도구

## 🚀 주요 기능

### 1. 자동 논문 수집
- PubMed API를 통한 안정적인 논문 검색
- 키워드 기반 맞춤형 검색
- 마크다운 형식으로 자동 저장

### 2. 스마트 분석 시스템
- 키워드 매칭 점수 계산
- 저자명, 제목, 초록 분석
- 중요도별 자동 분류 (고/중/저)

### 3. 자동 스케줄링
- 주간 자동 실행
- 커스텀 스케줄 설정
- 배치 파일을 통한 간편 실행

## 🔧 설치 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 설정 파일 구성
`config.py`에서 필요한 설정을 변경하세요.

## 📋 사용 방법

### 1. 기본 실행
```bash
python main.py
```

### 2. 배치 파일 실행 (Windows)
```bash
run_paper_surfer.bat
```

### 3. 스케줄러 실행
```bash
python main.py --scheduler
```

## ⚙️ 중요 설정 가이드

### 1. 검색 키워드 설정 (`config.py`)

```python
# 기본 검색 키워드
SEARCH_KEYWORDS = [
    "cancer",    
    "breast cancer",
    "cancer genomics", 
    "sequencing",
    "mutation",
    "evolution",
    "trajectory",
    "tumor",
    "somatic",
    "germline",
    "Van loo",      # 저자명 검색
    "Swanton"       # 저자명 검색
]

# 필수 키워드 (모든 논문에 포함되어야 함)
REQUIRED_KEYWORDS = [
    "cancer"
]

# 우선순위 키워드 (점수 가중치 적용)
PRIORITY_KEYWORDS = [
    "breast cancer",
    "cancer evolution",
    "evolution", 
    "clonal",
    "whole genome duplication",
    "WGD",
    "WGS", 
    "SNV",
    "CNV"
]
```

### 2. 스케줄링 설정

```python
# 자동 실행 스케줄
SCHEDULE_ENABLED = True
SCHEDULE_TIME = "02:00"  # 새벽 2시
SCHEDULE_DAYS = ["saturday"]  # 매주 토요일

# 다른 스케줄 옵션:
# SCHEDULE_DAYS = ["monday", "wednesday", "friday"]  # 주 3회
# SCHEDULE_DAYS = ["sunday"]  # 매주 일요일
# SCHEDULE_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]  # 평일 매일
```

### 3. 날짜 필터링 설정

```python
# 날짜 필터 활성화/비활성화
ENABLE_DATE_FILTER = True

# 검색 기간 설정 (현재 날짜 기준)
SEARCH_DAYS_BACK = 7  # 지난 7일

# 프리셋 옵션:
# SEARCH_DAYS_BACK = 7     # 지난 주 (매우 제한적)
# SEARCH_DAYS_BACK = 30    # 지난 달 (권장)
# SEARCH_DAYS_BACK = 90    # 지난 3개월 (더 많은 결과)
# SEARCH_DAYS_BACK = 365   # 지난 1년 (매우 광범위)
```

### 4. PubMed API 설정

```python
# PubMed API 키 (권장)
PUBMED_API_KEY = "your_api_key_here"

# 연락처 정보 (필수)
CONTACT_EMAIL = "your.email@example.com"

# 요청 제한 설정
MAX_REQUESTS_PER_SECOND = 10  # API 키 있을 때: 10, 없을 때: 3
```

## 📊 점수 산출 시스템

### 키워드 매칭 점수
- **기본 점수**: 키워드 매칭 시 1점
- **필수 키워드**: 가중치 1.0
- **우선순위 키워드**: 가중치 2.0
- **제목 매칭**: +0.5점 보너스
- **초록 매칭**: +0.2점 보너스
- **저자 매칭**: +0.3점 보너스

### 중요도 분류
- **고중요도 (High)**: 0.7점 이상
- **중중요도 (Medium)**: 0.4~0.7점
- **저중요도 (Low)**: 0.0~0.4점

## 📁 출력 구조

```
output/
└── papers/
    └── YYYY-MM-DD/
        ├── high_relevance/     # 고중요도 논문
        ├── medium_relevance/   # 중중요도 논문
        └── low_relevance/      # 저중요도 논문
```

### 파일명 형식
```
[저널명]_[논문제목]_PMID_[ID].md
```

## 🔍 논문 검색 로직

1. **ESearch API**: 각 키워드로 PMID 수집
2. **EFetch API**: 상세 정보 수집 (제목, 초록, 저자 등)
3. **키워드 분석**: 제목, 초록, 저자명에서 키워드 매칭
4. **점수 계산**: 복합 점수 시스템으로 중요도 평가
5. **카테고리 분류**: 점수 기준으로 폴더 분류
6. **마크다운 저장**: 구조화된 형식으로 저장

## 🛠️ 고급 설정

### 저널 우선순위
```python
HIGH_IMPACT_JOURNALS = [
    "nature", "cell", "science", "nature genetics", 
    "nature medicine", "cell metabolism", "cancer cell",
    "nature cancer", "nature biotechnology", "nature methods",
    "jama", "nejm", "lancet", "bmj", "pnas",
    "cancer research", "clinical cancer research", 
    "journal of clinical oncology", "cancer discovery",
    "nature communications", "elife", "plos one",
    "genome research", "genome biology", "bioinformatics"
]
```

### 필터링 옵션
```python
FILTER_SETTINGS = {
    "min_abstract_length": 50,
    "languages": ["english"],
    "publication_types": [
        "Journal Article",
        "Review", 
        "Meta-Analysis",
        "Systematic Review"
    ]
}
```

## 🚨 사용 시 주의사항

1. **API 제한**: PubMed API 사용 제한 준수
2. **네트워크**: 안정적인 인터넷 연결 필요
3. **저장공간**: 수집된 파일이 누적되므로 정기적 정리 필요
4. **연락처**: CONTACT_EMAIL 반드시 실제 이메일로 설정

## 📞 문의

이슈나 버그 신고는 GitHub Issues를 이용해 주세요.

---

**주의**: 이 도구는 연구 목적으로만 사용하며, 논문 저작권을 존중해야 합니다. 

# Paper Surfer 사용법 요약

## 1. 설치 및 준비

   ```bash
   pip install -r requirements.txt
   ```

## 2. 설정(config.py) 주요 포인트

- **검색 키워드**:  
  `SEARCH_KEYWORDS`에 원하는 논문 키워드, 저자명 등 추가  
  예시: `"cancer", "breast cancer", "Van loo", "Swanton"`

- **날짜 필터**:  
  `ENABLE_DATE_FILTER = True`  
  `SEARCH_DAYS_BACK = 7`  # 최근 7일 논문만

- **스케줄 설정**:  
  `SCHEDULE_ENABLED = True`  
  `SCHEDULE_TIME = "02:00"`  
  `SCHEDULE_DAYS = ["saturday"]`  # 매주 토요일 새벽 2시

- **PubMed API 키/이메일**:  
  `PUBMED_API_KEY`, `CONTACT_EMAIL` 반드시 본인 정보로 입력

---

## 3. 실행 방법

### (1) 수동 실행

```bash
python main.py --once
```
- 설정된 키워드로 논문을 한 번만 수집

### (2) 대화형 실행

   ```bash
python main.py
   ```
- 키워드, 결과 수 등 직접 입력하며 논문 수집

### (3) 스케줄러(자동) 실행

```bash
python main.py --scheduler
```
- config.py에 설정된 요일/시간에 맞춰 자동 실행

### (4) Windows에서 배치 파일로 실행

```bash
run_paper_surfer.bat
```
- 로그는 `logs/scheduler.log`에서 확인

### (5) Windows 작업 스케줄러 등록
- `run_paper_surfer.bat`을 매주 토요일 2시로 예약 등록하면 완전 자동화

---

## 4. 결과 파일 구조

```
output/
└── papers/
    └── YYYY-MM-DD/
        ├── high_relevance/
        ├── medium_relevance/
        └── low_relevance/
```
- 파일명: `[저널명]_[논문제목]_PMID_[ID].md`

---

## 5. 자주 쓰는 설정/팁

- **키워드 추가**: `config.py`의 `SEARCH_KEYWORDS`에 원하는 단어/저자명 추가
- **날짜 범위 변경**: `SEARCH_DAYS_BACK` 값만 바꾸면 됨 (예: 30, 90, 365)
- **스케줄 변경**: `SCHEDULE_TIME`, `SCHEDULE_DAYS` 수정
- **저널 우선순위**: `HIGH_IMPACT_JOURNALS`에 저널명 추가 가능

---

## 6. 참고/주의사항

- PubMed API 키와 이메일은 반드시 본인 것으로 설정
- 논문 저작권을 반드시 준수
- 수집 파일이 많아지면 주기적으로 output 폴더 정리 

---

## 7. Windows에서 완전 자동화 (작업 스케줄러 등록)

### (1) 작업 스케줄러 실행
- 시작 메뉴에서 "작업 스케줄러" 또는 "Task Scheduler" 검색 후 실행

### (2) 새 작업 만들기
- 오른쪽에서 "작업 만들기..." 클릭

### (3) 일반 탭
- 이름: 예) Paper Surfer 자동 논문 수집
- 설명: (선택) PubMed 논문 자동 수집

### (4) 트리거(Trigger) 탭
- "새로 만들기" 클릭
- 시작: "일정"
- "매주" 선택, "토요일" 체크
- 시작 시간: 02:00:00 (새벽 2시)
- 확인 클릭

### (5) 동작(Action) 탭
- "새로 만들기" 클릭
- 동작: "프로그램 시작"
- 프로그램/스크립트: run_paper_surfer.bat의 전체 경로 입력
  - 예: C:\Users\sejung\Desktop\paper-surfer-main\run_paper_surfer.bat
- 시작 위치: 배치 파일이 있는 폴더 경로 입력
  - 예: C:\Users\sejung\Desktop\paper-surfer-main
- 확인 클릭

### (6) 조건/설정 탭
- 필요에 따라 "컴퓨터가 AC 전원에 연결된 경우에만 시작" 등 체크 해제

### (7) 저장 및 완료
- "확인"을 눌러 작업 저장
- 관리자 권한이 필요할 수 있으니, 권한 요청 시 "예" 클릭

### (8) 테스트
- 작업 스케줄러에서 만든 작업을 우클릭 → "실행"을 눌러 수동 테스트 가능
- 로그는 logs/scheduler.log에서 확인

---

이렇게 하면 컴퓨터가 켜져 있는 한, 매주 토요일 새벽 2시에 논문 수집이 자동으로 실행됩니다! 

---

## 🛠️ 환경변수 추가 방법

### 1. 배치 파일에서 임시로 지정
```bat
@echo off
set PYTHONIOENCODING=utf-8
python main.py --once
```
(이미 있는 run_paper_surfer.bat에서 python 실행 전에 set PYTHONIOENCODING=utf-8 한 줄만 추가)

### 2. 작업 스케줄러에서 직접 지정
- "동작" 탭에서 "환경 변수"에 `PYTHONIOENCODING` = `utf-8` 추가

---

이렇게 하면 Paper Surfer가 한글, 이모지 등도 문제 없이 출력할 수 있습니다!  
필요하다면 배치 파일을 바로 수정해드릴 수도 있습니다.  
수정 원하시면 말씀해 주세요! 

---

## 1️⃣ PowerShell/명령 프롬프트에서 찾기

아래 명령어를 차례로 입력해보세요.

### 1. 가장 흔한 경로들 직접 확인

```powershell
dir "C:\Users\sejung\AppData\Local\Programs\Python" -Directory
dir "C:\Program Files\Python*" -Directory
dir "C:\Program Files (x86)\Python*" -Directory
```

### 2. 확실하게 찾기 (드라이브 전체 검색, 오래 걸릴 수 있음)

```powershell
<code_block_to_apply_changes_from>
```

### 3. Python이 실행되는지 확인

```powershell
py --version
```
- 만약 `py` 명령이 동작하면, 아래로도 확인:
```powershell
py -c "import sys; print(sys.executable)"
```
- 이 경로가 Python의 실제 실행 파일 경로입니다.

---

## 2️⃣ Windows 메뉴에서 찾기

- **시작 메뉴** → "Python" 검색  
- "Python 3.x (64-bit)" 아이콘 우클릭 → "파일 위치 열기"  
- 바로가기 우클릭 → "속성" → "대상"에서 경로 확인

---

## 3️⃣ Python 설치 경로 예시

- `C:\Users\sejung\AppData\Local\Programs\Python\Python311\`
- `C:\Program Files\Python311\`
- `C:\Program Files (x86)\Python310\`

---

## 4️⃣ Python이 여러 개 설치된 경우

- 위 방법으로 여러 경로가 나올 수 있습니다.
- 가장 최신 버전의 python.exe가 있는 폴더를 PATH에 추가하면 됩니다.

---

## 5️⃣ 찾은 경로를 PATH에 추가하는 방법

1. **경로 복사** (예: `C:\Users\sejung\AppData\Local\Programs\Python\Python311\`)
2. 시작 메뉴 → "환경 변수" → "시스템 환경 변수 편집" → "환경 변수(N)..."
3. "Path" → "편집" → "새로 만들기" → 복사한 경로 붙여넣기 → 확인

---

경로 찾기가 어렵거나, 결과를 붙여넣어주시면 추가로 도와드릴 수 있습니다!  
원하시면 위 명령어 중 하나를 실행해보시고, 결과를 알려주세요. 