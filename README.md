# needlings

Interactive exercises for [sphinx-needs](https://sphinx-needs.readthedocs.io/) 8.0 —
rustlings, but for engineering-as-code.

## Quickstart

### In GitHub Codespaces (recommended)

Click **Code → Open with Codespaces**. The devcontainer pre-installs everything
(uv, Python 3.12, `ubc`, the ubCode VS Code extension). When it finishes:

```bash
uv run needlings watch
```

### Locally

```bash
git clone https://github.com/<owner>/needlings
cd needlings
curl -LsSf https://astral.sh/uv/install.sh | sh     # if you don't have uv
uv sync --extra dev
uv run needlings init
uv run needlings watch
```

You'll also want:

- [ubCode](https://marketplace.visualstudio.com/items?itemName=useblocks.ubcode)
  — the recommended VS Code extension.
- The [`ubc`](https://ubcode.useblocks.com/ubc/installation.html) binary, used
  from chapter 6 onward.

### ubCode for open source

needlings is open source, so useblocks' **free open-source tier** applies.
Request a key via the ubCode docs and activate it with
`ubc license activate <KEY>`. You only need this to complete chapter 6+.

## Commands

| Command                    | What it does                              |
| -------------------------- | ----------------------------------------- |
| `needlings watch`          | Primary loop: watch + verify-on-save      |
| `needlings run <id>`       | One-shot verify of one exercise           |
| `needlings hint <id>`      | Print the exercise's hint                 |
| `needlings list`           | Show all chapters and exercises           |
| `needlings progress`       | Completed / total + full tree             |
| `needlings reset <id>`     | Restore starter to pristine state         |
| `needlings verify --all`   | CI: apply every solution, expect pass     |
| `needlings verify --starters` | CI: apply every starter, expect fail   |
| `needlings new-exercise <chapter>/<slug> --name "…"` | Scaffold a new exercise |
| `needlings doctor`         | Diagnose environment problems             |

## Curriculum (v0.1)

**Chapter 1 — Setup & first need** (5 exercises). Subsequent chapters are
authored in later releases. See `docs/superpowers/plans/` for the roadmap.

## Contributing

Exercises live under `exercises/<chapter>/<slug>/`. Each exercise has a
`starter/` (with a `.pristine/` snapshot for reset), `solution/`, and
`info.toml`. CI enforces that every starter fails and every solution passes.

To add an exercise:

```bash
uv run needlings new-exercise 01-setup/06-new --name "My new exercise"
```

Then fill in the starter, pristine, solution, and hint.

## License

MIT
