export function vibrateShort(type: 'light' | 'medium' | 'heavy' = 'light') {
  // #ifdef MP-WEIXIN
  try {
    const wxAny = wx as any
    if (wxAny && typeof wxAny.vibrateShort === 'function') {
      wxAny.vibrateShort({ type })
    }
  } catch (error) {
    console.warn('[feedback] vibrateShort failed:', error)
  }
  // #endif
}
