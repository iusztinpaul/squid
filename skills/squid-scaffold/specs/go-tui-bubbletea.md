---
name: go-tui-bubbletea
description: Bubbletea (Elm-style Model/Update/View + Lip Gloss) usage for a Go TUI — root model, keymap table, Cmd patterns, error messages, testing Update(). Read from go-tui.md when Bubbletea is the chosen framework.
---

## Go TUI — Bubbletea

Opinionated Bubbletea usage. Read this alongside [`go-tui.md`](go-tui.md) (layout, entry point, Makefile targets).

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
