<!-- 
  뉴스 챗봇 컴포넌트
  RAG 기반으로 뉴스 기사에 대한 질문과 답변을 처리하는 챗봇 인터페이스
-->
<template>
  <div class="chatbot-container">
    <h3 class="chatbot-title">
      <span class="chatbot-icon">🤖</span> 뉴스 AI 챗봇
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
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';

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
    // 백엔드 연동 부분 (현재는 모의 응답)
    // 실제 구현 시 axios를 사용하여 백엔드 API 호출
    await simulateResponse(userQuery);
  } catch (error) {
    console.error('챗봇 응답 처리 중 오류 발생:', error);
    // 오류 메시지 표시
    messages.value.push({
      role: 'assistant',
      content: '죄송합니다. 응답을 처리하는 중에 오류가 발생했습니다.'
    });
  } finally {
    // 로딩 상태 비활성화
    isLoading.value = false;
    // 스크롤 아래로 이동
    await scrollToBottom();
  }
};

// 모의 응답 함수 (백엔드 연동 전까지 임시 사용)
const simulateResponse = async (query) => {
  // 실제 구현에서는 이 부분을 백엔드 API 호출로 대체
  return new Promise((resolve) => {
    setTimeout(() => {
      // 뉴스 기사 내용 기반 모의 응답
      const newsTitle = props.news.title;
      const newsContent = props.news.content.substring(0, 100); // 내용 일부만 사용
      
      let response;
      if (query.includes('요약')) {
        response = `이 기사는 "${newsTitle}"에 관한 내용으로, ${newsContent}... 등의 내용을 다루고 있습니다.`;
      } else if (query.includes('작성자')) {
        response = `이 기사의 작성자는 ${props.news.writer}입니다.`;
      } else if (query.includes('날짜') || query.includes('언제')) {
        response = `이 기사는 ${new Date(props.news.write_date).toLocaleDateString()}에 작성되었습니다.`;
      } else {
        response = `질문하신 "${query}"에 대해 답변드리자면, 이 기사는 ${newsTitle}에 관한 내용입니다. 더 구체적인 질문이 있으시면 말씀해주세요.`;
      }
      
      // 응답 메시지 추가
      messages.value.push({
        role: 'assistant',
        content: response
      });
      
      resolve();
    }, 1000); // 1초 지연으로 응답 시뮬레이션
  });
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

// 컴포넌트가 마운트될 때 뉴스 정보를 기반으로 초기 메시지 설정
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
  
  .chatbot-icon {
    margin-right: 8px;
    font-size: 20px;
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