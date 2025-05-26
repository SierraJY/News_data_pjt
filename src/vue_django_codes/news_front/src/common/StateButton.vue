<script setup>
import { computed, useAttrs, defineProps } from "vue";
import { useRouter } from "vue-router";

const props = defineProps();
const type = computed(() => props.type || "button");
const size = computed(() => props.size || "md");
const isActive = computed(() => props.isActive || false);

const router = useRouter();

const buttonSizeClass = computed(() => size.value);
const buttonTypeClass = computed(() => type.value);

const attrs = useAttrs();

function handleClick() {
  if (props.to) {
    router.push(props.to);
  }
}
</script>

<template>
  <button
    :class="[
      'toggle-button',
      props.class,
      buttonSizeClass,
      buttonTypeClass,
      { active: isActive },
    ]"
    v-bind="attrs"
    @click="handleClick"
  >
    <slot></slot>
  </button>
</template>

<style scoped lang="scss">
.toggle-button {
  white-space: nowrap;
  padding: 10px 20px;
  font-size: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background-color: white;
  color: #333;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  
  .dark-mode & {
    background-color: var(--c-card-bg);
    border-color: var(--c-border);
    color: var(--c-text);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }

  &.tag {
    background-color: #f8f9fa;
    color: #0c3057;
    cursor: default;
    border: none;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    box-shadow: none;
    
    .dark-mode & {
      background-color: rgba(0, 70, 157, 0.15);
      color: var(--c-main);
    }
  }

  &.state {
    background-color: #f5f8fc;
    color: #0c3057;
    border: 1px solid #e1e8f0;
    
    .dark-mode & {
      background-color: rgba(0, 70, 157, 0.2);
      color: var(--c-main);
      border-color: var(--c-border);
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

    &:hover {
      background-color: #0a2744;
      
      .dark-mode & {
        background-color: #0055c4;
      }
    }
  }

  &:hover {
    background-color: #f5f7fa;
    border-color: #d1d5db;
    transform: translateY(-1px);
    
    .dark-mode & {
      background-color: var(--c-hover-bg);
      border-color: var(--c-border);
    }
  }

  &.sm {
    padding: 4px 10px;
    font-size: 12px;
    border-radius: 6px;
  }

  &.md {
    padding: 8px 12px;
    font-size: 14px;
  }

  &:disabled {
    pointer-events: none;
    opacity: 0.9;
  }
}
</style>
