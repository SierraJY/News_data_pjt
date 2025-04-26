// 404 에러 페이지를 위한 NotFoundView 컴포넌트 임포트
import NotFoundView from "@/views/NotFoundView.vue";
// Vue Router의 핵심 함수 임포트 - 라우터 생성 및 히스토리 모드 설정
import { createRouter, createWebHistory } from "vue-router";
// 뉴스 목록 페이지 컴포넌트 임포트
import NewsView from "@/views/NewsView.vue";
// 뉴스 상세 페이지 컴포넌트 임포트
import NewsDetailView from "@/views/NewsDetailView.vue";
// 대시보드 페이지 컴포넌트 임포트
import DashBoardView from "@/views/DashBoardView.vue";
// 로그인 페이지 컴포넌트 임포트
import LoginView from "@/views/LoginView.vue";
// 회원가입 페이지 컴포넌트 임포트
import RegisterView from "@/views/RegisterView.vue";
// 인증 스토어 임포트
import { useAuthStore } from "@/stores/auth";

// Vue Router 인스턴스 생성
const router = createRouter({
  // HTML5 History API를 사용한 라우팅 모드 설정 (URL에 #이 없는 형태)
  // 루트 경로("/")를 기준으로 히스토리 생성
  history: createWebHistory("/"),
  // 라우트 경로 정의
  routes: [
    {
      // 루트 경로("/")로 접속 시
      path: "/",
      // "/news" 경로로 리다이렉트 처리
      redirect: "/news",
    },
    {
      // 뉴스 목록 페이지 경로
      path: "/news",
      // 라우트 이름 (프로그래밍 방식으로 라우팅 시 사용)
      name: "News",
      // 표시할 컴포넌트
      component: NewsView,
    },
    {
      // 뉴스 상세 페이지 경로 - 동적 매개변수 id 사용
      path: "/news/:id",
      // 라우트 이름
      name: "newsDetail",
      // 표시할 컴포넌트
      component: NewsDetailView,
    },
    {
      // 대시보드 페이지 경로
      path: "/dashboard",
      // 라우트 이름
      name: "dashboard",
      // 표시할 컴포넌트
      component: DashBoardView,
      // 인증이 필요한 페이지
      meta: { requiresAuth: true }
    },
    {
      // 로그인 페이지 경로
      path: "/login",
      name: "login",
      component: LoginView,
      // 이미 로그인된 경우 접근 불가
      meta: { requiresGuest: true }
    },
    {
      // 회원가입 페이지 경로
      path: "/register",
      name: "register",
      component: RegisterView,
      // 이미 로그인된 경우 접근 불가
      meta: { requiresGuest: true }
    },
    {
      // 정의되지 않은 모든 경로에 대한 처리 (404 에러 페이지)
      // pathMatch(.*)*는 모든 경로에 일치하는 정규식 패턴
      path: "/:pathMatch(.*)*",
      // 404 페이지 컴포넌트 표시
      component: NotFoundView,
    },
  ],
});

// 네비게이션 가드 설정
router.beforeEach((to, from, next) => {
  // Pinia store는 setup 외부에서 사용할 때 useStore() 방식으로 접근
  const authStore = useAuthStore();
  
  // 인증이 필요한 페이지에 접근할 때
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 로그인 페이지로 리다이렉트
    next({ name: 'login' });
  } 
  // 로그인 상태에서 게스트 전용 페이지(로그인, 회원가입)에 접근할 때
  else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // 메인 페이지로 리다이렉트
    next({ name: 'News' });
  } 
  // 그 외의 경우는 정상적으로 라우팅
  else {
    next();
  }
});

// 생성된 라우터 인스턴스 내보내기
export default router;