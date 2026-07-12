FROM node:22-slim AS base
ENV PNPM_HOME=/pnpm
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
WORKDIR /app

# --- deps ---
FROM base AS deps
COPY package.json ./
RUN npm install

# --- dev runtime (used by docker-compose) ---
FROM base AS dev
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
ENV NUXT_HOST=0.0.0.0 NUXT_PORT=3000
CMD ["npm", "run", "dev"]

# --- production build ---
FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS prod
COPY --from=build /app/.output ./.output
EXPOSE 3000
ENV NUXT_HOST=0.0.0.0 NUXT_PORT=3000
CMD ["node", ".output/server/index.mjs"]
