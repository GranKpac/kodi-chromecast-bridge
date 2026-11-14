# Portabilidad de scripts Cast — 14 de noviembre de 2026

Se revisaron los scripts experimentales extraídos de la Raspberry Pi antes de publicarlos. Se eliminaron direcciones IP privadas y transportId antiguos fijados en el código.

La configuración pasa a variables de entorno:

- CAST_HOST: dirección del Chromecast (obligatoria).
- CAST_PORT: puerto Cast, 8009 por defecto.
- BRIDGE_DIR: carpeta local de trabajo.
- CAST_TIMEOUT: timeout de red.
- CAST_MEDIA_URL: URL HTTP(S) de prueba opcional; si no se define, se lee el archivo URL local correspondiente.

La comunicación Cast V2 se centralizó en scripts/experimental/cast_protocol.py. Los scripts que envían LOAD inician Default Media Receiver y obtienen el transportId dinámicamente de RECEIVER_STATUS en cada sesión. Los archivos URL locales no deben versionarse.

La sintaxis Python y las funciones de framing protobuf se comprobaron localmente. Estas comprobaciones no sustituyen una prueba real contra Chromecast.

El prototipo contextual extraído todavía no envía contenido. El repositorio ya dispone de script.kodi.castdiagnostic, por lo que no se duplica ese complemento ni se presenta el prototipo como funcional.

## Pendiente

1. Ejecutar los scripts portables en la Raspberry Pi.
2. Probar conexión, estado, lanzamiento del receptor y reproducción MP4 fragmentada.
3. Completar la limpieza de procesos y archivos al finalizar o interrumpir.
4. Desarrollar el resolver independiente de la reproducción HDMI y conectarlo con el menú contextual de Kodi.
