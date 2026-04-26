<!-- 三格知识卡 -->
<template>
  <view class="cards">
    <view v-for="(key, idx) in config.factsKeys" :key="key" class="card">
      <view class="icon">{{ config.factsIcons[idx] }}</view>
      <view class="label">{{ key }}</view>
      <view class="value">{{ facts[key] ?? '—' }}</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { getCategoryConfig, type Category } from '@/utils/category'

const props = defineProps<{
  category: Category
  facts: Record<string, string>
}>()

const config = computed(() => getCategoryConfig(props.category))
</script>

<style scoped lang="scss">
.cards {
  display: flex;
  gap: 12rpx;
  padding: 14rpx 32rpx 0;
}

.card {
  flex: 1;
  background: #fff;
  border-radius: 24rpx;
  padding: 14rpx 10rpx;
  text-align: center;
  box-shadow: 0 6rpx 16rpx var(--surface-shadow);
}

.icon {
  font-size: 42rpx;
}

.label {
  margin-top: 2rpx;
  font-size: 24rpx;
  font-weight: 900;
  color: var(--text-main);
}

.value {
  margin-top: 2rpx;
  font-size: 20rpx;
  color: var(--text-sub);
}
</style>
