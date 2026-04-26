<!-- API 错误态：可爱提示 + 重试 -->
<template>
  <view class="error-wrap">
    <view class="error-emoji">😿</view>
    <view class="error-title">{{ title }}</view>
    <view class="error-desc">{{ message }}</view>
    <view class="retry-btn" @tap="handleRetry">再试一次</view>
  </view>
</template>

<script setup lang="ts">
import { vibrateShort } from '@/utils/feedback'

const props = withDefaults(
  defineProps<{
    title?: string
    message?: string
  }>(),
  {
    title: '小探索家打了个喷嚏',
    message: '网络有点慢，我们一起再试一次吧～',
  },
)

const emit = defineEmits<{
  (event: 'retry'): void
}>()

function handleRetry() {
  vibrateShort()
  emit('retry')
}

void props
</script>

<style scoped lang="scss">
.error-wrap {
  margin: 20rpx 32rpx 0;
  padding: 24rpx;
  border-radius: 28rpx;
  background: #fff;
  box-shadow: 0 8rpx 18rpx var(--surface-shadow);
  text-align: center;
}

.error-emoji {
  font-size: 56rpx;
}

.error-title {
  margin-top: 8rpx;
  font-size: 30rpx;
  color: var(--text-main);
  font-weight: 900;
}

.error-desc {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: var(--text-sub);
  line-height: 1.6;
}

.retry-btn {
  margin: 16rpx auto 0;
  width: 220rpx;
  height: 72rpx;
  border-radius: 999rpx;
  color: #fff;
  font-size: 24rpx;
  font-weight: 900;
  background: linear-gradient(135deg, #81d4fa, #4fc3f7);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
