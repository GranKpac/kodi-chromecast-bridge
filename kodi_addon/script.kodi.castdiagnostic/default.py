# -*- coding: utf-8 -*-
"""Privacy-safe diagnostic for the media source currently playing in Kodi."""

import os
from urllib.parse import parse_qsl, urlsplit

import xbmc
import xbmcgui


def split_kodi_headers(raw_path):
    """Split Kodi's URL|Header=Value syntax without exposing header values."""
    if "|" not in raw_path:
        return raw_path, []

    media_url, header_text = raw_path.split("|", 1)
    names = []
    for name, _value in parse_qsl(header_text, keep_blank_values=True):
        clean_name = name.strip()
        if clean_name and clean_name.lower() not in [n.lower() for n in names]:
            names.append(clean_name)
    return media_url, names


def describe_source(raw_path):
    media_url, header_names = split_kodi_headers(raw_path)
    parsed = urlsplit(media_url)
    scheme = parsed.scheme.lower() or "ruta local"
    host = parsed.hostname or "(sin host)"

    # Only show the extension, never the full path or query string.
    extension = os.path.splitext(parsed.path)[1].lower() or "(sin extensión)"

    if scheme == "plugin":
        source_type = "Complemento de Kodi"
        addon_id = parsed.netloc or "(no identificado)"
    elif extension == ".m3u8":
        source_type = "HLS (indicado por .m3u8)"
        addon_id = None
    elif extension == ".mpd":
        source_type = "MPEG-DASH (indicado por .mpd)"
        addon_id = None
    elif extension in (".mp4", ".mkv", ".avi", ".mov", ".ts", ".webm"):
        source_type = "Archivo o contenedor multimedia"
        addon_id = None
    else:
        source_type = "No determinado por la extensión"
        addon_id = None

    lines = [
        "Fuente de reproducción de Kodi",
        "",
        "Esquema: " + scheme,
        "Host: " + host,
        "Extensión: " + extension,
        "Tipo probable: " + source_type,
    ]

    if addon_id:
        lines.append("ID del complemento: " + addon_id)

    lines.extend([
        "",
        "Cabeceras HTTP en la URL: "
        + ("Sí" if header_names else "No detectadas"),
        "Nombres de cabeceras: "
        + (", ".join(header_names) if header_names else "(ninguna)"),
        "",
        "Privacidad: no se muestran la URL completa, la ruta, "
        "los parámetros de consulta ni los valores de las cabeceras.",
        "Nota: la extensión orienta sobre el formato, pero no confirma "
        "el códec ni la compatibilidad del Chromecast.",
    ])
    return "\n".join(lines)


def main():
    player = xbmc.Player()

    if not player.isPlayingVideo():
        xbmcgui.Dialog().ok(
            "Kodi Cast Diagnostic",
            "Kodi no está reproduciendo un vídeo en este momento.\n\n"
            "Inicia un vídeo y vuelve a ejecutar el diagnóstico."
        )
        return

    raw_path = player.getPlayingFile() or ""
    if not raw_path:
        xbmcgui.Dialog().ok(
            "Kodi Cast Diagnostic",
            "Kodi no ha devuelto una dirección para la reproducción actual."
        )
        return

    report = describe_source(raw_path)
    xbmcgui.Dialog().textviewer("Diagnóstico de reproducción", report)


if __name__ == "__main__":
    main()
