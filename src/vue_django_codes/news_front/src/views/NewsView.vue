<!-- 
  뉴스 목록 페이지를 위한 컴포넌트
  AI 추천 뉴스를 보여주고 필터링과 정렬 기능을 제공
-->
<template>
  <div class="news">
    <div>
      <!-- 페이지 제목 -->
      <h1 class="news__title">🤖 AI 맞춤 추천 뉴스</h1>
      
      <!-- 서비스 설명 문구 -->
      <p class="news__description">
        당신이 원하는 뉴스, 이제 AI가 직접 추천해드립니다!<br />
        나만의 취향을 기반으로, 맞춤형 뉴스만 쏙쏙 골라주는 뉴스 큐레이팅 서비스<br />
        AI 챗봇과 기사에 대해 대화하며 궁금한 점을 물어보고, <br />
        한눈에 보기 쉬운 대시보드를 통해 나의 뉴스 소비 패턴도 확인할 수 있습니다.
      </p>

      <!-- 카테고리 탭 버튼 그룹 -->
      <ContentBox class="news__tabs">
        <!-- 각 탭 버튼을 반복하여 생성 -->
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
    
    <!-- 로딩 상태 표시 -->
    <div v-if="loading" class="loading">
      데이터를 불러오는 중입니다...
    </div>
    
    <!-- 오류 상태 표시 -->
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <!-- 뉴스 목록 컨테이너 -->
    <ContentBox v-else class="news__box">
      <div class="news__box__title-container">
        <!-- 정렬 옵션 선택 드롭다운 -->
        <div class="filters__container">
          <select class="filters" v-model="sortBy" @change="handleSortChange">
            <option value="latest">최신순</option>
            <option value="recommend">추천순</option>
          </select>
        </div>
      </div>

      <!-- 뉴스 카드 목록 -->
      <div class="news__box__cards">
        <NewsCard 
          v-for="news in newsList" 
          :key="news.id" 
          :news="news"
        />
      </div>

      <!-- 페이지네이션 컴포넌트 -->
      <PaginationButton v-model="currentPage" :totalPages="totalPages" />
    </ContentBox>
  </div>
</template>

<script setup>
// Vue Composition API 기능 임포트
import { ref, computed, watch, onMounted } from "vue";
// 컴포넌트 임포트
import ContentBox from "@/common/ContentBox.vue";
import NewsCard from "@/components/NewsCard.vue";
import PaginationButton from "@/common/PaginationButton.vue";
import StateButton from "@/common/StateButton.vue";
// 데이터 임포트
import { tabs } from "@/assets/data/tabs";
// axios 임포트
import axios from 'axios';
// 인증 스토어 임포트
import { useAuthStore } from '@/stores/auth';

// API 기본 URL 설정
const API_BASE_URL = 'http://127.0.0.1:8000';

// 인증 스토어 불러오기
const authStore = useAuthStore();

// 페이지당 표시할 뉴스 개수
const itemsPerPage = 10;

// 뉴스 목록 원본 데이터
const originalNewsList = ref([]);
// 로딩 상태 변수
const loading = ref(true);
// 오류 메시지 변수
const error = ref(null);

// 뉴스 데이터 가져오기 함수
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

// 코사인 유사도 기반 추천 뉴스 가져오기 함수
const fetchRecommendedNews = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // 인증 스토어에서 토큰 가져오기
    if (!authStore.isAuthenticated) {
      error.value = '로그인이 필요한 서비스입니다.';
      originalNewsList.value = [];
      loading.value = false;
      return;
    }
    
    console.log('인증 토큰:', authStore.accessToken); // 토큰 확인
    
    // 인증 헤더 설정 (스토어의 setAuthHeader 메서드가 이미 호출됨)
    const response = await axios.get(`${API_BASE_URL}/api/news/recommend/`);
    originalNewsList.value = response.data;
  } catch (err) {
    console.error('추천 뉴스 데이터를 가져오는 중 오류 발생:', err);
    console.error('오류 응답:', err.response); // 전체 응답 로깅
    console.error('오류 상태:', err.response?.status);
    console.error('오류 데이터:', err.response?.data);
    
    // 서버에서 반환한 오류 메시지가 있으면 그대로 표시
    if (err.response && err.response.data && err.response.data.error) {
      error.value = err.response.data.error;
    } else if (err.response && err.response.status === 401) {
      error.value = '로그인이 필요한 서비스입니다.';
      // 토큰이 만료되었을 수 있으므로 로그아웃 처리
      authStore.logout();
    } else if (err.response && err.response.status === 400) {
      error.value = '추천을 위한 좋아요 데이터가 부족합니다. 먼저 몇 개의 기사에 좋아요를 눌러주세요.';
    } else {
      error.value = '추천 뉴스 데이터를 가져오는 중 오류가 발생했습니다: ' + (err.message || '알 수 없는 오류');
    }
    
    // 오류 발생 시 일반 뉴스 목록을 가져오지 않고 오류 메시지만 표시
    originalNewsList.value = [];
  } finally {
    loading.value = false;
  }
};

// 정렬 방식 변경 처리 함수
const handleSortChange = async () => {
  if (sortBy.value === 'recommend') {
    // 추천순 선택 시 코사인 유사도 기반 추천 API 호출
    await fetchRecommendedNews();
  } else {
    // 최신순 선택 시 일반 뉴스 목록 API 호출
    await fetchNews();
  }
};

// 컴포넌트 마운트 시 데이터 가져오기
onMounted(() => {
  fetchNews();
});

// 필터링된 뉴스 목록 - 카테고리와 정렬 기준에 따라 필터링
const filteredNewsList = computed(() => {
  if (!originalNewsList.value.length) return [];
  
  let filteredNews = [...originalNewsList.value];
  
  // 카테고리 필터링 - 'all'이 아닌 경우에만 필터링 적용
  if (activeTab.value !== 'all') {
    filteredNews = filteredNews.filter(news => news.category === activeTab.value);
  }
  
  // 최신순 정렬일 경우에만 여기서 정렬 (추천순은 API에서 정렬된 결과를 사용)
  if (sortBy.value === 'latest') {
    filteredNews.sort((a, b) => {
      // 최신순 정렬 - 날짜 기준
      return new Date(b.write_date) - new Date(a.write_date);
    });
  }
  
  return filteredNews;
});

// 현재 페이지에 표시할 뉴스 목록 (페이지네이션 적용)
const newsList = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  return filteredNewsList.value.slice(startIndex, endIndex);
});

// 총 페이지 수 계산
const totalPages = computed(() => {
  return Math.ceil(filteredNewsList.value.length / itemsPerPage);
});

// 상태 변수 초기화
const sortBy = ref("latest");      // 정렬 기준 (기본값: 최신순)
const activeTab = ref('all');      // 선택된 카테고리 탭 (기본값: 전체)
const currentPage = ref(1);        // 현재 페이지 (기본값: 1페이지)

// 정렬 방식이 변경될 때마다 현재 페이지를 1페이지로 리셋
watch(sortBy, () => {
  currentPage.value = 1;
});

// 탭이 변경될 때마다 현재 페이지를 1페이지로 리셋
watch(activeTab, () => {
  currentPage.value = 1;
});

// 현재 페이지가 총 페이지 수를 초과하지 않도록 감시
// (필터링 등으로 페이지 수가 줄어든 경우를 처리)
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

  &__box {
    padding: 30px !important;

    &__title-container {
      position: relative;
      display: flex;
      align-items: center;
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