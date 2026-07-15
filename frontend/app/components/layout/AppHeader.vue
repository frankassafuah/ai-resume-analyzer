<script setup lang="ts">
import { Bell } from 'lucide-vue-next'

const notifications = useNotificationsStore()

onMounted(() => {
  notifications.fetch().catch(() => {})
})
</script>

<template>
  <header
    class="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background/80 px-4 backdrop-blur sm:px-6 lg:px-8"
  >
    <!-- Mobile logo (sidebar is hidden on small screens) -->
    <div class="lg:hidden">
      <SharedAppLogo />
    </div>

    <div class="ml-auto flex items-center gap-2">
      <NuxtLink
        to="/notifications"
        class="relative flex size-9 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
        aria-label="Notifications"
      >
        <Bell class="size-4" />
        <span
          v-if="notifications.unreadCount"
          class="absolute right-1.5 top-1.5 size-2 rounded-full bg-primary ring-2 ring-background"
        />
      </NuxtLink>
    </div>
  </header>
</template>
