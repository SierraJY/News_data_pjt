<!-- 
  대시보드 페이지 컴포넌트
  사용자의 뉴스 소비 패턴과 선호도를 시각화하여 보여주는 페이지
-->
<template>
  <div class="dashboard">
    <!-- 페이지 제목 -->
    <h1 class="title">DASHBOARD</h1>
    
    <!-- 페이지 설명 -->
    <p class="subtitle">
      <br />방문 기록 및 좋아요 데이터를 기반으로 나의 관심 분야를 확인하고,
      <br />관심 분야에 맞는 기사를 추천 받아보세요. <br />
    </p>
    
    <!-- 로딩 상태 표시 -->
    <div v-if="loading" class="loading-container">
      <p>데이터를 불러오는 중입니다...</p>
    </div>
    
    <!-- 오류 상태 표시 -->
    <div v-else-if="error" class="error-container">
      <p>{{ error }}</p>
    </div>
    
    <!-- 대시보드 콘텐츠 - 데이터가 있을 때만 표시 -->
    <template v-else>
      <!-- 첫 번째 차트 레이아웃 행 -->
      <div class="layout">
        <!-- 관심 카테고리 차트 컨테이너 -->
        <ContentBox class="category">
          <h1>🐤 나의 관심 카테고리</h1>
          <p class="card_description">
            내가 주로 읽은 기사들을 분석하여 정치, 경제, 문화 등 가장 관심 있는
            뉴스 카테고리를 한눈에 보여드립니다.
          </p>
          
          <div v-if="!hasCategoryData" class="no-data-message">
            아직 읽은 기사가 없습니다. 뉴스를 읽고 돌아오세요!
          </div>
          
          <!-- 도넛 차트와 카테고리 레이블 -->
          <div v-else class="category__chart">
            <!-- Chart.js의 Doughnut 컴포넌트를 활용한 도넛 차트 -->
            <Doughnut :data="categoryData" :options="options" />
            
            <!-- 카테고리 순위 레이블 목록 -->
            <div class="category__labels">
              <span
                v-for="(category, index) in categories"
                :key="index"
                :style="{
                  borderColor: categoryColors[index % categoryColors.length],
                  color: categoryColors[index % categoryColors.length],
                }"
                class="category__label"
              >
                <!-- 카테고리 이름과 기사 수를 표시 -->
                {{ index + 1 }}순위: {{ category.name }} ({{ category.count }}개)
              </span>
            </div>
          </div>
        </ContentBox>

        <!-- 주요 키워드 차트 컨테이너 -->
        <ContentBox class="keyword">
          <h1>⭐️ 주요 키워드</h1>
          <p class="card_description">
            내가 관심있게 본 뉴스 기사들에서 가장 많이 등장한 핵심 키워드를
            추출하여 현재 나의 주요 관심사를 보여드립니다.
          </p>
          
          <div v-if="!hasKeywordData" class="no-data-message">
            아직 데이터가 충분하지 않습니다. 더 많은 뉴스를 읽어보세요!
          </div>
          
          <!-- Chart.js의 Bar 컴포넌트를 활용한 가로 막대 차트 -->
          <Bar v-else :data="keywordData" :options="barOptions" class="keyword-chart" />
        </ContentBox>
      </div>
      
      <!-- 두 번째 차트 레이아웃 행 -->
      <div class="layout">
        <!-- 주간 읽은 기사 차트 컨테이너 -->
        <ContentBox>
          <h1>📰 주간 읽은 기사</h1>
          <p class="card_description">
            최근 일주일 동안 하루에 몇 개의 기사를 읽었는지 그래프로 확인하며 나의
            뉴스 소비 패턴을 분석합니다.
          </p>
          
          <div v-if="!hasWeeklyData" class="no-data-message">
            최근 7일간 읽은 기사가 없습니다. 뉴스를 읽고 통계를 확인해보세요!
          </div>
          
          <!-- Chart.js의 Bar 컴포넌트를 활용한 세로 막대 차트 -->
          <Bar v-else :data="readData" :options="readBarOptions" class="weekly-chart" />
        </ContentBox>

        <!-- 좋아요 누른 기사 목록 컨테이너 -->
        <ContentBox class="like-news">
          <h1>❤️ 좋아요 누른 기사</h1>
          <p class="card_description">
            내가 좋아요를 누른 기사들의 목록을 한곳에서 모아보고 다시 찾아볼 수
            있습니다.
          </p>
          
          <div v-if="!favoriteArticles.length" class="no-data-message">
            아직 좋아요한 기사가 없습니다. 마음에 드는 기사에 좋아요를 눌러보세요!
          </div>
          
          <!-- 좋아요 누른 기사 목록을 반복하여 표시 -->
          <div v-else class="favorite-articles">
            <div v-for="(article, index) in favoriteArticles" :key="index" class="favorite-article">
              <RouterLink :to="`/news/${article.id}`" class="article-link">
                <h3 class="article-title">{{ article.title }}</h3>
                <div class="article-meta">
                  <span class="article-category">{{ article.category }}</span>
                  <span class="article-date">{{ formatDate(article.write_date) }}</span>
                </div>
              </RouterLink>
            </div>
          </div>
        </ContentBox>
      </div>
    </template>
  </div>
</template>

<script setup>
// Chart.js 관련 컴포넌트 및 요소 임포트
import { Bar, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  ArcElement,      // 원형/도넛 차트를 위한 요소
  Tooltip,         // 툴팁 기능
  Legend,          // 범례 기능
  BarElement,      // 막대 차트를 위한 요소
  CategoryScale,   // 카테고리 축 스케일
  LinearScale,     // 선형 축 스케일
} from "chart.js";
// 공통 UI 컴포넌트 임포트
import ContentBox from "@/common/ContentBox.vue";
// Vue Composition API의 반응형 상태 관리를 위한 ref 임포트
import { ref, computed, onMounted } from "vue";
// 날짜 포맷팅을 위한 커스텀 컴포저블 훅 임포트
import { useDate } from "@/composables/useDate";
// axios 임포트
import axios from "axios";
// 인증 스토어 임포트
import { useAuthStore } from "@/stores/auth";
import { useRouter, RouterLink } from "vue-router";

// Chart.js 사용을 위한 필요 컴포넌트 등록
ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

// API 기본 URL 설정
const API_BASE_URL = 'http://127.0.0.1:8000';

// 라우터 및 인증 스토어 가져오기
const router = useRouter();
const authStore = useAuthStore();
const { formatDate } = useDate();

// 상태 변수 초기화
const loading = ref(true);
const error = ref(null);

// 카테고리 색상 배열
const categoryColors = [
  '#FF6384', // 빨간색
  '#36A2EB', // 파란색
  '#FFCE56', // 노란색
  '#4BC0C0', // 청록색
  '#9966FF', // 보라색
  '#FF9F40', // 주황색
  '#C9CBCF', // 회색
  '#7BC043', // 녹색
  '#F37736', // 주황색
  '#7C5295'  // 보라색
];

// 카테고리 데이터를 위한 반응형 객체 (도넛 차트용)
const categoryData = ref({
  labels: [],           // 카테고리 이름 배열
  datasets: [
    {
      data: [],         // 카테고리별 기사 수 배열
      backgroundColor: [], // 각 카테고리 색상 배열
    },
  ],
});
// 카테고리 정보를 위한 반응형 배열 (레이블 표시용)
const categories = ref([]);
// 좋아요 누른 기사 목록을 위한 반응형 배열
const favoriteArticles = ref([]);

// 키워드 데이터를 위한 반응형 객체 (가로 막대 차트용)
const keywordData = ref({
  labels: [],           // 키워드 레이블 배열
  datasets: [
    {
      label: "키워드 빈도수",
      data: [],         // 키워드 빈도수 배열
      backgroundColor: "#C7E4B8", // 차트 색상
    },
  ],
});

// 주간 읽은 기사 데이터를 위한 반응형 객체 (세로 막대 차트용)
const readData = ref({
  labels: [],           // 요일 레이블 배열
  datasets: [
    {
      label: "읽은 기사 수",
      data: [],         // 일별 읽은 기사 수 배열
      backgroundColor: "#DBB8E4", // 차트 색상
    },
  ],
});

// 데이터 존재 여부 확인을 위한 computed 속성
const hasCategoryData = computed(() => categories.value.length > 0);
const hasKeywordData = computed(() => keywordData.value.labels.length > 0);
const hasWeeklyData = computed(() => {
  return readData.value.datasets[0].data.some(value => value > 0);
});

// 도넛 차트 옵션 설정
const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,      // 범례 표시 여부
      position: "right",  // 범례 위치
      labels: {
        padding: 15,      // 범례 패딩
        boxWidth: 20,     // 범례 상자 너비
        font: {
          size: 14,       // 범례 폰트 크기
        },
      },
    },
    tooltip: {
      callbacks: {
        // 툴팁 커스터마이징 - 기사 수 표시
        label: (context) => {
          const label = context.label || "";
          const value = context.raw;
          return `${label}: ${value}개`;
        },
      },
    },
  },
};

// 가로 막대 차트(키워드) 옵션 설정
const barOptions = {
  indexAxis: "y",        // y축을 인덱스 축으로 사용 (가로 막대)
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      beginAtZero: true, // x축 0부터 시작
      title: {
        display: true,
        text: '빈도수'
      }
    },
    y: {
      title: {
        display: true,
        text: '키워드'
      }
    }
  },
  plugins: {
    legend: {
      display: false,    // 범례 숨김
    },
  },
};

// 세로 막대 차트(주간 읽은 기사) 옵션 설정
const readBarOptions = {
  indexAxis: "x",        // x축을 인덱스 축으로 사용 (세로 막대)
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true, // y축 0부터 시작
      title: {
        display: true,
        text: '읽은 기사 수'
      }
    },
    x: {
      title: {
        display: true,
        text: '요일'
      }
    }
  },
  plugins: {
    legend: {
      display: false,    // 범례 숨김
    },
  },
};

// 대시보드 데이터 가져오기
const fetchDashboardData = async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  try {
    const response = await axios.get(`${API_BASE_URL}/api/news/dashboard/`);
    
    // 카테고리 데이터 설정
    const categoryStats = response.data.category_stats || [];
    categories.value = categoryStats;
    
    if (categoryStats.length > 0) {
      categoryData.value.labels = categoryStats.map(cat => cat.name);
      categoryData.value.datasets[0].data = categoryStats.map(cat => cat.count);
      categoryData.value.datasets[0].backgroundColor = categoryStats.map((_, i) => 
        categoryColors[i % categoryColors.length]
      );
    }
    
    // 키워드 데이터 설정
    const keywordStats = response.data.keyword_stats || [];
    if (keywordStats.length > 0) {
      keywordData.value.labels = keywordStats.map(kw => kw.keyword);
      keywordData.value.datasets[0].data = keywordStats.map(kw => kw.count);
    }
    
    // 주간 읽은 기사 데이터 설정
    const weeklyViews = response.data.weekly_views || [];
    if (weeklyViews.length > 0) {
      // 요일을 한글로 변환
      const dayTranslation = {
        'Monday': '월요일',
        'Tuesday': '화요일',
        'Wednesday': '수요일',
        'Thursday': '목요일',
        'Friday': '금요일',
        'Saturday': '토요일',
        'Sunday': '일요일'
      };
      
      readData.value.labels = weeklyViews.map(day => dayTranslation[day.day] || day.day);
      readData.value.datasets[0].data = weeklyViews.map(day => day.count);
    }
    
    // 좋아요 누른 기사 목록 설정
    favoriteArticles.value = response.data.liked_articles || [];
    
  } catch (err) {
    console.error('대시보드 데이터를 가져오는 중 오류 발생:', err);
    error.value = '데이터를 불러오는 중 오류가 발생했습니다. 나중에 다시 시도해주세요.';
  } finally {
    loading.value = false;
  }
};

// 컴포넌트 마운트 시 데이터 가져오기
onMounted(() => {
  fetchDashboardData();
});
</script>

<style scoped lang="scss">
.title {
  margin: 0;
  font-size: 25px;
}

.subtitle {
  font-weight: 500;
  margin-bottom: 40px;
}

.loading-container, .error-container, .no-data-message {
  text-align: center;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
}

.error-container {
  background-color: #fff3f3;
  color: #d32f2f;
}

.no-data-message {
  color: #757575;
  font-style: italic;
  background-color: #f5f5f5;
  padding: 40px 20px;
}

.like-news {
  overflow-y: auto;
  box-sizing: border-box;
  max-height: 450px;
}

.dashboard {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card_description {
  margin: 10px;
  color: #666;
  font-size: 0.9rem;
}

.layout {
  display: flex;
  gap: 20px;
  > * {
    height: 450px;
    flex: 1;
  }

  @media (max-width: 768px) {
    flex-direction: column;
  }
}

.category {
  &__chart {
    height: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    padding-bottom: 30px;
  }
  
  &__labels {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 15px;
  }
  
  &__label {
    border: 1px solid;
    padding: 3px 8px;
    border-radius: 10px;
    margin-right: 5px;
    font-size: 0.85rem;
  }
}

.favorite-articles {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
  
  .favorite-article {
    padding: 10px;
    border-bottom: 1px solid #eee;
    
    &:last-child {
      border-bottom: none;
    }
    
    .article-link {
      text-decoration: none;
      color: inherit;
      display: block;
      
      &:hover {
        .article-title {
          color: #0c3057;
        }
      }
    }
    
    .article-title {
      margin: 0 0 5px 0;
      font-size: 1rem;
      transition: color 0.2s;
    }
    
    .article-meta {
      display: flex;
      gap: 15px;
      font-size: 0.8rem;
      color: #777;
    }
  }
}

h1 {
  margin-bottom: 20px;
  font-size: 1.2rem;
  color: #0c3057;
}

.keyword-chart {
  max-height: 80% ;
  width: 85% ;
}

.weekly-chart {
  max-height: 80%;
  width: 85%;
}
</style>