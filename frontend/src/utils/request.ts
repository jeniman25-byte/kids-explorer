interface RequestOptions<T = unknown> {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  data?: Record<string, unknown> | string | ArrayBuffer
  header?: Record<string, string>
}

const baseURL = import.meta.env.VITE_API_BASE_URL ?? ''

export function request<T = unknown>(options: RequestOptions): Promise<T> {
  const token = uni.getStorageSync('token') as string | undefined

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${baseURL}${options.url}`,
      method: options.method ?? 'GET',
      data: options.data,
      timeout: 15000,
      header: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token ?? ''}`,
        ...(options.header ?? {}),
      },
      success: (res) => {
        const statusCode = res.statusCode ?? 500
        if (statusCode >= 200 && statusCode < 300) {
          resolve(res.data as T)
          return
        }

        console.error('[request] HTTP error:', {
          url: options.url,
          statusCode,
          data: res.data,
        })
        reject(res)
      },
      fail: (err) => {
        console.error('[request] Network error:', {
          url: options.url,
          error: err,
        })
        reject(err)
      },
    })
  })
}

export default request
