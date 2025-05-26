<script setup>
import { computed } from "vue";

const props = defineProps({
  modelValue: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(["update:modelValue"]);

// 현재 페이지
const currentPage = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val)
});

// 페이지 번호 배열 생성 (최대 9개)
const pageNumbers = computed(() => {
  const totalVisible = 9; // 표시할 페이지 번호 개수
  
  if (props.totalPages <= totalVisible) {
    // 전체 페이지 수가 9개 이하면 모든 페이지 번호 표시
    return Array.from({ length: props.totalPages }, (_, i) => i + 1);
  }
  
  // 중앙 기준 표시할 페이지 수 (총 9개 중 양쪽에 4개씩)
  const sideItems = Math.floor(totalVisible / 2);
  
  // 시작 페이지 계산
  let startPage = Math.max(currentPage.value - sideItems, 1);
  // 끝 페이지 계산
  let endPage = Math.min(startPage + totalVisible - 1, props.totalPages);
  
  // 끝 페이지가 최대 페이지 수에 도달한 경우, 시작 페이지 조정
  if (endPage === props.totalPages) {
    startPage = Math.max(endPage - totalVisible + 1, 1);
  }
  
  return Array.from(
    { length: endPage - startPage + 1 },
    (_, i) => startPage + i
  );
});

// 페이지 이동 함수
function goToPage(page) {
  if (page >= 1 && page <= props.totalPages) {
    currentPage.value = page;
  }
}
</script>

<template>
  <div class="pagination" v-if="props.totalPages > 1">
    <!-- 이전 페이지 버튼 -->
    <button 
      class="pagination__nav-btn" 
      @click="goToPage(currentPage - 1)" 
      :disabled="currentPage === 1"
      title="이전 페이지"
    >
      &lt;
    </button>
    
    <!-- 페이지 번호 버튼 -->
    <div class="pagination__pages">
      <button
        v-for="page in pageNumbers"
        :key="page"
        @click="goToPage(page)"
        :class="['pagination__page-btn', { active: currentPage === page }]"
      >
        {{ page }}
      </button>
    </div>
    
    <!-- 다음 페이지 버튼 -->
    <button 
      class="pagination__nav-btn" 
      @click="goToPage(currentPage + 1)" 
      :disabled="currentPage === props.totalPages"
      title="다음 페이지"
    >
      &gt;
    </button>
  </div>
</template>

<style scoped lang="scss">
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 30px;
  
  &__pages {
    display: flex;
    gap: 4px;
  }
  
  &__page-btn, &__nav-btn {
    min-width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #e0e0e0;
    background-color: white;
    color: #333;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
    
    .dark-mode & {
      background-color: var(--c-card-bg);
      border-color: var(--c-border);
      color: var(--c-text);
    }
    
    &:hover:not(:disabled) {
      background-color: #f0f0f0;
      
      .dark-mode & {
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
    
    &:disabled {
      background-color: #f5f5f5;
      color: #ccc;
      cursor: not-allowed;
      
      .dark-mode & {
        background-color: var(--c-bg);
        color: var(--c-border);
      }
    }
  }
  
  &__nav-btn {
    font-weight: bold;
  }
}
</style>