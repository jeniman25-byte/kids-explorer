<!-- 八方罗盘组件 -->
<template>
  <view>
    <view class="hero" :style="{ background: `linear-gradient(135deg,${light},${primary})` }">
      <image v-if="currentImage?.url" class="hero-image" :src="currentImage.url" mode="aspectFit" />
      <view v-else class="hero-emoji">{{ emoji }}</view>
      <view class="view-label">🔭 {{ currentImage?.label ?? '当前' }}视角</view>
      <view class="badge">{{ currentIndex + 1 }} / 8</view>
    </view>

    <view class="compass-wrap">
      <view class="dial">
        <view class="dial-center">{{ emoji }}</view>
        <view
          v-for="(item, idx) in images"
          :key="`btn-${item.view}`"
          class="cbt"
          :class="[positionClass(idx), { active: item.view === currentView }]"
          :style="{ background: markerColors[idx % markerColors.length] }"
          @tap="handleSwitch(item.view)"
        >
          <view class="cic">{{ emoji }}</view>
          <view class="clb">{{ shortLabel(item.label) }}</view>
        </view>
      </view>
      <view class="legend">
        <view class="leg-row">
          <view class="leg-dot" :style="{ background: markerColors[0] }" />
          <view class="leg-txt">正面</view>
        </view>
        <view class="leg-row">
          <view class="leg-dot" :style="{ background: markerColors[2] }" />
          <view class="leg-txt">右面</view>
        </view>
        <view class="leg-row">
          <view class="leg-dot" :style="{ background: markerColors[4] }" />
          <view class="leg-txt">背面</view>
        </view>
        <view class="leg-row">
          <view class="leg-dot" :style="{ background: markerColors[6] }" />
          <view class="leg-txt">左面</view>
        </view>
        <view class="leg-row">
          <view class="leg-dot" :style="{ background: markerColors[1] }" />
          <view class="leg-txt">斜角 x4</view>
        </view>
      </view>
    </view>

    <view class="sec">🗂️ 八方全览 · 左右滑动</view>
    <scroll-view class="thumbs8" scroll-x show-scrollbar="false">
      <view
        v-for="(item, idx) in images"
        :key="`thumb-${item.view}`"
        class="thumb8"
        :class="{ sel: item.view === currentView }"
        :style="{ background: item.view === currentView ? markerColors[idx % markerColors.length] : '#fff' }"
        @tap="handleSwitch(item.view)"
      >
        <image v-if="item.url" class="thumb-image" :src="item.url" mode="aspectFill" />
        <view v-else class="t8e">{{ emoji }}</view>
        <view class="t8n">{{ item.label }}</view>
      </view>
    </scroll-view>

    <view class="desc-box">
      <view class="desc-ttl">🔭 当前视角 · 你知道吗？</view>
      <view class="desc-txt">{{ viewDescription }}</view>
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
  viewDescription: string
}>()

const emit = defineEmits<{
  (event: 'change', view: string): void
}>()

const ORDER = ['front', 'front_right', 'right', 'back_right', 'back', 'back_left', 'left', 'front_left']
const markerColors = ['#FF8A65', '#FFA726', '#66BB6A', '#26C6DA', '#5C6BC0', '#EC407A', '#AB47BC', '#8D6E63']

const currentImage = computed(() => props.images.find((item) => item.view === props.currentView))
const currentIndex = computed(() => {
  const idx = ORDER.indexOf(props.currentView)
  return idx < 0 ? 0 : idx
})

function shortLabel(label: string) {
  return label.length > 2 ? label.slice(0, 2) : label
}

function positionClass(idx: number) {
  const classes = ['cN', 'cNE', 'cE', 'cSE', 'cS', 'cSW', 'cW', 'cNW']
  return classes[idx] ?? 'cN'
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
  height: 320rpx;
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
  font-size: 128rpx;
}

.view-label {
  position: absolute;
  bottom: 12rpx;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(106, 27, 154, 0.75);
  color: #fff;
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
  color: #ab47bc;
}

.compass-wrap {
  margin: 0 16rpx 8rpx;
  position: relative;
  height: 260rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.legend {
  position: absolute;
  right: 8rpx;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.leg-row {
  display: flex;
  align-items: center;
  gap: 4rpx;
}

.leg-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
}

.leg-txt {
  font-size: 18rpx;
  color: #5a4020;
  font-weight: 700;
}

.dial {
  width: 236rpx;
  height: 236rpx;
  border-radius: 50%;
  background: radial-gradient(circle, #fff3cc 30%, #ffe08a 100%);
  position: relative;
  box-shadow: 0 4rpx 16rpx rgba(255, 179, 71, 0.3);
}

.dial-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 56rpx;
  z-index: 10;
}

.cbt {
  position: absolute;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 20;
}

.cbt.active {
  box-shadow: 0 0 0 3rpx #fff, 0 0 0 5rpx #ffb347;
}

.cic {
  font-size: 18rpx;
  line-height: 1;
}

.clb {
  font-size: 9rpx;
  margin-top: 1rpx;
  color: #fff;
  font-weight: 900;
}

.cN {
  top: -23rpx;
  left: 50%;
  transform: translateX(-50%);
}

.cNE {
  top: -7rpx;
  right: -20rpx;
}

.cE {
  top: 50%;
  right: -24rpx;
  transform: translateY(-50%);
}

.cSE {
  bottom: -7rpx;
  right: -20rpx;
}

.cS {
  bottom: -23rpx;
  left: 50%;
  transform: translateX(-50%);
}

.cSW {
  bottom: -7rpx;
  left: -20rpx;
}

.cW {
  top: 50%;
  left: -24rpx;
  transform: translateY(-50%);
}

.cNW {
  top: -7rpx;
  left: -20rpx;
}

.sec {
  padding: 6rpx 18rpx 5rpx;
  font-size: 24rpx;
  font-weight: 900;
  color: #3d2c00;
}

.thumbs8 {
  display: flex;
  gap: 8rpx;
  padding: 0 16rpx;
  white-space: nowrap;
}

.thumb8 {
  display: inline-flex;
  flex-shrink: 0;
  width: 90rpx;
  height: 110rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #fff;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rpx;
}

.thumb8.sel {
  box-shadow: 0 0 0 3rpx #ab47bc;
}

.thumb-image {
  width: 100%;
  height: 70rpx;
}

.t8e {
  font-size: 22rpx;
}

.t8n {
  font-size: 18rpx;
  font-weight: 900;
  color: #3d2c00;
}

.desc-box {
  margin: 10rpx 16rpx 0;
  background: #fff;
  border-radius: 18rpx;
  padding: 12rpx 14rpx;
  box-shadow: 0 3rpx 10rpx rgba(0, 0, 0, 0.07);
}

.desc-ttl {
  font-size: 24rpx;
  font-weight: 900;
  color: #3d2c00;
  margin-bottom: 3rpx;
}

.desc-txt {
  font-size: 22rpx;
  color: #7a5c30;
  line-height: 1.6;
}
</style>
