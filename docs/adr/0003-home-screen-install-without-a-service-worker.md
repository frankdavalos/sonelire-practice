# Install to the Home Screen without a service worker; backups are the durability guarantee

_Partly superseded by ADR 0004: the install support below stays, but the iPad is used in Safari, not as a Home Screen app, and the hand checks planned in #19 were dropped._

Results and the Check log live only in the browser's localStorage, which Safari deletes after 7 days without use. The main page therefore links a web app manifest (`display: standalone`, start URL the main page, scope the folder it is served from, so it works locally and on GitHub Pages) with icons, a 180×180 Apple touch icon and the iOS head tags, so a parent can add it to the iPad Home Screen and open it full-screen. On every open the page calls `navigator.storage.persist()` when it exists and ignores the answer. It registers **no service worker**.

None of this guarantees the data survives. What Safari does is dated and partly anecdotal (as of 2026-11):

- Apple says Home Screen web apps keep their own days-of-use count, separate from Safari's 7-day cap ([WebKit: Full Third-Party Cookie Blocking and More](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/)).
- WebKit grants `persist()` on its own judgement, which favours Home Screen apps ([WebKit: Updates to Storage Policy](https://webkit.org/?p=14403)). Developers report it has to be requested on every open ([Apple Developer Forums](https://developer.apple.com/forums/thread/710157)).
- Data loss in Home Screen apps has been reported ([WebKit bug 237350](https://bugs.webkit.org/show_bug.cgi?id=237350)).

So backups the parent keeps outside the browser are the durability guarantee; Home Screen install and `persist()` only make loss less likely. Whether they hold on a real iPad is checked by hand (#19).

## Considered Options

- **Service worker with an offline cache**: rejected. Offline use isn't needed, and a cache would serve old scripts against new pages, defeating the `?v=` release token that keeps each page paired with its scripts. A service worker isn't required for a Home Screen install on iPadOS.
- **Install prompt or reminder in the app**: rejected for now. It adds UI for a one-time step that HOW_TO_USE.md can explain.
- **Show whether `persist()` was granted**: rejected. The answer is a guess that can change, and acting on it would mean nagging; backups are the answer either way.
