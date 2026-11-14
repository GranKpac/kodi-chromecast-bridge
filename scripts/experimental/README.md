# Scripts Cast experimentales

No hay direcciones IP ni identificadores de sesión fijos en el código.

Configura antes de ejecutar:

```sh
export CAST_HOST="IP_DEL_CHROMECAST"
export CAST_PORT="8009"
export BRIDGE_DIR="/storage/kodi-chromecast-bridge"
```

Opcionales: `CAST_TIMEOUT` y `CAST_MEDIA_URL`. Si no se define `CAST_MEDIA_URL`, cada script lee su fichero URL local desde `BRIDGE_DIR`. Esos ficheros no se versionan. Ejemplo:

```sh
CAST_MEDIA_URL="https://servidor/medio.mp4" python3 scripts/experimental/cast_play_mp4.py
```

Los scripts de reproducción inician Default Media Receiver y obtienen el `transportId` actual de `RECEIVER_STATUS`; no reutilizan IDs antiguos. `cast_protocol.py` centraliza framing protobuf y heartbeat.

El TLS está cifrado, pero se acepta el certificado local autofirmado del dispositivo sin validarlo contra una CA. Un estado `PLAYING` no demuestra por sí solo imagen y sonido visibles. HLS sigue siendo experimental. La fuente debe ser accesible desde Chromecast.

No se incluye el prototipo de menú contextual: todavía no envía medios y el repositorio ya contiene un complemento de diagnóstico independiente.
