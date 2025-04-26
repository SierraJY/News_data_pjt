<template>
  <div class="auth-container">
    <div class="auth-box">
      <h1 class="auth-title">로그인</h1>
      
      <form @submit.prevent="handleLogin" class="auth-form">
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
        
        <div v-if="error" class="error-container">
          {{ error }}
        </div>
        
        <button type="submit" class="auth-button" :disabled="loading">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>
      
      <div class="auth-links">
        계정이 없으신가요? <RouterLink to="/register">회원가입</RouterLink>
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

// 로딩, 에러 상태
const loading = computed(() => authStore.loading);
const error = computed(() => authStore.error);

// 로그인 처리
async function handleLogin() {
  if (!username.value || !password.value) {
    return;
  }
  
  const success = await authStore.login(username.value, password.value);
  
  if (success) {
    router.push('/'); // 로그인 성공 시 메인 페이지로 이동
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
}

.auth-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
  color: #0c3057;
}

.auth-form {
  .form-group {
    margin-bottom: 15px;
    
    label {
      display: block;
      margin-bottom: 5px;
      font-weight: 500;
    }
    
    input {
      width: 100%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 16px;
      
      &:focus {
        outline: none;
        border-color: #0c3057;
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
  
  &:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  &:hover:not(:disabled) {
    background-color: #0a2744;
  }
}

.auth-links {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  
  a {
    color: #0c3057;
    text-decoration: none;
    
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
}
</style>