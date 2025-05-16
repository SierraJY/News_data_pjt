<template>
  <div class="news">
    <div>
      <h1 class="news__title">🤖 AI 맞춤 추천 뉴스</h1>
      <p class="news__description">
        당신이 원하는 뉴스, 이제 AI가 직접 추천해드립니다!<br />
        나만의 취향을 기반으로, 맞춤형 뉴스만 쏙쏙 골라주는 뉴스 큐레이팅 서비스<br />
        AI 챗봇과 기사에 대해 대화하며 궁금한 점을 물어보고, <br />
        한눈에 보기 쉬운 대시보드를 통해 나의 뉴스 소비 패턴도 확인할 수 있습니다.
      </p>
      <ContentBox class="news__tabs">
        <StateButton
          v-for="tab in tabs"
          :key="tab.id"
          type="state"
          :is-active="activeTab === tab.value"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
        </StateButton>
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

        <div class="filters__container">
          <select class="filters" v-model="sortBy" @change="handleSortChange">
            <option value="latest">최신순</option>
            <option value="recommend">추천순</option>
          </select>
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
  gap: 20px;
  margin-top: 30px;

  &__title {
    font-size: 20px;
    font-weight: 700;
    border-bottom: 1px solid #e2e2e2;
    padding-bottom: 10px;
  }

  &__description {
    font-size: 16px;
    font-weight: 400;
    color: #575757;
    line-height: normal;
    margin: 15px 0 25px;
  }

  &__tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 12px 30px !important;
  }

  .loading, .error {
    text-align: center;
    margin: 50px 0;
  }
  
  .no-results {
    text-align: center;
    margin: 30px 0;
    font-size: 16px;
    color: #666;
  }

  &__box {
    padding: 30px !important;

    &__title-container {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: space-between;

      .recommend-text, .search-result-text {
        font-size: 18px;
        font-weight: 600;
        margin-left: 5px;
      }
      
      .search-highlight {
        color: #0c3057;
        font-weight: bold;
      }

      .username-highlight {
        text-decoration: underline red;
        text-underline-offset: 3px;
        font-weight: bold;
        margin-right: 4px;
      }
    }

    .filters__container {
      position: absolute;
      right: 0;
    }

    &__cards {
      margin-top: 30px;
      margin-left: 30px;
    }
  }
}
</style>
