<script setup lang="ts">
import { RefreshCw } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

// M0 smoke test: confirm the SPA can reach the Django /health endpoint.
const config = useRuntimeConfig()

interface Health {
  status: string
  checks: Record<string, boolean>
}

const { data: health, error, refresh, status } = await useFetch<Health>(
  '/health/',
  { baseURL: config.public.apiBase, lazy: true },
)
</script>

<template>
  <main class="mx-auto max-w-xl px-4 py-16">
    <div class="space-y-6">
      <div>
        <h1 class="text-3xl font-bold tracking-tight">AI Resume Analyzer</h1>
        <p class="text-muted-foreground">
          M0 foundation — frontend ↔ API connectivity check.
        </p>
      </div>

      <Card>
        <CardHeader>
          <div class="flex items-center justify-between">
            <div>
              <CardTitle>API health</CardTitle>
              <CardDescription>GET /health/ on the Django API</CardDescription>
            </div>
            <Button
              size="sm"
              variant="outline"
              :disabled="status === 'pending'"
              @click="refresh()"
            >
              <RefreshCw class="size-4" :class="{ 'animate-spin': status === 'pending' }" />
              Re-check
            </Button>
          </div>
        </CardHeader>

        <CardContent>
          <p v-if="error" class="text-sm text-destructive">
            Cannot reach API: {{ String(error) }}
          </p>
          <div v-else-if="health" class="space-y-3">
            <span
              class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium"
              :class="
                health.status === 'ok'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-destructive text-destructive-foreground'
              "
            >
              {{ health.status }}
            </span>
            <ul class="text-sm">
              <li v-for="(ok, name) in health.checks" :key="name">
                {{ name }}: {{ ok ? '✅' : '❌' }}
              </li>
            </ul>
          </div>
          <p v-else class="text-sm text-muted-foreground">Checking…</p>
        </CardContent>
      </Card>
    </div>
  </main>
</template>
