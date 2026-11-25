import math, random, subprocess, io, functools
from PIL import Image

OUT="#2a1c14"; OW=5

def render(svg,w,h):
    r=subprocess.run(["rsvg-convert","-w",str(w),"-h",str(h),"-f","png"],input=svg.encode(),capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode())
    return Image.open(io.BytesIO(r.stdout)).convert("RGBA")

def f(x): return f"{x:.1f}"
def ik(H,F,l1,l2,bend=-1):
    hx,hy=H; fx,fy=F; dx,dy=fx-hx,fy-hy; L=math.hypot(dx,dy) or 1
    d=min(L,l1+l2-0.5); ux,uy=dx/L,dy/L; fx,fy=hx+ux*d,hy+uy*d
    a=(l1*l1-l2*l2+d*d)/(2*d); h=math.sqrt(max(0,l1*l1-a*a))
    mx,my=hx+ux*a,hy+uy*a; nx,ny=-uy,ux
    k1=(mx+nx*h,my+ny*h); k2=(mx-nx*h,my-ny*h)
    knee=(k1 if k1[0]<k2[0] else k2) if bend<0 else (k1 if k1[0]>k2[0] else k2)
    return knee,(fx,fy)

def foot_path(u,A,L,stance=0.6):
    u%=1
    if u<stance: return A-2*A*(u/stance),0
    w=(u-stance)/(1-stance); return -A+2*A*w, L*math.sin(math.pi*w)

def blob(cx,cy,rx,ry,n=26,jit=0.09,seed=1,rot=0):
    r=random.Random(seed); pts=[]
    for i in range(n):
        a=2*math.pi*i/n; k=1+(jit if i%2 else -jit*0.3)*(0.6+0.8*r.random())
        x=rx*k*math.cos(a); y=ry*k*math.sin(a)
        ca,sa=math.cos(rot),math.sin(rot)
        pts.append((cx+x*ca-y*sa,cy+x*sa+y*ca))
    d=f"M {f((pts[-1][0]+pts[0][0])/2)} {f((pts[-1][1]+pts[0][1])/2)} "
    for i in range(n):
        p=pts[i]; q=pts[(i+1)%n]; d+=f"Q {f(p[0])} {f(p[1])} {f((p[0]+q[0])/2)} {f((p[1]+q[1])/2)} "
    return d+"Z"

# ------------------------------------------------------------------ EMU
def emu_svg(p=0.0,mood="smug",dip=0.0,beak=0.0,lean=0.0,medal=False,gloves=False,stride=1.0,blink=0):
    W,H=560,640; G=600
    bob=-abs(math.sin(2*math.pi*p))*10*stride
    hips=[(205,430+bob),(245,430+bob)]
    legs=""
    for k,hp in enumerate(hips):
        ox,oy=foot_path(p+0.5*k,62*stride,48*stride)
        foot=(hp[0]+ox+8,G-oy)
        knee,ft=ik(hp,foot,70,86)
        col="#c9ae8b" if k==0 else "#a88f70"
        legs+=f'<path d="M {f(hp[0])} {f(hp[1])} L {f(knee[0])} {f(knee[1])} L {f(ft[0])} {f(ft[1])}" fill="none" stroke="{OUT}" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"/>'
        legs+=f'<path d="M {f(hp[0])} {f(hp[1])} L {f(knee[0])} {f(knee[1])} L {f(ft[0])} {f(ft[1])}" fill="none" stroke="{col}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>'
        for ang in (-28,0,28):
            a=math.radians(ang); tx=ft[0]+math.cos(a)*34; ty=ft[1]+math.sin(a)*14+4
            legs+=f'<path d="M {f(ft[0])} {f(ft[1])} L {f(tx)} {f(ty)}" stroke="{OUT}" stroke-width="15" stroke-linecap="round"/><path d="M {f(ft[0])} {f(ft[1])} L {f(tx)} {f(ty)}" stroke="{col}" stroke-width="8" stroke-linecap="round"/>'
            legs+=f'<circle cx="{f(tx+3)}" cy="{f(ty)}" r="4" fill="#2a1c14"/>'
    by=bob
    body=f'<g transform="translate(0,{f(by)}) rotate({f(-4+lean)} 220 350)">'
    # tail tuft
    body+=f'<path d="{blob(120,350,78,86,30,0.12,3,0.3)}" fill="url(#tail)" stroke="{OUT}" stroke-width="{OW}" stroke-linejoin="round"/>'
    body+=f'<path d="{blob(225,345,128,98,34,0.07,5,0.05)}" fill="url(#body)" stroke="{OUT}" stroke-width="{OW}" stroke-linejoin="round"/>'
    # belly
    body+=f'<path d="{blob(255,392,80,42,24,0.06,8)}" fill="#a98763" opacity=".55"/>'
    r=random.Random(11)
    for i in range(46):
        x=r.uniform(120,330); y=r.uniform(270,420)
        if ((x-225)/128)**2+((y-345)/98)**2>0.8: continue
        L=r.uniform(18,34); c=r.choice(["#3b281c","#b08f69","#4a3425","#c3a37c"])
        body+=f'<path d="M {f(x)} {f(y)} q {f(-L*.5)} {f(L*.3)} {f(-L*.9)} {f(L*.9)}" stroke="{c}" stroke-width="3.4" stroke-linecap="round" fill="none" opacity=".75"/>'
    # wing tuft
    body+=f'<path d="{blob(215,345,52,40,18,0.15,9,-0.3)}" fill="#5a4030" stroke="{OUT}" stroke-width="3" opacity=".85"/>'
    body+='</g>'
    # neck
    bx,byy=300,300+by
    up=((bx,byy),(338,236+by),(336,160+by),(372,112+by))
    dn=((bx,byy),(372,330+by),(420,420+by),(392,500+by))
    P=[(up[i][0]*(1-dip)+dn[i][0]*dip,up[i][1]*(1-dip)+dn[i][1]*dip) for i in range(4)]
    nd=f"M {f(P[0][0])} {f(P[0][1])} C {f(P[1][0])} {f(P[1][1])} {f(P[2][0])} {f(P[2][1])} {f(P[3][0])} {f(P[3][1])}"
    neck=f'<path d="{nd}" fill="none" stroke="{OUT}" stroke-width="50" stroke-linecap="round"/><path d="{nd}" fill="none" stroke="url(#neckg)" stroke-width="40" stroke-linecap="round"/>'
    # neck feather base
    neck+=f'<path d="{blob(bx-8,byy+4,46,38,16,0.18,4)}" fill="#6c4f3a" stroke="{OUT}" stroke-width="4"/>'
    hc=P[3]; ang=-6+dip*70+(-8 if mood=="smug" else 0)+(10 if mood=="shock" else 0)
    ey={"smug":-8,"angry":-8,"shock":-9,"happy":-8,"derp":-8}.get(mood,-8)
    head=f'<g transform="translate({f(hc[0])},{f(hc[1])}) rotate({f(ang)})">'
    # crest feathers
    for i,(dx,dy) in enumerate([(-22,-22),(-12,-28),(-2,-30)]):
        head+=f'<path d="M {dx} {dy+8} q {-3} {-16} {6+i} {-22}" stroke="{OUT}" stroke-width="4" fill="none" stroke-linecap="round"/>'
    head+=f'<ellipse cx="0" cy="0" rx="36" ry="28" fill="url(#neckg)" stroke="{OUT}" stroke-width="{OW}"/>'
    bo=beak*26
    head+=f'<g transform="rotate({f(bo*0.7)} 16 10)"><path d="M 14 8 Q 46 10 58 18 Q 36 28 12 20 Z" fill="#5a5e66" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/></g>'
    head+=f'<path d="M 14 -12 Q 50 -12 70 6 Q 46 10 14 8 Z" fill="#6d727a" stroke="{OUT}" stroke-width="4.5" stroke-linejoin="round"/><circle cx="42" cy="-3" r="2" fill="{OUT}"/>'
    ex,eyy=6,ey
    if mood=="happy":
        head+=f'<path d="M {ex-12} {eyy+4} Q {ex} {eyy-14} {ex+12} {eyy+4}" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    elif blink:
        head+=f'<path d="M {ex-12} {eyy} Q {ex} {eyy+8} {ex+12} {eyy}" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    else:
        er=15 if mood=="shock" else 12
        head+=f'<ellipse cx="{ex}" cy="{eyy}" rx="{er}" ry="{er+2}" fill="#fff" stroke="{OUT}" stroke-width="4"/>'
        pr=3 if mood=="shock" else 5.2
        px=ex+(5 if mood!="derp" else -1)
        head+=f'<circle cx="{px}" cy="{eyy+1}" r="{pr+3.5}" fill="#e8a028"/><circle cx="{px}" cy="{eyy+1}" r="{pr}" fill="#1a0f0a"/><circle cx="{px+2}" cy="{eyy-2}" r="1.8" fill="#fff"/>'
        if mood=="smug":
            head+=f'<path d="M {ex-15} {eyy-2} L {ex+15} {eyy-8} L {ex+15} {eyy-20} L {ex-15} {eyy-20} Z" fill="url(#neckg)" stroke="{OUT}" stroke-width="4" stroke-linejoin="round" transform="translate(0,1)"/>'
            head+=f'<path d="M {ex-16} {eyy-13} L {ex+16} {eyy-19}" stroke="{OUT}" stroke-width="5" stroke-linecap="round"/>'
        if mood=="angry":
            head+=f'<path d="M {ex-18} {eyy-16} L {ex+16} {eyy-2}" stroke="{OUT}" stroke-width="6.5" stroke-linecap="round"/>'
        if mood=="shock":
            head+=f'<path d="M {ex-14} {eyy-22} Q {ex} {eyy-30} {ex+14} {eyy-22}" stroke="{OUT}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    head+='</g>'
    extra=""
    if medal:
        mx,my=P[0][0]+30,P[0][1]-26
        extra+=f'<path d="M {mx-14} {my-34} L {mx+14} {my-34} L {mx+6} {my+2} L {mx-6} {my+2} Z" fill="#d4313c" stroke="{OUT}" stroke-width="3"/><circle cx="{mx}" cy="{my+16}" r="22" fill="#ffd23c" stroke="{OUT}" stroke-width="4"/><circle cx="{mx}" cy="{my+16}" r="13" fill="none" stroke="#c28a0f" stroke-width="3"/>'
    defs='''<defs>
<linearGradient id="body" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9a7656"/><stop offset=".55" stop-color="#7a5a40"/><stop offset="1" stop-color="#533a2a"/></linearGradient>
<linearGradient id="tail" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b4e38"/><stop offset="1" stop-color="#3f2c20"/></linearGradient>
<linearGradient id="neckg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8ea6b8"/><stop offset=".5" stop-color="#b4c8d6"/><stop offset="1" stop-color="#8aa0b2"/></linearGradient></defs>'''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}{legs}{body}{neck}{head}{extra}</svg>'

# ------------------------------------------------------------------ PEOPLE
PAL={
 "soldier":dict(tunic=("#c4ac6a","#97834a"),pants=("#a89258","#7e6c3b"),hat=("#8a7036","#5f4c22"),skin=("#f0c9a0","#d9a577")),
 "major":dict(tunic=("#8f9a6b","#66714a"),pants=("#7c8660","#586245"),hat=("#6d7450","#454c33"),skin=("#f2b894","#d98f6c")),
 "farmer":dict(tunic=("#d9553f","#a63a2c"),pants=("#4f79b5","#33557f"),hat=("#e6cf7a","#bba24c"),skin=("#eebf94","#d2966a")),
}
def vec(a,l): return math.sin(math.radians(a))*l, math.cos(math.radians(a))*l

def person_svg(kind="soldier",p=0.0,arms="walk",mood="determined",walk=1.0,sweat=False,mouth_open=0.0,rifle=True):
    pal=PAL[kind]; W,H=360,640; G=610
    bob=-abs(math.sin(2*math.pi*p))*7*walk
    fat=1.18 if kind in ("major","official") else 1.0
    hipc=(165,425+bob)
    legs=""
    for k,dx in enumerate((-18,18)):
        hp=(hipc[0]+dx,hipc[1])
        ox,oy=foot_path(p+0.5*k,48*walk,30*walk)
        foot=(hp[0]+ox,G-14-oy)
        knee,ft=ik(hp,foot,92,92,bend=+1)
        shade=pal["pants"][k]
        legs+=f'<path d="M {f(hp[0])} {f(hp[1])} L {f(knee[0])} {f(knee[1])} L {f(ft[0])} {f(ft[1])}" fill="none" stroke="{OUT}" stroke-width="{f(40*fat)}" stroke-linecap="round" stroke-linejoin="round"/><path d="M {f(hp[0])} {f(hp[1])} L {f(knee[0])} {f(knee[1])} L {f(ft[0])} {f(ft[1])}" fill="none" stroke="{shade}" stroke-width="{f(31*fat)}" stroke-linecap="round" stroke-linejoin="round"/>'
        legs+=f'<path d="M {f(ft[0]-18)} {f(ft[1]-12)} L {f(ft[0]+8)} {f(ft[1]-14)} Q {f(ft[0]+46)} {f(ft[1]-10)} {f(ft[0]+44)} {f(ft[1]+10)} L {f(ft[0]-20)} {f(ft[1]+12)} Z" fill="#4a2f1c" stroke="{OUT}" stroke-width="4.5" stroke-linejoin="round"/>'
    tw=58*fat; ty0=238+bob; ty1=430+bob
    torso=f'<rect x="{f(165-tw)}" y="{f(ty0)}" width="{f(tw*2)}" height="{f(ty1-ty0)}" rx="26" fill="url(#tun)" stroke="{OUT}" stroke-width="{OW}"/>'
    torso+=f'<rect x="{f(165-tw)}" y="{f(ty1-52)}" width="{f(tw*2)}" height="16" fill="#5b3a22" stroke="{OUT}" stroke-width="3.5"/><rect x="{f(158)}" y="{f(ty1-55)}" width="16" height="22" rx="3" fill="#e5c14a" stroke="{OUT}" stroke-width="3"/>'
    if kind not in ("farmer","local","local2"):
        torso+=f'<rect x="{f(165-tw+14)}" y="{f(ty0+48)}" width="30" height="30" rx="4" fill="none" stroke="{OUT}" stroke-width="3.5" opacity=".7"/><rect x="{f(165+tw-44)}" y="{f(ty0+48)}" width="30" height="30" rx="4" fill="none" stroke="{OUT}" stroke-width="3.5" opacity=".7"/>'
        torso+=f'<path d="M {f(165-16)} {f(ty0+2)} L 165 {f(ty0+36)} L {f(165+16)} {f(ty0+2)}" fill="#e9d9b0" stroke="{OUT}" stroke-width="3.5" stroke-linejoin="round"/>'
    elif kind=="farmer":
        torso+=f'<path d="M {f(165-tw+8)} {f(ty0+60)} L {f(165+tw-8)} {f(ty0+60)} L {f(165+tw-8)} {f(ty1-4)} L {f(165-tw+8)} {f(ty1-4)} Z" fill="url(#pnt)" stroke="{OUT}" stroke-width="4"/>'
        torso+=f'<path d="M {f(165-30)} {f(ty0+60)} L {f(165-22)} {f(ty0)} M {f(165+30)} {f(ty0+60)} L {f(165+22)} {f(ty0)}" stroke="{OUT}" stroke-width="12" stroke-linecap="round"/><path d="M {f(165-30)} {f(ty0+60)} L {f(165-22)} {f(ty0)} M {f(165+30)} {f(ty0+60)} L {f(165+22)} {f(ty0)}" stroke="#4f79b5" stroke-width="7" stroke-linecap="round"/>'
    if kind in ("local","local2"):
        vc="#8a3a2a" if kind=="local" else "#c27a1a"
        torso+=f'<path d="M {f(165-tw+2)} {f(ty0+8)} L {f(165-14)} {f(ty0+8)} L {f(165-14)} {f(ty1-62)} L {f(165-tw+2)} {f(ty1-62)} Z" fill="{vc}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/><path d="M {f(165+tw-2)} {f(ty0+8)} L {f(165+14)} {f(ty0+8)} L {f(165+14)} {f(ty1-62)} L {f(165+tw-2)} {f(ty1-62)} Z" fill="{vc}" stroke="{OUT}" stroke-width="4" stroke-linejoin="round"/>'
        for i in range(3): torso+=f'<circle cx="{f(165-26)}" cy="{f(ty0+40+i*34)}" r="5" fill="#ffd23c" stroke="{OUT}" stroke-width="2"/>'
    if kind=="major":
        for i in range(4): torso+=f'<circle cx="{f(165+22+ (i%2)*18)}" cy="{f(ty0+60+(i//2)*18)}" r="7" fill="#ffd23c" stroke="{OUT}" stroke-width="2.5"/>'
        torso+=f'<path d="M {f(165-tw+4)} {f(ty0+14)} L {f(165-tw+30)} {f(ty0+14)}" stroke="#ffd23c" stroke-width="6" stroke-linecap="round"/>'
    # arms: (shoulder, upper angle, fore angle)
    def arm(sx,sy,a1,a2,col,hand="#f0c9a0"):
        e=vec(a1,58); h=vec(a2,52); ex,ey=sx+e[0],sy+e[1]; hx,hy=ex+h[0],ey+h[1]
        s=f'<path d="M {f(sx)} {f(sy)} L {f(ex)} {f(ey)} L {f(hx)} {f(hy)}" fill="none" stroke="{OUT}" stroke-width="31" stroke-linecap="round" stroke-linejoin="round"/><path d="M {f(sx)} {f(sy)} L {f(ex)} {f(ey)} L {f(hx)} {f(hy)}" fill="none" stroke="{col}" stroke-width="21" stroke-linecap="round" stroke-linejoin="round"/>'
        s+=f'<circle cx="{f(hx)}" cy="{f(hy)}" r="16" fill="{pal["skin"][0]}" stroke="{OUT}" stroke-width="4"/>'
        return s,(hx,hy)
    sw=math.sin(2*math.pi*p)
    presets={"walk":((-30*sw,-30*sw+20),(30*sw,30*sw+22)),
             "point":((20,10),(95,90)),
             "fist":((15,30),(160,175)),
             "salute":((10,25),(150,255)),
             "flail":((170,200),(190,160)),
             "hips":((50,-10),(-50,10)),
             "shrug":((55,95),(-55,-95)),
             "idle":((8,14),(-6,-12))}
    (ba1,ba2),(fa1,fa2)=presets[arms]
    sy=ty0+30
    backarm,bh=arm(165-tw+6,sy,ba1,ba2,pal["tunic"][1])
    frontarm,fh=arm(165+tw-6,sy,fa1,fa2,pal["tunic"][0])
    rif=""
    if rifle and arms=="walk" and kind=="soldier":
        rif=f'<path d="M {f(fh[0]-30)} {f(fh[1]+80)} L {f(fh[0]+60)} {f(fh[1]-170)}" stroke="{OUT}" stroke-width="15" stroke-linecap="round"/><path d="M {f(fh[0]-30)} {f(fh[1]+80)} L {f(fh[0]+60)} {f(fh[1]-170)}" stroke="#8a5a32" stroke-width="8" stroke-linecap="round"/><path d="M {f(fh[0]+18)} {f(fh[1]-60)} L {f(fh[0]+60)} {f(fh[1]-170)}" stroke="#4d4d55" stroke-width="6" stroke-linecap="round"/>'
    if kind=="major" and arms in("walk","point","hips","idle"):
        rif=f'<path d="M {f(fh[0]-6)} {f(fh[1]+30)} L {f(fh[0]+10)} {f(fh[1]-120)}" stroke="{OUT}" stroke-width="9" stroke-linecap="round"/><path d="M {f(fh[0]-6)} {f(fh[1]+30)} L {f(fh[0]+10)} {f(fh[1]-120)}" stroke="#a87a45" stroke-width="4.5" stroke-linecap="round"/>' if arms!="point" else f'<path d="M {f(fh[0]-10)} {f(fh[1])} L {f(fh[0]+150)} {f(fh[1]-10)}" stroke="{OUT}" stroke-width="10" stroke-linecap="round"/><path d="M {f(fh[0]-10)} {f(fh[1])} L {f(fh[0]+150)} {f(fh[1]-10)}" stroke="#a87a45" stroke-width="5" stroke-linecap="round"/>'
    # head
    hy=ty0-48+bob*0.5; hx=170
    sk=pal["skin"]
    head=f'<rect x="{hx-18}" y="{f(hy+40)}" width="36" height="34" fill="{sk[1]}" stroke="{OUT}" stroke-width="4"/>'
    head+=f'<ellipse cx="{hx-48}" cy="{f(hy+6)}" rx="11" ry="15" fill="{sk[1]}" stroke="{OUT}" stroke-width="4"/>'
    head+=f'<ellipse cx="{hx}" cy="{f(hy)}" rx="56" ry="58" fill="url(#skn)" stroke="{OUT}" stroke-width="{OW}"/>'
    head+=f'<ellipse cx="{hx+54}" cy="{f(hy+14)}" rx="16" ry="14" fill="{sk[0]}" stroke="{OUT}" stroke-width="4.5"/>'
    ex=hx+22; ey=hy-6
    er,pr=(15,4) if mood=="shock" else (12,5.5)
    head+=f'<ellipse cx="{ex}" cy="{f(ey)}" rx="{er}" ry="{er+3}" fill="#fff" stroke="{OUT}" stroke-width="4"/><circle cx="{ex+4}" cy="{f(ey+1)}" r="{pr}" fill="#1a1a1a"/><circle cx="{ex+6}" cy="{f(ey-2)}" r="1.8" fill="#fff"/>'
    brow={"determined":(-8,8),"angry":(-14,4),"shock":(14,14),"worried":(6,-10),"smile":(0,6),"sad":(10,-8)}.get(mood,(0,0))
    head+=f'<path d="M {ex-16} {f(ey-22+brow[0]*0.4)} L {ex+16} {f(ey-22-brow[1]*0.4)}" stroke="{OUT}" stroke-width="6.5" stroke-linecap="round"/>'
    mx,my=hx+30,hy+34
    if mouth_open>0 or mood=="shock":
        o=max(mouth_open,0.8 if mood=="shock" else 0)
        head+=f'<ellipse cx="{mx}" cy="{f(my+6)}" rx="13" ry="{f(6+14*o)}" fill="#6a1f1f" stroke="{OUT}" stroke-width="4"/>'
    elif mood in("smile",):
        head+=f'<path d="M {mx-18} {f(my)} Q {mx} {f(my+16)} {mx+16} {f(my-4)}" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    elif mood in("sad","worried"):
        head+=f'<path d="M {mx-14} {f(my+8)} Q {mx} {f(my-4)} {mx+14} {f(my+8)}" stroke="{OUT}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    else:
        head+=f'<path d="M {mx-14} {f(my+2)} L {mx+14} {f(my-2)}" stroke="{OUT}" stroke-width="5.5" fill="none" stroke-linecap="round"/>'
    if kind in ("major","official","local","local2"):
        head+=f'<path d="M {mx-30} {f(my-8)} Q {mx-6} {f(my-26)} {mx+34} {f(my-8)} Q {mx+10} {f(my+6)} {mx-30} {f(my-8)} Z" fill="#241a14" stroke="{OUT}" stroke-width="3"/>'
        if kind in ("major","official"): head+=f'<circle cx="{ex}" cy="{f(ey)}" r="22" fill="none" stroke="#e5c14a" stroke-width="4"/><path d="M {ex+14} {f(ey+16)} Q {ex+20} {f(ey+60)} {ex-6} {f(ey+90)}" stroke="#e5c14a" stroke-width="2.5" fill="none"/>'
    if sweat:
        head+=f'<path d="M {hx-30} {f(hy-52)} q -9 16 0 24 q 9 -8 0 -24 Z" fill="#8fd0ff" stroke="{OUT}" stroke-width="3"/>'
    # hat
    h0,h1=pal["hat"]
    if kind=="farmer":
        head+=f'<ellipse cx="{hx}" cy="{f(hy-40)}" rx="86" ry="17" fill="{h0}" stroke="{OUT}" stroke-width="{OW}"/><path d="M {hx-48} {f(hy-42)} Q {hx-46} {f(hy-96)} {hx} {f(hy-98)} Q {hx+46} {f(hy-96)} {hx+48} {f(hy-42)} Z" fill="{h0}" stroke="{OUT}" stroke-width="{OW}"/><rect x="{hx-48}" y="{f(hy-58)}" width="96" height="12" fill="#a63a2c" stroke="{OUT}" stroke-width="3"/>'
    elif kind=="official":
        head+=f'<ellipse cx="{hx}" cy="{f(hy-40)}" rx="92" ry="17" fill="{h1}" stroke="{OUT}" stroke-width="{OW}"/><path d="M {hx-58} {f(hy-42)} Q {hx-62} {f(hy-122)} {hx} {f(hy-124)} Q {hx+62} {f(hy-122)} {hx+58} {f(hy-42)} Z" fill="{h0}" stroke="{OUT}" stroke-width="{OW}"/><rect x="{hx-58}" y="{f(hy-66)}" width="116" height="14" fill="#7c6a44" stroke="{OUT}" stroke-width="3.5"/><circle cx="{hx}" cy="{f(hy-128)}" r="8" fill="{h1}" stroke="{OUT}" stroke-width="3.5"/>'
    elif kind in ("local","local2"):
        head+=f'<path d="M {hx-62} {f(hy-30)} Q {hx-72} {f(hy-114)} {hx} {f(hy-122)} Q {hx+72} {f(hy-114)} {hx+62} {f(hy-30)} Q {hx} {f(hy-46)} {hx-62} {f(hy-30)} Z" fill="{h0}" stroke="{OUT}" stroke-width="{OW}" stroke-linejoin="round"/>'
        for k in range(4): head+=f'<path d="M {hx-60+k*3} {f(hy-40-k*20)} Q {hx} {f(hy-72-k*22)} {hx+62-k*3} {f(hy-34-k*20)}" stroke="{h1}" stroke-width="5" fill="none" opacity=".9"/>'
        head+=f'<circle cx="{hx+6}" cy="{f(hy-64)}" r="9" fill="#ffd23c" stroke="{OUT}" stroke-width="3"/>'
    elif kind=="major":
        head+=f'<path d="M {hx-58} {f(hy-34)} Q {hx-56} {f(hy-92)} {hx} {f(hy-96)} Q {hx+56} {f(hy-92)} {hx+58} {f(hy-34)} Z" fill="{h0}" stroke="{OUT}" stroke-width="{OW}"/><rect x="{hx-58}" y="{f(hy-52)}" width="116" height="16" fill="#e5c14a" stroke="{OUT}" stroke-width="3.5"/><path d="M {hx-8} {f(hy-36)} Q {hx+60} {f(hy-28)} {hx+96} {f(hy-34)} Q {hx+60} {f(hy-18)} {hx-8} {f(hy-22)} Z" fill="{h1}" stroke="{OUT}" stroke-width="4.5" stroke-linejoin="round"/><circle cx="{hx+18}" cy="{f(hy-74)}" r="9" fill="#ffd23c" stroke="{OUT}" stroke-width="3"/>'
    else:
        head+=f'<path d="M {hx-100} {f(hy-52)} Q {hx-112} {f(hy-96)} {hx-62} {f(hy-70)} Z" fill="{h1}" stroke="{OUT}" stroke-width="4.5" stroke-linejoin="round"/>'
        head+=f'<ellipse cx="{hx}" cy="{f(hy-38)}" rx="92" ry="19" fill="{h1}" stroke="{OUT}" stroke-width="{OW}" transform="rotate(-5 {hx} {f(hy-38)})"/>'
        head+=f'<path d="M {hx-58} {f(hy-42)} Q {hx-58} {f(hy-104)} {hx} {f(hy-104)} Q {hx+58} {f(hy-104)} {hx+58} {f(hy-40)} Z" fill="{h0}" stroke="{OUT}" stroke-width="{OW}"/><path d="M {hx-58} {f(hy-46)} L {hx+58} {f(hy-44)} L {hx+58} {f(hy-58)} L {hx-58} {f(hy-60)} Z" fill="#3e2c15" stroke="{OUT}" stroke-width="3.5"/>'
    defs=f'''<defs><linearGradient id="tun" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{pal["tunic"][0]}"/><stop offset="1" stop-color="{pal["tunic"][1]}"/></linearGradient>
<linearGradient id="pnt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{pal["pants"][0]}"/><stop offset="1" stop-color="{pal["pants"][1]}"/></linearGradient>
<radialGradient id="skn" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="{sk[0]}"/><stop offset="1" stop-color="{sk[1]}"/></radialGradient></defs>'''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}{backarm}{legs}{torso}{rif}{head}{frontarm}</svg>'

# ------------------------------------------------------------------ TRUCK
def truck_svg(p=0.0,mood="sweat"):
    W,H=760,430; G=400
    bob=math.sin(2*math.pi*p*2)*5
    s=f'<g transform="translate(0,{f(bob)})">'
    # bed with sandbags
    s+=f'<rect x="40" y="170" width="330" height="95" rx="8" fill="url(#tr)" stroke="{OUT}" stroke-width="{OW}"/><rect x="40" y="170" width="330" height="18" fill="#4d5a3a" stroke="{OUT}" stroke-width="4"/>'
    for i in range(5): s+=f'<ellipse cx="{85+i*62}" cy="160" rx="34" ry="19" fill="#c9b27a" stroke="{OUT}" stroke-width="4"/>'
    # lewis gun
    s+=f'<rect x="196" y="118" width="22" height="48" fill="#3a3a3f" stroke="{OUT}" stroke-width="4"/><path d="M 210 120 L 330 96" stroke="{OUT}" stroke-width="26" stroke-linecap="round"/><path d="M 210 120 L 330 96" stroke="#55585f" stroke-width="16" stroke-linecap="round"/>'
    for i in range(6): s+=f'<path d="M {236+i*14} {113-i*3} l 0 -18" stroke="#2b2c31" stroke-width="3"/>'
    s+=f'<circle cx="236" cy="96" r="28" fill="#3c3d44" stroke="{OUT}" stroke-width="4.5"/><circle cx="236" cy="96" r="10" fill="#6a6d76"/>'
    s+=f'<path d="M 322 98 L 372 90" stroke="{OUT}" stroke-width="12" stroke-linecap="round"/><path d="M 322 98 L 372 90" stroke="#777b84" stroke-width="6" stroke-linecap="round"/>'
    # cab + hood
    s+=f'<path d="M 370 120 L 470 120 L 500 190 L 500 265 L 370 265 Z" fill="url(#tr)" stroke="{OUT}" stroke-width="{OW}" stroke-linejoin="round"/>'
    s+=f'<path d="M 500 190 L 640 190 Q 668 190 668 215 L 668 265 L 500 265 Z" fill="url(#tr)" stroke="{OUT}" stroke-width="{OW}" stroke-linejoin="round"/>'
    s+=f'<path d="M 390 135 L 462 135 L 484 185 L 390 185 Z" fill="#a8d6ee" stroke="{OUT}" stroke-width="4.5"/>'
    # driver
    s+=f'<ellipse cx="438" cy="168" rx="26" ry="28" fill="#f0c9a0" stroke="{OUT}" stroke-width="4"/><ellipse cx="438" cy="136" rx="40" ry="9" fill="#5f4c22" stroke="{OUT}" stroke-width="4"/><path d="M 410 136 Q 412 104 438 104 Q 466 104 468 136 Z" fill="#8a7036" stroke="{OUT}" stroke-width="4"/>'
    s+=f'<circle cx="452" cy="164" r="8" fill="#fff" stroke="{OUT}" stroke-width="3"/><circle cx="455" cy="165" r="3.6" fill="#111"/><path d="M 438 154 L 464 160" stroke="{OUT}" stroke-width="4.5" stroke-linecap="round"/><ellipse cx="452" cy="186" rx="9" ry="7" fill="#6a1f1f" stroke="{OUT}" stroke-width="3"/>'
    s+=f'<path d="M 418 128 q -7 12 0 20 q 8 -7 0 -20 Z" fill="#8fd0ff" stroke="{OUT}" stroke-width="2.5"/>'
    # grille + headlight
    s+=f'<rect x="652" y="200" width="22" height="58" rx="6" fill="#bfc3c9" stroke="{OUT}" stroke-width="4"/><circle cx="660" cy="214" r="13" fill="#ffe98a" stroke="{OUT}" stroke-width="4"/>'
    s+=f'<rect x="20" y="262" width="650" height="22" rx="8" fill="#3a3a3f" stroke="{OUT}" stroke-width="4"/>'
    s+='</g>'
    for cx in (130,545):
        r=64; cy=G-r+bob*0.4
        s+=f'<circle cx="{cx}" cy="{f(cy)}" r="{r}" fill="#1f1f22" stroke="{OUT}" stroke-width="5"/><circle cx="{cx}" cy="{f(cy)}" r="36" fill="#8b8e96" stroke="{OUT}" stroke-width="4"/>'
        for k in range(6):
            a=p*2*math.pi*3+k*math.pi/3
            s+=f'<path d="M {cx} {f(cy)} L {f(cx+math.cos(a)*34)} {f(cy+math.sin(a)*34)}" stroke="#3c3d44" stroke-width="5" stroke-linecap="round"/>'
        s+=f'<circle cx="{cx}" cy="{f(cy)}" r="9" fill="#e5c14a" stroke="{OUT}" stroke-width="3"/>'
    defs='<defs><linearGradient id="tr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7f9763"/><stop offset="1" stop-color="#55683f"/></linearGradient></defs>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{defs}{s}</svg>'

if __name__=="__main__":
    from PIL import Image
    sheet=Image.new("RGBA",(2200,1000),(150,200,230,255))
    x=0
    for i,(m,d) in enumerate([("smug",0),("shock",0),("angry",0.0),("happy",0.0)]):
        im=render(emu_svg(p=i*0.2,mood=m,dip=d,beak=0.6 if m=="shock" else 0),420,480); sheet.alpha_composite(im,(i*400,0))
    im=render(emu_svg(p=.3,mood="derp",dip=1.0,beak=.5,medal=True),420,480); sheet.alpha_composite(im,(1600,0))
    for i,(k,a,m) in enumerate([("soldier","walk","determined"),("major","point","smile"),("farmer","fist","angry"),("soldier","flail","shock")]):
        im=render(person_svg(k,p=i*0.25,arms=a,mood=m,sweat=(i==3)),300,533); sheet.alpha_composite(im,(i*320,480))
    im=render(truck_svg(0.2),760,430); sheet.alpha_composite(im,(1300,560))
    sheet.convert("RGB").save("/home/claude/work/v2/sprites.png")
