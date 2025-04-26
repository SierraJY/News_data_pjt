# 뉴스 큐레이팅 서비스 프로젝트

## 프로젝트 개요
이 프로젝트는 사용자 맞춤형 뉴스 큐레이팅 서비스로, Django 백엔드와 Vue.js 프론트엔드로 구성되어 있습니다. 사용자는 뉴스를 조회하고, 좋아요를 누르며, 개인화된 대시보드를 통해 뉴스 소비 패턴을 확인할 수 있습니다.

## 주요 기능

- **회원가입 및 로그인**  
  개인 맞춤형 뉴스 큐레이팅 기능 제공

- **AI 맞춤 뉴스 추천**  
  카테고리별, 최신순/추천순 필터 제공

- **뉴스 상세 페이지**  
  기사 '좋아요' 저장, 관련 뉴스 사이드바 제공

- **대시보드**  
  사용자 활동 시각화: 관심 카테고리, 주요 키워드, 주간 기사 수, 좋아요한 뉴스 등

## 디렉토리 구조

```
/
├── .git/                    # Git 저장소 정보
├── .gitignore               # Git 버전 관리 제외 파일 설정
├── news_backend/            # 백엔드 프로젝트 (Django)
│   ├── news_backend/        # Django 프로젝트 설정 폴더
│   ├── manage.py            # Django 관리 스크립트
│   ├── news/                # 뉴스 관련 앱
│   │   ├── migrations/      # 데이터베이스 마이그레이션 파일
│   │   ├── __init__.py      # 패키지 초기화 파일
│   │   ├── admin.py         # Django 관리자 페이지 설정
│   │   ├── apps.py          # 앱 설정
│   │   ├── models.py        # 데이터 모델 정의 (News, Like, ArticleView 등)
│   │   ├── serializers.py   # API 직렬화 도구
│   │   ├── tests.py         # 테스트 코드
│   │   ├── urls.py          # URL 라우팅 설정
│   │   └── views.py         # API 뷰 함수 및 클래스
│   ├── users/               # 사용자 관리 앱
│   ├── requirements.txt     # Python 패키지 의존성 파일
│   └── venv/                # Python 가상 환경
│
└── news_front/              # 프론트엔드 프로젝트 (Vue.js)
    ├── node_modules/        # Node.js 패키지
    ├── public/              # 정적 파일 디렉토리
    ├── src/                 # 소스 코드
    │   ├── assets/          # 이미지, CSS 등 자산 파일
    │   ├── common/          # 공통 컴포넌트 및 유틸리티
    │   ├── components/      # Vue 컴포넌트
    │   ├── composables/     # Vue 컴포저블 함수
    │   ├── router/          # Vue Router 설정
    │   ├── stores/          # Pinia/Vuex 상태 관리
    │   ├── utils/           # 유틸리티 함수
    │   ├── views/           # Vue 페이지 컴포넌트
    │   ├── App.vue          # 루트 Vue 컴포넌트
    │   └── main.js          # Vue 애플리케이션 진입점
    ├── .gitignore           # Git 버전 관리 제외 파일 설정 (프론트엔드)
    ├── index.html           # Vue 애플리케이션 HTML 템플릿
    ├── jsconfig.json        # JavaScript 설정 파일
    ├── package.json         # Node.js 패키지 정보 및 스크립트
    ├── package-lock.json    # Node.js 패키지 의존성 상세 정보
    ├── vite.config.js       # Vite 빌드 도구 설정
    └── README.md            # 프론트엔드 프로젝트 설명서
```

## 백엔드 실행 방법

1. Python 가상 환경 활성화
```bash
cd news_backend
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

4. 서버 실행
```bash
python manage.py runserver
```

## 프론트엔드 실행 방법

1. 의존성 설치
```bash
cd news_front
npm install
```

2. 환경 변수 설정 (.env 파일)
```
VITE_BASE_URL='http://localhost:8000'
```

3. 개발 서버 실행
```bash
npm run dev
```

4. 프로덕션 빌드
```bash
npm run build
```

## 주요 모델

### News
뉴스 기사 정보를 저장하는 모델
- 제목, 내용, 작성일, 카테고리 등 포함

### Like
사용자가 좋아요를 누른 뉴스 기사를 추적하는 모델
- 사용자 ID, 뉴스 ID, 좋아요 일시 포함

### ArticleView
사용자가 조회한 뉴스 기사를 추적하는 모델
- 사용자 ID, 뉴스 ID, 조회 일시 포함 