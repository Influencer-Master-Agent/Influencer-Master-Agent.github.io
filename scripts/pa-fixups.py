#!/usr/bin/env python3
"""Re-apply the Influencer Master Agent fixups to Performance Analyst's exported build.

PA-demo-v4.html is a compiled single-file export of the mix-modeler-lab demo.
Every re-export replaces the bundle and drops edits made to the built file, so
the site-level fixes live here and are re-applied after each export:

    python3 scripts/pa-fixups.py              # patch PA-demo-v4.html in place
    python3 scripts/pa-fixups.py --check      # report only; exit 1 if any fix is missing

Each fix matches on structure, not on minified names (those change on every
build), is skipped when already applied, and fails loudly when its anchor is
gone, so a changed source shows up here instead of silently on the site.

Fixes:
  rail-link       AIM rail opens Brief Curator on its Monitor (#monitor)
  autoscroll      a Portfolio Overview datacut scrolls Influencer Deep Dive
                  into view when it is stacked below (< 1280px)
  tooltip         info tooltips render only while shown and stay on screen
  kpi-cards       Executive Summary cards reflow; labels never leave the card
  trend-cards     Cumulative E/R Trend cards reflow on narrow screens
  legend          Portfolio Overview legend wraps
  portfolio       Portfolio Overview table keeps 600px and scrolls sideways
  bars            contribution bars keep room for their % label
  deep-dive       Performance Change / Contributors stack when narrow
  impact-column   Impact on E/R column narrows on phones
  top-bar         top bar labels give way to icons below 600px
  map-header      map section header wraps its segmented control
  long-list       Long-list rows share one min width (aligned, full borders)
  recruiter-cta   the "Find candidates via Recruiter Agent" button under the
                  influencer list links where the chat's button does
  er-decimal      every E/R value shows one decimal (0.45% -> 0.5%)
  gallery         popup Content Gallery shows only posts that have a thumbnail;
                  an info tooltip says the thumbnails come from MX MAP
  disclaimer      page-foot disclaimer: generic wording, not the workbook-upload notes
  brief           Brief Summary panel above Executive Summary (as on MX MAP)
                  replaces the Rule-based Summary & Actions column; the E/R
                  trend takes the full card width
  contributors    Performance Contributors panel starts expanded
  tutorial        Tutorial toggle in the page header; while on, each section shows
                  a numbered "How to read this section" panel (copy: TUTORIAL)
  no-list-cta     no "Find candidates via Recruiter Agent" button under the Long-list
                  (the chat's button stays)
  no-chat         no AI assistant button (and its chat) at the bottom right
  mxmap           the report sections (head, Brief Summary, Executive Summary,
                  Portfolio Overview, Deep Dive, Long-list, Contribution Map)
                  are rendered by scripts/pa-mxmap.js: MX MAP's markup and class
                  names over the bundle's data, styled by scripts/pa-mxmap.css
  rail-limit      dragging the column divider never squeezes the main column
                  under 690px (MX MAP's ReportLayout limit)
  mxmap-css       that stylesheet, inlined as <style id="fx-mx">
  map-log         Influencer Contribution Map plots E/R on a log scale too, with
                  decade ticks on both axes (1M / 10M / 100M, 0.1% / 1%), as MX MAP does
  rail-menu       AIM rail: Influencer Master Agent brand in place of MX MAP; the three agents are
                  the top-level items (as in shared/flow-rail.js)
  css             the fx-fit stylesheet those hooks rely on
"""
import json
import re
import sys
from pathlib import Path

ID = r'[\w$]+'  # a minified identifier (may contain $)

CSS = '''<style id="fx-fit">
/* Fit pass: no text leaves its box at any width (320 – 1920 px). Hooks are the
   fx-* classes added to the components they name. Written by
   scripts/pa-fixups.py; edit there, not here. */
.fx-tip { max-width: min(20rem, calc(100vw - 16px)); }
.fx-wrap { overflow-wrap: break-word; }
.fx-kpis { grid-template-columns: repeat(auto-fit, minmax(min(100%, 170px), 1fr)); }
.fx-trend { grid-template-columns: repeat(auto-fit, minmax(min(100%, 96px), 1fr)); }
.fx-scroll-x { overflow-x: auto; }
.fx-po-table { min-width: 600px; }
.fx-contrib { grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); }
.fx-st-a { width: 7rem; }
.fx-st-b { width: 8rem; }
.fx-st-h { white-space: nowrap; }
.fx-bar-item { padding: 16px; }
@media (max-width: 599px) {
  .fx-bar-label { display: none; }
  .fx-bar-item { padding: 16px 10px; }
}
/* Brief Summary: measured off MX MAP's .ai-brief-summary. */
.fx-brief {
  padding: 16px 24px 24px; border: 2px solid #c9d3f8; border-radius: 12px;
  background: linear-gradient(90deg, #f2f6ff, #f5f1fe);
}
.fx-brief-head { display: flex; align-items: center; gap: 4px; margin-bottom: 8px; }
.fx-brief-head img { width: 56px; height: 56px; flex: none; margin-left: -10px; }
.fx-brief-head h2 { margin: 0; font: 700 26px/1.3 var(--mm-font-title); color: var(--color-text-default); }
.fx-brief-surface { padding: 14px 16px; border: 1px solid #dfe4f1; border-radius: 4px; background: #fff; }
.fx-brief-item { display: flex; min-width: 0; flex-direction: column; gap: 2px; overflow-wrap: break-word; }
.fx-brief-item + .fx-brief-item { margin-top: 16px; padding-top: 16px; border-top: 1px solid #c9ced8; }
.fx-brief-item h3 { margin: 0; font: 700 17px/1.4 var(--mm-font-body); color: #0b7cf4; }
.fx-brief-item + .fx-brief-item h3 { color: #5a4fcf; }
.fx-brief-item p { margin: 0; font: 400 17px/1.5 var(--mm-font-body); color: var(--color-text-default); }
.fx-brief-item button {
  align-self: flex-end; margin-top: 6px; padding: 0; border: 0; background: none; cursor: pointer; text-align: right;
  font: 700 13px/1.4 var(--mm-font-body); color: #0b7cf4;
}
.fx-brief-item button:hover { text-decoration: underline; }
/* Tutorial: panels exist only while the header toggle is on (html.fx-tut-on). */
.fx-tut-toggle {
  display: inline-flex; align-items: center; gap: 6px; height: 32px; padding: 0 12px; cursor: pointer; white-space: nowrap;
  border: 1px solid var(--color-border-primary-2); border-radius: 8px; background: var(--color-surface-highest);
  font: 700 14px/1 var(--mm-font-body); color: var(--color-text-primary-2);
}
.fx-tut-toggle[aria-pressed="true"] { background: var(--color-surface-primary); color: var(--color-text-inverse); }
.fx-tut { display: none; margin-top: 12px; border-radius: 8px; background: var(--color-surface-highlight); }
.fx-tut-on .fx-tut { display: block; }
.fx-tut.fx-tut-side { margin: 12px 16px; }
.fx-brief .fx-tut { margin: 0 0 12px; }
.fx-tut summary {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px; cursor: pointer; list-style: none;
  font: 700 14px/1.4 var(--mm-font-body); color: var(--color-text-default);
}
.fx-tut summary::-webkit-details-marker { display: none; }
.fx-tut summary::after {
  content: ""; width: 7px; height: 7px; margin: 0 4px 3px auto; flex: none;
  border-right: 2px solid currentColor; border-bottom: 2px solid currentColor; transform: rotate(45deg);
}
.fx-tut[open] summary::after { margin-bottom: -3px; transform: rotate(-135deg); }
.fx-tut-num {
  display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; flex: none; border-radius: 50%;
  background: var(--color-surface-primary); color: var(--color-text-inverse); font: 700 12px/1 var(--mm-font-body);
}
.fx-tut-body { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr)); gap: 12px 20px; padding: 4px 12px 14px 40px; }
.fx-tut-body h4 { margin: 0 0 2px; font: 700 13px/1.4 var(--mm-font-body); color: var(--color-text-primary-2); }
.fx-tut-body p { margin: 0; font: 400 14px/1.5 var(--mm-font-body); color: var(--color-text-default); overflow-wrap: break-word; }
@media (max-width: 479px) {
  .fx-tut-body { padding-left: 12px; }
  .fx-st-a { width: 5rem; }
  .fx-st-b { width: 5.5rem; }
  .fx-st-h { white-space: normal; line-height: 1.2; }
}
</style>'''


# Tutorial copy, for first-time subsidiary marketers. One panel per section, in
# reading order; each answers the same three questions.
TUT_PARTS = ('What this shows', 'How to read it', 'What to do next')
TUTORIAL = {
    'brief': (
        'The two things most worth knowing for this period, written by the AI from the numbers further down: how the latest month moved your cumulative E/R, and the one area holding it back.',
        'The blue headline is the overall result and the purple one is the main issue. The sentence under each gives the figures behind it.',
        'Start here. The link under the second headline takes you to Portfolio Overview with that group already selected, so you can check the evidence.',
    ),
    'exec': (
        'The KPI cards show the latest month only: how many Influencers were active, how much they posted, how many people those posts could reach (Po.Reach), how many engaged, and the resulting E/R. The trend below shows E/R accumulated from January.',
        'E/R is Engagement ÷ Po.Reach, so it measures efficiency, not size. The badge on each card compares the latest month with the month before (MoM): blue is up, red is down. In the chart, the blue line is cumulative E/R month by month and the red dashed line is your target.',
        'Check whether the blue line is closing in on the target. If Current YTD is lower than Prior Cumulative, the latest month pulled your E/R down, and the sections below show why.',
    ),
    'portfolio': (
        'How your activity is split across groups. Use the switch on the right to group by Passion Point, Tier or Channel.',
        'Compare the two bars in each row. Po.Reach Contribution is the group\'s share of your total reach; Engagement Contribution is its share of your total engagement. A group with a bigger reach share than engagement share is dragging E/R down. The reverse is lifting it.',
        'Click a row to filter the Influencer Long-list to that group and see who is in it. Click the row again to clear the filter.',
    ),
    'map': (
        'Every Influencer as one dot. Further right means more Po.Reach; higher up means a better E/R. Switch to Passion Point or Tier to plot groups instead of people.',
        'The two grey lines mark the median and split the map into four colour-coded quadrants. Top right is the ideal: big reach and strong E/R. Bottom right is big reach with weak E/R, which weighs most on your result. Both axes are log scale, so each gridline is 10× the one before.',
        'Hover a dot for its exact figures. Click it to jump to that Influencer in the Long-list.',
    ),
    'dive': (
        'Who moved your numbers. Performance Change lists the Influencers who pushed cumulative E/R down or up in the latest month. Performance Contributors ranks the top five by Po.Reach and by Engagement.',
        'Impact on E/R is in percentage points (%p): -0.050%p means that Influencer alone lowered your cumulative E/R by 0.05 points. In Contributors, compare each person\'s reach share with their engagement share, as in Portfolio Overview.',
        'Click a row to jump to that Influencer in the Long-list, or click their name to open their profile and recent posts.',
    ),
    'list': (
        'Every Influencer in the current selection, with archetype, tier, Po.Reach (and their share of the total) and E/R.',
        'When a Passion Point is selected in Portfolio Overview, its name appears in brackets in the title. Use the Po.Reach and E/R headers to sort, and the Tier header to filter by tier.',
        'Click a row to open that Influencer\'s profile and recent posts. Compare the top and bottom of the E/R column to decide who to keep working with and who to review.',
    ),
}


class Missing(Exception):
    pass


def one(pattern, s, what):
    """The single match of pattern in s, or Missing."""
    found = list(re.finditer(pattern, s))
    if len(found) != 1:
        raise Missing(f'{what}: expected 1 match, found {len(found)}')
    return found[0]


def react_alias(s):
    """The name the bundle uses for the React namespace (A.useState → A)."""
    names = re.findall(r'(' + ID + r')\.useLayoutEffect\(', s)
    if not names:
        raise Missing('React namespace: no useLayoutEffect call found')
    return max(set(names), key=names.count)


def fix_rail_link(s):
    if '["brief","Brief Curator","Brief_Curator.html#monitor"]' in s:
        return s, False
    m = one(r'\["brief","Brief Curator","Brief_Curator\.html(#[\w-]*)?"\]', s, 'rail link')
    return s[:m.start()] + '["brief","Brief Curator","Brief_Curator.html#monitor"]' + s[m.end():], True


def fix_autoscroll(s):
    if 'matchMedia("(min-width: 1280px)").matches||requestAnimationFrame' in s:
        return s, False
    panel = one(r'\.jsx\("div",\{ref:(' + ID + r'),style:(' + ID + r')!=null\?\{width:\2\}', s, 'Deep Dive panel ref')
    ref = panel.group(1)
    call = one(r'onSelectGroup:\((' + ID + r'),(' + ID + r')\)=>(' + ID + r')\(\1\)\(\2\)\}\)(?=,' + ID +
               r'\.jsx\("div",\{className:"hidden xl:block")', s, 'Portfolio Overview onSelectGroup')
    sel = one(r'\.jsx\(' + ID + r',\{analysisRecords:' + ID + r',selectedGroup:(' + ID + r')&&\(\1\.axis==="tier"',
              s[max(0, call.start() - 400):call.start()], 'Portfolio Overview selection').group(1)
    a, b, pick = call.group(1), call.group(2), call.group(3)
    new = ('onSelectGroup:(' + a + ',' + b + ')=>{const off=' + sel + '&&' + sel + '.axis===' + a + '&&' + sel + '.key===' + b +
           ';' + pick + '(' + a + ')(' + b + ');off||matchMedia("(min-width: 1280px)").matches||requestAnimationFrame(()=>{'
           'const el=' + ref + '.current;if(!el)return;const top=el.getBoundingClientRect().top;'
           'if(top>=0&&top<window.innerHeight*.5)return;window.scrollTo({top:window.scrollY+top-24,'
           'behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth"})})}})')
    return s[:call.start()] + new + s[call.end():], True


def fix_tooltip(s):
    if 'fx-tip pointer-events-none' in s:
        return s, False
    R = react_alias(s)
    m = one(r'function (' + ID + r')\(\{text:e,children:t\}\)\{return (' + ID + r')\.jsxs\("span",\{className:"group relative inline-flex",'
            r'tabIndex:0,children:\[t,\2\.jsx\("span",\{role:"tooltip",className:"pointer-events-none invisible absolute top-full '
            r'left-0 z-50 mt-1\.5 w-max max-w-xs opacity-0 transition-opacity group-hover:visible group-hover:opacity-100 '
            r'group-focus-visible:visible group-focus-visible:opacity-100",style:\{', s, 'tooltip component')
    fn, k = m.group(1), m.group(2)
    new = ('function ' + fn + '({text:e,children:t}){const[fo,fso]=' + R + '.useState(!1),[fx,fsx]=' + R + '.useState(0),fr=' + R +
           '.useRef(null),fd=' + R + '.useRef(0);' + R + '.useLayoutEffect(()=>{if(!fo||!fr.current)return;const b=fr.current.'
           'getBoundingClientRect(),w=document.documentElement.clientWidth,l=b.left-fd.current,rt=l+b.width,d=rt>w-8?'
           'Math.max(8-l,w-8-rt):l<8?8-l:0;fd.current=d,fsx(d)},[fo]);const fon=()=>fso(!0),foff=()=>{fso(!1),fd.current=0,fsx(0)};'
           'return ' + k + '.jsxs("span",{className:"group relative inline-flex",tabIndex:0,onMouseEnter:fon,onMouseLeave:foff,'
           'onFocus:fon,onBlur:foff,children:[t,fo&&' + k + '.jsx("span",{role:"tooltip",ref:fr,className:"fx-tip '
           'pointer-events-none absolute top-full left-0 z-50 mt-1.5 w-max",style:{transform:`translateX(${fx}px)`,')
    return s[:m.start()] + new + s[m.end():], True


def fix_kpi_cards(s):
    if 'fx-kpis' in s.split('<style id="fx-fit">')[0]:
        return s, False
    grid = one(r'className:"mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5"', s, 'KPI grid')
    s = s[:grid.start()] + 'className:"fx-kpis mt-4 grid gap-3"' + s[grid.end():]
    card = one(r'(function ' + ID + r'\(\{label:e,value:t,badge:a,sub:r\}\)\{return ' + ID + r'\.jsxs\("div",\{className:)"flex flex-col gap-2"'
               r'(,style:\{padding:16,[^}]*\},children:\[' + ID + r'\.jsx\("span",\{)(style:\{)', s, 'KPI card')
    return s[:card.start()] + card.group(1) + '"flex min-w-0 flex-col gap-2"' + card.group(2) + 'className:"fx-wrap",' + card.group(3) + s[card.end():], True


def simple(marker, old, new, what):
    def fix(s):
        if marker in s.split('<style id="fx-fit">')[0]:
            return s, False
        m = one(re.escape(old), s, what)
        return s[:m.start()] + new + s[m.end():], True
    return fix


fix_trend_cards = simple('fx-trend', 'className:"grid grid-cols-3 gap-2"', 'className:"fx-trend grid gap-2"', 'trend cards')


def fix_legend(s):
    # Anchored on the legend's first item: other rows share these classes.
    tail = r'",style:\{\.\.\.' + ID + r'\.label,color:' + ID + r'\.default\},children:\[' + ID + r'\.jsx\(' + ID + r',\{color:' + ID + r',label:"Po\.Reach Contribution"'
    if re.search(r'className:"mt-3 flex flex-wrap items-center gap-4' + tail, s):
        return s, False
    m = one(r'className:"mt-3 flex items-center gap-4(?=' + tail + ')', s, 'Portfolio legend')
    return s[:m.start()] + 'className:"mt-3 flex flex-wrap items-center gap-4' + s[m.end():], True


def fix_portfolio(s):
    if 'fx-po-table' in s.split('<style id="fx-fit">')[0]:
        return s, False
    start = one(r'(' + ID + r')\.jsxs\("div",\{className:"mt-3 grid items-center rounded-\[3px\] px-3"', s, 'Portfolio header')
    k = start.group(1)
    end = one(r',' + ID + r'\.jsx\("p",\{className:"mt-3 border-t pt-3"', s[start.start():], 'Portfolio caption')
    body = s[start.start():start.start() + end.start()]
    if body.count('.jsx("div",{className:"grid px-3"') != 1:
        raise Missing('Portfolio rows: expected one rows grid')
    body = body.replace('className:"mt-3 grid items-center rounded-[3px] px-3"', 'className:"grid items-center rounded-[3px] px-3"', 1)
    wrapped = k + '.jsx("div",{className:"fx-scroll-x mt-3",children:' + k + '.jsxs("div",{className:"fx-po-table",children:[' + body + ']})})'
    return s[:start.start()] + wrapped + s[start.start() + end.start():], True


def fix_bars(s):
    if 'style:{minWidth:56,height:a,' in s:
        return s, False
    m = one(r'(function ' + ID + r'\(\{pct:e,color:t,height:a=20\}\)\{return ' + ID +
            r'\.jsxs\("div",\{className:"relative w-full overflow-hidden rounded-\[3px\]",style:\{)(height:a,)', s, 'contribution bar')
    return s[:m.start()] + m.group(1) + 'minWidth:56,' + m.group(2) + s[m.end():], True


def fix_deep_dive(s):
    changed = False
    for section in ('performance-change', 'performance-contributors'):
        at = one(r'id:"' + section + '"', s, section).end()
        window = s[at:at + 700]
        if 'className:"fx-contrib grid gap-3"' in window:
            continue
        g = window.find('className:"grid grid-cols-2 gap-3"')
        if g < 0:
            raise Missing(section + ': two-column grid not found')
        s = s[:at + g] + 'className:"fx-contrib grid gap-3"' + s[at + g + len('className:"grid grid-cols-2 gap-3"'):]
        changed = True
    return s, changed


def fix_impact_column(s):
    head = one(r'children:"Impact on E/R"', s, 'Impact on E/R header')
    fn = s.rfind('function ', 0, head.start())
    end = s.find('function ', head.end())
    body = s[fn:end]
    if 'fx-st-a' in body:
        return s, False
    new = re.sub(r'className:"w-28((?: shrink-0)?) text-right whitespace-nowrap"', r'className:"fx-st-a fx-st-h\1 text-right"', body)
    new = re.sub(r'className:"w-32((?: shrink-0)?) text-right whitespace-nowrap"', r'className:"fx-st-b fx-st-h\1 text-right"', new)
    new = re.sub(r'className:"w-28((?: shrink-0)?) text-right tabular-nums"', r'className:"fx-st-a\1 text-right tabular-nums"', new)
    new = re.sub(r'className:"w-32((?: shrink-0)?) text-right tabular-nums"', r'className:"fx-st-b\1 text-right tabular-nums"', new)
    if new == body:
        raise Missing('Impact on E/R column: fixed-width classes not found')
    return s[:fn] + new + s[end:], True


def fix_top_bar(s):
    if 'fx-bar-item' in s.split('<style id="fx-fit">')[0]:
        return s, False
    m = one(r'(function ' + ID + r'\(\{label:e,last:t,children:a\}\)\{return (' + ID + r')\.jsxs\("div",\{className:)"flex items-center justify-center"'
            r',style:\{height:56,padding:16,(gap:8,.{0,160}?\},children:\[e&&\2\.jsx\("span",\{)(style:\{)', s, 'top bar item')
    return (s[:m.start()] + m.group(1) + '"fx-bar-item flex items-center justify-center",title:e,style:{height:56,' + m.group(3) +
            'className:"fx-bar-label",' + m.group(4) + s[m.end():]), True


def fix_map_header(s):
    m = list(re.finditer(r'\.jsxs\("section",\{style:\{\.\.\.' + ID + r',padding:' + ID + r'\.card\},children:\[' + ID +
                         r'\.jsxs\("div",\{className:"flex (flex-wrap )?items-start justify-between gap-3"', s))
    todo = [x for x in m if not x.group(1)]
    if not m:
        raise Missing('map header: not found')
    if not todo:
        return s, False
    for x in reversed(todo):
        s = s[:x.start()] + x.group(0).replace('className:"flex items-start', 'className:"flex flex-wrap items-start') + s[x.end():]
    return s, True


def fix_brief(s):
    if 'className:"fx-brief"' in s:
        return s, False
    # The rule column closes the Executive Summary section and its component.
    col = one(r',(' + ID + r')\.jsxs\("div",\{children:\[' + ID + r'\.jsxs\("div",\{className:"flex items-center gap-1\.5",children:\[' + ID +
              r'\.jsx\(' + ID + r',\{children:"Rule-based Summary & Actions"\}\),.*?\]\}\),' + ID +
              r'\.jsx\("div",\{className:"flex flex-col gap-2",children:(' + ID + r')\.map\((' + ID + r')=>' + ID + r'\.jsx\(' + ID +
              r',\{rule:\3,onAction:\3\.id==="L-02"\?(' + ID + r'):void 0\},\3\.id\)\)\}\)\]\}\)(\]\}\)\]\}\))\}', s, 'rule column')
    k, rules, act = col.group(1), col.group(2), col.group(4)
    s = s[:col.start()] + col.group(5) + ']})}' + s[col.end():]
    brief = (f'{k}.jsxs("section",{{className:"fx-brief","aria-label":"Brief Summary",children:['
             f'{k}.jsxs("div",{{className:"fx-brief-head",children:[{k}.jsx("img",{{src:"resources/ai-summary.png",alt:""}}),'
             f'{k}.jsx("h2",{{children:"Brief Summary"}})]}}),'
             f'{k}.jsx("div",{{className:"fx-brief-surface",children:{rules}.map(fxR=>{k}.jsxs("article",{{className:"fx-brief-item",children:['
             f'{k}.jsx("h3",{{children:fxR.title}}),{k}.jsx("p",{{children:fxR.evidence}}),'
             f'fxR.id==="L-02"&&{k}.jsx("button",{{type:"button",onClick:{act},children:fxR.action}})]}},fxR.id))}})]}})')
    sec = one(r'return (?=' + ID + r'\.jsxs\("section",\{style:\{\.\.\.' + ID + r',padding:' + ID + r'\.card\},children:\[' + ID +
              r'\.jsxs\("div",\{className:"flex items-center gap-1\.5",children:\[' + ID + r'\.jsx\("h2",\{style:\{[^}]*\},children:"Executive Summary"\}\))', s, 'executive summary')
    s = s[:sec.end()] + f'{k}.jsxs({k}.Fragment,{{children:[{brief},' + s[sec.end():]
    for old, new, what in (
        ('className:"mt-4 grid grid-cols-1 gap-4 border-t pt-4 lg:grid-cols-[1.05fr_1.3fr]"', 'className:"mt-4 border-t pt-4"', 'summary grid'),
        ('latest performance, cumulative efficiency and rule-based actions', 'latest performance and cumulative efficiency', 'summary tooltip'),
    ):
        m = one(re.escape(old), s, what)
        s = s[:m.start()] + new + s[m.end():]
    return s, True


def fix_contributors(s):
    m = one(r'id:"performance-contributors",title:"Performance Contributors",(defaultOpen:!0,)?', s, 'contributors panel')
    if m.group(1):
        return s, False
    return s[:m.end()] + 'defaultOpen:!0,' + s[m.end():], True


def fix_tutorial(s):
    if 'function FxTut(' in s:
        return s, False
    k = one(r'(' + ID + r')\.jsx\("h2",\{style:\{[^}]*\},children:"Executive Summary"\}\)', s, 'jsx runtime').group(1)
    copy = json.dumps({key: {'n': n, 'parts': list(zip(TUT_PARTS, texts))}
                       for n, (key, texts) in enumerate(TUTORIAL.items(), 1)}, ensure_ascii=False, separators=(',', ':'))

    def panel(key, side=False):
        return f'{k}.jsx(FxTut,{{id:"{key}"' + (',side:!0' if side else '') + '})'

    # Insert after (or, with before=True, in front of) each section's anchor.
    spots = [
        ('brief', r'\.jsx\("h2",\{children:"Brief Summary"\}\)\]\}\)', False, False),
        ('exec', r'children:"Executive Summary"\}\),' + ID + r'\.jsx\(' + ID + r',\{text:`[^`]*`\}\)\]\}\)', False, False),
        ('portfolio', r'children:"Portfolio Overview".*?,(?=' + ID + r'\.jsxs?\("div",\{className:"mt-3 flex flex-wrap items-center gap-4")', True, False),
        ('map', r'children:"Influencer Contribution Map".*?,(?=' + ID + r'\.jsxs?\("div",\{className:"mt-3 flex flex-wrap items-center gap-4")', True, False),
        ('dive', r'children:"Influencer Deep Dive"\}\)\}\)', False, True),
        ('list', r'children:' + ID + r'\("label"\)\}\),' + ID + r'\.jsx\("div",\{className:"mt-1 text-sm font-semibold",style:\{color:' + ID +
                 r'\},children:' + ID + r'\?\?' + ID + r'\("all"\)\}\)\]\}\)', False, True),
    ]
    for key, pattern, before, side in spots:
        m = one(pattern, s, f'tutorial {key}')
        s = s[:m.end()] + (panel(key, side) + ',' if before else ',' + panel(key, side)) + s[m.end():]
    ctl = one(r'children:\[(?=' + ID + r'\.jsx\(' + ID + r',\{value:' + ID + r',onChange:' + ID + r',placeholder:' + ID + r',maxDate:)', s, 'header controls')
    s = (s[:ctl.end()] + f'{k}.jsx("button",{{type:"button",className:"fx-tut-toggle","aria-pressed":!1,onClick:fxTutToggle,children:"Tutorial"}}),' + s[ctl.end():])
    dims = one(r'const ' + ID + r'=\["Influencer","Passion Point","Tier"\]', s, 'map dims')
    s = (s[:dims.start()] +
         'function fxTutToggle(e){e.currentTarget.setAttribute("aria-pressed",document.documentElement.classList.toggle("fx-tut-on"))}'
         f'function FxTut({{id:e,side:t}}){{const a={copy}[e];return {k}.jsxs("details",{{className:"fx-tut"+(t?" fx-tut-side":""),open:a.n===1,children:['
         f'{k}.jsxs("summary",{{children:[{k}.jsx("span",{{className:"fx-tut-num",children:a.n}}),"How to read this section"]}}),'
         f'{k}.jsx("div",{{className:"fx-tut-body",children:a.parts.map(([r,n])=>{k}.jsxs("div",{{children:[{k}.jsx("h4",{{children:r}}),{k}.jsx("p",{{children:n}})]}},r))}})]}})}}' +
         s[dims.start():])
    return s, True


def fix_no_list_cta(s):
    fn = one(r'function (' + ID + r')\(\)\{return ' + ID + r'\.jsx\("div",\{className:"border-t px-4 py-3"[^;]*?"Find candidates via Recruiter Agent"', s, 'list cta').group(1)
    calls = list(re.finditer(r',' + ID + r'\.jsx\(' + re.escape(fn) + r',\{\}\)', s))
    if not calls:
        return s, False
    for m in reversed(calls):
        s = s[:m.start()] + s[m.end():]
    return s, True


def fix_no_chat(s):
    fn = one(r'function (' + ID + r')\(\)\{(?:(?!function ).)*?"AI Assistant is typing"', s, 'chat component').group(1)
    calls = list(re.finditer(ID + r'\.jsx\(' + re.escape(fn) + r',\{\}\),', s))
    if not calls:
        return s, False
    for m in reversed(calls):
        s = s[:m.start()] + s[m.end():]
    return s, True


def fix_mxmap(s):
    if 'function FxExec(' in s:
        return s, False
    g = lambda pattern, what, n=1: one(pattern, s, 'mxmap ' + what).group(n)
    k = g(r'(' + ID + r')\.jsx\("h2",\{style:\{[^}]*\},children:"Executive Summary"\}\)', 'jsx runtime')
    ytd = re.search(r'er:([\d.]+)\},\{\.\.\.' + ID + r',points:' + ID + r',currentYtdEr:\1\}', s)
    line = one(ID + r'\.jsx\((' + ID + r'),\{width:"100%",height:140,children:' + ID + r'\.jsxs\((' + ID + r'),\{data:' + ID +
               r',margin:\{top:8,right:12,bottom:0,left:0\},accessibilityLayer:!1,children:\[' + ID + r'\.jsx\((' + ID +
               r'),\{strokeDasharray:"3 3",stroke:' + ID + r'\}\),' + ID + r'\.jsx\((' + ID + r'),\{dataKey:"month"', s, 'mxmap line chart')
    tip = one(ID + r'\.jsx\((' + ID + r'),\{cursor:\{stroke:' + ID + r'\},content:' + ID + r'\.jsx\((' + ID + r'),\{\}\)\}\)', s, 'mxmap trend tooltip')
    groups = one(r'==="Tier"\?(' + ID + r')\(' + ID + r',\[\.\.\.(' + ID + r')\],' + ID + r'=>' + ID + r'\.tier\):' + ID + r'==="Channel"\?\1\(' + ID +
                 r',\[\.\.\.(' + ID + r')\],' + ID + r'=>' + ID + r'\.channel\):\1\(' + ID + r',\[\.\.\.(' + ID + r')\],' + ID + r'=>' + ID + r'\.pp\)', s, 'mxmap portfolio rows')
    points = one(r'==="Tier"\?(' + ID + r')\(' + ID + r',\[\.\.\.' + ID + r'\],' + ID + r'=>' + ID + r'\.tier\):' + ID + r'==="Passion Point"\?\1\(' + ID +
                 r',\[\.\.\.' + ID + r'\],' + ID + r'=>' + ID + r'\.pp\):(' + ID + r')\(' + ID + r'\)', s, 'mxmap map points')
    popup = set(re.findall(r'\{bind:' + ID + r',portal:' + ID + r'\}=(' + ID + r')\(', s))
    if len(popup) != 1:
        raise Missing(f'mxmap popup hook: expected 1 name, found {len(popup)}')
    names = {
        'K': k, 'A': react_alias(s),
        'LO': g(r'function ' + ID + r'\(\{text:(' + ID + r')\}\)\{return ' + ID + r'\.jsx\((' + ID + r'),\{text:\1,children:' + ID + r'\.jsx\(' + ID + r',\{name:"IconInfoSizeMedium"', 'tooltip', 2),
        'NX': g(r'\.useMemo\(\(\)=>(' + ID + r')\((' + ID + r')\?\?(' + ID + r')\),\[\2,\3\]\)', 'trend builder'),
        'YTD': ytd.group(1) if ytd else 'null',
        'PX': g(r'\?(' + ID + r')\(\{priorEr:', 'rules'),
        'RC': line.group(1), 'LINECHART': line.group(2), 'GRID': line.group(3), 'XAXIS': line.group(4),
        'YAXIS': g(ID + r'\.jsx\((' + ID + r'),\{width:40,tickCount:4', 'y axis'),
        'REFLINE': g(ID + r'\.jsx\((' + ID + r'),\{y:' + ID + r',stroke:' + ID + r'\.below,strokeWidth:1\.3', 'reference line'),
        'TOOLTIP': tip.group(1), 'TRENDTIP': tip.group(2),
        'LINE': g(ID + r'\.jsx\((' + ID + r'),\{type:"monotone",dataKey:"er"', 'line'),
        'SCATTERCHART': g(ID + r'\.jsxs\((' + ID + r'),\{margin:\{top:16,right:16,bottom:8,left:4\},accessibilityLayer:!1', 'scatter chart'),
        'SCATTER': g(ID + r'\.jsx\((' + ID + r'),\{data:' + ID + r'\.points,onClick:', 'scatter'),
        'H4': groups.group(1), 'NL': groups.group(2), 'BA': groups.group(3), 'DA': groups.group(4),
        'FT': points.group(1), 'XO': points.group(2),
        'XW': g(r'\.useMemo\(\(\)=>(' + ID + r')\(' + ID + r'\),\[' + ID + r'\]\),' + ID + r'=' + ID + r'\.useMemo\(\(\)=>' + ID + r'\.filter\(' + ID + r'=>' + ID + r'\.impact<0\)', 'impact rows'),
        'NO': popup.pop(),
        'NS': g(r'function (' + ID + r')\(' + ID + r'\)\{const ' + ID + r'=' + ID + r'\[' + ID + r'\];if\(' + ID + r'\)return typeof ' + ID + r'=="string"\?' + ID + r':' + ID + r'\.src\}', 'avatar lookup'),
        'U4': g(r'\.useMemo\(\(\)=>(' + ID + r')\(' + ID + r'\),\[' + ID + r'\]\),' + ID + r'=' + ID + r'\.useMemo\(\(\)=>' + ID + r'\(' + ID + r'\(' + ID + r',\{tier:' + ID + r'\}\)', 'list rows'),
    }
    code = (Path(__file__).resolve().parent / 'pa-mxmap.js').read_text(encoding='utf-8')
    code = re.sub(r'__([A-Z0-9]+)__', lambda m: names[m.group(1)], code)
    group = g(r'selectedGroup:(' + ID + r')&&\(\1\.axis==="tier"\|\|\1\.axis==="ppoint"\|\|\1\.axis==="channel"\)', 'selected group')
    setter = g(r'(' + ID + r')\(\{axis:"ppoint",key:"Photography & Film"\}\)', 'group setter')

    def swap(pattern, new, what):
        nonlocal s
        m = one(pattern, s, 'mxmap ' + what)
        s = s[:m.start(1)] + new + s[m.end(1):]

    # The report head leaves the left column and spans both, as on MX MAP.
    head = one(ID + r'\.jsxs\("div",\{className:"flex items-start gap-3",children:\[' + ID + r'\.jsx\("div",\{className:"min-w-0 flex-1",children:' + ID +
               r'\.jsx\(' + ID + r',\{scopeName:(.*?),periodLabel:(' + ID + r'),asOf:(' + ID + r')\}\)\}\),(' + ID + r')\.length>1&&' + ID +
               r'\.jsx\("div",\{className:"shrink-0",children:' + ID + r'\.jsx\(' + ID + r',\{index:(.*?),total:(.*?),onChange:(' + ID + r')\}\)\}\)\]\}\),', s, 'mxmap report head')
    h = head.groups()
    s = s[:head.start()] + s[head.end():]
    cols = one(ID + r'\.jsxs\("div",\{className:"flex flex-col gap-6 xl:flex-row xl:items-start",children:\[(' + ID +
               r'\.jsx\("div",\{className:"flex min-w-0 flex-1 flex-col gap-6",children:(' + ID + r')\?' + ID +
               r'\.jsxs\("div",\{className:")animate-in fade-in-0 flex flex-col gap-6"', s, 'mxmap columns')
    s = (s[:cols.start()] + f'{k}.jsxs("div",{{className:"fx-mx subsidiary-performance-brief performance-analysis",children:[{cols.group(2)}&&'
         f'{k}.jsx(FxHead,{{scopeName:{h[0]},periodLabel:{h[1]},asOf:{h[2]},pager:{h[3]}.length>1?{{index:{h[4]},total:{h[5]},onChange:{h[6]}}}:null}}),'
         f'{k}.jsxs("div",{{className:"fx-mx-cols flex flex-col xl:flex-row xl:items-start",children:[' + cols.group(1) + 'animate-in fade-in-0 spa-main"' + s[cols.end():])
    end = one(ID + r'&&' + ID + r'\.jsx\("div",\{className:"xl:hidden",children:' + ID + r'\(\)\}\)\]\}\)', s, 'mxmap columns end')
    s = s[:end.end()] + ']})' + s[end.end():]

    swap(ID + r'\.jsx\((' + ID + r'),\{scopeName:[^{}]*?,analysisRecords:' + ID + r',trendRecords:' + ID + r',benchmark:' + ID + r',onReviewPhotographyFilm:', 'FxExec', 'executive summary')
    swap(ID + r'\.jsx\((' + ID + r'),\{analysisRecords:' + ID + r',selectedGroup:' + ID + r'&&\(' + ID + r'\.axis==="tier"\|\|' + ID + r'\.axis==="ppoint"\|\|' + ID + r'\.axis==="channel"\)', 'FxPortfolio', 'portfolio')
    swap(r'=\(\)=>' + ID + r'\.jsx\((' + ID + r'),\{analysisRecords:' + ID + r',analysisRows:' + ID + r',selectedGroup:', 'FxMap', 'map')
    swap(r'topSlot:' + ID + r'\?' + ID + r'\.jsx\((' + ID + r'),\{analysisRecords:' + ID + r',analysisRows:' + ID + r',onFocus:', 'FxDive', 'deep dive')
    rail = one(ID + r'\.jsxs\("div",\{className:"overflow-hidden",style:' + ID + r',children:\[' + ID + r'\.jsx\(' + ID + r',\{records:', s, 'mxmap rail')
    s = s[:rail.start()] + f'{k}.jsxs("div",{{className:"spa-rail",children:[{k}.jsx(FxList,{{group:{group},onClear:()=>{setter}(null),records:' + s[rail.end():]
    for old, new, what in (
        ('xl:w-[560px]', 'fx-mx-half', 'rail width'),
        ('className:"hidden xl:block xl:-mx-3 xl:w-2.5 xl:shrink-0 xl:cursor-col-resize xl:self-stretch xl:rounded-full xl:bg-transparent xl:transition-colors hover:xl:bg-border"',
         f'className:"spa-resize-handle fx-mx-handle",children:{k}.jsx("span",{{className:"spa-resize-handle__grip","aria-hidden":!0}})', 'resize handle'),
    ):
        m = one(re.escape(old), s, 'mxmap ' + what)
        s = s[:m.start()] + new + s[m.end():]
    dims = one(r'const ' + ID + r'=\["Influencer","Passion Point","Tier"\]', s, 'map dims')
    return s[:dims.start()] + code + s[dims.start():], True


def fix_rail_limit(s):
    if '.offsetWidth??1e9)-720' in s:
        return s, False
    ref = one(r'\(\(' + ID + r'=(' + ID + r')\.current\)==null\?void 0:' + ID + r'\.offsetWidth\)\?\?440', s, 'rail ref').group(1)
    m = one(r'Math\.min\(Math\.max\((' + ID + r'\+\(' + ID + r'-' + ID + r'\.clientX\)),360\),window\.innerWidth\*\.75\)', s, 'rail drag')
    # 720 = 690px of main column + the 10px handle and its two 10px gaps.
    new = f'Math.max(360,Math.min({m.group(1)},window.innerWidth*.75,({ref}.current?.parentElement?.offsetWidth??1e9)-720))'
    return s[:m.start()] + new + s[m.end():], True


def fix_mxmap_css(s):
    css = '<style id="fx-mx">\n' + (Path(__file__).resolve().parent / 'pa-mxmap.css').read_text(encoding='utf-8') + '</style>'
    block = re.search(r'<style id="fx-mx">.*?</style>', s, re.S)
    if block:
        if block.group(0) == css:
            return s, False
        return s[:block.start()] + css + s[block.end():], True
    m = one(r'</head>', s, '</head>')
    return s[:m.start()] + css + '\n' + s[m.start():], True


def fix_map_log(s):
    if 'fxDom(' in s:
        return s, False
    # Helpers: padded domain of the positive values; decade ticks inside it
    # (recharts' own ticks when the domain spans fewer than two decades).
    dims = one(r'const ' + ID + r'=\["Influencer","Passion Point","Tier"\]', s, 'map dims')
    s = (s[:dims.start()] +
         'function fxDom(v){v=v.filter(x=>x>0);return v.length?[Math.min(...v)*.7,Math.max(...v)*1.4]:[.1,10]}'
         'function fxTicks(d){const t=[];for(let n=Math.ceil(Math.log10(d[0]));10**n<=d[1];n++)t.push(10**n);return t.length>1?t:void 0}' +
         s[dims.start():])
    x = one(r'scale:"log",domain:(' + ID + r'),allowDataOverflow:!0,tick:(' + ID + r'),tickFormatter:(' + ID + r'),', s, 'map x axis')
    s = s[:x.start()] + f'scale:"log",domain:{x.group(1)},allowDataOverflow:!0,ticks:fxTicks({x.group(1)}),tick:{x.group(2)},tickFormatter:fxV=>{x.group(3)}(fxV).replace(".0",""),' + s[x.end():]
    pts = one(r'\{data:(' + ID + r')\.points,onClick:', s, 'map points').group(1)
    # E/R of 0 has no place on a log axis: it is drawn on the bottom edge, the tooltip keeps the real value.
    y = one(r'\{type:"number",dataKey:"y",name:(' + ID + r'),unit:"%",tick:(' + ID + r'),tickFormatter:(' + ID + r')=>\3\.toFixed\(1\),(.*?position:"insideLeft",\.\.\.' + ID + r'\}\})', s, 'map y axis')
    s = (s[:y.start()] + '(fxD=>({type:"number",dataKey:fxP=>Math.max(fxP.y,fxD[0]),name:' + y.group(1) +
         ',unit:"%",scale:"log",domain:fxD,allowDataOverflow:!0,ticks:fxTicks(fxD),tick:' + y.group(2) +
         ',tickFormatter:fxV=>+fxV.toPrecision(2),' + y.group(4) + f'))(fxDom({pts}.points.map(fxP=>fxP.y)))' + s[y.end():])
    tip = one(r'X = \$\{(' + ID + r')\} \(log scale\), Y = \$\{(' + ID + r')\} — quadrants', s, 'map tooltip')
    s = s[:tip.start()] + f'X = ${{{tip.group(1)}}}, Y = ${{{tip.group(2)}}} (both log scale) — quadrants' + s[tip.end():]
    return s, True


def fix_long_list(s):
    if 'fxZw=' in s:
        return s, False
    m = one(r'\[(' + ID + r'),' + ID + r'\]=' + ID + r'\.useState\(' + ID + r'\),(' + ID + r')=(' + ID + r')\(\1\),', s, 'Long-list column state')
    cols, tpl, fn = m.group(1), m.group(2), m.group(3)
    one(re.escape(fn) + r'=e=>`24px minmax\(0,1fr\) \$\{e\.archetype\}px', s, 'Long-list column template')
    # Fixed columns + gaps (5×12) + padding (2×16) + a 104px floor for the name column:
    # the 560px desktop panel fits without sideways scroll.
    s = s[:m.end()] + 'fxZw=24+104+' + '+'.join(cols + '.' + c for c in ('archetype', 'tier', 'reach', 'er')) + '+60+32,' + s[m.end():]
    for row in ('sticky top-0 z-20 grid items-center gap-3 border-b px-4', 'grid items-center gap-3 border-b px-4 py-2.5'):
        r = one(r'className:"' + re.escape(row) + r'",style:\{gridTemplateColumns:' + re.escape(tpl) + ',', s, 'Long-list row: ' + row)
        s = s[:r.end()] + 'minWidth:fxZw,' + s[r.end():]
    return s, True


def fix_recruiter_cta(s):
    # The chat's CTA is a real link; the one under the Long-list is a styled span.
    # Point it at the same address (read from the chat's), so both stay in sync.
    href = one(r'\.cta&&' + ID + r'\.jsxs\("a",\{href:"(Influencer_Recruiter\.html[^"]*)"', s, 'chat Recruiter CTA').group(1)
    head = (r'(function ' + ID + r'\(\)\{return (' + ID + r')\.jsx\("div",\{className:"border-t px-4 py-3",style:\{borderColor:' +
            ID + r'\.subtleColor\},children:\2\.jsxs\()')
    tail = r'(,style:\{background:"linear-gradient\(135deg, #0380FE 0%, #0079CD 100%\)"[^}]*\},children:\["Find candidates via Recruiter Agent")'
    if re.search(head + r'"a",\{href:"' + re.escape(href) + '"', s):
        return s, False
    m = one(head + r'"span",\{className:"flex items-center justify-center gap-1\.5 rounded-\[10px\] px-4 py-3 text-\[13px\] font-bold"' + tail,
            s, 'Long-list Recruiter CTA')
    return (s[:m.start()] + m.group(1) + '"a",{href:"' + href + '",className:"flex items-center justify-center gap-1.5 rounded-[10px] '
            'px-4 py-3 text-[13px] font-bold transition-opacity hover:opacity-90"' + m.group(3) + s[m.end():]), True


# E/R sites formatted with toFixed(2), as (pattern with the digit in group 2, count).
ER_SITES = [
    (r'(label:"E/R",value:`\$\{[^`]{1,80}?\.toFixed\()([12])(\)\}%`)', 4),  # KPI, trend tooltip, detail, post popup
    (r'(children:\[' + ID + r'\.er\.toFixed\()([12])(\),"%"\])', 1),  # Portfolio table cell
    (r'("\u2014":`\$\{' + ID + r'\.er\.toFixed\()([12])(\)\}%`)', 1),  # Long-list row
    (r'(function ' + ID + r'\(\{label:e,value:t,bad:a\}\)\{return .{0,400}?children:\[t\.toFixed\()([12])(\),"%"\])', 1),  # trend cards
]
# E/R written into the demo's canned text. 0.03% (Hugo's E/R) is left alone: 0.0% reads wrong.
ER_TEXT = [('an E/R of 0.45%', 'an E/R of 0.5%'), ("E/R is lower (0.33%)", "E/R is lower (0.3%)"),
           ('E/R growth to 0.92%', 'E/R growth to 0.9%')]


def fix_er_decimal(s):
    changed = False
    for pat, n in ER_SITES:
        found = list(re.finditer(pat, s))
        if len(found) != n:
            raise Missing(f'E/R format {pat[:40]}...: expected {n} matches, found {len(found)}')
        for m in reversed(found):
            if m.group(2) == '2':
                s = s[:m.start(2)] + '1' + s[m.end(2):]
                changed = True
    for old, new in ER_TEXT:
        if new in s:
            continue
        m = one(re.escape(old), s, 'E/R text ' + old)
        s = s[:m.start()] + new + s[m.end():]
        changed = True
    return s, changed


RAIL_BRAND = ('<div style="display:flex;flex-direction:column;gap:4px">'
              '<span style="font:700 22px/1 Samsung SS Head,SamsungSSHead,sans-serif;color:#263144">Influencer Master Agent</span>'
              '<span style="font-size:12px;font-weight:500;line-height:1.2;color:#0380FE">Samsung Electronics Marketing Platform</span></div>')


GALLERY_TIP = ("Thumbnails are imported from MX MAP's Influencer Content Gallery. "
               "Posts without a thumbnail there are not shown.")
# A post has a thumbnail when the fetch shim can answer for it: an entry in
# MX_THUMB_OVERRIDES (if this build has one) or a YouTube URL (i.ytimg.com).
YT_ID = r'/(?:youtube\.com\/watch\?(?:.*&)?v=|youtu\.be\/|youtube\.com\/(?:embed|v|shorts)\/)[\w-]{11}/'


def fix_gallery(s):
    if 'Posts without a thumbnail there are not shown.' in s:
        return s, False
    tip = one(r'function (' + ID + r')\(\{text:e\}\)\{return (' + ID + r')\.jsx\(' + ID + r',\{text:e,children:\2\.jsx\(' + ID +
              r',\{name:"IconInfoSizeMedium"', s, 'info tooltip').group(1)
    norm = one(r'function (' + ID + r')\(e\)\{return e\.replace\(/\^https\?:\\/\\//,""\)\.replace\(/\\/\$/,""\)\.toLowerCase\(\)\}',
               s, 'post URL normalizer').group(1)
    m = one(r'(' + ID + r')\.jsx\("div",\{className:"mb-2 uppercase",style:\{\.\.\.(' + ID + r')\.caption,color:(' + ID +
            r')\.muted,letterSpacing:"0\.04em"\},children:"Content Gallery"\}\),(' + ID + r')\.length===0\?\1\.jsx\("p",\{style:\{\.\.\.\2'
            r'\.caption,color:\3\.muted\},children:"No tracked posts in the selected scope\."\}\):\1\.jsx\("div",\{className:"flex gap-3 '
            r'overflow-x-auto pb-1",children:\4\.map\(\((' + ID + r'),(' + ID + r')\)=>\1\.jsx\((' + ID + r'),\{post:\5\},`\$\{\5\.uid\}-'
            r'\$\{\6\}`\)\)\}\)', s, 'Content Gallery')
    k, oe, ae, posts, l, i, card = m.groups()
    pred = ('p=>{const u=p.postUrl||"";return u!=="#"&&(!!(typeof MX_THUMB_OVERRIDES<"u"&&MX_THUMB_OVERRIDES[' + norm +
            '(u)])||' + YT_ID + '.test(u))}')
    new = (k + '.jsxs("div",{className:"mb-2 flex items-center gap-1.5",style:{...' + oe + '.caption,color:' + ae + '.muted},children:[' +
           k + '.jsx("span",{className:"uppercase",style:{letterSpacing:"0.04em"},children:"Content Gallery"}),' +
           k + '.jsx(' + tip + ',{text:' + json.dumps(GALLERY_TIP) + '})]}),(fx=>fx.length===0?' +
           k + '.jsx("p",{style:{...' + oe + '.caption,color:' + ae + '.muted},children:"No MX MAP gallery content in the selected scope."}):' +
           k + '.jsx("div",{className:"flex gap-3 overflow-x-auto pb-1",children:fx.map((' + l + ',' + i + ')=>' + k + '.jsx(' + card +
           ',{post:' + l + '},`${' + l + '.uid}-${' + i + '}`))}))(' + posts + '.filter(' + pred + '))')
    return s[:m.start()] + new + s[m.end():], True


DISCLAIMER = ["Figures are estimates based on tracked Influencer content and may differ from platform-reported metrics.",
              "AI-generated insights are for reference only and should be verified before use."]


def fix_disclaimer(s):
    new = '"disclaimer":' + json.dumps(DISCLAIMER)
    if new in s:
        return s, False
    m = one(r'"disclaimer":\["Figures are calculated from[^\]]*\]', s, 'disclaimer copy')
    return s[:m.start()] + new + s[m.end():], True


def fix_rail_menu(s):
    if 'Samsung Electronics Marketing Platform' in s:
        return s, False
    logo = one(r'<img src="\'\+' + ID + r'\+\'" height="24" alt="MX MAP">', s, 'rail logo')
    s = s[:logo.start()] + RAIL_BRAND + s[logo.end():]
    tops = one(r'<div style="color:#0380FE;font-size:12px;font-weight:500;line-height:1\.2;height:14px">Digital Performance Analysis</div>\'\+'
               r'(' + ID + r')\("Social Marketing"\)\+\1\("PR Analysis"\)\+\1\("Influencer Marketing"\)\+', s, 'rail top items')
    s = s[:tops.start()] + "'+" + s[tops.end():]
    item = one(r'(function ' + ID + r'\((' + ID + r')\)\{var (' + ID + r')=\2\[0\]===' + ID + r';return\'<a href="\'\+\2\[2\]\+\'"\'\+\(\3\?\' aria-current="page"\':""\)\+\' style=")'
               r'display:flex;align-items:center;gap:8px;padding-left:29px;height:32px;font-size:16px;font-weight:\'\+\(\3\?700:500\)\+'
               r'(";border-radius:4px"\+\(\3\?";color:#0380FE;background:#E6F2FE":""\)\+\'">)'
               r'<span style="width:4px;height:4px;border-radius:50%;background:\'\+\(\3\?"#0380FE":"#CECECE"\)\+\'"></span>\'\+', s, 'rail page item')
    new = (item.group(1) + "display:flex;align-items:center;margin-top:8px;padding-left:40px;height:40px;font-size:18px;font-weight:'+(" +
           item.group(3) + '?700:500)+' + item.group(4) + "'+")
    return s[:item.start()] + new + s[item.end():], True


def fix_css(s):
    block = re.search(r'<style id="fx-fit">.*?</style>', s, re.S)
    if block:
        if block.group(0) == CSS:
            return s, False
        return s[:block.start()] + CSS + s[block.end():], True
    m = one(r'</head>', s, '</head>')
    return s[:m.start()] + CSS + '\n' + s[m.start():], True


FIXES = [
    ('rail-link', fix_rail_link), ('autoscroll', fix_autoscroll), ('tooltip', fix_tooltip),
    ('kpi-cards', fix_kpi_cards), ('trend-cards', fix_trend_cards), ('legend', fix_legend),
    ('portfolio', fix_portfolio), ('bars', fix_bars), ('deep-dive', fix_deep_dive),
    ('impact-column', fix_impact_column), ('top-bar', fix_top_bar), ('map-header', fix_map_header),
    ('long-list', fix_long_list), ('recruiter-cta', fix_recruiter_cta), ('er-decimal', fix_er_decimal),
    ('brief', fix_brief), ('contributors', fix_contributors), ('tutorial', fix_tutorial), ('no-list-cta', fix_no_list_cta), ('no-chat', fix_no_chat), ('map-log', fix_map_log), ('gallery', fix_gallery), ('disclaimer', fix_disclaimer), ('rail-menu', fix_rail_menu), ('css', fix_css),
    ('mxmap', fix_mxmap), ('rail-limit', fix_rail_limit), ('mxmap-css', fix_mxmap_css),
]


def main(argv):
    check = '--check' in argv
    args = [a for a in argv if not a.startswith('--')]
    path = Path(args[0]) if args else Path(__file__).resolve().parent.parent / 'PA-demo-v4.html'
    s = path.read_text(encoding='utf-8')
    failed = pending = 0
    for name, fix in FIXES:
        try:
            s, changed = fix(s)
        except Missing as e:
            print(f'  FAIL     {name:14} {e}')
            failed += 1
            continue
        status = ('missing' if check else 'applied') if changed else 'ok'
        pending += changed
        print(f'  {status:8} {name}')
    if check:
        print(f'{path.name}: {pending} fix(es) missing, {failed} anchor(s) not found')
        return 1 if pending or failed else 0
    if failed:
        print(f'{path.name}: not written, {failed} anchor(s) not found. Update the pattern in {Path(__file__).name}.')
        return 1
    if pending:
        path.write_text(s, encoding='utf-8')
    print(f'{path.name}: {pending} fix(es) applied')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
