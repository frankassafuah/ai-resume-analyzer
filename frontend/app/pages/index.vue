<script setup lang="ts">
// Root simply routes into the app; auth middleware handles the rest.
definePageMeta({
  middleware: () => navigateTo('/dashboard'),
})
</script>

<template>
  <div />
</template>
