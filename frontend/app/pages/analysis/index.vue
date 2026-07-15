<script setup lang="ts">
import { Sparkles, Plus } from 'lucide-vue-next'
import { ref } from 'vue'
import { analysisService } from '~/services/analysis.service'
import { jobService } from '~/services/job.service'
import { resumeService } from '~/services/resume.service'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Label } from '@/components/ui/label'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const toast = useToast()
const showForm = ref(false)
const resumeId = ref('')
const jobId = ref('')

const { data, pending, error, refresh } = useLoader(() => analysisService.list())
const { data: options } = useLoader(async () => ({
  resumes: (await resumeService.list({ page_size: 100 })).results,
  jobs: (await jobService.list({ page_size: 100 })).results,
}))

const { run: create, pending: creating } = useAsyncAction(async () => {
  if (!resumeId.value || !jobId.value) {
    toast.error('Pick a resume and a job')
    return
  }
  const analysis = await analysisService.create({ resume_id: resumeId.value, job_id: jobId.value })
  toast.success('Analysis started', 'This runs in the background.')
  showForm.value = false
  await refresh()
  await navigateTo(`/analysis/${analysis.id}`)
})

const selectClass =
  'flex h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50'
const statusVariant: Record<string, string> = {
  completed: 'success',
  processing: 'warning',
  pending: 'secondary',
  failed: 'destructive',
}
</script>

<template>
  <div>
    <SharedPageHeader title="Analyses" description="Resume-vs-job match reports.">
      <template #actions>
        <Button @click="showForm = !showForm"><Plus class="size-4" /> New analysis</Button>
      </template>
    </SharedPageHeader>

    <Card v-if="showForm" class="mb-6 p-5">
      <form class="grid gap-4 sm:grid-cols-2" @submit.prevent="create()">
        <div class="space-y-2">
          <Label>Resume</Label>
          <select v-model="resumeId" :class="selectClass">
            <option value="" disabled>Select a resume…</option>
            <option v-for="r in options?.resumes" :key="r.id" :value="r.id">{{ r.title }}</option>
          </select>
        </div>
        <div class="space-y-2">
          <Label>Job description</Label>
          <select v-model="jobId" :class="selectClass">
            <option value="" disabled>Select a job…</option>
            <option v-for="j in options?.jobs" :key="j.id" :value="j.id">
              {{ j.job_title }} — {{ j.company_name }}
            </option>
          </select>
        </div>
        <div class="flex items-center gap-2 sm:col-span-2">
          <Button type="submit" :disabled="creating">
            {{ creating ? 'Starting…' : 'Run analysis' }}
          </Button>
          <Button type="button" variant="ghost" @click="showForm = false">Cancel</Button>
        </div>
      </form>
    </Card>

    <SharedLoadingState v-if="pending" />
    <SharedErrorState v-else-if="error" :message="error.message" @retry="refresh" />
    <SharedEmptyState
      v-else-if="data && !data.results.length"
      :icon="Sparkles"
      title="No analyses yet"
      description="Run your first resume-vs-job analysis."
    />
    <Card v-else-if="data" class="divide-y p-0">
      <NuxtLink
        v-for="a in data.results"
        :key="a.id"
        :to="`/analysis/${a.id}`"
        class="flex items-center justify-between px-5 py-3.5 transition-colors hover:bg-accent/40"
      >
        <div class="min-w-0">
          <p class="truncate text-sm font-medium">
            Analysis · {{ new Date(a.created_at).toLocaleString() }}
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
