<template>
  <div class="tts-controls">
    <button 
      class="tts-button"
      :class="{ 'is-playing': isPlaying }"
      @click="togglePlay"
      :disabled="loading"
    >
      <span class="button-icon">
        {{ isPlaying ? '⏹' : '▶' }}
      </span>
      {{ buttonText }}
    </button>
    <audio 
      ref="audioPlayer"
      @ended="handleEnded"
      style="display: none;"
    ></audio>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'TextToSpeech',
  props: {
    newsId: {
      type: [Number, String],
      required: true
    }
  },
  data() {
    return {
      isPlaying: false,
      loading: false,
      audioUrl: null,
      API_BASE_URL: 'http://localhost:8000'  // 또는 실제 백엔드 URL
    }
  },
  computed: {
    buttonText() {
      if (this.loading) return '변환 중...'
      return this.isPlaying ? '정지' : '뉴스 읽기'
    }
  },
  methods: {
    async togglePlay() {
      if (this.isPlaying) {
        this.stopAudio()
      } else {
        await this.playAudio()
      }
    },
    async playAudio() {
      try {
        this.loading = true
        console.log('TTS 요청 시작:', this.newsId)
        
        // 음성 파일이 없는 경우에만 새로 요청
        if (!this.audioUrl) {
          const response = await axios.post(
            `${this.API_BASE_URL}/api/news/${this.newsId}/tts/`,
            {},
            { 
              responseType: 'blob',
              headers: {
                'Content-Type': 'application/json',
              }
            }
          )
          console.log('TTS 응답 받음')
          this.audioUrl = URL.createObjectURL(response.data)
        }
        
        const player = this.$refs.audioPlayer
        player.src = this.audioUrl
        await player.play()
        this.isPlaying = true
        console.log('오디오 재생 시작')
      } catch (error) {
        console.error('음성 재생 실패:', error.response || error)
        alert('음성 변환에 실패했습니다. 잠시 후 다시 시도해주세요.')
      } finally {
        this.loading = false
      }
    },
    stopAudio() {
      const player = this.$refs.audioPlayer
      player.pause()
      player.currentTime = 0
      this.isPlaying = false
      console.log('오디오 정지')
    },
    handleEnded() {
      this.isPlaying = false
      console.log('오디오 재생 완료')
    }
  },
  beforeDestroy() {
    if (this.audioUrl) {
      URL.revokeObjectURL(this.audioUrl)
    }
    this.stopAudio()
  }
}
</script>

<style scoped>
.tts-controls {
  margin: 1rem 0;
}

.tts-button {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.tts-button:hover {
  background-color: #45a049;
}

.tts-button.is-playing {
  background-color: #f44336;
}

.tts-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.button-icon {
  margin-right: 8px;
  font-size: 16px;
}
</style>