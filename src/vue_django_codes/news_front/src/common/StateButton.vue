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
  border-radius: 10px;
  background-color: white;
  color: #333;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  
  .dark-mode & {
    background-color: var(--c-card-bg);
    border-color: var(--c-border);
    color: var(--c-text);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }

  &.tag {
    background-color: rgba(10, 77, 149, 0.08);
    color: var(--c-main);
    cursor: default;
    border: none;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 12px;
    box-shadow: none;
    
    .dark-mode & {
      background-color: rgba(30, 136, 229, 0.15);
      color: var(--c-main-light);
    }
  }

  &.state {
    background-color: rgba(10, 77, 149, 0.08);
    color: var(--c-main);
    border: 1px solid rgba(10, 77, 149, 0.15);
    font-weight: 500;
    
    .dark-mode & {
      background-color: rgba(30, 136, 229, 0.15);
      color: var(--c-main-light);
      border-color: rgba(30, 136, 229, 0.2);
    }
  }

  &.active {
    background: var(--gradient-button);
    color: white;
    border-color: transparent;
    box-shadow: 0 2px 5px rgba(10, 77, 149, 0.2);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(10, 77, 149, 0.25);
    }
    
    &:active {
      transform: translateY(0);
    }
  }

  &:hover {
    background-color: #f5f7fa;
    border-color: #d1d5db;
    transform: translateY(-2px);
    
    .dark-mode & {
      background-color: var(--c-hover-bg);
      border-color: var(--c-border);
    }
  }

  &.sm {
    padding: 4px 12px;
    font-size: 12px;
    border-radius: 8px;
  }

  &.md {
    padding: 8px 16px;
    font-size: 14px;
  }

  &:disabled {
    pointer-events: none;
    opacity: 0.9;
  }
}
</style>
