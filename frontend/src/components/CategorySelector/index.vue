<!-- 三分类切换卡：支持总览/分类模式 -->
<template>
  <view class="cat-row">
    <view
      v-for="item in categoryCards"
      :key="item.key"
      class="cat-card"
      :class="{ 'cat-card--active': item.key === currentCategory }"
      :style="cardStyle(item.key)"
      @tap="handleChange(item.key)"
    >
      <view v-if="item.key === currentCategory" class="cat-badge" />
      <view class="cat-emoji">{{ item.emoji }}</view>
      <view class="cat-name">{{ item.label }}</view>
      <view class="cat-count">{{ getSubText(item.key) }}</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { CATEGORY_CONFIG, type Category } from '@/utils/category'

type SelectorMode = 'overview' | 'category'

const props = withDefaults(
  defineProps<{
    currentCategory: Category
    mode?: SelectorMode
  }>(),
  {
    mode: 'overview',
  },
)

const emit = defineEmits<{
  (event: 'change', category: Category): void
}>()

const CATEGORY_ORDER: Category[] = ['food', 'animal', 'plant']

const OVERVIEW_COUNT_TEXT: Record<Category, string> = {
  food: '12 个',
  animal: '8 个',
  plant: '5 个',
}

const categoryCards = computed(() =>
  CATEGORY_ORDER.map((key) => ({
    key,
    ...CATEGORY_CONFIG[key],
  })),
)

function getSubText(category: Category): string {
  if (props.mode === 'category') {
    return category === props.currentCategory ? '当前模式' : '切换'
  }
  return OVERVIEW_COUNT_TEXT[category]
}

function cardStyle(category: Category) {
  const config = CATEGORY_CONFIG[category]
  return {
    '--card-bg': `linear-gradient(135deg,${config.light},${config.primary})`,
    '--card-text': config.dark,
    opacity: category === props.currentCategory ? '1' : '0.6',
  }
}

function handleChange(category: Category) {
  emit('change', category)
}
</script>

<style scoped lang="scss">
.cat-row {
  display: flex;
  gap: 20rpx;
  padding: 0 32rpx 20rpx;
}

.cat-card {
  flex: 1;
  height: 184rpx;
  border-radius: 44rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  position: relative;
  overflow: hidden;
  background-image: var(--card-bg);
  color: var(--card-text);
  transform: scale(1);
  transition: transform 0.15s ease, opacity 0.2s ease, box-shadow 0.25s ease;
}

.cat-card:active {
  transform: scale(0.97);
}

.cat-card--active {
  box-shadow: 0 0 0 6rpx var(--color-white), 0 0 0 10rpx var(--card-text);
}

.cat-badge {
  position: absolute;
  top: 12rpx;
  right: 14rpx;
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: var(--color-white);
}

.cat-emoji {
  font-size: 60rpx;
  line-height: 1;
}

.cat-name {
  font-size: 26rpx;
  font-weight: 900;
}

.cat-count {
  font-size: 22rpx;
  opacity: 0.8;
}
</style>
