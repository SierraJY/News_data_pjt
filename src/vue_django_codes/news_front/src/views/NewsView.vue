<template>
  <div class="news">
    <div>
      <div class="how_to_use">
        <div class="sort-buttons">
          <button 
            class="sort-btn" 
            :class="{ active: sortBy === 'latest' }" 
            @click="sortBy = 'latest'; handleSortChange()"
          >
            <span class="icon">🕒</span> 최신순으로 보기
          </button>
          <button 
            class="sort-btn" 
            :class="{ active: sortBy === 'recommend' }" 
            @click="sortBy = 'recommend'; handleSortChange()"
          >
            <span class="icon">✨</span> 맞춤 추천 보기
          </button>
        </div>
      </div>
      <ContentBox class="news__tabs">
        <div class="tabs-wrapper">
          <button class="scroll-btn scroll-left" @click="scrollTabs('left')">
            &lt;
          </button>
          <div class="tab-container" ref="tabContainerRef">
            <div 
              v-for="tab in tabs" 
              :key="tab.id" 
              class="tab-item"
              :class="{ 'active': activeTab === tab.value }"
              @click="activeTab = tab.value"
            >
              {{ tab.label }}
              <div class="tab-indicator" v-if="activeTab === tab.value"></div>
            </div>
          </div>
          <button class="scroll-btn scroll-right" @click="scrollTabs('right')">
            &gt;
          </button>
          <div class="scroll-hint right"></div>
        </div>
      </ContentBox>
    </div>

    <div v-if="loading" class="loading">
      데이터를 불러오는 중입니다...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <ContentBox v-else class="news__box">
      <div class="news__box__title-container">
        <!-- 검색 결과 표시 -->
        <div v-if="searchQuery" class="search-result-text">
          <span class="search-highlight">"{{ searchQuery }}"</span>에 대한 검색 결과 ({{ originalNewsList.length }}건)
        </div>
        
        <!-- 추천순 문구 -->
        <div v-else-if="sortBy === 'recommend' && authStore.user?.username" class="recommend-text">
          <span class="username-highlight">{{ authStore.user.username }}</span>님에게 추천하는 뉴스 목록이에요
        </div>
      </div>

      <div class="news__box__cards">
        <NewsCard 
          v-for="news in newsList" 
          :key="news.id" 
          :news="news"
        />
      </div>
      
      <div v-if="newsList.length === 0 && !loading" class="no-results">
        검색 결과가 없습니다.
      </div>

      <PaginationButton v-model="currentPage" :totalPages="totalPages" />
    </ContentBox>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import ContentBox from "@/common/ContentBox.vue";
import NewsCard from "@/components/NewsCard.vue";
import PaginationButton from "@/common/PaginationButton.vue";
import StateButton from "@/common/StateButton.vue";
import { tabs } from "@/assets/data/tabs";
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { useRoute, useRouter } from 'vue-router';

const API_BASE_URL = 'http://127.0.0.1:8000';
const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const itemsPerPage = 10;

const originalNewsList = ref([]);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');

// URL에서 검색어 가져오기
onMounted(() => {
  if (route.query.search) {
    searchQuery.value = route.query.search;
    fetchSearchResults(searchQuery.value);
  } else {
    fetchNews();
  }
});

// URL 쿼리 파라미터 변경 감지
watch(() => route.query.search, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery;
    fetchSearchResults(searchQuery.value);
  } else {
    searchQuery.value = '';
    fetchNews();
  }
});

const fetchNews = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await axios.get(`${API_BASE_URL}/api/news/`);
    originalNewsList.value = response.data;
  } catch (err) {
    console.error('뉴스 데이터를 가져오는 중 오류 발생:', err);
    error.value = '뉴스 데이터를 가져오는 중 오류가 발생했습니다.';
  } finally {
    loading.value = false;
  }
};

const fetchSearchResults = async (query) => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await axios.get(`${API_BASE_URL}/api/news/search/`, {
      params: { query }
    });
    originalNewsList.value = response.data.results || [];
  } catch (err) {
    console.error('검색 중 오류 발생:', err);
    error.value = '검색 중 오류가 발생했습니다: ' + (err.response?.data?.error || err.message);
    originalNewsList.value = [];
  } finally {
    loading.value = false;
  }
};

const fetchRecommendedNews = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    if (!authStore.isAuthenticated) {
      error.value = '로그인이 필요한 서비스입니다.';
      originalNewsList.value = [];
      loading.value = false;
      return;
    }

    const response = await axios.get(`${API_BASE_URL}/api/news/recommend/`);
    originalNewsList.value = response.data;
  } catch (err) {
    console.error('추천 뉴스 데이터를 가져오는 중 오류 발생:', err);
    if (err.response && err.response.data?.error) {
      error.value = err.response.data.error;
    } else if (err.response?.status === 401) {
      error.value = '로그인이 필요한 서비스입니다.';
      authStore.logout();
    } else if (err.response?.status === 400) {
      error.value = '추천을 위한 좋아요 데이터가 부족합니다. 먼저 몇 개의 기사에 좋아요를 눌러주세요.';
    } else {
      error.value = '추천 뉴스 데이터를 가져오는 중 오류가 발생했습니다: ' + (err.message || '알 수 없는 오류');
    }

    originalNewsList.value = [];
  } finally {
    loading.value = false;
  }
};

const handleSortChange = async () => {
  if (searchQuery.value) {
    // 검색 중에는 정렬 변경 시 검색 쿼리 제거
    searchQuery.value = '';
    router.replace({ query: {} });
  }
  
  if (sortBy.value === 'recommend') {
    await fetchRecommendedNews();
  } else {
    await fetchNews();
  }
};

const filteredNewsList = computed(() => {
  if (!originalNewsList.value.length) return [];
  let filteredNews = [...originalNewsList.value];
  if (activeTab.value !== 'all') {
    filteredNews = filteredNews.filter(news => news.category === activeTab.value);
  }
  if (sortBy.value === 'latest' && !searchQuery.value) {
    filteredNews.sort((a, b) => new Date(b.write_date) - new Date(a.write_date));
  }
  return filteredNews;
});

const newsList = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  return filteredNewsList.value.slice(startIndex, startIndex + itemsPerPage);
});

const totalPages = computed(() => {
  return Math.ceil(filteredNewsList.value.length / itemsPerPage);
});

const sortBy = ref("latest");
const activeTab = ref('all');
const currentPage = ref(1);

// 탭 스크롤을 위한 참조
const tabContainerRef = ref(null);

// 탭 스크롤 함수
const scrollTabs = (direction) => {
  if (!tabContainerRef.value) return;
  
  const container = tabContainerRef.value;
  const scrollAmount = 200; // 스크롤할 픽셀 양
  
  if (direction === 'left') {
    container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  } else {
    container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  }
};

watch(sortBy, () => {
  currentPage.value = 1;
});
watch(activeTab, () => {
  currentPage.value = 1;
});
watch(totalPages, (newValue) => {
  if (currentPage.value > newValue && newValue > 0) {
    currentPage.value = newValue;
  }
});
</script>

<style scoped lang="scss">
.news {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 10px;

  &__title {
    font-size: 20px;
    font-weight: 700;
    border-bottom: 1px solid #e2e2e2;
    padding-bottom: 10px;
    
    .dark-mode & {
      border-bottom-color: var(--c-border);
      color: var(--c-text);
    }
  }

  &__description {
    font-size: 16px;
    font-weight: 400;
    color: #575757;
    line-height: normal;
    margin: 15px 0 25px;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
  }

  &__tabs {
    padding: 0 !important;
    overflow: hidden;
    position: relative;
    
    .tabs-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }
    
    .tab-container {
      display: flex;
      overflow-x: auto;
      scrollbar-width: none; /* Firefox */
      -ms-overflow-style: none; /* IE and Edge */
      scroll-behavior: smooth;
      padding: 0 10px;
      flex: 1;
      
      &::-webkit-scrollbar {
        display: none; /* Chrome, Safari, Opera */
      }
    }
    
    .tab-item {
      padding: 15px 20px;
      font-size: 14px;
      font-weight: 500;
      color: #666;
      cursor: pointer;
      position: relative;
      white-space: nowrap;
      transition: color 0.3s;
      
      .dark-mode & {
        color: var(--c-gray-500);
      }
      
      &:hover {
        color: #0c3057;
        
        .dark-mode & {
          color: var(--c-main);
        }
      }
      
      &.active {
        color: #0c3057;
        font-weight: 600;
        
        .dark-mode & {
          color: var(--c-main);
        }
      }
      
      .tab-indicator {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background-color: #0c3057;
        animation: slideIn 0.3s ease-in-out;
        
        .dark-mode & {
          background-color: var(--c-main);
        }
      }
    }
    
    .scroll-btn {
      width: 30px;
      height: 30px;
      background-color: #fff;
      border: 1px solid #ddd;
      border-radius: 50%;
      cursor: pointer;
      z-index: 2;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      color: #0c3057;
      transition: all 0.2s;
      
      .dark-mode & {
        background-color: var(--c-card-bg);
        border-color: var(--c-border);
        color: var(--c-main);
      }
      
      &:hover {
        background-color: #f0f4f9;
        border-color: #0c3057;
        
        .dark-mode & {
          background-color: var(--c-hover-bg);
          border-color: var(--c-main);
        }
      }
      
      &.scroll-left {
        margin-left: 5px;
      }
      
      &.scroll-right {
        margin-right: 5px;
      }
    }
    
    .scroll-hint {
      position: absolute;
      top: 0;
      bottom: 0;
      width: 20px;
      pointer-events: none;
      
      &.right {
        right: 0;
        background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.9) 70%);
        
        .dark-mode & {
          background: linear-gradient(to right, transparent, rgba(34, 39, 41, 0.9) 70%);
        }
      }
    }
    
    @keyframes slideIn {
      from {
        transform: translateX(-100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  }

  .loading, .error {
    text-align: center;
    margin: 50px 0;
    
    .dark-mode & {
      color: var(--c-text);
    }
  }
  
  .no-results {
    text-align: center;
    margin: 30px 0;
    font-size: 16px;
    color: #666;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
  }

  .how_to_use {
    background-color: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    margin-bottom: 5px;
    display: flex;
    justify-content: center;
    
    .dark-mode & {
      background-color: var(--c-card-bg);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
  }

  .sort-buttons {
    display: flex;
    gap: 15px;
    justify-content: center;
    
    .sort-btn {
      padding: 12px 20px;
      border-radius: 8px;
      border: 1px solid #ddd;
      background-color: white;
      font-size: 15px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
      
      .dark-mode & {
        background-color: var(--c-card-bg);
        border-color: var(--c-border);
        color: var(--c-text);
      }
      
      &:hover {
        border-color: #0c3057;
        background-color: #f5f7fa;
        transform: translateY(-2px);
        box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
        
        .dark-mode & {
          border-color: var(--c-main);
          background-color: var(--c-hover-bg);
        }
      }
      
      &.active {
        background-color: #0c3057;
        color: white;
        border-color: #0c3057;
        
        .dark-mode & {
          background-color: var(--c-main);
          border-color: var(--c-main);
        }
      }
      
      .icon {
        margin-right: 8px;
        font-size: 16px;
      }
    }
  }

  &__box {
    padding: 25px !important;
    border-radius: 14px;

    &__title-container {
      position: relative;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      margin-bottom: 20px;

      .recommend-text, .search-result-text {
        font-size: 18px;
        font-weight: 600;
        margin-left: 0;
        margin-bottom: 5px;
        color: #333;
        
        .dark-mode & {
          color: var(--c-text);
        }
      }
      
      .search-highlight {
        color: #0c3057;
        font-weight: bold;
        
        .dark-mode & {
          color: var(--c-main);
        }
      }

      .username-highlight {
        text-decoration: underline #e74c3c;
        text-underline-offset: 3px;
        font-weight: bold;
        margin-right: 4px;
        color: #0c3057;
        
        .dark-mode & {
          color: var(--c-main);
          text-decoration: underline #e55039;
        }
      }
    }

    &__cards {
      margin-top: 20px;
      display: flex;
      flex-direction: column;
      width: 92%;
      max-width: 850px;
      margin-left: auto;
      margin-right: auto;
      gap: 15px;
    }
  }
}
</style>
