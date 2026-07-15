<script setup lang="ts">
import {
  ArrowRight,
  Gauge,
  Target,
  ListChecks,
  Sparkles,
  FileText,
  MessagesSquare,
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

definePageMeta({ layout: false })

const auth = useAuthStore()

const features = [
  { icon: Gauge, title: 'ATS score', desc: 'See how machine-readable your resume is before a recruiter ever opens it.' },
  { icon: Target, title: 'Job match score', desc: 'Semantic + keyword matching against any job description, scored 0–100.' },
  { icon: ListChecks, title: 'Skills gap', desc: 'Exactly which required skills you have — and which you’re missing.' },
  { icon: Sparkles, title: 'AI rewrite', desc: 'A tailored professional summary rewritten for the role you want.' },
  { icon: FileText, title: 'Cover letters', desc: 'Role-specific cover letters generated in seconds.' },
  { icon: MessagesSquare, title: 'Interview prep', desc: 'Likely interview questions with talking points, ready to rehearse.' },
]
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <!-- Nav -->
    <header class="sticky top-0 z-30 border-b bg-background/80 backdrop-blur">
      <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <SharedAppLogo />
        <nav class="flex items-center gap-2">
          <template v-if="auth.isAuthenticated">
            <Button as-child><NuxtLink to="/dashboard">Dashboard</NuxtLink></Button>
          </template>
          <template v-else>
            <Button variant="ghost" as-child>
              <NuxtLink to="/auth/login">Sign in</NuxtLink>
            </Button>
            <Button as-child><NuxtLink to="/auth/register">Get started</NuxtLink></Button>
          </template>
        </nav>
      </div>
    </header>

    <!-- Hero -->
    <section class="relative overflow-hidden">
      <div
        class="pointer-events-none absolute -top-40 left-1/2 size-160 -translate-x-1/2 rounded-full bg-primary/5 blur-3xl"
      />
      <div class="mx-auto max-w-3xl px-4 py-24 text-center sm:px-6 sm:py-32">
        <span
          class="inline-flex items-center gap-1.5 rounded-full border bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground"
        >
          <Sparkles class="size-3" /> AI-powered resume analysis
        </span>
        <h1 class="mt-6 text-4xl font-semibold tracking-tight sm:text-6xl">
          Land more interviews with a resume that fits the job.
        </h1>
        <p class="mx-auto mt-6 max-w-xl text-lg text-muted-foreground">
          Upload your resume, paste a job description, and get an instant ATS score,
          match score, missing skills, and a tailored rewrite.
        </p>
        <div class="mt-8 flex items-center justify-center gap-3">
          <Button size="lg" as-child>
            <NuxtLink to="/auth/register">
              Analyze my resume <ArrowRight class="size-4" />
            </NuxtLink>
          </Button>
          <Button size="lg" variant="outline" as-child>
            <NuxtLink to="/auth/login">Sign in</NuxtLink>
          </Button>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="mx-auto max-w-6xl px-4 pb-24 sm:px-6">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="f in features"
          :key="f.title"
          class="rounded-xl border bg-card p-6 transition-colors hover:border-foreground/20"
        >
          <div
            class="mb-4 flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary"
          >
            <component :is="f.icon" class="size-5" />
          </div>
          <h3 class="text-sm font-semibold">{{ f.title }}</h3>
          <p class="mt-1 text-sm text-muted-foreground">{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <footer class="border-t">
      <div
        class="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-4 py-8 text-sm text-muted-foreground sm:flex-row sm:px-6"
      >
        <span>© {{ new Date().getFullYear() }} AI Resume Analyzer</span>
        <span>Built with Nuxt · Django · Celery</span>
      </div>
    </footer>
  </div>
</template>
