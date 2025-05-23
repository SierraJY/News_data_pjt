import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 로컬 스토리지에서 다크모드 상태 불러오기 (없으면 기본값 false)
  const isDarkMode = ref(localStorage.getItem('darkMode') === 'true')

  // 다크모드 토글 함수
  function toggleDarkMode() {
    isDarkMode.value = !isDarkMode.value
    localStorage.setItem('darkMode', isDarkMode.value)
    applyTheme()
  }

  // 다크모드 적용 함수
  function applyTheme() {
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark-mode')
    } else {
      document.documentElement.classList.remove('dark-mode')
    }
  }

  // 컴포넌트 초기화 시 테마 적용
  function initTheme() {
    applyTheme()
  }

  // 테마 변경을 감시하여 적용
  watch(isDarkMode, () => {
    applyTheme()
  })

  return {
    isDarkMode,
    toggleDarkMode,
    initTheme
  }
}) 