# Use Sonelire in Safari on the iPad, not the Home Screen app; backups are the only durability guarantee

ADR 0003 made the app installable to the iPad Home Screen so its saved data would be less likely to be deleted. In use, the Home Screen app breaks the phone companion's QR return: the iPad Camera opens results QR links only in Safari, and the Home Screen app keeps its own storage, so the scanned marks land in a Safari page that has no unfinished Check. The parent then has to fall back to **Share results** or a code file for every Check. We therefore use Sonelire in Safari on the iPad and do not set up the Home Screen app. The phone companion flow was checked by hand in Safari on the real iPad and phone, which replaces the Home Screen checks planned in #19.

The trade-off is durability. Safari can delete the site's localStorage after 7 days of Safari use without opening the site, and the Home Screen app's separate days-of-use count no longer helps. Backup files kept outside the browser, plus the Results tab's reminder when a saved Check has gone 30 days without one, are now the only protection against that loss. ADR 0003 already treated backups as the guarantee, so nothing in the code changes. The manifest, icons and `navigator.storage.persist()` call stay: they cost nothing in Safari, and the Home Screen install still works for anyone who prefers it and accepts the QR limitation.

## Considered Options

- **Keep the Home Screen app and return marks only by file or code**: rejected. It adds a manual step to every Check to guard against a deletion that a regular backup also covers.
- **Remove the manifest and Home Screen support**: rejected for now. It doesn't affect Safari use, and removing it would make a later return to the Home Screen app a code change instead of a setup choice.
