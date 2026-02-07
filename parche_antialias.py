# parche_antialias.py
import sys
import PIL.Image

print("=== PARCHE PARA PILLOW ANTIALIAS ===")
print(f"Python: {sys.version}")
print(f"Pillow versión: {PIL.__version__}")

# Verificar si ANTIALIAS existe
if hasattr(PIL.Image, 'ANTIALIAS'):
    print("✅ ANTIALIAS ya existe, no se necesita parche")
else:
    print("❌ ANTIALIAS no existe, aplicando parche...")
    
    # Para Pillow >= 10.0
    if hasattr(PIL.Image, 'Resampling'):
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
        print("✅ Parche aplicado: ANTIALIAS = Resampling.LANCZOS")
    else:
        # Para versiones muy raras
        PIL.Image.ANTIALIAS = 1  # Valor por defecto antiguo
        print("✅ Parche aplicado: ANTIALIAS = 1")
    
    print("✅ Parche completado exitosamente")

# Probar
try:
    test_value = PIL.Image.ANTIALIAS
    print(f"✅ ANTIALIAS ahora vale: {test_value}")
except Exception as e:
    print(f"❌ Error al probar parche: {e}")