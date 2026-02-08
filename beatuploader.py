import os
import sys
import json
from moviepy.editor import ImageClip, AudioFileClip
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
from PIL import Image
import argparse
from pathlib import Path
import time
# =========== PARCHE PARA PILLOW ANTIALIAS ===========
import PIL.Image
import PIL
import random
DEFAULT_DESCRIPTION = """this version of the beat is *free for youtube and soundcloud *, email/dm to buy a lease

https://www.instagram.com/goodbyenostalgiabeats/
goodbyenostalgiabeats@gmail.com
must credit goodbyenostalgiabeats

key and bpm:  dm me ;)

#nettspendtypebeat #wegonebeoktypebeat #oktypebeat


nettspend type beat free for profit, nettspend bafk type beat, nettspend tyla type beat, nettspend type beat, osamason type beat, type beat, type beat nettspend, xaviersobased type beat, yhapojj x nettspend type beat, jerk type beat, free type beat, free nettspend type beat, yhapojj type beat, free osamason type beat, osamason type beat hard, glokk40spaz type beat, instrumental yhapojj, subiibabii type beat, osamason type beat free, type beat xaviersobased, type beat yhapojj free, type beat nettspend free, type beat glokk40spaz, free yhapojj type beat, osamason x ok type beat, osamason, yhpaojj type beat 2023, netspend type beat, ok type beat, type beat yhapojj, osamason type beat free for profit, yhapojj instrumental, osamason type beat 2023, nettspend, tainiykick, osamason type beat 808, osamason x ken carson type beat, type beat subiibabii, ken carson a great chaos type beat, osamason x osama season type beat, a great chaos type beat, ken carson type beat, osamason ok type beat, osamason type beat nettspend, osamason nettspend, nettspend ok type beat, ken carson type beat 2023, prod ok, ken carson type beat free, osama season type beat, osamason type beat ok, osamason perc40 type beat, 1oneam type beat, boolymon type beat, nettspend sample type beat, 2024 freestyle, wegonebeok type beat, osamason boolymon type beat, prod ok type beat, osamson ok type beat, osamson sampled type beat, osamason nettspend type beat, osamson, osamson prod ok, nettspend osamson prod ok type beat, netspend osamason type beat, nettspend deftones, nettspend 2024, nettspend deftones type beat, nett spend, nettspend osamason, pour up, osamason pour up, wavguide, yhapojj type beat, type beat yhapojj, type beat yhapojj free,free yhapojj type beat,xaviersobased type beat, type beat xaviersobased,glokk40spaz type beat,type beat glokk40spaz,yhapojj x xaviersobased type beat,yhpaojj type beat 2023,xaviersobased type beat 2023,glokk40spaz type beat 2023,type beat,free type beat,yhapojj instrumental,instrumental yhapojj, instrumental glokk40spaz,instrumental xaviersobased,subiibabii type beat,type beat subiibabii,nettspend type beat,type beat nettspend,yhapojj x nettspend type beat,type beat nettspend free,free nettspend type beat"""

# Arreglar ANTIALIAS para versiones nuevas de Pillow
if not hasattr(PIL.Image, 'ANTIALIAS'):
    if hasattr(PIL.Image, 'Resampling'):
        # Pillow >= 10.0
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
    else:
        # Fallback
        PIL.Image.ANTIALIAS = 1
    
    print("🔄 Parche Pillow aplicado: ANTIALIAS disponible")

# También parchear Image si se importa por separado
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        if hasattr(Image, 'Resampling'):
            Image.ANTIALIAS = Image.Resampling.LANCZOS
        else:
            Image.ANTIALIAS = 1
except:
    pass
# =========== FIN DEL PARCHE ===========

class BatchYouTubeUploader:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
        self.API_SERVICE_NAME = 'youtube'
        self.API_VERSION = 'v3'
        self.service = None
        self.uploaded_videos = []
    
    def authenticate(self):
        """Autenticación con OAuth 2.0"""
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build(self.API_SERVICE_NAME, self.API_VERSION, credentials=creds)
        print("✅ Autenticación exitosa con YouTube API")
        return True
    
    def create_video_from_pair(self, image_path, audio_path, output_folder="videos"):
        """
        Crea video - Para imágenes pequeñas: ESCALA PARA LLENAR LA ALTURA (1080px)
        Mantiene relación de aspecto, centra horizontalmente
        """
        try:
            # Crear carpeta de salida si no existe
            os.makedirs(output_folder, exist_ok=True)
            
            # Generar nombre del video
            image_name = os.path.splitext(os.path.basename(image_path))[0]
            audio_name = os.path.splitext(os.path.basename(audio_path))[0]
            video_name = f"{image_name}_{audio_name}.mp4"
            output_path = os.path.join(output_folder, video_name)
            
            # Verificar si el video ya existe
            if os.path.exists(output_path):
                print(f"⚠️  Video ya existe: {output_path}")
                return output_path
            
            # Cargar audio
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            
            # Cargar imagen
            image_clip = ImageClip(image_path, duration=audio_duration)
            
            # Obtener dimensiones originales de la imagen
            img_width, img_height = image_clip.size
            #print(f"📐  Tamaño original de imagen: {img_width}x{img_height}")
            
            # Tamaño del video (Full HD 1080p)
            video_width, video_height = 1920, 1080
            
            # DECISIÓN DE ESCALADO:
            # 1. Si la imagen es MUY pequeña (menos de 500px en cualquier dimensión)
            #    la escalamos para que al menos tenga 500px en la dimensión más pequeña
            # 2. Luego, escalamos para que la ALTURA sea exactamente 1080px
            # 3. Si el ancho resultante es menor que 1920, tendrá bordes a los lados
            # 4. Si el ancho resultante es mayor que 1920, recortamos los lados
            
            # Paso 1: Si es muy pequeña, escala mínima
            min_acceptable_size = 500
            if img_width < min_acceptable_size or img_height < min_acceptable_size:
                # Escalar para que la dimensión más pequeña sea al menos 500px
                scale_min = max(min_acceptable_size / img_width, min_acceptable_size / img_height)
                img_width = int(img_width * scale_min)
                img_height = int(img_height * scale_min)
                image_clip = image_clip.resize((img_width, img_height))
                #print(f"📐  Escalado mínimo aplicado: {img_width}x{img_height}")
            
            # Paso 2: Escalar para que la altura sea 1080px (FILL HEIGHT)
            scale_height = video_height / img_height
            new_height = video_height  # Exactamente 1080px
            new_width = int(img_width * scale_height)
            
            #print(f"📏  Escalando para altura 1080px:")
            #print(f"    • Factor de escala: {scale_height:.2f}")
            #print(f"    • Nuevo tamaño: {new_width}x{new_height}")
            
            # Redimensionar imagen
            image_clip = image_clip.resize((new_width, new_height))
            
            # Paso 3: Manejar el ancho
            x_position = 0
            needs_crop = False
            
            if new_width < video_width:
                # La imagen es más angosta que el video → CENTRAR con bordes
                x_position = (video_width - new_width) // 2
                #print(f"🎯  Imagen centrada: borde izquierdo/derecho")
                #print(f"    • Ancho imagen: {new_width}px")
                #print(f"    • Ancho video: {video_width}px")
                #print(f"    • Borde total: {video_width - new_width}px ({x_position}px cada lado)")
                
                # Crear fondo negro
                from moviepy.editor import ColorClip
                background = ColorClip(
                    size=(video_width, video_height), 
                    color=(0, 0, 0),  # Negro puro
                    duration=audio_duration
                )
                
                # Posicionar imagen
                image_clip = image_clip.set_position((x_position, 0))
                
                # Crear composición
                from moviepy.editor import CompositeVideoClip
                video_clip = CompositeVideoClip([background, image_clip])
                
            elif new_width > video_width:
                # La imagen es más ancha que el video → RECORTAR LADOS (centrado)
                needs_crop = True
                crop_amount = (new_width - video_width) // 2
                #print(f"✂️  Recortando lados para ajustar al ancho:")
                #print(f"    • Ancho imagen: {new_width}px")
                #print(f"    • Ancho video: {video_width}px")
                #print(f"    • Recortar: {crop_amount}px de cada lado")
                
                # Recortar imagen (crop)
                image_clip = image_clip.crop(x1=crop_amount, x2=new_width - crop_amount)
                
                # La imagen ahora tiene exactamente 1920x1080
                video_clip = image_clip
                
            else:
                # Ancho perfecto (1920px) → usar directamente
                #print(f"✅  Ancho perfecto: 1920px")
                video_clip = image_clip
            
            # Añadir audio
            video_clip = video_clip.set_audio(audio_clip)
            
            # Escribir video
            print(f"🎬  Creando video: {video_name}")
            video_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Liberar recursos
            image_clip.close()
            audio_clip.close()
            video_clip.close()
            if not needs_crop and 'background' in locals():
                background.close()
            
            print(f"✅  Video creado: {output_path}")
            #print(f"    • Resolución final: 1920x1080")
            #print(f"    • Imagen escalada a: {new_width}x{new_height}")
            #print(f"    • Estrategia: {'Fill Height' + (' + bordes' if new_width < video_width else ' + crop lados' if needs_crop else ' (perfect fit)')}")
            
            return output_path
            
        except Exception as e:
            print(f"❌  Error al crear video {image_path} + {audio_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def batch_create_videos(self, input_folder, output_folder="videos", 
                           image_extensions=None, audio_extensions=None):
        """
        Crea videos para todas las combinaciones de imágenes y audios en una carpeta
        
        Args:
            input_folder: Carpeta con imágenes y audios
            output_folder: Carpeta donde guardar los videos
            image_extensions: Extensiones de imagen permitidas
            audio_extensions: Extensiones de audio permitidas
        """
        if image_extensions is None:
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        if audio_extensions is None:
            audio_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.aac']
        
        # Buscar archivos
        image_files = []
        audio_files = []
        
        for file in os.listdir(input_folder):
            file_path = os.path.join(input_folder, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in image_extensions:
                    image_files.append(file_path)
                elif ext in audio_extensions:
                    audio_files.append(file_path)
        
        print(f"📁  Encontrados: {len(image_files)} imágenes, {len(audio_files)} audios")
        
        if not image_files or not audio_files:
            print("❌  No hay suficientes archivos para procesar")
            return []
        
        # Crear todas las combinaciones posibles
        created_videos = []
        total_combinations = len(image_files) * len(audio_files)
        current = 1
        
        for image_path in image_files:
            for audio_path in audio_files:
                print(f"\n🔄  Procesando {current}/{total_combinations}")
                print(f"   Imagen: {os.path.basename(image_path)}")
                print(f"   Audio: {os.path.basename(audio_path)}")
                
                video_path = self.create_video_from_pair(image_path, audio_path, output_folder)
                if video_path:
                    created_videos.append({
                        'image': image_path,
                        'audio': audio_path,
                        'video': video_path,
                        'title': f"{os.path.splitext(os.path.basename(image_path))[0]} - {os.path.splitext(os.path.basename(audio_path))[0]}"
                    })
                
                current += 1
        
        print(f"\n✨  Proceso completado: {len(created_videos)} videos creados")
        return created_videos
    
    def batch_create_from_pairs(self, pairs_list, output_folder="videos"):
        """
        Crea videos a partir de una lista específica de pares (imagen, audio)
        
        Args:
            pairs_list: Lista de diccionarios con 'image' y 'audio'
            output_folder: Carpeta donde guardar los videos
        """
        created_videos = []
        
        for i, pair in enumerate(pairs_list, 1):
            print(f"\n🔄  Procesando par {i}/{len(pairs_list)}")
            print(f"   Imagen: {os.path.basename(pair['image'])}")
            print(f"   Audio: {os.path.basename(pair['audio'])}")
            
            video_path = self.create_video_from_pair(pair['image'], pair['audio'], output_folder)
            if video_path:
                created_videos.append({
                    'image': pair['image'],
                    'audio': pair['audio'],
                    'video': video_path,
                    'title': pair.get('title', 
                        f"{os.path.splitext(os.path.basename(pair['image']))[0]} - {os.path.splitext(os.path.basename(pair['audio']))[0]}")
                })
        
        print(f"\n✨  Proceso completado: {len(created_videos)} videos creados")
        return created_videos
    
    def upload_video(self, video_path, title, description="", tags=None, 
                    category_id="22", privacy_status="private", 
                    thumbnail_path=None, max_retries=3):
        """
        Sube un video individual a YouTube
        
        Returns:
            Diccionario con info del video subido o None si falla
        """
        if tags is None:
            tags = []
            
            #print(f"\n🚀  INICIANDO SUBIDA: {title}")
            #print(f"⏳  Esto puede tardar varios minutos...")
            #print(f"   • Archivo: {os.path.basename(video_path)}")
            #print(f"   • Por favor espera pacientemente")
        
        for attempt in range(max_retries):
            try:
                body = {
                    'snippet': {
                        'title': title,
                        'description': description,
                        'tags': tags,
                        'categoryId': category_id
                    },
                    'status': {
                        'privacyStatus': privacy_status
                    }
                }
                
                print(f"⬆️  Subiendo: {title}")
                
                media = MediaFileUpload(
                    video_path,
                    mimetype='video/mp4',
                    chunksize=1024*1024,
                    resumable=True
                )
                
                request = self.service.videos().insert(
                    part=','.join(body.keys()),
                    body=body,
                    media_body=media
                )
                
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        print(f"   Progreso: {int(status.progress() * 100)}%")
                
                video_id = response['id']
                print(f"✅  Subido: {title}")
                #print(f"   ID: {video_id}")
                #print(f"   URL: https://www.youtube.com/watch?v={video_id}")
                
                # Subir miniatura si se proporciona
                if thumbnail_path and os.path.exists(thumbnail_path):
                    try:
                        media_thumbnail = MediaFileUpload(
                            thumbnail_path,
                            mimetype='image/jpeg'
                        )
                        self.service.thumbnails().set(
                            videoId=video_id,
                            media_body=media_thumbnail
                        ).execute()
                        print(f"   Miniatura personalizada subida")
                    except Exception as e:
                        print(f"   ⚠️  No se pudo subir miniatura: {e}")
                
                return {
                    'id': video_id,
                    'title': title,
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'path': video_path
                }
                
            except Exception as e:
                print(f"❌  Error en intento {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Backoff exponencial
                    print(f"   Reintentando en {wait_time} segundos...")
                    time.sleep(wait_time)
                else:
                    print(f"   ❌  Falló después de {max_retries} intentos")
                    return None
    
    def batch_upload_videos(self, videos_list, privacy_status="private", 
                        description_template=DEFAULT_DESCRIPTION, tags=None, delay=5):
        """
        Sube múltiples videos a YouTube
        
        Args:
            videos_list: Lista de diccionarios con info de videos
            privacy_status: Configuración de privacidad
            description_template: Plantilla para descripción
            tags: Etiquetas comunes para todos los videos
            delay: Segundos de espera entre subidas
        """
        
        if tags is None:
            tags = ["nettspend bafk type beat", "nettspend tyla type beat", "nettspend type beat", 
                    "osamason type beat", "type beat", "nettspend", "yhapojj x nettspend type beat", 
                    "free type beat", "free nettspend type beat", "yhapojj type beat", "free osamason type beat", 
                    "osamason type beat hard", "glokk40spaz type beat", "osamason type beat free", "che type beat",
                    "fakemink", "fakemink prod ok", "free che type beat" ,"free fakemink type beat", "wegonebeok", 
                    "ok beats", "free ok beats", "underground beats", "gyro beats", "prod gyro beats","ok"]
        
        uploaded = []
        total = len(videos_list)
        
        print(f"\n📤  Iniciando subida de {total} videos a YouTube...")
        
        for i, video_info in enumerate(videos_list, 1):
            print(f"\n{'='*50}")
            print(f"📤  Subiendo video {i}/{total}")
            print(f"{'='*50}")
            
            # Crear descripción personalizada (si hay información de imagen/audio)
            if 'image' in video_info and 'audio' in video_info:
                description = DEFAULT_DESCRIPTION.format(
                    image=os.path.basename(video_info['image']),
                    audio=os.path.basename(video_info['audio']),
                    video=os.path.basename(video_info['video'])
                ) if description_template else ""
                # Tags específicos para videos creados desde pares
                video_tags = tags
            else:
                # Para videos independientes (solo archivo MP4)
                description = DEFAULT_DESCRIPTION.format(
                    video=os.path.basename(video_info['video'])
                ) if DEFAULT_DESCRIPTION else ""
                video_tags = tags
            
            # Obtener título (con fallback si no existe)
            base_title = video_info.get('title', '')
        
            # Formatear como: "free nettspend + wegonebeok type beat - "Titulo""
            # Si el título está vacío, usar un fallback
            if not base_title:
                base_title = os.path.splitext(os.path.basename(video_info.get('video', '')))[0]
            # Extraer solo primer nombre del fallback también
            base_title = base_title.split()[0] if ' ' in base_title else base_title
        
            # Capitalizar primera letra
            base_title_cap = base_title.capitalize()
        
            # Título final formateado
            final_title = f'free nettspend + wegonebeok type beat - "{base_title_cap}"'
        
            print(f"📝 Título: {final_title}")
        
            # Subir video
            result = self.upload_video(
                video_path=video_info['video'],
                title=final_title,
                description=DEFAULT_DESCRIPTION,
                tags=video_tags,
                privacy_status=privacy_status,
                thumbnail_path=video_info.get('thumbnail')
            )
            
            if result:
                uploaded.append(result)
                self.uploaded_videos.append(result)
            
            # Esperar entre subidas para evitar límites de API
            if i < total and delay > 0:
                print(f"\n⏳  Esperando {delay} segundos antes del próximo...")
                time.sleep(delay)
        
        # Guardar registro de videos subidos
        if uploaded:
            self.save_upload_log(uploaded)
        
        print(f"\n✨  Subida completada: {len(uploaded)}/{total} videos subidos exitosamente")
        return uploaded
    
    def save_upload_log(self, uploaded_videos, filename="uploaded_videos.json"):
        """Guarda un registro de los videos subidos"""
        log_data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_uploaded': len(uploaded_videos),
            'videos': uploaded_videos
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        #print(f"📝  Registro guardado en: {filename}")

def find_files_by_pattern(folder):
    """
    Crea pares aleatorios: cada audio con una imagen diferente
    No necesita que tengan el mismo nombre
    """
    import re
    
    
    # Separar imágenes y audios
    image_files = []
    audio_files = []
    
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                image_files.append(file_path)
            elif ext in ['.mp3', '.wav', '.m4a', '.flac', '.aac']:
                audio_files.append(file_path)
    
    print(f"📊 Encontrados: {len(image_files)} imágenes, {len(audio_files)} audios")
    
    if not image_files or not audio_files:
        print("❌ No hay suficientes archivos")
        return []
    
    # Mezclar las imágenes para distribución aleatoria
    random.shuffle(image_files)
    
    # Crear pares: cada audio con una imagen
    pairs = []
    
    # Si hay menos imágenes que audios, repetir algunas imágenes
    if len(image_files) < len(audio_files):
        print(f"⚠️  Más audios que imágenes. Algunas imágenes se repetirán.")
        # Extender la lista de imágenes para que alcance
        while len(image_files) < len(audio_files):
            image_files.append(random.choice(image_files))
    
    # Crear los pares
    for i, audio_path in enumerate(audio_files):
        
        # Usar imagen correspondiente (si hay más audios, se repiten imágenes)
        image_path = image_files[i % len(image_files)]
        
        # Obtener nombre del archivo de audio sin extensión
        audio_filename = os.path.basename(audio_path)
        audio_name_without_ext = os.path.splitext(audio_filename)[0]
        
        
        # EXTRAER NOMBRE COMPLETO HASTA EL PRIMER NÚMERO (BPM)
        # Buscar el primer número en el string
        match = re.search(r'\d+', audio_name_without_ext)
        
        if match:
            # Todo lo que está antes del primer número es el nombre del beat
            beat_name = audio_name_without_ext[:match.start()].strip()
        else:
            # Si no hay número, tomar todo hasta el @ si existe
            if '@' in audio_name_without_ext:
                beat_name = audio_name_without_ext.split('@')[0].strip()
            else:
                beat_name = audio_name_without_ext.strip()
        
        # titulo en minuscula
        formatted_title = beat_name.lower()
        
        # Nombres para mostrar
        audio_name = os.path.splitext(os.path.basename(audio_path))[0]
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        
        pairs.append({
            'image': image_path,
            'audio': audio_path,
            'title': formatted_title,  # El título será solo el nombre del audio
            'image_name': image_name,
            'audio_name': audio_name
        })
    
    # Mostrar qué pares se crearon
    #print(f"\n🔀 Pares creados aleatoriamente:")
    #for i, pair in enumerate(pairs, 1):
        #print(f"   {i:2d}. 🎵 {pair['audio_name']} + 🖼️  {pair['image_name']}")
    
    #return pairs

def main():
    parser = argparse.ArgumentParser(description='Crear y subir múltiples videos a YouTube')
    
    # Modos de operación
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando: crear videos
    create_parser = subparsers.add_parser('create', help='Crear videos a partir de imágenes y audios')
    create_parser.add_argument('--input', required=True, help='Carpeta con imágenes y audios')
    create_parser.add_argument('--output', default='videos', help='Carpeta para videos creados')
    create_parser.add_argument('--match-by-name', action='store_true', 
                              help='Emparejar imágenes y audios por nombre')
    
    # Comando: subir videos
    upload_parser = subparsers.add_parser('upload', help='Subir videos a YouTube')
    upload_parser.add_argument('--videos', required=True, help='Carpeta con videos o archivo JSON con lista')
    upload_parser.add_argument('--privacy', default='private', 
                              choices=['public', 'private', 'unlisted'],
                              help='Configuración de privacidad')
    upload_parser.add_argument('--delay', type=int, default=10,
                              help='Segundos de espera entre subidas')
    
    # Comando: crear y subir (todo en uno)
    full_parser = subparsers.add_parser('full', help='Crear y subir videos (todo en uno)')
    full_parser.add_argument('--input', required=True, help='Carpeta con imágenes y audios')
    full_parser.add_argument('--output', default='videos', help='Carpeta para videos creados')
    full_parser.add_argument('--privacy', default='private', 
                            choices=['public', 'private', 'unlisted'],
                            help='Configuración de privacidad')
    full_parser.add_argument('--match-by-name', action='store_true',
                            help='Emparejar imágenes y audios por nombre')
    full_parser.add_argument('--delay', type=int, default=10,
                            help='Segundos de espera entre subidas')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    uploader = BatchYouTubeUploader()
    
    # Autenticar (siempre necesario para subir)
    try:
        uploader.authenticate()
    except Exception as e:
        print(f"❌ Error de autenticación: {e}")
        print("Asegúrate de tener el archivo 'client_secret_712901190109-fnepsp8bbntmfo76lo1525jm6uo66c26.apps.googleusercontent.com.json' en el mismo directorio")
        sys.exit(1)
    
    if args.command == 'create':
        # Solo crear videos
        if args.match_by_name:
            pairs = find_files_by_pattern(args.input)
            videos = uploader.batch_create_from_pairs(pairs, args.output)
        else:
            videos = uploader.batch_create_videos(args.input, args.output)
        
        # Guardar lista de videos creados
        if videos:
            with open('videos_created.json', 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
            print(f"📝  Lista de videos guardada en: videos_created.json")
    
    elif args.command == 'upload':
        # Subir videos existentes
        if os.path.isdir(args.videos):
            # Buscar todos los videos en la carpeta
            video_files = []
            for file in os.listdir(args.videos):
                if file.lower().endswith('.mp4'):
                    video_path = os.path.join(args.videos, file)
                    video_files.append({
                        'video': video_path,
                        'title': os.path.splitext(file)[0]
                    })
            
            if not video_files:
                print(f"❌ No se encontraron videos en: {args.videos}")
                return
            
            uploader.batch_upload_videos(
                video_files, 
                privacy_status=args.privacy,
                delay=args.delay
            )
        
        elif os.path.isfile(args.videos) and args.videos.endswith('.json'):
            # Cargar lista desde JSON
            with open(args.videos, 'r', encoding='utf-8') as f:
                videos = json.load(f)
            
            uploader.batch_upload_videos(
                videos,
                privacy_status=args.privacy,
                delay=args.delay
            )
    
    elif args.command == 'full':
        # Crear y subir todo en uno
        if args.match_by_name:
            pairs = find_files_by_pattern(args.input)
            videos = uploader.batch_create_from_pairs(pairs, args.output)
        else:
            videos = uploader.batch_create_videos(args.input, args.output)
        
        if videos:
            uploader.batch_upload_videos(
                videos,
                privacy_status=args.privacy,
                delay=args.delay
            )

def interactive_mode():
    """Modo interactivo para uso sencillo"""
    print("="*60)
    print("🎵 BATCH YOUTUBE UPLOADER 🎵")
    print("="*60)
    
    uploader = BatchYouTubeUploader()
    
    # Autenticar
    print("\n🔐 Autenticando con YouTube...")
    try:
        uploader.authenticate()
    except:
        print("❌ Error de autenticación. Verifica las credenciales.")
        return
    
    # Seleccionar modo
    print("\nSelecciona modo:")
    print("1. Crear videos (solo generar archivos MP4)")
    print("2. Subir videos existentes a YouTube")
    print("3. Crear y subir (todo en uno)")
    
    choice = input("\nTu elección (1-3): ").strip()
    
    if choice == '1':
        folder = input("\n📁 Carpeta con imágenes y audios: ").strip('"')
        output = input("📁 Carpeta para videos [videos]: ").strip('"') or "videos"
        
        match = input("\n¿Emparejar por nombre? (ej: imagen.jpg + imagen.mp3) [s/n]: ").lower()
        match_by_name = match.startswith('s')
        
        if match_by_name:
            pairs = find_files_by_pattern(folder)
            videos = uploader.batch_create_from_pairs(pairs, output)
        else:
            videos = uploader.batch_create_videos(folder, output)
        
        if videos:
            with open('videos_created.json', 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
            print(f"\n✅ {len(videos)} videos creados")
            print("📝 Lista guardada en: videos_created.json")
    
    elif choice == '2':
        source = input("\n📁 Carpeta con videos o archivo JSON [videos/]: ").strip('"') or "videos"
        privacy = input("\n🔒 Privacidad (public/private/unlisted) [private]: ").lower() or "private"
        delay = input("⏳ Delay entre subidas (segundos) [10]: ").strip()
        delay = int(delay) if delay.isdigit() else 10
        
        if os.path.isdir(source):
            video_files = []
            for file in os.listdir(source):
                if file.lower().endswith('.mp4'):
                    video_path = os.path.join(source, file)
                    video_files.append({
                        'video': video_path,
                        'title': os.path.splitext(file)[0]
                    })
            
            if not video_files:
                print("❌ No se encontraron videos")
                return
            
            uploader.batch_upload_videos(video_files, privacy, delay=delay)
        
        elif os.path.isfile(source) and source.endswith('.json'):
            with open(source, 'r', encoding='utf-8') as f:
                videos = json.load(f)
            
            uploader.batch_upload_videos(videos, privacy, delay=delay)
    
    elif choice == '3':
        folder = input("\n📁 Carpeta con imágenes y audios: ").strip('"')
        output = input("📁 Carpeta para videos [videos]: ").strip('"') or "videos"
        privacy = input("\n🔒 Privacidad (public/private/unlisted) [private]: ").lower() or "private"
        delay = input("⏳ Delay entre subidas (segundos) [10]: ").strip()
        delay = int(delay) if delay.isdigit() else 10
        
        match = input("\n¿Emparejar por nombre? (ej: imagen.jpg + imagen.mp3) [s/n]: ").lower()
        match_by_name = match.startswith('s')
        
        if match_by_name:
            pairs = find_files_by_pattern(folder)
            videos = uploader.batch_create_from_pairs(pairs, output)
        else:
            videos = uploader.batch_create_videos(folder, output)
        
        if videos:
            print(f"\n✅ {len(videos)} videos creados. Iniciando subida...")
            uploader.batch_upload_videos(videos, privacy, delay=delay)



if __name__ == "__main__":
    # Para uso con argumentos:
    # python batch_uploader.py create --input mi_carpeta --output videos --match-by-name
    # python batch_uploader.py upload --videos videos --privacy private --delay 10
    # python batch_uploader.py full --input mi_carpeta --output videos --privacy public
    
    # Para modo interactivo:
    interactive_mode()


