#!/usr/bin/env python3
"""Create a 90-second H.264 + AAC MP4 test from current-item.json."""
import json, os, subprocess
BASE=os.path.abspath(os.environ.get("BRIDGE_DIR","/storage/kodi-chromecast-bridge"))
ITEM=os.path.abspath(os.environ.get("CURRENT_ITEM_FILE",os.path.join(BASE,"current-item.json")))
FFMPEG=os.environ.get("FFMPEG_PATH",os.path.join(BASE,"ffmpeg/ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg"))
OUTPUT=os.path.join(BASE,"prueba_audio_aac.mp4")
with open(ITEM,encoding="utf-8") as f:
    data=json.load(f)
url=data.get("result",{}).get("item",{}).get("file")
if not isinstance(url,str) or not url.startswith(("http://","https://")):
    raise SystemExit("El JSON no contiene una URL HTTP(S) válida.")
if not os.path.isfile(FFMPEG):
    raise SystemExit("No se encuentra FFmpeg; configura FFMPEG_PATH.")
cmd=[FFMPEG,"-hide_banner","-loglevel","error","-user_agent","KodiChromecastBridge/0.1",
     "-i",url,"-t","90","-map","0:v:0","-map","0:a:0","-c:v","copy","-c:a","aac",
     "-ac","2","-b:a","192k","-movflags","+faststart","-y",OUTPUT]
print("Generando MP4 de prueba de 90 segundos...")
result=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
if result.returncode:
    print("FFmpeg falló (código {}). Se omite stderr para no revelar la URL privada.".format(result.returncode))
    raise SystemExit(result.returncode)
print("Prueba creada:",OUTPUT)
print("Tamaño: {:.1f} MB".format(os.path.getsize(OUTPUT)/1024/1024))
