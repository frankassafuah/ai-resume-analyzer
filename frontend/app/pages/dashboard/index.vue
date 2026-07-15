<script setup lang="ts">
import { FileText, Briefcase, Sparkles, Target } from 'lucide-vue-next'
import { computed } from 'vue'
import { analysisService } from '~/services/analysis.service'
import { jobService } from '~/services/job.service'
import { resumeService } from '~/services/resume.service'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const auth = useAuthStore()

const { data, pending, error, refresh } = useLoader(async () => {
  const [resumes, jobs, analyses] = await Promise.all([
    resumeService.list({ page_size: 1 }),
    jobService.list({ page_size: 1 }),
    analysisService.list({ page_size: 8 }),
  ])
  const completed = analyses.results.filter((a) => a.status === 'completed' && a.score != null)
  const avg = completed.length
    ? Math.round(completed.reduce((s, a) => s + (a.score || 0), 0) / completed.length)
    : null
  return {
    resumes: resumes.pagination?.count ?? resumes.results.length,
    jobs: jobs.pagination?.count ?? jobs.results.length,
    analyses: analyses.pagination?.count ?? analyses.results.length,
    avgScore: avg,
    recent: analyses.results,
  }
})

// Oldest → newest scores for the trend chart.
const trend = computed(() =>
  (data.value?.recent ?? [])
    .filter((a) => a.status === 'completed' && a.score != null)
    .map((a) => a.score as number)
    .reverse(),
)

const statusVariant: Record<string, string> = {
  completed: 'success',
  processing: 'warning',
  pending: 'secondary',
  failed: 'destructive',
}
</script>

<template>
  <div>
    <SharedPageHeader
      :title="`Welcome back${auth.user?.first_name ? ', ' + auth.user.first_name : ''}`"
      description="Your resume analysis at a glance."
    >
      <template #actions>
        <Button as-child><NuxtLink to="/analysis">New analysis</NuxtLink></Button>
      </template>
    </SharedPageHeader>

    <SharedErrorState v-if="error" :message="error.message" @retry="refresh" />

    <template v-else>
      <!-- Stats -->
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <template v-if="pending">
          <Skeleton v-for="i in 4" :key="i" class="h-26 rounded-xl" />
        </template>
        <template v-else-if="data">
          <SharedStatCard label="Resumes" :value="data.resumes" :icon="FileText" />
          <SharedStatCard label="Job descriptions" :value="data.jobs" :icon="Briefcase" />
          <SharedStatCard label="Analyses" :value="data.analyses" :icon="Sparkles" />
          <SharedStatCard
            label="Avg. match score"
            :value="data.avgScore != null ? `${data.avgScore}%` : '—'"
            :icon="Target"
          />
        </template>
      </div>

      <!-- Charts + recent -->
      <div class="mt-6 grid gap-4 lg:grid-cols-3">
        <!-- Avg score ring -->
        <Card class="flex flex-col items-center justify-center p-6">
          <h3 class="mb-4 self-start text-sm font-medium text-muted-foreground">Average match</h3>
          <ChartsScoreRing v-if="data?.avgScore != null" :value="data.avgScore" />
          <p v-else class="py-8 text-sm text-muted-foreground">Run an analysis to see your score.</p>
        </Card>

        <!-- Trend -->
        <Card class="flex flex-col p-6 lg:col-span-2">
          <h3 class="mb-4 text-sm font-medium text-muted-foreground">Recent scores</h3>
          <div class="flex flex-1 items-end">
            <ChartsMiniBars :values="trend" :height="120" class="w-full" />
          </div>
        </Card>
      </div>

      <!-- Recent analyses -->
      <div class="mt-6">
        <h2 class="mb-3 text-sm font-medium text-muted-foreground">Recent analyses</h2>
        <SharedLoadingState v-if="pending" :rows="3" />
        <SharedEmptyState
          v-else-if="data && !data.recent.length"
          :icon="Sparkles"
          title="No analyses yet"
          description="Upload a resume and a job description to run your first analysis."
        />
        <Card v-else-if="data" class="divide-y p-0">
          <NuxtLink
            v-for="a in data.recent"
            :key="a.id"
            :to="`/analysis/${a.id}`"
            class="flex items-center justify-between px-5 py-3.5 transition-colors hover:bg-accent/40"
          >
            <div class="min-w-0">
              <p class="truncate text-sm font-medium">
                Analysis · {{ new Date(a.created_at).toLocaleDateString() }}
              </p>
              <p class="text-xs text-muted-foreground">
                {{ a.status === 'completed' ? `Match ${a.score}% · ATS ${a.ats_score}%` : a.status }}
              </p>
            </div>
            <Badge :variant="(statusVariant[a.status] as any)">{{ a.status }}</Badge>
          </NuxtLink>
        </Card>
      </div>
    </template>
  </div>
</template>
