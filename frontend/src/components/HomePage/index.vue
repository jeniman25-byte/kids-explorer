<!-- 首页骨架：用于 PAGE 1/2/3/4 -->
<template>
  <view class="home-page" :style="pageStyle">
    <view class="home-header">
      <view class="app-name">{{ pageTitle }}</view>
      <view class="app-sub">{{ pageSubTitle }}</view>
    </view>

    <view class="cat-label">{{ categoryLabel }}</view>
    <CategorySelector :current-category="currentCategory" :mode="variant" @change="handleCategoryChange" />

    <view class="hint-wrap">
      <view class="hint-main">{{ hintMain }}</view>
      <view class="hint-sub">{{ hintSub }}</view>
      <view v-if="recognizedText" class="recognized-text">识别到：{{ recognizedText }}</view>
    </view>

    <MicButton
      :primary="currentConfig.primary"
      :light="currentConfig.light"
      :shadow="currentConfig.micShadow"
      :ring-colors="micRingColors"
      :hint="micHint"
      :active="isRecording"
      :disabled="isParsing"
      @record-start="handleRecordStart"
      @record-end="handleRecordEnd"
    />

    <view v-if="quickTitle" class="section-title">{{ quickTitle }}</view>
    <QuickCards :cards="currentConfig.quickCards" />

    <view class="section-title">{{ historyTitle }}</view>
    <HistoryScroll :items="filteredHistory" />

    <GuideBox
      :icon="guideIcon"
      :title="currentConfig.guideTitle"
      :text="currentConfig.guideText"
      :light="currentConfig.light"
      :primary="currentConfig.primary"
    />
  </view>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import CategorySelector from '@/components/CategorySelector/index.vue'
import GuideBox from '@/components/GuideBox/index.vue'
import HistoryScroll from '@/components/HistoryScroll/index.vue'
import MicButton from '@/components/MicButton/index.vue'
import QuickCards from '@/components/QuickCards/index.vue'
import { useExplorerStore } from '@/store/explorerStore'
import request from '@/utils/request'
import { startSpeechRecord, stopSpeechRecord } from '@/utils/speech'
import { getCategoryConfig, type Category } from '@/utils/category'

type HomeVariant = 'overview' | 'category'

interface HistoryItem {
  id: string
  name: string
  emoji: string
  category: Category
}

interface ParseResponse {
  success: boolean
  name: string
  name_en: string
  emoji: string
  category: string
  sub_category: string
}

const props = withDefaults(
  defineProps<{
    variant?: HomeVariant
    initialCategory?: Category
  }>(),
  {
    variant: 'overview',
    initialCategory: 'food',
  },
)

const CATEGORY_SUBTITLE: Record<Category, string> = {
  food: '看看能吃的东西都长什么样',
  animal: '观察耳朵、眼睛、尾巴和爪子',
  plant: '看看花瓣、叶子、茎和种子',
}

const HISTORY_EMOJI: Record<Category, string> = {
  food: '🍽️',
  animal: '🐾',
  plant: '🌿',
}

const GUIDE_ICON: Record<Category, string> = {
  food: '🍽️',
  animal: '🐾',
  plant: '🌿',
}

const HISTORY_LIST: HistoryItem[] = [
  { id: '1', name: '香蕉', emoji: '🍌', category: 'food' },
  { id: '2', name: '熊猫', emoji: '🐼', category: 'animal' },
  { id: '3', name: '樱花', emoji: '🌸', category: 'plant' },
  { id: '4', name: '苹果', emoji: '🍎', category: 'food' },
  { id: '5', name: '狮子', emoji: '🦁', category: 'animal' },
  { id: '6', name: '向日葵', emoji: '🌻', category: 'plant' },
]

const currentCategory = ref<Category>(props.initialCategory)
const isRecording = ref(false)
const isParsing = ref(false)
const recognizedText = ref('')
const explorerStore = useExplorerStore()

watch(
  () => props.initialCategory,
  (value) => {
    currentCategory.value = value
  },
)

const currentConfig = computed(() => getCategoryConfig(currentCategory.value))

const pageTitle = computed(() => {
  if (props.variant === 'overview') {
    return '🔭 小探索家'
  }
  return `${currentConfig.value.emoji} ${currentConfig.value.label}探索`
})

const pageSubTitle = computed(() => {
  if (props.variant === 'overview') {
    return '探索食物 · 动物 · 花草'
  }
  return CATEGORY_SUBTITLE[currentCategory.value]
})

const categoryLabel = computed(() => (props.variant === 'overview' ? '选择探索类型 ✨' : '当前分类'))

const hintMain = computed(() => currentConfig.value.hintText)

const hintSub = computed(() => currentConfig.value.hintExample)

const micHint = computed(() => {
  if (isParsing.value) {
    return '正在识别，请稍等...'
  }
  if (isRecording.value) {
    return '松开结束录音'
  }
  if (props.variant === 'overview') {
    return '按住说话'
  }
  return `按住说出${currentConfig.value.label}名称`
})

const historyTitle = computed(() => {
  if (props.variant === 'overview') {
    return '最近探索 👀'
  }
  return `最近探索 ${HISTORY_EMOJI[currentCategory.value]}`
})

const guideIcon = computed(() => {
  if (props.variant === 'overview') {
    return '✨'
  }
  return GUIDE_ICON[currentCategory.value]
})

const quickTitle = computed(() => {
  if (props.variant === 'overview') {
    return ''
  }
  return `推荐${currentConfig.value.label}`
})

const micRingColors = computed(() => [
  currentConfig.value.primary,
  currentConfig.value.primary,
  currentConfig.value.primary,
])

const filteredHistory = computed(() =>
  HISTORY_LIST.filter((item) => item.category === currentCategory.value),
)

const pageStyle = computed(() => ({
  backgroundImage: currentConfig.value.bgGradient,
}))

function ensureApiToken() {
  const existing = uni.getStorageSync('token') as string | undefined
  if (existing) {
    return
  }
  const envToken = import.meta.env.VITE_APP_TOKEN as string | undefined
  uni.setStorageSync('token', envToken ?? 'your-random-secret-token')
}

function isCategory(value: string): value is Category {
  return value === 'food' || value === 'animal' || value === 'plant'
}

function handleCategoryChange(category: Category) {
  currentCategory.value = category
}

async function handleRecordStart() {
  if (isRecording.value || isParsing.value) {
    return
  }

  try {
    await startSpeechRecord()
    isRecording.value = true
    recognizedText.value = ''
  } catch (error) {
    console.error('[speech] start failed:', error)
    uni.showToast({
      title: '录音功能暂不可用',
      icon: 'none',
    })
  }
}

async function handleRecordEnd() {
  if (!isRecording.value || isParsing.value) {
    return
  }

  isRecording.value = false
  isParsing.value = true

  try {
    const text = await stopSpeechRecord()
    recognizedText.value = text
    await parseAndNavigate(text)
  } catch (error) {
    console.error('[speech] stop failed:', error)
  } finally {
    isParsing.value = false
  }
}

async function parseAndNavigate(text: string) {
  ensureApiToken()

  try {
    const result = await request<ParseResponse>({
      url: '/api/parse',
      method: 'POST',
      data: { text },
    })

    if (!result.success || !isCategory(result.category)) {
      uni.showToast({
        title: '我还没听懂这个对象，再试试～',
        icon: 'none',
      })
      return
    }

    if (result.category !== currentCategory.value) {
      const targetConfig = getCategoryConfig(result.category)
      currentCategory.value = result.category
      uni.showToast({
        title: `我听到的是 ${targetConfig.emoji} ${targetConfig.label}，帮你切换过去了～`,
        icon: 'none',
        duration: 1800,
      })
    }

    const seed = Math.floor(Math.random() * 90000) + 10000
    explorerStore.setCurrentSubject({
      name: result.name,
      nameEn: result.name_en,
      emoji: result.emoji,
      category: result.category,
      subCategory: result.sub_category,
      seed,
      subjectId: null,
    })
    explorerStore.resetImages()
    explorerStore.setGeneratingState({
      step: 1,
      fourProgress: 0,
      fourDone: false,
      eightDone: false,
      visionDone: false,
    })

    const query = `subjectName=${encodeURIComponent(result.name)}&category=${result.category}&nameEn=${encodeURIComponent(result.name_en)}&seed=${seed}`
    uni.navigateTo({
      url: `/pages/generating/index?${query}`,
    })
  } catch (error) {
    console.error('[parse] request failed:', error)
    uni.showToast({
      title: '识别失败，请稍后再试',
      icon: 'none',
    })
  }
}
</script>

<style scoped lang="scss">
.home-page {
  min-height: 100vh;
  padding-bottom: 36rpx;
  background-size: cover;
  background-position: center;
  transition: background-image 0.4s ease;
}

.home-header {
  text-align: center;
  padding: 28rpx 0 10rpx;
}

.app-name {
  font-size: 48rpx;
  font-weight: 900;
  color: var(--text-main);
}

.app-sub {
  font-size: 26rpx;
  color: var(--text-sub);
  margin-top: 4rpx;
}

.cat-label {
  padding: 16rpx 36rpx 12rpx;
  font-size: 30rpx;
  font-weight: 900;
  color: var(--text-main);
}

.hint-wrap {
  text-align: center;
  padding: 0 48rpx 14rpx;
}

.hint-main {
  font-size: 40rpx;
  font-weight: 900;
  color: var(--text-main);
  line-height: 1.45;
}

.hint-sub {
  margin-top: 8rpx;
  font-size: 25rpx;
  color: var(--text-sub);
  line-height: 1.5;
}

.recognized-text {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: var(--text-sub);
}

.section-title {
  padding: 16rpx 36rpx 12rpx;
  font-size: 30rpx;
  font-weight: 900;
  color: var(--text-main);
}
</style>
