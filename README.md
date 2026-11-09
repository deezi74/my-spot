# MySpot
Open index.html on a phone or computer. This session-only prototype previews an uploaded image or video, profile soundtrack, animated profile wallpaper and adjustable feed watermark. Refresh clears the preview.

## Shared app and website
Use one identity, profile URL, social graph, privacy model and post ID across Android and web. Both clients read the same versioned theme document. Store personal feed wallpaper separately from published profile layers. Each layer records its asset, placement, order, opacity and color. Visitors can mute music and disable motion.

## Product scope
- Posts: text, photos, albums, vertical clips, long video, stories, reactions, comments, saves and sharing. Include resumable uploads, thumbnails, captions, transcoding and audience selection.
- Social: friends, follows, searchable profiles, groups, events, requests, private messages, group chat and notifications.
- Calling: voice and video from chats with ring, accept, decline, mute, camera switch and reconnect. Build authenticated signaling and WebRTC with TURN relay.
- Live: start from phone or browser, preview camera and microphone, invite co-hosts, chat, assign moderators, end stream and optionally publish a replay. Use an SFU for hosts and adaptive streaming for the audience.
- Discovery: chronological Friends and interest-based Discover. Provide explicit topic controls.
- Personal AI: optional name, voice and editable memory. Draft captions and theme changes with a preview before publishing.
- Community controls: block, report, message and call permissions, live moderation and private accounts.

## First integration test
Sign in on Android, upload a clip, and view it on the website under the same profile URL. From a second account, call the creator, join their broadcast, post a live comment, then open the replay. Verify private media stays restricted across both clients.
