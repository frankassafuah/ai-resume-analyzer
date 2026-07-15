export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore()
  await auth.init()
  if (!auth.isAuthenticated) {
    return navigateTo({ path: '/auth/login', query: { redirect: to.fullPath } })
  }
})
