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
      
      <!-- 검색창 -->
      <div class="header__search">
        <form @submit.prevent="handleSearch" class="search-form">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="뉴스 검색..." 
            class="search-input"
            @keydown.enter="handleSearch"
          />
          <button type="submit" class="search-btn">
            🔍
          </button>
        </form>
      </div>
      
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
import { computed, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const searchQuery = ref('');

// 현재 URL에서 검색어 가져오기
searchQuery.value = route.query.search || '';

// 인증 상태
const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user);

// 로그아웃 처리
function handleLogout() {
  authStore.logout();
  router.push('/login');
}

// 검색 처리
function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({
      path: '/news',
      query: { search: searchQuery.value.trim() }
    });
  } else {
    // 검색어가 비어있으면 쿼리 파라미터 제거
    router.push({ path: '/news' });
  }
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
  
  &__search {
    flex: 1;
    max-width: 300px;
    margin: 0 20px;
    
    .search-form {
      display: flex;
      position: relative;
    }
    
    .search-input {
      width: 100%;
      padding: 8px 40px 8px 12px;
      border: 1px solid #ddd;
      border-radius: 20px;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
      
      &:focus {
        border-color: #0c3057;
      }
    }
    
    .search-btn {
      position: absolute;
      right: 5px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      font-size: 16px;
      cursor: pointer;
      padding: 5px;
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
    
    &__nav, &__search, &__auth {
      width: 100%;
      max-width: 100%;
      justify-content: center;
      margin: 5px 0;
    }
  }
}
</style>