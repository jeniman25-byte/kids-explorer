<!-- 部位特写弹出层 -->
<template>
  <view v-if="visible" class="overlay" @tap="handleClose">
    <view class="sheet" @tap.stop @touchstart="handleTouchStart" @touchend="handleTouchEnd">
      <view class="handle" />
      <view class="title">{{ part?.name ?? '部位详情' }}</view>
      <view class="karaoke" v-if="karaokeWords.length > 0">
        <text
          v-for="(word, idx) in karaokeWords"
          :key="`${word}-${idx}`"
          class="karaoke-word"
          :class="{ hi: idx === activeWordIndex }"
        >
          {{ word }}
        </text>
      </view>
      <view class="desc">{{ part?.description ?? '' }}</view>

      <view class="facts" v-if="part">
        <view v-for="(value, key) in part.facts" :key="key" class="fact-row">
          <text class="fact-key">{{ key }}</text>
          <text class="fact-val">{{ value }}</text>
        </view>
      </view>

      <view class="audio-label">🔊 语音讲解（M6）</view>
      <view class="audio-bar">
        <view class="audio-progress" :style="audioProgressStyle" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'

import type { SubjectPart } from '@/store/explorerStore'
import { vibrateShort } from '@/utils/feedback'
import { getTtsAudioBase64 } from '@/utils/tts'

const props = defineProps<{
  visible: boolean
  part: SubjectPart | null
  primary: string
}>()

const emit = defineEmits<{
  (event: 'close'): void
}>()

const touchStartY = ref(0)
const audioProgress = ref(0)
const activeWordIndex = ref(-1)
const karaokeWords = ref<string[]>([])

let playTicket = 0
let audioContext: UniApp.InnerAudioContext | null = null
let audioDuration = 0

const audioProgressStyle = computed(() => ({
  width: `${Math.round(audioProgress.value * 100)}%`,
  background: props.primary,
}))

function ensureAudioContext(): UniApp.InnerAudioContext {
  if (audioContext) {
    return audioContext
  }

  const ctx = uni.createInnerAudioContext()
  ctx.autoplay = false
  ctx.obeyMuteSwitch = false

  ctx.onTimeUpdate(() => {
    const duration = ctx.duration || audioDuration
    const current = ctx.currentTime || 0
    audioDuration = duration
    if (duration > 0) {
      audioProgress.value = Math.min(1, current / duration)
    } else {
      audioProgress.value = 0
    }
    syncKaraokeIndex(current, duration)
  })

  ctx.onEnded(() => {
    audioProgress.value = 1
    activeWordIndex.value = -1
  })

  ctx.onStop(() => {
    activeWordIndex.value = -1
  })

  ctx.onError(() => {
    activeWordIndex.value = -1
    uni.showToast({
      title: '语音播放失败，请稍后重试',
      icon: 'none',
    })
  })

  audioContext = ctx
  return ctx
}

function tokenizeForKaraoke(text: string): string[] {
  const normalized = text
    .replace(/[，。！？；：,.!?;:()\n\r]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  if (!normalized) {
    return []
  }

  const bySpace = normalized.split(' ').filter(Boolean)
  if (bySpace.length > 1) {
    return bySpace
  }
  return normalized.split('').filter((item) => item.trim().length > 0)
}

function syncKaraokeIndex(currentTime: number, duration: number) {
  const totalWords = karaokeWords.value.length
  if (totalWords === 0 || duration <= 0) {
    activeWordIndex.value = -1
    return
  }

  const unit = duration / totalWords
  if (unit <= 0) {
    activeWordIndex.value = -1
    return
  }

  const idx = Math.floor(currentTime / unit)
  activeWordIndex.value = idx >= totalWords ? -1 : idx
}

function stopAudio(resetProgress = true) {
  playTicket += 1
  if (audioContext) {
    audioContext.stop()
  }
  activeWordIndex.value = -1
  if (resetProgress) {
    audioProgress.value = 0
  }
}

async function playPartTts() {
  const text = (props.part?.description ?? '').trim()
  karaokeWords.value = tokenizeForKaraoke(text)
  audioProgress.value = 0
  activeWordIndex.value = -1
  audioDuration = 0

  if (!props.visible || !text) {
    stopAudio()
    return
  }

  const currentTicket = ++playTicket
  const ctx = ensureAudioContext()

  try {
    const audioBase64 = await getTtsAudioBase64(text)
    if (currentTicket !== playTicket || !props.visible) {
      return
    }

    ctx.src = audioBase64
    ctx.play()
  } catch (error) {
    console.error('[tts] part detail request failed:', error)
    if (currentTicket === playTicket) {
      uni.showToast({
        title: '语音生成失败，请稍后重试',
        icon: 'none',
      })
    }
  }
}

function handleTouchStart(event: any) {
  touchStartY.value = event.changedTouches?.[0]?.clientY ?? 0
}

function handleTouchEnd(event: any) {
  const endY = event.changedTouches?.[0]?.clientY ?? 0
  const delta = endY - touchStartY.value
  if (delta < -80) {
    handleClose()
  }
}

function handleClose() {
  vibrateShort()
  emit('close')
}

watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      void playPartTts()
      return
    }
    stopAudio()
  },
)

watch(
  () => props.part?.id,
  () => {
    if (!props.visible) {
      return
    }
    void playPartTts()
  },
)

onBeforeUnmount(() => {
  stopAudio()
  if (audioContext) {
    audioContext.destroy()
    audioContext = null
  }
})
</script>

<style scoped lang="scss">
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 30;
  display: flex;
  align-items: flex-end;
}

.sheet {
  width: 100%;
  background: #fff;
  border-radius: 34rpx 34rpx 0 0;
  padding: 18rpx 28rpx 30rpx;
}

.handle {
  width: 88rpx;
  height: 8rpx;
  border-radius: 999rpx;
  background: #e0e0e0;
  margin: 0 auto 14rpx;
}

.title {
  font-size: 34rpx;
  color: var(--text-main);
  font-weight: 900;
}

.desc {
  margin-top: 10rpx;
  color: #5a4020;
  font-size: 25rpx;
  line-height: 1.7;
}

.karaoke {
  margin-top: 8rpx;
  line-height: 1.8;
}

.karaoke-word {
  display: inline-block;
  margin-right: 8rpx;
  margin-bottom: 6rpx;
  color: #7a5b34;
  font-size: 24rpx;
  padding: 2rpx 8rpx;
  border-radius: 12rpx;
  transition: all 0.16s ease;
}

.karaoke-word.hi {
  color: #fff;
  background: var(--text-main);
  font-weight: 900;
}

.facts {
  margin-top: 12rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.fact-row {
  display: flex;
  gap: 12rpx;
  font-size: 22rpx;
}

.fact-key {
  color: var(--text-main);
  font-weight: 900;
  min-width: 72rpx;
}

.fact-val {
  color: var(--text-sub);
  flex: 1;
}

.audio-label {
  margin-top: 14rpx;
  font-size: 22rpx;
  color: var(--text-sub);
}

.audio-bar {
  margin-top: 10rpx;
  height: 12rpx;
  border-radius: 999rpx;
  background: #f5edd8;
  overflow: hidden;
}

.audio-progress {
  width: 0;
  height: 100%;
  border-radius: 999rpx;
}
</style>
