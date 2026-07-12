// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt(
  // shadcn-vue generates these; keep them out of linting (they follow upstream style).
  { ignores: ['app/components/ui/**'] },
)
