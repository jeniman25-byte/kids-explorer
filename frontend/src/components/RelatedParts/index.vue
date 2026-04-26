<!-- 相关部位横滑 -->
<template>
  <scroll-view scroll-x class="related-scroll" show-scrollbar="false">
    <view
      v-for="part in parts"
      :key="part.id"
      class="item"
      :class="{ 'item--active': currentPartId === part.id }"
      @tap="emit('select', part.id)"
    >
      <view class="emoji">{{ part.shortName }}</view>
      <view class="name">{{ part.name }}</view>
      <view class="sub">点击切换</view>
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import type { SubjectPart } from '@/store/explorerStore'

defineProps<{
  parts: SubjectPart[]
  currentPartId: string | null
}>()

const emit = defineEmits<{
  (event: 'select', partId: string): void
}>()
</script>

<style scoped lang="scss">
.related-scroll {
  padding: 14rpx 32rpx 0;
  white-space: nowrap;
}

.item {
  width: 172rpx;
  height: 164rpx;
  margin-right: 12rpx;
  border-radius: 24rpx;
  background: #fff;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6rpx 16rpx var(--surface-shadow);
}

.item--active {
  border: 3rpx solid var(--light);
}

.emoji {
  font-size: 42rpx;
  font-weight: 900;
  color: var(--text-main);
}

.name {
  margin-top: 4rpx;
  font-size: 22rpx;
  font-weight: 800;
  color: var(--text-main);
}

.sub {
  margin-top: 2rpx;
  font-size: 18rpx;
  color: var(--text-sub);
}
</style>
