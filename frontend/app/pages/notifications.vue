<script setup lang="ts">
import { Bell } from 'lucide-vue-next'
import { onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const store = useNotificationsStore()
onMounted(() => store.fetch())
</script>

<template>
  <div>
    <SharedPageHeader title="Notifications">
      <template #actions>
        <Button
          v-if="store.unreadCount"
          variant="outline"
          size="sm"
          @click="store.markAllRead()"
        >
          Mark all read
        </Button>
      </template>
    </SharedPageHeader>

    <SharedLoadingState v-if="store.loading" :rows="3" />
    <SharedEmptyState
      v-else-if="!store.items.length"
      :icon="Bell"
      title="No notifications"
      description="You're all caught up."
    />
    <Card v-else class="divide-y p-0">
      <button
        v-for="n in store.items"
        :key="n.id"
        class="flex w-full items-start gap-3 px-5 py-3.5 text-left transition-colors hover:bg-accent/40"
        @click="!n.is_read && store.markRead(n.id)"
      >
        <span
          class="mt-1.5 size-2 shrink-0 rounded-full"
          :class="n.is_read ? 'bg-transparent' : 'bg-primary'"
        />
        <div class="min-w-0 flex-1">
          <p class="text-sm font-medium">{{ n.title }}</p>
          <p class="text-sm text-muted-foreground">{{ n.message }}</p>
          <p class="mt-0.5 text-xs text-muted-foreground">
            {{ new Date(n.created_at).toLocaleString() }}
          </p>
        </div>
      </button>
    </Card>
  </div>
</template>
