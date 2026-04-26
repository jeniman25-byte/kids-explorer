<!-- PAGE C：视角标注 + 特写 -->
<template>
  <view class="page" :style="pageVars">
    <view class="topbar">
      <view class="back" @tap="goBack">←</view>
      <view class="title">{{ subjectName }} · 标注特写</view>
      <view class="pill">{{ config.label }}</view>
    </view>

    <scroll-view class="view-tabs" scroll-x show-scrollbar="false">
      <view
        v-for="item in allViews"
        :key="item.view"
        class="vtab"
        :class="{ on: item.view === currentView }"
        :style="item.view === currentView ? { background: config.primary } : undefined"
        @tap="switchView(item.view)"
      >
        {{ item.label }}
      </view>
    </scroll-view>

    <ApiErrorState
      v-if="errorMessage"
      title="标注放大镜正在擦镜片"
      :message="errorMessage"
      @retry="reloadCurrentView"
    />

    <view v-else>
      <SubjectCanvas :image-url="currentImageUrl" :parts="currentParts" @select="handleMarkerSelect" />

      <scroll-view class="parts-strip" scroll-x show-scrollbar="false">
        <view
          v-for="part in currentParts"
          :key="part.id"
          class="pchip"
          :class="{ active: part.id === selectedPartId }"
          @tap="selectPart(part.id)"
        >
          <view class="pdot" :style="{ background: part.color }" />
          <text>{{ part.name }}</text>
        </view>
      </scroll-view>

      <view class="sec">🔍 当前选中：{{ selectedPart?.name ?? '—' }}</view>
      <view class="detail-popup">
        <view class="pop-img" :style="{ background: `linear-gradient(135deg,${config.light},${config.primary})` }">
          <image v-if="currentImageUrl" class="pop-image" :src="currentImageUrl" mode="aspectFit" />
          <view v-else class="pop-emoji">{{ subjectEmoji }}</view>
          <view class="zoom-b">🔍 {{ currentViewLabel }} · {{ selectedPart?.shortName ?? '部位' }}</view>
        </view>
        <view class="pop-body">
          <view class="pop-name">{{ subjectName }} · {{ selectedPart?.name ?? '部位' }}</view>
          <view class="pop-tag">{{ config.label }} · 部位观察</view>
          <view class="pop-text">{{ selectedPart?.description ?? '点击上方标注点开始探索吧～' }}</view>
          <view class="audio-bar"><view class="audio-prog" :style="{ background: `linear-gradient(90deg,${config.primary},${config.light})` }" /></view>
        </view>
      </view>

      <FactCards :category="category" :facts="selectedPart?.facts ?? {}" />

      <view class="next" :style="{ background: `linear-gradient(135deg,${config.light},${config.primary})` }" @tap="nextPart">
        👉 下一个部位
      </view>
    </view>

    <PartDetailSheet :visible="sheetVisible" :part="selectedPart" :primary="config.primary" @close="sheetVisible = false" />
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import ApiErrorState from '@/components/ApiErrorState/index.vue'
import FactCards from '@/components/FactCards/index.vue'
import PartDetailSheet from '@/components/PartDetailSheet/index.vue'
import SubjectCanvas from '@/components/SubjectCanvas/index.vue'
import { useExplorerStore, type Category, type SubjectPart } from '@/store/explorerStore'
import request from '@/utils/request'
import { getCategoryConfig } from '@/utils/category'
import { vibrateShort } from '@/utils/feedback'

interface VisionApiPart {
  id: string
  name: string
  short_name: string
  color: string
  x: number
  y: number
  description: string
  facts: Record<string, string>
}

interface VisionResponse {
  success: boolean
  parts: VisionApiPart[]
}

const explorerStore = useExplorerStore()
const category = computed<Category>(() => explorerStore.currentSubject?.category ?? explorerStore.currentCategory)
const config = computed(() => getCategoryConfig(category.value))

const currentView = ref('front')
const selectedPartId = ref<string | null>(null)
const errorMessage = ref('')
const sheetVisible = ref(false)
const partsByView = ref<Record<string, SubjectPart[]>>({})

const subjectName = computed(() => explorerStore.currentSubject?.name ?? '探索对象')
const subjectNameEn = computed(() => explorerStore.currentSubject?.nameEn ?? 'unknown')
const subjectEmoji = computed(() => explorerStore.currentSubject?.emoji ?? config.value.emoji)
const subjectId = computed(() => explorerStore.currentSubject?.subjectId ?? null)

const allViews = computed(() => {
  const views = [...explorerStore.images.four, ...explorerStore.images.eight]
  if (views.length > 0) {
    return views
  }
  return [{ view: 'front', url: '', label: '正面' }]
})

const currentViewLabel = computed(() => allViews.value.find((item) => item.view === currentView.value)?.label ?? '当前')
const currentImageUrl = computed(() => allViews.value.find((item) => item.view === currentView.value)?.url ?? '')
const currentParts = computed(() => partsByView.value[currentView.value] ?? [])
const selectedPart = computed(() => currentParts.value.find((part) => part.id === selectedPartId.value) ?? currentParts.value[0] ?? null)

const pageVars = computed(() => ({
  '--primary': config.value.primary,
  '--light': config.value.light,
}))

function mapParts(raw: VisionApiPart[]): SubjectPart[] {
  return raw.map((item) => ({
    id: item.id,
    name: item.name,
    shortName: item.short_name,
    color: item.color,
    x: item.x,
    y: item.y,
    description: item.description,
    facts: item.facts,
  }))
}

function selectPart(partId: string) {
  vibrateShort()
  selectedPartId.value = partId
}

function handleMarkerSelect(part: SubjectPart) {
  vibrateShort()
  selectedPartId.value = part.id
  sheetVisible.value = true
}

function nextPart() {
  if (currentParts.value.length === 0) {
    return
  }
  vibrateShort()
  const index = currentParts.value.findIndex((item) => item.id === selectedPartId.value)
  const nextIndex = index < 0 ? 0 : (index + 1) % currentParts.value.length
  selectedPartId.value = currentParts.value[nextIndex].id
}

async function loadVisionForView(view: string, force = false) {
  if (!subjectId.value || !currentImageUrl.value) {
    return
  }
  if (!force && partsByView.value[view]?.length) {
    return
  }

  try {
    const result = await request<VisionResponse>({
      url: '/api/vision',
      method: 'POST',
      data: {
        image_url: currentImageUrl.value,
        name: subjectName.value,
        name_en: subjectNameEn.value,
        category: category.value,
        view,
        subject_id: subjectId.value,
      },
    })

    const mapped = mapParts(result.parts || [])
    partsByView.value = {
      ...partsByView.value,
      [view]: mapped,
    }

    if (!selectedPartId.value && mapped[0]) {
      selectedPartId.value = mapped[0].id
    }
  } catch (error) {
    console.error('[multiview-detail] vision failed:', error)
    errorMessage.value = '标注识别暂时没完成，我们再试一次吧～'
  }
}

async function switchView(view: string) {
  if (currentView.value === view) {
    return
  }
  vibrateShort()
  currentView.value = view
  selectedPartId.value = null
  await loadVisionForView(view)
  if (currentParts.value[0]) {
    selectedPartId.value = currentParts.value[0].id
  }
}

async function reloadCurrentView() {
  errorMessage.value = ''
  await loadVisionForView(currentView.value, true)
}

function goBack() {
  vibrateShort()
  uni.navigateBack()
}

onMounted(async () => {
  const pages = getCurrentPages() as unknown as Array<{ options?: Record<string, string> }>
  const options = pages[pages.length - 1]?.options ?? {}
  currentView.value = options.view || allViews.value[0]?.view || 'front'
  await loadVisionForView(currentView.value)
  if (currentParts.value[0]) {
    selectedPartId.value = currentParts.value[0].id
  }
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #fffbf0;
  padding-bottom: 16rpx;
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
  font-size: 22rpx;
  font-weight: 900;
  padding: 4rpx 10rpx;
  border-radius: 20rpx;
  color: #fff;
  background: var(--primary);
}

.view-tabs {
  white-space: nowrap;
  padding: 0 16rpx 8rpx;
}

.vtab {
  display: inline-flex;
  margin-right: 8rpx;
  padding: 10rpx 16rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 900;
  background: #f5edd8;
  color: #a07840;
}

.vtab.on {
  color: #fff;
}

.parts-strip {
  display: flex;
  gap: 8rpx;
  padding: 0 16rpx 8rpx;
  white-space: nowrap;
}

.pchip {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  padding: 9rpx 13rpx;
  border-radius: 14rpx;
  background: #fff;
  box-shadow: 0 3rpx 8rpx rgba(0, 0, 0, 0.07);
}

.pchip.active {
  border: 2rpx solid var(--primary);
}

.pdot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
}

.sec {
  padding: 4rpx 16rpx 8rpx;
  font-size: 24rpx;
  font-weight: 900;
  color: #3d2c00;
}

.detail-popup {
  margin: 0 16rpx;
  border-radius: 24rpx;
  overflow: hidden;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
}

.pop-img {
  width: 100%;
  height: 220rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.pop-image {
  width: 100%;
  height: 100%;
}

.pop-emoji {
  font-size: 80rpx;
}

.zoom-b {
  position: absolute;
  bottom: 10rpx;
  right: 12rpx;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 10rpx;
  font-size: 20rpx;
  font-weight: 900;
  color: #3d2c00;
  padding: 3rpx 9rpx;
}

.pop-body {
  background: #fff;
  padding: 14rpx 16rpx;
}

.pop-name {
  font-size: 30rpx;
  font-weight: 900;
  color: #3d2c00;
  margin-bottom: 4rpx;
}

.pop-tag {
  display: inline-block;
  font-size: 20rpx;
  font-weight: 900;
  padding: 3rpx 10rpx;
  border-radius: 20rpx;
  color: #fff;
  margin-bottom: 8rpx;
  background: var(--primary);
}

.pop-text {
  font-size: 24rpx;
  line-height: 1.7;
  color: #5a4020;
}

.audio-bar {
  margin: 10rpx 0 0;
  background: #f5edd8;
  border-radius: 20rpx;
  height: 7rpx;
  overflow: hidden;
}

.audio-prog {
  width: 48%;
  height: 100%;
  border-radius: 20rpx;
}

.next {
  margin: 12rpx 16rpx 0;
  height: 76rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 900;
  color: #3d2c00;
  box-shadow: 0 6rpx 16rpx rgba(0, 0, 0, 0.1);
}
</style>
