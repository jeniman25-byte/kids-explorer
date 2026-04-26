<!-- 历史横滚列表 -->
<template>
  <scroll-view scroll-x class="history-scroll" show-scrollbar="false">
    <view v-for="item in items" :key="item.id" class="history-card">
      <view class="history-emoji">{{ item.emoji }}</view>
      <view class="history-name">{{ item.name }}</view>
      <view class="history-tag" :style="tagStyle(item.category)">{{ getCategoryConfig(item.category).label }}</view>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { getCategoryConfig, type Category } from '@/utils/category'

interface HistoryItem {
  id: string
  name: string
  emoji: string
  category: Category
}

defineProps<{
  items: HistoryItem[]
}>()

function tagStyle(category: Category) {
  const config = getCategoryConfig(category)
  return {
    background: config.primary,
  }
}
</script>

<style scoped lang="scss">
.history-scroll {
  white-space: nowrap;
  padding: 0 32rpx;
}

.history-card {
  width: 152rpx;
  height: 168rpx;
  margin-right: 20rpx;
  border-radius: 36rpx;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  background: var(--surface);
  box-shadow: 0 6rpx 20rpx var(--surface-shadow);
}

.history-emoji {
  font-size: 54rpx;
  line-height: 1;
}

.history-name {
  font-size: 22rpx;
  font-weight: 800;
  color: var(--text-main);
}

.history-tag {
  font-size: 18rpx;
  font-weight: 900;
  color: var(--color-white);
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}
</style>
