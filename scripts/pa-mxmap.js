/* fx-mx: Performance Analyst's report sections, rebuilt on MX MAP's markup and
   class names (pages/PerformanceAnalysis/PerformanceAnalysis.jsx) so MX MAP's
   own CSS (scripts/pa-mxmap.css) styles them. Data still comes from the
   bundle's builders; the double-underscore UPPERCASE tokens are filled in by pa-fixups.py with
   the minified names of this build. Injected at module top level. */
const fxH=(t,p,...c)=>__K__.jsx(t,{...(p||{}),children:c.length>1?c:c[0]});
const fxMag=v=>new Intl.NumberFormat("en-US",{notation:"compact",maximumFractionDigits:1}).format(Number(v)||0);
const fxPct=(v,d=2)=>`${(Number(v)||0).toFixed(d)}%`;
const fxInitials=n=>String(n||"?").trim().split(/\s+/).slice(0,2).map(w=>w[0]).join("").toUpperCase();
const FX_QUAD={H_ER_L_X:"#31B03A",H_ER_H_X:"#0380FE",L_ER_L_X:"#FF7043",L_ER_H_X:"#777F8C"};
const FX_PP={"Photography & Film":"#515B74",Gaming:"#AB0F7A","Health & Fitness":"#1A9E1F","Music & Entertainment":"#0D958A","Food & Travel":"#FF7700","Fashion & Beauty":"#E91E63",Others:"#777F8C"};
const FX_TIER={Icon:"#6F29BA",Hero:"#FF4949",Macro:"#1F9A31",Micro:"#E07400"};
const FX_CHIP={Macro:"type-green",Micro:"type-yellow",Hero:"type-red",Icon:"type-purple",Mirror:"type-red",Firestarter:"type-purple",Sage:"type-yellow",Visionary:"type-green"};
const FX_TIERS=["Icon","Hero","Macro","Micro"];

function FxTip({text:e}){return fxH("span",{className:"mx-form-tooltip"},__K__.jsx(__LO__,{text:e,children:fxH("span",{className:"mx-form-tooltip__icon"},"icon")}))}
function FxTitle({title:e,info:t,children:a}){return fxH("div",{className:"content__dashboard__title-box type-align-center"},fxH("div",{className:"content__dashboard__title__left"},fxH("h2",{className:"content__dashboard__title mg-b0"},e,t?__K__.jsx(FxTip,{text:t}):null)),a)}
function FxSwitch({id:s,options:t,value:a,onChange:r}){const e=s+__A__.useId();return __K__.jsx("div",{className:"mx-form-switchbox",children:t.flatMap(n=>[__K__.jsx("input",{type:"radio",id:`${e}:${n}`,name:e,checked:a===n,onChange:()=>r(n)},"i"+n),__K__.jsx("label",{htmlFor:`${e}:${n}`,children:n},"l"+n)])})}
function FxAvatar({name:e}){const t=__NS__(e);return fxH("span",{className:"spa-list-avatar","aria-hidden":!0},t?__K__.jsx("img",{src:t,alt:""}):fxH("span",{className:"fx-mx-initials"},fxInitials(e)))}
function FxBar({value:e,engagement:t}){const a=Number.isFinite(Number(e))?Number(e):0;return fxH("span",{className:"spa-contrib__bar"+(t?" is-eng":"")},fxH("span",{className:"spa-contrib__track","aria-hidden":!0},__K__.jsx("span",{className:"spa-contrib__fill",style:{width:`${Math.max(0,Math.min(100,a))}%`}})),fxH("span",{className:"spa-contrib__label"},`${a.toFixed(1)}%`))}

// Report head: subsidiary · period, pager, and the data-through note.
function FxHead({scopeName:e,periodLabel:t,asOf:a,pager:r}){
  const n=(s,p,l)=>fxH("button",{type:"button",className:"mx-btn-white type-h32",disabled:!p,onClick:()=>r.onChange(r.index+s)},fxH("span",{className:"blind"},l),__K__.jsx("span",{className:"spa-chevron"+(s<0?" is-prev":""),"aria-hidden":!0}));
  return fxH("div",{className:"content__dashboard__title-box spa-report-head"},
    fxH("div",{className:"spa-report-head__title-row"},
      fxH("div",{className:"content__dashboard__title__left"},fxH("h1",{className:"content__dashboard__title mg-b0"},`${e} · ${t}`)),
      r?fxH("div",{className:"spa-pager","aria-label":"Subsidiary pages"},n(-1,r.index>0,"Previous subsidiary"),fxH("span",null,`${r.index+1} / ${r.total}`),n(1,r.index<r.total-1,"Next subsidiary")):null),
    fxH("div",{className:"spa-report-head__right"},fxH("p",{className:"spa-report-note"},fxH("strong",null,`Data through ${a?a.toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"}):"—"}`),fxH("span",null,"Manual monthly upload · approx. 2-week lag"))))}

// One record is one post. Per calendar month: influencers, posts, reach, engagement, E/R.
function fxMonths(e){const t=new Map;for(const a of e){if(!a.date)continue;const r=a.date.getFullYear()*12+a.date.getMonth();let n=t.get(r);n||(n={key:r,uids:new Set,posts:0,reach:0,eng:0},t.set(r,n)),n.uids.add(a.uid),n.posts+=1,n.reach+=a.reach,n.eng+=a.eng}return[...t.values()].sort((a,r)=>a.key-r.key).map(a=>({influencers:a.uids.size,posts:a.posts,reach:a.reach,eng:a.eng,er:a.reach>0?a.eng/a.reach*100:0}))}
const fxGrowth=(e,t)=>e>0?(t-e)/e*100:null;
const fxMom=e=>{const t=Number(e.toFixed(1));return`${t>=0?"+":"-"}${Math.abs(t)}%`};

function FxTrend({trend:e,target:t}){
  const a={fill:"#666666",fontSize:10,fontWeight:400},r={stroke:"#CECECE"},n=s=>{const p=Number(s).toFixed(2);return p.endsWith(".00")?`${Number(s).toFixed(0)}%`:`${p}%`};
  return fxH("div",{className:"mx-form-line-chart type-full"},__K__.jsx(__RC__,{width:"100%",height:"100%",children:__K__.jsxs(__LINECHART__,{data:e.points,margin:{top:5,right:5,left:5,bottom:5},accessibilityLayer:!1,children:[
    __K__.jsx(__GRID__,{strokeDasharray:"3 3",stroke:"#ccc"}),
    __K__.jsx(__XAXIS__,{dataKey:"month",height:20,axisLine:r,tickLine:r,tick:a}),
    __K__.jsx(__YAXIS__,{width:44,domain:[0,s=>Math.max(s,t??0,1)*1.15],tickFormatter:n,axisLine:r,tickLine:r,tick:a}),
    t!=null&&__K__.jsx(__REFLINE__,{y:t,stroke:"#FF4949",strokeWidth:2,strokeDasharray:"8 4",label:{value:`Target ${t.toFixed(2)}%`,position:"insideTopRight",fill:"#FF4949",fontSize:10,fontWeight:400}}),
    __K__.jsx(__TOOLTIP__,{cursor:r,content:__K__.jsx(__TRENDTIP__,{})}),
    __K__.jsx(__LINE__,{type:"monotone",dataKey:"er",stroke:"#0380FE",strokeWidth:2.5,dot:{r:2.7,fill:"#fff",strokeWidth:2},activeDot:{r:6},isAnimationActive:!1})]})}))}

// Brief Summary + Executive Summary (KPI cards show the latest month, with MoM).
function FxExec({analysisRecords:e,trendRecords:t,benchmark:a,onReviewPhotographyFilm:r}){
  const n=__A__,s=n.useMemo(()=>fxMonths(e),[e]),p=n.useMemo(()=>__NX__(t??e),[t,e]),
    l=n.useMemo(()=>{const g=__YTD__;if(!p||g==null)return p;const d=p.points.slice();return d[d.length-1]={...d[d.length-1],er:g},{...p,points:d,currentYtdEr:g}},[p]),
    m=n.useMemo(()=>l?__PX__({priorEr:l.priorCumulativeEr,latestEr:l.latestMonthEr,ytdEr:l.currentYtdEr}):[],[l]),
    u=s[s.length-1],g=s.length>1?s[s.length-2]:null,
    d=u?[["Active Influencers",u.influencers.toLocaleString("en-US"),g?(f=>`${f>=0?"+":""}${f.toLocaleString("en-US")}`)(u.influencers-g.influencers):null,g?u.influencers-g.influencers:0],
      ["Post Volume",u.posts.toLocaleString("en-US"),g&&fxGrowth(g.posts,u.posts)!=null?fxMom(fxGrowth(g.posts,u.posts)):null,g?u.posts-g.posts:0],
      ["Po.Reach",fxMag(u.reach),g&&fxGrowth(g.reach,u.reach)!=null?fxMom(fxGrowth(g.reach,u.reach)):null,g?u.reach-g.reach:0],
      ["Engagement",fxMag(u.eng),g&&fxGrowth(g.eng,u.eng)!=null?fxMom(fxGrowth(g.eng,u.eng)):null,g?u.eng-g.eng:0],
      ["E/R",fxPct(u.er),g?`${u.er-g.er>=0?"+":""}${(u.er-g.er).toFixed(3)}%p`:null,g?u.er-g.er:0]]:[];
  return fxH(__K__.Fragment,null,
    m.length>0?fxH("section",{className:"ai-brief-summary spa-brief-summary","aria-label":"Brief Summary"},
      fxH("div",{className:"ai-brief-summary__header"},fxH("span",{className:"ai-brief-summary__icon","aria-hidden":!0},__K__.jsx("img",{src:"resources/ai-summary.png",alt:""})),fxH("h2",null,"Brief Summary")),
      __K__.jsx(FxTut,{id:"brief"}),
      __K__.jsx("div",{className:"ai-brief-summary__surface",children:m.flatMap((f,T)=>[T>0?__K__.jsx("span",{className:"ai-brief-summary__divider","aria-hidden":!0},"d"+f.id):null,
        __K__.jsxs("article",{className:`ai-brief-summary__highlight ai-brief-summary__highlight--${T%2===0?"primary":"secondary"}`,children:[fxH("h3",null,f.title),fxH("p",null,f.evidence),f.id==="L-02"?fxH("button",{type:"button",className:"spa-rule__cta",onClick:r},"Review Passion Point contribution →"):null]},f.id)])})):null,
    fxH("section",{className:"content__dashboard"},
      __K__.jsx(FxTitle,{title:"Executive Summary",info:"KPI cards show the latest month only, using the same KPI values as Influencer Marketing > Overview page. The Cumulative E/R Trend below shows E/R accumulated from January to each month."}),
      __K__.jsx(FxTut,{id:"exec"}),
      __K__.jsx("div",{className:"content__influencer-highlight-box type-num5 spa-executive-metrics",children:d.map(([f,T,v,w])=>__K__.jsxs("div",{className:"content__influencer-highlight-box__item",children:[fxH("div",{className:"content__influencer-highlight-box__title"},f),fxH("div",{className:"content__influencer-highlight-box__value"},T),v!=null?fxH("p",{className:"spa-delta"},fxH("span",{className:`spa-delta__badge ${w>=0?"is-up":"is-down"}`},v),fxH("span",{className:"spa-delta__text"},"MoM")):null]},f))}),
      fxH("div",{className:"spa-trend-panel"},
        fxH("h3",{className:"mx-form-line-chart__title"},"Cumulative E/R Trend"),
        l?fxH("div",{className:"spa-trend-chart"},__K__.jsx(FxTrend,{trend:l,target:a})):null,
        __K__.jsx("div",{className:"content__influencer-highlight-box type-num2 spa-trend-cards mg-t0",children:[["Prior Cumulative",l?.priorCumulativeEr],["Current YTD",l?.currentYtdEr]].map(([f,T])=>__K__.jsxs("div",{className:"content__influencer-highlight-box__item",children:[fxH("div",{className:"content__influencer-highlight-box__title"},f),fxH("div",{className:"content__influencer-highlight-box__value"},T==null?"—":fxPct(T))]},f))}))))}

// Portfolio Overview: MX MAP's grid, as a plain CSS grid with its sizes and colours.
function FxPortfolio({analysisRecords:e,selectedGroup:t,onSelectGroup:a}){
  const r=__A__,[n,s]=r.useState("Passion Point"),p={"Passion Point":"ppoint",Tier:"tier",Channel:"channel"}[n],
    l=r.useMemo(()=>n==="Tier"?__H4__(e,[...__NL__],m=>m.tier):n==="Channel"?__H4__(e,[...__BA__],m=>m.channel):__H4__(e,[...__DA__],m=>m.pp),[n,e]);
  return fxH("section",{id:"portfolio-overview",tabIndex:-1,className:"content__dashboard spa-portfolio","aria-label":"Portfolio Overview"},
    __K__.jsx(FxTitle,{title:"Portfolio Overview",info:"Portfolio composition explains performance. Contribution is each group's share of cumulative Po.Reach and Engagement from January to the selected month. Select a group to filter the Influencer Long-list.",children:__K__.jsx(FxSwitch,{id:"pa-portfolio",options:["Passion Point","Tier","Channel"],value:n,onChange:s})}),
    __K__.jsx(FxTut,{id:"portfolio"}),
    fxH("div",{className:"spa-chart-legend"},fxH("span",{className:"spa-chart-legend__item is-reach"},__K__.jsx("span",{className:"spa-chart-legend__marker","aria-hidden":!0}),"Po.Reach Contribution"),fxH("span",{className:"spa-chart-legend__item is-engagement"},__K__.jsx("span",{className:"spa-chart-legend__marker","aria-hidden":!0}),"Engagement Contribution"),fxH("span",{className:"spa-chart-legend__note"},"KPI = E/R")),
    fxH("div",{className:"mx-form-grid type-b-bottom type-hover-row spa-portfolio-grid"},fxH("div",{className:"fx-mx-grid",role:"table"},
      __K__.jsx("div",{className:"fx-mx-grid__head",role:"row",children:["Group","No. of\nInfluencers","Posts","Po.Reach\nContribution","Engagement\nContribution","E/R"].map(m=>__K__.jsx("span",{role:"columnheader",children:m},m))}),
      l.map(m=>__K__.jsxs("div",{role:"row",tabIndex:0,className:"fx-mx-grid__row"+(t?.axis===p&&t.key===m.key?" spa-selected-row":""),onClick:()=>a(p,m.key),onKeyDown:u=>{u.key==="Enter"&&a(p,m.key)},children:[
        fxH("span",{role:"cell"},fxH("span",{className:"spa-group-name"},m.label)),
        fxH("span",{role:"cell","data-field":"influencers"},m.influencers.toLocaleString("en-US")),
        fxH("span",{role:"cell","data-field":"posts"},m.posts.toLocaleString("en-US")),
        fxH("span",{role:"cell",className:"pd-l0"},__K__.jsx(FxBar,{value:m.reachContribution})),
        fxH("span",{role:"cell",className:"pd-l0"},__K__.jsx(FxBar,{value:m.engContribution,engagement:!0})),
        fxH("span",{role:"cell","data-field":"er"},fxPct(m.er))]},m.key)))),
    fxH("p",{className:"content__dashboard__sub-title mg-t12 mg-b0"},"Main visual = contribution only. Influencer count and posts provide scale/activity context. Archetype cross-analysis is intentionally excluded here."))}

// Log axis: padded positive range, powers of ten as ticks (the range ends when it spans under two).
function fxLogAxis(e){const t=e.filter(n=>Number.isFinite(n)&&n>0);if(!t.length)return null;const a=[Math.min(...t)*.85,Math.max(...t)*1.15],r=[];for(let n=Math.ceil(Math.log10(a[0]));n<=Math.floor(Math.log10(a[1]));n++)r.push(10**n);return{domain:a,ticks:r.length>1?r:a}}
function FxDot({cx:e,cy:t,payload:a}){return __K__.jsxs("g",{style:{cursor:"pointer"},children:[__K__.jsx("circle",{cx:e,cy:t,r:5.64,fill:a.color}),__K__.jsx("text",{x:e,y:t+17,fill:a.color,fontSize:"9px",fontWeight:"700",textAnchor:"middle",style:{pointerEvents:"none",userSelect:"none"},children:a.label})]})}
function FxMapTip({active:e,payload:t}){const a=e&&t&&t.length?t[0].payload:null;return a?fxH("div",{className:"mx-form-scatter-chart__tooltip"},fxH("span",null,a.label),fxH("p",null,`E/R : ${fxPct(a.y)}`,__K__.jsx("br",{}),`Po.Reach : ${fxMag(a.x)}`)):null}

function FxMap({analysisRecords:e,analysisRows:t,onSelectGroup:a,selectedInfluencerUid:r,onSelectInfluencer:n,dim:s,onDimChange:p}){
  const l=__A__,m=l.useMemo(()=>{const v=s==="Tier"?__FT__(e,[...__NL__],w=>w.tier):s==="Passion Point"?__FT__(e,[...__DA__],w=>w.pp):__XO__(t),w=s==="Passion Point"?FX_PP:s==="Tier"?FX_TIER:null;return{...v,points:v.points.filter(I=>I.x>0&&I.y>0).map(I=>({...I,color:w?.[I.key]??FX_QUAD[I.quadrant]}))}},[s,e,t]),
    u=fxLogAxis(m.points.map(v=>v.x)),g=fxLogAxis(m.points.map(v=>v.y)),d=s==="Tier"?"tier":s==="Passion Point"?"ppoint":null,
    f={fontSize:"10px",fill:"#777F8C",fontFamily:"var(--mm-font-body)",fontWeight:"500"},T={stroke:"#CECECE",strokeWidth:2};
  return fxH("section",{className:"content__dashboard mg-b0 spa-map-section","aria-label":"Influencer Contribution Map"},
    __K__.jsx(FxTitle,{title:"Influencer Contribution Map",info:"Po.Reach and E/R use logarithmic scales; median lines split the plotted points into four quadrants.",children:__K__.jsx(FxSwitch,{id:"pa-map",options:["Influencer","Passion Point","Tier"],value:s,onChange:p})}),
    __K__.jsx(FxTut,{id:"map"}),
    __K__.jsx("div",{className:"spa-chart-legend",children:s==="Influencer"?[["is-q1","High E/R · Low Po.Reach"],["is-q2","High E/R · High Po.Reach"],["is-q3","Low E/R · Low Po.Reach"],["is-q4","Low E/R · High Po.Reach"]].map(([v,w])=>__K__.jsxs("span",{className:"spa-chart-legend__item "+v,children:[__K__.jsx("span",{className:"spa-chart-legend__marker","aria-hidden":!0}),w]},v)):m.points.map(v=>__K__.jsxs("span",{className:"spa-chart-legend__item",children:[__K__.jsx("span",{className:"spa-chart-legend__marker","aria-hidden":!0,style:{backgroundColor:v.color}}),v.label]},v.key))}),
    m.points.length>0&&u&&g?fxH("div",{className:"mx-form-scatter-chart type-action-guide"},fxH("div",{className:"scroll-box"},__K__.jsx(__RC__,{width:"100%",height:"100%",children:__K__.jsxs(__SCATTERCHART__,{margin:{top:15,right:15,bottom:20,left:20},accessibilityLayer:!1,children:[
      __K__.jsx(__GRID__,{strokeDasharray:"3 3",vertical:!0,stroke:"#CECECE"}),
      __K__.jsx(__REFLINE__,{x:m.xMedian}),__K__.jsx(__REFLINE__,{y:m.yMedian}),
      __K__.jsx(__XAXIS__,{type:"number",dataKey:"x",domain:u.domain,scale:"log",ticks:u.ticks,allowDataOverflow:!0,tickFormatter:fxMag,tick:f,label:{value:"Po.Reach",position:"insideBottom",offset:-10,fill:"#777F8C"},axisLine:T,tickLine:{stroke:"#CECECE"}}),
      __K__.jsx(__YAXIS__,{type:"number",dataKey:"y",domain:g.domain,scale:"log",ticks:g.ticks,allowDataOverflow:!0,tickFormatter:v=>`${new Intl.NumberFormat("en-US",{maximumSignificantDigits:3}).format(v)}%`,tick:f,label:{value:"E/R",position:"insideLeft",offset:-5,style:{textAnchor:"middle"},fill:"#777F8C"},axisLine:T,tickLine:{stroke:"#CECECE"}}),
      __K__.jsx(__TOOLTIP__,{isAnimationActive:!1,cursor:{strokeDasharray:"5 5",stroke:"#cbd5e1"},content:__K__.jsx(FxMapTip,{}),wrapperStyle:{pointerEvents:"none"}}),
      __K__.jsx(__SCATTER__,{data:m.points,isAnimationActive:!1,onClick:v=>{d?a(d,v.key):n(r===v.key?null:v.key)},shape:v=>__K__.jsx(FxDot,{...v})})]})}))):fxH("div",{className:"content__influencer-highlight-box__item"},fxH("p",{className:"content__dashboard__sub-title mg-b0"},"No matrix data.")),
    fxH("p",{className:"content__dashboard__sub-title mg-t12 mg-b0"},(s==="Influencer"?"Click a point to open its Influencer Long-list row.":"Click a point to filter the Influencer Long-list by group.")+" Logarithmic axes show only positive Po.Reach and E/R values."))}

// Influencer Deep Dive: two collapsible comparison tables, rows without rank numbers.
function FxCompare({label:e,metricLabel:t,empty:a,children:r}){return fxH("div",{className:"spa-compare__viewport"},fxH("div",{className:"spa-compare__table"},fxH("div",{className:"spa-compare__head"},fxH("span",null,fxH("span",{className:"spa-compare__heading-text",title:e},e)),fxH("span",null,fxH("span",{className:"spa-compare__heading-text",title:t},t))),a?fxH("p",{className:"spa-empty"},"There is no data to analyze."):__K__.jsx("ul",{className:"spa-compare__list",children:r})))}
function FxWho({row:e,bind:t}){return fxH(__K__.Fragment,null,fxH("span",{className:"pa-row-focus"},__K__.jsx(FxAvatar,{name:e.name})),__K__.jsx("button",{type:"button",className:"spa-compare__name",title:e.name,"aria-haspopup":"dialog",...t(e.uid),children:e.name}))}
function FxDive({analysisRecords:e,analysisRows:t,onFocus:a}){
  const r=__A__,n=r.useMemo(()=>__XW__(e),[e]),s=n.filter(f=>f.impact<0).slice(0,5),p=[...n].filter(f=>f.impact>0).reverse().slice(0,5),
    l=r.useMemo(()=>t.reduce((f,T)=>f+T.eng,0),[t]),m=r.useMemo(()=>[...t].filter(f=>f.reach>0).sort((f,T)=>T.reach-f.reach).slice(0,5),[t]),u=r.useMemo(()=>[...t].filter(f=>f.eng>0).sort((f,T)=>T.eng-f.eng).slice(0,5),[t]),
    {bind:g,portal:d}=__NO__(e,t),
    f=(T,v,w)=>__K__.jsx(FxCompare,{label:v,metricLabel:"Impact on E/R",empty:T.length===0,children:T.map(I=>__K__.jsx("li",{onClick:()=>a(I.uid,w),children:fxH("div",{className:"spa-compare__row"},fxH("span",{className:"spa-compare__identity"},__K__.jsx(FxWho,{row:I,bind:g})),fxH("strong",{className:`spa-compare__value ${I.impact>0?"is-up":"is-down"}`},`${I.impact>0?"+":""}${I.impact.toFixed(3)}%p`))},I.uid))}),
    T=(v,w,I,O)=>__K__.jsx(FxCompare,{label:I,metricLabel:O,empty:v.length===0,children:v.map(K=>{const F=l>0?K.eng/l*100:0;return __K__.jsx("li",{onClick:()=>a(K.uid),children:fxH("div",{className:"spa-compare__row"},fxH("span",{className:"spa-contrib__main"},fxH("span",{className:"spa-contrib__who"},__K__.jsx(FxWho,{row:K,bind:g})),__K__.jsx(FxBar,{value:w==="reach"?K.reachShare:F,engagement:w!=="reach"})),fxH("span",{className:"spa-contrib__other is-centered"},fxPct(w==="reach"?F:K.reachShare,1)))},K.uid)})}),
    v=(w,I,O)=>__K__.jsxs("details",{className:"spa-deep-details",open:!0,children:[fxH("summary",{className:"content__influencer-highlight-box__headline spa-deep-subtitle"},fxH("span",{className:"spa-deep-subtitle__label"},w,fxH("span",{onClick:K=>K.preventDefault()},__K__.jsx(FxTip,{text:I}))),__K__.jsx("span",{className:"spa-deep-subtitle__icon","aria-hidden":!0})),__K__.jsx("div",{className:"spa-compare",children:O})]});
  return fxH("section",{className:"content__dashboard mg-b0 spa-deep-dive"},
    __K__.jsx(FxTitle,{title:"Influencer Deep Dive"}),
    __K__.jsx(FxTut,{id:"dive"}),
    v("Performance Change","Influencers that moved the latest monthly update of cumulative E/R",[f(s,"Negative E/R Impact","down"),f(p,"Positive E/R Impact","up")]),
    v("Performance Contributors","Top contributors are ranked separately by Po.Reach and Engagement; both contribution shares remain visible",[T(m,"reach","Top Po.Reach Contributors","Engagement Contribution"),T(u,"engagement","Top Engagement Contributors","Po.Reach Contribution")]),
    d)}

// Influencer Long-list: MX MAP's grid columns, 80px rows, sort on Po.Reach / E/R, tier filter on the Tier header.
function FxList({records:e,scopeLabel:t,focusUid:a,topSlot:r,scopeRecords:n,scopeRows:s,group:p,onClear:l}){
  const m=__A__,[u,g]=m.useState({field:"reach",dir:"desc"}),[d,f]=m.useState("All"),[T,v]=m.useState(!1),{bind:w,portal:I}=__NO__(n,s),O=m.useRef(new Map),
    K=m.useMemo(()=>{const E=__U4__(e).filter(L=>d==="All"||L.tier===d),L=u.dir==="asc"?1:-1;return E.sort((x,H)=>(x[u.field]-H[u.field])*L||H.reach-x.reach)},[e,d,u]),
    F=p?.axis==="ppoint"?p.key:null,U=[!F&&p?t:null,d!=="All"?d:null].filter(Boolean),
    E=(L,x)=>__K__.jsx("button",{type:"button",className:"fx-mx-sort"+(u.field===L?" is-"+u.dir:""),onClick:()=>g(H=>({field:L,dir:H.field===L&&H.dir==="desc"?"asc":"desc"})),children:x});
  return m.useEffect(()=>{a&&O.current.get(a)?.scrollIntoView({behavior:"auto",block:"center"})},[a,K]),
    fxH(__K__.Fragment,null,r,fxH("section",{className:"content__dashboard mg-b0 spa-long-list"},
      __K__.jsx(FxTitle,{title:F?`Influencer Long-list (${F})`:"Influencer Long-list",children:F?fxH("button",{type:"button",className:"mx-btn-black type-h32 spa-clear-passion-point",onClick:l},"Clear Passion Point"):null}),
      __K__.jsx(FxTut,{id:"list"}),
      U.length>0?fxH("div",{className:"content__dashboard__sub-title mg-b16 spa-list-scope"},fxH("span",null,U.join(" · ")),fxH("button",{type:"button",className:"mx-form-blueline",onClick:F||!p?()=>f("All"):()=>{f("All"),l()}},F||!p?"Clear Tier":"Clear selection")):null,
      fxH("div",{className:"mx-form-grid type-b-bottom type-hover-row spa-grid"},fxH("div",{className:"fx-mx-grid",role:"table","aria-label":"Influencer Long-list"},
        fxH("div",{className:"fx-mx-grid__head",role:"row"},fxH("span",{role:"columnheader"},"#"),fxH("span",{role:"columnheader"},"Influencer"),fxH("span",{role:"columnheader"},"Archetype"),
          fxH("span",{role:"columnheader",className:"fx-mx-tier"},fxH("button",{type:"button",className:"spa-tier-filter"+(d!=="All"?" is-active":""),"aria-haspopup":"menu","aria-expanded":T,onClick:()=>v(L=>!L)},"Tier ",__K__.jsx("span",{className:"spa-chevron is-down","aria-hidden":!0})),
            T?__K__.jsx("div",{className:"fx-mx-menu",role:"menu","aria-label":"Tier filter",children:["All",...FX_TIERS].map(L=>__K__.jsx("button",{type:"button",role:"menuitem",className:d===L?"is-selected":"",onClick:()=>{f(L),v(!1)},children:L},L))}):null),
          fxH("span",{role:"columnheader"},E("reach","Po.\nReach")),fxH("span",{role:"columnheader"},E("er","E/R"))),
        K.length===0?fxH("p",{className:"spa-empty"},"No influencer data."):K.map((L,x)=>__K__.jsxs("div",{role:"row",ref:H=>{H?O.current.set(L.uid,H):O.current.delete(L.uid)},className:"fx-mx-grid__row"+(L.uid===a?" spa-selected-row":""),...w(L.uid),children:[
          fxH("span",{role:"cell","data-field":"rank"},x+1),
          fxH("span",{role:"cell"},fxH("span",{className:"spa-influencer-cell"},__K__.jsx(FxAvatar,{name:L.name}),fxH("span",{className:"spa-influencer-name"},fxH("strong",{title:L.name},L.name||"(no name)"),fxH("small",null,`${L.posts} posts · ${L.sub}`)))),
          fxH("span",{role:"cell",className:"fx-mx-center"},fxH("span",{className:`grid-influencer-tier-cell ${L.archetype?FX_CHIP[L.archetype]||"":"type-gray"}`},L.archetype||"N/A")),
          fxH("span",{role:"cell",className:"fx-mx-center"},fxH("span",{className:`grid-influencer-tier-cell ${FX_CHIP[L.tier]||""}`},L.tier)),
          fxH("span",{role:"cell"},fxH("div",{className:"spa-reach"},fxH("strong",null,fxMag(L.reach)),fxH("small",null,fxPct(L.reachShare,1)))),
          fxH("span",{role:"cell","data-field":"er"},fxPct(L.er))]},L.uid)))),
      I))}
