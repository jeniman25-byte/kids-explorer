<!-- 部位特写弹出层 -->
<template>
  <view v-if="visible" class="overlay" @tap="emit('close')">
    <view class="sheet" @tap.stop @touchstart="handleTouchStart" @touchend="handleTouchEnd">
      <view class="handle" />
      <view class="title">{{ part?.name ?? '部位详情' }}</view>
      <view class="desc">{{ part?.description ?? '' }}</view>

      <view class="facts" v-if="part">
        <view v-for="(value, key) in part.facts" :key="key" class="fact-row">
          <text class="fact-key">{{ key }}</text>
          <text class="fact-val">{{ value }}</text>
        </view>
      </view>

      <view class="audio-label">🔊 语音讲解（M6）</view>
      <view class="audio-bar">
        <view class="audio-progress" :style="{ background: primary }" />
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import type { SubjectPart } from '@/store/explorerStore'

defineProps<{
  visible: boolean
  part: SubjectPart | null
  primary: string
}>()

const emit = defineEmits<{
  (event: 'close'): void
}>()

const touchStartY = ref(0)

function handleTouchStart(event: any) {
  touchStartY.value = event.changedTouches?.[0]?.clientY ?? 0
}

function handleTouchEnd(event: any) {
  const endY = event.changedTouches?.[0]?.clientY ?? 0
  const delta = endY - touchStartY.value
  if (delta < -80) {
    emit('close')
  }
}
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
  width: 38%;
  height: 100%;
  border-radius: 999rpx;
}
</style>
