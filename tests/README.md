# Tests

These are manual integration tests performed from a Windows computer on the same LAN as a 2nd-generation Google Chromecast. The Raspberry Pi / LibreELEC installation has not been changed.

## Device discovery and control

- scripts/discover_chromecasts.py discovered the Chromecast named Salón.
- scripts/check_chromecast.py connected and read the receiver state.
- The Python client successfully sent media playback commands.

## Public media tests

- A public MP4 test URL (Big Buck Bunny, H.264/AAC, 360p) was visibly reproduced on the TV in an earlier test.
- A later repeat showed an image briefly and then stopped. A revised test script was prepared to keep the PyChromecast connection open for 15 seconds after a PLAYING status, but that revised run has not yet been confirmed.
- Several public low-resolution HLS variants were reported as PLAYING; some were visually observed during earlier tests. These results are not a comprehensive HLS compatibility certification.
- A 720p60 HLS test and a local 720p60 MP4 did not produce stable, visually confirmed playback.

**Important:** PLAYING from PyChromecast is not sufficient evidence of successful playback. Confirm the video on the TV and whether it remains visible for the expected duration.

## Local HTTP and byte-range test

- The initial local-file test used Python's standard http.server. A request with a Range: bytes=0-1023 header returned 200 OK, not 206 Partial Content.
- The project test server servidor_range.py was checked with:

```cmd
curl.exe -H "Range: bytes=0-1023" -D - "http://192.168.1.187:8000/prueba_720p60.mp4" -o NUL
```

- The server returned 206 Partial Content, confirming that it handled this byte-range request correctly.
- Repeating the 720p60 playback test after this change still did not establish stable playback. Therefore, the Range response issue was identified and corrected for the test server, but it was not proven to be the only cause of the playback failure.

## Current conclusions

1. Device discovery, connection, and command delivery work from Windows.
2. Basic playback of public media has been observed, but repeatable stable playback is not yet established.
3. The local Range-capable server responds with 206 Partial Content to the tested byte-range request.
4. The cause of the 720p60 playback failures remains unknown.
5. None of these tests yet proves that a URL obtained from Kodi, Palantir, or AllDebrid can be played directly by Chromecast.

## Next test milestone

Capture the current playback URL using Kodi's xbmc.Player().getPlayingFile() and inspect whether it is a direct MP4, HLS, DASH, local path, or protected URL. Do not publish private URLs, tokens, cookies, authorization headers, or credentials in the repository or logs.

## Original discovery test

The first milestone is a manual integration test rather than an automated unit test:

1. Install the requirements in a Python virtual environment on a computer on the same LAN as the Chromecast.
2. Run python scripts/discover_chromecasts.py.
3. Confirm that the expected Chromecast name, model, and local IP address are listed.

No playback is started by this discovery test. If discovery fails, check that multicast/mDNS traffic is allowed and that the devices are not separated by guest Wi-Fi or VLAN isolation.