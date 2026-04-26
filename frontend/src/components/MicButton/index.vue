<!-- 麦克风按钮：长按开始，松开结束 -->
<template>
  <view class="mic-area" :class="{ 'mic-area--disabled': disabled }">
    <view
      class="mic-rings"
      @longpress="handleLongPress"
      @touchend="handleTouchEnd"
      @touchcancel="handleTouchEnd"
    >
      <view
        v-for="(color, index) in ringPalette"
        :key="`${color}-${index}`"
        class="ring"
        :class="[`ring-${index + 1}`, { 'ring--active': active }]"
        :style="ringStyle(color)"
      />
      <view class="mic-btn" :style="buttonStyle">🎙️</view>
    </view>
    <view class="mic-hint">{{ hint }}</view>
  </view>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { vibrateShort } from '@/utils/feedback'

const props = withDefaults(
  defineProps<{
    primary: string
    light: string
    shadow: string
    hint: string
    ringColors: string[]
    active?: boolean
    disabled?: boolean
  }>(),
  {
    active: false,
    disabled: false,
  },
)

const emit = defineEmits<{
  (event: 'record-start'): void
  (event: 'record-end'): void
}>()

const ringPalette = computed(() => {
  if (props.ringColors.length >= 3) {
    return props.ringColors.slice(0, 3)
  }
  return [props.primary, props.primary, props.primary]
})

const buttonStyle = computed(() => ({
  backgroundImage: `linear-gradient(145deg,${props.light},${props.primary})`,
  boxShadow: `0 16rpx 48rpx ${props.shadow}`,
}))

function ringStyle(color: string) {
  return {
    borderColor: color,
  }
}

function handleLongPress() {
  if (props.disabled) {
    return
  }
  vibrateShort('medium')
  emit('record-start')
}

function handleTouchEnd() {
  if (props.disabled) {
    return
  }
  vibrateShort()
  emit('record-end')
}
</script>

<style scoped lang="scss">
.mic-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 22rpx;
}

.mic-area--disabled {
  opacity: 0.6;
}

.mic-rings {
  position: relative;
  width: 328rpx;
  height: 328rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ring {
  position: absolute;
  border-radius: 50%;
  border-style: solid;
  border-width: 6rpx;
  animation: pulse 2s ease-out infinite;
  animation-play-state: paused;
  transition: border-color 0.3s ease;
}

.ring--active {
  animation-play-state: running;
}

.ring-1 {
  width: 328rpx;
  height: 328rpx;
  opacity: 0.18;
}

.ring-2 {
  width: 264rpx;
  height: 264rpx;
  opacity: 0.28;
  animation-delay: 0.35s;
}

.ring-3 {
  width: 208rpx;
  height: 208rpx;
  opacity: 0.38;
  animation-delay: 0.7s;
}

.mic-btn {
  width: 196rpx;
  height: 196rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 82rpx;
  z-index: 2;
  transition: background-image 0.3s ease, box-shadow 0.3s ease;
}

.mic-hint {
  margin-top: 16rpx;
  font-size: 26rpx;
  color: var(--text-sub);
  font-weight: 700;
}

@keyframes pulse {
  0% {
    transform: scale(0.9);
    opacity: 0.38;
  }
  70% {
    transform: scale(1.12);
    opacity: 0;
  }
  100% {
    transform: scale(0.9);
    opacity: 0;
  }
}
</style>
