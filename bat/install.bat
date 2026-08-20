@echo off
cd /d "%~dp0"

Title WEBUI INSTALL - %~dp0

call paths.bat

echo/
if exist "%ARTHA_GITHUB_BIN%" (
    goto GITUPDATE
) else (
    goto GITINSTALL
)

:GITUPDATE
set isgitup=
set /p "isgitup=GITHUB EXISTS. UPDATE GITHUB?[y/n]: "
if /i not "%isgitup%"=="y" goto GITSKIP
echo/
echo ...DELETING EXISTING GITHUB DIRECTORY...
echo/
rmdir /s /q %ARTHA_GITHUB_DIR%
goto GITDOWNLOAD

:GITINSTALL
set isgit=
set /p "isgit=INSTALL GITHUB?[y/n]: "
if /i not "%isgit%"=="y" goto GITSKIP

:GITDOWNLOAD
if not exist %ARTHA_GITHUB_DIR% md %ARTHA_GITHUB_DIR%

echo/
echo ...DOWNLOADING GITHUB...
echo/
curl -L -o %ARTHA_GITHUB_DIR%PortableGit.7z.exe %ARTHA_GITHUB_URL%

echo/
echo ...INSTALLING GITHUB...
echo/
%ARTHA_GITHUB_DIR%PortableGit.7z.exe

echo ...DELETING 7Z.EXE FILE...
echo/
del %ARTHA_GITHUB_DIR%PortableGit.7z.exe

echo ...MOVING GITHUB FILES...
echo/
xcopy %ARTHA_GITHUB_DIR%PortableGit %ARTHA_GITHUB_DIR% /s

echo/
echo ...DELETING TEMPORARY FOLDER...
echo/
rmdir /s /q %ARTHA_GITHUB_DIR%PortableGit

:GITSKIP

for /f "tokens=1,2 delims=." %%a in ("%ARTHA_PYTHON_VERSION%") do set ARTHA_PYTHON_DIGITS=%%a%%b

if not exist %ARTHA_BIN_DIR% (
md %ARTHA_BIN_DIR%
)

if exist "%PYTHON%" (
    goto PYUPDATE
) else (
    goto PYINSTALL
)

:PYUPDATE
echo/
set ispyup=
set /p "ispyup=PYTHON EXISTS. UPDATE PYTHON?[y/n]: "
if /i not "%ispyup%"=="y" goto PYSKIP
echo/
echo ...DELETING EXISTING PYTHON DIRECTORY...
echo/
rmdir /s /q %ARTHA_PYTHON_DIR%
goto PYDOWNLOAD

:PYINSTALL
set ispy=
set /p "ispy=INSTALL PYTHON?[y/n]: "
if /i not "%ispy%"=="y" goto PYSKIP

:PYDOWNLOAD
if not exist %ARTHA_PYTHON_DIR% md %ARTHA_PYTHON_DIR%
echo/
echo ...DOWNLOADING PYTHON...
echo/
curl -o %ARTHA_PYTHON_DIR%python%ARTHA_PYTHON_VERSION%.zip %ARTHA_PYTHON_URL%%ARTHA_PYTHON_VERSION%/python-%ARTHA_PYTHON_VERSION%-embed-amd64.zip

echo/
echo ...EXTRACTING PYTHON...
echo/

tar -xf %ARTHA_PYTHON_DIR%python%ARTHA_PYTHON_VERSION%.zip -C %ARTHA_PYTHON_DIR%

echo ...DELETING ZIP FILE...
echo/

del %ARTHA_PYTHON_DIR%python%ARTHA_PYTHON_VERSION%.zip

if not exist %ARTHA_PYTHON_DIR%Lib (
echo ...CREATING PYTHON SUB DIRECTORIES...
echo/
md %ARTHA_PYTHON_DIR%Lib
md %ARTHA_PYTHON_DIR%DLLs
tar -xf %ARTHA_PYTHON_DIR%python%ARTHA_PYTHON_DIGITS%.zip -C %ARTHA_PYTHON_DIR%Lib
xcopy %ARTHA_PYTHON_DIR%*.dll %ARTHA_PYTHON_DIR%DLLs /y
xcopy %ARTHA_PYTHON_DIR%*.pyd %ARTHA_PYTHON_DIR%DLLs /y
)

echo/
echo ...DOWNLOADING NUGET...
echo/
set ARTHA_NUGET_ZIP=%ARTHA_BIN_DIR%python_nuget.zip
set ARTHA_NUGET_DIR=%ARTHA_BIN_DIR%python_nuget_extracted
curl -L -o "%ARTHA_NUGET_ZIP%" "https://www.nuget.org/api/v2/package/python/%ARTHA_PYTHON_VERSION%"

echo/
echo ...EXTRACTING ARCHIVE...
echo/
if not exist "%ARTHA_NUGET_DIR%" md "%ARTHA_NUGET_DIR%"
tar -xf "%ARTHA_NUGET_ZIP%" -C "%ARTHA_NUGET_DIR%"

echo ...COPYING INCLUDE AND LIBS...
echo/
xcopy "%ARTHA_NUGET_DIR%\tools\include" "%ARTHA_PYTHON_DIR%include" /E /I /Y
xcopy "%ARTHA_NUGET_DIR%\tools\libs" "%ARTHA_PYTHON_DIR%libs" /E /I /Y

echo/
echo ...CLEANING UP TEMPORARY FILES...
echo/
del "%ARTHA_NUGET_ZIP%"
rmdir /s /q "%ARTHA_NUGET_DIR%"

echo/
echo ...CONFIGURING PYTHON...
echo/

echo .\Lib>%ARTHA_PYTHON_DIR%python%ARTHA_PYTHON_DIGITS%._pth
echo .\Scripts>>%ARTHA_PYTHON_DIR%python%ARTHA_PYTHON_DIGITS%._pth
echo .>>%ARTHA_PYTHON_DIR%python%ARTHA_PYTHON_DIGITS%._pth
echo import site>>%ARTHA_PYTHON_DIR%python%ARTHA_PYTHON_DIGITS%._pth

echo import site>%ARTHA_PYTHON_DIR%Lib\sitecustomize.py
echo site.addsitedir(r"%ARTHA_ENV_DIR%Lib\site-packages")>>%ARTHA_PYTHON_DIR%Lib\sitecustomize.py

echo ...DOWNLOADING PIP...
echo/
curl -o %ARTHA_PYTHON_DIR%get-pip.py %ARTHA_PIP_URL%

echo/
echo ...INSTALLING PIP...
echo/
%PYTHON% %ARTHA_PYTHON_DIR%get-pip.py --no-warn-script-location

echo/
echo ...UPGRADING PIP...
echo/
%PYTHON% -m pip install --upgrade pip scikit-build-core cmake ninja

echo/
echo ...INSTALLING UV...
echo/
%PYTHON% -m pip install uv

:PYSKIP

echo/
if exist "%ARTHA_ENV_DIR%" (
    goto ENVUPDATE
) else (
    goto ENVINSTALL
)

:ENVUPDATE
set isenvup=
set /p "isenvup=ENV EXISTS. FORCE INSTALL REQUIREMENTS?[y/n]: "
if /i not "%isenvup%"=="y" goto ENVSKIP
goto ENVDOWNLOAD

:ENVINSTALL
set isenv=
set /p "isenv=INSTALL REQUIREMENTS?[y/n]: "
if /i not "%isenv%"=="y" goto ENVSKIP

:ENVDOWNLOAD
if not exist %ARTHA_ENV_DIR% (
echo/
echo ...CREATING ENV DIRECTORY...

md %ARTHA_ENV_DIR%Lib\site-packages
md %ARTHA_ENV_DIR%Scripts
)

echo/
echo ...PURGING CACHE...
echo/
%PYTHON% -m pip cache purge

echo/
echo ...INSTALLING REQUIREMENTS...
echo/
%PYTHON% -m pip install -U --force-reinstall -r requirments.txt --target %ARTHA_ENV_DIR%Lib\site-packages

:ENVSKIP

echo/
set istorch=
set /p "istorch=INSTALL TORCH %ARTHA_TORCH_VER% WITH CUDA?[y/n]: "

if /i not "%istorch%"=="y" goto CUDASKIP

echo/
echo ...INSTALLING TORCH %ARTHA_TORCH_VER% WITH CUDA %ARTHA_CUDA_TAG%...
echo/
%PYTHON% -m pip install -U torch==%ARTHA_TORCH_VER% torchvision --extra-index-url https://download.pytorch.org/whl/%ARTHA_CUDA_TAG% --target %ARTHA_ENV_DIR%Lib\site-packages
echo/

:CUDASKIP

echo/
set isllama=
set /p "isllama=INSTALL LLAMA.CPP?[y/n]: "

if /i not "%isllama%"=="y" goto LLAMASKIP

if not exist %ARTHA_LLMCCP_DIR% (
echo/
echo ...CREATING LLAMA CCP DIRECTORY...
echo/
md %ARTHA_LLMCCP_DIR%
) else (
echo/
echo ...DELETING EXISTING LLAMA CCP DIRECTORY...
echo/
rmdir /s /q %ARTHA_LLMCCP_DIR%
md %ARTHA_LLMCCP_DIR%
)

echo ...DOWNLOADING LLAMA CCP ...
echo/
curl -L -o %ARTHA_LLMCCP_DIR%llama.zip %ARTHA_LLMCCP_URL%

echo/
echo ...EXTRACTING LLAMA CCP...
echo/
	
tar -xf %ARTHA_LLMCCP_DIR%llama.zip -C %ARTHA_LLMCCP_DIR%

echo ...DELETING ZIP FILE...
echo/
	
del %ARTHA_LLMCCP_DIR%llama.zip

set CMAKE_ARGS=-DGGML_CUDA=on
set FORCE_CMAKE=1
set PATH=%PATH%;%ARTHA_GITHUB_DIR%;%ARTHA_GITHUB_DIR%bin;%ARTHA_GITHUB_DIR%cmd

if exist "%ARTHA_BASE_DIR%bat\whl\llama_cpp_python*.whl" (
	echo/
    echo ...INSTALLING PRE-COMPILED LLAMA CCP WHEEL...
    echo/
    for %%f in ("%ARTHA_BASE_DIR%bat\whl\llama_cpp_python*.whl") do (
        %PYTHON% -m pip install --upgrade --force-reinstall --no-cache-dir "%%f" --target %ARTHA_ENV_DIR%Lib\site-packages
    )
) else (
	echo/
    echo ...COMPILING LLAMA CCP AND SAVING WHEEL...
    echo/
    if not exist "%ARTHA_BASE_DIR%bat\whl" md "%ARTHA_BASE_DIR%bat\whl"
    %PYTHON% -m pip wheel --wheel-dir="%ARTHA_BASE_DIR%bat\whl" git+https://github.com/abetlen/llama-cpp-python.git
    for %%f in ("%ARTHA_BASE_DIR%bat\whl\llama_cpp_python*.whl") do (
        %PYTHON% -m pip install --upgrade --force-reinstall --no-cache-dir "%%f" --target %ARTHA_ENV_DIR%Lib\site-packages
    )
)

:LLAMASKIP

echo/
if exist "%ARTHA_FFMPEG_BIN%" (
    goto MPEGUPDATE
) else (
	goto MPEGINSTALL
)

:MPEGUPDATE

set isffmpegup=
set /p "isffmpegup=FFMPEG EXISTS. UPDATE FFMPEG?[y/n]: "

if /i not "%isffmpegup%"=="y" goto MPEGSKIP 

echo/
echo ...DELETING EXISTING FFMPEG DIRECTORY...
echo/
rmdir /s /q %ARTHA_FFMPEG_DIR%
goto MPEGDOWNLOAD

:MPEGINSTALL
set isffmpeg=
set /p "isffmpeg=INSTALL FFMPEG?[y/n]: "

if /i not "%isffmpeg%"=="y" goto MPEGSKIP

:MPEGDOWNLOAD

if not exist %ARTHA_FFMPEG_DIR% md %ARTHA_FFMPEG_DIR%

echo/
echo ...DOWNLOADING FFMPEG...
echo/
curl -L -o %ARTHA_FFMPEG_DIR%ffmpeg.zip %ARTHA_FFMPEG_URL%

echo/
echo ...EXTRACTING FFMPEG...
echo/
	
tar -xf %ARTHA_FFMPEG_DIR%ffmpeg.zip --strip-components=1 -C %ARTHA_FFMPEG_DIR%
	
echo ...DELETING ZIP FILE...
echo/
	
del %ARTHA_FFMPEG_DIR%ffmpeg.zip

:MPEGSKIP

:command
echo/
echo ..........
echo ...DONE...
echo ..........
echo/
cmd /k

:exit
echo/
echo Install failed. Press a button to exit...
pause >nul
exit