<!-- 底部引导框 -->
<template>
  <view class="guide-box" :style="boxStyle">
    <view class="guide-icon">{{ icon }}</view>
    <view class="guide-title">{{ title }}</view>
    <view class="guide-text">{{ text }}</view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  icon: string
  title: string
  text: string
  light: string
  primary: string
}>()

const boxStyle = computed(() => ({
  backgroundImage: `linear-gradient(135deg,${props.light},${props.primary})`,
}))
</script>

<style scoped lang="scss">
.guide-box {
  margin: 24rpx 32rpx 0;
  border-radius: 40rpx;
  padding: 28rpx 32rpx;
  text-align: center;
}

.guide-icon {
  font-size: 48rpx;
  line-height: 1;
  margin-bottom: 8rpx;
}

.guide-title {
  font-size: 30rpx;
  font-weight: 900;
  color: var(--text-main);
}

.guide-text {
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.6;
  color: var(--text-sub);
  white-space: pre-line;
}
</style>
