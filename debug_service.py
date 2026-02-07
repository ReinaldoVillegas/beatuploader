import pickle
import os
from googleapiclient.discovery import build

print("🔍 DEBUG: Verificando servicio...")

# 1. Cargar token
if not os.path.exists('token.pickle'):
    print("❌ No hay token.pickle")
    exit()

with open('token.pickle', 'rb') as f:
    creds = pickle.load(f)
print("✅ Token cargado")

# 2. Crear servicio (como test_rapido.py)
service = build('youtube', 'v3', credentials=creds)
print("✅ Servicio creado")

# 3. Verificar que funciona
try:
    response = service.channels().list(part='snippet', mine=True).execute()
    print(f"✅ API funciona. Canal: {response['items'][0]['snippet']['title']}")
except Exception as e:
    print(f"❌ Error API: {e}")

# 4. Ahora prueba CON tu clase
print("\n🔍 Probando con TU clase...")

import sys
sys.path.append('.')
try:
    from beatuploader import BatchYouTubeUploader
    
    uploader = BatchYouTubeUploader()
    print("✅ Clase importada")
    
    # ¿Tiene servicio?
    print(f"🔍 uploader.service es: {uploader.service}")
    
    # Forzar autenticación
    print("🔍 Llamando a authenticate()...")
    uploader.authenticate()
    
    print(f"🔍 Después de authenticate(), uploader.service es: {uploader.service}")
    
    # Probar subida rápida
    print("\n🔍 Probando subida con tu clase...")
    
    # Encontrar un video
    videos = [f for f in os.listdir('videos_generados') if f.endswith('.mp4')]
    if videos:
        video_path = os.path.join('videos_generados', videos[0])
        print(f"🎬 Video: {video_path}")
        
        # Llamar DIRECTAMENTE a upload_video
        result = uploader.upload_video(
            video_path=video_path,
            title="DEBUG TEST",
            description="Prueba debug",
            tags=["debug"],
            privacy_status="private"
        )
        
        print(f"✅ Resultado: {result}")
    else:
        print("❌ No hay videos")
        
except ImportError as e:
    print(f"❌ No se pudo importar: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()