<!-- 
  뉴스 챗봇 컴포넌트
  RAG 기반으로 뉴스 기사에 대한 질문과 답변을 처리하는 챗봇 인터페이스
-->
<template>
  <div class="chatbot-container">
    <h3 class="chatbot-title">
      <span class="chatbot-icon">🤖</span> 뉴스 AI 챗봇
      <button class="reset-button" @click="resetChat" v-if="authStore.isAuthenticated">
        <span class="reset-icon">🔄</span> 대화 초기화
      </button>
    </h3>
    
    <div class="chat-messages" ref="chatMessagesRef">
      <!-- 시스템 메시지 (환영 메시지) -->
      <div class="message system">
        <div class="message-content">
          <p>안녕하세요! 이 뉴스 기사에 대해 궁금한 점이 있으시면 질문해주세요.</p>
        </div>
      </div>
      
      <!-- 채팅 메시지 목록 -->
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        :class="['message', message.role]"
      >
        <div class="message-avatar">
          <!-- 사용자 아바타 -->
          <span v-if="message.role === 'user'">👤</span>
          <!-- AI 아바타 -->
          <span v-else-if="message.role === 'assistant'">🤖</span>
        </div>
        <div class="message-content">
          <p>{{ message.content }}</p>
        </div>
      </div>
      
      <!-- 로딩 표시 -->
      <div v-if="isLoading" class="message assistant loading">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 메시지 입력 폼 -->
    <div class="chat-input">
      <input
        type="text"
        v-model="userInput"
        placeholder="뉴스에 대해 질문하세요..."
        @keyup.enter="sendMessage"
        :disabled="isLoading"
      />
      <button 
        class="send-button" 
        @click="sendMessage" 
        :disabled="!userInput.trim() || isLoading"
      >
        전송
      </button>
    </div>
    
    <!-- 로그인 유도 메시지 -->
    <div v-if="!authStore.isAuthenticated" class="login-prompt">
      <p>로그인하시면 대화 내용이 저장되어 더 자연스러운 대화가 가능합니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

// 인증 스토어
const authStore = useAuthStore();

// API 기본 URL
const API_BASE_URL = 'http://127.0.0.1:8000';

// 컴포넌트 props 정의
const props = defineProps({
  // 뉴스 기사 객체
  news: {
    type: Object,
    required: true
  }
});

// 사용자 입력을 저장하는 반응형 변수
const userInput = ref('');
// 채팅 메시지 목록을 저장하는 반응형 변수
const messages = ref([]);
// 로딩 상태를 저장하는 반응형 변수
const isLoading = ref(false);
// 채팅 메시지 컨테이너에 대한 참조
const chatMessagesRef = ref(null);

// 메시지 전송 함수
const sendMessage = async () => {
  // 입력이 비어있으면 무시
  if (!userInput.value.trim()) return;
  
  // 사용자 메시지 추가
  const userMessage = {
    role: 'user',
    content: userInput.value
  };
  messages.value.push(userMessage);
  
  // 입력 필드 초기화
  const userQuery = userInput.value;
  userInput.value = '';
  
  // 로딩 상태 활성화
  isLoading.value = true;
  
  // 스크롤 아래로 이동
  await scrollToBottom();
  
  try {
    let response;
    
    // 로그인 여부에 따라 다른 API 호출
    if (authStore.isAuthenticated) {
      // 로그인 사용자: 세션 기반 챗봇 API 호출
      response = await axios.post(
        `${API_BASE_URL}/api/news/chatbot/`,
        {
          article_id: props.news.id,
          question: userQuery
        },
        {
          headers: {
            Authorization: `Bearer ${authStore.accessToken}`
          }
        }
      );
    } else {
      // 비로그인 사용자: 익명 챗봇 API 호출
      response = await axios.post(
        `${API_BASE_URL}/api/news/chatbot/anonymous/`,
        {
          title: props.news.title,
          writer: props.news.writer,
          write_date: props.news.write_date,
          content: props.news.content,
          question: userQuery
        }
      );
    }
    
    // 응답 메시지 추가
    messages.value.push({
      role: 'assistant',
      content: response.data.response
    });
  } catch (error) {
    console.error('챗봇 응답 처리 중 오류 발생:', error);
    
    // API 오류 메시지 표시
    let errorMessage = '죄송합니다. 응답을 처리하는 중에 오류가 발생했습니다.';
    if (error.response && error.response.data && error.response.data.error) {
      errorMessage = error.response.data.error;
    }
    
    // 오류 메시지 추가
    messages.value.push({
      role: 'assistant',
      content: errorMessage
    });
  } finally {
    // 로딩 상태 비활성화
    isLoading.value = false;
    // 스크롤 아래로 이동
    await scrollToBottom();
  }
};

// 대화 초기화 함수
const resetChat = async () => {
  if (!authStore.isAuthenticated || !props.news.id) return;
  
  try {
    await axios.post(
      `${API_BASE_URL}/api/news/chatbot/reset/${props.news.id}/`,
      {},
      {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`
        }
      }
    );
    
    // 메시지 초기화
    messages.value = [];
    
    // 시스템 메시지 추가
    messages.value.push({
      role: 'system',
      content: '대화가 초기화되었습니다. 새로운 질문을 해보세요!'
    });
  } catch (error) {
    console.error('대화 초기화 중 오류 발생:', error);
  }
};

// 채팅창을 아래로 스크롤하는 함수
const scrollToBottom = async () => {
  await nextTick();
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight;
  }
};

// 메시지가 추가될 때마다 스크롤 아래로 이동
watch(() => messages.value.length, scrollToBottom);

// 컴포넌트가 마운트될 때 스크롤 초기화
onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped lang="scss">
.chatbot-container {
  margin-top: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: #f9f9f9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.chatbot-title {
  background-color: #4a7bae;
  color: white;
  padding: 15px;
  margin: 0;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .chatbot-icon {
    margin-right: 8px;
    font-size: 20px;
  }
  
  .reset-button {
    background: none;
    border: 1px solid rgba(255, 255, 255, 0.5);
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    
    &:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }
    
    .reset-icon {
      margin-right: 5px;
    }
  }
}

.chat-messages {
  padding: 15px;
  height: 350px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
  background-color: #fff;
}

.message {
  display: flex;
  max-width: 80%;
  
  &.user {
    align-self: flex-end;
    flex-direction: row-reverse;
    
    .message-content {
      background-color: #4a7bae;
      color: white;
      border-radius: 18px 18px 0 18px;
    }
    
    .message-avatar {
      margin-left: 8px;
      margin-right: 0;
    }
  }
  
  &.assistant {
    align-self: flex-start;
    
    .message-content {
      background-color: #f0f0f0;
      border-radius: 18px 18px 18px 0;
    }
  }
  
  &.system {
    align-self: center;
    
    .message-content {
      background-color: #f5f5f5;
      border-radius: 18px;
      color: #666;
      font-style: italic;
    }
  }
  
  &.loading {
    .message-content {
      padding: 10px 15px;
    }
  }
}

.message-avatar {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 8px;
}

.message-content {
  padding: 10px 15px;
  
  p {
    margin: 0;
    line-height: 1.4;
    white-space: pre-wrap;
    word-break: break-word;
  }
}

.chat-input {
  display: flex;
  padding: 15px;
  background-color: #fff;
  border-top: 1px solid #e0e0e0;
  
  input {
    flex: 1;
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 20px;
    outline: none;
    font-size: 14px;
    
    &:focus {
      border-color: #4a7bae;
    }
    
    &:disabled {
      background-color: #f5f5f5;
      cursor: not-allowed;
    }
  }
  
  .send-button {
    margin-left: 10px;
    padding: 8px 20px;
    background-color: #4a7bae;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-size: 14px;
    transition: background-color 0.2s;
    
    &:hover {
      background-color: #3a6a9e;
    }
    
    &:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }
  }
}

.login-prompt {
  padding: 10px 15px;
  background-color: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  text-align: center;
  font-size: 12px;
  color: #666;
}

// 타이핑 표시기 애니메이션
.typing-indicator {
  display: flex;
  align-items: center;
  
  span {
    height: 8px;
    width: 8px;
    margin: 0 2px;
    background-color: #888;
    display: block;
    border-radius: 50%;
    opacity: 0.4;
    animation: typing 1s infinite;
    
    &:nth-child(1) {
      animation-delay: 0s;
    }
    
    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

@keyframes typing {
  0% {
    opacity: 0.4;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
  100% {
    opacity: 0.4;
    transform: scale(1);
  }
}
</style> 