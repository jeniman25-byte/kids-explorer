<!-- PAGE A/B：四面图 + 八方图 -->
<template>
  <view class="page" :style="pageVars">
    <view class="topbar">
      <view class="back" @tap="goBack">←</view>
      <view class="title">{{ subjectName }} · 多视角</view>
      <view class="pill">{{ activeTab === 'four' ? '4VIEW' : '8VIEW' }}</view>
    </view>

    <view class="tabs">
      <view class="tab" :class="activeTab === 'four' ? 'tab-on' : 'tab-off'" @tap="switchTab('four')">🔲 四面图</view>
      <view
        class="tab"
        :class="activeTab === 'eight' ? 'tab-on tab-purple' : 'tab-off'"
        @tap="switchTab('eight')"
      >
        {{ eightUnlocked ? '🔮 八方图' : '⏳ 生成中…' }}
      </view>
    </view>

    <ApiErrorState
      v-if="errorMessage"
      title="多视角望远镜起雾啦"
      :message="errorMessage"
      @retry="reloadPageData"
    />
    <view v-else-if="loading" class="loading">正在整理多视角图片…</view>

    <view v-else>
      <Compass4
        v-if="activeTab === 'four'"
        :images="fourImages"
        :current-view="currentView"
        :emoji="subjectEmoji"
        :light="config.light"
        :primary="config.primary"
        @change="handleSwitchView"
      />

      <Compass8
        v-else
        :images="eightImages"
        :current-view="currentView"
        :emoji="subjectEmoji"
        :light="config.light"
        :primary="config.primary"
        :view-description="currentViewDescription"
        @change="handleSwitchView"
      />

      <view class="btns">
        <view class="btn btn-1" @tap="toggleCompass">{{ activeTab === 'four' ? '🔮 八方图' : '🔲 四面图' }}</view>
        <view class="btn btn-2" @tap="speakCurrentView">🔊 介绍</view>
        <view class="btn btn-3" @tap="openDetailView">🔍 部位</view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import ApiErrorState from '@/components/ApiErrorState/index.vue'
import Compass4 from '@/components/Compass4/index.vue'
import Compass8 from '@/components/Compass8/index.vue'
import { useExplorerStore, type Category, type ViewImage } from '@/store/explorerStore'
import request from '@/utils/request'
import { getCategoryConfig } from '@/utils/category'
import { vibrateShort } from '@/utils/feedback'
import { getTtsAudioBase64 } from '@/utils/tts'

interface ImageStatusResponse {
  success: boolean
  status: string
  four_done: boolean
  eight_done: boolean
  images: {
    four: ViewImage[]
    eight: ViewImage[]
  }
}

interface VisionResponse {
  success: boolean
  view_description: string
}

const explorerStore = useExplorerStore()
const activeTab = ref<'four' | 'eight'>('four')
const currentView = ref('front')
const errorMessage = ref('')
const loading = ref(false)
const descriptions = ref<Record<string, string>>({})

let pollTimer: ReturnType<typeof setInterval> | null = null
let ttsAudioContext: UniApp.InnerAudioContext | null = null

const category = computed<Category>(() => explorerStore.currentSubject?.category ?? explorerStore.currentCategory)
const config = computed(() => getCategoryConfig(category.value))
const subjectId = computed(() => explorerStore.currentSubject?.subjectId ?? null)
const subjectName = computed(() => explorerStore.currentSubject?.name ?? '探索对象')
const subjectNameEn = computed(() => explorerStore.currentSubject?.nameEn ?? 'unknown')
const subjectEmoji = computed(() => explorerStore.currentSubject?.emoji ?? config.value.emoji)
const fourImages = computed(() => explorerStore.images.four)
const eightImages = computed(() => explorerStore.images.eight)
const eightUnlocked = computed(() => explorerStore.generating.eightDone || eightImages.value.length >= 4)

const pageVars = computed(() => ({
  '--primary': config.value.primary,
  '--light': config.value.light,
}))

const currentImage = computed(() => {
  const list = activeTab.value === 'four' ? fourImages.value : eightImages.value
  return list.find((item) => item.view === currentView.value) ?? list[0]
})

const currentViewDescription = computed(() => {
  return descriptions.value[currentView.value] || `这是${subjectName.value}的${currentImage.value?.label ?? '当前'}视角。`
})

function ensureAudioContext() {
  if (ttsAudioContext) {
    return ttsAudioContext
  }
  ttsAudioContext = uni.createInnerAudioContext()
  ttsAudioContext.autoplay = false
  ttsAudioContext.obeyMuteSwitch = false
  return ttsAudioContext
}

async function speakCurrentView() {
  if (!currentViewDescription.value) {
    return
  }
  try {
    const audioBase64 = await getTtsAudioBase64(currentViewDescription.value)
    const ctx = ensureAudioContext()
    ctx.stop()
    ctx.src = audioBase64
    ctx.play()
  } catch (error) {
    console.error('[multiview] speak failed:', error)
    uni.showToast({
      title: '语音播报失败，再试试吧～',
      icon: 'none',
    })
  }
}

async function fetchViewDescription(view: string) {
  if (!subjectId.value || !currentImage.value?.url || descriptions.value[view]) {
    return
  }

  try {
    const result = await request<VisionResponse>({
      url: '/api/vision',
      method: 'POST',
      data: {
        image_url: currentImage.value.url,
        name: subjectName.value,
        name_en: subjectNameEn.value,
        category: category.value,
        view,
        subject_id: subjectId.value,
      },
    })
    descriptions.value[view] = result.view_description
  } catch (error) {
    console.error('[multiview] vision description failed:', error)
  }
}

async function refreshImageStatus() {
  if (!subjectId.value) {
    return
  }

  loading.value = true
  try {
    const status = await request<ImageStatusResponse>({
      url: `/api/image/status/${subjectId.value}`,
      method: 'GET',
    })

    explorerStore.setFourImages(status.images.four ?? [])
    explorerStore.setEightImages(status.images.eight ?? [])
    explorerStore.setGeneratingState({
      ...explorerStore.generating,
      fourDone: status.four_done,
      eightDone: status.eight_done,
    })
  } catch (error) {
    console.error('[multiview] status failed:', error)
    errorMessage.value = '图片加载有点慢，我们一起再试一次吧～'
  } finally {
    loading.value = false
  }
}

async function reloadPageData() {
  errorMessage.value = ''
  await refreshImageStatus()
  const initialView = activeTab.value === 'four' ? fourImages.value[0]?.view : eightImages.value[0]?.view
  currentView.value = initialView ?? 'front'
  await fetchViewDescription(currentView.value)
}

function switchTab(tab: 'four' | 'eight') {
  if (tab === 'eight' && !eightUnlocked.value) {
    vibrateShort('light')
    uni.showToast({
      title: '八方图还在生成中…',
      icon: 'none',
    })
    return
  }
  vibrateShort()
  activeTab.value = tab
  currentView.value = tab === 'four' ? fourImages.value[0]?.view ?? 'front' : eightImages.value[0]?.view ?? 'front_left'
  void fetchViewDescription(currentView.value)
}

function handleSwitchView(view: string) {
  currentView.value = view
  void fetchViewDescription(view)
  void speakCurrentView()
}

function toggleCompass() {
  switchTab(activeTab.value === 'four' ? 'eight' : 'four')
}

function openDetailView() {
  vibrateShort()
  uni.navigateTo({
    url: `/pages/multiview/detail?view=${encodeURIComponent(currentView.value)}`,
  })
}

function goBack() {
  vibrateShort()
  uni.navigateBack()
}

function startPollingIfNeeded() {
  if (eightUnlocked.value || !subjectId.value) {
    return
  }
  pollTimer = setInterval(() => {
    void refreshImageStatus()
  }, 3000)
}

onMounted(async () => {
  await reloadPageData()
  startPollingIfNeeded()
})

onBeforeUnmount(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  if (ttsAudioContext) {
    ttsAudioContext.stop()
    ttsAudioContext.destroy()
    ttsAudioContext = null
  }
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #fffbf0;
  padding-bottom: 20rpx;
}

.topbar {
  display: flex;
  align-items: center;
  padding: 14rpx 16rpx 10rpx;
  gap: 10rpx;
}

.back {
  width: 64rpx;
  height: 64rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 38rpx;
  background: var(--light);
  color: #7d5f35;
}

.title {
  flex: 1;
  font-size: 34rpx;
  color: #3d2c00;
  font-weight: 900;
}

.pill {
  font-size: 20rpx;
  font-weight: 900;
  padding: 4rpx 10rpx;
  border-radius: 20rpx;
  color: #fff;
  background: var(--primary);
}

.tabs {
  display: flex;
  margin: 0 16rpx 10rpx;
  gap: 8rpx;
}

.tab {
  flex: 1;
  height: 72rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 900;
}

.tab-on {
  background: var(--primary);
  color: #fff;
  box-shadow: 0 4rpx 12rpx rgba(255, 179, 71, 0.35);
}

.tab-purple {
  background: #ab47bc;
  box-shadow: 0 4rpx 12rpx rgba(171, 71, 188, 0.4);
}

.tab-off {
  background: #f5edd8;
  color: #a07840;
}

.btns {
  display: flex;
  gap: 10rpx;
  padding: 12rpx 16rpx 0;
}

.loading {
  margin: 24rpx 16rpx;
  padding: 24rpx 16rpx;
  border-radius: 18rpx;
  background: #fff;
  text-align: center;
  color: #8a6a42;
  font-size: 24rpx;
}

.btn {
  flex: 1;
  height: 78rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5rpx;
  font-size: 24rpx;
  font-weight: 900;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.btn-1 {
  background: linear-gradient(135deg, #ffd166, #ffb347);
  color: #3d2c00;
}

.btn-2 {
  background: linear-gradient(135deg, #80deea, #26c6da);
  color: #fff;
}

.btn-3 {
  background: linear-gradient(135deg, #a5d6a7, #66bb6a);
  color: #fff;
}
</style>
