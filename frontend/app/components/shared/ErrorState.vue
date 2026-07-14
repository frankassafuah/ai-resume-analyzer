<script setup lang="ts">
import { AlertCircle } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

defineProps<{ message?: string }>()
defineEmits<{ (e: 'retry'): void }>()
</script>

<template>
  <div
    class="flex flex-col items-center justify-center rounded-lg border border-destructive/30 bg-destructive/5 px-6 py-12 text-center"
  >
    <AlertCircle class="mb-3 size-8 text-destructive" />
    <p class="text-sm font-medium">Something went wrong</p>
    <p class="mt-1 max-w-sm text-sm text-muted-foreground">
      {{ message || 'Please try again.' }}
    </p>
    <Button variant="outline" size="sm" class="mt-5" @click="$emit('retry')">
      Retry
    </Button>
  </div>
</template>
