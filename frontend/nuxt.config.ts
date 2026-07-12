import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  future: { compatibilityVersion: 4 },
  devtools: { enabled: true },

  // SPA, matching amev-crm (ADR-0005).
  ssr: false,

  css: ['~/assets/css/tailwind.css'],

  app: {
    head: {
      title: 'AI Resume Analyzer',
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },

  // shadcn-nuxt is the only UI library (ADR-0005). Tailwind v4 via its Vite plugin.
  modules: ['shadcn-nuxt', '@pinia/nuxt', '@nuxt/eslint'],

  shadcn: {
    // Components imported without a prefix, e.g. <Button />.
    prefix: '',
    componentDir: '@/components/ui',
  },

  runtimeConfig: {
    public: {
      // Base URL of the Django API; overridable via NUXT_PUBLIC_API_BASE.
      apiBase: 'http://localhost:8000',
    },
  },

  vite: {
    plugins: [tailwindcss()],
  },

  typescript: {
    tsConfig: {
      exclude: ['app/components/ui/**/*', 'node_modules'],
    },
  },
})
