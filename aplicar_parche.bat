@echo off
echo === APLICADOR DE PARCHE PILLOW ===
echo.

echo 1. Creando respaldo del archivo original...
if exist beatuploader.py (
    copy beatuploader.py beatuploader_backup.py
    echo ✅ Respaldo creado: beatuploader_backup.py
)

echo.
echo 2. Aplicando parche...
echo.

REM Crear script de parche temporal
echo # PARCHE PARA PILLOW ANTIALIAS > temp_patch.py
echo import sys >> temp_patch.py
echo import PIL.Image >> temp_patch.py
echo import PIL >> temp_patch.py
echo. >> temp_patch.py
echo print("Python:", sys.version[:20]) >> temp_patch.py
echo print("Pillow:", PIL.__version__) >> temp_patch.py
echo. >> temp_patch.py
echo if not hasattr(PIL.Image, "ANTIALIAS"): >> temp_patch.py
echo     if hasattr(PIL.Image, "Resampling"): >> temp_patch.py
echo         PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS >> temp_patch.py
echo         print("ANTIALIAS = Resampling.LANCZOS") >> temp_patch.py
echo     else: >> temp_patch.py
echo         PIL.Image.ANTIALIAS = 1 >> temp_patch.py
echo         print("ANTIALIAS = 1") >> temp_patch.py
echo else: >> temp_patch.py
echo     print("ANTIALIAS ya existe") >> temp_patch.py

python temp_patch.py

echo.
echo 3. Modificando beatuploader.py...
echo.

REM Verificar si ya tiene el parche
findstr /C:"PARCHE PARA PILLOW ANTIALIAS" beatuploader.py >nul
if %errorlevel% equ 0 (
    echo ✅ El archivo ya tiene el parche
) else (
    echo 🔧 Insertando parche en beatuploader.py...
    
    REM Crear nuevo archivo con el parche
    echo # =========== PARCHE PARA PILLOW ANTIALIAS =========== > beatuploader_new.py
    echo import PIL.Image >> beatuploader_new.py
    echo import PIL >> beatuploader_new.py
    echo. >> beatuploader_new.py
    echo # Arreglar ANTIALIAS para versiones nuevas de Pillow >> beatuploader_new.py
    echo if not hasattr(PIL.Image, "ANTIALIAS"): >> beatuploader_new.py
    echo     if hasattr(PIL.Image, "Resampling"): >> beatuploader_new.py
    echo         PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS >> beatuploader_new.py
    echo     else: >> beatuploader_new.py
    echo         PIL.Image.ANTIALIAS = 1 >> beatuploader_new.py
    echo     print("🔧 Parche Pillow aplicado") >> beatuploader_new.py
    echo # =========== FIN DEL PARCHE =========== >> beatuploader_new.py
    echo. >> beatuploader_new.py
    
    REM Agregar el contenido original
    type beatuploader.py >> beatuploader_new.py
    
    REM Reemplazar
    move /Y beatuploader_new.py beatuploader.py
    echo ✅ Parche aplicado exitosamente
)

echo.
echo 4. Limpiando...
del temp_patch.py 2>nul

echo.
echo ========================================
echo ✅ PARCHE COMPLETADO
echo ========================================
echo.
echo Ahora ejecuta: python beatuploader.py
echo.
pause