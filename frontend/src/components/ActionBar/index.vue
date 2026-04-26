<!-- 底部操作栏 -->
<template>
  <view class="bar">
    <view class="btn btn-primary" :style="primaryStyle" @tap="handleTap('intro')">🔊 介绍</view>
    <view class="btn btn-secondary" @tap="handleTap('retry')">🔄 再来</view>
    <view class="btn btn-third" @tap="handleTap('multiview')">🔮 多角度</view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { vibrateShort } from '@/utils/feedback'

const props = defineProps<{
  primary: string
}>()

const emit = defineEmits<{
  (event: 'intro'): void
  (event: 'retry'): void
  (event: 'multiview'): void
}>()

function handleTap(event: 'intro' | 'retry' | 'multiview') {
  vibrateShort()
  emit(event)
}

function mixWithWhite(hex: string, ratio: number): string {
  const raw = hex.replace('#', '').trim()
  if (!/^[\da-fA-F]{6}$/.test(raw)) {
    return hex
  }

  const r = parseInt(raw.slice(0, 2), 16)
  const g = parseInt(raw.slice(2, 4), 16)
  const b = parseInt(raw.slice(4, 6), 16)

  const nextR = Math.round(r + (255 - r) * ratio)
  const nextG = Math.round(g + (255 - g) * ratio)
  const nextB = Math.round(b + (255 - b) * ratio)
  return `rgb(${nextR},${nextG},${nextB})`
}

const primaryStyle = computed(() => ({
  '--btn-primary': props.primary,
  '--btn-primary-soft': mixWithWhite(props.primary, 0.35),
}))
</script>

<style scoped lang="scss">
.bar {
  display: flex;
  gap: 12rpx;
  padding: 14rpx 32rpx 0;
}

.btn {
  flex: 1;
  height: 88rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 900;
}

.btn-primary {
  color: #fff;
  background: linear-gradient(135deg, var(--btn-primary-soft), var(--btn-primary));
}

.btn-secondary {
  color: #fff;
  background: linear-gradient(135deg, #81d4fa, #4fc3f7);
}

.btn-third {
  color: #fff;
  background: linear-gradient(135deg, #ce93d8, #ab47bc);
}
</style>
