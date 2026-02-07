@echo off
echo ========================================
echo    RENOMBRADOR DE CREDENCIALES
echo ========================================
echo.

echo 1. Buscando archivos descargados...
echo.

set "downloads_folder=%USERPROFILE%\Downloads"
set "target_folder=C:\Users\equipo\Desktop\beatuploader"

echo Buscando en: %downloads_folder%
echo.

if not exist "%downloads_folder%\client_secret*.json" (
    echo ❌ No se encontraron credenciales en Descargas
    echo.
    echo SOLUCIÓN:
    echo 1. Ve a: https://console.cloud.google.com/apis/credentials
    echo 2. Crea credenciales OAuth tipo "Aplicación de escritorio"
    echo 3. Descarga el archivo JSON
    echo 4. Vuelve a ejecutar este script
    pause
    exit /b 1
)

echo ✅ Archivos encontrados:
dir "%downloads_folder%\client_secret*.json" /b

echo.
echo 2. Seleccionando el más reciente...
for /f "delims=" %%i in ('dir "%downloads_folder%\client_secret*.json" /b /od') do set "newest_file=%%i"

echo    Último archivo: %newest_file%
echo.

echo 3. Copiando y renombrando...
copy "%downloads_folder%\%newest_file%" "%target_folder%\client_secrets.json"

echo.
echo 4. Verificando...
if exist "%target_folder%\client_secrets.json" (
    echo ✅ Credenciales copiadas correctamente a:
    echo    %target_folder%\client_secrets.json
    echo.
    
    echo 5. Mostrando primeras líneas...
    echo ========================================
    more +1 "%target_folder%\client_secrets.json" | findstr /n "^" | findstr /b "1: 2: 3: 4: 5:"
    echo ========================================
    
    echo.
    echo 6. Eliminando token anterior...
    if exist "%target_folder%\token.pickle" (
        del "%target_folder%\token.pickle"
        echo ✅ token.pickle eliminado
    )
    
) else (
    echo ❌ Error al copiar las credenciales
)

echo.
echo ========================================
echo    ¡LISTO PARA USAR!
echo ========================================
echo Ejecuta: python beatuploader.py
pause