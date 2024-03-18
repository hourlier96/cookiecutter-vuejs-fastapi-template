export const APISettings = {
  baseURL: import.meta.env.VITE_BASE_URL || 'https://animechan.xyz/api',
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json'
  }
}

export const TEST_PREFIX = 'quotes'
