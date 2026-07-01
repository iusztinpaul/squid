---
name: typescript-frontend
description: How to structure a TypeScript frontend package — Node 20+, package.json, tsconfig, eslint, prettier, module layout conventions. TRIGGER when writing TypeScript frontend code or bootstrapping a frontend package. SKIP for pure Node backends or CLI tools.
---

# TypeScript frontend

Opinionated starter for browser-targeting TypeScript packages. This is the top-level index; framework-specific skills (`react-app`, `vue-app`, `svelte-app`, `vanilla-ts-app`) build on top.

## When to use

- Writing or modifying TypeScript frontend code (browser-targeting).
- Adding a new frontend package to a monorepo under `packages/<name>/`.
- Bootstrapping a browser app from scratch.

## When NOT to use

- Node backends (API servers, CLIs) — those have different constraints (server-side `fs`, secrets handling, no bundler). Use a pure TS Node spec if one exists, or go language-agnostic.
- Deno / Bun projects — this skill assumes Node 20+ and npm.
- Non-TypeScript frontends (pure JS, Elm, ClojureScript).

## Decision tree

- **React** → this + [`react-app`](../react-app/SKILL.md).
- **Vue** → this + [`vue-app`](../vue-app/SKILL.md).
- **Svelte** → this + [`svelte-app`](../svelte-app/SKILL.md).
- **No framework** (hand-rolled) → this + [`vanilla-ts-app`](../vanilla-ts-app/SKILL.md).

Every variant uses the same `typescript-frontend` foundation below; the framework skill layers on top.

## Canonical principles

### Versions & tooling

- **Node 20+** minimum. Default to the latest LTS available to the team (22 LTS is current).
- **Package manager:** `npm`. Lockfile is `package-lock.json`. We don't use pnpm / yarn by default — pick one per team, not per project.
- **Bundler + dev server:** Vite. Never webpack, never create-react-app.
- **Testing:** Vitest (not Jest). jsdom environment for DOM tests.
- **Linter:** ESLint 9 (flat config). **Formatter:** Prettier 3. Both are non-optional.
- **TS strictness:** `strict: true`, plus `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`, `isolatedModules`. These are not negotiable.

### package.json scripts (contract with root Makefile delegator)

Every frontend package exposes the same script names so the monorepo Makefile can wire targets uniformly:

```jsonc
{
  "scripts": {
    "dev":          "vite",
    "build":        "tsc -b && vite build",   // vue uses `vue-tsc -b`; svelte uses `svelte-check && vite build`
    "preview":      "vite preview",
    "test":         "vitest run",
    "test:watch":   "vitest",
    "lint":         "eslint src",
    "lint:fix":     "eslint src --fix",
    "format":       "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

See [`makefile-delegator`](../makefile-delegator/SKILL.md) for how the root Makefile consumes these.

### Layout

See [`config.md`](config.md) for canonical `package.json` / `tsconfig.json` / `vite.config.ts`. Headlines:

```
packages/<name>/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── eslint.config.js        # flat config
├── .prettierrc
├── index.html
├── public/                 # static assets served as-is
├── src/
│   ├── main.ts(x)          # bundler entry point
│   ├── App.(tsx|vue|svelte)
│   ├── api/                # generated OpenAPI client lands here (if monorepo uses shared contracts)
│   └── ...
└── tests/
    └── **/*.test.ts(x)     # Vitest; mirrors src/
```

Module conventions:

- **One exported component per file.** `Button.tsx` exports one `Button`. Co-locate tightly-coupled subcomponents in the same file; split when another module needs them.
- **Tests mirror `src/` 1:1.** `src/foo/Bar.tsx` → `tests/foo/Bar.test.tsx`.
- **`src/api/` is generated** (from `packages/shared/openapi/api.yaml`) when the monorepo uses shared contracts. **Never hand-edit.** See [`openapi-contracts`](../openapi-contracts/SKILL.md).
- **`public/`** holds static assets Vite copies verbatim. Imported assets go in `src/assets/`.

### Environment variables (security-critical)

- Only variables prefixed `VITE_` reach the browser bundle. **Secrets must never be `VITE_*`** — they leak in the built JS. A `VITE_API_KEY` is public; a `API_KEY` is not.
- Declare every public var in `.env.example` with a safe dummy value.
- Read via `import.meta.env.VITE_FOO`. Never `process.env` in frontend code — it's a Node-ism.

### Testing discipline

- **Vitest**, not Jest. Keeps the bundler stack consistent (Vitest shares Vite's config).
- **jsdom** environment for component tests (`environment: 'jsdom'` in `vite.config.ts`).
- **AAA pattern.** Arrange, Act, Assert. Same as backend.
- React: **React Testing Library** over Enzyme. Query by role / label / text, not by test-id unless there's no alternative.
- Every framework has its testing library equivalent (`@vue/test-utils`, `@testing-library/svelte`) — use them.
- Zero skipped tests committed. If a test is broken, fix it or delete it — never `.skip`.


## TypeScript frontend — canonical configs

Reference configs. Copy, don't improvise. Swap the framework-specific plugin (React / Vue / Svelte / none) per the relevant framework skill; everything else stays.

### `package.json` (React example — adapt for Vue / Svelte / vanilla)

```json
{
  "name": "<package-name>",
  "version": "0.1.0",
  "type": "module",
  "private": true,
  "scripts": {
    "dev":          "vite",
    "build":        "tsc -b && vite build",
    "preview":      "vite preview",
    "test":         "vitest run",
    "test:watch":   "vitest",
    "lint":         "eslint src",
    "lint:fix":     "eslint src --fix",
    "format":       "prettier --write .",
    "format:check": "prettier --check ."
  },
  "dependencies": {
    "react":       "^18.3.0",
    "react-dom":   "^18.3.0"
  },
  "devDependencies": {
    "@types/react":                 "^18.3.0",
    "@types/react-dom":             "^18.3.0",
    "@vitejs/plugin-react":         "^4.3.0",
    "@testing-library/react":       "^16.0.0",
    "@testing-library/jest-dom":    "^6.4.0",
    "eslint":                       "^9.0.0",
    "prettier":                     "^3.3.0",
    "typescript":                   "^5.5.0",
    "vite":                         "^5.4.0",
    "vitest":                       "^2.0.0",
    "jsdom":                        "^25.0.0"
  }
}
```

Framework swaps:
- **Vue:** dep `vue`, dev `@vitejs/plugin-vue` + `vue-tsc`; `build` becomes `vue-tsc -b && vite build`.
- **Svelte:** dep `svelte`, dev `@sveltejs/vite-plugin-svelte` + `svelte-check`; `build` becomes `svelte-check && vite build`.
- **Vanilla:** no framework deps; `build` stays as `tsc -b && vite build`.

### `tsconfig.json`

```jsonc
{
  "compilerOptions": {
    "target":              "ES2022",
    "module":              "ESNext",
    "moduleResolution":    "bundler",
    "lib":                 ["ES2022", "DOM", "DOM.Iterable"],
    "jsx":                 "react-jsx",      // React only; drop for other frameworks
    "strict":              true,
    "noUnusedLocals":      true,
    "noUnusedParameters":  true,
    "noFallthroughCasesInSwitch": true,
    "isolatedModules":     true,
    "skipLibCheck":        true,
    "esModuleInterop":     true,
    "resolveJsonModule":   true,
    "allowImportingTsExtensions": false,
    "outDir":              "dist",
    "baseUrl":             ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src", "tests"],
  "exclude": ["node_modules", "dist"]
}
```

Non-negotiables:
- `strict: true` — catches the class of bugs TypeScript was invented to catch.
- `noUnusedLocals` / `noUnusedParameters` — dead code in a frontend bundle is *shipped*.
- `moduleResolution: "bundler"` — matches what Vite actually does; avoids `node`/`bundler` drift.
- `isolatedModules: true` — forces every file to be independently transpilable (required by Vite / esbuild).

### `vite.config.ts`

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";   // swap per framework
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  test: {
    globals:     true,
    environment: "jsdom",
    include:     ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
    setupFiles:  ["tests/setup.ts"],   // optional; add if you need global matchers
  },
});
```

`test.globals: true` means you can write `describe` / `it` / `expect` without importing them. We accept the global pollution for terseness; you can flip to `false` and import from `vitest` if you prefer.

### ESLint flat config (`eslint.config.js`)

```js
// eslint.config.js
import js from "@eslint/js";
import ts from "typescript-eslint";

export default [
  js.configs.recommended,
  ...ts.configs.recommended,
  {
    ignores: ["dist/**", "node_modules/**"],
  },
];
```

Keep it short. Add framework-specific ESLint configs (`eslint-plugin-react`, `eslint-plugin-vue`) in the framework skills, not here.

### Prettier (`.prettierrc`)

```json
{
  "semi":           true,
  "singleQuote":    false,
  "trailingComma":  "all",
  "printWidth":     100,
  "tabWidth":       2
}
```

Minimal. Don't debate Prettier settings — pick once, commit, stop talking about it.

### `.env.example`

```
## Only VITE_* vars reach the browser bundle. NEVER put secrets here.
VITE_API_BASE_URL=http://localhost:8000
```

### `tests/setup.ts` (optional)

```ts
import "@testing-library/jest-dom/vitest";
```

Only needed if you want DOM matchers (`toBeInTheDocument`, etc.).
