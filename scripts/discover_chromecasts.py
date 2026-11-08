#!/usr/bin/env python3
"""Discover Google Cast devices on the local network."""

from __future__ import annotations

import sys
import pychromecast


def main() -> int:
    print("Buscando dispositivos Chromecast en la red local...")
    chromecasts = []
    browser = None

    try:
        chromecasts, browser = pychromecast.get_chromecasts()
        if not chromecasts:
            print("No se han encontrado dispositivos Cast.")
            return 1

        print(f"Dispositivos encontrados: {len(chromecasts)}\n")
        for index, cast in enumerate(chromecasts, start=1):
            info = cast.cast_info
            print(f"{index}. {info.friendly_name}")
            print(f"   Modelo: {info.model_name or 'Desconocido'}")
            print(f"   Fabricante: {info.manufacturer or 'Desconocido'}")
            print(f"   Dirección: {info.host}:{info.port}")
            print()
        return 0
    except KeyboardInterrupt:
        print("\nBúsqueda interrumpida.")
        return 130
    except Exception as exc:
        print(f"Error durante el descubrimiento: {exc}", file=sys.stderr)
        return 2
    finally:
        if browser is not None:
            browser.stop_discovery()


if __name__ == "__main__":
    raise SystemExit(main())
