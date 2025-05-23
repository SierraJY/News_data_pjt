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
    
    <!-- 로그인 되어 있을 때만 챗봇 인터페이스 표시 -->
    <div v-if="authStore.isAuthenticated">
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
            <img v-else-if="message.role === 'assistant'" src="@/components/icons/chatgpt.png" alt="AI" class="ai-avatar">
          </div>
          <div class="message-content">
            <p>{{ message.content }}</p>
          </div>
        </div>
        
        <!-- 로딩 표시 -->
        <div v-if="isLoading" class="message assistant loading">
          <div class="message-avatar">
            <img src="@/components/icons/chatgpt.png" alt="AI" class="ai-avatar">
          </div>
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
    </div>
    
    <!-- 로그인 유도 메시지 (로그인하지 않은 경우) -->
    <div v-else class="login-required">
      <div class="login-icon">🔒</div>
      <h4>로그인이 필요한 기능입니다</h4>
      <p>뉴스 AI 챗봇을 이용하시려면 로그인해주세요.</p>
      <router-link to="/login" class="login-button">로그인하기</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

// 인증 스토어
const authStore = useAuthStore();
const router = useRouter();

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
  // 로그인되지 않은 경우 처리
  if (!authStore.isAuthenticated) {
    return;
  }
  
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
    // 로그인 사용자: 세션 기반 챗봇 API 호출
    const response = await axios.post(
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
  
  .dark-mode & {
    background-color: var(--c-card-bg);
    border-color: var(--c-border);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
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
  
  .dark-mode & {
    background-color: var(--c-main);
  }
  
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
  
  .dark-mode & {
    background-color: var(--c-bg);
  }
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
      
      .dark-mode & {
        background-color: var(--c-main);
      }
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
      
      .dark-mode & {
        background-color: var(--c-card-bg);
        color: var(--c-text);
      }
    }
  }
  
  &.system {
    align-self: center;
    
    .message-content {
      background-color: #f5f5f5;
      border-radius: 18px;
      color: #666;
      font-style: italic;
      
      .dark-mode & {
        background-color: var(--c-hover-bg);
        color: var(--c-gray-500);
      }
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
  
  .ai-avatar {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
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
  
  .dark-mode & {
    background-color: var(--c-bg);
    border-top-color: var(--c-border);
  }
  
  input {
    flex: 1;
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 20px;
    outline: none;
    font-size: 14px;
    
    .dark-mode & {
      background-color: var(--c-input-bg);
      border-color: var(--c-input-border);
      color: var(--c-text);
    }
    
    &:focus {
      border-color: #4a7bae;
      
      .dark-mode & {
        border-color: var(--c-main);
      }
    }
    
    &:disabled {
      background-color: #f5f5f5;
      cursor: not-allowed;
      
      .dark-mode & {
        background-color: rgba(0, 0, 0, 0.2);
      }
    }
    
    &::placeholder {
      .dark-mode & {
        color: var(--c-gray-500);
      }
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
    
    .dark-mode & {
      background-color: var(--c-main);
    }
    
    &:hover {
      background-color: #3a6a9e;
      
      .dark-mode & {
        background-color: #0055c4;
      }
    }
    
    &:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
      
      .dark-mode & {
        background-color: #1e3756;
      }
    }
  }
}

.login-required {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
  background-color: #fff;
  text-align: center;
  
  .dark-mode & {
    background-color: var(--c-bg);
  }
  
  .login-icon {
    font-size: 40px;
    margin-bottom: 15px;
    color: #4a7bae;
    
    .dark-mode & {
      color: var(--c-main);
    }
  }
  
  h4 {
    font-size: 18px;
    margin: 0 0 10px 0;
    color: #333;
    
    .dark-mode & {
      color: var(--c-text);
    }
  }
  
  p {
    font-size: 14px;
    color: #666;
    margin: 0 0 20px 0;
    
    .dark-mode & {
      color: var(--c-gray-500);
    }
  }
  
  .login-button {
    display: inline-block;
    background-color: #4a7bae;
    color: white;
    padding: 10px 20px;
    border-radius: 20px;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.2s;
    
    .dark-mode & {
      background-color: var(--c-main);
    }
    
    &:hover {
      background-color: #3a6a9e;
      
      .dark-mode & {
        background-color: #0055c4;
      }
    }
  }
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
    
    .dark-mode & {
      background-color: var(--c-gray-500);
    }
    
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