<script setup lang="ts">
import { TooltipProvider } from 'reka-ui'
import { Toaster } from '@/components/ui/sonner'

useHead({
  titleTemplate: (chunk) => (chunk ? `${chunk} · Resume Analyzer` : 'AI Resume Analyzer'),
})
</script>

<template>
  <NuxtRouteAnnouncer />
  <NuxtLoadingIndicator :height="2" color="var(--primary)" />
  <Toaster rich-colors />
  <TooltipProvider :delay-duration="200">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </TooltipProvider>
</template>
