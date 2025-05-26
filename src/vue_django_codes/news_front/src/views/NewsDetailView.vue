<!-- 
  뉴스 상세 페이지 컴포넌트
  특정 뉴스 기사의 상세 내용과 관련 기사를 보여주는 페이지
-->
<template>
  <!-- 뒤로가기 버튼 - 이전 페이지로 돌아가기 위한 버튼 -->
  <button @click="() => router.back()" class="back-btn"><LeftArrow /></button>
  
  <!-- 로딩 상태 표시 -->
  <div v-if="loading" class="loading">
    데이터를 불러오는 중입니다...
  </div>
  
  <!-- 오류 상태 표시 -->
  <div v-else-if="error" class="error">
    {{ error }}
  </div>
  
  <!-- 뉴스 데이터가 있을 때만 내용을 표시 (조건부 렌더링) -->
  <div v-else-if="news" class="news-detail">
    <!-- 메인 기사 컨테이너 -->
    <div class="article__container">
      <ContentBox>
        <div class="article">
          <!-- 기사 헤더 섹션: 카테고리, 제목, 작성자 정보 -->
          <div class="article__header">
            <!-- 카테고리 표시 버튼 (클릭 불가능) -->
            <StateButton type="state" size="sm" isActive disabled>{{
              news?.category
            }}</StateButton>
            
            <!-- 기사 제목 -->
            <h2 class="article__header-title">{{ news?.title }}</h2>
            
            <!-- 작성자 정보와 작성 날짜 -->
            <div class="article__header-writer">
              <span>{{ news.writer }}</span>
              <span> 🕒 {{ formatDate(news.write_date) }}</span>
            </div>
          </div>

          <!-- 기사 본문 내용 -->
          <p class="article__content">{{ news?.content }}</p>

          <!-- 기사 키워드 태그 목록 (키워드가 있을 경우에만 표시) -->
          <div v-if="parsedKeywords.length" class="article__tags">
            <StateButton
              v-for="(tag, index) in parsedKeywords"
              :key="index"
              type="tag"
              size="sm"
            >
              {{ tag }}
            </StateButton>
          </div>

          <!-- 기사 하단 섹션: 좋아요, 원본 링크 및 좋아요 버튼 -->
          <div class="article__content__footer">
            <!-- 좋아요 수, 원본 링크 아이콘 그룹 -->
            <div class="article__content__emoji">
              <!-- 좋아요 상태 및 개수 표시 -->
              <span class="emoji-btn">
                <span v-if="liked" class="heart-icon filled-heart">❤️</span>
                <span v-else class="heart-icon empty-heart">🤍</span>
                {{ likeCount }}
              </span>
              
              <!-- 원본 기사 링크 -->
              <a :href="news.url">📄</a>
            </div>
            
            <!-- 좋아요 토글 버튼 -->
            <button class="emoji-btn" @click="toggleLike" :disabled="!authStore.isAuthenticated">
              <span v-if="!authStore.isAuthenticated">로그인 필요</span>
              <span v-else>
                <span v-if="liked" class="heart-icon filled-heart">❤️</span>
                <span v-else class="heart-icon empty-heart">🤍</span>
                좋아요
              </span>
            </button>
            
            <!-- 좋아요 버튼 클릭시 애니메이션 효과 (하트 띄우기) -->
            <transition name="heart-float">
              <span v-if="isAnimating" class="floating-heart">
                <span v-if="liked" class="filled-heart">❤️</span>
                <span v-else class="empty-heart">🤍</span>
              </span>
            </transition>
          </div>
        </div>
      </ContentBox>
      
      <!-- 뉴스 챗봇 컴포넌트 추가 (ContentBox 밖으로 이동) -->
      <NewsChatbot :news="news" />
    </div>

    <!-- 사이드바: 관련 기사 목록 -->
    <ContentBox class="sidebar">
      <h1 class="sidebar__title">📰 관련 기사</h1>
      <!-- 관련 기사가 있을 경우에만 표시 -->
      <div v-if="relatedNews.length">
        <div v-for="(item, index) in relatedNews" :key="index">
          <!-- 각 관련 기사 표시 -->
          <div class="related-article">
            <RouterLink :to="`/news/${item.id}`" class="related-link">
              <h3>{{ item.title }}</h3>
              <div class="related-meta">
                <span>{{ item.category }}</span>
                <span> 🕒 {{ formatDate(item.write_date) }}</span>
              </div>
            </RouterLink>
          </div>
        </div>
      </div>
      <div v-else class="no-related">
        관련 기사가 없습니다.
      </div>
    </ContentBox>
  </div>
</template>

<script setup>
// Vue Composition API의 반응형 상태 관리를 위한 ref 임포트
import { ref, computed } from "vue";
// 공통 UI 컴포넌트 임포트
import ContentBox from "@/common/ContentBox.vue";
// 상태 표시 버튼 컴포넌트 임포트 (카테고리, 태그 등 표시용)
import StateButton from "@/common/StateButton.vue";
// 날짜 포맷팅을 위한 커스텀 컴포저블 훅 임포트
import { useDate } from "@/composables/useDate";
// 라우터 인스턴스 임포트 (페이지 이동 처리용)
import router from "@/router";
// 뒤로가기 아이콘 SVG 컴포넌트 임포트
import LeftArrow from "@/components/icons/LeftArrow.svg";
// Vue Router의 훅 임포트
import { useRoute, onBeforeRouteUpdate } from 'vue-router';
// 라이프사이클 훅 임포트
import { onMounted } from 'vue';
// axios 임포트
import axios from 'axios';
import { RouterLink } from 'vue-router';
// 인증 스토어 임포트
import { useAuthStore } from '@/stores/auth';
// 뉴스 챗봇 컴포넌트 임포트
import NewsChatbot from "@/components/NewsChatbot.vue";

// API 기본 URL 설정 (나중에 환경 변수로 분리 가능)
const API_BASE_URL = 'http://127.0.0.1:8000';

// 현재 표시 중인 뉴스 데이터를 저장하는 반응형 변수
const news = ref(null);
// 관련 뉴스 목록을 저장하는 반응형 변수
const relatedNews = ref([]);
// 로딩 상태를 저장하는 반응형 변수
const loading = ref(true);
// 오류 메시지를 저장하는 반응형 변수
const error = ref(null);

// 날짜 포맷팅 함수 추출
const { formatDate } = useDate();

// 좋아요 상태를 저장하는 반응형 변수 (true: 좋아요 누름, false: 좋아요 안 누름)
const liked = ref(false);
// 좋아요 개수를 저장하는 반응형 변수
const likeCount = ref(0);
// 좋아요 애니메이션 상태를 제어하는 반응형 변수
const isAnimating = ref(false);

// 현재 라우트 정보 가져오기
const route = useRoute();
// 인증 스토어 가져오기
const authStore = useAuthStore();

// 파싱된 키워드 배열을 computed 속성으로 정의
const parsedKeywords = computed(() => {
  if (!news.value || !news.value.keywords) return [];
  return parseKeywords(news.value.keywords);
});

// 키워드 문자열을 배열로 변환하는 함수
const parseKeywords = (keywords) => {
  if (!keywords) return [];
  
  // 이미 배열인 경우 그대로 반환
  if (Array.isArray(keywords)) return keywords;
  
  // 문자열인 경우 처리
  if (typeof keywords === 'string') {
    // 문자열이 '[', ']'로 둘러싸인 경우 제거
    let processedKeywords = keywords.trim();
    if (processedKeywords.startsWith('[') && processedKeywords.endsWith(']')) {
      processedKeywords = processedKeywords.substring(1, processedKeywords.length - 1);
    }
    
    try {
      // JSON 형식의 문자열인지 먼저 시도
      return JSON.parse(`[${processedKeywords}]`);
    } catch (e) {
      // JSON 파싱에 실패하면 일반 쉼표로 구분된 문자열로 처리
      return processedKeywords.split(',').map(k => k.trim());
    }
  }
  
  // 다른 형식의 경우 빈 배열 반환
  return [];
};

// 관련 뉴스 데이터를 가져오는 함수 (벡터 유사도 기반)
const fetchRelatedNews = async (newsId) => {
  try {
    // 새로운 관련 기사 API 사용
    const response = await axios.get(`${API_BASE_URL}/api/news/${newsId}/related/`);
    relatedNews.value = response.data;
  } catch (err) {
    console.error('관련 뉴스를 가져오는 중 오류 발생:', err);
    // 관련 뉴스 가져오기에 실패해도 기본 뉴스 표시에는 영향 없도록 처리
    relatedNews.value = [];
  }
};

// ID로 뉴스 데이터를 가져오는 함수 (API 호출)
const fetchNewsById = async (id) => {
  loading.value = true;
  error.value = null;
  
  try {
    // API 호출로 뉴스 데이터 가져오기
    const response = await axios.get(`${API_BASE_URL}/api/news/${id}/`);
    
    // 응답 데이터 저장
    news.value = response.data;
    
    // 좋아요 수 설정 (API 응답 구조에 따라 조정 필요)
    likeCount.value = response.data.like_count || 0;
    
    // 관련 기사 가져오기 (수정된 함수 호출)
    fetchRelatedNews(id);
    
    // 로그인한 경우 조회 기록 추가 및 좋아요 상태 확인
    if (authStore.isAuthenticated) {
      recordArticleView(id);
      checkLikeStatus(id);
    }
  } catch (err) {
    console.error('뉴스 데이터를 가져오는 중 오류 발생:', err);
    error.value = '뉴스 데이터를 가져오는 중 오류가 발생했습니다.';
  } finally {
    loading.value = false;
  }
};

// 좋아요 상태 확인
const checkLikeStatus = async (id) => {
  if (!authStore.isAuthenticated) return;
  
  try {
    const response = await axios.get(`${API_BASE_URL}/api/news/${id}/check-like/`, {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`
      }
    });
    liked.value = response.data.liked;
  } catch (err) {
    console.error('좋아요 상태 확인 중 오류 발생:', err);
  }
};

// 조회 기록 추가
const recordArticleView = async (id) => {
  if (!authStore.isAuthenticated) return;
  
  try {
    await axios.post(`${API_BASE_URL}/api/news/${id}/view/`, {}, {
      headers: {
        Authorization: `Bearer ${authStore.accessToken}`
      }
    });
    console.log('조회 기록이 저장되었습니다.');
  } catch (err) {
    console.error('조회 기록 저장 중 오류 발생:', err);
    // 조회 기록 저장 실패는 사용자 경험에 영향을 주지 않도록 조용히 처리
  }
};

// 좋아요 기능 처리
const toggleLike = async () => {
  if (!authStore.isAuthenticated) {
    alert('좋아요를 하려면 로그인이 필요합니다.');
    return;
  }
  
  try {
    let response;
    if (!liked.value) {
      // 좋아요 추가
      response = await axios.post(
        `${API_BASE_URL}/api/news/${news.value.id}/like/`,
        {},
        { headers: { Authorization: `Bearer ${authStore.accessToken}` } }
      );
      liked.value = true;
      likeCount.value += 1;
    } else {
      // 좋아요 취소 (백엔드에 unlike 엔드포인트 추가 필요)
      response = await axios.post(
        `${API_BASE_URL}/api/news/${news.value.id}/unlike/`,
        {},
        { headers: { Authorization: `Bearer ${authStore.accessToken}` } }
      );
      liked.value = false;
      likeCount.value -= 1;
    }
    
    // 애니메이션 효과
    isAnimating.value = true;
    setTimeout(() => {
      isAnimating.value = false;
    }, 600);
    
    console.log(response.data.message);
  } catch (err) {
    console.error('좋아요 처리 중 오류 발생:', err);
    if (err.response && err.response.status === 400) {
      alert(err.response.data.message);
    }
  }
};

onMounted(() => {
  // 라우트 파라미터에서 ID 가져오기
  const newsId = route.params.id;
  
  if (newsId) {
    fetchNewsById(newsId);
  } else {
    console.error('뉴스 ID가 없습니다.');
    error.value = '유효하지 않은 뉴스 ID입니다.';
    loading.value = false;
  }
});

// 같은 컴포넌트 내에서 라우트가 변경될 때 호출되는 함수
// 관련 기사 클릭 시 같은 NewsDetailView 컴포넌트 내에서 다른 ID로 이동할 때 필요
onBeforeRouteUpdate((to, from) => {
  // 뉴스 ID가 변경된 경우에만 데이터 다시 불러오기
  if (to.params.id !== from.params.id) {
    fetchNewsById(to.params.id);
  }
});
</script>

<style scoped lang="scss">
.back-btn {
  margin-bottom: 10px;
}

.loading, .error {
  text-align: center;
  margin: 50px 0;
  
  .dark-mode & {
    color: var(--c-text);
  }
}

.news-detail {
  display: flex;
  gap: 20px;

  @media (max-width: 800px) {
    flex-direction: column;
  }

  .article__container {
    flex: 2;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .sidebar {
    flex: 1;
    &__title {
      font-weight: 700;
      font-size: 18px;
      margin-bottom: 20px;
      
      .dark-mode & {
        color: var(--c-text);
      }
    }
  }

  .article {
    font-size: 1rem;
    padding: 20px;
    &__header {
      color: #888;
      font-size: 0.9rem;
      margin-bottom: 10px;
      
      .dark-mode & {
        color: var(--c-gray-500);
      }
      
      &-title {
        margin: 12px 0;
        font-size: 1.6rem;
        font-weight: bold;
        color: #1c1c1e;
        
        .dark-mode & {
          color: var(--c-text);
        }
      }
      &-writer {
        display: flex;
        gap: 10px;
      }
    }

    &__content {
      margin: 16px 0;
      line-height: 1.6;
      
      .dark-mode & {
        color: var(--c-text);
      }

      &__footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 30px;
      }

      &__emoji {
        color: #888;
        font-size: 16px;
        display: flex;
        gap: 30px;
        align-items: center;
        
        .dark-mode & {
          color: var(--c-gray-500);
        }
        
        &-eye {
          font-size: 17px;
        }
      }
    }

    &__tags {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 15px;
    }
  }

  .emoji-btn {
    display: flex;
    align-items: center;
    font-size: 15px;
    color: #888;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
  }
  
  .heart-icon {
    display: inline-block;
    margin-right: 4px;
  }
  
  .filled-heart {
    color: #e74c3c !important;
    text-shadow: 0 0 0 #e74c3c;
  }
  
  .empty-heart {
    color: #888 !important;
    text-shadow: 0 0 0 #888;
    
    .dark-mode & {
      color: #aaa !important;
      text-shadow: 0 0 0 #aaa;
    }
  }

  .floating-heart {
    position: absolute;
    font-size: 24px;
    animation: heartFloat 0.6s ease-out forwards;
    
    .filled-heart {
      color: #e74c3c !important;
    }
  }

  @keyframes heartFloat {
    0% {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    50% {
      opacity: 0.8;
      transform: translateY(-20px) scale(1.2);
    }
    100% {
      opacity: 0;
      transform: translateY(-40px) scale(0.8);
    }
  }
  
  .related-article {
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
    
    .dark-mode & {
      border-bottom-color: var(--c-border);
    }
    
    &:last-child {
      border-bottom: none;
    }
    
    .related-link {
      text-decoration: none;
      color: inherit;
      display: block;
      
      &:hover {
        h3 {
          color: #4a7bae;
          
          .dark-mode & {
            color: var(--c-main);
          }
        }
      }
      
      h3 {
        font-size: 16px;
        margin: 0 0 8px 0;
        transition: color 0.2s;
        
        .dark-mode & {
          color: var(--c-text);
        }
      }
      
      .related-meta {
        font-size: 12px;
        color: #888;
        display: flex;
        gap: 10px;
        
        .dark-mode & {
          color: var(--c-gray-500);
        }
      }
    }
  }
  
  .no-related {
    color: #888;
    text-align: center;
    padding: 20px 0;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
  }
}
</style>