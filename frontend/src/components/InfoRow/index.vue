<!-- 三格知识横排 -->
<template>
  <view class="row">
    <view v-for="(key, idx) in config.factsKeys" :key="key" class="item">
      <view class="icon">{{ config.factsIcons[idx] }}</view>
      <view class="label">{{ key }}</view>
      <view class="value">{{ info[key] ?? '—' }}</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { getCategoryConfig, type Category } from '@/utils/category'

const props = defineProps<{
  category: Category
  info: Record<string, string>
}>()

const config = computed(() => getCategoryConfig(props.category))
</script>

<style scoped lang="scss">
.row {
  display: flex;
  gap: 12rpx;
  padding: 14rpx 32rpx 0;
}

.item {
  flex: 1;
  background: #fff;
  border-radius: 24rpx;
  padding: 16rpx 12rpx;
  text-align: center;
  box-shadow: 0 6rpx 16rpx var(--surface-shadow);
}

.icon {
  font-size: 40rpx;
}

.label {
  margin-top: 4rpx;
  font-size: 23rpx;
  color: var(--text-main);
  font-weight: 900;
}

.value {
  margin-top: 4rpx;
  font-size: 20rpx;
  color: var(--text-sub);
}
</style>
