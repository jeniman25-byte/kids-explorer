<!-- 图鉴列表通用页（PAGE 12/13/14） -->
<template>
  <view class="page" :style="pageVars">
    <view class="top-bar">
      <view class="back-btn" @tap="goBack">←</view>
      <view class="title">{{ config.label }}图鉴</view>
      <view class="cat-pill">{{ config.label }}</view>
    </view>

    <SearchBar v-model="keyword" :placeholder="searchPlaceholder" />
    <FilterRow :tags="config.filterTags" :active-tag="activeTag" :primary="config.primary" @change="handleFilterChange" />

    <ApiErrorState
      v-if="errorMessage"
      title="哎呀，图鉴小本本掉地上了"
      :message="errorMessage"
      @retry="loadSubjects"
    />

    <view v-else-if="loading" class="loading">正在翻开图鉴中…</view>

    <view v-else-if="filteredItems.length === 0" class="empty-wrap">
      <view class="empty-emoji">🧭</view>
      <view class="empty-main">暂时没找到这个对象</view>
      <view class="empty-sub">换个关键词试试，或者清空筛选条件吧～</view>
    </view>

    <SubjectGrid
      v-else
      :items="filteredItems"
      :light="config.light"
      :primary="config.primary"
      @select="handleSelectSubject"
    />
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import ApiErrorState from '@/components/ApiErrorState/index.vue'
import FilterRow from '@/components/FilterRow/index.vue'
import SearchBar from '@/components/SearchBar/index.vue'
import SubjectGrid, { type SubjectGridItem } from '@/components/SubjectGrid/index.vue'
import { useExplorerStore, type Category, type ViewImage } from '@/store/explorerStore'
import request from '@/utils/request'
import { vibrateShort } from '@/utils/feedback'
import { getCategoryConfig } from '@/utils/category'

interface SubjectApiItem {
  id: number
  name: string
  name_en: string
  emoji: string
  category: Category
  sub_category: string
  explored: boolean
  image_url: string
  parts_preview: string[]
}

interface SubjectListResponse {
  success: boolean
  items: SubjectApiItem[]
}

interface ImageStatusResponse {
  success: boolean
  subject_id: number
  images: {
    four: ViewImage[]
    eight: ViewImage[]
  }
}

const props = defineProps<{
  category: Category
}>()

const explorerStore = useExplorerStore()
const config = computed(() => getCategoryConfig(props.category))

const loading = ref(false)
const errorMessage = ref('')
const keyword = ref('')
const activeTag = ref('全部')
const listItems = ref<SubjectApiItem[]>([])

const searchPlaceholder = computed(() => {
  if (props.category === 'food') return '搜索水果、蔬菜、零食…'
  if (props.category === 'animal') return '搜索陆地、海洋、昆虫…'
  return '搜索花朵、树木、叶片…'
})

const pageVars = computed(() => ({
  '--primary': config.value.primary,
  '--light': config.value.light,
  '--dark': config.value.dark,
}))

const filteredItems = computed<SubjectGridItem[]>(() => {
  const key = keyword.value.trim()
  return listItems.value
    .filter((item) => {
      const filterByTag = activeTag.value === '全部' || item.sub_category === activeTag.value
      const filterByKeyword = !key || item.name.includes(key)
      return filterByTag && filterByKeyword
    })
    .map((item) => ({
      id: item.id,
      name: item.name,
      emoji: item.emoji,
      explored: item.explored,
      partsPreviewText: item.parts_preview.length > 0 ? item.parts_preview.join('、') : '等待探索',
    }))
})

async function loadSubjects() {
  loading.value = true
  errorMessage.value = ''

  try {
    const res = await request<SubjectListResponse>({
      url: `/api/subjects?category=${props.category}`,
      method: 'GET',
    })
    listItems.value = res.items ?? []
  } catch (error) {
    console.error('[subjects] load failed:', error)
    errorMessage.value = '网络有点慢，图鉴还没翻开，我们再试一次吧～'
  } finally {
    loading.value = false
  }
}

function handleFilterChange(tag: string) {
  activeTag.value = tag
}

function goBack() {
  vibrateShort()
  uni.navigateBack({
    fail: () => {
      uni.switchTab({
        url: '/pages/index/index',
      })
    },
  })
}

async function handleSelectSubject(item: SubjectGridItem) {
  const matched = listItems.value.find((candidate) => candidate.id === item.id)
  if (!matched) {
    return
  }

  explorerStore.setCurrentSubject({
    name: matched.name,
    nameEn: matched.name_en,
    emoji: matched.emoji,
    category: matched.category,
    subCategory: matched.sub_category,
    seed: Math.floor(Math.random() * 90000) + 10000,
    subjectId: matched.id,
  })
  explorerStore.resetImages()

  try {
    const status = await request<ImageStatusResponse>({
      url: `/api/image/status/${matched.id}`,
      method: 'GET',
    })

    explorerStore.setFourImages(status.images.four ?? [])
    explorerStore.setEightImages(status.images.eight ?? [])
  } catch (error) {
    console.error('[subjects] preload image status failed:', error)
  }

  uni.navigateTo({
    url: `/pages/${props.category}/explore/index`,
  })
}

onMounted(() => {
  explorerStore.setCurrentCategory(props.category)
  void loadSubjects()
})
</script>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  background: #fffbf0;
  padding: 12rpx 0 20rpx;
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

.title {
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

.loading {
  margin: 30rpx 32rpx 0;
  font-size: 24rpx;
  color: var(--text-sub);
  text-align: center;
}

.empty-wrap {
  margin: 24rpx 32rpx 0;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 8rpx 20rpx var(--surface-shadow);
  padding: 24rpx 20rpx;
  text-align: center;
}

.empty-emoji {
  font-size: 56rpx;
}

.empty-main {
  margin-top: 8rpx;
  font-size: 30rpx;
  color: var(--text-main);
  font-weight: 900;
}

.empty-sub {
  margin-top: 8rpx;
  font-size: 23rpx;
  color: var(--text-sub);
}
</style>
