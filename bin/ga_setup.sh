#!/usr/bin/env bash
# Status check for the analytics dashboard's Google setup.
#
#   bash bin/ga_setup.sh
#
# Read-only: it changes nothing, it just reports what is and is not in place.
# Uses the same token path as bin/fetch_analytics.py, because gcloud's
# --impersonate-service-account ignores --scopes and gives a misleading answer.
set -uo pipefail

PROJECT="merylye-site-analytics"
SA="analytics-reader@${PROJECT}.iam.gserviceaccount.com"
SCOPE="https://www.googleapis.com/auth/analytics.readonly"
PROPERTY="451567195"

if ! command -v gcloud >/dev/null 2>&1; then
  export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
fi

ACCOUNT="$(gcloud config get-value account 2>/dev/null)"
echo "signed in as            : ${ACCOUNT:-NOT SIGNED IN (run: gcloud auth login)}"

if gcloud services list --enabled --project="$PROJECT" --format='value(config.name)' 2>/dev/null | grep -q iamcredentials; then
  echo "IAM Credentials API     : enabled"
else
  echo "IAM Credentials API     : NOT enabled"
fi

USER_TOKEN="$(gcloud auth print-access-token 2>/dev/null)"
SA_TOKEN="$(curl -s -X POST \
  "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/${SA}:generateAccessToken" \
  -H "Authorization: Bearer ${USER_TOKEN}" -H 'Content-Type: application/json' \
  -d "{\"scope\":[\"${SCOPE}\"],\"lifetime\":\"3600s\"}" |
  python3 -c 'import sys,json;print(json.load(sys.stdin).get("accessToken",""))' 2>/dev/null)"

if [ -z "$SA_TOKEN" ]; then
  echo "service account token   : CANNOT MINT - grant yourself Service Account Token Creator"
  exit 1
fi
echo "service account token   : ok"

ROWS="$(curl -s -X POST "https://analyticsdata.googleapis.com/v1beta/properties/${PROPERTY}:runReport" \
  -H "Authorization: Bearer ${SA_TOKEN}" -H 'Content-Type: application/json' \
  -d '{"dateRanges":[{"startDate":"28daysAgo","endDate":"today"}],"metrics":[{"name":"screenPageViews"}]}' |
  python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("rowCount") or 0)' 2>/dev/null)"

if [ "${ROWS:-0}" -gt 0 ]; then
  echo "GA property ${PROPERTY}   : readable, data present"
  echo
  echo "All set. Run:  python3 bin/fetch_analytics.py"
else
  echo "GA property ${PROPERTY}   : reachable but returns no data"
  echo
  echo "Remaining step - in the browser, no command for this:"
  echo "  analytics.google.com -> Admin -> Property Access Management -> +"
  echo "  add   $SA"
  echo "  role  Viewer"
  echo
  echo "Sign into Analytics as whichever account administers the property."
fi
