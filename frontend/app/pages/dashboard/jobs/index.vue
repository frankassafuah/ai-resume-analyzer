<script setup lang="ts">
import { Briefcase, Plus, Archive, Trash2 } from 'lucide-vue-next'
import { reactive, ref } from 'vue'
import { jobService } from '~/services/job.service'
import type { JobDescription } from '~/types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const toast = useToast()
const showForm = ref(false)
const form = reactive({
  company_name: '',
  job_title: '',
  description: '',
  required_skills: '',
  location: '',
  employment_type: 'full_time' as const,
})

const { data, pending, error, refresh } = useLoader(() => jobService.list())

const { run: create, pending: creating } = useAsyncAction(async () => {
  await jobService.create({
    company_name: form.company_name,
    job_title: form.job_title,
    description: form.description,
    location: form.location,
    employment_type: form.employment_type,
    required_skills: form.required_skills
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean),
  })
  toast.success('Job description created')
  showForm.value = false
  Object.assign(form, { company_name: '', job_title: '', description: '', required_skills: '', location: '' })
  await refresh()
})

const { run: toggleArchive } = useAsyncAction(async (job: JobDescription) => {
  await (job.is_archived ? jobService.unarchive(job.id) : jobService.archive(job.id))
  await refresh()
})

const { run: remove } = useAsyncAction(async (job: JobDescription) => {
  await jobService.remove(job.id)
  toast.success('Job deleted')
  await refresh()
})
</script>

<template>
  <div>
    <SharedPageHeader title="Job descriptions" description="Roles you analyze resumes against.">
      <template #actions>
        <Button @click="showForm = !showForm">
          <Plus class="size-4" /> New job
        </Button>
      </template>
    </SharedPageHeader>

    <Card v-if="showForm" class="mb-6 p-5">
      <form class="grid gap-4 sm:grid-cols-2" @submit.prevent="create()">
        <div class="space-y-2">
          <Label>Company</Label>
          <Input v-model="form.company_name" placeholder="Acme Inc." />
        </div>
        <div class="space-y-2">
          <Label>Job title</Label>
          <Input v-model="form.job_title" placeholder="Senior Engineer" />
        </div>
        <div class="space-y-2 sm:col-span-2">
          <Label>Description</Label>
          <textarea
            v-model="form.description"
            rows="4"
            placeholder="Paste the job description…"
            class="flex w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
          />
        </div>
        <div class="space-y-2">
          <Label>Required skills (comma-separated)</Label>
          <Input v-model="form.required_skills" placeholder="Python, Django, AWS" />
        </div>
        <div class="space-y-2">
          <Label>Location</Label>
          <Input v-model="form.location" placeholder="Remote" />
        </div>
        <div class="flex items-center gap-2 sm:col-span-2">
          <Button type="submit" :disabled="creating">
            {{ creating ? 'Saving…' : 'Save job' }}
          </Button>
          <Button type="button" variant="ghost" @click="showForm = false">Cancel</Button>
        </div>
      </form>
    </Card>

    <SharedLoadingState v-if="pending" />
    <SharedErrorState v-else-if="error" :message="error.message" @retry="refresh" />
    <SharedEmptyState
      v-else-if="data && !data.results.length"
      :icon="Briefcase"
      title="No job descriptions"
      description="Add a role to analyze your resumes against it."
    />
    <Card v-else-if="data" class="divide-y p-0">
      <div
        v-for="job in data.results"
        :key="job.id"
        class="flex items-center gap-4 px-5 py-3.5"
      >
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium">
            {{ job.job_title }}
            <Badge v-if="job.is_archived" variant="outline" class="ml-1">Archived</Badge>
          </p>
          <p class="truncate text-xs text-muted-foreground">
            {{ job.company_name }} · {{ job.employment_type_display }}
          </p>
        </div>
        <div class="flex items-center gap-1">
          <Button variant="ghost" size="icon" :title="job.is_archived ? 'Unarchive' : 'Archive'" @click="toggleArchive(job)">
            <Archive class="size-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            class="text-muted-foreground hover:text-destructive"
            title="Delete"
            @click="remove(job)"
          >
            <Trash2 class="size-4" />
          </Button>
        </div>
      </div>
    </Card>
  </div>
</template>
