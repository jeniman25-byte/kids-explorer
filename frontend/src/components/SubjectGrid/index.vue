<!-- 图鉴 2x2 卡片网格 -->
<template>
  <view class="grid-list">
    <view
      v-for="(item, idx) in items"
      :key="item.id"
      class="list-card"
      :style="cardStyle(idx)"
      @tap="handleSelect(item)"
    >
      <view class="lc1">{{ item.emoji }}</view>
      <view class="lc2">{{ item.name }}</view>
      <view class="lc3">{{ item.partsPreviewText || '点击开始探索更多部位' }}</view>
      <view class="lc4" :style="badgeStyle(item)">{{ item.explored ? '已探索' : '开始探索' }}</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { vibrateShort } from '@/utils/feedback'

export interface SubjectGridItem {
  id: number
  name: string
  emoji: string
  explored: boolean
  partsPreviewText: string
}

const props = defineProps<{
  items: SubjectGridItem[]
  light: string
  primary: string
}>()

const emit = defineEmits<{
  (event: 'select', item: SubjectGridItem): void
}>()

function cardStyle(index: number) {
  const opacity = index % 2 === 0 ? 0.24 : 0.38
  const soft = `rgba(255,255,255,${opacity})`
  return {
    background: `linear-gradient(135deg,${props.light},${soft})`,
  }
}

function badgeStyle(item: SubjectGridItem) {
  return {
    background: item.explored ? props.primary : 'rgba(255,255,255,0.8)',
    color: item.explored ? '#fff' : '#7d5f35',
  }
}

function handleSelect(item: SubjectGridItem) {
  vibrateShort()
  emit('select', item)
}
</script>

<style scoped lang="scss">
.grid-list {
  margin-top: 12rpx;
  padding: 0 32rpx 24rpx;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12rpx;
}

.list-card {
  min-height: 220rpx;
  border-radius: 24rpx;
  padding: 16rpx 14rpx;
  box-shadow: 0 8rpx 16rpx var(--surface-shadow);
}

.lc1 {
  font-size: 56rpx;
  line-height: 1;
}

.lc2 {
  margin-top: 8rpx;
  font-size: 28rpx;
  color: var(--text-main);
  font-weight: 900;
}

.lc3 {
  margin-top: 6rpx;
  min-height: 64rpx;
  font-size: 20rpx;
  line-height: 1.5;
  color: #7a5c30;
}

.lc4 {
  display: inline-flex;
  margin-top: 8rpx;
  padding: 4rpx 12rpx;
  border-radius: 999rpx;
  font-size: 20rpx;
  font-weight: 900;
}
</style>
