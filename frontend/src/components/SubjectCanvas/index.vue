<!-- 图像画布 + 标注点 -->
<template>
  <view class="canvas-wrap">
    <canvas
      class="subject-canvas"
      :canvas-id="canvasId"
      :id="canvasId"
      :style="{ width: `${canvasWidthRpx}rpx`, height: `${canvasHeightRpx}rpx` }"
    />

    <view
      v-for="(part, idx) in parts"
      :key="part.id"
      class="marker"
      :style="markerStyle(part, idx)"
      @tap="emit('select', part)"
    >
      <view class="marker-text">{{ part.shortName }}</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { getCurrentInstance, onMounted, watch } from 'vue'

import type { SubjectPart } from '@/store/explorerStore'

const MARKER_COLORS = ['#FFB347', '#4FC3F7', '#66BB6A', '#F06292']

const props = defineProps<{
  imageUrl: string
  parts: SubjectPart[]
}>()

const emit = defineEmits<{
  (event: 'select', part: SubjectPart): void
}>()

const instance = getCurrentInstance()
const canvasId = `subject-canvas-${instance?.uid ?? 'default'}`

const canvasWidthRpx = 686
const canvasHeightRpx = 456
const canvasWidthPx = uni.upx2px(canvasWidthRpx)
const canvasHeightPx = uni.upx2px(canvasHeightRpx)

function markerStyle(part: SubjectPart, idx: number) {
  return {
    left: `${part.x * 100}%`,
    top: `${part.y * 100}%`,
    '--marker-color': MARKER_COLORS[idx % MARKER_COLORS.length],
  }
}

function drawPlaceholder(ctx: UniApp.CanvasContext) {
  ctx.setFillStyle('#F8E8C8')
  ctx.fillRect(0, 0, canvasWidthPx, canvasHeightPx)
  ctx.setFontSize(16)
  ctx.setFillStyle('#A07840')
  ctx.fillText('图像加载中...', canvasWidthPx / 2 - 40, canvasHeightPx / 2)
  ctx.draw()
}

function drawImage() {
  const ctx = uni.createCanvasContext(canvasId, instance)

  if (!props.imageUrl) {
    drawPlaceholder(ctx)
    return
  }

  uni.getImageInfo({
    src: props.imageUrl,
    success: (res) => {
      ctx.clearRect(0, 0, canvasWidthPx, canvasHeightPx)

      const imgW = res.width
      const imgH = res.height
      const scale = Math.min(canvasWidthPx / imgW, canvasHeightPx / imgH)
      const drawW = imgW * scale
      const drawH = imgH * scale
      const offsetX = (canvasWidthPx - drawW) / 2
      const offsetY = (canvasHeightPx - drawH) / 2

      ctx.setFillStyle('#ffffff')
      ctx.fillRect(0, 0, canvasWidthPx, canvasHeightPx)
      ctx.drawImage(res.path, offsetX, offsetY, drawW, drawH)
      ctx.draw()
    },
    fail: () => {
      drawPlaceholder(ctx)
    },
  })
}

watch(
  () => props.imageUrl,
  () => {
    drawImage()
  },
)

onMounted(() => {
  drawImage()
})
</script>

<style scoped lang="scss">
.canvas-wrap {
  margin: 0 32rpx 16rpx;
  height: 456rpx;
  border-radius: 44rpx;
  overflow: hidden;
  position: relative;
  background: #ffffff;
  box-shadow: 0 12rpx 28rpx var(--surface-shadow);
}

.subject-canvas {
  width: 100%;
  height: 100%;
}

.marker {
  position: absolute;
  width: 80rpx;
  height: 80rpx;
  margin-left: -40rpx;
  margin-top: -40rpx;
  border-radius: 50%;
  background: var(--marker-color);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: markerPulse 1.5s ease-in-out infinite;
  box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.5);
}

.marker-text {
  color: #ffffff;
  font-size: 24rpx;
  font-weight: 900;
}

@keyframes markerPulse {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.6);
  }
  50% {
    transform: scale(1.12);
    box-shadow: 0 0 0 16rpx rgba(255, 255, 255, 0);
  }
}
</style>
