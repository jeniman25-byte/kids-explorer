<!-- 图鉴过滤标签 -->
<template>
  <scroll-view class="filter-row" scroll-x show-scrollbar="false">
    <view
      v-for="tag in tags"
      :key="tag"
      class="chip"
      :class="{ 'chip--active': tag === activeTag }"
      :style="tag === activeTag ? { background: primary, color: '#fff' } : undefined"
      @tap="handleChange(tag)"
    >
      {{ tag }}
    </view>
  </scroll-view>
</template>

<script setup lang="ts">
import { vibrateShort } from '@/utils/feedback'

defineProps<{
  tags: ReadonlyArray<string>
  activeTag: string
  primary: string
}>()

const emit = defineEmits<{
  (event: 'change', tag: string): void
}>()

function handleChange(tag: string) {
  vibrateShort()
  emit('change', tag)
}
</script>

<style scoped lang="scss">
.filter-row {
  margin-top: 10rpx;
  white-space: nowrap;
  padding: 0 32rpx;
}

.chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 12rpx;
  min-width: 88rpx;
  padding: 0 18rpx;
  height: 60rpx;
  border-radius: 999rpx;
  background: #f5edd8;
  color: #9b7a51;
  font-size: 22rpx;
  font-weight: 800;
}

.chip--active {
  box-shadow: 0 6rpx 14rpx rgba(0, 0, 0, 0.12);
}
</style>
