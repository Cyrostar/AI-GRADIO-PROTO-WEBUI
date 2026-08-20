@echo off

::MASTER CONFIGURATION
set ARTHA_PYTHON_VERSION=3.13.14
set ARTHA_TORCH_VER=2.13.0
set ARTHA_CUDA_TAG=cu133
set ARTHA_NVCUDA_VER=v13.3

::DOWNLOAD LOCATIONS

set ARTHA_PYTHON_URL=https://www.python.org/ftp/python/
set ARTHA_PIP_URL=https://bootstrap.pypa.io/get-pip.py
set ARTHA_GITHUB_URL=https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/PortableGit-2.43.0-64-bit.7z.exe
set ARTHA_FFMPEG_URL=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
set ARTHA_LLMCCP_URL=https://github.com/ggml-org/llama.cpp/releases/download/b10488/llama-b10488-bin-win-cuda-13.3-x64.zip

::PATHS

set ARTHA_HOME=wui
set ARTHA_PATH=%~dp0
set ARTHA_BASE_DIR=%ARTHA_PATH:~0,-4%
set ARTHA_HOME_DIR=%ARTHA_BASE_DIR%%ARTHA_HOME%\
set ARTHA_BIN_DIR=%ARTHA_BASE_DIR%bin\
set ARTHA_PYTHON_DIR=%ARTHA_BIN_DIR%python\
set ARTHA_PYTHON_SCR=%ARTHA_PYTHON_DIR%Scripts\

set PYTHON=%ARTHA_PYTHON_DIR%python.exe
set ARTHA_ENV_DIR=%ARTHA_BASE_DIR%env\

set ARTHA_GITHUB_DIR=%ARTHA_BIN_DIR%github\
set ARTHA_FFMPEG_DIR=%ARTHA_BIN_DIR%ffmpeg\

set ARTHA_GITHUB_BIN=%ARTHA_GITHUB_DIR%bin\
set ARTHA_GITHUB_USR_BIN=%ARTHA_GITHUB_DIR%usr\bin\
set ARTHA_FFMPEG_BIN=%ARTHA_FFMPEG_DIR%bin\
set ARTHA_LLMCCP_DIR=%ARTHA_BIN_DIR%llmccp\

set PATH=C:\Windows;C:\Windows\system32;%ARTHA_PYTHON_DIR%;%ARTHA_PYTHON_SCR%;%ARTHA_HOME_DIR%

if exist "%ARTHA_GITHUB_BIN%" set PATH=%PATH%;%ARTHA_GITHUB_BIN%
if exist "%ARTHA_GITHUB_USR_BIN%" set PATH=%PATH%;%ARTHA_GITHUB_USR_BIN%
if exist "%ARTHA_FFMPEG_BIN%" set PATH=%PATH%;%ARTHA_FFMPEG_BIN%
if exist "%ARTHA_LLMCCP_DIR%" set PATH=%PATH%;%ARTHA_LLMCCP_DIR%

::EVIRONMENT VARIABLES

set PYTHONUTF8=1
set TORCHDYNAMO_DISABLE=1

set UV_TOOL_BIN_DIR=%ARTHA_BIN_DIR%hf\
set HF_HOME=%ARTHA_BASE_DIR%models\hf\
set HF_HUB_CACHE=%ARTHA_BASE_DIR%models\hf\hf_cache\
set XDG_CACHE_HOME=%ARTHA_BASE_DIR%models\
set TORCH_HOME=%ARTHA_BASE_DIR%models\torch\
set TORCH_HF_HOME=%ARTHA_BASE_DIR%models\huggingface\
set OLLAMA_MODELS=%ARTHA_BASE_DIR%models\ollama\

::CUDA

set ARTHA_NVCUDA_DIR=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\%ARTHA_NVCUDA_VER%\
set ARTHA_NVCUDA_BIN=%ARTHA_NVCUDA_DIR%bin\
set ARTHA_NVCUDA_LIB=%ARTHA_NVCUDA_DIR%lib\
set ARTHA_NVCUDA_NVP=%ARTHA_NVCUDA_DIR%libnvvp\
set ARTHA_NVCUDA_INC=%ARTHA_NVCUDA_DIR%include\

if exist "%ARTHA_NVCUDA_DIR%" set PATH=%PATH%;%ARTHA_NVCUDA_BIN%
if exist "%ARTHA_NVCUDA_DIR%" set PATH=%PATH%;%ARTHA_NVCUDA_LIB%
if exist "%ARTHA_NVCUDA_DIR%" set PATH=%PATH%;%ARTHA_NVCUDA_NVP%
if exist "%ARTHA_NVCUDA_DIR%" set PATH=%PATH%;%ARTHA_NVCUDA_INC%

::VC

set ARTHA_VSCODE_CLD=C:\Program Files\Microsoft Visual Studio\2022\Professional\
set ARTHA_VSCODE_CLE=%ARTHA_VSCODE_CLD%VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\

if exist "%ARTHA_VSCODE_CLE%cl.exe" set PATH=%PATH%;%ARTHA_VSCODE_CLE%

::TRITON

set TORCHINDUCTOR_FORCE_DISABLE_CACHES=1
set TORCHINDUCTOR_CACHE_DIR=%ARTHA_BASE_DIR%models\torch\cache
set TORCHDYNAMO_VERBOSE=1

::TEMP DIRECTORY

mkdir "%ARTHA_HOME_DIR%\temp" 2>nul
set "TMP=%ARTHA_HOME_DIR%\temp"
set "TEMP=%ARTHA_HOME_DIR%\temp"
set "GRADIO_TEMP_DIR=%ARTHA_HOME_DIR%\temp"

::TOKENS

set HF_TOKEN=

::KEYS

set GEMINI_API_KEY=