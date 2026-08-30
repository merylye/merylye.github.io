---
layout: page
title: driving
permalink: /driving/
description: a report card from my passengers
nav: false
---

<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bungee&display=swap" />

<div class="dr">
  <div class="dr-sticker">
    <svg class="dr-wheel" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
      <circle cx="50" cy="50" r="41" fill="none" stroke="currentColor" stroke-width="11" />
      <path d="M12 50h76M50 50v38" fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" />
      <circle cx="50" cy="50" r="14" fill="var(--paint)" />
    </svg>
    <span class="dr-sticker-q">Rate my driving</span>
  </div>

  <p class="dr-status" id="dr-status">Warming up the engine&hellip;</p>

  <div id="dr-body" hidden>
    <p class="dr-intro">Based on <b id="dr-n">0</b> <span id="dr-n-label">rides</span></p>

    <h2 class="dr-h">Skills</h2>
    <div id="dr-skills" class="dr-grid"></div>

    <h2 class="dr-h">How safe did you feel?</h2>
    <div id="dr-safe"></div>

    <h2 class="dr-h">How willing would you be to ride with Meryl again?</h2>
    <div id="dr-willing"></div>

    <h2 class="dr-h">Would you trust me to drive your child?</h2>
    <div id="dr-child"></div>

    <div id="dr-text"></div>

  </div>
</div>

<style>
  .dr {
    /* road-sign palette, scoped to this page */
    --road: #ebe7e0;
    --paint: #f2b705;
    --bad: #d64545;
    --mid: #e0912f;
    --good: #3f9960;
    --plate-bg: #f6f4ec;
    --plate-ink: #17171a;
    --bubble: rgba(0, 0, 0, 0.035);
  }
  html[data-theme="dark"] .dr {
    --road: #2c2c31;
    --paint: #f5c22b;
    --bad: #e26565;
    --mid: #eda94f;
    --good: #57b87c;
    --plate-bg: #22221e;
    --plate-ink: #f2efe4;
    --bubble: rgba(255, 255, 255, 0.05);
  }

  /* ---- bumper sticker ---- */
  .dr-sticker {
    background: var(--plate-ink);
    color: var(--plate-bg);
    border-radius: 6px;
    padding: 1rem 1.25rem 0.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.9rem;
    border-bottom: 5px solid var(--paint);
    margin-bottom: 1.25rem;
  }
  .dr-wheel {
    flex: 0 0 auto;
    width: clamp(2.1rem, 8vw, 3.1rem);
    height: clamp(2.1rem, 8vw, 3.1rem);
    transform: rotate(-12deg);
  }
  .dr-sticker-q {
    display: block;
    font-family: "Bungee", "Impact", sans-serif;
    font-size: clamp(1.35rem, 5.5vw, 2.1rem);
    line-height: 1.1;
    letter-spacing: 0.01em;
    text-transform: uppercase;
  }

  .dr-status {
    color: var(--global-text-color-light);
  }
  .dr-intro {
    font-size: 1rem;
    color: var(--global-text-color-light);
  }
  .dr-intro b {
    color: var(--global-text-color);
    font-size: 1.15rem;
  }

  /* ---- section headings as road markings ---- */
  .dr-h {
    font-family: "Bungee", "Impact", sans-serif;
    font-size: 1.05rem !important;
    letter-spacing: 0.01em;
    margin-top: 2.5rem;
    margin-bottom: 0.9rem;
    padding-bottom: 0.5rem;
    background-image: linear-gradient(to right, var(--paint) 0 14px, transparent 14px 26px);
    background-repeat: repeat-x;
    background-size: 26px 4px;
    background-position: left bottom;
  }

  /* ---- skill cards ---- */
  .dr-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
    gap: 0.8rem;
  }
  .dr-card {
    background: var(--bubble);
    border-radius: 5px;
    padding: 0.85rem 0.95rem 0.75rem;
  }
  .dr-card-top {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.7rem;
  }
  .dr-skill {
    font-size: 0.88rem;
    line-height: 1.25;
    font-weight: 600;
  }
  .dr-mean {
    font-family: ui-monospace, "SFMono-Regular", Menlo, monospace;
    font-size: 1.4rem;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }
  .dr-hist {
    display: flex;
    align-items: flex-end;
    gap: 5px;
    height: 3.1rem;
    padding: 0 0.15rem;
    background: var(--road);
    border-radius: 3px 3px 0 0;
  }
  .dr-hcol {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    height: 100%;
  }
  .dr-hbar {
    border-radius: 2px 2px 0 0;
    min-height: 3px;
  }
  .dr-hbar.r1,
  .dr-hbar.r2 {
    background: var(--bad);
  }
  .dr-hbar.r3 {
    background: var(--mid);
  }
  .dr-hbar.r4,
  .dr-hbar.r5 {
    background: var(--good);
  }
  .dr-hbar.zero {
    background: transparent;
    box-shadow: inset 0 -3px 0 rgba(128, 128, 128, 0.25);
  }
  .dr-hcount {
    font-family: ui-monospace, "SFMono-Regular", Menlo, monospace;
    font-size: 0.7rem;
    text-align: center;
    height: 0.95rem;
    line-height: 0.95rem;
    opacity: 0.75;
  }
  /* the road under the bars */
  .dr-lane {
    height: 5px;
    background-image: linear-gradient(to right, var(--paint) 0 12px, transparent 12px 22px);
    background-repeat: repeat-x;
    background-size: 22px 3px;
    background-position: left center;
    background-color: var(--road);
    border-radius: 0 0 3px 3px;
  }
  .dr-ends {
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    opacity: 0.7;
    margin-top: 0.35rem;
  }
  .dr-sub {
    font-size: 0.74rem;
    color: var(--global-text-color-light);
    margin-top: 0.35rem;
  }

  /* ---- option tallies ---- */
  .dr-opt {
    display: grid;
    grid-template-columns: 1fr 5.5rem 1.5rem;
    gap: 0.6rem;
    align-items: center;
    padding: 0.35rem 0;
  }
  .dr-opt-label {
    font-size: 0.9rem;
  }
  .dr-opt.empty {
    opacity: 0.45;
  }
  .dr-opt-track {
    height: 0.9rem;
    background: var(--road);
    border-radius: 2px;
    overflow: hidden;
  }
  .dr-opt-fill {
    height: 100%;
    border-radius: 2px;
    background: var(--good);
  }
  .dr-opt-fill.bad {
    background: var(--bad);
  }
  .dr-opt-fill.mid {
    background: var(--mid);
  }
  .dr-opt-fill.neutral {
    background: var(--plate-ink);
    opacity: 0.55;
  }
  .dr-opt-n {
    font-family: ui-monospace, "SFMono-Regular", Menlo, monospace;
    text-align: right;
    font-variant-numeric: tabular-nums;
    font-size: 0.9rem;
  }

  /* ---- quotes as speech bubbles ---- */
  .dr-q h3 {
    font-family: "Bungee", "Impact", sans-serif;
    font-size: 0.92rem;
    margin: 2.2rem 0 0.9rem;
    line-height: 1.35;
  }
  .dr-quotes {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }
  .dr-quotes li {
    position: relative;
    background: var(--bubble);
    border-radius: 10px;
    padding: 0.6rem 0.85rem;
    font-size: 0.95rem;
  }
  .dr-quotes li::after {
    content: "";
    position: absolute;
    left: 1.4rem;
    bottom: -7px;
    width: 0;
    height: 0;
    border-left: 8px solid transparent;
    border-right: 0 solid transparent;
    border-top: 8px solid var(--bubble);
  }
  .dr-na {
    color: var(--global-text-color-light);
  }

  @media (max-width: 576px) {
    .dr-opt {
      grid-template-columns: 1fr 3.5rem 1.4rem;
      gap: 0.45rem;
    }
    .dr-opt-label {
      font-size: 0.82rem;
    }
    .dr-ends {
      font-size: 0.65rem;
    }
  }
</style>

<script>
  (function () {
    // ---- Data source -------------------------------------------------------
    // Live read of the responses sheet. The query deliberately omits column B
    // (Name), so this page never requests respondent names.
    var SHEET = "1R7aTj_JBSiXLe6FVUcxmnTJUvFhe7huPQi0eLhurZUI";
    var QUERY = "select A,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q";
    var DATA_URL =
      "https://docs.google.com/spreadsheets/d/" + SHEET + "/gviz/tq?tqx=out:csv&tq=" + encodeURIComponent(QUERY);

    // Answer choices come from the Google Form itself, not from the responses,
    // so options nobody has picked still show with a count of 0. If the form's
    // wording ever changes, update these lists to match it exactly.
    var SAFE_CHOICES = [
      "1- Not safe at all",
      "2- Unsafe, but YOLO",
      "3- Slightly unsafe, but this was my only option",
      "4- Relatively safe",
      "5- Super safe, I would trust Meryl with my life",
    ];
    var WILLING_CHOICES = [
      "1- Unwilling, I'm never riding with Meryl again",
      "2- Largely unwilling, though I would accept a ride if it was my only option",
      "3- Eh, I'd risk my life again",
      "4- Willing",
      "5- Super willing",
    ];
    var CHILD_CHOICES = ["Yes", "No", "Maybe"];
    var CHILD_TONE = { Yes: "", No: "bad", Maybe: "mid", Other: "neutral" };

    var SKILLS = [
      { col: 3, label: "Parallel parking" },
      { col: 4, label: "Regular parking" },
      { col: 5, label: "Turning" },
      { col: 6, label: "Merging/Changing lanes" },
      { col: 7, label: "Maintaining an appropriate speed" },
      { col: 8, label: "Braking smoothly" },
      { col: 9, label: "Following traffic signs/signals" },
    ];
    var SAFE = 10;
    var WILLING = 11;
    var CHILD = 14;
    var TEXTS = [
      { col: 12, title: "What is Meryl's strongest driving skill?" },
      { col: 13, title: "What is Meryl's weakest driving skill?" },
      { col: 15, title: "Anything else I should know about my driving?" },
    ];

    function parseCSV(text) {
      var rows = [],
        row = [],
        field = "",
        quoted = false,
        i,
        c;
      for (i = 0; i < text.length; i++) {
        c = text.charAt(i);
        if (quoted) {
          if (c === '"') {
            if (text.charAt(i + 1) === '"') {
              field += '"';
              i++;
            } else {
              quoted = false;
            }
          } else {
            field += c;
          }
        } else if (c === '"') {
          quoted = true;
        } else if (c === ",") {
          row.push(field);
          field = "";
        } else if (c === "\n") {
          row.push(field);
          rows.push(row);
          row = [];
          field = "";
        } else if (c !== "\r") {
          field += c;
        }
      }
      if (field.length || row.length) {
        row.push(field);
        rows.push(row);
      }
      return rows;
    }

    function el(tag, cls, txt) {
      var e = document.createElement(tag);
      if (cls) e.className = cls;
      if (txt !== undefined) e.textContent = txt;
      return e;
    }

    function renderSkills(host, rows) {
      SKILLS.forEach(function (skill) {
        var counts = [0, 0, 0, 0, 0];
        var na = 0;
        var sum = 0;
        var n = 0;
        rows.forEach(function (r) {
          var v = parseInt((r[skill.col] || "").trim(), 10);
          if (v >= 1 && v <= 5) {
            counts[v - 1]++;
            sum += v;
            n++;
          } else {
            na++;
          }
        });

        var card = el("div", "dr-card");
        var top = el("div", "dr-card-top");
        top.appendChild(el("div", "dr-skill", skill.label));
        top.appendChild(el("div", "dr-mean", n ? (sum / n).toFixed(1) : "–"));
        card.appendChild(top);

        var max = 0;
        counts.forEach(function (c) {
          if (c > max) max = c;
        });

        var hist = el("div", "dr-hist");
        counts.forEach(function (c, i) {
          var col = el("div", "dr-hcol");
          col.appendChild(el("div", "dr-hcount", c ? String(c) : ""));
          var bar = el("div", c ? "dr-hbar r" + (i + 1) : "dr-hbar zero");
          bar.style.height = max ? (c / max) * 100 + "%" : "0";
          col.appendChild(bar);
          hist.appendChild(col);
        });
        card.appendChild(hist);
        card.appendChild(el("div", "dr-lane"));

        var ends = el("div", "dr-ends");
        ends.appendChild(el("span", null, "1 = bad"));
        ends.appendChild(el("span", null, "5 = good"));
        card.appendChild(ends);

        if (na) {
          card.appendChild(el("div", "dr-sub", na + (na === 1 ? " person" : " people") + " answered N/A"));
        }
        host.appendChild(card);
      });
    }

    // Every choice the form offers, with its tally - including unpicked ones.
    function renderChoices(host, rows, col, choices, allowOther, scaled) {
      var counts = {};
      var other = [];
      choices.forEach(function (c) {
        counts[c] = 0;
      });
      rows.forEach(function (r) {
        var raw = (r[col] || "").trim();
        if (!raw) return;
        if (counts.hasOwnProperty(raw)) counts[raw]++;
        else if (allowOther) other.push(raw);
      });

      var max = 0;
      choices.forEach(function (c) {
        if (counts[c] > max) max = counts[c];
      });
      if (allowOther && other.length > max) max = other.length;

      function tone(label, i) {
        if (scaled) return i < 2 ? "bad" : i === 2 ? "mid" : "";
        return CHILD_TONE[label] || "";
      }

      function addRow(label, n, i) {
        var row = el("div", n ? "dr-opt" : "dr-opt empty");
        row.appendChild(el("div", "dr-opt-label", label));
        var track = el("div", "dr-opt-track");
        if (n) {
          var t = tone(label, i);
          var fill = el("div", t ? "dr-opt-fill " + t : "dr-opt-fill");
          fill.style.width = max ? (n / max) * 100 + "%" : "0";
          track.appendChild(fill);
        }
        row.appendChild(track);
        row.appendChild(el("div", "dr-opt-n", String(n)));
        host.appendChild(row);
      }

      choices.forEach(function (c, i) {
        addRow(c, counts[c], i);
      });
      if (allowOther) {
        addRow("Other", other.length, choices.length);
        if (other.length) {
          var ul = el("ul", "dr-quotes");
          ul.style.marginTop = "0.7rem";
          other.forEach(function (t) {
            ul.appendChild(el("li", null, t));
          });
          host.appendChild(ul);
        }
      }
    }

    function renderText(host, rows) {
      TEXTS.forEach(function (q) {
        var wrap = el("div", "dr-q");
        wrap.appendChild(el("h3", null, q.title));
        var answers = [];
        rows.forEach(function (r) {
          var t = (r[q.col] || "").trim();
          if (t) answers.push(t);
        });
        if (!answers.length) {
          wrap.appendChild(el("p", "dr-na", "No answers yet."));
        } else {
          var ul = el("ul", "dr-quotes");
          answers.forEach(function (t) {
            ul.appendChild(el("li", null, t));
          });
          wrap.appendChild(ul);
        }
        host.appendChild(wrap);
      });
    }

    function render(rows) {
      document.getElementById("dr-n").textContent = rows.length;
      document.getElementById("dr-n-label").textContent = rows.length === 1 ? "ride" : "rides";
      renderSkills(document.getElementById("dr-skills"), rows);
      renderChoices(document.getElementById("dr-safe"), rows, SAFE, SAFE_CHOICES, false, true);
      renderChoices(document.getElementById("dr-willing"), rows, WILLING, WILLING_CHOICES, false, true);
      renderChoices(document.getElementById("dr-child"), rows, CHILD, CHILD_CHOICES, true, false);
      renderText(document.getElementById("dr-text"), rows);
      document.getElementById("dr-status").hidden = true;
      document.getElementById("dr-body").hidden = false;
    }

    fetch(DATA_URL)
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.text();
      })
      .then(function (text) {
        var rows = parseCSV(text);
        rows.shift();
        rows = rows.filter(function (r) {
          return r.some(function (c) {
            return (c || "").trim() !== "";
          });
        });
        if (!rows.length) {
          document.getElementById("dr-status").textContent = "No responses yet.";
          return;
        }
        render(rows);
      })
      .catch(function (e) {
        document.getElementById("dr-status").textContent = "Couldn't load the responses right now. (" + e.message + ")";
      });
  })();
</script>
