<!-- 部位标签网格 -->
<template>
  <view class="grid">
    <view
      v-for="part in parts"
      :key="part.id"
      class="chip"
      :class="{ 'chip--active': selectedPartId === part.id }"
      @tap="handleSelect(part)"
    >
      <view class="dot" :style="{ background: part.color }" />
      <view class="name">{{ part.name }}</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import type { SubjectPart } from '@/store/explorerStore'
import { vibrateShort } from '@/utils/feedback'

defineProps<{
  parts: SubjectPart[]
  selectedPartId?: string | null
}>()

const emit = defineEmits<{
  (event: 'select', part: SubjectPart): void
}>()

function handleSelect(part: SubjectPart) {
  vibrateShort()
  emit('select', part)
}
</script>

<style scoped lang="scss">
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12rpx;
  padding: 0 32rpx;
}

.chip {
  background: #fff;
  border-radius: 22rpx;
  padding: 18rpx 20rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  box-shadow: 0 6rpx 16rpx var(--surface-shadow);
}

.chip--active {
  border: 3rpx solid var(--light);
}

.dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
}

.name {
  color: var(--text-main);
  font-size: 25rpx;
  font-weight: 800;
}
</style>
