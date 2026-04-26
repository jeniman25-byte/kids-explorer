<!-- 特写页通用容器（PAGE 9/10/11） -->
<template>
  <view class="detail-page" :style="pageVars">
    <view class="top-bar">
      <view class="back-btn" @tap="goBack">←</view>
      <view class="page-title">{{ currentPart?.name ?? '部位' }} 🔍</view>
      <view class="cat-pill">{{ config.label }}</view>
    </view>

    <view class="detail-card">
      <view class="detail-img">
        <image v-if="currentImageUrl" class="detail-main-image" :src="currentImageUrl" mode="aspectFill" />
        <view v-else class="detail-emoji">{{ subjectEmoji }}</view>
        <view class="zoom-badge">🔍 {{ currentPart?.name ?? '部位' }}特写</view>
      </view>

      <view class="detail-body">
        <view class="detail-name">{{ subjectName }} · {{ currentPart?.name ?? '部位' }}</view>
        <view class="detail-tag">{{ subjectEmoji }} {{ config.label }} · 部位观察</view>

        <view class="karaoke">
          <rich-text
            v-for="(line, idx) in karaokeNodes"
            :key="`karaoke-${idx}`"
            class="karaoke-line"
            :nodes="line"
          />
        </view>

        <view class="audio-label">🔊 语音讲解（M6）</view>
        <view class="audio-bar">
          <view class="audio-prog" />
        </view>
      </view>
    </view>

    <FactCards :category="props.category" :facts="currentPart?.facts ?? {}" />

    <view class="section-title">相关部位</view>
    <RelatedParts :parts="parts" :current-part-id="currentPartId" @select="switchPart" />

    <view class="next-btn" @tap="nextPart">👉 下一个部位</view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import FactCards from '@/components/FactCards/index.vue'
import RelatedParts from '@/components/RelatedParts/index.vue'
import { useExplorerStore, type SubjectPart } from '@/store/explorerStore'
import { getCategoryConfig, type Category } from '@/utils/category'
import { vibrateShort } from '@/utils/feedback'

const props = defineProps<{
  category: Category
}>()

const explorerStore = useExplorerStore()
const config = computed(() => getCategoryConfig(props.category))
const currentPartId = ref<string | null>(null)

const subjectName = computed(() => explorerStore.currentSubject?.name ?? config.value.quickCards[0].name)
const subjectEmoji = computed(() => explorerStore.currentSubject?.emoji ?? config.value.emoji)
const currentImageUrl = computed(
  () => explorerStore.images.four.find((item) => item.view === 'front')?.url ?? explorerStore.images.four[0]?.url ?? '',
)

const pageVars = computed(() => ({
  '--primary': config.value.primary,
  '--light': config.value.light,
}))

const parts = computed<SubjectPart[]>(() => {
  if (explorerStore.parts.length > 0) {
    return explorerStore.parts
  }
  const keys = config.value.factsKeys
  return [
    {
      id: `${props.category}_part_1`,
      name: props.category === 'animal' ? '眼睛' : props.category === 'plant' ? '花瓣' : '外皮',
      shortName: props.category === 'animal' ? '眼' : props.category === 'plant' ? '瓣' : '皮',
      color: '#FFB347',
      x: 0.4,
      y: 0.3,
      description: `${subjectName.value}的这个部位有独特的外观特点，很适合近距离观察。`,
      facts: {
        [keys[0]]: `${subjectName.value}常见${keys[0]}特征`,
        [keys[1]]: `${subjectName.value}的${keys[1]}知识`,
        [keys[2]]: `${subjectName.value}${keys[2]}相关信息`,
      },
    },
  ]
})

const currentPart = computed(() => parts.value.find((part) => part.id === currentPartId.value) ?? parts.value[0] ?? null)

const karaokeNodes = computed(() => {
  const description = currentPart.value?.description ?? ''
  const facts = Object.values(currentPart.value?.facts ?? {}).slice(0, 3)
  const lines = description
    .replace(/\n/g, '。')
    .split(/[。！？]/)
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 3)

  const source = lines.length > 0 ? lines : [description || `${subjectName.value}这个部位值得继续观察。`]
  return source.map((line, idx) => toKaraokeLine(line, facts[idx], idx))
})

function escapeHtml(raw: string): string {
  return raw
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function toKaraokeLine(line: string, keyword: string | undefined, idx: number): string {
  const text = escapeHtml(line)
  const safeKeyword = escapeHtml(keyword ?? '')
  const colors = [config.value.primary, '#4FC3F7', '#66BB6A']
  const bgColors = [config.value.light, '#E3F6FF', '#E8F5E9']

  if (!safeKeyword || !text.includes(safeKeyword)) {
    return text
  }

  const marker = `<span style="color:${colors[idx % 3]};background:${bgColors[idx % 3]};font-weight:900;padding:2px 8px;border-radius:12px;">${safeKeyword}</span>`
  return text.replace(safeKeyword, marker)
}

function initCurrentPartId() {
  const pages = getCurrentPages() as unknown as Array<{ options?: Record<string, string> }>
  const currentPage = pages[pages.length - 1]
  const queryPartId = currentPage?.options?.partId
  const storePartId = explorerStore.currentPartId
  currentPartId.value = queryPartId || storePartId || parts.value[0]?.id || null
  explorerStore.setCurrentPartId(currentPartId.value)
}

function switchPart(partId: string) {
  vibrateShort()
  currentPartId.value = partId
  explorerStore.setCurrentPartId(partId)
}

function nextPart() {
  if (parts.value.length === 0) {
    return
  }
  vibrateShort()
  const currentIndex = parts.value.findIndex((part) => part.id === currentPartId.value)
  const nextIndex = currentIndex < 0 ? 0 : (currentIndex + 1) % parts.value.length
  switchPart(parts.value[nextIndex].id)
}

function goBack() {
  vibrateShort()
  uni.navigateBack({
    fail: () => {
      uni.navigateTo({
        url: `/pages/${props.category}/explore/index`,
      })
    },
  })
}

onMounted(() => {
  explorerStore.setCurrentCategory(props.category)
  initCurrentPartId()
})
</script>

<style scoped lang="scss">
.detail-page {
  min-height: 100vh;
  background: #fffbf0;
  padding: 12rpx 0 30rpx;
}

.top-bar {
  display: flex;
  align-items: center;
  gap: 14rpx;
  padding: 16rpx 32rpx 10rpx;
}

.back-btn {
  width: 66rpx;
  height: 66rpx;
  border-radius: 20rpx;
  background: var(--light);
  color: var(--primary);
  font-size: 38rpx;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-title {
  flex: 1;
  font-size: 34rpx;
  color: var(--text-main);
  font-weight: 900;
}

.cat-pill {
  height: 52rpx;
  padding: 0 18rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 800;
  color: #ffffff;
  background: var(--primary);
  display: flex;
  align-items: center;
}

.detail-card {
  margin: 8rpx 32rpx 0;
  border-radius: 32rpx;
  background: #ffffff;
  overflow: hidden;
  box-shadow: 0 12rpx 24rpx var(--surface-shadow);
}

.detail-img {
  height: 300rpx;
  position: relative;
  background: linear-gradient(135deg, var(--light), #ffffff);
}

.detail-main-image {
  width: 100%;
  height: 100%;
}

.detail-emoji {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 140rpx;
}

.zoom-badge {
  position: absolute;
  right: 16rpx;
  bottom: 16rpx;
  height: 46rpx;
  padding: 0 16rpx;
  border-radius: 999rpx;
  background: rgba(0, 0, 0, 0.58);
  color: #ffffff;
  font-size: 22rpx;
  display: flex;
  align-items: center;
}

.detail-body {
  padding: 16rpx 18rpx 20rpx;
}

.detail-name {
  font-size: 30rpx;
  color: var(--text-main);
  font-weight: 900;
}

.detail-tag {
  display: inline-flex;
  align-items: center;
  margin-top: 8rpx;
  padding: 0 14rpx;
  height: 44rpx;
  border-radius: 999rpx;
  background: var(--primary);
  color: #ffffff;
  font-size: 20rpx;
  font-weight: 800;
}

.karaoke {
  margin-top: 12rpx;
}

.karaoke-line {
  display: block;
  margin-top: 6rpx;
  color: #5a4020;
  font-size: 23rpx;
  line-height: 1.7;
}

.audio-label {
  margin-top: 12rpx;
  font-size: 22rpx;
  color: var(--text-sub);
}

.audio-bar {
  margin-top: 8rpx;
  height: 12rpx;
  border-radius: 999rpx;
  background: #f5edd8;
  overflow: hidden;
}

.audio-prog {
  width: 42%;
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, var(--primary), var(--light));
}

.section-title {
  margin: 12rpx 32rpx 0;
  font-size: 24rpx;
  color: var(--text-sub);
  font-weight: 800;
}

.next-btn {
  margin: 16rpx 32rpx 0;
  height: 90rpx;
  border-radius: 28rpx;
  font-size: 29rpx;
  font-weight: 900;
  color: #ffffff;
  background: linear-gradient(135deg, var(--light), var(--primary));
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
