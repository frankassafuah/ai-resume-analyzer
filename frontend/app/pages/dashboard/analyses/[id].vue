<script setup lang="ts">
import { CheckCircle2, XCircle } from 'lucide-vue-next'
import { computed, onBeforeUnmount, ref } from 'vue'
import { analysisService } from '~/services/analysis.service'
import type { Analysis } from '~/types'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const route = useRoute()
const id = route.params.id as string

const { data, pending, error, refresh } = useLoader<Analysis>(() => analysisService.get(id))

// Poll while the analysis is still running.
let timer: ReturnType<typeof setInterval> | null = null
const polling = ref(false)
watch(
  () => data.value?.status,
  (status) => {
    const running = status === 'pending' || status === 'processing'
    if (running && !timer) {
      polling.value = true
      timer = setInterval(refresh, 2000)
    } else if (!running && timer) {
      clearInterval(timer)
      timer = null
      polling.value = false
    }
  },
)
onBeforeUnmount(() => timer && clearInterval(timer))

const result = computed(() => data.value?.result_json ?? null)
</script>

<template>
  <div>
    <SharedPageHeader title="Analysis" description="Resume-vs-job match report">
      <template #actions>
        <Badge v-if="data" :variant="data.status === 'completed' ? 'success' : data.status === 'failed' ? 'destructive' : 'warning'">
          {{ data.status }}<span v-if="polling"> · refreshing</span>
        </Badge>
      </template>
    </SharedPageHeader>

    <SharedLoadingState v-if="pending && !data" :rows="3" />
    <SharedErrorState v-else-if="error" :message="error.message" @retry="refresh" />

    <div v-else-if="data" class="space-y-6">
      <!-- Running / failed states -->
      <Card v-if="data.status !== 'completed'" class="p-8 text-center">
        <p v-if="data.status === 'failed'" class="text-sm text-destructive">
          {{ data.error || 'Analysis failed.' }}
        </p>
        <p v-else class="text-sm text-muted-foreground">
          Analyzing your resume… this usually takes a few seconds.
        </p>
      </Card>

      <template v-else-if="result">
        <!-- Scores -->
        <div class="grid gap-4 sm:grid-cols-2">
          <Card class="p-6">
            <p class="text-sm text-muted-foreground">Job match score</p>
            <p class="mt-1 text-4xl font-semibold tracking-tight">{{ result.score }}%</p>
          </Card>
          <Card class="p-6">
            <p class="text-sm text-muted-foreground">ATS score</p>
            <p class="mt-1 text-4xl font-semibold tracking-tight">{{ result.ats_score }}%</p>
          </Card>
        </div>

        <Card class="p-6">
          <h3 class="mb-2 text-sm font-medium">Summary</h3>
          <p class="text-sm text-muted-foreground">{{ result.summary }}</p>
        </Card>

        <!-- Skills -->
        <div class="grid gap-4 sm:grid-cols-2">
          <Card class="p-6">
            <h3 class="mb-3 text-sm font-medium">Matching skills</h3>
            <div class="flex flex-wrap gap-1.5">
              <Badge v-for="s in result.matching_skills" :key="s" variant="success">{{ s }}</Badge>
              <p v-if="!result.matching_skills.length" class="text-sm text-muted-foreground">None</p>
            </div>
          </Card>
          <Card class="p-6">
            <h3 class="mb-3 text-sm font-medium">Missing skills</h3>
            <div class="flex flex-wrap gap-1.5">
              <Badge v-for="s in result.missing_skills" :key="s" variant="warning">{{ s }}</Badge>
              <p v-if="!result.missing_skills.length" class="text-sm text-muted-foreground">None</p>
            </div>
          </Card>
        </div>

        <!-- Strengths / weaknesses -->
        <div class="grid gap-4 sm:grid-cols-2">
          <Card class="p-6">
            <h3 class="mb-3 text-sm font-medium">Strengths</h3>
            <ul class="space-y-2">
              <li v-for="(s, i) in result.strengths" :key="i" class="flex gap-2 text-sm">
                <CheckCircle2 class="mt-0.5 size-4 shrink-0 text-emerald-500" /> {{ s }}
              </li>
            </ul>
          </Card>
          <Card class="p-6">
            <h3 class="mb-3 text-sm font-medium">Weaknesses</h3>
            <ul class="space-y-2">
              <li v-for="(w, i) in result.weaknesses" :key="i" class="flex gap-2 text-sm">
                <XCircle class="mt-0.5 size-4 shrink-0 text-amber-500" /> {{ w }}
              </li>
            </ul>
          </Card>
        </div>

        <Card class="p-6">
          <h3 class="mb-3 text-sm font-medium">Recommendations</h3>
          <ul class="list-disc space-y-1.5 pl-5 text-sm text-muted-foreground">
            <li v-for="(r, i) in result.recommendations" :key="i">{{ r }}</li>
          </ul>
        </Card>
      </template>
    </div>
  </div>
</template>
