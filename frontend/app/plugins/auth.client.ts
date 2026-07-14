// Restore the session from storage before the app renders (SPA).
export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  await auth.init()
})
