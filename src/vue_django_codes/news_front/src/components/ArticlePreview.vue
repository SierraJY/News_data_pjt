<!-- 
  뉴스 미리보기 컴포넌트
  관련 기사 목록에서 간략한 정보만 보여주는 컴포넌트
-->
<template>
  <RouterLink :to="to" class="preview">
    <div class="preview__container" v-if="article">
      <!-- 미리보기 헤더: 카테고리와 날짜 -->
      <div class="preview__header">
        <StateButton type="state" size="sm" disabled>{{ article.category }}</StateButton>
        <span> 🕒 {{ formatDate(article.write_date) }}</span>
      </div>
      
      <!-- 미리보기 제목 -->
      <h3 class="preview__title">{{ article.title }}</h3>
      
      <!-- 통계 정보: 좋아요 -->
      <div class="preview__stats">
        <span>❤️ {{ article.like_count || 0 }}</span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import axios from 'axios';
import { parseKeywords } from '@/utils/keywords';

// API 기본 URL 설정
const API_BASE_URL = 'http://127.0.0.1:8000';

// props 정의
const props = defineProps({
  id: {
    type: Number,
    required: true
  },
  to: {
    type: String,
    required: true
  }
});

// 뉴스 기사 데이터
const article = ref(null);

// 파싱된 키워드 배열을 computed 속성으로 정의
const keywords = computed(() => {
  if (!article.value || !article.value.keywords) return [];
  return parseKeywords(article.value.keywords);
});

// ID로 뉴스 데이터 가져오기
const fetchArticle = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/news/${props.id}/`);
    article.value = response.data;
  } catch (err) {
    console.error(`기사 ID ${props.id}를 가져오는 중 오류 발생:`, err);
  }
};

// 컴포넌트 마운트 시 데이터 가져오기
onMounted(() => {
  fetchArticle();
});

// 날짜 포맷팅 함수 사용
const { formatDate } = useDate();
</script>

<style scoped lang="scss">
.preview {
  display: block;
  padding: 15px 10px;
  text-decoration: none;
  color: inherit;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #f5f5f5;
  }
  
  &__container {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  &__header {
    display: flex;
    align-items: center;
    gap: 15px;
    font-size: 0.85rem;
    color: #888;
  }
  
  &__title {
    font-size: 16px;
    font-weight: 600;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  &__stats {
    display: flex;
    gap: 15px;
    font-size: 0.85rem;
    color: #888;
  }
}
</style>