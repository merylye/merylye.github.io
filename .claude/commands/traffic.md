---
description: Pull fresh site analytics and give a diagnostic reading of the traffic
---

Give Meryl a diagnostic reading of her website traffic.

## Steps

1. Refresh the data:

   ```
   export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
   python3 bin/fetch_analytics.py
   ```

   If it fails on auth, run `bash bin/ga_setup.sh` to see which step is missing.
   The whole chain is: gcloud login → impersonate the `analytics-reader`
   service account → mint a token with the Analytics scope → GA4 Data API.

2. Compare against the previous snapshot where possible:

   ```
   git diff --stat _data/analytics.json
   git show HEAD:_data/analytics.json > /tmp/analytics_prev.json 2>/dev/null
   ```

   If a previous version exists, report what actually changed rather than
   restating the same totals.

3. Read `_data/analytics.json` and write the diagnosis.

## What makes this useful rather than a number dump

Lead with what is surprising or actionable, not with totals. Specifically look for:

- **Traffic that is probably not human.** Datacenter cities (Council Bluffs =
  Google, Ashburn = AWS), implausible city concentrations for a personal
  academic site, high views with near-zero engagement time, one city
  dominating totals. Say so plainly and estimate how much it inflates things.
- **Engagement outliers.** Pages holding far more or less attention than the
  site average. Seconds-per-view is `avg_seconds / views` in `top_pages`.
- **Spikes.** Any day well above baseline. Try to attribute it: cross-check
  referrers, and check `git log --since` for anything published around then.
- **Blog read-through.** `post_reads` holds read_25/50/75/100 and read_time_*
  buckets per post. Low 100% rates mean people are not finishing. This is
  empty until enough traffic hits instrumented pages.
- **Repeat audience.** `new_vs_returning`: sessions per returning user shows
  whether there are regulars.
- **Timing.** `heatmap` is dayOfWeek (0 = Sunday) by hour in the visitor's
  local time, so it is a blend of timezones - do not read it as her local time.

## Tone and honesty

- Lead with the two or three things she would not already know.
- Distinguish what the data shows from what it suggests. Bot traffic is an
  inference from shape, not a fact the API reports.
- Small numbers are noisy. A jump from 2 to 6 is not a trend; say so.
- Do not congratulate or pad. If a week was quiet, that is the finding.
- Note when an effect is better explained by something boring (a crawler, a
  single referrer, a deploy) than by readership.
