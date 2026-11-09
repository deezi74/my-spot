# MySpot shared-feed beta
Run python3 server.py from the extracted project on a trusted computer. Open http://localhost:8000 on that computer. Phones on the same private Wi-Fi can visit http://COMPUTER-LAN-IP:8000. Create two different test handles. Publish a caption and a JPEG on one device, tap Refresh feed on the other, then restart the server and confirm the post persists.

This closed-test server uses SQLite. All signed-in testers can read the beta feed. Use test credentials and media intended for the whole test group. Keep the database on persistent storage. For Android home-screen installation serve behind HTTPS and select Install app or Add to Home screen in the browser. Set HTTPS_ONLY=1 behind HTTPS. No offline feed is included.

Profile themes, pages, groups and marketplace are still local previews. Calls, live streams, personal AI and cross-account profile customization are planned. Public release requires moderation, abuse limits, account recovery and scalable media storage.
