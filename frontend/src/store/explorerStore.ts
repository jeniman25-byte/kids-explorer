import { defineStore } from 'pinia'

export type Category = 'food' | 'animal' | 'plant'

export interface ViewImage {
  view: string
  url: string
  label: string
}

export interface SubjectPart {
  id: string
  name: string
  shortName: string
  color: string
  x: number
  y: number
  description: string
  facts: Record<string, string>
}

interface HistoryItem {
  id: string
  name: string
  emoji: string
  category: Category
  imageUrl: string
  timestamp: number
}

interface ExplorerState {
  currentCategory: Category

  currentSubject: {
    name: string
    nameEn: string
    emoji: string
    category: Category
    subCategory: string
    seed: number
    subjectId: number | null
  } | null

  images: { single: string; four: ViewImage[]; eight: ViewImage[] }
  parts: SubjectPart[]

  generating: {
    step: number
    fourProgress: number
    fourDone: boolean
    eightDone: boolean
    visionDone: boolean
  }

  currentPartId: string | null
  history: HistoryItem[]
}

const HISTORY_STORAGE_KEY = 'kids_explorer_history'

function loadHistory(): HistoryItem[] {
  const cached = uni.getStorageSync(HISTORY_STORAGE_KEY) as HistoryItem[] | ''
  if (!cached || !Array.isArray(cached)) {
    return []
  }
  return cached.slice(0, 20)
}

function saveHistory(history: HistoryItem[]) {
  uni.setStorageSync(HISTORY_STORAGE_KEY, history.slice(0, 20))
}

export const useExplorerStore = defineStore('explorer', {
  state: (): ExplorerState => ({
    currentCategory: 'food',
    currentSubject: null,
    images: {
      single: '',
      four: [],
      eight: [],
    },
    parts: [],
    generating: {
      step: 0,
      fourProgress: 0,
      fourDone: false,
      eightDone: false,
      visionDone: false,
    },
    currentPartId: null,
    history: loadHistory(),
  }),
  actions: {
    setCurrentCategory(category: Category) {
      this.currentCategory = category
    },
    setCurrentSubject(subject: ExplorerState['currentSubject']) {
      this.currentSubject = subject
      if (subject) {
        this.currentCategory = subject.category
      }
    },
    setSubjectId(subjectId: number | null) {
      if (!this.currentSubject) {
        return
      }
      this.currentSubject = {
        ...this.currentSubject,
        subjectId,
      }
    },
    setImages(images: ExplorerState['images']) {
      this.images = images
    },
    setFourImages(images: ViewImage[]) {
      this.images = {
        ...this.images,
        four: images,
      }
    },
    setEightImages(images: ViewImage[]) {
      this.images = {
        ...this.images,
        eight: images,
      }
    },
    resetImages() {
      this.images = {
        single: '',
        four: [],
        eight: [],
      }
    },
    setParts(parts: SubjectPart[]) {
      this.parts = parts
    },
    setGeneratingState(generating: ExplorerState['generating']) {
      this.generating = generating
    },
    setCurrentPartId(partId: string | null) {
      this.currentPartId = partId
    },
    addHistory(item: HistoryItem) {
      const deduped = this.history.filter((historyItem) => historyItem.id !== item.id)
      this.history = [item, ...deduped].slice(0, 20)
      saveHistory(this.history)
    },
    clearHistory() {
      this.history = []
      saveHistory(this.history)
    },
  },
})
