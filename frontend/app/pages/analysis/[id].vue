<script setup lang="ts">
import { ArrowLeft, CheckCircle2, XCircle, Lightbulb, KeyRound } from 'lucide-vue-next'
import { computed, onBeforeUnmount, watch } from 'vue'
import { analysisService } from '~/services/analysis.service'
import type { Analysis } from '~/types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const route = useRoute()
const id = route.params.id as string

const { data, pending, error, refresh } = useLoader<Analysis>(() => analysisService.get(id))

// Poll while the analysis is still running.
let timer: ReturnType<typeof setInterval> | null = null
const running = computed(
  () => data.value?.status === 'pending' || data.value?.status === 'processing',
)
watch(running, (isRunning) => {
  if (isRunning && !timer) timer = setInterval(refresh, 2000)
  else if (!isRunning && timer) {
    clearInterval(timer)
    timer = null
  }
})
onBeforeUnmount(() => timer && clearInterval(timer))

const result = computed(() => data.value?.result_json ?? null)
const statusVariant = computed(() =>
  data.value?.status === 'completed'
    ? 'success'
    : data.value?.status === 'failed'
      ? 'destructive'
      : 'warning',
)
</script>

<template>
  <div>
    <Button variant="ghost" size="sm" class="mb-3 -ml-2 text-muted-foreground" as-child>
      <NuxtLink to="/analysis"><ArrowLeft class="size-4" /> Back to analyses</NuxtLink>
    </Button>

    <SharedPageHeader title="Analysis report" description="How your resume matches this role.">
      <template #actions>
        <Badge v-if="data" :variant="statusVariant">
          {{ data.status }}<span v-if="running"> · live</span>
        </Badge>
      </template>
    </SharedPageHeader>

    <SharedLoadingState v-if="pending && !data" :rows="3" />
    <SharedErrorState v-else-if="error" :message="error.message" @retry="refresh" />

    <div v-else-if="data" class="space-y-6">
      <!-- Running / failed -->
      <Card v-if="data.status !== 'completed'" class="flex flex-col items-center gap-3 p-10 text-center">
        <template v-if="data.status === 'failed'">
          <XCircle class="size-8 text-destructive" />
          <p class="text-sm text-destructive">{{ data.error || 'Analysis failed.' }}</p>
        </template>
        <template v-else>
          <span class="size-8 animate-spin rounded-full border-2 border-muted border-t-primary" />
          <p class="text-sm text-muted-foreground">
            Analyzing your resume… this usually takes a few seconds.
          </p>
        </template>
      </Card>

      <template v-else-if="result">
        <!-- Scores + skills overview -->
        <div class="grid gap-4 lg:grid-cols-3">
          <Card class="flex items-center justify-around p-6 lg:col-span-2">
            <ChartsScoreRing :value="result.score" label="Job match" />
            <ChartsScoreRing :value="result.ats_score" label="ATS score" />
          </Card>
          <Card class="flex flex-col justify-center p-6">
            <h3 class="mb-4 text-sm font-medium">Skills coverage</h3>
            <ChartsSkillBars
              :matching="result.matching_skills.length"
              :missing="result.missing_skills.length"
            />
          </Card>
        </div>

        <!-- Summary -->
        <Card class="p-6">
          <h3 class="mb-2 text-sm font-medium">Summary</h3>
          <p class="text-sm leading-relaxed text-muted-foreground">{{ result.summary }}</p>
        </Card>

        <!-- Skill badges -->
        <div class="grid gap-4 sm:grid-cols-2">
          <Card class="p-6">
            <h3 class="mb-3 flex items-center gap-2 text-sm font-medium">
              <CheckCircle2 class="size-4 text-emerald-500" /> Matching skills
            </h3>
            <div class="flex flex-wrap gap-1.5">
              <Badge v-for="s in result.matching_skills" :key="s" variant="success">{{ s }}</Badge>
              <p v-if="!result.matching_skills.length" class="text-sm text-muted-foreground">None found</p>
            </div>
          </Card>
          <Card class="p-6">
            <h3 class="mb-3 flex items-center gap-2 text-sm font-medium">
              <XCircle class="size-4 text-amber-500" /> Missing skills
            </h3>
            <div class="flex flex-wrap gap-1.5">
              <Badge v-for="s in result.missing_skills" :key="s" variant="warning">{{ s }}</Badge>
              <p v-if="!result.missing_skills.length" class="text-sm text-muted-foreground">None — great coverage!</p>
            </div>
          </Card>
        </div>

        <!-- Keywords -->
        <Card v-if="result.keywords.length" class="p-6">
          <h3 class="mb-3 flex items-center gap-2 text-sm font-medium">
            <KeyRound class="size-4 text-muted-foreground" /> Keywords
          </h3>
          <div class="flex flex-wrap gap-1.5">
            <Badge v-for="k in result.keywords" :key="k" variant="secondary">{{ k }}</Badge>
          </div>
        </Card>

        <!-- Strengths / weaknesses -->
        <div class="grid gap-4 sm:grid-cols-2">
          <Card class="p-6">
            <h3 class="mb-3 text-sm font-medium">Strengths</h3>
            <ul class="space-y-2.5">
              <li v-for="(s, i) in result.strengths" :key="i" class="flex gap-2.5 text-sm">
                <CheckCircle2 class="mt-0.5 size-4 shrink-0 text-emerald-500" />
                <span class="text-muted-foreground">{{ s }}</span>
              </li>
            </ul>
          </Card>
          <Card class="p-6">
            <h3 class="mb-3 text-sm font-medium">Weaknesses</h3>
            <ul class="space-y-2.5">
              <li v-for="(w, i) in result.weaknesses" :key="i" class="flex gap-2.5 text-sm">
                <XCircle class="mt-0.5 size-4 shrink-0 text-amber-500" />
                <span class="text-muted-foreground">{{ w }}</span>
              </li>
            </ul>
          </Card>
        </div>

        <!-- Recommendations -->
        <Card class="p-6">
          <h3 class="mb-3 flex items-center gap-2 text-sm font-medium">
            <Lightbulb class="size-4 text-primary" /> Recommendations
          </h3>
          <ul class="space-y-2.5">
            <li v-for="(r, i) in result.recommendations" :key="i" class="flex gap-2.5 text-sm">
              <span
                class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary"
              >{{ i + 1 }}</span>
              <span class="text-muted-foreground">{{ r }}</span>
            </li>
          </ul>
        </Card>
      </template>
    </div>
  </div>
</template>
