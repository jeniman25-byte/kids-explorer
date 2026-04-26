<!-- 图鉴搜索框 -->
<template>
  <view class="search-wrap">
    <text class="icon">🔎</text>
    <input
      class="search-input"
      type="text"
      :value="modelValue"
      :placeholder="placeholder"
      confirm-type="search"
      @input="handleInput"
      @confirm="handleConfirm"
    />
    <view v-if="modelValue" class="clear-btn" @tap="clearKeyword">清空</view>
  </view>
</template>

<script setup lang="ts">
import { vibrateShort } from '@/utils/feedback'

const props = withDefaults(
  defineProps<{
    modelValue: string
    placeholder?: string
  }>(),
  {
    placeholder: '搜索你想探索的对象',
  },
)

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
}>()

function handleInput(event: any) {
  emit('update:modelValue', event.detail?.value ?? '')
}

function handleConfirm() {
  vibrateShort()
}

function clearKeyword() {
  vibrateShort()
  emit('update:modelValue', '')
}

void props
</script>

<style scoped lang="scss">
.search-wrap {
  margin: 12rpx 32rpx 0;
  height: 76rpx;
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 6rpx 16rpx var(--surface-shadow);
  display: flex;
  align-items: center;
  padding: 0 16rpx;
  gap: 10rpx;
}

.icon {
  font-size: 28rpx;
}

.search-input {
  flex: 1;
  height: 100%;
  font-size: 24rpx;
  color: var(--text-main);
}

.clear-btn {
  min-width: 68rpx;
  padding: 0 10rpx;
  height: 46rpx;
  border-radius: 999rpx;
  background: #f7efdd;
  font-size: 20rpx;
  color: #8a6a42;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
