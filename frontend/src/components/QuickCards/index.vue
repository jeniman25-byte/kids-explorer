<!-- 推荐三格卡 -->
<template>
  <view class="quick-row">
    <view v-for="item in cards" :key="item.name" class="quick-card">
      <view class="quick-emoji">{{ item.emoji }}</view>
      <view class="quick-name">{{ item.name }}</view>
      <view class="quick-desc">{{ item.desc }}</view>
    </view>
  </view>
</template>

<script setup lang="ts">
interface QuickCardItem {
  emoji: string
  name: string
  desc: string
}

defineProps<{
  cards: ReadonlyArray<QuickCardItem>
}>()
</script>

<style scoped lang="scss">
.quick-row {
  display: flex;
  gap: 20rpx;
  padding: 0 32rpx 20rpx;
}

.quick-card {
  flex: 1;
  height: 148rpx;
  border-radius: 36rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  background: var(--surface);
  box-shadow: 0 8rpx 24rpx var(--surface-shadow);
}

.quick-emoji {
  font-size: 46rpx;
  line-height: 1;
}

.quick-name {
  font-size: 24rpx;
  font-weight: 800;
  color: var(--text-main);
}

.quick-desc {
  font-size: 20rpx;
  color: var(--text-sub);
}
</style>
