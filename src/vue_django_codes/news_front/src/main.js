import "@/assets/scss/main.scss";
import { createApp } from "vue";
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";
import App from "@/App.vue";
import router from "@/router";
import { createPinia } from "pinia";
import axios from "axios";
import { useAuthStore } from "@/stores/auth";
import { useThemeStore } from "@/stores/theme";

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);

// Axios 인터셉터 설정
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // 토큰 만료 에러(401)이고, 토큰 리프레시를 시도하지 않은 요청인 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const authStore = useAuthStore();
      // 토큰 리프레시 시도
      const refreshed = await authStore.refreshAuthToken();
      
      if (refreshed) {
        // 리프레시 성공 시 원래 요청 재시도
        return axios(originalRequest);
      }
    }
    
    return Promise.reject(error);
  }
);

// 애플리케이션 마운트 전에 인증 상태 초기화
const authStore = useAuthStore();
authStore.initAuth();

// 테마 초기화
const themeStore = useThemeStore();
themeStore.initTheme();

app.use(router);
app.mount("#app");