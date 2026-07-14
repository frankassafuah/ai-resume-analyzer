<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

definePageMeta({ layout: 'auth', middleware: 'guest' })

const auth = useAuthStore()

const schema = toTypedSchema(
  z.object({
    first_name: z.string().optional(),
    last_name: z.string().optional(),
    email: z.string().min(1, 'Email is required').email('Enter a valid email'),
    password: z.string().min(8, 'At least 8 characters'),
  }),
)
const { handleSubmit, errors, defineField } = useForm({ validationSchema: schema })
const [firstName, firstNameAttrs] = defineField('first_name')
const [lastName, lastNameAttrs] = defineField('last_name')
const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')

const { run, pending } = useAsyncAction(async (values: {
  email: string
  password: string
  first_name?: string
  last_name?: string
}) => {
  await auth.register(values)
  useToast().success('Account created')
  await navigateTo('/dashboard')
})

const onSubmit = handleSubmit((values) => run(values))
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold tracking-tight">Create your account</h1>
    <p class="mt-1 text-sm text-muted-foreground">Start analyzing resumes in minutes.</p>

    <form class="mt-8 space-y-4" @submit="onSubmit">
      <div class="grid grid-cols-2 gap-3">
        <div class="space-y-2">
          <Label for="first_name">First name</Label>
          <Input id="first_name" v-model="firstName" v-bind="firstNameAttrs" placeholder="Jane" />
        </div>
        <div class="space-y-2">
          <Label for="last_name">Last name</Label>
          <Input id="last_name" v-model="lastName" v-bind="lastNameAttrs" placeholder="Doe" />
        </div>
      </div>

      <div class="space-y-2">
        <Label for="email">Email</Label>
        <Input
          id="email"
          v-model="email"
          v-bind="emailAttrs"
          type="email"
          placeholder="you@example.com"
          autocomplete="email"
        />
        <p v-if="errors.email" class="text-xs text-destructive">{{ errors.email }}</p>
      </div>

      <div class="space-y-2">
        <Label for="password">Password</Label>
        <Input
          id="password"
          v-model="password"
          v-bind="passwordAttrs"
          type="password"
          placeholder="At least 8 characters"
          autocomplete="new-password"
        />
        <p v-if="errors.password" class="text-xs text-destructive">{{ errors.password }}</p>
      </div>

      <Button type="submit" class="w-full" :disabled="pending">
        {{ pending ? 'Creating account…' : 'Create account' }}
      </Button>
    </form>

    <p class="mt-6 text-center text-sm text-muted-foreground">
      Already have an account?
      <NuxtLink to="/login" class="font-medium text-foreground hover:underline">
        Sign in
      </NuxtLink>
    </p>
  </div>
</template>
