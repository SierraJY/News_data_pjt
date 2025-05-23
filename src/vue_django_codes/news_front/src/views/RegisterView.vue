<template>
  <div class="auth-container">
    <div class="auth-box">
      <h1 class="auth-title">회원가입</h1>
      
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label for="username">아이디</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            placeholder="아이디를 입력하세요"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="비밀번호를 입력하세요"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="passwordConfirm">비밀번호 확인</label>
          <input 
            type="password" 
            id="passwordConfirm" 
            v-model="passwordConfirm" 
            placeholder="비밀번호를 다시 입력하세요"
            required
          >
          <p v-if="passwordError" class="error-text">{{ passwordError }}</p>
        </div>
        
        <div v-if="error" class="error-container">
          {{ error }}
        </div>
        
        <button type="submit" class="auth-button" :disabled="loading">
          {{ loading ? '처리 중...' : '회원가입' }}
        </button>
      </form>
      
      <div class="auth-links">
        이미 계정이 있으신가요? <RouterLink to="/login">로그인</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { RouterLink } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();

const username = ref('');
const password = ref('');
const passwordConfirm = ref('');

// 비밀번호 일치 여부 확인
const passwordError = computed(() => {
  if (passwordConfirm.value && password.value !== passwordConfirm.value) {
    return '비밀번호가 일치하지 않습니다';
  }
  return null;
});

// 로딩, 에러 상태
const loading = computed(() => authStore.loading);
const error = computed(() => authStore.error);

// 회원가입 처리
async function handleRegister() {
  // 기본 유효성 검사
  if (!username.value || !password.value) {
    return;
  }
  
  // 비밀번호 일치 여부 확인
  if (password.value !== passwordConfirm.value) {
    return;
  }
  
  // 회원가입 요청
  const success = await authStore.register(username.value, password.value);
  
  if (success) {
    router.push('/'); // 회원가입 성공 시 메인 페이지로 이동
  }
}
</script>

<style scoped lang="scss">
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
}

.auth-box {
  background-color: white;
  border-radius: 8px;
  padding: 30px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  
  .dark-mode & {
    background-color: var(--c-card-bg);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  }
}

.auth-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
  color: #0c3057;
  
  .dark-mode & {
    color: var(--c-main);
  }
}

.auth-form {
  .form-group {
    margin-bottom: 15px;
    
    label {
      display: block;
      margin-bottom: 5px;
      font-weight: 500;
      
      .dark-mode & {
        color: var(--c-text);
      }
    }
    
    input {
      width: 100%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 16px;
      
      .dark-mode & {
        background-color: var(--c-input-bg);
        border-color: var(--c-input-border);
        color: var(--c-text);
      }
      
      &:focus {
        outline: none;
        border-color: #0c3057;
        
        .dark-mode & {
          border-color: var(--c-main);
        }
      }
    }
  }
}

.auth-button {
  width: 100%;
  padding: 12px;
  background-color: #0c3057;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
  
  .dark-mode & {
    background-color: var(--c-main);
  }
  
  &:disabled {
    background-color: #cccccc;
    
    .dark-mode & {
      background-color: #444;
    }
  }
  
  &:hover:not(:disabled) {
    background-color: #0a2744;
    
    .dark-mode & {
      background-color: #0055c4;
    }
  }
}

.auth-links {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  
  .dark-mode & {
    color: var(--c-text);
  }
  
  a {
    color: #0c3057;
    text-decoration: none;
    
    .dark-mode & {
      color: var(--c-main);
    }
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.error-container {
  background-color: #ffebee;
  color: #d32f2f;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
  
  .dark-mode & {
    background-color: rgba(211, 47, 47, 0.2);
    color: #ff6b6b;
  }
}

.error-text {
  color: #d32f2f;
  font-size: 12px;
  margin-top: 4px;
  margin-bottom: 0;
  
  .dark-mode & {
    color: #ff6b6b;
  }
}
</style>