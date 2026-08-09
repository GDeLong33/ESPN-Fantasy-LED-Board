# ESPN-Fantasy-LED-Board
 
A physical scoreboard for a 4-person mini-league inside a 14-team ESPN Fantasy Football league. A Raspberry Pi Pico W will drive an LED matrix display, while a Node.js backend hosted on Oracle Cloud handles ESPN authentication, data polling, and parsing.
 
## How it will work
 
**Server (Oracle Cloud)**
- Polls ESPN's private Fantasy Football API on an interval using authenticated session cookies (`SWID`, `espn_s2`)
- Parses the response and filters it down to the 4 relevant teams
- Exposes a small internal endpoint that returns a lightweight JSON payload
**Pico W**
- Connects to WiFi
- Periodically fetches the small JSON payload from the server (not ESPN directly)
- Renders team names and scores on the LED matrix, rotating through teams
This split keeps ESPN auth/parsing off the Pico entirely — the Pico only ever talks to the server, and only ever displays what it's given.
 
## Hardware
 
- Raspberry Pi Pico W
- Interstate 75 W board
- 64x32 HUB75 LED matrix panel
## Stack
 
- **Pico:** MicroPython
- **Server:** Node.js / Express
- **Data source:** ESPN Fantasy Football API (unofficial, private league via cookie auth)
- **Hosting:** Oracle Cloud (Ampere A1)
## Notes
 
- ESPN's Fantasy API is unofficial and undocumented by ESPN; endpoints/response shapes could change without notice.
- Live scoring only really moves during NFL game windows (Sun/Mon/Thu), so polling frequency will be adjusted around that.
- ESPN session cookies are kept server-side only and are never committed to this repo.s