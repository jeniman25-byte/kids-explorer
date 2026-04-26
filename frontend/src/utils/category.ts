// utils/category.ts
export type Category = 'food' | 'animal' | 'plant'

export const CATEGORY_CONFIG = {
  food: {
    label: '食物', emoji: '🍎',
    primary: '#FFB347', light: '#FFF3CC', dark: '#E65100',
    bgGradient: 'linear-gradient(160deg,#FFF8E7,#FFF1CC,#FFE0A3)',
    micShadow:  'rgba(255,179,71,0.52)',
    hintText:    '说出你想认识的食物吧！',
    hintExample: '试试说"香蕉长什么样"',
    guideTitle:  '食物探索重点',
    guideText:   '更适合展示颜色、口感、果皮、果核等结构。',
    factsKeys:   ['颜色', '口感', '吃法'],
    factsIcons:  ['🎨', '👅', '🍽️'],
    filterTags:  ['全部', '水果', '蔬菜', '主食', '甜品'],
    quickCards: [
      { emoji: '🍌', name: '香蕉',   desc: '看看果皮和果肉' },
      { emoji: '🍉', name: '西瓜',   desc: '看看瓜皮和籽' },
      { emoji: '🥕', name: '胡萝卜', desc: '看看根部和叶子' },
    ],
  },
  animal: {
    label: '动物', emoji: '🐼',
    primary: '#66BB6A', light: '#E8F5E9', dark: '#2E7D32',
    bgGradient: 'linear-gradient(160deg,#F1FFF1,#E8F5E9,#DCEDC8)',
    micShadow:  'rgba(102,187,106,0.5)',
    hintText:    '说出你想认识的动物吧！',
    hintExample: '试试说"熊猫长什么样"',
    guideTitle:  '动物探索重点',
    guideText:   '更适合展示耳朵、眼睛、尾巴、花纹和习性知识。',
    factsKeys:   ['颜色', '习性', '趣味'],
    factsIcons:  ['🎨', '🐾', '💡'],
    filterTags:  ['全部', '陆地', '海洋', '天空', '昆虫'],
    quickCards: [
      { emoji: '🐼', name: '熊猫', desc: '看黑眼圈和爪子' },
      { emoji: '🦁', name: '狮子', desc: '看鬃毛和尾巴' },
      { emoji: '🦋', name: '蝴蝶', desc: '看翅膀花纹' },
    ],
  },
  plant: {
    label: '花草', emoji: '🌸',
    primary: '#EC407A', light: '#FCE4EC', dark: '#880E4F',
    bgGradient: 'linear-gradient(160deg,#FFF0F5,#FCE4EC,#F8BBD0)',
    micShadow:  'rgba(236,64,122,0.45)',
    hintText:    '说出你想认识的花草吧！',
    hintExample: '试试说"樱花长什么样"',
    guideTitle:  '花草探索重点',
    guideText:   '更适合展示花瓣、叶子、花蕊、枝干和香味特点。',
    factsKeys:   ['颜色', '气味', '特征'],
    factsIcons:  ['🎨', '👃', '🍃'],
    filterTags:  ['全部', '花朵', '树木', '叶子', '草本'],
    quickCards: [
      { emoji: '🌸', name: '樱花',   desc: '看花瓣和花蕊' },
      { emoji: '🌻', name: '向日葵', desc: '看花盘和种子' },
      { emoji: '🎍', name: '竹子',   desc: '看竹节和叶片' },
    ],
  },
} as const

export const getCategoryConfig = (cat: Category) => CATEGORY_CONFIG[cat]
