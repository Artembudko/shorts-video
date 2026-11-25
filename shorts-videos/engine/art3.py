import math, random
from art import *
import art
art.PAL["official"]=dict(tunic=("#f4efe2","#d8d0bb"),pants=("#ebe5d4","#cbc2ab"),hat=("#efe3c4","#c8b98f"),skin=("#f4c3a0","#da9a74"))
art.PAL["local"]=dict(tunic=("#f3e6c8","#d8c79e"),pants=("#f2ede2","#d2c9b2"),hat=("#e0592e","#a63a1c"),skin=("#c98d5c","#a96b3f"))
art.PAL["local2"]=dict(tunic=("#d9f0e6","#a9cfc0"),pants=("#f2ede2","#d2c9b2"),hat=("#2f86cc","#1f5a92"),skin=("#b97a4b","#97592f"))
CG=("#c3a640","#8a7324"); CD="#5a4a18"

def bez(p0,p1,p2,p3,u):
    a=(1-u)**3;b=3*u*(1-u)**2;c=3*u*u*(1-u);d=u**3
    x=a*p0[0]+b*p1[0]+c*p2[0]+d*p3[0]; y=a*p0[1]+b*p1[1]+c*p2[1]+d*p3[1]
    dx=3*(1-u)**2*(p1[0]-p0[0])+6*(1-u)*u*(p2[0]-p1[0])+3*u*u*(p3[0]-p2[0])
    dy=3*(1-u)**2*(p1[1]-p0[1])+6*(1-u)*u*(p2[1]-p1[1])+3*u*u*(p3[1]-p2[1])
    L=math.hypot(dx,dy) or 1; return x,y,dx/L,dy/L

def cobra_face(hx,hy,mood,tongue,flare,lookx=0,sc=1.0):
    s=f'<g transform="translate({f(hx)},{f(hy)}) scale({sc})">'
    s+=f'<ellipse cx="0" cy="0" rx="{f(84*flare)}" ry="104" fill="url(#hood)" stroke="{OUT}" stroke-width="{OW}"/>'
    s+=f'<ellipse cx="0" cy="36" rx="{f(40*flare)}" ry="62" fill="#f1e3a0" opacity=".85"/>'
    for k in range(5): s+=f'<path d="M {f(-34*flare)} {38+k*22-26} Q 0 {50+k*22-26+10} {f(34*flare)} {38+k*22-26}" stroke="{CD}" stroke-width="3.5" fill="none" opacity=".45"/>'
    s+=f'<ellipse cx="0" cy="-26" rx="58" ry="48" fill="#d3b84c" stroke="{OUT}" stroke-width="4.5"/>'
    for sx in (-1,1):
        ex=sx*24; ey=-38
        if mood=="scared":
            s+=f'<ellipse cx="{ex}" cy="{ey}" rx="18" ry="22" fill="#fff" stroke="{OUT}" stroke-width="4"/><ellipse cx="{ex+lookx}" cy="{ey}" rx="3.5" ry="7" fill="#111"/>'
            s+=f'<path d="M {ex-16} {ey-28} Q {ex} {ey-36} {ex+16} {ey-28}" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>'
        elif mood=="happy":
            s+=f'<path d="M {ex-15} {ey+4} Q {ex} {ey-16} {ex+15} {ey+4}" stroke="{OUT}" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
        else:
            s+=f'<ellipse cx="{ex}" cy="{ey}" rx="16" ry="19" fill="#fff" stroke="{OUT}" stroke-width="4"/><ellipse cx="{ex+lookx}" cy="{ey+1}" rx="4.6" ry="14" fill="#111"/><circle cx="{ex+lookx+2}" cy="{ey-5}" r="2" fill="#fff"/>'
            # heavy lid for sly
            s+=f'<path d="M {ex-18} {ey-3} L {ex+18} {ey-3} L {ex+18} {ey-24} L {ex-18} {ey-24} Z" fill="#d3b84c" stroke="{OUT}" stroke-width="4" stroke-linejoin="round" transform="translate(0,{3 if mood=="sly" else -8})"/>'
            s+=f'<path d="M {ex-sx*(-14)-0} {ey-18} L {ex+sx*(-16)} {ey-4}" stroke="{OUT}" stroke-width="5.5" stroke-linecap="round" opacity="0"/>'
    s+=f'<circle cx="-9" cy="-14" r="3" fill="{OUT}"/><circle cx="9" cy="-14" r="3" fill="{OUT}"/>'
    if mood=="scared":
        s+=f'<ellipse cx="0" cy="10" rx="17" ry="14" fill="#7a1f1f" stroke="{OUT}" stroke-width="4"/>'
    else:
        s+=f'<path d="M -34 2 Q 0 36 34 2" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>'
        s+=f'<path d="M -20 12 L -15 30 L -10 15 Z M 20 12 L 15 30 L 10 15 Z" fill="#fff" stroke="{OUT}" stroke-width="2.5" stroke-linejoin="round"/>'
    if tongue:
        s+=f'<path d="M 0 22 L 0 {40+34*tongue} M 0 {40+34*tongue} L -9 {52+34*tongue} M 0 {40+34*tongue} L 9 {52+34*tongue}" stroke="{OUT}" stroke-width="10" stroke-linecap="round" fill="none"/><path d="M 0 22 L 0 {40+34*tongue} M 0 {40+34*tongue} L -9 {52+34*tongue} M 0 {40+34*tongue} L 9 {52+34*tongue}" stroke="#e03a4a" stroke-width="5" stroke-linecap="round" fill="none"/>'
    return s+'</g>'

def cobra_up_svg(sway=0.0,rise=1.0,mood="sly",tongue=0,flare=1.0,coil=True):
    W,H=460,640; bx,by=230,590
    hx=230+sway*60; hy=by-110-rise*310
    s=""
    if coil:
        for (cy,rx,ry) in ((by-14,128,34),(by-48,102,28),(by-78,78,24)):
            s+=f'<ellipse cx="{bx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#bd)" stroke="{OUT}" stroke-width="{OW}"/>'
            for k in range(-3,4): s+=f'<path d="M {bx+k*rx/3.6} {cy-ry*.8} L {bx+k*rx/3.2} {cy+ry*.8}" stroke="{CD}" stroke-width="3" opacity=".35"/>'
    p0=(bx,by-70); p3=(hx,hy+70); p1=(bx-sway*90,by-190-rise*40); p2=(hx+sway*70,hy+150)
    if not coil: p0=(bx,by+30)
    d=f"M {f(p0[0])} {f(p0[1])} C {f(p1[0])} {f(p1[1])} {f(p2[0])} {f(p2[1])} {f(p3[0])} {f(p3[1])}"
    s+=f'<path d="{d}" fill="none" stroke="{OUT}" stroke-width="76" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#a98f2e" stroke-width="66" stroke-linecap="round"/><path d="{d}" fill="none" stroke="#7d6820" stroke-width="22" stroke-linecap="round" opacity=".5" transform="translate(16,0)"/>'
    s+=f'<path d="{d}" fill="none" stroke="#e8d684" stroke-width="22" stroke-linecap="round" opacity=".55"/>'
    for i in range(1,12):
        x,y,tx,ty=bez(p0,p1,p2,p3,i/12); nx,ny=-ty,tx
        s+=f'<path d="M {f(x-nx*30)} {f(y-ny*30)} L {f(x+nx*30)} {f(y+ny*30)}" stroke="{CD}" stroke-width="5" opacity=".5" stroke-linecap="round"/>'
    s+=cobra_face(hx,hy,mood,tongue,flare,lookx=sway*3)
    defs=f'<defs><linearGradient id="bd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CG[0]}"/><stop offset=".6" stop-color="{CG[1]}"/><stop offset="1" stop-color="#5f4e16"/></linearGradient><linearGradient id="hood" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9c15a"/><stop offset="1" stop-color="#8f7826"/></linearGradient></defs>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}{s}</svg>'

def cobra_slither_svg(ph=0.0,mood="sly",tongue=0):
    W,H=620,330; G=300
    N=46; pts=[]
    for i in range(N+1):
        u=i/N; x=50+u*430; y=G-34-(1-u*0.4)*16+math.sin(u*10-ph*2*math.pi)*24*(0.45+0.55*(1-u))
        y-=100*max(0,(u-0.8)/0.2)**1.6
        pts.append((x,y,10+u*26))
    s=""
    for k in (0,1):
        for i in range(N):
            a,b=pts[i],pts[i+1]
            if k==0: s+=f'<path d="M {f(a[0])} {f(a[1])} L {f(b[0])} {f(b[1])}" stroke="{OUT}" stroke-width="{f(a[2]+9)}" stroke-linecap="round"/>'
            else:
                s+=f'<path d="M {f(a[0])} {f(a[1])} L {f(b[0])} {f(b[1])}" stroke="{CG[0] if i%6<3 else CG[1]}" stroke-width="{f(a[2])}" stroke-linecap="round"/>'
    hx,hy=pts[-1][0]+12,pts[-1][1]-12
    s+=f'<ellipse cx="{f(hx-8)}" cy="{f(hy+8)}" rx="26" ry="44" fill="url(#hood)" stroke="{OUT}" stroke-width="5" transform="rotate(8 {f(hx)} {f(hy)})"/>'
    s+=f'<ellipse cx="{f(hx+22)}" cy="{f(hy)}" rx="40" ry="30" fill="#d3b84c" stroke="{OUT}" stroke-width="5"/>'
    s+=f'<ellipse cx="{f(hx+22)}" cy="{f(hy-8)}" rx="13" ry="15" fill="#fff" stroke="{OUT}" stroke-width="4"/><ellipse cx="{f(hx+26)}" cy="{f(hy-7)}" rx="3.6" ry="10" fill="#111"/>'
    s+=f'<path d="M {f(hx+4)} {f(hy-22)} L {f(hx+40)} {f(hy-14)}" stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>'
    s+=f'<path d="M {f(hx+8)} {f(hy+12)} Q {f(hx+36)} {f(hy+28)} {f(hx+60)} {f(hy+10)}" stroke="{OUT}" stroke-width="4.5" fill="none" stroke-linecap="round"/><path d="M {f(hx+40)} {f(hy+18)} l 4 14 l 5 -12 z" fill="#fff" stroke="{OUT}" stroke-width="2.5"/>'
    if tongue: s+=f'<path d="M {f(hx+58)} {f(hy+12)} L {f(hx+90)} {f(hy+16)} M {f(hx+90)} {f(hy+16)} L {f(hx+104)} {f(hy+6)} M {f(hx+90)} {f(hy+16)} L {f(hx+104)} {f(hy+26)}" stroke="#e03a4a" stroke-width="5" stroke-linecap="round" fill="none"/>'
    defs=f'<defs><linearGradient id="hood" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9c15a"/><stop offset="1" stop-color="#8f7826"/></linearGradient></defs>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}{s}</svg>'

def basket_svg(part):
    W,H=260,210; s=""
    if part=="back":
        s+=f'<ellipse cx="130" cy="84" rx="112" ry="28" fill="#2a1a10" stroke="{OUT}" stroke-width="7"/>'
    else:
        s+=f'<path d="M 18 86 L 36 186 Q 130 214 224 186 L 242 86 Q 130 120 18 86 Z" fill="url(#wk)" stroke="{OUT}" stroke-width="{OW+1}" stroke-linejoin="round"/>'
        for k in range(5):
            y=100+k*20; s+=f'<path d="M {22+k*3} {y} Q 130 {y+32} {238-k*3} {y}" stroke="#74501f" stroke-width="4" fill="none" opacity=".7"/>'
        for k in range(14):
            x=36+k*14.5; s+=f'<path d="M {x} {100+ (abs(k-6.5))*1.2} L {x+(k-6.5)*1.6} {188}" stroke="#74501f" stroke-width="3" opacity=".45"/>'
        s+=f'<path d="M 18 86 Q 130 120 242 86" fill="none" stroke="#c9974e" stroke-width="12" stroke-linecap="round"/><path d="M 18 86 Q 130 120 242 86" fill="none" stroke="{OUT}" stroke-width="3" stroke-linecap="round" transform="translate(0,6)" opacity=".5"/>'
    defs='<defs><linearGradient id="wk" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#cf9f5e"/><stop offset=".5" stop-color="#b98745"/><stop offset="1" stop-color="#8a5f2c"/></linearGradient></defs>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}{s}</svg>'

def bulb_svg():
    s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 280"><defs><radialGradient id="g"><stop offset="0" stop-color="#fff6a0"/><stop offset="1" stop-color="#ffd23a"/></radialGradient></defs>'
    for k in range(9):
        a=math.radians(-90+(k-4)*34); s+=f'<path d="M {120+math.cos(a)*100:.0f} {110+math.sin(a)*100:.0f} L {120+math.cos(a)*128:.0f} {110+math.sin(a)*128:.0f}" stroke="#ffd23a" stroke-width="10" stroke-linecap="round"/>'
    s+=f'<path d="M 120 20 C 55 20 40 90 82 130 C 96 144 96 160 96 170 L 144 170 C 144 160 144 144 158 130 C 200 90 185 20 120 20 Z" fill="url(#g)" stroke="{OUT}" stroke-width="7" stroke-linejoin="round"/>'
    s+=f'<rect x="92" y="170" width="56" height="16" rx="4" fill="#9a9aa2" stroke="{OUT}" stroke-width="5"/><rect x="98" y="186" width="44" height="16" rx="4" fill="#82828a" stroke="{OUT}" stroke-width="5"/><path d="M 100 120 L 120 90 L 140 120" fill="none" stroke="#b8860b" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    return s

def coin_svg():
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><defs><radialGradient id="c" cx=".35" cy=".3"><stop offset="0" stop-color="#fff1a0"/><stop offset="1" stop-color="#e8a91c"/></radialGradient></defs><circle cx="60" cy="60" r="52" fill="url(#c)" stroke="{OUT}" stroke-width="7"/><circle cx="60" cy="60" r="36" fill="none" stroke="#b9780e" stroke-width="6"/><path d="M 40 44 L 80 44 M 40 58 L 80 58 M 52 44 Q 78 44 78 52 Q 78 62 52 62 L 82 84" fill="none" stroke="#b9780e" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def sign_svg():
    W,H=440,680
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><defs><linearGradient id="w" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a87848"/><stop offset="1" stop-color="#7a5430"/></linearGradient></defs>
<rect x="196" y="300" width="48" height="370" rx="8" fill="url(#w)" stroke="{OUT}" stroke-width="6"/>
<rect x="14" y="14" width="412" height="330" rx="16" fill="url(#w)" stroke="{OUT}" stroke-width="7"/>
<rect x="40" y="40" width="360" height="278" rx="8" fill="#f4e6bf" stroke="{OUT}" stroke-width="5"/>
<circle cx="30" cy="30" r="8" fill="#555" stroke="{OUT}" stroke-width="3"/><circle cx="410" cy="30" r="8" fill="#555" stroke="{OUT}" stroke-width="3"/></svg>'''

def city_street(name,seed,sun,palette=None):
    from scenery import M,W,H,HOR
    P=dict(day=dict(top="#62b6ea",hor="#fff0cc",sun="#fffbe0",glow="#fff1a8",far="#c9b6d4",ga="#e6c48c",gb="#c19662",st="#a5794a"),
           noon=dict(top="#44a5ea",hor="#ffeec2",sun="#ffffe6",glow="#fff3a8",far="#c4b2d6",ga="#ecc98e",gb="#c8995f",st="#a8794a"),
           dusk=dict(top="#4d4296",hor="#ffb27d",sun="#ffe0a0",glow="#ffb06a",far="#9a78ae",ga="#d9a874",gb="#a9744b",st="#8a5a38"))[name]
    r=random.Random(seed)
    cols=[("#eab566","#c78d44"),("#e48b7a","#bf6558"),("#69b8ad","#418d84"),("#f4dcae","#d2b27c"),("#d98056","#b25a38"),("#f2ab3e","#cc8420"),("#b49ad0","#8a70ab")]
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-M} 0 {W+2*M} {H}" width="{W+2*M}" height="{H}"><defs>'
    svg+=f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["top"]}"/><stop offset="1" stop-color="{P["hor"]}"/></linearGradient>'
    svg+=f'<radialGradient id="glow"><stop offset="0" stop-color="{P["glow"]}" stop-opacity=".95"/><stop offset=".4" stop-color="{P["glow"]}" stop-opacity=".35"/><stop offset="1" stop-color="{P["glow"]}" stop-opacity="0"/></radialGradient>'
    svg+=f'<linearGradient id="gd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["ga"]}"/><stop offset="1" stop-color="{P["gb"]}"/></linearGradient>'
    svg+=f'<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["hor"]}" stop-opacity="0"/><stop offset="1" stop-color="{P["hor"]}" stop-opacity=".8"/></linearGradient></defs>'
    for i,(c0,c1) in enumerate(cols): svg+=f'<linearGradient id="b{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c0}"/><stop offset="1" stop-color="{c1}"/></linearGradient>'
    svg+=f'<rect x="{-M}" y="0" width="{W+2*M}" height="{HOR+10}" fill="url(#sky)"/><circle cx="{sun[0]}" cy="{sun[1]}" r="360" fill="url(#glow)"/><circle cx="{sun[0]}" cy="{sun[1]}" r="105" fill="{P["sun"]}"/>'
    # far skyline: domes & minarets (hazy)
    x=-M
    while x<W+M:
        w=r.randint(90,190); h=r.randint(120,260); k=r.random()
        svg+=f'<rect x="{x}" y="{HOR-h}" width="{w}" height="{h+20}" fill="{P["far"]}"/>'
        if k<0.4: svg+=f'<path d="M {x+10} {HOR-h} Q {x+w/2} {HOR-h-w*0.8} {x+w-10} {HOR-h} Z" fill="{P["far"]}"/><rect x="{x+w/2-3}" y="{HOR-h-w*0.8-30}" width="6" height="34" fill="{P["far"]}"/>'
        elif k<0.65: svg+=f'<rect x="{x+w/2-9}" y="{HOR-h-120}" width="18" height="130" fill="{P["far"]}"/><path d="M {x+w/2-14} {HOR-h-120} Q {x+w/2} {HOR-h-160} {x+w/2+14} {HOR-h-120} Z" fill="{P["far"]}"/>'
        x+=w-10
    svg+=f'<rect x="{-M}" y="{HOR-300}" width="{W+2*M}" height="320" fill="url(#haze)"/>'
    # mid buildings
    x=-M-20; i=0
    while x<W+M:
        w=r.randint(150,250); h=r.randint(210,400); ci=r.randrange(len(cols)); y0=HOR+30
        svg+=f'<rect x="{x}" y="{y0-h}" width="{w}" height="{h}" fill="url(#b{ci})" stroke="{OUT}" stroke-width="6"/>'
        svg+=f'<rect x="{x-6}" y="{y0-h-18}" width="{w+12}" height="22" fill="{cols[ci][1]}" stroke="{OUT}" stroke-width="5"/>'
        k=r.random()
        if k<0.35: svg+=f'<path d="M {x+w*.2} {y0-h-18} Q {x+w/2} {y0-h-18-w*0.75} {x+w*.8} {y0-h-18} Z" fill="#f4ecd6" stroke="{OUT}" stroke-width="6"/><rect x="{x+w/2-3}" y="{y0-h-w*0.75-52}" width="6" height="40" fill="{OUT}"/><circle cx="{x+w/2}" cy="{y0-h-w*0.75-52}" r="8" fill="#ffd23c" stroke="{OUT}" stroke-width="3"/>'
        for row in range(max(1,int(h/130))):
            for cx in range(int(w//75)):
                wx=x+24+cx*(w-48)/max(1,int(w//75)); wy=y0-h+30+row*110
                if wy>y0-170: continue
                svg+=f'<path d="M {wx:.0f} {wy+62:.0f} L {wx:.0f} {wy+22:.0f} Q {wx+16:.0f} {wy-4:.0f} {wx+32:.0f} {wy+22:.0f} L {wx+32:.0f} {wy+62:.0f} Z" fill="#3a2a40" stroke="{OUT}" stroke-width="4"/><rect x="{wx-4:.0f}" y="{wy+62:.0f}" width="40" height="8" fill="#fff" opacity=".35" stroke="{OUT}" stroke-width="3"/>'
        # awning
        if r.random()<0.65:
            aw=min(w-20,170); ax=x+(w-aw)/2
            for j in range(6): svg+=f'<path d="M {ax+j*aw/6:.0f} {y0-150} L {ax+(j+1)*aw/6:.0f} {y0-150} L {ax+(j+1)*aw/6+4:.0f} {y0-100} L {ax+j*aw/6-4:.0f} {y0-100} Z" fill="{"#f6f1e6" if j%2 else "#d9453a"}" stroke="{OUT}" stroke-width="3.5"/>'
        x+=w-4; i+=1
    # laundry line
    for k in range(3):
        xa=r.uniform(-M,W); y=HOR-150-k*30
        svg+=f'<path d="M {xa:.0f} {y} Q {xa+160:.0f} {y+40} {xa+320:.0f} {y}" stroke="{OUT}" stroke-width="3" fill="none"/>'
        for j in range(5):
            u=(j+1)/6; cx=xa+320*u; cy=y+40*2*u*(1-u)*1.0
            svg+=f'<rect x="{cx-12:.0f}" y="{cy:.0f}" width="24" height="34" fill="{r.choice(["#e8505b","#5fa9e0","#ffd23c","#fff","#6fcf8a"])}" stroke="{OUT}" stroke-width="3"/>'
    svg+=f'<rect x="{-M}" y="{HOR-30}" width="{W+2*M}" height="60" fill="url(#haze)" opacity=".35"/>'
    svg+=f'<rect x="{-M}" y="{HOR+30}" width="{W+2*M}" height="{H-HOR-30}" fill="url(#gd)"/>'
    vx=W/2
    for i in range(-24,25):
        if i%2==0: svg+=f'<polygon points="{vx+i*30},{HOR+30} {vx+i*30+30},{HOR+30} {vx+i*230+230},{H} {vx+i*230},{H}" fill="{P["st"]}" opacity=".13"/>'
    for i in range(5200):
        u=r.random()**0.75; y=HOR+40+u*(H-HOR-40); t=(y-HOR)/(H-HOR); x=r.uniform(-M,W+M)
        wd=3+30*t**1.1; ht=wd*0.36
        svg+=f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{wd:.1f}" ry="{ht:.1f}" fill="{r.choice([P["st"],"#fff3d0",P["gb"]])}" opacity="{r.uniform(.07,.2):.2f}"/>'
    svg+=f'<rect x="{-M}" y="{HOR+30}" width="{W+2*M}" height="70" fill="url(#haze)" opacity=".3"/></svg>'
    return render(svg,W+2*M,H)

def fg_city(name,seed):
    from scenery import M,W,H
    h=300; r=random.Random(seed)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-M} {H-h} {W+2*M} {h}" width="{W+2*M}" height="{h}"><defs><linearGradient id="sh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#1a0f05" stop-opacity=".6"/></linearGradient></defs><rect x="{-M}" y="{H-h}" width="{W+2*M}" height="{h}" fill="url(#sh)"/>'
    for i in range(40):
        x=r.uniform(-M,W+M); y=H-r.uniform(0,150); w=r.uniform(20,60)
        svg+=f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{w:.0f}" ry="{w*.35:.0f}" fill="#8c6a48" opacity=".5"/>'
    return render(svg+'</svg>',W+2*M,h)

if __name__=="__main__":
    from PIL import Image
    sh=Image.new("RGBA",(2200,1100),(255,235,200,255)); x=0
    for i,(sw,ri,m,tg,fl) in enumerate([(0,1,"sly",0,1),(0.8,1,"sly",1,1),(-.6,.8,"scared",0,1.1),(0,1,"happy",0,1)]):
        im=render(cobra_up_svg(sw,ri,m,tg,fl),460,640); sh.alpha_composite(im,(i*340,0))
    for i,(k,a,m) in enumerate([("official","hips","smile"),("local","idle","smile"),("local2","flail","shock")]):
        im=render(person_svg(k,p=0,arms=a,mood=m),300,533); sh.alpha_composite(im,(1400+i*270,0))
    sh.alpha_composite(render(cobra_slither_svg(0.2,"sly",1),620,330),(0,650))
    sh.alpha_composite(render(basket_svg("back"),260,210),(700,700)); 
    sh.alpha_composite(render(cobra_up_svg(0.3,.6,"sly",0,1,False),230,320),(730,520))
    sh.alpha_composite(render(basket_svg("front"),260,210),(700,700))
    sh.alpha_composite(render(bulb_svg(),160,187),(1000,720)); sh.alpha_composite(render(coin_svg(),100,100),(1200,740)); sh.alpha_composite(render(sign_svg(),220,340),(1350,600))
    sh.convert("RGB").save("sprites3.png")
    st=city_street("day",5,(800,400)); st.crop((200,0,1280,1920)).convert("RGB").resize((540,960)).save("street.png")
