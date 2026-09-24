# Search method

## The matrix

Search is queries x locations, not one query. Titles for the same job vary
enormously, so a single query misses most of the market.

Run 6-10 queries per track across each configured location. Stop when results
saturate, meaning the same postings keep returning under different query and
location pairs. That saturation is the signal that the metro is covered, and it
usually arrives faster than expected.

**IT track:** IT support specialist, help desk technician, systems
administrator, desktop support technician, IT technician, network administrator,
IT coordinator, technical support analyst, IT specialist, MSP technician

**AV / media track:** audio visual technician, AV installation technician, AV
service technician, audio engineer, production technician, media systems, low
voltage technician

Adjust per the candidate's tracks in config.

## Sourcing traps

Each of these cost real time to discover.

**Do not scrape job boards directly.** Roughly ten rapid requests to Indeed
triggers Cloudflare, which then blocks the browser for hours behind a CAPTCHA
you must not solve. Use the job-search connector. If it is unavailable, go to
employer portals directly rather than scraping an aggregator.

**Schools and universities hide their IT jobs.** Districts post paraeducators,
coaches, and bus attendants to public boards, and route every IT role to their
own applicant tracking system. Check the ATS directly: Frontline/AppliTrack
(`applitrack.com/<district>`), SchoolSpring, Workday. The district's public
careers page is often a marketing landing page with the real board one link
deeper. Note that the ATS slug rarely matches the district's initials.

**Large multinationals may have no local IT roles at all.** Support is
frequently offshored. Check the actual job feed before assuming a big local
employer is a target; one packaging company had 11 of 13 IT openings in Serbia
and Brazil with a single local role, a finance data manager.

**Airline IT lives at corporate HQ, not the hub airport.** A hub is a station:
ramp, customer service, maintenance. Only a carrier headquartered locally has a
local IT organization.

**Retail tech roles are invisible on aggregators.** Apple, for one, posts only
to its own board. If the candidate has consumer-tech aptitude, check those
directly.

**Custom AV integration gates on control platforms.** Nearly every integration
role above $30/hour requires Control4, Crestron, Savant, URC, or Lutron
programming. Those certifications are generally dealer-gated, so an individual
cannot simply buy one. The way in is a shop that lists them as preferred rather
than required.

## Odds calibration

State a percentage, label it as judgment, and be willing to say a number below
50. An honest low estimate with the blocker named is more useful than optimism.

| Signal | Effect |
|---|---|
| Meets every required item, several preferred | 70-80% |
| Meets required, missing one preferred | 60-70% |
| Missing one *required* item, equivalency clause exists | 40-55% |
| Missing a requirement stated with a year count | subtract heavily |
| Requirement restated twice, or tested at interview | near-disqualifying |
| Hard credential gate: clearance, license, certification | disqualified, say so |

A requirement with a number attached ("3 years of X", "5+ years") is a real
filter. A requirement in a preferred list is not.

## Disqualifiers to check every time

- **Security clearance.** "Must possess an active Secret clearance" means an
  uncleared candidate is filtered before a human reads it. Not a stretch.
- **Pay floor**, including a range whose *bottom* breaches it.
- **Schedule**, per the candidate's constraints. Distinguish a scheduled
  weekend shift from an on-call rotation; the first is usually disqualifying
  and the second is often negotiable.
- **Relocation required before start.**
- **Remote that is not remote.** Aggregators mislabel constantly. Check the
  posting body for a physical location.
- **Stale postings.** Anything past about six weeks may be filled. Worth
  applying, worth flagging.

## What to report

Qualifying roles ranked by odds, each with pay, location, deadline, and the one
thing that could sink it. Then disqualified roles with the specific reason,
because that shows the market's shape. Then near-misses worth watching.

Structural findings are worth as much as listings. "Every integrator in this
metro gates on Control4" changes what the candidate does next more than any
single posting does.
