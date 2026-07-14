<script setup lang="ts">
import { toTypedSchema } from '@vee-validate/zod'
import { useForm } from 'vee-validate'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

definePageMeta({ layout: 'auth', middleware: 'guest' })

const auth = useAuthStore()
const route = useRoute()

const schema = toTypedSchema(
  z.object({
    email: z.string().min(1, 'Email is required').email('Enter a valid email'),
    password: z.string().min(1, 'Password is required'),
  }),
)
const { handleSubmit, errors, defineField } = useForm({ validationSchema: schema })
const [email, emailAttrs] = defineField('email')
const [password, passwordAttrs] = defineField('password')

const { run, pending } = useAsyncAction(async (values: { email: string; password: string }) => {
  await auth.login(values)
  useToast().success('Welcome back')
  await navigateTo((route.query.redirect as string) || '/dashboard')
})

const onSubmit = handleSubmit((values) => run(values))
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold tracking-tight">Sign in</h1>
    <p class="mt-1 text-sm text-muted-foreground">
      Welcome back. Enter your details to continue.
    </p>

    <form class="mt-8 space-y-4" @submit="onSubmit">
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
          placeholder="••••••••"
          autocomplete="current-password"
        />
        <p v-if="errors.password" class="text-xs text-destructive">{{ errors.password }}</p>
      </div>

      <Button type="submit" class="w-full" :disabled="pending">
        {{ pending ? 'Signing in…' : 'Sign in' }}
      </Button>
    </form>

    <p class="mt-6 text-center text-sm text-muted-foreground">
      Don't have an account?
      <NuxtLink to="/register" class="font-medium text-foreground hover:underline">
        Sign up
      </NuxtLink>
    </p>
  </div>
</template>
