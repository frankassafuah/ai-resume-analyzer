<script setup lang="ts">
import {
  FileText,
  LayoutDashboard,
  Briefcase,
  Sparkles,
  Settings,
} from 'lucide-vue-next'
import type { Component } from 'vue'

interface NavItem {
  label: string
  to: string
  icon: Component
}

const nav: NavItem[] = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Resumes', to: '/resumes', icon: FileText },
  { label: 'Jobs', to: '/jobs', icon: Briefcase },
  { label: 'Analyses', to: '/analysis', icon: Sparkles },
  { label: 'Settings', to: '/settings', icon: Settings },
]

const route = useRoute()
function isActive(to: string): boolean {
  return to === '/dashboard' ? route.path === to : route.path.startsWith(to)
}
</script>

<template>
  <aside
    class="fixed inset-y-0 left-0 z-40 hidden w-60 flex-col border-r bg-background lg:flex"
  >
    <div class="flex h-14 items-center border-b px-5">
      <SharedAppLogo />
    </div>

    <nav class="flex-1 space-y-0.5 overflow-y-auto p-3">
      <NuxtLink
        v-for="item in nav"
        :key="item.to"
        :to="item.to"
        :class="[
          'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
          isActive(item.to)
            ? 'bg-accent text-accent-foreground'
            : 'text-muted-foreground hover:bg-accent/50 hover:text-foreground',
        ]"
      >
        <component :is="item.icon" class="size-4" />
        {{ item.label }}
      </NuxtLink>
    </nav>

    <div class="border-t p-3">
      <LayoutUserMenu />
    </div>
  </aside>
</template>
