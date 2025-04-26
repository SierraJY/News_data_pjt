<template>
  <header class="header">
    <div class="header__container">
      <!-- 로고 및 사이트 제목 -->
      <RouterLink to="/" class="header__logo">
        📰 뉴스 큐레이션
      </RouterLink>
      
      <!-- 네비게이션 메뉴 -->
      <nav class="header__nav">
        <RouterLink to="/news" class="nav-link">뉴스 목록</RouterLink>
        <RouterLink to="/dashboard" class="nav-link">대시보드</RouterLink>
      </nav>
      
      <!-- 인증 관련 버튼 -->
      <div class="header__auth">
        <template v-if="isAuthenticated">
          <span class="user-info">{{ user?.username }}</span>
          <button @click="handleLogout" class="auth-btn logout-btn">로그아웃</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="auth-btn login-btn">로그인</RouterLink>
          <RouterLink to="/register" class="auth-btn register-btn">회원가입</RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();

// 인증 상태
const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user);

// 로그아웃 처리
function handleLogout() {
  authStore.logout();
  router.push('/login');
}
</script>

<style scoped lang="scss">
.header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 15px 0;
  
  &__container {
    max-width: 1280px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 15px;
  }
  
  &__logo {
    font-size: 20px;
    font-weight: 700;
    color: #0c3057;
    text-decoration: none;
  }
  
  &__nav {
    display: flex;
    gap: 20px;
    
    .nav-link {
      color: #333;
      text-decoration: none;
      font-weight: 500;
      
      &:hover, &.router-link-active {
        color: #0c3057;
      }
    }
  }
  
  &__auth {
    display: flex;
    align-items: center;
    gap: 10px;
    
    .user-info {
      font-size: 14px;
      margin-right: 5px;
    }
    
    .auth-btn {
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      text-decoration: none;
      
      &.login-btn {
        color: #0c3057;
        background-color: transparent;
        border: 1px solid #0c3057;
        
        &:hover {
          background-color: #f0f4f9;
        }
      }
      
      &.register-btn, &.logout-btn {
        color: white;
        background-color: #0c3057;
        border: 1px solid #0c3057;
        
        &:hover {
          background-color: #0a2744;
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .header {
    &__container {
      flex-direction: column;
      gap: 15px;
    }
    
    &__nav, &__auth {
      width: 100%;
      justify-content: center;
    }
  }
}
</style>