# Bitácora de desarrollo — Kodi Chromecast Bridge

**Fecha de actualización:** 8 de noviembre de 2026  
**Estado:** desarrollo experimental en Raspberry Pi / LibreELEC

> Esta bitácora registra pruebas realizadas en el entorno Raspberry Pi. Distingue los resultados observados de las hipótesis y de las tareas pendientes. No implica que estas pruebas estén integradas todavía en una versión publicada del complemento Kodi.

## 1. Objetivo

Desarrollar un puente que permita enviar al Chromecast contenidos reproducidos desde Kodi, incluidos enlaces de AllDebrid.

El objetivo es que Kodi actúe como interfaz de selección y control, mientras que Chromecast recibe y reproduce el contenido a través de la red local. Uno de los retos principales es adaptar el formato y el transporte del contenido a lo que admite el receptor multimedia de Chromecast.

## 2. Entorno de pruebas

- Raspberry Pi 5 (ARM64).
- LibreELEC 12.2.1.
- Kodi 21.3.
- Chromecast de segunda generación.
- Python disponible en LibreELEC.
- FFmpeg precompilado para Linux ARM64, instalado dentro del directorio del proyecto.

La Raspberry Pi utilizada en estas pruebas tiene la dirección local `192.168.1.159`. La dirección del Chromecast y otros datos de la red se omiten deliberadamente de esta documentación.

## 3. Comunicación con Chromecast

Se ha desarrollado una implementación experimental del protocolo Google Cast utilizando Python y bibliotecas estándar, sin depender de PyChromecast ni de protobuf en LibreELEC.

Se ha comprobado que es posible:

- Establecer una conexión TLS con Chromecast.
- Enviar el mensaje `CONNECT` e intercambiar mensajes de control.
- Consultar el estado del receptor mediante `GET_STATUS`.
- Iniciar la aplicación Default Media Receiver (`CC1AD845`).
- Obtener el identificador de transporte (`transportId`) de la sesión activa.
- Enviar órdenes `LOAD` al receptor.
- Recibir mensajes `MEDIA_STATUS` y consultar el estado de reproducción.

**Detalle importante:** el `transportId` cambia al iniciar una nueva sesión del receptor. No debe tratarse como un identificador permanente ni dejarse fijado en el código definitivo. La implementación final deberá obtenerlo dinámicamente a partir del estado del receptor.

## 4. Problema inicial: reproducción sin sonido

La reproducción directa de un contenido de AllDebrid a través del puente experimental permitió observar imagen en Chromecast, pero no sonido.

En la prueba investigada, el contenido original utilizaba vídeo H.264 y audio E-AC-3 5.1 dentro de un contenedor MKV. Kodi reproducía ese mismo contenido con imagen y sonido.

La causa exacta del problema inicial no se ha aislado: no se ha demostrado si se debía al contenedor MKV, al códec E-AC-3 o a la combinación de ambos.

## 5. Prueba satisfactoria: MP4 H.264 + AAC

Se instaló FFmpeg para ARM64 en la Raspberry Pi y se generó un MP4 de prueba de 90 segundos a partir del contenido original.

Parámetros relevantes:

- Vídeo: H.264 copiado sin recodificación.
- Audio: E-AC-3 convertido a AAC estéreo.
- Frecuencia de muestreo del audio: 48 kHz.
- Contenedor: MP4.
- Duración: 90 segundos.

Archivo de prueba: `prueba_audio_aac.mp4`.

### Resultado observado

**Chromecast reprodujo el archivo de prueba con imagen y sonido.**

Esta prueba confirma que la combinación H.264 + AAC dentro de MP4 funciona en el entorno probado. También demuestra que se puede conservar el flujo de vídeo original y convertir únicamente el audio, evitando una recodificación de vídeo innecesaria.

El archivo de prueba se sirvió desde la Raspberry Pi mediante HTTP y se envió al Default Media Receiver.

Esta prueba corresponde a un archivo MP4 ya generado; no demuestra todavía que la reproducción pueda comenzar mientras FFmpeg sigue generando el archivo.

## 6. Investigación de HLS

Se investigó HLS para evitar tener que generar un archivo completo antes de iniciar la reproducción. Se partió del MP4 de prueba y se generaron dos variantes VOD.

### 6.1. HLS MPEG-TS

Se generó una lista `index.m3u8` con segmentos MPEG-TS (23 segmentos), manteniendo los flujos H.264 y AAC.

**Resultado:** el receptor rechazó la reproducción. Los registros HTTP mostraron varias solicitudes de `index.m3u8` desde Chromecast, con respuesta HTTP 200, pero no se observaron solicitudes a los segmentos `.ts`.

### 6.2. HLS fMP4

Se generó una segunda lista HLS con fragmentos MP4:

- `index.m3u8`
- `init.mp4`
- Segmentos `segment_XXX.m4s`

Se comprobó que la lista y el archivo de inicialización estaban disponibles mediante HTTP. Se envió la lista al Default Media Receiver.

**Resultado:** el receptor también rechazó esta variante. Los registros HTTP mostraron solicitudes de `index.m3u8` con respuesta HTTP 200, pero no se observaron solicitudes desde Chromecast a `init.mp4` ni a los segmentos `.m4s`.

### Interpretación y límites

En ambas pruebas, Chromecast obtuvo la lista HLS, pero no llegó a solicitar los recursos multimedia referenciados por ella.

Esto sitúa el fallo antes de la descarga de los segmentos. Sin embargo, **no permite concluir que Chromecast sea incompatible con HLS en general**. La causa concreta del rechazo sigue sin identificarse; puede estar relacionada con el manifiesto, el perfil HLS utilizado o algún requisito del receptor.

Las pruebas fueron realizadas con listas VOD generadas previamente a partir de un MP4 de prueba. No constituyen todavía una prueba de una canalización HLS en directo desde AllDebrid.

## 7. Estado de los componentes

| Componente o prueba | Estado |
|---|---|
| Comunicación TLS con Chromecast | Probada |
| Protocolo Cast experimental en Python | Probado |
| Inicio de Default Media Receiver | Probado |
| Envío de órdenes LOAD y consulta de estado | Probados |
| FFmpeg para ARM64 | Instalado y operativo |
| Conversión E-AC-3 a AAC | Probada |
| Reproducción HTTP de MP4 H.264 + AAC | Correcta, con sonido |
| HLS MPEG-TS VOD | Rechazado en la prueba |
| HLS fMP4 VOD | Rechazado en la prueba |
| MP4 progresivo generado en directo | Pendiente |
| Integración automática con Kodi | Pendiente |

## 8. Próxima línea de desarrollo: MP4 progresivo

La siguiente vía propuesta es investigar MP4 progresivo servido por HTTP.

Flujo previsto:

1. Obtener la URL de reproducción de AllDebrid.
2. Entregar el flujo de origen a FFmpeg.
3. Copiar el vídeo H.264 sin recodificarlo.
4. Convertir el audio a AAC estéreo.
5. Producir un MP4 apto para reproducción progresiva.
6. Servirlo mediante HTTP desde la Raspberry Pi.
7. Enviar la URL al Default Media Receiver.

El principal reto es permitir que Chromecast empiece a reproducir antes de que FFmpeg haya terminado de procesar todo el contenido.

Habrá que estudiar la estructura del contenedor MP4, la ubicación y disponibilidad de los metadatos `moov atom`, el búfer y el soporte de solicitudes HTTP Range. No basta con eliminar el límite de duración de la prueba anterior: la generación y el servidor deben permitir que el receptor lea un archivo que todavía está creciendo.

La reproducción satisfactoria del MP4 completo es un punto de partida, pero no demuestra todavía que este modo progresivo vaya a funcionar.

## 9. Seguridad y publicación

No deben incorporarse al repositorio:

- Claves API de AllDebrid.
- Contraseñas o credenciales.
- URLs privadas de reproducción.
- Tokens de acceso o de sesión.
- Archivos de configuración que contengan información sensible.
- Registros que expongan esos datos.

Las direcciones IP privadas y los identificadores temporales de sesión también deben omitirse cuando no sean necesarios para explicar una prueba.

Los scripts experimentales y los archivos multimedia generados en las pruebas no se consideran parte de una versión estable del complemento por el mero hecho de estar descritos aquí.

## 10. Conclusión

En la Raspberry Pi se ha conseguido establecer comunicación con Chromecast mediante una implementación experimental del protocolo Cast y reproducir por HTTP un MP4 con vídeo H.264 y audio AAC.

Las pruebas HLS MPEG-TS y fMP4 no consiguieron iniciar la reproducción: el receptor solicitó las listas, pero no los segmentos. La causa exacta sigue pendiente de investigación.

El siguiente objetivo es validar MP4 progresivo mediante FFmpeg y HTTP. La integración completa con Kodi, la automatización del envío y la compatibilidad general con enlaces de AllDebrid continúan pendientes.
