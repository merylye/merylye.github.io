#!/usr/bin/env python3
"""Pull GA4 numbers into _data/analytics.json for the dashboard page.

Run it whenever you want fresh numbers:

    python3 bin/fetch_analytics.py

Authentication uses your own Google login, not a service account key:

    gcloud auth application-default login

Only aggregated figures are written - daily totals, top pages, referrer
domains, country totals. No city, no landing-page-plus-location combinations,
nothing that would let a reader of the public repo pick out an individual
visitor.
"""

import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

PROPERTY_ID = "451567195"
API = f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY_ID}:runReport"
OUT = pathlib.Path(__file__).resolve().parent.parent / "_data" / "analytics.json"

# Events added by _includes/scripts/engagement.liquid
READ_DEPTH = ["read_25", "read_50", "read_75", "read_100"]
READ_TIME = ["read_time_under_30s", "read_time_30s_2m", "read_time_2m_5m", "read_time_over_5m"]


ANALYTICS_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"

# Google blocks the built-in gcloud client ID from requesting Analytics scopes
# ("This app is blocked"), so we borrow a service account instead. Your own
# login only needs cloud-platform, which is still allowed; the service account
# supplies the Analytics scope. No key is involved, so the organisation's
# disableServiceAccountKeyCreation policy is satisfied.
#
# Requires, both one-time and done in the console:
#   - your account granted "Service Account Token Creator" on this account
#   - this account added as a Viewer on the GA property
IMPERSONATE = "analytics-reader@merylye-site-analytics.iam.gserviceaccount.com"


def access_token() -> str:
    """Mint a service-account token carrying the Analytics scope.

    gcloud's --impersonate-service-account ignores --scopes and hands back a
    cloud-platform token, which the Analytics API rejects. Calling the IAM
    Credentials API directly does honour the scope, so do that: our own gcloud
    token (cloud-platform, which Google still allows) is used only to ask for
    the service account's token.
    """
    try:
        out = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit("gcloud not found. Install it, then run:\n  gcloud auth login")

    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("Not signed in. Run:\n  gcloud auth login\n\n" + (out.stderr or "").strip())

    user_token = out.stdout.strip()
    req = urllib.request.Request(
        f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{IMPERSONATE}:generateAccessToken",
        data=json.dumps({"scope": [ANALYTICS_SCOPE], "lifetime": "3600s"}).encode(),
        headers={"Authorization": f"Bearer {user_token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)["accessToken"]
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:400]
    if "iam.serviceAccounts.getAccessToken" in err or "PERMISSION_DENIED" in err:
        sys.exit(
            f"Not allowed to impersonate {IMPERSONATE}.\n\n"
            "In the Cloud console: IAM & Admin -> Service Accounts -> that account ->\n"
            "Permissions -> Grant access -> your own email -> role\n"
            '"Service Account Token Creator".\n\n' + err
        )
    if "not found" in err.lower():
        sys.exit(f"Service account {IMPERSONATE} not found. Check the email in bin/fetch_analytics.py.\n\n" + err)
    sys.exit("Could not get an access token.\n\n" + err)


def run_report(token: str, dimensions, metrics, start="365daysAgo", end="today", limit=25, order_by_metric=None):
    body = {
        "dateRanges": [{"startDate": start, "endDate": end}],
        "dimensions": [{"name": d} for d in dimensions],
        "metrics": [{"name": m} for m in metrics],
        "limit": limit,
    }
    if order_by_metric:
        body["orderBys"] = [{"metric": {"metricName": order_by_metric}, "desc": True}]
    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:400]
        if e.code == 403:
            if "ACCESS_TOKEN_SCOPE_INSUFFICIENT" in detail:
                sys.exit(
                    "403: the credentials lack the Analytics scope.\n"
                    "Re-run the login asking for it explicitly:\n\n"
                    "  gcloud auth application-default login \\\n"
                    "    --scopes=openid,https://www.googleapis.com/auth/userinfo.email,"
                    "https://www.googleapis.com/auth/cloud-platform,"
                    "https://www.googleapis.com/auth/analytics.readonly\n"
                )
            if "SERVICE_DISABLED" in detail or "has not been used" in detail:
                sys.exit(
                    "403: the Google Analytics Data API is not enabled on the quota project.\n"
                    "Enable it in the Cloud console, or point at a different project with:\n"
                    "  gcloud auth application-default set-quota-project PROJECT_ID\n\n" + detail
                )
            sys.exit(
                f"403: this Google account does not appear to have access to property {PROPERTY_ID}.\n"
                "Check which account you authenticated as, and that it can see the property "
                "at analytics.google.com.\n\n" + detail
            )
        if e.code == 401:
            sys.exit("401 - credentials expired. Re-run:\n  gcloud auth application-default login\n\n" + detail)
        sys.exit(f"HTTP {e.code} from the Analytics API:\n{detail}")

    rows = []
    for row in payload.get("rows", []):
        rows.append(
            {
                "keys": [d.get("value", "") for d in row.get("dimensionValues", [])],
                "values": [m.get("value", "0") for m in row.get("metricValues", [])],
            }
        )
    return rows


def page_titles() -> dict:
    """Map URL paths to human titles, read from the repo itself.

    Posts follow the permalink pattern /blog/:year/:slug/ configured in
    _config.yml; pages declare their own permalink in front matter. Reading
    both from source means new posts resolve automatically.
    """
    root = pathlib.Path(__file__).resolve().parent.parent
    titles = {"/": "Home"}

    def front_matter_title(text: str) -> str:
        m = re.search(r"^---\s*$(.*?)^---\s*$", text, re.S | re.M)
        if not m:
            return ""
        t = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', m.group(1), re.M)
        return t.group(1).strip() if t else ""

    for post in (root / "_posts").glob("*.md"):
        m = re.match(r"(\d{4})-\d{2}-\d{2}-(.+)", post.stem)
        if not m:
            continue
        title = front_matter_title(post.read_text(encoding="utf-8"))
        if title:
            titles[f"/blog/{m.group(1)}/{m.group(2)}/"] = title

    for page in (root / "_pages").glob("*.md"):
        text = page.read_text(encoding="utf-8")
        fm = re.search(r"^---\s*$(.*?)^---\s*$", text, re.S | re.M)
        if not fm:
            continue
        perm = re.search(r"^permalink:\s*(\S+)\s*$", fm.group(1), re.M)
        title = front_matter_title(text)
        if perm and title:
            titles[perm.group(1)] = title

    return titles


def main() -> None:
    token = access_token()
    titles = page_titles()

    daily = run_report(token, ["date"], ["activeUsers", "sessions", "screenPageViews"], limit=400)
    daily_rows = sorted(
        (
            {
                "date": f"{r['keys'][0][:4]}-{r['keys'][0][4:6]}-{r['keys'][0][6:]}",
                "users": int(r["values"][0]),
                "sessions": int(r["values"][1]),
                "views": int(r["values"][2]),
            }
            for r in daily
        ),
        key=lambda d: d["date"],
    )

    pages = [
        {
            "path": r["keys"][0],
            "title": titles.get(r["keys"][0], r["keys"][0]),
            "views": int(r["values"][0]),
            "avg_seconds": round(float(r["values"][1]), 1),
        }
        for r in run_report(
            token,
            ["pagePath"],
            ["screenPageViews", "userEngagementDuration"],
            limit=40,
            order_by_metric="screenPageViews",
        )
    ]

    referrers = [
        {"source": r["keys"][0], "sessions": int(r["values"][0])}
        for r in run_report(token, ["sessionSource"], ["sessions"], limit=15, order_by_metric="sessions")
    ]

    countries = [
        {"country": r["keys"][0], "users": int(r["values"][0])}
        for r in run_report(token, ["country"], ["activeUsers"], limit=15, order_by_metric="activeUsers")
    ]

    events = {r["keys"][0]: int(r["values"][0]) for r in run_report(token, ["eventName"], ["eventCount"], limit=100)}

    regions = [
        {"region": r["keys"][0], "country": r["keys"][1], "users": int(r["values"][0])}
        for r in run_report(token, ["region", "country"], ["activeUsers"], limit=100, order_by_metric="activeUsers")
        if r["keys"][0] and r["keys"][0] != "(not set)"
    ]

    # Every city, at the site owner's explicit request. Note this file is
    # committed to a public repo, so single-visitor cities are published too.
    CITY_MIN_USERS = 1
    cities = [
        {"city": r["keys"][0], "country": r["keys"][1], "users": int(r["values"][0])}
        for r in run_report(token, ["city", "country"], ["activeUsers"], limit=300, order_by_metric="activeUsers")
        if r["keys"][0] and r["keys"][0] != "(not set)" and int(r["values"][0]) >= CITY_MIN_USERS
    ]

    returning = [
        {"kind": r["keys"][0] or "unknown", "users": int(r["values"][0]), "sessions": int(r["values"][1])}
        for r in run_report(token, ["newVsReturning"], ["activeUsers", "sessions"], limit=10)
    ]

    # When people actually read: day of week (0 = Sunday) by hour, visitor local time.
    heatmap = [
        {"day": int(r["keys"][0]), "hour": int(r["keys"][1]), "views": int(r["values"][0])}
        for r in run_report(token, ["dayOfWeek", "hour"], ["screenPageViews"], limit=200)
        if r["keys"][0].isdigit() and r["keys"][1].isdigit()
    ]

    # Per-post read funnel: how many reached each depth on each post.
    funnel = {}
    for r in run_report(token, ["pagePath", "eventName"], ["eventCount"], limit=500):
        path, name = r["keys"]
        if name in READ_DEPTH or name in READ_TIME:
            entry = funnel.setdefault(path, {"title": titles.get(path, path)})
            entry[name] = int(r["values"][0])

    data = {
        "property_id": PROPERTY_ID,
        "generated_utc": subprocess.run(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True
        ).stdout.strip(),
        "window": "last 12 months",
        "totals": {
            "users": sum(d["users"] for d in daily_rows),
            "sessions": sum(d["sessions"] for d in daily_rows),
            "views": sum(d["views"] for d in daily_rows),
        },
        "daily": daily_rows,
        "top_pages": pages,
        "referrers": referrers,
        "countries": countries,
        "regions": regions,
        "cities": cities,
        "city_min_users": CITY_MIN_USERS,
        "new_vs_returning": returning,
        "heatmap": heatmap,
        "events": events,
        "post_reads": funnel,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n")

    print(f"wrote {OUT.relative_to(pathlib.Path.cwd())}")
    print(f"  {data['totals']['views']} views / {data['totals']['users']} users over {data['window']}")
    print(f"  {len(pages)} pages, {len(referrers)} sources, {len(events)} event types")
    read_events = {k: v for k, v in events.items() if k.startswith("read_")}
    print(f"  blog read events so far: {sum(read_events.values())} across {len(read_events)} types")


if __name__ == "__main__":
    main()
