<template>
  <header class="header">
    <div class="header__container">
      
      <!-- 네비게이션 메뉴 - 아이콘 추가 -->
      <nav class="header__nav">
        <RouterLink to="/news" class="nav-link">
          <span class="nav-icon">📋</span>
          <span>뉴스 목록</span>
        </RouterLink>
        <RouterLink to="/dashboard" class="nav-link">
          <span class="nav-icon">📊</span>
          <span>대시보드</span>
        </RouterLink>
      </nav>
      
      <!-- 검색창 -->
      <div class="header__search">
        <form @submit.prevent="handleSearch" class="search-form">
          <div class="search-icon">🔍</div>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="뉴스 검색..." 
            class="search-input"
            @keydown.enter="handleSearch"
          />
          <button type="submit" class="search-btn">
            검색
          </button>
        </form>
      </div>
      
      <!-- 인증 관련 버튼 및 다크모드 토글 -->
      <div class="header__auth">
        <!-- 다크모드 토글 버튼 -->
        <button @click="toggleDarkMode" class="theme-toggle-btn">
          <span class="theme-icon" v-if="isDarkMode">☀️</span>
          <span class="theme-icon" v-else>🌙</span>
        </button>
        
        <template v-if="isAuthenticated">
          <span class="user-info">
            <span class="user-icon">👤</span>
            {{ user?.username }}
          </span>
          <button @click="handleLogout" class="auth-btn logout-btn">
            <span class="btn-icon">🚪</span>
            로그아웃
          </button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="auth-btn login-btn">
            <span class="btn-icon">🔑</span>
            로그인
          </RouterLink>
          <RouterLink to="/register" class="auth-btn register-btn">
            <span class="btn-icon">✏️</span>
            회원가입
          </RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';
import { computed, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const themeStore = useThemeStore();
const searchQuery = ref('');

// 현재 URL에서 검색어 가져오기
searchQuery.value = route.query.search || '';

// 인증 상태
const isAuthenticated = computed(() => authStore.isAuthenticated);
const user = computed(() => authStore.user);

// 다크모드 상태
const isDarkMode = computed(() => themeStore.isDarkMode);

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

// 다크모드 토글
function toggleDarkMode() {
  themeStore.toggleDarkMode();
}
</script>

<style scoped lang="scss">
.header {
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  padding: 12px 0;
  position: sticky;
  top: 0;
  z-index: 100;
  
  .dark-mode & {
    background-color: var(--c-bg);
    color: var(--c-text);
  }
  
  &__container {
    max-width: 1280px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
  }
  
  &__nav {
    display: flex;
    gap: 30px;
    flex: 0 0 auto;
    
    .nav-link {
      color: #333;
      text-decoration: none;
      font-weight: 500;
      position: relative;
      padding: 5px 0;
      display: flex;
      align-items: center;
      gap: 6px;
      
      .dark-mode & {
        color: var(--c-text);
      }
      
      .nav-icon {
        font-size: 18px;
      }
      
      &::after {
        content: '';
        position: absolute;
        width: 0;
        height: 2px;
        bottom: 0;
        left: 0;
        background-color: #0c3057;
        transition: width 0.3s;
        
        .dark-mode & {
          background-color: var(--c-main);
        }
      }
      
      &:hover, &.router-link-active {
        color: #0c3057;
        
        .dark-mode & {
          color: var(--c-main);
        }
        
        &::after {
          width: 100%;
        }
      }
    }
  }
  
  &__search {
    flex: 1;
    max-width: 450px;
    margin: 0 20px;
    
    .search-form {
      display: flex;
      position: relative;
      align-items: center;
      background-color: #f5f7fb;
      border-radius: 30px;
      padding: 2px;
      transition: all 0.3s;
      border: 1px solid transparent;
      min-width: 200px;
      
      .dark-mode & {
        background-color: var(--c-input-bg);
      }
      
      &:focus-within {
        background-color: #fff;
        border-color: #0c3057;
        box-shadow: 0 2px 8px rgba(12, 48, 87, 0.1);
        
        .dark-mode & {
          background-color: var(--c-card-bg);
          border-color: var(--c-main);
        }
      }
    }
    
    .search-icon {
      position: absolute;
      left: 15px;
      font-size: 16px;
      color: #0c3057;
      opacity: 0.7;
      z-index: 1;
      
      .dark-mode & {
        color: var(--c-text);
      }
    }
    
    .search-input {
      width: 100%;
      min-width: 0;
      padding: 12px 12px 12px 45px;
      border: none;
      border-radius: 30px;
      font-size: 15px;
      background: transparent;
      outline: none;
      color: #333;
      
      .dark-mode & {
        color: var(--c-text);
      }
      
      &::placeholder {
        color: #8a9ab0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        
        .dark-mode & {
          color: var(--c-gray-500);
        }
      }
    }
    
    .search-btn {
      background-color: #0c3057;
      color: white;
      border: none;
      border-radius: 24px;
      padding: 10px 20px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      margin-right: 2px;
      white-space: nowrap;
      flex-shrink: 0;
      
      .dark-mode & {
        background-color: var(--c-main);
      }
      
      &:hover {
        background-color: #0a2744;
        transform: translateY(-1px);
        
        .dark-mode & {
          background-color: #0055c4;
        }
      }
    }
  }
  
  &__auth {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 0 0 auto;
    
    .theme-toggle-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      cursor: pointer;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      padding: 0;
      font-size: 20px;
      background-color: rgba(0, 0, 0, 0.05);
      transition: all 0.3s;
      
      .dark-mode & {
        background-color: rgba(255, 255, 255, 0.1);
      }
      
      &:hover {
        background-color: rgba(0, 0, 0, 0.1);
        
        .dark-mode & {
          background-color: rgba(255, 255, 255, 0.2);
        }
      }
      
      .theme-icon {
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }
    
    .user-info {
      font-size: 14px;
      margin-right: 5px;
      color: #555;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 4px;
      
      .dark-mode & {
        color: var(--c-text);
      }
      
      .user-icon {
        font-size: 16px;
      }
    }
    
    .auth-btn {
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 6px;
      
      .btn-icon {
        font-size: 14px;
      }
      
      &.login-btn {
        color: white;
        background-color: #0c3057;
        border: 1px solid #0c3057;
        
        .dark-mode & {
          color: white;
          background-color: var(--c-main);
          border-color: var(--c-main);
        }
        
        &:hover {
          background-color: #0a2744;
          transform: translateY(-2px);
          box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
          
          .dark-mode & {
            background-color: #0055c4;
          }
        }
      }
      
      &.register-btn, &.logout-btn {
        color: white;
        background-color: #0c3057;
        border: 1px solid #0c3057;
        
        .dark-mode & {
          background-color: var(--c-main);
          border-color: var(--c-main);
        }
        
        &:hover {
          background-color: #0a2744;
          transform: translateY(-2px);
          box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
          
          .dark-mode & {
            background-color: #0055c4;
          }
        }
      }
    }
  }
}

@media (max-width: 900px) {
  .header {
    &__search {
      max-width: 300px;
      
      .search-btn {
        padding: 10px 15px;
      }
      
      .search-input {
        padding: 12px 12px 12px 40px;
      }
      
      .search-icon {
        left: 12px;
      }
    }
  }
}

@media (max-width: 800px) {
  .header {
    &__search {
      .search-btn {
        display: none;
      }
    }
  }
}

@media (max-width: 768px) {
  .header {
    &__container {
      flex-direction: column;
      gap: 15px;
      padding: 10px;
    }
    
    &__nav, &__search, &__auth {
      width: 100%;
      max-width: 100%;
      justify-content: center;
      margin: 5px 0;
    }
    
    &__search {
      order: -1;
      margin-bottom: 15px;
      
      .search-btn {
        display: block;
      }
    }
  }
}
</style>