---
name: go-tui-tview
description: tview (widget composition — Pages/Flex/Grid) usage for a Go TUI — single Application, QueueUpdateDraw for async, tcell keys, styling. Read from go-tui.md when tview is the chosen framework.
---

## Go TUI — tview

Opinionated tview usage. Read this alongside [`go-tui.md`](go-tui.md) (layout, entry point, Makefile targets).

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
- **Globals for app state.** Hang state off your `App` struct and close over it in handlers — testability and clarity.
