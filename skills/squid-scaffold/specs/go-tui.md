---
name: go-tui
description: How to structure a Go 1.22+ TUI project — go mod, gofmt, go test, cmd/ vs internal/ layout, TUI framework choice (bubbletea vs tview). TRIGGER when writing or bootstrapping a Go terminal UI. SKIP for Go services without a TUI.
---

# Go TUI

Opinionated starter for Go terminal-UI applications. The layout opinions apply to any Go CLI/TUI; the framework-specific parts live in two supporting files — pick one.

## When to use

- Writing or modifying a Go terminal UI.
- Adding a TUI to an existing Go codebase.
- Bootstrapping a Go TUI from scratch (monorepo or standalone).

## When NOT to use

- Go HTTP services / gRPC servers — the `cmd/` / `internal/` layout below still applies, but skip the framework files.
- Non-Go TUIs (Python `rich`/`textual`, Rust `ratatui`, JS `ink`) — different tooling entirely.

## Decision tree — which TUI framework?

- **Bubbletea** (default) — Elm-style Model/Update/View. Best when the app is state-driven and reactive (dashboards, forms, wizards), or when you want Lip Gloss styling. Chose Bubbletea → read [`go-tui-bubbletea.md`](go-tui-bubbletea.md).
- **tview** — traditional widget composition (Flex, Pages, Grid, etc.). Best when the app is a composed layout of off-the-shelf widgets (tables, forms, menu trees). Chose tview → read [`go-tui-tview.md`](go-tui-tview.md).

Default to Bubbletea unless you specifically want tview's widget library.

## Canonical principles

### Versions & tooling

- **Go 1.22 minimum.** Default to the latest stable (1.23+).
- **Modules are mandatory.** Every project has `go.mod`. Module path is the full import path (e.g. `github.com/<org>/<repo>`).
- **Formatter:** `gofmt` (authoritative, via pre-commit). No debate.
- **Linter:** `go vet ./...`. Optional add-ons (`golangci-lint`, `staticcheck`) only if the team already runs them.
- **Testing:** stdlib `testing`. No ginkgo / gomega / testify unless the team already uses them — keep the test stack small.
- **Pinned dependency versions in `go.mod`**, so `go mod tidy` is deterministic across developers.

### Layout

Tree, rules, and anti-patterns: [Go TUI — module layout](#go-tui--module-layout) below.

### Entry-point shape (framework-agnostic)

```go
package main

import (
    "log"
    "os"
    // import your chosen framework: bubbletea or tview
)

func main() {
    if err := run(); err != nil {
        log.Fatalf("fatal: %v", err)
        os.Exit(1)
    }
}

func run() error {
    // wire the framework here — see go-tui-bubbletea.md or go-tui-tview.md
    return nil
}
```

Keep `main()` tiny. All logic goes in `run()`; `main()` just handles the exit code. This is the test seam — `run()` is callable from `cmd_test.go` if needed.

### Makefile targets (contract with root delegator)

Every Go TUI package exposes:

| Target | Command |
|---|---|
| `install` | `go mod tidy` |
| `build` | `go build -o bin/<slug> ./cmd/<slug>` |
| `test` | `go test ./...` |
| `lint-check` | `go vet ./...` |
| `format-fix` | `gofmt -w .` |
| `format-check` | `gofmt -l .` (fails if any file needs formatting) |
| `run` | `go run ./cmd/<slug>` |

See [`makefile-delegator`](makefile-delegator.md) for how the root Makefile consumes these.

### TUIs are NOT containerised for routine dev

TUIs need an interactive terminal with a real TTY — a Docker run loses input focus, line-drawing characters, keybindings, and colour capability. Don't ship a Dockerfile for the TUI package by default. If you need reproducible binary builds, use `goreleaser` or a CI build step, not a dev Docker.

### OpenAPI client (if monorepo uses shared contracts)

When the TUI consumes a backend API defined in `packages/shared/openapi/api.yaml`:

- Generated client lands at `internal/api/client.go`.
- Regen is driven by `make -C ../shared gen-go` (or root `make openapi-gen`).
- **Never hand-edit `internal/api/client.go`.** Regenerate from the spec.
- Base URL via an env var (`API_BASE_URL`), read at startup.
- See [`openapi-contracts`](openapi-contracts.md).


## Go TUI — module layout

Canonical tree for a Go TUI package.

```
packages/<name>/                # or repo root for a standalone project
├── go.mod                      # module github.com/<org>/<repo>
├── go.sum                      # committed
├── Makefile                    # targets: see "Makefile targets" above
├── .env.example                # runtime config (API_BASE_URL, etc.)
├── cmd/
│   └── <project_slug>/
│       ├── main.go             # tiny — wires framework, calls run()
│       └── main_test.go        # optional; tests for flag parsing / run()
├── internal/                   # private to this module
│   ├── ui/
│   │   ├── model.go            # Bubbletea: root Model struct + Init/Update/View
│   │   ├── keys.go             # keybinding table
│   │   ├── styles.go           # Lip Gloss styles, colour palette
│   │   ├── components/         # sub-models (split when Update() gets long)
│   │   └── model_test.go       # unit tests for Update() transitions
│   ├── api/                    # generated OpenAPI client — DO NOT hand-edit
│   │   └── client.go
│   └── config/
│       ├── config.go           # env var loading, defaults, validation
│       └── config_test.go
├── pkg/                        # only for stable public API; often empty
└── bin/                        # build output, .gitignored
    └── <project_slug>
```

### Why this shape

- **`cmd/<slug>/main.go` is the only entry point.** Standard Go convention. The binary name is the directory name under `cmd/`. A project can have multiple binaries (`cmd/server/`, `cmd/worker/`, `cmd/migrate/`) — each gets its own subdir, never two `main()`s in one package. For a TUI, you typically have just one.
- **Tiny `main()`, real work in `run()`.** `main()` handles OS-level concerns (exit codes, signal setup, log setup). `run()` returns `error` and is callable from tests. This is the single most common Go main-function pattern — follow it.
- **`internal/` is your real codebase.** The Go compiler enforces that packages under `internal/` can only be imported by the parent module. You get encapsulation without annotations.
- **`internal/ui/` is the TUI boundary.** Anything Bubbletea- or tview-specific lives here. `cmd/<slug>/main.go` imports `internal/ui` and `internal/config`; it doesn't know about `tea.Program` or `tview.Application` directly if you split well.
- **`internal/api/` is generated.** Treat it like a dependency — regenerate, don't edit. See [`openapi-contracts`](openapi-contracts.md).
- **Tests beside code (`_test.go`).** Co-located tests can access unexported identifiers (they're in the same package). A separate `tests/` dir forces you to export things you shouldn't. Use `foo_test.go` (same package) for unit tests, and optionally `foo_blackbox_test.go` (package `foo_test`) for tests that exercise only the public API.
- **`pkg/` is usually empty.** Only put code there if a separate module imports it. For a TUI that nobody else imports, `pkg/` is dead space.
- **Lowercase, single-word package names.** `package ui`, not `package user_interface`.

### Anti-patterns

- **Big `main.go`.** Any TUI with more than ~50 lines in `main()` is doing UI work there. Move it to `internal/ui/`.
- **Deep sub-packages before they're justified.** `internal/ui/components/widgets/buttons/primary/` is not a filing system. Flatten until a sub-package is needed for encapsulation.
- **Importing `fmt.Println` for user output.** In a TUI, stdout is the terminal buffer. Use the framework's rendering; never `fmt.Println` from `Update()`.
- **Ignoring `context.Context` in long-running work.** Any goroutine fired from `Update()` takes a `ctx` so cancellation works (e.g. when the user hits `q` mid-request).
- **Catching every error with `log.Fatal` inside a TUI.** `log.Fatal` writes to stderr and exits — it corrupts the terminal buffer. Surface errors through the Model's state and let the View render them.
