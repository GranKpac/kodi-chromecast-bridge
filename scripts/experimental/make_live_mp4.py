#!/usr/bin/env python3
"""Start the experimental FFmpeg fragmented-MP4 pipeline.

Environment:
  BRIDGE_DIR (default /storage/kodi-chromecast-bridge)
  CURRENT_ITEM_FILE (default BRIDGE_DIR/current-item.json)
  FFMPEG_PATH (default BRIDGE_DIR/ffmpeg/.../ffmpeg)
"""
import json, os, subprocess, time

BASE=os.path.abspath(os.environ.get("BRIDGE_DIR","/storage/kodi-chromecast-bridge"))
ITEM=os.path.abspath(os.environ.get("CURRENT_ITEM_FILE",os.path.join(BASE,"current-item.json")))
FFMPEG=os.environ.get("FFMPEG_PATH",os.path.join(BASE,"ffmpeg/ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg"))
OUTPUT=os.path.join(BASE,"live.mp4")
PID=os.path.join(BASE,"live_ffmpeg.pid")
LOG=os.path.join(BASE,"live_ffmpeg.log")

with open(ITEM,encoding="utf-8") as f:
    data=json.load(f)
url=data.get("result",{}).get("item",{}).get("file")
if not isinstance(url,str) or not url.startswith(("http://","https://")):
    raise SystemExit("El JSON no contiene una URL HTTP(S) válida.")
if not os.path.isfile(FFMPEG):
    raise SystemExit("No se encuentra FFmpeg; configura FFMPEG_PATH.")
if os.path.exists(PID):
    try:
        old=int(open(PID,encoding="ascii").read().strip())
        os.kill(old,0)
    except (ValueError,OSError):
        os.remove(PID)
    else:
        raise SystemExit("Ya existe un proceso FFmpeg activo (PID {}).".format(old))

cmd=[FFMPEG,"-hide_banner","-loglevel","warning","-user_agent","KodiChromecastBridge/0.1",
     "-i",url,"-map","0:v:0","-map","0:a:0","-c:v","copy","-c:a","aac","-ac","2",
     "-b:a","192k","-movflags","+empty_moov+frag_keyframe+default_base_moof",
     "-frag_duration","1000000","-flush_packets","1","-f","mp4","-y",OUTPUT]
with open(LOG,"w",encoding="utf-8") as log:
    proc=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                          stderr=log,start_new_session=True)
with open(PID,"w",encoding="ascii") as f:
    f.write(str(proc.pid))
time.sleep(2)
if proc.poll() is not None:
    os.remove(PID)
    raise SystemExit("FFmpeg terminó al iniciar (código {}). Consulta el log local.".format(proc.returncode))
print("FFmpeg sigue generando el MP4 fragmentado.")
print("PID:",proc.pid)
print("Salida:",OUTPUT)
print("La URL de origen se mantiene oculta.")
