<!-- 四面图组件 -->
<template>
  <view>
    <view class="hero" :style="{ background: `linear-gradient(135deg,${light},${primary})` }">
      <image v-if="currentImage?.url" class="hero-image" :src="currentImage.url" mode="aspectFit" />
      <view v-else class="hero-emoji">{{ emoji }}</view>
      <view class="view-label">📷 {{ currentImage?.label ?? '正面' }}视角</view>
      <view class="badge">{{ currentIndex + 1 }} / 4</view>
    </view>

    <view class="grid4">
      <view
        v-for="item in images"
        :key="item.view"
        class="dir"
        :class="{ sel: item.view === currentView }"
        :style="{ background: item.view === currentView ? `linear-gradient(135deg,${light},${primary})` : '#fff' }"
        @tap="handleSwitch(item.view)"
      >
        <view class="dir-e">{{ directionEmoji(item.view) }}</view>
        <view class="dir-n">{{ item.label }}</view>
        <view class="dir-s">{{ item.view }}</view>
      </view>
    </view>

    <view class="sec">✨ 四面总览</view>
    <view class="thumbs4">
      <view
        v-for="item in images"
        :key="`thumb-${item.view}`"
        class="thumb4"
        :class="{ sel: item.view === currentView }"
        @tap="handleSwitch(item.view)"
      >
        <image v-if="item.url" class="thumb-image" :src="item.url" mode="aspectFill" />
        <view v-else class="t4e">{{ emoji }}</view>
        <view class="t4n">{{ item.label }}</view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { ViewImage } from '@/store/explorerStore'
import { vibrateShort } from '@/utils/feedback'

const props = defineProps<{
  images: ViewImage[]
  currentView: string
  emoji: string
  light: string
  primary: string
}>()

const emit = defineEmits<{
  (event: 'change', view: string): void
}>()

const ORDER = ['front', 'back', 'left', 'right']

const currentImage = computed(() => props.images.find((item) => item.view === props.currentView))
const currentIndex = computed(() => {
  const idx = ORDER.indexOf(props.currentView)
  return idx < 0 ? 0 : idx
})

function directionEmoji(view: string) {
  if (view === 'front') return '⬆️'
  if (view === 'back') return '⬇️'
  if (view === 'left') return '⬅️'
  return '➡️'
}

function handleSwitch(view: string) {
  vibrateShort()
  emit('change', view)
}
</script>

<style scoped lang="scss">
.hero {
  margin: 0 16rpx 10rpx;
  border-radius: 24rpx;
  height: 360rpx;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.1);
}

.hero-image {
  width: 100%;
  height: 100%;
}

.hero-emoji {
  font-size: 132rpx;
}

.view-label {
  position: absolute;
  bottom: 12rpx;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(61, 44, 0, 0.75);
  color: #ffd166;
  font-size: 24rpx;
  font-weight: 900;
  padding: 4rpx 14rpx;
  border-radius: 20rpx;
}

.badge {
  position: absolute;
  top: 12rpx;
  right: 12rpx;
  background: #fff;
  border-radius: 10rpx;
  font-size: 20rpx;
  font-weight: 900;
  padding: 3rpx 9rpx;
  color: #ffb347;
}

.grid4 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8rpx;
  padding: 0 16rpx 10rpx;
}

.dir {
  height: 124rpx;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3rpx;
}

.dir.sel {
  box-shadow: 0 0 0 3rpx #ffb347, 0 4rpx 16rpx rgba(255, 179, 71, 0.35);
}

.dir-e {
  font-size: 30rpx;
}

.dir-n {
  font-size: 24rpx;
  font-weight: 900;
  color: #3d2c00;
}

.dir-s {
  font-size: 20rpx;
  color: #a07840;
}

.sec {
  padding: 6rpx 18rpx 5rpx;
  font-size: 24rpx;
  font-weight: 900;
  color: #3d2c00;
}

.thumbs4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8rpx;
  padding: 0 16rpx;
}

.thumb4 {
  height: 110rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rpx;
}

.thumb4.sel {
  box-shadow: 0 0 0 3rpx #ffb347;
}

.thumb-image {
  width: 100%;
  height: 72rpx;
}

.t4e {
  font-size: 24rpx;
}

.t4n {
  font-size: 20rpx;
  font-weight: 900;
  color: #3d2c00;
}
</style>
