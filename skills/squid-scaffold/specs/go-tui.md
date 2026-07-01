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

- Go HTTP services / gRPC servers — the `cmd/` / `internal/` layout below still applies, but skip the framework sections.
- Non-Go TUIs (Python `rich`/`textual`, Rust `ratatui`, JS `ink`) — different tooling entirely.

## Decision tree — which TUI framework?

- **Bubbletea** (default) — Elm-style Model/Update/View. Best when the app is state-driven and reactive (dashboards, forms, wizards), or when you want Lip Gloss styling. See [`bubbletea.md`](bubbletea.md).
- **tview** — traditional widget composition (Flex, Pages, Grid, etc.). Best when the app is a composed layout of off-the-shelf widgets (tables, forms, menu trees). See [`tview.md`](tview.md).

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

See [`layout.md`](layout.md) for the full tree. Headlines:

```
packages/<name>/
├── go.mod
├── go.sum
├── Makefile
├── cmd/
│   └── <project_slug>/
│       └── main.go        # entry point; wires the framework and runs
├── internal/              # importable by this module only (Go convention)
│   ├── ui/                # TUI-specific: models, components, styles
│   └── api/               # generated OpenAPI client (if monorepo uses shared contracts)
├── pkg/                   # importable by external modules (use rarely)
└── tests/
    └── example_test.go    # or *_test.go beside code
```

Rules:

- **`cmd/<binary_name>/main.go` is the only entry point.** One binary per `cmd/` subdir. If you need two binaries, you have two subdirs — not two `main()`s in one package.
- **`internal/`** is where 95% of code lives. The Go compiler enforces it's not importable by other modules — free encapsulation.
- **`pkg/`** is for code you *want* other modules to import. Use rarely; most TUIs have nothing to expose.
- **Test files live beside code** (`foo.go` + `foo_test.go` in the same dir). A `tests/` subdir is fine too but not idiomatic — prefer co-location unless you're doing an integration harness.
- **Lowercase package names**, single word. `package ui`, not `package user_interface`.

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
    // wire the framework here — see bubbletea.md or tview.md
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

See [`makefile-delegator`](../makefile-delegator/SKILL.md) for how the root Makefile consumes these.

### TUIs are NOT containerised for routine dev

TUIs need an interactive terminal with a real TTY — a Docker run loses input focus, line-drawing characters, keybindings, and colour capability. Don't ship a Dockerfile for the TUI package by default. If you need reproducible binary builds, use `goreleaser` or a CI build step, not a dev Docker.

### OpenAPI client (if monorepo uses shared contracts)

When the TUI consumes a backend API defined in `packages/shared/openapi/api.yaml`:

- Generated client lands at `internal/api/client.go`.
- Regen is driven by `make -C ../shared gen-go` (or root `make openapi-gen`).
- **Never hand-edit `internal/api/client.go`.** Regenerate from the spec.
- Base URL via an env var (`API_BASE_URL`), read at startup.
- See [`openapi-contracts`](../openapi-contracts/SKILL.md).


## Go TUI — module layout

Canonical tree for a Go TUI package.

```
packages/<name>/                # or repo root for a standalone project
├── go.mod                      # module github.com/<org>/<repo>
├── go.sum                      # committed
├── Makefile                    # see go-tui/SKILL.md for targets
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

- **`cmd/<slug>/main.go` pattern.** Standard Go convention. The binary name is the directory name under `cmd/`. A project can have multiple binaries (`cmd/server/`, `cmd/worker/`, `cmd/migrate/`) — each gets its own subdir. For a TUI, you typically have just one.
- **Tiny `main()`, real work in `run()`.** `main()` handles OS-level concerns (exit codes, signal setup, log setup). `run()` returns `error` and is callable from tests. This is the single most common Go main-function pattern — follow it.
- **`internal/` is your real codebase.** The Go compiler enforces that packages under `internal/` can only be imported by the parent module. You get encapsulation without annotations.
- **`internal/ui/` is the TUI boundary.** Anything Bubbletea- or tview-specific lives here. `cmd/<slug>/main.go` imports `internal/ui` and `internal/config`; it doesn't know about `tea.Program` or `tview.Application` directly if you split well.
- **`internal/api/` is generated.** Treat it like a dependency — regenerate, don't edit. See [`openapi-contracts`](../openapi-contracts/SKILL.md).
- **Tests beside code (`_test.go`).** Co-located tests can access unexported identifiers (they're in the same package). A separate `tests/` dir forces you to export things you shouldn't. Use `foo_test.go` (same package) for unit tests, and optionally `foo_blackbox_test.go` (package `foo_test`) for tests that exercise only the public API.
- **`pkg/` is usually empty.** Only put code there if a separate module imports it. For a TUI that nobody else imports, `pkg/` is dead space.

### Anti-patterns

- **Big `main.go`.** Any TUI with more than ~50 lines in `main()` is doing UI work there. Move it to `internal/ui/`.
- **Deep sub-packages before they're justified.** `internal/ui/components/widgets/buttons/primary/` is not a filing system. Flatten until a sub-package is needed for encapsulation.
- **Importing `fmt.Println` for user output.** In a TUI, stdout is the terminal buffer. Use the framework's rendering; never `fmt.Println` from `Update()`.
- **Singletons / global state.** Bubbletea's Model is your state container; tview has explicit state in widgets. Neither needs a package-level `var currentUser User`.
- **Ignoring `context.Context` in long-running work.** Any goroutine fired from `Update()` takes a `ctx` so cancellation works (e.g. when the user hits `q` mid-request).
- **Catching every error with `log.Fatal` inside a TUI.** `log.Fatal` writes to stderr and exits — it corrupts the terminal buffer. Surface errors through the Model's state and let the View render them.

## Go TUI — Bubbletea

Opinionated Bubbletea usage. Read this alongside the top-level [`go-tui/SKILL.md`](SKILL.md).

### Core pattern: Model / Update / View

Bubbletea is Elm-style. Your app is a single `Model` (state) with three methods:

- `Init() tea.Cmd` — returns an initial command (fire an HTTP request, read a file, etc.), or `nil`.
- `Update(msg tea.Msg) (tea.Model, tea.Cmd)` — given an incoming message, return the new model and optionally a new command.
- `View() string` — render the current model as a string; Bubbletea diffs and paints it.

All state lives in `Model`. No hidden globals, no package-level mutation. If two components need to share state, they're both branches of the same Model.

### Canonical root model

```go
// internal/ui/model.go
package ui

import (
    tea "github.com/charmbracelet/bubbletea"
    "github.com/charmbracelet/lipgloss"
)

type Model struct {
    // state
    items    []string
    cursor   int
    quitting bool
    err      error

    // sub-models (split when Update() grows past ~100 lines)
    // list list.Model
    // input textinput.Model
}

func New() Model {
    return Model{
        items: []string{"one", "two", "three"},
    }
}

func (m Model) Init() tea.Cmd {
    return nil
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.KeyMsg:
        switch msg.String() {
        case "q", "ctrl+c":
            m.quitting = true
            return m, tea.Quit
        case "up", "k":
            if m.cursor > 0 {
                m.cursor--
            }
        case "down", "j":
            if m.cursor < len(m.items)-1 {
                m.cursor++
            }
        }
    case errMsg:
        m.err = msg
    }
    return m, nil
}

func (m Model) View() string {
    if m.quitting {
        return ""
    }
    if m.err != nil {
        return errStyle.Render("error: " + m.err.Error()) + "\n"
    }
    var s string
    for i, item := range m.items {
        cursor := "  "
        if m.cursor == i {
            cursor = "> "
        }
        s += cursor + item + "\n"
    }
    return s + "\nq: quit\n"
}

type errMsg error
```

And the entry point wires it:

```go
// cmd/<slug>/main.go
package main

import (
    "fmt"
    "os"

    tea "github.com/charmbracelet/bubbletea"
    "github.com/<org>/<repo>/internal/ui"
)

func main() {
    if _, err := tea.NewProgram(ui.New(), tea.WithAltScreen()).Run(); err != nil {
        fmt.Fprintln(os.Stderr, "error:", err)
        os.Exit(1)
    }
}
```

`tea.WithAltScreen()` uses the terminal's alternate screen buffer — the user's scrollback is preserved when the TUI exits.

### Opinionated rules

- **One root `Model`.** It may embed sub-models (`list.Model`, `textinput.Model`, your own); keep the root skeleton thin.
- **Keybindings in a table, not scattered through `Update()`.** Use `internal/ui/keys.go` with a `KeyMap` struct the `Update()` switches on. Makes help text generation trivial.
- **Commands for async work.** Never block inside `Update()`. Fire a `tea.Cmd` that does the work and returns a message; handle the message in a subsequent `Update()`.
- **Errors are messages.** Define a local `errMsg error` type; commands that can fail return it via the message channel. `View()` reads `m.err` and renders a state, not a panic.
- **Lip Gloss for all styling.** Define styles once in `internal/ui/styles.go` (`titleStyle`, `errStyle`, `selectedStyle`, …). Don't build strings with raw ANSI escapes.
- **Test `Update()` directly.** Unit tests call `model.Update(tea.KeyMsg{Type: tea.KeyUp})` and assert the new model's fields. No real TTY needed.

### Common Cmd patterns

```go
func fetchItems() tea.Cmd {
    return func() tea.Msg {
        items, err := api.List(context.Background())
        if err != nil {
            return errMsg(err)
        }
        return itemsMsg(items)
    }
}

// in Update:
case itemsMsg:
    m.items = []string(msg)
```

Always pass a `context.Context` through to the API layer so long requests can be cancelled when the user quits.

### Anti-patterns

- **Mutating `m` then returning `m, nil` where `m` is a pointer.** Bubbletea's `Model` is pass-by-value on purpose. Don't use pointer receivers for the root model.
- **`fmt.Println` in `Update()` or `View()`.** Stdout is the terminal buffer Bubbletea is painting to. Use styled strings via the Model's state.
- **Global state.** If a sub-component needs data, embed it in the root Model and pass the relevant slice down.
- **One giant `Update()`.** Split into sub-models with their own `Update()`; the root `Update()` dispatches to them.
- **Reading from channels inside `Update()`.** Use `tea.Cmd` to read; messages flow through the framework.

## Go TUI — tview

Opinionated tview usage. Read this alongside the top-level [`go-tui/SKILL.md`](SKILL.md).

### Core pattern: widget composition

tview is a traditional retained-mode widget toolkit. You build a tree of `tview.Primitive` nodes (`Flex`, `Pages`, `Grid`, `List`, `TextView`, `Form`, `Table`, …), wire event handlers, and hand the root to `app.SetRoot()`.

State lives inside widgets. Keybindings are registered per widget (or on the `tview.Application` for global ones). There's no single reducer — each widget's handler updates the widgets that need updating and calls `app.Draw()` when needed.

### Canonical root

```go
// internal/ui/app.go
package ui

import (
    "github.com/gdamore/tcell/v2"
    "github.com/rivo/tview"
)

type App struct {
    tui   *tview.Application
    pages *tview.Pages
    items []string
}

func New() *App {
    return &App{
        tui:   tview.NewApplication(),
        pages: tview.NewPages(),
        items: []string{"one", "two", "three"},
    }
}

func (a *App) Run() error {
    list := tview.NewList()
    for _, item := range a.items {
        item := item
        list.AddItem(item, "", 0, func() {
            // handle selection
        })
    }
    list.SetBorder(true).SetTitle(" items ")

    a.pages.AddPage("main", list, true, true)

    a.tui.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
        if event.Key() == tcell.KeyCtrlC || event.Rune() == 'q' {
            a.tui.Stop()
            return nil
        }
        return event
    })

    return a.tui.SetRoot(a.pages, true).Run()
}
```

And the entry point:

```go
// cmd/<slug>/main.go
package main

import (
    "fmt"
    "os"

    "github.com/<org>/<repo>/internal/ui"
)

func main() {
    if err := ui.New().Run(); err != nil {
        fmt.Fprintln(os.Stderr, "error:", err)
        os.Exit(1)
    }
}
```

### Opinionated rules

- **One `tview.Application` per process.** Usually held on an `App` struct (as above). Don't spin up a second.
- **`tview.Pages` as the root** whenever the app has more than one screen. Swapping via `pages.SwitchToPage("name")` is cheap and keeps layout simple.
- **`tview.Flex` for linear layouts**, `tview.Grid` for tabular. Avoid nesting `Flex` within `Flex` within `Flex` more than three deep — flatten by promoting children into the parent with explicit proportions.
- **One global `SetInputCapture` for quit keys.** Per-widget captures for widget-specific shortcuts.
- **Async work goes through goroutines + `app.QueueUpdateDraw()`**. Never update widgets from a goroutine directly — it races with tview's render loop.

```go
go func() {
    data, err := api.Fetch(ctx)
    a.tui.QueueUpdateDraw(func() {
        if err != nil {
            status.SetText("error: " + err.Error())
            return
        }
        list.Clear()
        for _, d := range data {
            list.AddItem(d.Name, "", 0, nil)
        }
    })
}()
```

- **`tcell` key constants**, not raw runes, for function keys and modifiers. Runes are fine for letters.
- **Context cancellation** for every goroutine that does I/O. When the app quits (`Stop()`), you need to unblock those goroutines — carry a `ctx` from `App` and cancel it in `Stop()`.

### Styling

tview uses `tcell.Color` constants and markup tags:

```go
text := "[yellow::b]warning[::-] something happened"
view := tview.NewTextView().SetDynamicColors(true).SetText(text)
```

Keep colours in `internal/ui/styles.go` as named constants:

```go
var (
    colorAccent  = tcell.NewRGBColor(255, 200, 0)
    colorError   = tcell.ColorRed
    colorNeutral = tcell.ColorWhite
)
```

### Anti-patterns

- **Updating widgets from a goroutine without `QueueUpdateDraw`.** Causes tearing and data races.
- **Creating a new `tview.Application` mid-run.** There's exactly one per process; reach for `SwitchToPage` or `SetRoot` instead.
- **Blocking the main goroutine inside an input handler.** Input handlers run on the render goroutine; any blocking call freezes the UI. Offload to a goroutine + `QueueUpdateDraw`.
- **Reinventing modals.** `tview.Modal` exists. So do `Form`, `InputField`, `DropDown`. Use them before hand-rolling.
- **Globals for app state.** Hang state off your `App` struct and close over it in handlers. Same reason as the Bubbletea version — testability and clarity.
