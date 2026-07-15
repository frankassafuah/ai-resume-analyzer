<script setup lang="ts">
import {
  DropdownMenuRoot,
  DropdownMenuTrigger,
  DropdownMenuPortal,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from 'reka-ui'
import { ChevronsUpDown, LogOut, Settings, User } from 'lucide-vue-next'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

const auth = useAuthStore()

async function logout() {
  await auth.logout({ redirect: true })
}
</script>

<template>
  <DropdownMenuRoot>
    <DropdownMenuTrigger
      class="flex w-full items-center gap-2.5 rounded-md p-2 text-left outline-none transition-colors hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring/50"
    >
      <Avatar class="size-8">
        <AvatarImage v-if="auth.user?.profile_image" :src="auth.user.profile_image" />
        <AvatarFallback>{{ auth.initials }}</AvatarFallback>
      </Avatar>
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-medium">
          {{ auth.user?.full_name || auth.user?.email }}
        </p>
        <p class="truncate text-xs text-muted-foreground">{{ auth.user?.email }}</p>
      </div>
      <ChevronsUpDown class="size-4 shrink-0 text-muted-foreground" />
    </DropdownMenuTrigger>

    <DropdownMenuPortal>
      <DropdownMenuContent
        :side-offset="8"
        align="start"
        class="z-50 w-56 rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0"
      >
        <NuxtLink to="/settings">
          <DropdownMenuItem
            class="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none data-[highlighted]:bg-accent"
          >
            <User class="size-4" /> Profile
          </DropdownMenuItem>
        </NuxtLink>
        <NuxtLink to="/settings">
          <DropdownMenuItem
            class="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none data-[highlighted]:bg-accent"
          >
            <Settings class="size-4" /> Settings
          </DropdownMenuItem>
        </NuxtLink>
        <DropdownMenuSeparator class="my-1 h-px bg-border" />
        <DropdownMenuItem
          class="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-destructive outline-none data-[highlighted]:bg-destructive/10"
          @select="logout"
        >
          <LogOut class="size-4" /> Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenuPortal>
  </DropdownMenuRoot>
</template>
