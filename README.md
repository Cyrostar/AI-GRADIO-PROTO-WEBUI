# AI Prototype Gradio WebUI

A reusable, self-contained Gradio web interface designed as a starting point for building AI-powered applications.

Instead of building foundational UI components from scratch for every new AI project, this prototype provides the essential scaffolding—user management, model caching, hardware monitoring, and offline support—allowing you to focus immediately on your domain-specific AI logic (like LLMs, image generation, or RAG).

## ✨ Features

- **Portable & Self-Contained:** Bundles its own embedded Python 3.13, portable Git, FFmpeg, and CUDA toolkit. No system-level installations required.
- **Offline-First Architecture:** Configured by default to prevent unexpected internet pings. Transformers and HuggingFace Hub libraries are set to offline mode, ensuring strict data privacy.
- **Multi-User Workspaces:** Built-in file system structure to manage multiple users and isolate their distinct project directories.
- **Model Management:** Dedicated UI tab to download specific models or snapshots directly from the Hugging Face Hub, with local cache scanning.
- **Live Hardware Monitoring:** Real-time visual meters for CPU, System RAM, GPU, and VRAM utilization.
- **Internationalization (i18n):** Easy-to-extend locale system. Currently ships with English (`en_US`) and Turkish (`tr_TR`) support.
- **Custom Theming:** Overridden Gradio CSS for a sleek, consistent dark-mode experience.

## 🚀 Getting Started

### Prerequisites

Because the environment is fully portable, you only need a Windows machine with an NVIDIA GPU (for CUDA acceleration).

### Installation

1. Clone or download the repository.
2. Run the interactive setup script to download and configure Python, Git, FFmpeg, and `pip` dependencies (including PyTorch and `llama.cpp`):
  
  ```bat
  bat\install.bat
  ```
  
  *(Note: This will download several gigabytes of dependencies on the first run).*

### Launching the App

Once installed, start the web interface by running:

```bat
webui.bat
```

The launcher will initialize the environment and automatically open `http://127.0.0.1:7860` in your default web browser.

## 📂 Architecture Overview

- **`wui/`**: The core Gradio application source code.
  - `app.py`: The entry point and main layout router.
  - `core/core.py`: Global state management and configuration logic.
  - `locales/`: JSON translation files.
- **`bat/`**: Installation, environment configuration, and launcher scripts.
- **`bin/`**: Directory for portable binary tools (Python, Git, FFmpeg, llama.cpp tools).
- **`env/`**: The isolated Python virtual environment containing downloaded packages.
- **`whl/`**: Local cache for compiled Python wheels (like `llama_cpp_python`) to speed up offline re-installations.

## 🛠 Extending the Prototype

To add a new AI capability (e.g., an LLM Chat tab or Image Generation tab):

1. Create a new Python file in `wui/` (e.g., `chat.py`).
2. Build your UI inside a function that returns a `gr.Column` or `gr.Tab`.
3. Import your module into `wui/app.py` and mount it under the `gr.Tabs()` block.
4. Add your new UI string keys to the JSON files in `wui/locales/`.
