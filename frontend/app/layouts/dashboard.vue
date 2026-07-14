<script setup lang="ts">
// Authenticated app shell: fixed sidebar + top header + scrollable content.
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <LayoutAppSidebar />
    <div class="lg:pl-60">
      <LayoutAppHeader />
      <main class="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <slot />
      </main>
    </div>
  </div>
</template>
