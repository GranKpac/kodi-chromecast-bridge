# Kodi Chromecast Bridge

A small, experimental Kodi add-on project to send the currently playing video to a Google Cast device.

## Status

The desktop proof-of-concept has completed its initial device-discovery and Cast-control checks. Basic playback has been observed with public test media, but stable playback across formats and resolutions is not yet established. The next major milestone is to obtain the URL of media currently playing in Kodi and determine whether the Chromecast can access it.

No Kodi installation or Raspberry Pi configuration has been changed during the desktop tests.

## Target environment

- Kodi 21.x
- LibreELEC 12.x
- Raspberry Pi 5
- Google Chromecast (the current test device is a 2nd-generation model)

## Current test results

### Confirmed

- PyChromecast discovers the Chromecast on the same LAN.
- The Python client connects to the device and can inspect its receiver state.
- The Python client can send playback commands.
- A public MP4 test URL has produced visible video on the TV in an earlier test. A later repeat was not stable, so this is evidence of basic playback capability, not a reliability result.
- The Chromecast can request a media file from the Windows test computer over the LAN.
- The standard Python http.server used in an initial local-file test returned 200 OK to a Range request. The project's servidor_range.py test server was then checked separately and returned 206 Partial Content for a byte-range request.

### Partially tested / not conclusive

- Some low-resolution public HLS test streams reached playback, and some were visually observed. This does not establish general HLS compatibility.
- A 720p60 H.264/AAC local MP4 and a 720p60 HLS test did not achieve stable, visually confirmed playback.
- PyChromecast reporting PLAYING is not by itself proof that video is visibly playing on the TV.
- The cause of the 720p60 failures has not been isolated. Do not infer a codec limitation from these tests alone.

See tests/README.md for the test notes.

## Important compatibility note

Kodi's xbmc.Player().getPlayingFile() returns the current playback URL or path, but that does not guarantee a Chromecast can fetch it. The URL may be local, temporary, protected by cookies or authorization headers, or point to an adaptive HLS/DASH stream. The Chromecast must be able to reach the resource and support its protocol, container, and codecs.

AllDebrid and Palantir compatibility will be investigated after the Kodi playback URL has been captured and its accessibility to the Chromecast has been assessed. They are not assumed to work merely because Kodi can play a link.

## Desktop test environment

The initial tests were performed on a Windows computer and a Chromecast on the same local network, using a Python virtual environment and PyChromecast. The Raspberry Pi / LibreELEC installation has not yet been modified for this project.

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

## Development principles

- Test on a computer before installing anything on LibreELEC.
- Do not stop local Kodi playback until the Cast receiver has accepted the media.
- Never commit AllDebrid credentials, tokens, private stream URLs, cookies, or sensitive logs.
- Keep the initial implementation independent of Palantir; add provider-specific handling only when the media URL behavior is understood.
- Treat the receiver's reported playback state as diagnostic information, not as visual confirmation of playback.

## Roadmap

1. [x] Discover Chromecast devices from a desktop computer.
2. [x] Confirm basic Cast connection and device selection.
3. [x] Send playback commands and observe basic playback with public test media (stability and broad format support remain unverified).
4. [ ] Capture the current playback URL from Kodi and inspect its type and access requirements.
5. [ ] Determine whether the Chromecast can fetch the Kodi playback URL directly; identify when a local relay/remux/transcode is required.
6. [ ] Implement the Kodi context-menu action and playback-state checks.
7. [ ] Investigate protected/adaptive streams and AllDebrid compatibility.
8. [ ] Package and test the add-on on LibreELEC.

## License

MIT. See [LICENSE](LICENSE).