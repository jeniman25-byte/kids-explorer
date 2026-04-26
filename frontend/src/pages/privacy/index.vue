<!-- 隐私政策页 -->
<template>
  <view class="page">
    <view class="topbar">
      <view class="back" @tap="goBack">←</view>
      <view class="title">隐私政策</view>
    </view>

    <view class="card">
      <view class="h1">小探索家隐私声明</view>
      <view class="p">我们非常重视儿童隐私与数据安全。</view>
      <view class="p">本应用不会收集儿童姓名、联系方式、家庭住址、学校等个人敏感信息。</view>
      <view class="p">语音、图片等数据仅用于当次探索功能处理，不做广告画像用途。</view>
      <view class="p">如有隐私相关问题，可通过应用内反馈联系我们。</view>
      <view class="time">更新日期：2026-04-26</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { vibrateShort } from '@/utils/feedback'

function goBack() {
  vibrateShort()
  uni.navigateBack({
    fail: () => {
      uni.switchTab({
        url: '/pages/index/index',
      })
    },
  })
}
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #fffbf0;
  padding: 12rpx 0;
}

.topbar {
  display: flex;
  align-items: center;
  padding: 12rpx 24rpx;
  gap: 12rpx;
}

.back {
  width: 62rpx;
  height: 62rpx;
  border-radius: 14rpx;
  background: #f5e9ca;
  color: #7d5f35;
  font-size: 36rpx;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title {
  font-size: 34rpx;
  color: var(--text-main);
  font-weight: 900;
}

.card {
  margin: 10rpx 24rpx 0;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 8rpx 20rpx var(--surface-shadow);
  padding: 22rpx 20rpx;
}

.h1 {
  font-size: 30rpx;
  color: var(--text-main);
  font-weight: 900;
}

.p {
  margin-top: 12rpx;
  font-size: 24rpx;
  line-height: 1.7;
  color: #5a4020;
}

.time {
  margin-top: 20rpx;
  font-size: 20rpx;
  color: var(--text-sub);
}
</style>
