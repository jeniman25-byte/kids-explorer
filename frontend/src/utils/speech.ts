interface RecognizeResult {
  result?: string
}

interface WechatSIManager {
  start: (options: Record<string, unknown>) => void
  stop: () => void
  onRecognize: ((res: RecognizeResult) => void) | null
  onStop: ((res: RecognizeResult) => void) | null
  onError: ((error: unknown) => void) | null
}

interface PendingTask {
  resolve: (text: string) => void
  reject: (error: Error) => void
}

let manager: WechatSIManager | null = null
let pendingTask: PendingTask | null = null
let latestText = ''
let isRecording = false

function showRetryToast() {
  uni.showToast({
    title: '没听清，再说一次吧～',
    icon: 'none',
  })
}

function ensureManager(): WechatSIManager {
  if (manager) {
    return manager
  }

  // #ifdef MP-WEIXIN
  try {
    const plugin = (wx as any).requirePlugin('WechatSI')
    manager = plugin.getRecordRecognitionManager() as WechatSIManager
  } catch (error) {
    throw new Error(`WechatSI plugin init failed: ${String(error)}`)
  }
  // #endif

  // #ifndef MP-WEIXIN
  throw new Error('WechatSI only supports mp-weixin runtime')
  // #endif

  manager.onRecognize = (res: RecognizeResult) => {
    latestText = (res.result ?? '').trim()
  }

  manager.onStop = (res: RecognizeResult) => {
    isRecording = false
    const finalText = (res.result ?? latestText).trim()
    const task = pendingTask
    pendingTask = null

    if (!task) {
      return
    }

    if (finalText) {
      task.resolve(finalText)
      return
    }

    showRetryToast()
    task.reject(new Error('Speech recognition empty result'))
  }

  manager.onError = (error: unknown) => {
    isRecording = false
    const task = pendingTask
    pendingTask = null
    showRetryToast()
    task?.reject(new Error(`Speech recognition failed: ${String(error)}`))
  }

  return manager
}

export async function startSpeechRecord(): Promise<void> {
  if (isRecording) {
    return
  }

  const recordManager = ensureManager()
  latestText = ''
  isRecording = true

  recordManager.start({
    lang: 'zh_CN',
    duration: 30000,
  })
}

export async function stopSpeechRecord(): Promise<string> {
  if (!isRecording || !manager) {
    throw new Error('Speech recognition not started')
  }

  const result = new Promise<string>((resolve, reject) => {
    pendingTask = { resolve, reject }
  })

  manager.stop()
  return result
}

export function isSpeechRecording(): boolean {
  return isRecording
}
