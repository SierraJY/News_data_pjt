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
      <span>❤️ {{ props.news.like_count || 0 }}</span>
      <!-- 원본 링크는 클릭 이벤트 전파를 막아서 카드 클릭 없이 직접 이동 가능 -->
      <a @click.stop :href="props.news.url" target="_blank">📄</a>
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
  padding: 22px 25px;
  margin-bottom: 0;
  display: block;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #f0f0f0;
  position: relative;
  overflow: hidden;

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
    width: 4px;
    height: 100%;
    background-color: #0c3057;
    opacity: 0;
    transition: opacity 0.3s ease;

    .dark-mode & {
      background-color: var(--c-main);
    }
  }

  &:hover {
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-3px);
    
    .dark-mode & {
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
      background-color: var(--c-hover-bg);
    }
    
    &::before {
      opacity: 1;
    }
  }

  &__header {
    display: flex;
    align-items: center;
    gap: 8px;
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
    margin: 14px 0;
    font-size: 20px;
    font-weight: 700;
    color: #1c1c1e;
    line-height: 1.3;
    
    .dark-mode & {
      color: var(--c-text);
    }
  }

  .description {
    font-size: 15px;
    width: 95%;
    color: #555;
    margin: 15px 0;
    display: -webkit-box;
    -webkit-line-clamp: 3;  /* 최대 3줄까지만 표시 */
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.5;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
  }

  .stats {
    display: flex;
    gap: 15px;
    font-size: 0.85rem;
    color: #666;
    margin: 15px 0;
    align-items: center;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
    
    a {
      color: #0c3057;
      transition: transform 0.2s;
      
      .dark-mode & {
        color: var(--c-main);
      }
      
      &:hover {
        transform: scale(1.2);
      }
    }
  }

  .tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    padding-bottom: 5px;
    margin-top: 10px;
  }
}
</style>