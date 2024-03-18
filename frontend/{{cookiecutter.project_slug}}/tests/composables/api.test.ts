import { ref } from 'vue'
import { setActivePinia, createPinia } from 'pinia'
import { beforeEach, expect, test } from 'vitest'
import { wrapper } from '@/composables/use-api-wrapper.ts'
import { useApis } from '@/composables/use-apis.ts'

beforeEach(() => {
  // creates a fresh pinia and makes it active
  // Needed by useStores in wrapper
  setActivePinia(createPinia())
})

test(
  'Test api-wrapper & apis composables',
  async () => {
    const apis = useApis()
    const loading = ref(false)
    const apiResult = await wrapper(apis.test.callExemple(), loading) // May fail due to public API
    expect(apiResult.length !== 0).toBeTruthy()
  },
  { timeout: 8000 }
)
