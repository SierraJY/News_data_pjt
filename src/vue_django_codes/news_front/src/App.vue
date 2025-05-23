<template>
  <!-- 
    조건부 렌더링: 로그인 또는 회원가입 페이지가 아닐 때만 헤더 표시
    route.path를 체크하여 현재 경로에 따라 헤더 표시 여부 결정
  -->
  <TheHeader v-if="route.path !== '/login' && route.path !== '/register'" />
  
  <!-- 
    메인 콘텐츠 영역: 실제 라우팅된 컴포넌트가 이곳에 표시됨
    RouterView는 현재 경로에 해당하는 컴포넌트를 렌더링
  -->
  <main>
    <RouterView />
  </main>
  
  <!-- 
    조건부 렌더링: 로그인 또는 회원가입 페이지가 아닐 때만 푸터 표시
    route.path를 체크하여 현재 경로에 따라 푸터 표시 여부 결정
  -->
  <TheFooter v-if="route.path !== '/login' && route.path !== '/register'" />
</template>

<script setup>
// Vue Router의 useRoute 훅을 가져옴 - 현재 라우트 정보에 접근하기 위해 사용
import { useRoute } from "vue-router";
// 헤더 컴포넌트 임포트
import TheHeader from "./components/TheHeader.vue";
// 푸터 컴포넌트 임포트
import TheFooter from "./components/TheFooter.vue";

// useRoute 훅을 사용하여 현재 라우트 정보를 가져옴
// 이를 통해 현재 페이지 경로에 따라 헤더와 푸터 표시 여부 결정
const route = useRoute();
</script>

<style lang="scss">
main {
  max-width: 1280px;
  min-width: 360px;
  min-height: 100vh;
  margin: 0 auto;
  padding: 15px 15px 50px;
}
</style>