# Kodi Chromecast Bridge

A small, experimental Kodi add-on project to send the currently playing video to a Google Cast device.

## Status

Early development. The first milestone is discovering Chromecast devices from a computer on the same LAN. No Kodi installation or Raspberry Pi configuration is changed by this test.

## Target environment

- Kodi 21.x
- LibreELEC 12.x
- Raspberry Pi 5
- Google Chromecast (1st/2nd generation)

## Important compatibility note

Kodi's `xbmc.Player().getPlayingFile()` returns the current playback URL or path, but that does not guarantee a Chromecast can fetch it. The URL may be local, temporary, protected by cookies or authorization headers, or point to an adaptive HLS/DASH stream. The Chromecast must be able to reach the resource and support its protocol, container, and codecs.

AllDebrid and Palantir compatibility will be investigated after basic Cast discovery and playback are proven. They are not assumed to work merely because Kodi can play a link.

## First milestone: discover Cast devices

Use a computer connected to the same network as the Chromecast.

Requirements: Python 3.9 or newer.

```bash
python -m venv .venv
```

Activate the virtual environment, then install:

```bash
python -m pip install -r requirements.txt
python scripts/discover_chromecasts.py
```

The script lists discovered Cast devices and exits. It does not start playback or interact with Kodi.

### Network requirements

Device discovery uses mDNS/multicast. The computer and Chromecast should be on a network that permits multicast discovery; guest Wi-Fi isolation, VLAN separation, or firewall rules can prevent discovery.

## Development principles

- Test on a computer before installing anything on LibreELEC.
- Do not stop local Kodi playback until the Cast receiver has accepted the media.
- Never commit AllDebrid credentials, tokens, private stream URLs, cookies, or sensitive logs.
- Keep the initial implementation independent of Palantir; add provider-specific handling only when the media URL behavior is understood.

## Roadmap

1. Discover Chromecast devices from a desktop computer.
2. Confirm basic Cast connection and device selection.
3. Test a known public media URL supported by the receiver.
4. Implement the Kodi context-menu action and playback-state checks.
5. Investigate protected/adaptive streams and AllDebrid compatibility.
6. Package and test the add-on on LibreELEC.

## License

MIT. See [LICENSE](LICENSE).
