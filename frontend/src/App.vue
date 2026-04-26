<template>
  <view class="app-root">
    <slot />
  </view>
</template>

<script setup lang="ts">
// App 根组件
</script>

<style lang="scss">
page {
  --text-main: #3d2c00;
  --text-sub: #a07840;
  --surface: #ffffff;
  --surface-shadow: rgba(0, 0, 0, 0.08);
  --color-white: #ffffff;
  background: var(--surface);
  color: var(--text-main);
}

.app-root {
  min-height: 100vh;
}
</style>
