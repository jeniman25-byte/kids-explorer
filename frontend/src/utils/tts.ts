import request from '@/utils/request'

interface TtsResponse {
  success: boolean
  audio_base64: string
}

const ttsCache = new Map<string, string>()

function normalizeText(text: string): string {
  return text.trim().replace(/\s+/g, ' ')
}

function ensureApiToken() {
  const token = uni.getStorageSync('token') as string | undefined
  if (token) {
    return
  }
  const envToken = import.meta.env.VITE_APP_TOKEN as string | undefined
  uni.setStorageSync('token', envToken ?? 'your-random-secret-token')
}

export async function getTtsAudioBase64(text: string): Promise<string> {
  const normalized = normalizeText(text)
  if (!normalized) {
    throw new Error('TTS text is empty')
  }

  const cached = ttsCache.get(normalized)
  if (cached) {
    return cached
  }

  ensureApiToken()

  const result = await request<TtsResponse>({
    url: '/api/tts',
    method: 'POST',
    data: { text: normalized },
  })

  if (!result.success || !result.audio_base64) {
    throw new Error('TTS request failed')
  }

  ttsCache.set(normalized, result.audio_base64)
  return result.audio_base64
}

export function clearTtsCache() {
  ttsCache.clear()
}
