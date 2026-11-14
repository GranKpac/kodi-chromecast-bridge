# Tests

Manual integration tests are documented by environment. Results from one environment must not be treated as results from another.

## Historical Windows tests

These tests were performed from a Windows computer on the same LAN as a 2nd-generation Google Chromecast.

- Device discovery and receiver-state queries worked with PyChromecast.
- Public MP4 H.264/AAC 360p was visibly reproduced in an earlier run; a later repeat stopped after a brief image.
- Some low-resolution HLS tests reported PLAYING and were visually observed, but no general HLS compatibility was established.
- A 720p60 HLS test and local 720p60 MP4 did not produce stable, visually confirmed playback.
- A Range-capable test server returned HTTP 206 for the tested byte-range request. This did not resolve the 720p60 playback issue.

A receiver-reported PLAYING state is not sufficient evidence of successful playback. Confirm the video on the TV and whether it remains visible for the expected duration.

## Raspberry Pi / LibreELEC tests (14 November 2026)

The later experiments used a Raspberry Pi 5, LibreELEC 12.2.1, Kodi 21.3 and a 2nd-generation Chromecast.

- The Cast V2 test scripts established TLS communication, sent CONNECT, queried receiver state, launched Default Media Receiver (CC1AD845) and sent LOAD.
- An MP4 using H.264 video copied without re-encoding and AAC stereo audio was observed with image and sound.
- HLS MPEG-TS and HLS fMP4 were rejected in the observed runs. The receiver requested the playlists but did not request their referenced media segments. This does not establish general HLS incompatibility.
- A fragmented-MP4 pipeline using FFmpeg and a local HTTP server started playback with image and sound while FFmpeg was still generating the file. Natural end-of-playback and automatic cleanup remain unverified.

## Current conclusions

1. Basic device discovery, connection and command delivery have been observed.
2. Playback has been observed in specific cases, but broad and repeatable format support is not established.
3. The Raspberry Pi experiment validates the tested H.264 + AAC fragmented-MP4 path only.
4. The cause of earlier 720p60 failures remains unknown.
5. None of these tests proves every URL obtained from Kodi, Palantir or AllDebrid can be played directly by Chromecast.

## Security and reproducibility

- Do not commit private stream URLs, cookies, authorization headers, API keys, passwords, session tokens, local media files or logs containing them.
- Set CAST_HOST at runtime; do not hard-code LAN addresses.
- Cast transportId values are session-specific and must be obtained dynamically from RECEIVER_STATUS.
- See [the experimental script guide](../scripts/experimental/README.md).

## Next milestone

Complete the lifecycle of the progressive-MP4 pipeline: natural end, receiver disconnect, FFmpeg termination, stale PID handling and temporary-file cleanup. Then integrate a source resolver independent of Kodi's HDMI player.
