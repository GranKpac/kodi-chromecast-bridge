# Kodi Chromecast Bridge

Experimental project to send media selected or played in Kodi to a Google Cast receiver.

## Current status

The desktop proof-of-concept established device discovery and basic Cast control. Subsequent Raspberry Pi experiments established Cast V2 communication from LibreELEC and observed playback with image and sound using an H.264 + AAC MP4. A fragmented-MP4 pipeline also started playback while FFmpeg was still generating the file.

The project is **not yet a complete Kodi-to-Chromecast integration**. The contextual prototype does not yet resolve an independent source or send media to Chromecast. End-of-playback cleanup, robust error handling, source resolution and full AllDebrid compatibility remain open work.

See [the development log](docs/bitacora-desarrollo.md) and [test notes](tests/README.md) for observed results and limitations.

## Target environment

- Kodi 21.x
- LibreELEC 12.x
- Raspberry Pi 5 (ARM64)
- Google Chromecast (2nd-generation device used in current tests)

## Confirmed observations

- PyChromecast discovers Cast devices on the same LAN.
- The experimental Cast V2 client establishes TLS, sends CONNECT, queries receiver status and launches Default Media Receiver (CC1AD845).
- The receiver accepts LOAD commands in the tested cases.
- An H.264 video stream copied without re-encoding and E-AC-3 audio converted to AAC stereo played with image and sound in an MP4 container.
- A fragmented MP4 pipeline using FFmpeg and a local HTTP server began playback while the file was still being generated.

These observations apply to specific test sources and devices. They do not certify general codec, container, HLS or AllDebrid compatibility. A receiver-reported PLAYING state is not proof of visible playback.

## Experimental scripts

The portable manual test scripts are in [scripts/experimental](scripts/experimental/README.md). They use runtime configuration (CAST_HOST, CAST_PORT, BRIDGE_DIR) and retrieve the Cast transportId dynamically for each session. They are not a stable background service.

Do not commit local URL files, current-item.json, credentials, cookies, tokens, media files, FFmpeg binaries or sensitive logs.

## Compatibility note

Kodi's xbmc.Player().getPlayingFile() returns the current playback URL or path, but that does not guarantee Chromecast can fetch it. The URL may be local, temporary, protected by cookies or authorization headers, or point to an adaptive HLS/DASH stream. Chromecast must be able to reach the resource and support its protocol, container and codecs.

AllDebrid and Palantir compatibility is not assumed merely because Kodi can play a link.

## Development principles

- Keep provider-specific handling separate until source URL behavior is understood.
- Keep Kodi/HDMI playback independent from Chromecast playback.
- Do not stop or change local Kodi playback as a side effect of a Cast session.
- Never commit API credentials, passwords, tokens, private URLs, cookies or sensitive logs.
- Verify playback visually and audibly on the TV; do not rely only on receiver status.

## Roadmap

1. [x] Discover Chromecast devices and establish Cast control.
2. [x] Observe playback with selected public and local test media.
3. [x] Observe fragmented MP4 playback while FFmpeg is generating the file.
4. [ ] Verify natural playback end, disconnect handling and automatic cleanup.
5. [ ] Resolve a source independently for Chromecast, without depending on the HDMI player.
6. [ ] Implement a working Kodi context-menu action and Cast playback controls.
7. [ ] Investigate protected/adaptive streams and AllDebrid compatibility.
8. [ ] Package and test the add-on on LibreELEC.

## License

MIT. See LICENSE.
