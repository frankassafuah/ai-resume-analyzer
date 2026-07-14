<script setup lang="ts">
// Centered, minimal layout for login / register.
</script>

<template>
  <div class="grid min-h-screen bg-background text-foreground lg:grid-cols-2">
    <!-- Left: form -->
    <div class="flex flex-col justify-center px-6 py-12 sm:px-12">
      <div class="mx-auto w-full max-w-sm">
        <SharedAppLogo class="mb-8" />
        <slot />
      </div>
    </div>

    <!-- Right: brand panel (hidden on small screens) -->
    <div class="relative hidden overflow-hidden border-l bg-muted/40 lg:block">
      <div class="absolute inset-0 flex flex-col justify-center px-12">
        <blockquote class="max-w-md space-y-4">
          <p class="text-2xl font-medium leading-snug tracking-tight">
            "Land more interviews. Instantly see how your resume stacks up against
            any job — ATS score, missing skills, and a tailored rewrite."
          </p>
          <p class="text-sm text-muted-foreground">AI Resume Analyzer</p>
        </blockquote>
      </div>
      <div
        class="pointer-events-none absolute -right-24 -top-24 size-96 rounded-full bg-primary/5 blur-3xl"
      />
    </div>
  </div>
</template>
