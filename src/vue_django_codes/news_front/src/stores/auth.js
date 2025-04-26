import { defineStore } from 'pinia';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // 사용자 토큰 정보
    accessToken: null,
    refreshToken: null,
    user: null,
    loading: false,
    error: null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },
  
  actions: {
    // 로그인 요청
    async login(username, password) {
      this.loading = true;
      this.error = null;
      
      try {
        // JWT 토큰 요청
        const response = await axios.post(`${API_BASE_URL}/api/users/login/`, {
          username,
          password
        });
        
        // 토큰 저장
        this.accessToken = response.data.access;
        this.refreshToken = response.data.refresh;
        
        // Axios 기본 헤더에 인증 토큰 설정
        this.setAuthHeader();
        
        // 사용자 정보 설정
        this.user = { username };
        
        return true;
      } catch (error) {
        this.error = 
          error.response?.data?.detail || 
          '로그인 중 오류가 발생했습니다. 아이디와 비밀번호를 확인해주세요.';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    // 회원가입 요청
    async register(username, password) {
      this.loading = true;
      this.error = null;
      
      try {
        // 회원가입 요청
        await axios.post(`${API_BASE_URL}/api/users/register/`, {
          username,
          password
        });
        
        // 회원가입 후 자동 로그인
        return await this.login(username, password);
      } catch (error) {
        this.error = 
          error.response?.data?.username?.[0] || 
          error.response?.data?.password?.[0] || 
          '회원가입 중 오류가 발생했습니다.';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    // 로그아웃
    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      
      // 인증 헤더 제거
      axios.defaults.headers.common['Authorization'] = '';
    },
    
    // 토큰 갱신
    async refreshAuthToken() {
      try {
        if (!this.refreshToken) return false;
        
        const response = await axios.post(`${API_BASE_URL}/api/users/token/refresh/`, {
          refresh: this.refreshToken
        });
        
        this.accessToken = response.data.access;
        this.setAuthHeader();
        return true;
      } catch (error) {
        this.logout();
        return false;
      }
    },
    
    // 인증 헤더 설정
    setAuthHeader() {
      if (this.accessToken) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
      }
    },
    
    // 초기화: 저장된 토큰으로 상태 복원
    initAuth() {
      this.setAuthHeader();
    }
  },
  
  persist: {
    // LocalStorage에 인증 정보 유지
    storage: localStorage,
    paths: ['accessToken', 'refreshToken', 'user'],
  },
});