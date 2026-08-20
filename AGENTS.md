# AGENTS.md — AI Prototype Gradio WebUI

## Project Summary

This is a **prototype Gradio-based web UI** designed as a reusable starting point for building AI-powered web interfaces. It provides foundational scaffolding — multi-user management, project workspaces, model downloading, hardware monitoring, and i18n — on top of which domain-specific AI features can be added.

The application is a **self-contained, portable Windows application** that bundles its own embedded Python, Git, FFmpeg, and CUDA toolkit paths. It runs offline-first (HuggingFace/Transformers are set to offline mode by default) and uses a custom virtual environment stored in `env/`.

---

## Architecture Overview

```
webui.bat                  ← Entry point: sets paths, launches Gradio app
├── bat/                   ← Build, install, and environment scripts
│   ├── paths.bat          ← Defines ALL environment variables and paths
│   ├── site.bat           ← Configures Python sitecustomize.py at launch
│   ├── install.bat        ← Interactive installer (Python, Git, FFmpeg, pip, torch, llama.cpp)
│   ├── requirments.txt    ← pip dependencies (note: filename has typo, preserve it)
│   ├── freeze.bat         ← Freeze current packages
│   └── python.bat         ← Direct Python access
├── bin/                   ← Portable binaries
│   ├── python/            ← Embedded Python 3.13.x
│   ├── github/            ← Portable Git
│   └── ffmpeg/            ← Portable FFmpeg
├── env/                   ← Virtual environment (Lib/site-packages, Scripts)
├── whl/                   ← Pre-compiled wheel files (e.g., sageattn)
└── wui/                   ← Application source code (the main codebase)
    ├── app.py             ← Gradio Blocks entry point, top-level layout
    ├── main.py            ← HOME tab: user/project CRUD, system monitor
    ├── models.py          ← MODELS tab: HuggingFace model download/listing
    ├── wui.json           ← Runtime config (language, active user, active project)
    ├── core/              ← Core library
    │   ├── __init__.py
    │   └── core.py        ← Global state, config I/O, Translator, user/project helpers
    ├── locales/           ← i18n translation files
    │   ├── en_US.json
    │   └── tr_TR.json
    ├── assets/
    │   └── css/
    │       └── gradio.css ← Custom Gradio theme overrides
    ├── users/             ← Per-user data directories
    │   └── <username>/
    │       └── projects/
    │           └── <projectname>/
    └── temp/              ← Gradio temp files (GRADIO_TEMP_DIR)
```

---

## Key Modules

### `wui/app.py` — Application Entry Point

- Creates the root `gr.Blocks` layout with a header row (app title, user/project/language selectors).
- Defines two top-level tabs: **HOME** and **MODELS**.
- Wires up event handlers for user selection, project selection, and language switching.
- Runs a `gr.Timer` (5s interval) to auto-refresh the project list from disk.
- Launches on `http://127.0.0.1:7860` with dark theme and custom CSS.

### `wui/main.py` — HOME Tab

- **User Management**: Create, rename, delete users. Each user gets a folder under `wui/users/`.
- **Project Management**: Create, rename, delete projects within the active user's `projects/` subfolder.
- **System Monitor**: Real-time CPU, RAM, GPU, and VRAM usage bars (2s refresh via `gr.Timer`), using `psutil` and `pynvml`.
- **Active Project Info**: File count and total size of the selected project folder.

### `wui/models.py` — MODELS Tab

- Download models from HuggingFace Hub (full snapshot or single file).
- Temporarily disables offline mode during download, then restores it.
- Lists cached models by scanning the HF cache directory (`models/hf/hf_cache/`).

### `wui/core/core.py` — Core Library

- **Global State**: Module-level variables (`user_name`, `project_name`, `user_path`, `project_path`, etc.) used across the app. These are mutated at runtime — the app uses module-level state, not classes.
- **Config I/O**: `load_wui()` / `save_wui()` read/write `wui.json` with keys: `wui_lang`, `wui_user`, `wui_project`.
- **Translator**: The `_()` function is a `Translator` callable that loads a locale JSON file and returns translated strings by key, falling back to the key itself.
- **User/Project Helpers**: `list_users()`, `list_projects()`, `delete_user()`, `delete_project()` operate on the filesystem.
- **Hardcoded Paths** (lines 18-24): Contains references to a ComfyUI installation (`S:\ComfyUI\...`). These are development-only paths and should be made configurable or removed when forking.

### `wui/locales/` — Internationalization

- JSON files named `{lang}_{COUNTRY}.json` (e.g., `en_US.json`, `tr_TR.json`).
- The language code prefix (e.g., `en`) is what gets stored in `wui.json` and displayed in the dropdown.
- All UI strings are keyed (e.g., `HOME_BTN_CREATE`, `HOME_CPU_USAGE`). To add a language, create a new JSON file with the same keys.

---

## Environment & Runtime

| Setting             | Value                                              |
| ------------------- | -------------------------------------------------- |
| **Python**          | 3.13.x (embedded, portable)                        |
| **Framework**       | Gradio (`gr.Blocks`)                               |
| **Package Manager** | pip + uv (installed into `env/Lib/site-packages`)  |
| **CUDA**            | v13.3 (NVIDIA GPU Computing Toolkit)               |
| **PyTorch**         | 2.13.0 + CUDA cu133                                |
| **Server**          | `http://127.0.0.1:7860` (dark theme by default)    |
| **Offline Mode**    | HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1 (default) |

### Key Environment Variables (set in `bat/paths.bat`)

- `ARTHA_HOME_DIR` — Points to the `wui/` directory.
- `HF_HOME`, `HF_HUB_CACHE` — HuggingFace cache under `models/hf/`.
- `TORCH_HOME` — PyTorch model cache under `models/torch/`.
- `OLLAMA_MODELS` — Ollama model storage under `models/ollama/`.
- `GRADIO_TEMP_DIR` — Set to `wui/temp/`.
- `HF_TOKEN`, `GEMINI_API_KEY` — API tokens (empty by default, set in `paths.bat`).

---

## Development Conventions

### Code Style

- **Python**: No explicit linter config. Code uses 4-space indentation, f-strings, and type-less function signatures.
- **Global State Pattern**: The app uses mutable module-level variables in `core.py` rather than class instances. When modifying state, update the module attributes directly (e.g., `core.project_name = "new_name"`).
- **Gradio Patterns**: UI is built using `gr.Blocks` context managers. Event wiring is done via `.click()`, `.change()`, and `.success()` chaining. Timer-based polling is used for auto-refresh.

### Adding a New Tab

1. Create a new module (e.g., `wui/inference.py`) with a `create_*_tab()` function.
2. Import it in `app.py` and add a `with gr.Tab(_(\"TAB_KEY\")):` block.
3. Add the tab label key to all locale JSON files.

### Adding UI Strings

1. Add the key-value pair to **all** JSON files in `wui/locales/`.
2. Use `_("YOUR_KEY")` in Python code to reference it.

### Adding a New Language

1. Create a new file in `wui/locales/` named `{lang}_{COUNTRY}.json` (e.g., `de_DE.json`).
2. Copy all keys from `en_US.json` and translate the values.
3. The language will auto-appear in the dropdown on next launch.

### User/Project Data Model

- Users are simply **directories** under `wui/users/`.
- Projects are **directories** under `wui/users/<username>/projects/`.
- There is no database — all state is filesystem-based.
- A default user `artha` and project `myproject` are auto-created if none exist.

---

## Dependencies (from `bat/requirments.txt`)

| Category              | Packages                                                                                                                                                                        |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **UI**                | `gradio`                                                                                                                                                                        |
| **RAG/Orchestration** | `langchain`, `langchain-community`, `langchain-chroma`, `langchain-ollama`, `langchain-huggingface`, `sentence-transformers`                                                    |
| **Deep Learning**     | `torch`, `torchaudio`, `torchvision`, `transformers`, `tokenizers`, `accelerate`, `safetensors`, `bitsandbytes`, `gguf`, `numpy`, `triton-windows`, `huggingface_hub`, `hf-xet` |
| **Data**              | `pypdf`                                                                                                                                                                         |
| **Image**             | `pillow`, `diffusers`, `einops`, `opencv-python`                                                                                                                                |
| **Audio**             | `soundfile`                                                                                                                                                                     |
| **Monitoring**        | `psutil`, `nvidia-ml-py`                                                                                                                                                        |

---

## How to Run

```bat
:: First-time setup (interactive — installs Python, Git, FFmpeg, packages, torch)
bat\install.bat

:: Launch the web UI
webui.bat
```

The launcher auto-opens `http://127.0.0.1:7860/?__theme=dark` in the browser after a short delay.

---

## Important Notes for AI Agents

1. **Do not modify files under `bin/`, `env/`, or `whl/`** — these are runtime binaries and installed packages.
2. **All application source code lives in `wui/`** — this is the only directory agents should edit.
3. **`wui.json` is runtime state** — it gets overwritten at startup and on every user/project change. Do not use it for persistent configuration.
4. **The filename `requirments.txt` is intentionally misspelled** — it is referenced by name in `install.bat`. Do not rename it without updating the reference.
5. **ComfyUI paths in `core.py`** (lines 18-24) are hardcoded development paths. They are guarded by `os.path.exists()` checks and are safe to ignore, but should be removed or made configurable in production.
6. **Offline mode is the default** — model downloads temporarily disable offline mode and restore it after. Keep this pattern when adding new download features.
7. **The app uses module-level mutable state** in `core.py`. Be aware of import-time side effects: importing `core.core` triggers config loading, directory creation, and state initialization.
