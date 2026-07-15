<script setup lang="ts">
import { reactive, watchEffect } from 'vue'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

definePageMeta({ layout: 'dashboard', middleware: 'auth' })

const auth = useAuthStore()
const toast = useToast()

const form = reactive({ first_name: '', last_name: '' })
watchEffect(() => {
  form.first_name = auth.user?.first_name ?? ''
  form.last_name = auth.user?.last_name ?? ''
})

const { run: save, pending } = useAsyncAction(async () => {
  await auth.updateProfile({ first_name: form.first_name, last_name: form.last_name })
  toast.success('Profile updated')
})
</script>

<template>
  <div>
    <SharedPageHeader title="Settings" description="Manage your account." />

    <Card class="max-w-xl p-6">
      <form class="space-y-4" @submit.prevent="save()">
        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-2">
            <Label>First name</Label>
            <Input v-model="form.first_name" />
          </div>
          <div class="space-y-2">
            <Label>Last name</Label>
            <Input v-model="form.last_name" />
          </div>
        </div>
        <div class="space-y-2">
          <Label>Email</Label>
          <Input :model-value="auth.user?.email" disabled />
        </div>
        <Button type="submit" :disabled="pending">
          {{ pending ? 'Saving…' : 'Save changes' }}
        </Button>
      </form>
    </Card>
  </div>
</template>
