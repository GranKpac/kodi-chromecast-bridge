# Tests

The first milestone is a manual integration test rather than an automated unit test:

1. Install the requirements in a Python virtual environment on a computer on the same LAN as the Chromecast.
2. Run `python scripts/discover_chromecasts.py`.
3. Confirm that the expected Chromecast name, model, and local IP address are listed.

No playback is started by this test. If discovery fails, check that multicast/mDNS traffic is allowed and that the devices are not separated by guest Wi-Fi or VLAN isolation.
