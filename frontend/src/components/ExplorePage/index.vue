<!-- 探索页通用容器（PAGE 6/7/8） -->
<template>
  <view class="explore-page" :style="pageVars">
    <view class="top-bar">
      <view class="back-btn" @tap="goBack">←</view>
      <view class="page-title">{{ subjectName }} {{ subjectEmoji }}</view>
      <view class="cat-pill">{{ config.label }}</view>
    </view>

    <view class="hero-wrap">
      <SubjectCanvas :image-url="currentImageUrl" :parts="parts" @select="handleSelectPart" />
    </view>

    <view class="section-title">点击部位了解更多</view>
    <PartChipGrid :parts="parts" :selected-part-id="selectedPartId" @select="handleSelectPart" />
    <view class="view-desc">{{ viewDescription }}</view>
    <InfoRow :category="props.category" :info="infoRow" />
    <ActionBar :primary="config.primary" @intro="openCurrentPartDetail" @retry="retryExplore" @multiview="openMultiview" />

    <PartDetailSheet
      :visible="sheetVisible"
      :part="selectedPart"
      :primary="config.primary"
      @close="sheetVisible = false"
    />
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import ActionBar from '@/components/ActionBar/index.vue'
import InfoRow from '@/components/InfoRow/index.vue'
import PartChipGrid from '@/components/PartChipGrid/index.vue'
import PartDetailSheet from '@/components/PartDetailSheet/index.vue'
import SubjectCanvas from '@/components/SubjectCanvas/index.vue'
import { useExplorerStore, type SubjectPart } from '@/store/explorerStore'
import request from '@/utils/request'
import { getCategoryConfig, type Category } from '@/utils/category'

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
  view_description: string
  info_row: Record<string, string>
}

const MARKER_COLORS = ['#FFB347', '#4FC3F7', '#66BB6A', '#F06292']

const props = defineProps<{
  category: Category
}>()

const explorerStore = useExplorerStore()
const config = computed(() => getCategoryConfig(props.category))

const parts = ref<SubjectPart[]>([])
const infoRow = ref<Record<string, string>>({})
const viewDescription = ref('正在观察这个对象的关键部位～')
const sheetVisible = ref(false)
const selectedPartId = ref<string | null>(null)

const subjectName = computed(() => explorerStore.currentSubject?.name ?? config.value.quickCards[0].name)
const subjectEmoji = computed(() => explorerStore.currentSubject?.emoji ?? config.value.emoji)
const subjectId = computed(() => explorerStore.currentSubject?.subjectId ?? null)
const subjectNameEn = computed(() => explorerStore.currentSubject?.nameEn ?? config.value.quickCards[0].name)

const currentImageUrl = computed(() => {
  const front = explorerStore.images.four.find((item) => item.view === 'front')
  return front?.url ?? explorerStore.images.four[0]?.url ?? ''
})

const selectedPart = computed(() => parts.value.find((part) => part.id === selectedPartId.value) ?? null)

const pageVars = computed(() => ({
  '--primary': config.value.primary,
  '--light': config.value.light,
  '--dark': config.value.dark,
}))

function ensureApiToken() {
  const token = uni.getStorageSync('token') as string | undefined
  if (token) {
    return
  }
  const envToken = import.meta.env.VITE_APP_TOKEN as string | undefined
  uni.setStorageSync('token', envToken ?? 'your-random-secret-token')
}

function buildFallbackParts(): SubjectPart[] {
  const labels: Record<Category, string[]> = {
    food: ['皮', '肉', '柄', '尖'],
    animal: ['耳', '眼', '爪', '尾'],
    plant: ['瓣', '蕊', '叶', '枝'],
  }

  const names: Record<Category, string[]> = {
    food: ['外皮', '果肉', '果柄', '果尖'],
    animal: ['耳朵', '眼睛', '爪子', '尾巴'],
    plant: ['花瓣', '花蕊', '叶子', '花枝'],
  }

  const points = [
    { x: 0.3, y: 0.25 },
    { x: 0.62, y: 0.36 },
    { x: 0.35, y: 0.72 },
    { x: 0.72, y: 0.66 },
  ]

  return points.map((point, idx) => {
    const key = config.value.factsKeys
    const name = names[props.category][idx]
    return {
      id: `${props.category}_fallback_${idx}`,
      name,
      shortName: labels[props.category][idx],
      color: MARKER_COLORS[idx],
      x: point.x,
      y: point.y,
      description: `${subjectName.value}的${name}有很多值得观察的小细节。`,
      facts: {
        [key[0]]: `${subjectName.value}的${key[0]}特点`,
        [key[1]]: `${subjectName.value}的${key[1]}信息`,
        [key[2]]: `${subjectName.value}的${key[2]}知识`,
      },
    }
  })
}

function toPartList(rawParts: VisionApiPart[]): SubjectPart[] {
  return rawParts.slice(0, 4).map((part, idx) => ({
    id: part.id,
    name: part.name,
    shortName: (part.short_name || part.name || '?').slice(0, 1),
    color: part.color || MARKER_COLORS[idx % MARKER_COLORS.length],
    x: Math.max(0.05, Math.min(0.95, Number(part.x) || 0.5)),
    y: Math.max(0.05, Math.min(0.95, Number(part.y) || 0.5)),
    description: part.description,
    facts: part.facts ?? {},
  }))
}

function hydrateFallback() {
  const fallback = buildFallbackParts()
  parts.value = fallback
  selectedPartId.value = fallback[0]?.id ?? null
  explorerStore.setParts(fallback)
  explorerStore.setCurrentPartId(selectedPartId.value)
  infoRow.value = { ...(fallback[0]?.facts ?? {}) }
  viewDescription.value = `从这个视角看${subjectName.value}，我们可以找到几个代表性的部位。`
}

async function fetchVision() {
  if (!subjectId.value || !currentImageUrl.value) {
    hydrateFallback()
    return
  }

  ensureApiToken()

  try {
    const result = await request<VisionResponse>({
      url: '/api/vision',
      method: 'POST',
      data: {
        image_url: currentImageUrl.value,
        name: subjectName.value,
        name_en: subjectNameEn.value,
        category: props.category,
        view: 'front',
        subject_id: subjectId.value,
      },
    })

    const nextParts = toPartList(result.parts || [])
    parts.value = nextParts.length > 0 ? nextParts : buildFallbackParts()
    selectedPartId.value = parts.value[0]?.id ?? null
    explorerStore.setParts(parts.value)
    explorerStore.setCurrentPartId(selectedPartId.value)
    infoRow.value = Object.keys(result.info_row || {}).length > 0 ? result.info_row : { ...(parts.value[0]?.facts ?? {}) }
    viewDescription.value = result.view_description || `从这个视角看${subjectName.value}，可以观察到关键部位。`
  } catch (error) {
    console.error('[vision] request failed:', error)
    hydrateFallback()
    uni.showToast({
      title: '部位识别失败，先看示例点位',
      icon: 'none',
    })
  }
}

function handleSelectPart(part: SubjectPart) {
  selectedPartId.value = part.id
  explorerStore.setCurrentPartId(part.id)
  sheetVisible.value = true
}

function goBack() {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({
        url: '/pages/index/index',
      })
    },
  })
}

function openCurrentPartDetail() {
  const target = selectedPartId.value ?? parts.value[0]?.id
  if (!target) {
    return
  }
  uni.navigateTo({
    url: `/pages/${props.category}/detail/index?partId=${encodeURIComponent(target)}`,
  })
}

function retryExplore() {
  uni.navigateTo({
    url: `/pages/${props.category}/index/index`,
  })
}

function openMultiview() {
  uni.navigateTo({
    url: '/pages/multiview/index',
  })
}

onMounted(() => {
  explorerStore.setCurrentCategory(props.category)
  void fetchVision()
})
</script>

<style scoped lang="scss">
.explore-page {
  min-height: 100vh;
  padding: 12rpx 0 30rpx;
  background: #fffbf0;
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
  color: var(--dark);
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

.hero-wrap {
  margin: 0 20rpx;
  border-radius: 42rpx;
  padding: 16rpx 0;
  background: linear-gradient(135deg, var(--light), #ffffff);
}

.section-title {
  margin: 10rpx 32rpx 12rpx;
  font-size: 24rpx;
  color: var(--text-sub);
  font-weight: 800;
}

.view-desc {
  margin: 10rpx 32rpx 0;
  font-size: 23rpx;
  color: #8a6a42;
  line-height: 1.6;
}
</style>
