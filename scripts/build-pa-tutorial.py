#!/usr/bin/env python3
"""Build PA-tutorial-v1.html: the Performance Analyst walkthrough for SEDM, an
imaginary subsidiary with 24 fictional influencers, safe to send company-wide.

    python3 scripts/build-pa-tutorial.py            # write PA-tutorial-v1.html
    python3 scripts/build-pa-tutorial.py --stats    # print the generated figures only

It starts from PA-demo-v4.html (already patched by pa-fixups.py) and swaps in:
  - a generated dataset (same record shape as the export's), seeded so every
    build gives the same numbers, shaped so each section has something to show;
  - the fictional avatars and post thumbnails from resources/pa-tutorial/
    (web-sized copies of resources/pa-tutorial-assets/, made here on first run);
  - Brief Summary wording computed from that data.
It also removes what must not travel with a company-wide file: the real
influencers' records and photos, the second embedded dataset, the chat script.
"""
import hashlib
import html
import json
import random
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / 'PA-demo-v4.html', ROOT / 'PA-tutorial-v1.html'
RAW, WEB = ROOT / 'resources/pa-tutorial-assets', ROOT / 'resources/pa-tutorial'
ID = r'[\w$]+'
SUB, REGION, YEAR, MONTHS = 'SEDM', 'NA', 2026, 8
MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']
PP_ORDER = ['Photography & Film', 'Gaming', 'Health & Fitness', 'Music & Entertainment', 'Food & Travel', 'Fashion & Beauty', 'Others']

# id, name, passion point, tier, archetype, followers, posts, base E/R %, latest-month E/R multiplier
ROSTER = [
    (1, 'Mira Solenne', 'Photography & Film', 'Icon', 'Sage', 10_000_000, 30, 0.35, 0.6),
    (2, 'Dax Okonkwo-Reyes', 'Music & Entertainment', 'Icon', 'Firestarter', 9_000_000, 20, 1.9, 2.8),
    (3, 'Ilse Varga', 'Health & Fitness', 'Hero', 'Visionary', 4_200_000, 28, 2.4, 1.5),
    (4, 'Teo Marchetti-Lin', 'Food & Travel', 'Hero', 'Sage', 2_600_000, 26, 0.7, 0.6),
    (5, 'Sunniva Aalto', 'Fashion & Beauty', 'Hero', 'Mirror', 3_600_000, 24, 1.5, 1.4),
    (6, 'Kenji Abara', 'Gaming', 'Hero', 'Firestarter', 1_800_000, 30, 2.9, 1.3),
    (7, 'Odalys Ferreira', 'Photography & Film', 'Hero', 'Visionary', 2_200_000, 18, 0.9, 1.0),
    (8, 'Bram Vandersteen', 'Photography & Film', 'Macro', 'Sage', 980_000, 20, 1.4, 0.15),
    (9, 'Naledi Mokoena', 'Photography & Film', 'Macro', 'Mirror', 450_000, 16, 2.6, 1.6),
    (10, 'Rafi Calloway', 'Photography & Film', 'Micro', 'Firestarter', 90_000, 22, 4.5, 1.0),
    (11, 'Leocadia Brandt', 'Music & Entertainment', 'Hero', 'Mirror', 3_000_000, 15, 1.2, 0.7),
    (12, 'Jun-ho Savary', 'Music & Entertainment', 'Macro', 'Firestarter', 800_000, 24, 3.2, 1.5),
    (13, 'Paloma Idris', 'Music & Entertainment', 'Macro', 'Visionary', 520_000, 14, 2.0, 1.0),
    (14, 'Viggo Halloran', 'Health & Fitness', 'Macro', 'Sage', 960_000, 18, 1.1, 0.2),
    (15, 'Amara Delacroix', 'Health & Fitness', 'Macro', 'Mirror', 380_000, 20, 3.6, 1.3),
    (16, 'Tobias Nkemelu', 'Health & Fitness', 'Micro', 'Sage', 110_000, 25, 5.2, 1.0),
    (17, 'Élodie Wren', 'Fashion & Beauty', 'Macro', 'Visionary', 640_000, 16, 2.8, 1.0),
    (18, 'Cassian Oyelaran', 'Fashion & Beauty', 'Micro', 'Mirror', 75_000, 18, 3.9, 0.8),
    (19, 'Ingrid Tamsin', 'Food & Travel', 'Macro', 'Visionary', 420_000, 15, 1.8, 1.0),
    (20, 'Beto Quillfeather', 'Food & Travel', 'Micro', 'Firestarter', 60_000, 20, 6.0, 1.2),
    (21, 'Yara Lindqvist', 'Gaming', 'Macro', 'Mirror', 900_000, 22, 0.8, 0.9),
    (22, 'Maddox Thibodeau', 'Gaming', 'Micro', 'Sage', 45_000, 14, 2.2, 1.0),
    (23, 'Hollis Penhaligon', 'Others', 'Macro', 'Sage', 330_000, 12, 1.6, 1.0),
    (24, 'Zuri Adeyemi-Clarke', 'Others', 'Micro', 'Mirror', 100_000, 16, 3.0, 1.0),
]
CHANNELS = [('Instagram', 'ig', 0.45), ('TikTok', 'tiktok', 0.35), ('YouTube', 'yt', 0.12), ('Facebook', 'fb', 0.08)]


def walkthrough(st, target):
    """The guided analysis, in order. Figures come from the generated data."""
    month = MONTH_NAMES[MONTHS - 1]
    m = st['mom']
    pct = lambda v: f'{"+" if v >= 0 else "-"}{abs(round(v, 1)):g}%'
    drag = next(p for p in st['pps'] if p[2] == st['drag'])
    others = [p for p in st['pps'][:3] if p[2] != st['drag']]
    group = sorted((w for w in st['who'].values() if w['pp'] == st['drag']), key=lambda w: -w['reach'])
    top, rest, group_reach = group[0], group[1:], sum(w['reach'] for w in group)
    best = max((w for w in st['who'].values() if w['reach'] > top['reach'] * 0.4 and w['name'] != top['name']), key=lambda w: w['er'])
    neg, pos = st['impact'][:2], st['impact'][::-1][:1]
    alt = max(rest[:3], key=lambda w: w['er'])   # among the rows on screen: the list shows four, sorted by Po.Reach
    return [
        {'target': '.ai-brief-summary__highlight--primary', 'title': 'Start with the headline', 'body': [
            f'Brief Summary opens with the overall result: {month} came in at {st["latest"]:.2f}% E/R and lifted {SUB}\'s cumulative E/R to {st["ytd"]:.2f}%.',
            'That reads like good news. But a summary is a claim, so the first thing to do is check it against the numbers in Executive Summary.']},
        {'target': '.spa-executive-metrics', 'title': 'Check the latest month', 'body': [
            f'These five cards show {month} only, each with its change from the month before (MoM).',
            f'E/R is {st["latest"]:.2f}%, {m["er"]:+.3f}%p on {MONTH_NAMES[MONTHS - 2]}. Look at why: Engagement grew {pct(m["eng"])} while Po.Reach grew only {pct(m["reach"])}. '
            'When engagement rises faster than reach, E/R goes up. So the headline holds for the month.']},
        {'target': '.spa-trend-panel', 'title': 'Then check the year so far', 'body': [
            f'One good month matters only if it moves the year. The blue line is cumulative E/R from January; it slid to {st["prior"]:.2f}% by {MONTH_NAMES[MONTHS - 2]} (Prior Cumulative) '
            f'and {month} pulled it back up to {st["ytd"]:.2f}% (Current YTD).',
            f'The red dashed line is the {target}% target. {SUB} is closer than it was, but still under it, which is why the second point in Brief Summary matters.']},
        # The diagnosis: which passion point is pulling E/R down.
        {'target': '.ai-brief-summary__highlight--secondary', 'advanceOn': '.spa-rule__cta', 'title': 'Now the diagnosis', 'body': [
            f'The second point names what is holding E/R back: {drag[2]} takes {drag[0]:.1f}% of Po.Reach, yet has the lowest E/R of the three biggest passion points.',
            'Check this one too. Click "Review Passion Point contribution →", or press Next and the walkthrough will open it for you.']},
        {'target': '.spa-portfolio .spa-selected-row', 'fallback': '.spa-portfolio-grid', 'enter': 'selectDrag', 'title': f'Read the {drag[2]} row', 'body': [
            f'The link selected {drag[2]} in Portfolio Overview. Compare its two bars.',
            f'It takes {drag[0]:.1f}% of all Po.Reach (blue bar) but returns only {drag[3]:.1f}% of all engagement (navy bar), for an E/R of {drag[1]:.2f}%. '
            'A group whose reach share is bigger than its engagement share is pulling E/R down.']},
        {'target': '.spa-portfolio-grid', 'title': 'Compare the other passion points', 'body': [
            ' '.join(f'{pp} is the opposite: {share:.1f}% of reach returns {eng:.1f}% of engagement, at {er:.2f}% E/R.' if n == 0 else
                     f'So is {pp}: {share:.1f}% of reach, {eng:.1f}% of engagement, {er:.2f}% E/R.' for n, (share, er, pp, eng) in enumerate(others)),
            f'So the drag is one passion point, not the whole portfolio. Without {drag[2]}, {SUB}\'s E/R would be {st["without_drag"]:.2f}% instead of {st["ytd"]:.2f}%'
            + (f', above the {target}% target.' if st['without_drag'] >= target else '.'),
            f'That settles which passion point. The next question is who inside {drag[2]} is behind it.']},
        # Finding the person.
        {'target': '.spa-long-list', 'enter': 'showList', 'title': 'Who is inside it?', 'body': [
            f'Selecting the passion point also filtered the Long-list. Its title now reads "Influencer Long-list ({drag[2]})" and it holds only that group\'s {len(group)} Influencers. '
            'Influencer Deep Dive is folded away for a moment so the list is in view.',
            f'Read the Po.Reach and E/R columns together. {top["name"]} alone carries {top["reach"] / group_reach * 100:.0f}% of the group\'s Po.Reach, at {top["er"]:.2f}% E/R. '
            f'The other {len(group) - 1} run from {min(g["er"] for g in rest):.2f}% to {max(g["er"] for g in rest):.2f}%.',
            'So the problem is not the passion point as a whole. It is one very large account inside it.']},
        {'target': '.spa-map-section', 'enter': 'showMap', 'mark': top['name'], 'title': 'See the same person on the map', 'body': [
            'Here every Influencer is a dot. Further right means more Po.Reach; higher up means a better E/R. The two grey lines are the medians, which split the map into four quadrants.',
            f'{top["name"]} is the circled dot: furthest to the right and at the very bottom, alone in the "Low E/R · High Po.Reach" corner. That corner weighs most on your result, because a weak E/R is multiplied by a big audience.',
            f'Compare {best["name"]}, top right: a similar-sized audience, at {best["er"]:.2f}% E/R.']},
        {'target': '.spa-deep-details', 'enter': 'showChange', 'title': 'Measure the damage', 'body': [
            f'Performance Change answers a sharper question: who moved {SUB}\'s cumulative E/R in the latest month, and by how much?',
            f'{neg[0][1]} tops Negative E/R Impact at {neg[0][0]:+.3f}%p, about {neg[0][0] / neg[1][0]:.0f} times the next name ({neg[1][1]}, {neg[1][0]:+.3f}%p). '
            f'It means their {month} posts alone lowered the whole subsidiary\'s cumulative E/R by {abs(neg[0][0]):.2f} points.',
            f'The other column shows it works both ways: {pos[0][1]} added {pos[0][0]:+.3f}%p.']},
        {'target': '.fx-mx ~ .fixed.inset-0 > div, .fixed.inset-0 > div', 'enter': 'showProfile', 'leave': 'closeProfile', 'plain': True, 'profile': top['name'],
         'title': 'Open their profile', 'body': [
            f'Clicking a name opens that Influencer\'s profile. The cards confirm the pattern for one person: {top["posts"]} posts, {top["reach_share"]:.1f}% of all Po.Reach, '
            f'but only {top["eng_share"]:.1f}% of all engagement, at {top["er"]:.2f}% E/R.',
            'Content Gallery below shows their tracked posts, and on the real page "Go to post" opens the original. This is where you look for the reason: the format, the topic, how the product appears.',
            'The numbers told you where to look. The posts tell you why.']},
        # The resolution, and what is coming to help with it.
        {'target': '.spa-long-list', 'enter': 'showList', 'title': 'Reach a resolution', 'body': [
            f"An analysis ends with a decision. Back in the Long-list, the evidence points to {top['name']}: {top['posts']} posts, {top['reach_share']:.1f}% of all Po.Reach, {top['er']:.2f}% E/R. There are two ways to resolve it.",
            "Keep them and fix the content. An audience this large is hard to replace. If the posts are the weak point, a sharper brief could lift E/R without giving up the reach.",
            f"Or phase them out and find Influencers similar to {alt['name']}, who runs at {alt['er']:.2f}% E/R in the same passion point. This audience does engage with the right creator.",
            "Which one is right is your call. It depends on things this page cannot see: the contract, the relationship, the campaign plan."]},
        {'title': 'Two more agents are on the way', 'body': [
            "Both resolutions are about to get easier. Two more agents are in development for Influencer Master Agent.",
            "Brief Curator will help creators make better-performing content, for when you decide to keep someone and fix the posts. Influencer Recruiter will help you find stronger candidates, for when you decide to replace them.",
            "Until then, the routine is the one you just followed: read the headline, check it, find the passion point, find the person, look at the posts, decide. Every name here was imaginary, but your own subsidiary's page reads the same way."]},
    ]


# Shown on every load, in two steps: first that nothing on the page is real, then
# the choice between the guided walkthrough and reading the tutorial notes alone.
# {{RULE_TITLE}} / {{RULE_EVIDENCE}} are the summary point the walkthrough starts from;
# {{STEPS}} is the walkthrough itself (see walkthrough()).
NOTICE = '''<style>
.fx-notice { position: fixed; inset: 0; margin: auto; height: fit-content; width: calc(100% - 48px); max-width: 520px; padding: 32px; border: 0; border-radius: 8px; background: #fff; color: #263144;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); font: 400 16px/1.5 "Samsung SS Body", -apple-system, "Segoe UI", sans-serif; }
.fx-notice::backdrop { background: rgba(0, 0, 0, 0.5); }
.fx-notice h2 { margin: 0 0 12px; font: 700 24px/1.4 "Samsung SS Head", -apple-system, "Segoe UI", sans-serif; }
.fx-notice p { margin: 0 0 12px; }
.fx-notice blockquote { margin: 0 0 12px; padding: 12px 16px; border: 1px solid #d7e5f7; border-radius: 4px; background: #f6f9ff; }
.fx-notice blockquote strong { display: block; margin-bottom: 4px; color: #0380fe; font-weight: 700; }
.fx-notice button { display: block; width: 100%; height: 48px; margin-top: 12px; border: 0; border-radius: 8px; background: #263144;
  color: #fff; font: 500 18px/1 "Samsung SS Body", -apple-system, "Segoe UI", sans-serif; cursor: pointer; }
.fx-notice p + button, .fx-notice blockquote + button { margin-top: 24px; }
.fx-notice button.is-secondary { border: 1px solid #cecece; background: #fff; color: #263144; }
.fx-notice button:focus-visible { outline: 2px solid #0380fe; outline-offset: 2px; }
.fx-walking .fx-walk-start { display: none; }
/* Guided walkthrough: a spotlight on the current target and a card beside it. */
.fx-walk-spot { position: fixed; z-index: 10000; border-radius: 8px; box-shadow: 0 0 0 3px #0380fe, 0 0 0 9999px rgba(0, 0, 0, 0.5); pointer-events: none; }
.fx-walk-card { position: fixed; z-index: 10002; box-sizing: border-box; width: min(380px, calc(100vw - 32px)); padding: 20px; border-radius: 8px; background: #fff; color: #263144;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25); font: 400 15px/1.5 "Samsung SS Body", -apple-system, "Segoe UI", sans-serif; transition: opacity 0.18s; }
.fx-walk-card.is-hidden { opacity: 0; pointer-events: none; }
/* Over something that already dims the page (the profile popup): the ring only. */
.fx-walk-spot.is-none { box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5); }
.fx-walk-spot.is-plain { box-shadow: 0 0 0 3px #0380fe; }
/* A second, smaller pointer inside the spotlight (one dot on the map). */
.fx-walk-mark { position: fixed; z-index: 10001; width: 34px; height: 34px; margin: -17px 0 0 -17px; border: 3px solid #0380fe; border-radius: 50%; pointer-events: none; animation: fx-walk-pulse 1.4s ease-out infinite; }
@keyframes fx-walk-pulse { from { box-shadow: 0 0 0 0 rgba(3, 128, 254, 0.5); } to { box-shadow: 0 0 0 14px rgba(3, 128, 254, 0); } }
@media (prefers-reduced-motion: reduce) { .fx-walk-mark { animation: none; } }
.fx-walk-card small { display: block; margin-bottom: 4px; color: #0380fe; font-size: 12px; font-weight: 700; }
.fx-walk-card h3 { margin: 0 0 8px; font: 700 20px/1.3 "Samsung SS Head", -apple-system, "Segoe UI", sans-serif; }
.fx-walk-card p { margin: 0 0 8px; }
.fx-walk-card footer { display: flex; align-items: center; gap: 8px; margin-top: 16px; }
.fx-walk-card button { height: 36px; padding: 0 14px; border: 1px solid #cecece; border-radius: 8px; background: #fff; color: #263144; font: 500 15px/1 "Samsung SS Body", -apple-system, "Segoe UI", sans-serif; cursor: pointer; }
.fx-walk-card button[data-walk="exit"] { margin-right: auto; padding: 0; border: 0; color: #777f8c; text-decoration: underline; }
.fx-walk-card button[data-walk="next"] { border-color: #263144; background: #263144; color: #fff; }
.fx-walk-card button:disabled { opacity: 0.4; cursor: default; }
.fx-walk-card button:focus-visible { outline: 2px solid #0380fe; outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { .fx-walk-card { transition: none; } }
</style>
<dialog class="fx-notice" id="fx-notice">
  <section aria-labelledby="fx-notice-1">
    <h2 id="fx-notice-1">This is a tutorial</h2>
    <p>For this walkthrough, every Influencer and every post on this page has been replaced with imaginary placeholders.</p>
    <p>The names, photos, posts and figures are illustrative examples only. They do not represent real people or real performance.</p>
    <button type="button" data-next autofocus>Got it</button>
  </section>
  <section aria-labelledby="fx-notice-2" hidden>
    <h2 id="fx-notice-2">How would you like to learn?</h2>
    <p>The guided walkthrough takes you through one full analysis, step by step, starting from the first point in Brief Summary:</p>
    <blockquote><strong>{{RULE_TITLE}}</strong>{{RULE_EVIDENCE}}</blockquote>
    <p>Or close this and read the tutorial notes on each section at your own pace.</p>
    <button type="button" data-guided>Start the guided walkthrough</button>
    <button type="button" data-own class="is-secondary">Explore on my own</button>
  </section>
</dialog>
<script>
(function () {
  var d = document.getElementById('fx-notice'), steps = d.querySelectorAll('section');
  function choose() { steps[0].hidden = true; steps[1].hidden = false; d.querySelector('[data-guided]').focus(); }
  // On your own: the per-section tutorial notes are switched on.
  function alone() {
    d.close();
    var t = document.querySelector('.fx-tut-toggle:not(.fx-walk-start)');
    if (t && t.getAttribute('aria-pressed') !== 'true') t.click();
  }
  function guided() { d.close(); walk.start(); }

  // ---------- Guided walkthrough ----------
  // One step = a target on the page (CSS selector), a title and paragraphs.
  var STEPS = {{STEPS}};
  var walk = (function () {
    var at = -1, spot, card, mark, side, last, still, since, frame, scrolled;
    // The first match that is actually on screen (the map is mounted twice; one copy is hidden).
    function seen(sel) { return Array.prototype.filter.call(document.querySelectorAll(sel), function (e) { return e.getClientRects().length; })[0]; }
    function target() { var s = STEPS[at]; return s.target && seen(s.target) || (s.fallback && seen(s.fallback)); }
    function details(open) { Array.prototype.forEach.call(document.querySelectorAll('.spa-deep-details'), function (d, i) { d.open = open === 'all' || i < open; }); }
    function named(sel, name) { return Array.prototype.filter.call(document.querySelectorAll(sel), function (e) { return e.textContent === name; })[0]; }
    function profile() { return document.querySelector('.fixed.inset-0'); }
    // Things a step does to the page when it opens, so the walkthrough never depends on the reader having clicked.
    var ENTER = {
      // Portfolio Overview on Passion Point, with the passion point from Brief Summary selected.
      selectDrag: function () {
        var axis = document.querySelector('.spa-portfolio .mx-form-switchbox label');
        if (axis) axis.click();
        var cta = document.querySelector('.spa-rule__cta');
        if (cta && !document.querySelector('.spa-portfolio .spa-selected-row')) cta.click();
      },
      // The filtered Long-list, with Deep Dive folded so the list is on screen.
      showList: function () { ENTER.selectDrag(); details(0); },
      // The map on its Influencer view.
      showMap: function () { var m = seen('.spa-map-section'), axis = m && m.querySelector('.mx-form-switchbox label'); if (axis) axis.click(); },
      // Performance Change open, Performance Contributors folded.
      showChange: function () { details(1); },
      // The profile popup of the step's influencer, opened from their name in Performance Change.
      showProfile: function (s) { details(1); if (!profile()) { var b = named('.spa-compare__name', s.profile); if (b) b.click(); } },
      closeProfile: function () { var p = profile(); if (p) p.click(); }
    };
    // Which side of the target the card sits on. Chosen once per step, when the page has stopped
    // scrolling, so the card never hops between sides while the target moves through the window.
    function pick(r, w, h) {
      var pad = 8, gap = 16, vw = innerWidth, vh = innerHeight;
      if (r.right + pad + gap + w <= vw - 16) return 'right';
      if (r.left - pad - gap - w >= 16) return 'left';
      if (r.bottom + pad + gap + h <= vh - 16) return 'below';
      if (r.top - pad - gap - h >= 16) return 'above';
      return 'corner';
    }
    function put(r) {
      var pad = 8, gap = 16, vw = innerWidth, vh = innerHeight, w = card.offsetWidth, h = card.offsetHeight;
      var cy = function (y) { return Math.max(16, Math.min(y, vh - h - 16)); }, cx = function (x) { return Math.max(16, Math.min(x, vw - w - 16)); };
      var x = side === 'right' ? r.right + pad + gap : side === 'left' ? r.left - pad - gap - w : side === 'corner' ? vw - w - 16 : cx(r.left - pad);
      var y = side === 'below' ? r.bottom + pad + gap : side === 'above' ? r.top - pad - gap - h : side === 'corner' ? vh - h - 16 : cy(r.top - pad);
      card.style.left = x + 'px'; card.style.top = y + 'px';
    }
    // Every frame: the spotlight sits exactly on the target (no easing of its own, so it rides the
    // page's scroll instead of chasing it). The card appears once the target has stopped moving.
    function tick(now) {
      frame = requestAnimationFrame(tick);
      if (at >= 0 && !STEPS[at].target) {      // a closing card with nothing to point at: centred
        spot.style.cssText = 'top:50%;left:50%;width:0;height:0';
        card.style.left = (innerWidth - card.offsetWidth) / 2 + 'px'; card.style.top = Math.max(16, (innerHeight - card.offsetHeight) / 2) + 'px';
        if (!side) { side = 'center'; card.classList.remove('is-hidden'); card.querySelector('[data-walk="next"]').focus({ preventScroll: true }); }
        return;
      }
      var el = at >= 0 && target();
      if (!el) return;
      if (!scrolled) {      // once the target exists (a step may have just made the page render it)
        scrolled = true; since = now;
        el.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: el.getBoundingClientRect().height > innerHeight * 0.7 ? 'start' : 'center' });
      }
      var r = el.getBoundingClientRect(), pad = 8, key = [r.top, r.left, r.width, r.height, innerWidth, innerHeight].join();
      if (key !== last) {
        last = key; still = 0;
        spot.style.cssText = 'top:' + (r.top - pad) + 'px;left:' + (r.left - pad) + 'px;width:' + (r.width + 2 * pad) + 'px;height:' + (r.height + 2 * pad) + 'px';
        if (side) put(r);
      } else still += 1;
      var dot = STEPS[at].mark && named('.spa-map-section text', STEPS[at].mark);
      if (dot && dot.getClientRects().length) {
        var c = dot.previousElementSibling.getBoundingClientRect();
        mark.hidden = false; mark.style.left = c.left + c.width / 2 + 'px'; mark.style.top = c.top + c.height / 2 + 'px';
      }
      if (!side && (still >= 6 || now - since > 1200)) {
        side = pick(r, card.offsetWidth, card.offsetHeight);
        put(r);
        card.classList.remove('is-hidden');
        card.querySelector('[data-walk="next"]').focus({ preventScroll: true });
      }
    }
    function show(i) {
      at = i; side = null; last = null; still = 0; since = performance.now(); scrolled = false;
      card.classList.add('is-hidden');
      var s = STEPS[i];
      card.innerHTML = '<small>Step ' + (i + 1) + ' of ' + STEPS.length + '</small><h3></h3><div></div><footer>' +
        '<button type="button" data-walk="exit">Exit walkthrough</button><button type="button" data-walk="back">Back</button>' +
        '<button type="button" data-walk="next">' + (i === STEPS.length - 1 ? 'Finish' : 'Next') + '</button></footer>';
      card.querySelector('h3').textContent = s.title;
      s.body.forEach(function (t) { var p = document.createElement('p'); p.textContent = t; card.querySelector('div').appendChild(p); });
      card.querySelector('[data-walk="back"]').disabled = i === 0;
      spot.classList.toggle('is-plain', !!s.plain); spot.classList.toggle('is-none', !s.target);
      mark.hidden = true;
      if (s.enter) ENTER[s.enter](s);
    }
    // A step can name something on the page to click; doing so moves on, the same as Next.
    function clicked(e) {
      var s = at >= 0 && STEPS[at];
      if (s && s.advanceOn && e.target.closest && e.target.closest(s.advanceOn)) setTimeout(function () { step(1); }, 0);
    }
    function stop() {
      leave(); details('all');
      at = -1;
      document.documentElement.classList.remove('fx-walking');
      cancelAnimationFrame(frame);
      spot.remove(); card.remove(); mark.remove();
      document.removeEventListener('keydown', keys); document.removeEventListener('click', clicked, true);
    }
    function leave() { var s = at >= 0 && STEPS[at]; if (s && s.leave) ENTER[s.leave](s); }
    function step(n) { var i = at + n; if (i >= STEPS.length) stop(); else if (i >= 0) { leave(); show(i); } }
    function keys(e) { if (e.key === 'Escape') stop(); else if (e.key === 'ArrowRight') step(1); else if (e.key === 'ArrowLeft') step(-1); }
    function start() {
      if (at >= 0) return;
      document.documentElement.classList.add('fx-walking');
      spot = document.createElement('div'); spot.className = 'fx-walk-spot';
      card = document.createElement('div'); card.className = 'fx-walk-card'; card.setAttribute('role', 'dialog'); card.setAttribute('aria-label', 'Guided walkthrough');
      card.addEventListener('click', function (e) {
        var b = e.target.closest('[data-walk]');
        if (b) { var a = b.getAttribute('data-walk'); if (a === 'exit') stop(); else step(a === 'next' ? 1 : -1); }
      });
      mark = document.createElement('div'); mark.className = 'fx-walk-mark'; mark.hidden = true;
      document.body.appendChild(spot); document.body.appendChild(card); document.body.appendChild(mark);
      document.addEventListener('keydown', keys); document.addEventListener('click', clicked, true);
      show(0);
      frame = requestAnimationFrame(tick);
    }
    return { start: start, stop: stop };
  })();
  window.fxWalkthrough = walk;
  d.querySelector('[data-next]').addEventListener('click', choose);
  d.querySelector('[data-own]').addEventListener('click', alone);
  d.querySelector('[data-guided]').addEventListener('click', guided);
  // Esc never skips the notice: on the first step it moves on, on the second it means "on my own".
  d.addEventListener('cancel', function (e) { e.preventDefault(); if (steps[1].hidden) choose(); else alone(); });
  d.showModal();
})();
</script>
'''


def slug_of(i):
    """The asset folder name for roster id i (e.g. 17-elodie-wren)."""
    return next(p.name for p in sorted((RAW / 'thumbnails').iterdir()) if p.name.startswith(f'{i:02d}-'))


def web_assets():
    """Web-sized JPEG copies of the delivered PNGs: avatars 256px, thumbnails 640px on the long side."""
    for src in sorted(RAW.rglob('*.png')):
        dst = (WEB / src.relative_to(RAW)).with_suffix('.jpg')
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        size = '256' if src.parent.name == 'avatars' else '640'
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '80', '-Z', size, str(src), '--out', str(dst)],
                       check=True, stdout=subprocess.DEVNULL)


def post_url(code, handle, i, n):
    # Not real posts: ids that the platforms cannot have issued, under handles that cannot exist.
    return {
        'ig': f'https://www.instagram.com/p/sedm{i:02d}{n:03d}/',
        'tiktok': f'https://www.tiktok.com/@{handle}/video/90000000000{i:02d}{n:03d}',
        'yt': f'https://www.youtube.com/watch?v=sedm{i:02d}{n:03d}',      # 9 characters, so never read as a YouTube id
        'fb': f'https://www.facebook.com/{handle}/posts/9000000{i:02d}{n:03d}',
    }[code]


def generate():
    rng = random.Random(20261123)
    records, thumbs = [], {}
    for i, name, pp, tier, archetype, followers, posts, er, latest in ROSTER:
        slug = slug_of(i)
        handle = 'sedm.demo.' + slug[3:]
        files = sorted(p.stem for p in (RAW / 'thumbnails' / slug).iterdir())
        need = defaultdict(int)
        for f in files:
            need[f.rsplit('-', 1)[1]] += 1
        # Channel per post: at least as many of each as there are thumbnails for it.
        chans = [c for c, n in need.items() for _ in range(n)]
        chans += rng.choices([c[1] for c in CHANNELS], weights=[c[2] for c in CHANNELS], k=posts - len(chans))
        months = sorted(rng.choices(range(MONTHS), weights=[1] * (MONTHS - 1) + [1.1], k=posts))
        rng.shuffle(chans)
        mine = []
        for n, (m, code) in enumerate(zip(months, chans), 1):
            reach = round(followers * rng.uniform(0.9, 1.12) * (1 + 0.02 * m))
            rate = er / 100 * (latest if m == MONTHS - 1 else 1) * rng.lognormvariate(0, 0.35)
            day = rng.randint(1, [31, 28, 31, 30, 31, 30, 31, 30][m])
            mine.append({
                'uid': hashlib.md5(slug.encode()).hexdigest(), 'name': name, 'sub': SUB, 'region': REGION, 'strategic': True,
                'tier': tier, 'channel': next(c[0] for c in CHANNELS if c[1] == code), 'pp': pp, 'archetype': archetype,
                'arise': 'newly', 'histAbove': None,
                'profiles': {'Instagram': f'https://www.instagram.com/{handle}', 'TikTok': f'https://www.tiktok.com/@{handle}',
                             'YouTube': f'https://www.youtube.com/@{handle}'},
                'reach': reach, 'eng': max(1, round(reach * rate)), 'postUrl': post_url(code, handle, i, n),
                'date': datetime(YEAR, m + 1, day, rng.randint(8, 22), rng.randint(0, 59), rng.randint(0, 59)).strftime('%Y-%m-%dT%H:%M:%S.000'),
                '_code': code,
            })
        # Thumbnails go to the most recent posts on their channel.
        for f in files:
            code = f.rsplit('-', 1)[1]
            post = next(p for p in sorted(mine, key=lambda p: p['date'], reverse=True) if p['_code'] == code and '_thumb' not in p)
            post['_thumb'] = True
            key = re.sub(r'^https?://', '', post['postUrl']).rstrip('/').lower()
            thumbs[key] = f'resources/pa-tutorial/thumbnails/{slug}/{f}.jpg'
        records += mine
    latest_day = max(r['date'] for r in records)
    if not latest_day.startswith(f'{YEAR}-{MONTHS:02d}-31'):      # "Data through" reads the last post date
        last = max(records, key=lambda r: r['date'])
        last['date'] = f'{YEAR}-{MONTHS:02d}-31T18:42:10.000'
    for r in records:
        r.pop('_code'), r.pop('_thumb', None)
    records.sort(key=lambda r: r['date'])
    return records, thumbs


def stats(records):
    er = lambda rows: 100 * sum(r['eng'] for r in rows) / max(1, sum(r['reach'] for r in rows))
    month = lambda r: int(r['date'][5:7])
    latest = [r for r in records if month(r) == MONTHS]
    prior = [r for r in records if month(r) < MONTHS]
    total = sum(r['reach'] for r in records)
    by_pp = defaultdict(list)
    for r in records:
        by_pp[r['pp']].append(r)
    total_eng = sum(r['eng'] for r in records)
    pps = sorted(((sum(r['reach'] for r in rows) / total * 100, er(rows), pp, sum(r['eng'] for r in rows) / total_eng * 100)
                  for pp, rows in by_pp.items()), reverse=True)
    drag = sorted(pps[:3], key=lambda p: p[1])[0][2]
    impact = []
    for uid in {r['uid'] for r in latest}:
        mine = [r for r in latest if r['uid'] == uid]
        rest = [r for r in records if not (r['uid'] == uid and month(r) == MONTHS)]
        impact.append((er(records) - er(rest), mine[0]['name']))
    before = [r for r in records if month(r) == MONTHS - 1]
    total_of = lambda rows, k: sum(r[k] for r in rows)
    mom = {'er': er(latest) - er(before), 'reach': (total_of(latest, 'reach') / total_of(before, 'reach') - 1) * 100,
           'eng': (total_of(latest, 'eng') / total_of(before, 'eng') - 1) * 100}
    people = defaultdict(list)
    for r in records:
        people[r['name']].append(r)
    who = {name: {'name': name, 'pp': rows[0]['pp'], 'posts': len(rows), 'reach': total_of(rows, 'reach'), 'er': er(rows),
                  'reach_share': total_of(rows, 'reach') / total * 100, 'eng_share': total_of(rows, 'eng') / total_eng * 100}
           for name, rows in people.items()}
    return {'latest': er(latest), 'prior': er(prior), 'ytd': er(records), 'pps': pps, 'impact': sorted(impact), 'mom': mom, 'who': who,
            'drag': drag, 'without_drag': er([r for r in records if r['pp'] != drag]),
            'monthly': [er([r for r in records if month(r) <= m]) for m in range(1, MONTHS + 1)],
            'posts': len(records), 'reach': total}


def one(pattern, s, what, flags=0):
    found = list(re.finditer(pattern, s, flags))
    if len(found) != 1:
        raise SystemExit(f'{what}: expected 1 match, found {len(found)}')
    return found[0]


def js_string(obj):
    """obj as the body of a single-quoted JS string holding JSON."""
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('\\', '\\\\').replace("'", "\\'")


def build(records, thumbs, st):
    s = SRC.read_text(encoding='utf-8')

    def sub(pattern, new, what, flags=0):
        nonlocal s
        m = one(pattern, s, what, flags)
        s = s[:m.start()] + (new(m) if callable(new) else new) + s[m.end():]

    # Data: the analysis dataset becomes SEDM's; the other embedded dataset is emptied.
    sets = list(re.finditer(r"=JSON\.parse\('(\{\"period\":.*?\"dropped\":\{[^}]*\}\})'\)", s, re.S))
    if len(sets) != 2:
        raise SystemExit(f'datasets: expected 2, found {len(sets)}')
    head = {'period': f'{YEAR}-01 ~ {YEAR}-{MONTHS:02d}', 'baseYear': str(YEAR)}
    tail = {'dropped': {'tier': 0, 'channel': 0, 'passionPoint': 0}}
    for m, rows in reversed(list(zip(sets, (records, [])))):
        s = s[:m.start(1)] + js_string({**head, 'records': rows, **tail}) + s[m.end(1):]

    # SEDM in the subsidiary tables: E/R target, region, selector label, and the demo-mode default.
    target = round(st['ytd'] * 1.06, 1)
    sub(r'=\{HQ:2\.7,SEA:1\.2,', lambda m: m.group(0) + f'{SUB}:{target},', 'E/R targets')
    sub(r'=\{HQ:"SUWON",', lambda m: m.group(0) + f'{SUB}:"{REGION}",', 'region table')
    sub(r'=\{KOREA:"Korea",SEA:"SEA",', lambda m: m.group(0) + f'{SUB}:"{SUB}",', 'selector labels')
    sub(r'codes:\["SEA"\]', f'codes:["{SUB}"]', 'demo scope')
    sub(r'lockedCode:(' + ID + r')\?"SEA"', lambda m: f'lockedCode:{m.group(1)}?"{SUB}"', 'locked scope')

    # Avatars: name -> file. The real people's embedded photos are blanked.
    faces = one(r'(' + ID + r')=\{("[^"{}]+":' + ID + r',?)+\};function ' + ID + r'\(' + ID + r'\)\{const ' + ID + r'=\1\[', s, 'avatar table')
    for var in set(re.findall(r'":(' + ID + r')[,}]', faces.group(0))):
        sub(r'(?<![\w$])' + re.escape(var) + r'="data:image/[a-z]+;base64,[A-Za-z0-9+/=]+"', f'{var}=""', f'avatar {var}')
    table = {name: f'resources/pa-tutorial/avatars/{slug_of(i)}.jpg' for i, name, *_ in ROSTER}
    faces = one(r'(' + ID + r')=\{("[^"{}]+":' + ID + r',?)+\}(?=;function ' + ID + r'\(' + ID + r'\)\{const ' + ID + r'=\1\[)', s, 'avatar table')
    s = s[:faces.start()] + faces.group(1) + '=' + json.dumps(table, ensure_ascii=False, separators=(',', ':')) + s[faces.end():]

    # Post thumbnails.
    sub(r'const MX_THUMB_OVERRIDES=\{.*?\};', 'const MX_THUMB_OVERRIDES=' + json.dumps(thumbs, separators=(',', ':')) + ';', 'thumbnail table', re.S)

    # Brief Summary wording, from the generated figures (MX MAP's sentence patterns).
    up = st['latest'] >= st['prior']
    month = MONTH_NAMES[MONTHS - 1]
    main = next(p for p in st['pps'] if p[2] == st['drag'])
    rules = [
        (f'{month} performance {"enhanced" if up else "diluted"} overall E/R Performance',
         f'{SUB} delivered E/R {st["latest"]:.2f}% for {month} which {"pushed E/R up" if up else "pulled E/R down"} to {st["ytd"]:.2f}% (MoM x{st["ytd"] / st["prior"]:.1f}).'),
        (f'{main[2]} is hindering E/R growth',
         f'{main[2]} accounted for {main[0]:.1f}% of Po.Reach but recorded the lowest E/R among the 3 main PPs.'),
    ]
    for rule_id, (title, evidence) in zip(('L-01', 'L-02'), rules):
        sub(r'(id:"' + rule_id + r'",tone:"\w+",title:)"[^"]*",evidence:"[^"]*"',
            lambda m: m.group(1) + json.dumps(title) + ',evidence:' + json.dumps(evidence), f'rule {rule_id}')
    sub(r'\(\{axis:"ppoint",key:"Photography & Film"\}\)', '({axis:"ppoint",key:' + json.dumps(main[2]) + '})', 'rule link')
    # The export pins the last cumulative E/R point for its demo; the tutorial shows what the data gives.
    sub(r'const (' + ID + r')=[\d.]+;if\(!(' + ID + r')\|\|\1==null\)', lambda m: f'const {m.group(1)}=null;if(!{m.group(2)}||{m.group(1)}==null)', 'pinned E/R')

    # The assistant's scripted chat names real people; it is not shown, and now not shipped.
    chat = one(r'=\[\{from:"agent",text:"Hi! Ask me anything about this dashboard', s, 'chat script')
    end = s.index('}];', chat.start()) if '}];' in s[chat.start():chat.start() + 20000] else s.index('}],', chat.start())
    s = s[:chat.start()] + '=[{from:"agent",text:""' + s[end:]

    # A way back into the walkthrough, beside the Tutorial toggle (hidden while it is running).
    sub(r'(' + ID + r')\.jsx\("button",\{type:"button",className:"fx-tut-toggle"',
        lambda m: m.group(1) + '.jsx("button",{type:"button",className:"fx-tut-toggle fx-walk-start",'
                  'onClick:()=>{window.fxWalkthrough&&window.fxWalkthrough.start()},children:"Guided walkthrough"}),' + m.group(0), 'walkthrough button')
    # The tutorial is the site's only page: its rail lists nothing else.
    sub(r'\[\["pa","Performance Analyst","PA-demo-v4\.html"\],\["recruiter".*?"Brief_Curator\.html#monitor"\]\]',
        '[["pa","Performance Analyst","PA-tutorial-v1.html"]]', 'rail pages')
    sub(r'<title>[^<]*</title>', '<title>Performance Analyst · Tutorial</title>', 'title')
    end = s.rindex('</body>')
    notice = (NOTICE.replace('{{RULE_TITLE}}', html.escape(rules[0][0])).replace('{{RULE_EVIDENCE}}', html.escape(rules[0][1]))
              .replace('{{STEPS}}', json.dumps(walkthrough(st, target), ensure_ascii=False).replace('</', '<\\/')))
    s = s[:end] + notice + s[end:]
    OUT.write_text(s, encoding='utf-8')
    return target


def main(argv):
    web_assets()
    records, thumbs = generate()
    st = stats(records)
    print(f'{len(records)} posts, {len({r["uid"] for r in records})} influencers, {len(thumbs)} thumbnails, Po.Reach {st["reach"] / 1e6:.0f}M')
    print('cumulative E/R by month:', ' '.join(f'{v:.2f}' for v in st['monthly']), f'| latest month {st["latest"]:.2f}  prior {st["prior"]:.2f}')
    for share, er, pp, _ in st['pps']:
        print(f'  {pp:24} reach {share:5.1f}%  E/R {er:.2f}%')
    print('negative:', ', '.join(f'{n} {v:+.3f}' for v, n in st['impact'][:6]))
    print('positive:', ', '.join(f'{n} {v:+.3f}' for v, n in st['impact'][::-1][:6]))
    if '--stats' in argv:
        return 0
    target = build(records, thumbs, st)
    print(f'{OUT.name}: written ({OUT.stat().st_size / 1e6:.1f} MB), E/R target {target}%')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
