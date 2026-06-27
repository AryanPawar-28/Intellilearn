import streamlit as st
import json
from utils.mindmap_generator import generate_mindmap_data


def render_mindmap_page():
    st.markdown("""
    <div class="page-header">
        <span class="page-icon">🧠</span>
        <div>
            <h1 class="page-title">Mind Map</h1>
            <p class="page-subtitle">Visual knowledge structure — click any node to explore details</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.index is None or st.session_state.text_chunks is None:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📄</div>
            <h3>No Document Loaded</h3>
            <p>Upload and process a PDF from the <strong>Chat + PDF</strong> page first.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    if "mindmap_data" not in st.session_state:
        st.session_state.mindmap_data = None

    col1, col2 = st.columns([3, 1])
    with col1:
        depth = st.selectbox(
            "Map Depth",
            ["2 levels (Overview)", "3 levels (Detailed)", "4 levels (Deep Dive)"],
            index=1
        )
        depth_num = int(depth[0])
    with col2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        gen_btn = st.button("🧠 Generate Mind Map", use_container_width=True, type="primary")

    if gen_btn:
        with st.spinner("🔍 Mapping your document's knowledge..."):
            data = generate_mindmap_data(st.session_state.text_chunks, depth=depth_num)
            if not data:
                st.error("Failed to generate mind map. Please try again.")
                return
            st.session_state.mindmap_data = data
        st.success("✅ Mind map generated! Click any node to see its details.")

    if st.session_state.mindmap_data:
        data      = st.session_state.mindmap_data
        data_json = json.dumps(data)

        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  *{{ margin:0;padding:0;box-sizing:border-box; }}
  body{{ background:#0d1117;font-family:'Segoe UI',sans-serif;overflow:hidden;width:100%;height:100vh; }}
  #canvas{{ width:100%;height:100vh;cursor:grab;position:relative;overflow:hidden; }}
  #canvas:active{{ cursor:grabbing; }}
  svg{{ width:100%;height:100%;user-select:none; }}

  .node-center{{ fill:#00c8ff;filter:drop-shadow(0 0 14px #00c8ff99); }}
  .node-l1{{ fill:#ff6b9d;filter:drop-shadow(0 0 10px #ff6b9d88); }}
  .node-l2{{ fill:#a855f7;filter:drop-shadow(0 0 8px #a855f788); }}
  .node-l3{{ fill:#22c55e;filter:drop-shadow(0 0 6px #22c55e77); }}
  .node-l4{{ fill:#f59e0b;filter:drop-shadow(0 0 5px #f59e0b77); }}
  .node-clickable{{ cursor:pointer; transition:opacity 0.15s; }}
  .node-clickable:hover{{ opacity:0.8; }}

  .link{{ stroke:#1e3050;stroke-width:1.8;fill:none; }}
  .link-l1{{ stroke:#ff6b9d33;stroke-width:2.2; }}
  .link-l2{{ stroke:#a855f733;stroke-width:1.6; }}
  .link-l3{{ stroke:#22c55e22;stroke-width:1.2; }}

  .label{{ fill:#e2e8f0;text-anchor:middle;dominant-baseline:central;pointer-events:none;font-weight:600; }}

  /* ── Detail Panel ── */
  #detail-panel{{
    position:absolute;top:16px;left:16px;width:280px;
    background:rgba(10,14,22,0.97);
    border:1px solid rgba(0,200,255,0.3);
    border-radius:14px;padding:20px;display:none;z-index:30;
    backdrop-filter:blur(16px);
    box-shadow:0 12px 48px rgba(0,0,0,0.7),0 0 0 1px rgba(0,200,255,0.08);
    animation:panelIn 0.18s ease;
  }}
  @keyframes panelIn{{ from{{opacity:0;transform:translateY(-8px)}} to{{opacity:1;transform:translateY(0)}} }}

  .panel-close{{
    position:absolute;top:12px;right:14px;background:none;border:none;
    color:#475569;font-size:15px;cursor:pointer;line-height:1;padding:2px 4px;
    border-radius:4px;transition:color 0.15s;
  }}
  .panel-close:hover{{ color:#e2e8f0;background:rgba(255,255,255,0.06); }}

  .panel-breadcrumb{{
    font-size:0.65rem;color:#475569;margin-bottom:8px;
    text-transform:uppercase;letter-spacing:0.06em;
  }}
  .panel-title{{
    font-size:1rem;font-weight:800;color:#00c8ff;
    margin-bottom:14px;padding-bottom:10px;
    border-bottom:1px solid rgba(0,200,255,0.15);
    line-height:1.3;
  }}
  .panel-section-label{{
    font-size:0.65rem;color:#64748b;text-transform:uppercase;
    letter-spacing:0.08em;margin-bottom:8px;font-weight:700;
  }}
  .panel-list{{ list-style:none;padding:0; }}
  .panel-list li{{
    font-size:0.82rem;color:#cbd5e1;
    padding:7px 0 7px 18px;
    border-bottom:1px solid rgba(255,255,255,0.04);
    position:relative;line-height:1.45;
  }}
  .panel-list li:last-child{{ border-bottom:none; }}
  .panel-list li::before{{
    content:'';position:absolute;left:0;top:14px;
    width:8px;height:8px;border-radius:50%;
  }}
  .panel-list.pink li::before{{ background:#ff6b9d; }}
  .panel-list.purple li::before{{ background:#a855f7; }}
  .panel-list.green li::before{{ background:#22c55e; }}
  .panel-list.amber li::before{{ background:#f59e0b; }}

  .panel-sub-badge{{
    display:inline-block;margin-left:6px;
    font-size:0.62rem;color:#475569;
    background:rgba(255,255,255,0.06);
    border-radius:4px;padding:1px 5px;
  }}
  .panel-leaf{{
    font-size:0.78rem;color:#475569;font-style:italic;text-align:center;
    padding:10px 0;
  }}
  .panel-depth-tag{{
    display:inline-block;margin-top:12px;
    font-size:0.63rem;font-weight:700;letter-spacing:0.06em;
    padding:3px 8px;border-radius:4px;
  }}
  .tag-l1{{ background:rgba(255,107,157,0.15);color:#ff6b9d; }}
  .tag-l2{{ background:rgba(168,85,247,0.15);color:#a855f7; }}
  .tag-l3{{ background:rgba(34,197,94,0.15);color:#22c55e; }}
  .tag-l4{{ background:rgba(245,158,11,0.15);color:#f59e0b; }}

  /* Legend */
  .legend{{
    position:absolute;top:16px;right:16px;
    background:rgba(10,14,22,0.92);
    border:1px solid #1e293b;border-radius:10px;
    padding:12px 16px;font-size:11px;color:#94a3b8;z-index:10;
  }}
  .legend-item{{ display:flex;align-items:center;gap:8px;margin-bottom:5px; }}
  .legend-dot{{ width:10px;height:10px;border-radius:50%;flex-shrink:0; }}
  .legend-tip{{
    margin-top:9px;padding-top:8px;border-top:1px solid #1e293b;
    font-size:10px;color:#475569;font-style:italic;
  }}

  /* Controls */
  .controls{{
    position:absolute;bottom:18px;right:16px;
    display:flex;gap:8px;z-index:10;
  }}
  .ctrl-btn{{
    background:#1e293b;border:1px solid #334155;
    color:#94a3b8;padding:7px 15px;
    border-radius:8px;cursor:pointer;font-size:13px;
    transition:all 0.18s;font-weight:600;
  }}
  .ctrl-btn:hover{{ background:#334155;color:#e2e8f0; }}
</style>
</head>
<body>
<div id="canvas">
  <svg id="svg"></svg>

  <div id="detail-panel">
    <button class="panel-close" onclick="closePanel()">✕</button>
    <div class="panel-breadcrumb" id="panel-breadcrumb"></div>
    <div class="panel-title" id="panel-title"></div>
    <div class="panel-section-label" id="panel-section-label"></div>
    <ul class="panel-list" id="panel-list"></ul>
    <div class="panel-leaf" id="panel-leaf" style="display:none">Leaf node — no sub-topics</div>
    <div id="panel-depth-tag"></div>
  </div>

  <div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background:#00c8ff"></div>Central Topic</div>
    <div class="legend-item"><div class="legend-dot" style="background:#ff6b9d"></div>Main Branches</div>
    <div class="legend-item"><div class="legend-dot" style="background:#a855f7"></div>Sub-topics</div>
    <div class="legend-item"><div class="legend-dot" style="background:#22c55e"></div>Details</div>
    <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div>Deep Points</div>
    <div class="legend-tip">👆 Click any node for details</div>
  </div>

  <div class="controls">
    <button class="ctrl-btn" onclick="zoom(1.2)">＋</button>
    <button class="ctrl-btn" onclick="zoom(0.8)">－</button>
    <button class="ctrl-btn" onclick="resetView()">Reset</button>
  </div>
</div>

<script>
const data = {data_json};
const svgEl = document.getElementById('svg');
const W = window.innerWidth, H = window.innerHeight;
let scale=1, tx=0, ty=0, dragging=false, lastX, lastY;
const nodeMap = {{}};

const COLORS  = ['#00c8ff','#ff6b9d','#a855f7','#22c55e','#f59e0b'];
const RADII   = [56, 44, 34, 26, 20];
const BR      = [0, 190, 140, 105, 78];   // branch radius per level
const FSIZES  = [14, 12, 11, 10, 9];
const LABEL_COLORS = ['#0d1117','#fff','#f0e6ff','#d1fae5','#fef9c3'];
const LIST_CLASSES = ['','pink','purple','green','amber'];
const TAG_CLASSES  = ['','tag-l1','tag-l2','tag-l3','tag-l4'];
const LEVEL_NAMES  = ['Root','Main Branch','Sub-topic','Detail','Deep Point'];

function wrapText(t, maxCh) {{
  if(t.length<=maxCh) return [t];
  const words=t.split(' '); const lines=[]; let ln='';
  for(const w of words){{
    const test=(ln+' '+w).trim();
    if(test.length<=maxCh) ln=test;
    else{{ if(ln) lines.push(ln); ln=w; }}
  }}
  if(ln) lines.push(ln);
  return lines.length?lines:[t];
}}

function buildTree(node, x, y, lvl, aStart, aEnd, px, py, ancestors, nid) {{
  const r  = RADII[Math.min(lvl,4)];
  const id = nid||'root';
  const children = node.children||[];

  // Link
  if(px!==null){{
    const path=`M ${{px}} ${{py}} C ${{(px+x)/2}} ${{py}} ${{(px+x)/2}} ${{y}} ${{x}} ${{y}}`;
    const ln=document.createElementNS('http://www.w3.org/2000/svg','path');
    ln.setAttribute('d',path);
    ln.setAttribute('class','link'+(lvl<=3?' link-l'+lvl:''));
    svgEl.appendChild(ln);
  }}

  // Circle
  const circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
  circle.setAttribute('cx',x); circle.setAttribute('cy',y); circle.setAttribute('r',r);
  circle.setAttribute('class','node-l'+Math.min(lvl,4)+(lvl>0?' node-clickable':'').replace('node-l0','node-center'));
  if(lvl>0){{
    circle.addEventListener('mouseenter',()=>circle.setAttribute('r',r+4));
    circle.addEventListener('mouseleave',()=>circle.setAttribute('r',r));
    circle.addEventListener('click',(e)=>{{ e.stopPropagation(); showPanel(id); }});
  }}
  svgEl.appendChild(circle);

  // Label
  const maxCh = lvl===0?13:(lvl===1?10:8);
  const lines  = wrapText(node.name||'',maxCh);
  const lh     = FSIZES[Math.min(lvl,4)]+3;
  const startY = y-((lines.length-1)*lh)/2;
  lines.forEach((ln,i)=>{{
    const t=document.createElementNS('http://www.w3.org/2000/svg','text');
    t.setAttribute('x',x); t.setAttribute('y',startY+i*lh);
    t.setAttribute('class','label');
    t.setAttribute('font-size',FSIZES[Math.min(lvl,4)]);
    t.setAttribute('fill',LABEL_COLORS[Math.min(lvl,4)]);
    t.setAttribute('font-weight',lvl<=1?'700':'600');
    t.setAttribute('pointer-events','none');
    t.textContent=ln;
    svgEl.appendChild(t);
  }});

  // Register
  if(lvl>0) nodeMap[id]={{ node, lvl, ancestors:[...ancestors] }};

  // Children
  if(children.length>0){{
    const spread=aEnd-aStart;
    const step=spread/children.length;
    const br=BR[Math.min(lvl+1,4)];
    children.forEach((child,i)=>{{
      const a=aStart+step*i+step/2;
      const nx=x+Math.cos(a)*br, ny=y+Math.sin(a)*br;
      buildTree(child,nx,ny,lvl+1,a-step/2,a+step/2,x,y,[...ancestors,node.name],id+'_'+i);
    }});
  }}
}}

function renderMap(){{
  svgEl.innerHTML='';
  svgEl.setAttribute('viewBox',`${{-W/2+tx}} ${{-H/2+ty}} ${{W/scale}} ${{H/scale}}`);
  buildTree(data,0,0,0,-Math.PI,Math.PI,null,null,[],'root');
}}

function showPanel(id){{
  const reg=nodeMap[id]; if(!reg) return;
  const {{node,lvl,ancestors}}=reg;
  const children=node.children||[];

  document.getElementById('panel-breadcrumb').textContent=
    ancestors.length? ancestors.join(' › ')+' › '+node.name : node.name;

  document.getElementById('panel-title').textContent=node.name;

  const list=document.getElementById('panel-list');
  const leaf=document.getElementById('panel-leaf');
  const secLabel=document.getElementById('panel-section-label');
  const depthTag=document.getElementById('panel-depth-tag');

  list.innerHTML=''; leaf.style.display='none';
  list.className='panel-list '+(LIST_CLASSES[Math.min(lvl,4)]||'');

  if(children.length===0){{
    secLabel.textContent='';
    leaf.style.display='block';
  }} else {{
    secLabel.textContent=children.length+' sub-topics';
    children.forEach(c=>{{
      const li=document.createElement('li');
      li.textContent=c.name;
      const sub=c.children||[];
      if(sub.length>0){{
        const badge=document.createElement('span');
        badge.className='panel-sub-badge';
        badge.textContent='+'+sub.length;
        li.appendChild(badge);
      }}
      list.appendChild(li);
    }});
  }}

  depthTag.innerHTML=`<span class="panel-depth-tag ${{TAG_CLASSES[Math.min(lvl,4)]}}">${{LEVEL_NAMES[Math.min(lvl,4)]}}</span>`;
  document.getElementById('detail-panel').style.display='block';
}}

function closePanel(){{
  document.getElementById('detail-panel').style.display='none';
}}

function zoom(f){{ scale=Math.max(0.2,Math.min(4,scale*f)); renderMap(); }}
function resetView(){{ scale=1;tx=0;ty=0;renderMap(); }}

const canvas=document.getElementById('canvas');
canvas.addEventListener('mousedown',e=>{{ dragging=true;lastX=e.clientX;lastY=e.clientY; }});
document.addEventListener('mousemove',e=>{{
  if(!dragging) return;
  tx-=(e.clientX-lastX)/scale; ty-=(e.clientY-lastY)/scale;
  lastX=e.clientX; lastY=e.clientY; renderMap();
}});
document.addEventListener('mouseup',()=>dragging=false);
canvas.addEventListener('wheel',e=>{{ e.preventDefault(); zoom(e.deltaY<0?1.1:0.9); }},{{passive:false}});

renderMap();
</script>
</body>
</html>"""

        st.components.v1.html(html_content, height=620, scrolling=False)

        st.markdown("---")
        st.markdown("### 📝 Topic Outline")
        render_outline(data, 0)


def render_outline(node, level):
    indent = "&nbsp;" * (level * 4)
    icons  = ["🎯","📌","🔹","▫️","·"]
    sizes  = ["1.1rem","1rem","0.95rem","0.9rem","0.85rem"]
    colors = ["#00c8ff","#ff6b9d","#a855f7","#22c55e","#f59e0b"]
    icon   = icons[min(level,4)]
    size   = sizes[min(level,4)]
    weight = "700" if level==0 else ("600" if level==1 else "400")
    color  = colors[min(level,4)]
    st.markdown(
        f'<p style="margin:2px 0;font-size:{size};font-weight:{weight};color:{color}">'
        f'{indent}{icon} {node.get("name","")}</p>',
        unsafe_allow_html=True
    )
    for child in node.get("children",[]):
        render_outline(child, level+1)