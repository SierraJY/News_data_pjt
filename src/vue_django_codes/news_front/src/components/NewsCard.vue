<!--
  뉴스 카드 컴포넌트
  뉴스 목록에서 각 뉴스 항목을 표시하는 카드 형태의 컴포넌트
-->
<template>
  <!-- 전체 카드가 클릭 가능한 RouterLink로 구성 -->
  <RouterLink 
    class="card"
    :to="{ 
      name: 'newsDetail', 
      params: { id: props.news.id }
    }"
    v-if="props.news"
  >
    <!-- 카드 헤더: 카테고리, 작성자, 날짜 -->
    <div class="card__header">
      <!-- 카테고리 버튼 -->
      <StateButton type="state" size="sm" disabled>
        {{ props.news.category }}
      </StateButton>
      <span class="card__header-item">{{ props.news.writer }}</span>
      <span class="card__header-item">· {{ formatDate(props.news.write_date) }}</span>
    </div>

    <!-- 카드 본문: 제목과 내용 요약 -->
    <div>
      <h2 class="title">{{ props.news.title }}</h2>
      <p class="description">{{ props.news.content }}</p>
    </div>
    
    <!-- 통계 정보: 좋아요, 원본 링크 -->
    <div class="stats">
      <span class="stats-item">
        <span class="stats-icon like-icon">❤️</span>
        {{ props.news.like_count || 0 }}
      </span>
      <!-- 원본 링크는 클릭 이벤트 전파를 막아서 카드 클릭 없이 직접 이동 가능 -->
      <a @click.stop :href="props.news.url" target="_blank" class="stats-item">
        <span class="stats-icon">📄</span>
        원본 링크
      </a>
    </div>

    <!-- 키워드 태그 목록 (키워드가 있는 경우에만 표시) -->
    <div v-if="keywords.length" class="tags">
      <StateButton
        v-for="(tag, index) in keywords"
        :key="index"
        type="tag"
        size="sm"
      >
        #{{ tag }}
      </StateButton>
    </div>
  </RouterLink>
</template>

<script setup>
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import { computed } from "vue";
import { parseKeywords } from '@/utils/keywords';

// props 정의: 전체 뉴스 객체를 직접 전달받음
const props = defineProps({
  news: {
    type: Object,
    required: true
  }
});

// 키워드 처리 로직 (백엔드 응답 형식에 맞게 변환)
const keywords = computed(() => {
  return parseKeywords(props.news.keywords);
});

// 날짜 포맷팅 함수 사용
const { formatDate } = useDate();
</script>

<style scoped lang="scss">
.card {
  background-color: white;
  width: 100%;
  padding: 24px 28px;
  margin-bottom: 0;
  display: block;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  border: 1px solid #f0f0f0;
  position: relative;
  overflow: hidden;
  background-image: var(--gradient-card);
  background-position: top;
  background-repeat: no-repeat;

  .dark-mode & {
    background-color: var(--c-card-bg);
    border-color: var(--c-border);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 5px;
    height: 100%;
    background: var(--gradient-accent);
    opacity: 0;
    transition: opacity 0.3s ease;
    border-radius: 4px 0 0 4px;
  }

  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-4px);
    
    .dark-mode & {
      background-color: var(--c-hover-bg);
    }
    
    &::before {
      opacity: 1;
    }
    
    .title {
      color: var(--c-main);
      
      .dark-mode & {
        color: var(--c-main-light);
      }
    }
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.85rem;
    color: #888;
    flex-wrap: wrap;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
    
    &-item {
      font-weight: normal;
    }
  }

  .title {
    margin: 16px 0;
    font-size: 20px;
    font-weight: 700;
    color: #1c1c1e;
    line-height: 1.4;
    transition: color 0.3s ease;
    
    .dark-mode & {
      color: var(--c-text);
    }
  }

  .description {
    font-size: 15px;
    width: 95%;
    color: #555;
    margin: 16px 0;
    display: -webkit-box;
    -webkit-line-clamp: 3;  /* 최대 3줄까지만 표시 */
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.6;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
  }

  .stats {
    display: flex;
    gap: 20px;
    font-size: 14px;
    color: #666;
    margin: 16px 0;
    align-items: center;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
    
    &-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    
    &-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    
    .like-icon {
      transform: scale(0.9);
    }
    
    a {
      color: var(--c-main);
      transition: all 0.2s ease;
      text-decoration: none;
      
      .dark-mode & {
        color: var(--c-main-light);
      }
      
      &:hover {
        color: var(--c-accent);
        transform: translateY(-1px);
      }
    }
  }

  .tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    padding-bottom: 5px;
    margin-top: 12px;
  }
}
</style>