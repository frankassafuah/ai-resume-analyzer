<script setup lang="ts">
import { FileText, Upload, Download, Trash2 } from 'lucide-vue-next'
import { ref } from 'vue'
import { resumeService } from '~/services/resume.service'
import type { Resume } from '~/types'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const toast = useToast()
const fileInput = ref<HTMLInputElement>()

const { data, pending, error, refresh } = useLoader(() => resumeService.list())

const { run: upload, pending: uploading } = useAsyncAction(async (file: File) => {
  await resumeService.upload(file)
  toast.success('Resume uploaded', 'Parsing has started.')
  await refresh()
})

function onPick(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) upload(file)
  if (fileInput.value) fileInput.value.value = ''
}

const { run: remove } = useAsyncAction(async (resume: Resume) => {
  await resumeService.remove(resume.id)
  toast.success('Resume deleted')
  await refresh()
})

async function download(resume: Resume) {
  const blob = await resumeService.download(resume.id)
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = resume.current_version?.original_filename || 'resume'
  a.click()
  URL.revokeObjectURL(url)
}

const statusVariant: Record<string, string> = {
  parsed: 'success',
  parsing: 'warning',
  pending: 'secondary',
  failed: 'destructive',
  empty: 'outline',
}
</script>

<template>
  <div>
    <SharedPageHeader title="Resumes" description="Upload and manage your resumes.">
      <template #actions>
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.docx"
          class="hidden"
          @change="onPick"
        >
        <Button :disabled="uploading" @click="fileInput?.click()">
          <Upload class="size-4" />
          {{ uploading ? 'Uploading…' : 'Upload resume' }}
        </Button>
      </template>
    </SharedPageHeader>

    <SharedLoadingState v-if="pending" />
    <SharedErrorState v-else-if="error" :message="error.message" @retry="refresh" />
    <SharedEmptyState
      v-else-if="data && !data.results.length"
      :icon="FileText"
      title="No resumes yet"
      description="Upload a PDF or DOCX to get started."
    />
    <Card v-else-if="data" class="divide-y p-0">
      <div
        v-for="resume in data.results"
        :key="resume.id"
        class="flex items-center gap-4 px-5 py-3.5"
      >
        <span class="flex size-9 items-center justify-center rounded-md bg-muted">
          <FileText class="size-4 text-muted-foreground" />
        </span>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium">{{ resume.title }}</p>
          <p class="text-xs text-muted-foreground">
            v{{ resume.current_version?.version ?? 0 }} ·
            {{ new Date(resume.created_at).toLocaleDateString() }}
          </p>
        </div>
        <Badge :variant="(statusVariant[resume.status] as any)">{{ resume.status }}</Badge>
        <div class="flex items-center gap-1">
          <Button variant="ghost" size="icon" title="Download" @click="download(resume)">
            <Download class="size-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title="Delete"
            class="text-muted-foreground hover:text-destructive"
            @click="remove(resume)"
          >
            <Trash2 class="size-4" />
          </Button>
        </div>
      </div>
    </Card>
  </div>
</template>
