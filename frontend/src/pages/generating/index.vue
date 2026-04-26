<!-- PAGE 5：生成中 -->
<template>
  <view class="page" :style="pageStyle">
    <view class="top-bar">
      <view class="back-btn">←</view>
      <view class="page-title">正在生成中…</view>
      <view class="cat-pill">AI✨</view>
    </view>

    <view class="small-sub">听到你说“{{ subjectName }}长什么样”啦，正在帮你画图和拆解部位。</view>

    <view class="step-list">
      <view
        v-for="(step, index) in steps"
        :key="step.title"
        class="step-card"
        :class="getStepClass(index + 1)"
      >
        <view class="step-icon" :style="stepIconStyle(index + 1)">{{ step.icon }}</view>
        <view class="step-main-wrap">
          <view class="step-main">{{ step.title }}</view>
          <view class="step-sub" :style="stepSubStyle(index + 1)">{{ step.sub }}</view>
        </view>
        <view v-if="step.time" class="step-time" :class="{ 'step-time--active': currentStep === index + 1 }">
          {{ step.time }}
        </view>
      </view>
    </view>

    <view class="progress">
      <view class="bar" :style="barStyle" />
    </view>

    <view class="preview-row">
      <view
        v-for="preview in previews"
        :key="preview.label"
        class="preview-mini"
        :class="preview.done ? 'preview-mini--done' : 'preview-mini--pending'"
      >
        <image v-if="preview.done && preview.url" class="preview-image" :src="preview.url" mode="aspectFill" />
        <view v-else class="pm1">✨</view>
        <view class="pm2">{{ preview.label }}</view>
        <view class="pm3">{{ preview.done ? '已完成' : '生成中' }}</view>
      </view>
    </view>

    <view class="loading-card">
      <view class="l1">🎨</view>
      <view class="l2">{{ waitingTexts[waitingIndex] }}</view>
      <view class="l3">先把{{ subjectName }}的四个方向画出来，
再继续补齐八个方向和身体部位。</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onBackPress, onLoad, onUnload } from '@dcloudio/uni-app'

import { useExplorerStore, type ViewImage } from '@/store/explorerStore'
import request from '@/utils/request'
import { getCategoryConfig, type Category } from '@/utils/category'

interface ImageStartResponse {
  success: boolean
  subject_id: number
  images: ViewImage[]
}

interface ImageStatusResponse {
  success: boolean
  subject_id: number
  status: string
  four_progress: number
  four_done: boolean
  eight_progress: number
  eight_done: boolean
  images: {
    four: ViewImage[]
    eight: ViewImage[]
  }
}

interface StepItem {
  icon: string
  title: string
  sub: string
  time: string
}

const explorerStore = useExplorerStore()

const subjectName = ref('熊猫')
const nameEn = ref('giant panda')
const currentCategory = ref<Category>('animal')
const currentStep = ref(1)
const waitingIndex = ref(0)
const subjectId = ref<number | null>(null)
const fourProgress = ref(0)
const eightProgress = ref(0)
const fourDone = ref(false)
const eightDone = ref(false)
const hasNavigated = ref(false)
const seed = ref(Math.floor(Math.random() * 90000) + 10000)

let waitingTimer: ReturnType<typeof setInterval> | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null
let mockTimer: ReturnType<typeof setTimeout> | null = null

const waitingTexts = [
  'AI 小画家正在努力工作～',
  '正在给你画出最可爱的视角～',
  '正在补全四面图细节，请稍等～',
  '马上就能看到部位拆解啦～',
  '再等一下下，探索就要开始啦～',
]

const currentConfig = computed(() => getCategoryConfig(currentCategory.value))

const steps = computed<StepItem[]>(() => [
  {
    icon: '✅',
    title: '识别关键词',
    sub: `已识别：${subjectName.value} / ${currentCategory.value}`,
    time: '0.4s',
  },
  {
    icon: currentStep.value > 2 ? '✅' : '⚙️',
    title: '生成正面图',
    sub: fourProgress.value > 0 ? '正面插画已开始生成' : '任务已创建，等待开始…',
    time: fourProgress.value > 0 ? `${Math.max(1, Math.round(fourProgress.value / 25))}.0s` : '',
  },
  {
    icon: fourDone.value ? '✅' : currentStep.value === 3 ? '⚙️' : '⏳',
    title: '生成四面图',
    sub: fourDone.value ? '四面图已完成' : `当前进度 ${fourProgress.value}%`,
    time: `${fourProgress.value}%`,
  },
  {
    icon: eightDone.value ? '✅' : currentStep.value >= 4 ? '⚙️' : '⏳',
    title: '生成八方图',
    sub: eightDone.value ? '八方图已完成' : currentStep.value >= 4 ? `当前进度 ${eightProgress.value}%` : '等待四面图完成…',
    time: currentStep.value >= 4 ? `${eightProgress.value}%` : '',
  },
  {
    icon: '⏳',
    title: '图像拆解标注',
    sub: '等待全部图完成…',
    time: '',
  },
])

const previews = computed(() => {
  const labels: Array<{ key: string; label: string }> = [
    { key: 'front', label: '正面' },
    { key: 'back', label: '背面' },
    { key: 'left', label: '左面' },
    { key: 'right', label: '右面' },
  ]

  return labels.map((item) => {
    const img = explorerStore.images.four.find((entry) => entry.view === item.key)
    return {
      label: item.label,
      done: Boolean(img),
      url: img?.url ?? '',
    }
  })
})

const barStyle = computed(() => ({
  width: `${stepProgress(currentStep.value)}%`,
  backgroundImage: `linear-gradient(90deg,${currentConfig.value.primary},${currentConfig.value.light})`,
}))

const pageStyle = computed(() => ({
  '--primary': currentConfig.value.primary,
  '--light': currentConfig.value.light,
}))

function stepProgress(step: number): number {
  if (step <= 1) return 20
  if (step === 2) return 40
  if (step === 3) return 60
  if (step === 4) return 82
  return 100
}

function getStepClass(step: number) {
  if (step < currentStep.value) {
    return 'step-card--done'
  }
  if (step === currentStep.value) {
    return 'step-card--active'
  }
  return 'step-card--pending'
}

function stepIconStyle(step: number) {
  if (step < currentStep.value) {
    return { background: '#E8F5E9' }
  }
  if (step === currentStep.value) {
    return { background: '#FFF3CC' }
  }
  return { background: '#F3E5F5' }
}

function stepSubStyle(step: number) {
  if (step < currentStep.value) {
    return { color: '#66BB6A' }
  }
  if (step === currentStep.value) {
    return { color: 'var(--primary)' }
  }
  return { color: '#B2B2B2' }
}

function ensureApiToken() {
  const existing = uni.getStorageSync('token') as string | undefined
  if (existing) {
    return
  }
  const envToken = import.meta.env.VITE_APP_TOKEN as string | undefined
  uni.setStorageSync('token', envToken ?? 'your-random-secret-token')
}

function applyStatus(result: ImageStatusResponse) {
  subjectId.value = result.subject_id
  fourProgress.value = result.four_progress
  eightProgress.value = result.eight_progress
  fourDone.value = result.four_done
  eightDone.value = result.eight_done

  explorerStore.setSubjectId(result.subject_id)
  explorerStore.setFourImages(result.images.four)
  explorerStore.setEightImages(result.images.eight)

  if (fourDone.value && !eightDone.value) {
    currentStep.value = 4
  } else if (fourProgress.value > 0 && !fourDone.value) {
    currentStep.value = 3
  } else if (subjectId.value) {
    currentStep.value = 2
  }

  explorerStore.setGeneratingState({
    step: currentStep.value,
    fourProgress: fourProgress.value,
    fourDone: fourDone.value,
    eightDone: eightDone.value,
    visionDone: false,
  })

  if (fourDone.value && !hasNavigated.value) {
    hasNavigated.value = true
    stopPolling()
    navigateToExplorePage()
  }
}

async function startGeneration() {
  ensureApiToken()

  const payload = {
    name: subjectName.value,
    name_en: nameEn.value,
    category: currentCategory.value,
    mode: '4view' as const,
    seed: seed.value,
  }

  try {
    const res = await request<ImageStartResponse>({
      url: '/api/image',
      method: 'POST',
      data: payload,
    })

    subjectId.value = res.subject_id
    explorerStore.setSubjectId(res.subject_id)
    explorerStore.setFourImages(res.images)

    currentStep.value = 2
    startPolling()
  } catch (error) {
    console.error('[image] start generation failed:', error)
    uni.showToast({
      title: '生成任务创建失败',
      icon: 'none',
    })
  }
}

async function pollStatus() {
  if (!subjectId.value) {
    return
  }

  try {
    const result = await request<ImageStatusResponse>({
      url: `/api/image/status/${subjectId.value}`,
      method: 'GET',
    })
    applyStatus(result)
  } catch (error) {
    console.error('[image] polling status failed:', error)
  }
}

function startPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
  pollTimer = setInterval(() => {
    void pollStatus()
  }, 2000)
  void pollStatus()
}

function stopPolling() {
  if (!pollTimer) {
    return
  }
  clearInterval(pollTimer)
  pollTimer = null
}

function navigateToExplorePage() {
  const routeMap: Record<Category, string> = {
    food: '/pages/food/explore/index',
    animal: '/pages/animal/explore/index',
    plant: '/pages/plant/explore/index',
  }
  uni.navigateTo({
    url: routeMap[currentCategory.value],
  })
}

function enableUnloadGuard() {
  // #ifdef MP-WEIXIN
  const wxAny = wx as any
  if (wxAny.enableAlertBeforeUnload) {
    wxAny.enableAlertBeforeUnload({
      message: '图片正在生成，确定离开吗？',
    })
  }
  // #endif
}

function disableUnloadGuard() {
  // #ifdef MP-WEIXIN
  const wxAny = wx as any
  if (wxAny.disableAlertBeforeUnload) {
    wxAny.disableAlertBeforeUnload()
  }
  // #endif
}

function startMockProgress() {
  mockTimer = setTimeout(() => {
    if (currentStep.value < 3) {
      currentStep.value = 3
    }
  }, 2000)
}

function startWaitingRotation() {
  waitingTimer = setInterval(() => {
    waitingIndex.value = (waitingIndex.value + 1) % waitingTexts.length
  }, 3000)
}

function clearTimers() {
  if (mockTimer) {
    clearTimeout(mockTimer)
    mockTimer = null
  }
  if (waitingTimer) {
    clearInterval(waitingTimer)
    waitingTimer = null
  }
  stopPolling()
}

onLoad((query) => {
  const name = typeof query.subjectName === 'string' ? decodeURIComponent(query.subjectName) : ''
  const category = typeof query.category === 'string' ? query.category : ''
  const seedParam = Number(query.seed)
  const nameEnParam = typeof query.nameEn === 'string' ? decodeURIComponent(query.nameEn) : ''

  if (name) {
    subjectName.value = name
  }

  if (nameEnParam) {
    nameEn.value = nameEnParam
  }

  if (category === 'food' || category === 'animal' || category === 'plant') {
    currentCategory.value = category
  }

  if (Number.isFinite(seedParam) && seedParam > 0) {
    seed.value = seedParam
  }

  if (explorerStore.currentSubject) {
    subjectName.value = explorerStore.currentSubject.name
    nameEn.value = explorerStore.currentSubject.nameEn
    currentCategory.value = explorerStore.currentSubject.category
    seed.value = explorerStore.currentSubject.seed
  }
})

onMounted(() => {
  enableUnloadGuard()
  startMockProgress()
  startWaitingRotation()
  void startGeneration()
})

onUnload(() => {
  clearTimers()
  disableUnloadGuard()
})

onBackPress(() => {
  uni.showToast({
    title: '正在生成中，请稍等～',
    icon: 'none',
  })
  return true
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #fffbf0;
  padding-bottom: 30rpx;
}

.top-bar {
  display: flex;
  align-items: center;
  padding: 16rpx 32rpx 12rpx;
  gap: 20rpx;
}

.back-btn {
  width: 76rpx;
  height: 76rpx;
  border-radius: 28rpx;
  background: var(--light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34rpx;
}

.page-title {
  flex: 1;
  text-align: center;
  font-size: 40rpx;
  font-weight: 900;
  color: var(--text-main);
}

.cat-pill {
  font-size: 22rpx;
  font-weight: 900;
  color: var(--color-white);
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  background: #66bb6a;
}

.small-sub {
  padding: 0 36rpx 14rpx;
  color: var(--text-sub);
  font-size: 24rpx;
  line-height: 1.6;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding: 0 32rpx;
}

.step-card {
  background: var(--surface);
  border-radius: 34rpx;
  padding: 24rpx 26rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 6rpx 20rpx var(--surface-shadow);
}

.step-card--active {
  background: #fff8e7;
  border: 4rpx solid var(--light);
}

.step-card--pending {
  opacity: 0.52;
}

.step-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34rpx;
}

.step-main-wrap {
  flex: 1;
}

.step-main {
  font-size: 30rpx;
  font-weight: 900;
  color: var(--text-main);
}

.step-sub {
  font-size: 24rpx;
  margin-top: 4rpx;
}

.step-time {
  font-size: 22rpx;
  color: #b2b2b2;
}

.step-time--active {
  color: var(--primary);
  font-weight: 900;
}

.progress {
  margin: 16rpx 32rpx 0;
  background: #f5edd8;
  border-radius: 999rpx;
  height: 18rpx;
  overflow: hidden;
}

.bar {
  height: 100%;
  border-radius: 999rpx;
  transition: width 0.4s ease;
}

.preview-row {
  display: flex;
  gap: 14rpx;
  padding: 20rpx 32rpx 0;
}

.preview-mini {
  flex: 1;
  height: 152rpx;
  border-radius: 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  overflow: hidden;
}

.preview-mini--done {
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
}

.preview-mini--pending {
  background: linear-gradient(135deg, #fff8e7, #ffe8a3);
}

.preview-image {
  width: 100%;
  height: 78rpx;
  border-radius: 20rpx;
  margin-top: 8rpx;
}

.pm1 {
  font-size: 46rpx;
}

.pm2 {
  font-size: 22rpx;
  font-weight: 900;
  color: var(--text-main);
}

.pm3 {
  font-size: 18rpx;
  color: var(--text-sub);
}

.loading-card {
  margin: 18rpx 32rpx 0;
  border-radius: 38rpx;
  padding: 28rpx;
  text-align: center;
  background: linear-gradient(135deg, #fff3cc, #ffe08a);
}

.l1 {
  font-size: 56rpx;
}

.l2 {
  margin-top: 8rpx;
  font-size: 30rpx;
  font-weight: 900;
  color: var(--text-main);
}

.l3 {
  margin-top: 8rpx;
  font-size: 24rpx;
  color: var(--text-sub);
  line-height: 1.6;
  white-space: pre-line;
}
</style>
