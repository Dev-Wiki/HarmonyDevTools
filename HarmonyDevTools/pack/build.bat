set version=1.0.0

if not "%~1"=="" (
    set version=%1
)

cd ../ && rmdir /s /q bin && rmdir /s /q obj 
cd pack

if not exist "output" (
    mkdir output
)

cd output
if exist "HarmonyTools-%version%.exe" (
    del /q /s HarmonyDevTools-%version%.exe
)
cd ../

dotnet publish ../../HarmonyDevTools/HarmonyDevTools.csproj -c Release -r win-x86 /p:PublishSingleFile=true /p:IncludeNativeLibrariesForSelfExtract=true /p:SelfContained=false -o ./output

if NOT %errorlevel%==0 @goto :FailureOnBuild

cd output && move HarmonyDevTools.exe HarmonyDevTools-%version%.exe && move HarmonyDevTools.pdb HarmonyDevTools-%version%.pdb && cd ../
xcopy ..\..\toolchains .\output\toolchains /E /I /Y
cd ../bin && del /q /s Release && cd ../pack

goto :eof

:FailureOnBuild
echo build project failure