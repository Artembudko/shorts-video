import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from art import render, OUT, blob, f

W,H=1080,1920; HOR=860; M=200  # margin for parallax
PALS={
 "day":dict(top="#3b9bec",hor="#d4f0ff",sun="#fff7cc",glow="#fff2a8",far="#9db4dc",far2="#b7c8e8",mid="#d08a5a",mid2="#b8734a",tree="#6f8a6a",tree2="#8fa584",fa="#ecd079",fb="#c7923c",st="#b8802f",gr="#6d5a26"),
 "dawn":dict(top="#6657b5",hor="#ffc48f",sun="#fff0b8",glow="#ffd27a",far="#a78ac0",far2="#c49bb8",mid="#c8704f",mid2="#a85a45",tree="#5f6a67",tree2="#7a8078",fa="#f2c27a",fb="#c4803a",st="#a96b2a",gr="#5a4422"),
 "dusk":dict(top="#4a3f8f",hor="#ffb27d",sun="#ffe2a0",glow="#ffb36b",far="#8c6fa8",far2="#a67fa6",mid="#b2604c",mid2="#8f4d45",tree="#4f5a5e",tree2="#667072",fa="#e3b06a",fb="#b36f35",st="#945c25",gr="#4d3a1f"),
 "noon":dict(top="#2c8fe8",hor="#c6e9ff",sun="#fffbd8",glow="#fff6b0",far="#92aedc",far2="#aec3e6",mid="#cf8858",mid2="#b9714a",tree="#6a8964",tree2="#8aa57f",fa="#f0d37a",fb="#cf9a40",st="#bd8530",gr="#6a5726"),
}
def ridge(seed,y0,amp,wavs,xs0=-M,xs1=W+M,step=60):
    r=random.Random(seed); ph=[r.uniform(0,6.28) for _ in wavs]; pts=[]
    x=xs0
    while x<=xs1+step:
        y=y0
        for (wl,a),p in zip(wavs,ph): y-=a*amp*(0.5+0.5*math.sin(x/wl+p))
        pts.append((x,y)); x+=step
    d=f"M {pts[0][0]} {H} L {pts[0][0]} {f(pts[0][1])} "
    for i in range(1,len(pts)-1):
        p=pts[i]; q=pts[i+1]; d+=f"Q {f(p[0])} {f(p[1])} {f((p[0]+q[0])/2)} {f((p[1]+q[1])/2)} "
    return d+f"L {pts[-1][0]} {H} Z"

def tree(x,y,s,c1,c2,seed):
    r=random.Random(seed); g=f'<g transform="translate({x},{y}) scale({s})">'
    g+=f'<path d="M -6 0 Q -10 -60 -2 -120 Q 4 -150 14 -190" stroke="#4a3a30" stroke-width="12" fill="none" stroke-linecap="round"/>'
    g+=f'<path d="M 0 -100 Q 30 -130 52 -150" stroke="#4a3a30" stroke-width="7" fill="none" stroke-linecap="round"/>'
    for cx,cy,rx,ry in [(10,-205,70,34),(-34,-170,56,28),(62,-168,58,30),(48,-150,40,22)]:
        g+=f'<path d="{blob(cx,cy,rx,ry,18,0.14,r.randint(0,99))}" fill="{c1}"/><path d="{blob(cx+4,cy-8,rx*0.7,ry*0.55,14,0.14,r.randint(0,99))}" fill="{c2}"/>'
    return g+'</g>'

def clouds(seed,n=5,w=W+2*M):
    r=random.Random(seed); s=""
    for i in range(n):
        cx=r.uniform(0,w); cy=r.uniform(40,360); k=r.uniform(.8,1.5); g=f'<g transform="translate({cx},{cy}) scale({k})">'
        for dx,dy,rr in [(-90,10,48),(-40,-10,64),(20,-22,74),(80,0,56),(120,14,40),(-5,18,60)]:
            g+=f'<circle cx="{dx}" cy="{dy+8}" r="{rr}" fill="#c9dcf0"/>'
        for dx,dy,rr in [(-90,10,48),(-40,-10,64),(20,-22,74),(80,0,56),(120,14,40),(-5,18,60)]:
            g+=f'<circle cx="{dx}" cy="{dy}" r="{rr}" fill="#fff"/>'
        s+=g+'</g>'
    return render(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 460" width="{w}" height="460">{s}</svg>',w,460)

def make_bg(name,seed=1,sun=(800,470),sun_r=120,trees=True):
    P=PALS[name]; r=random.Random(seed)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-M} 0 {W+2*M} {H}" width="{W+2*M}" height="{H}"><defs>'
    svg+=f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["top"]}"/><stop offset="1" stop-color="{P["hor"]}"/></linearGradient>'
    svg+=f'<radialGradient id="glow"><stop offset="0" stop-color="{P["glow"]}" stop-opacity=".95"/><stop offset=".4" stop-color="{P["glow"]}" stop-opacity=".35"/><stop offset="1" stop-color="{P["glow"]}" stop-opacity="0"/></radialGradient>'
    svg+=f'<linearGradient id="gd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["fa"]}"/><stop offset="1" stop-color="{P["fb"]}"/></linearGradient>'
    svg+=f'<linearGradient id="far" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["far2"]}"/><stop offset="1" stop-color="{P["far"]}"/></linearGradient>'
    svg+=f'<linearGradient id="mid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["mid"]}"/><stop offset="1" stop-color="{P["mid2"]}"/></linearGradient>'
    svg+=f'<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["hor"]}" stop-opacity="0"/><stop offset="1" stop-color="{P["hor"]}" stop-opacity=".75"/></linearGradient></defs>'
    svg+=f'<rect x="{-M}" y="0" width="{W+2*M}" height="{HOR+4}" fill="url(#sky)"/>'
    svg+=f'<circle cx="{sun[0]}" cy="{sun[1]}" r="{sun_r*3.2}" fill="url(#glow)"/><circle cx="{sun[0]}" cy="{sun[1]}" r="{sun_r}" fill="{P["sun"]}"/>'
    svg+=f'<path d="{ridge(seed,HOR-22,150,[(260,.55),(130,.3),(70,.15)])}" fill="url(#far)"/>'
    svg+=f'<rect x="{-M}" y="{HOR-160}" width="{W+2*M}" height="170" fill="url(#haze)"/>'
    svg+=f'<path d="{ridge(seed+5,HOR+6,86,[(190,.55),(90,.3),(45,.15)])}" fill="url(#mid)"/>'
    if trees:
        for i in range(9):
            x=r.uniform(-M+40,W+M-40); s=r.uniform(.32,.6); svg+=tree(x,HOR+14+r.uniform(-8,10),s,P["tree"],P["tree2"],i+seed)
    svg+=f'<rect x="{-M}" y="{HOR-20}" width="{W+2*M}" height="40" fill="url(#haze)" opacity=".3"/>'
    # ground
    svg+=f'<rect x="{-M}" y="{HOR+8}" width="{W+2*M}" height="{H-HOR}" fill="url(#gd)"/>'
    vx=W/2
    for i in range(-26,27):
        x0=vx+i*26; x1=vx+i*190
        if i%2==0:
            svg+=f'<polygon points="{x0},{HOR+8} {x0+26},{HOR+8} {x1+190},{H} {x1},{H}" fill="{P["st"]}" opacity=".16"/>'
    for k in range(14):
        y=HOR+8+((k/14)**1.8)*(H-HOR); svg+=f'<rect x="{-M}" y="{f(y)}" width="{W+2*M}" height="{f(3+k*1.5)}" fill="#fff" opacity=".05"/>'
    n=2600
    for i in range(n):
        u=r.random()**0.8; y=HOR+14+u*(H-HOR-14); t=(y-HOR)/(H-HOR)
        x=r.uniform(-M,W+M); L=5+60*t**1.2; lean=r.uniform(-.35,.35)
        col=r.choice([P["fa"],"#fff3b8",P["fb"],P["st"],"#e8c460"])
        svg+=f'<path d="M {f(x)} {f(y)} q {f(lean*L*.4)} {f(-L*.55)} {f(lean*L)} {f(-L)}" stroke="{col}" stroke-width="{f(1.2+3.2*t)}" stroke-linecap="round" fill="none" opacity="{f(.5+.4*r.random())}"/>'
    svg+=f'<rect x="{-M}" y="{HOR+8}" width="{W+2*M}" height="60" fill="url(#haze)" opacity=".18"/></svg>'
    return render(svg,W+2*M,H)

def fg_layer(name,seed=3,h=330):
    P=PALS[name]; r=random.Random(seed)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-M} {H-h} {W+2*M} {h}" width="{W+2*M}" height="{h}"><defs><linearGradient id="bl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{P["fa"]}"/><stop offset="1" stop-color="{P["gr"]}"/></linearGradient><linearGradient id="sh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#1a0f05" stop-opacity=".55"/></linearGradient></defs>'
    svg+=f'<rect x="{-M}" y="{H-h}" width="{W+2*M}" height="{h}" fill="url(#sh)"/>'
    for i in range(34):
        x=r.uniform(-M,W+M); s=r.uniform(.7,1.5); y=H+10
        for b in range(7):
            a=r.uniform(-.5,.5); L=r.uniform(120,250)*s
            ex=x+math.sin(a)*L; ey=y-math.cos(a)*L
            svg+=f'<path d="M {f(x+b*5-15)} {y} Q {f(x+math.sin(a)*L*.4+b*4-12)} {f(y-L*.6)} {f(ex)} {f(ey)}" stroke="{OUT}" stroke-width="{f(9*s)}" stroke-linecap="round" fill="none"/>'
            svg+=f'<path d="M {f(x+b*5-15)} {y} Q {f(x+math.sin(a)*L*.4+b*4-12)} {f(y-L*.6)} {f(ex)} {f(ey)}" stroke="url(#bl)" stroke-width="{f(5.5*s)}" stroke-linecap="round" fill="none"/>'
    svg+='</svg>'
    return render(svg,W+2*M,h)

def rock_img(seed=1,w=240):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 160"><defs><linearGradient id="r" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bda68e"/><stop offset="1" stop-color="#7d6755"/></linearGradient></defs><path d="M 10 150 Q 6 90 56 60 Q 100 20 160 44 Q 224 64 232 150 Z" fill="url(#r)" stroke="{OUT}" stroke-width="6" stroke-linejoin="round"/><path d="M 60 70 Q 100 40 150 56" stroke="#e6d6bf" stroke-width="7" fill="none" stroke-linecap="round" opacity=".7"/></svg>'
    return render(svg,w,int(w*160/240))

def tumbleweed_img(w=260):
    r=random.Random(4); s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 260"><circle cx="130" cy="130" r="112" fill="#a9824a" opacity=".25"/>'
    for i in range(46):
        a=r.uniform(0,6.28); b=a+r.uniform(1.2,2.6); rr=r.uniform(80,118)
        s+=f'<path d="M {130+math.cos(a)*rr:.0f} {130+math.sin(a)*rr:.0f} Q {130+r.uniform(-50,50):.0f} {130+r.uniform(-50,50):.0f} {130+math.cos(b)*rr:.0f} {130+math.sin(b)*rr:.0f}" stroke="{OUT if i%3==0 else "#8a6532"}" stroke-width="{3 if i%3==0 else 4}" fill="none" stroke-linecap="round"/>'
    return render(s+'</svg>',w,w)

def puff_img(w=256):
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><defs><radialGradient id="p"><stop offset="0" stop-color="#f0dcb4" stop-opacity=".95"/><stop offset=".6" stop-color="#e0c496" stop-opacity=".7"/><stop offset="1" stop-color="#d4b484" stop-opacity="0"/></radialGradient></defs><circle cx="128" cy="128" r="124" fill="url(#p)"/></svg>'
    return render(svg,w,w)

def shadow_img(w=400,h=70):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><defs><radialGradient id="s"><stop offset="0" stop-color="#2a1608" stop-opacity=".55"/><stop offset=".7" stop-color="#2a1608" stop-opacity=".3"/><stop offset="1" stop-color="#2a1608" stop-opacity="0"/></radialGradient></defs><ellipse cx="{w/2}" cy="{h/2}" rx="{w/2}" ry="{h/2}" fill="url(#s)"/></svg>'
    return render(svg,w,h)

def board_img():
    w,h=560,560
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><defs><linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2f5a47"/><stop offset="1" stop-color="#1f3f32"/></linearGradient></defs>
<path d="M 120 380 L 70 548 M 440 380 L 490 548 M 280 380 L 280 548" stroke="{OUT}" stroke-width="26" stroke-linecap="round"/><path d="M 120 380 L 70 548 M 440 380 L 490 548 M 280 380 L 280 548" stroke="#9c6b3c" stroke-width="16" stroke-linecap="round"/>
<rect x="20" y="20" width="520" height="380" rx="16" fill="#9c6b3c" stroke="{OUT}" stroke-width="7"/><rect x="42" y="42" width="476" height="336" rx="8" fill="url(#bd)" stroke="{OUT}" stroke-width="5"/>
<rect x="60" y="392" width="440" height="22" rx="6" fill="#b88049" stroke="{OUT}" stroke-width="5"/><rect x="90" y="378" width="50" height="14" rx="3" fill="#f4f4f0" stroke="{OUT}" stroke-width="3"/></svg>'''
    return render(svg,w,h)

def paper_img(w=720,h=560):
    r=random.Random(2)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><rect x="6" y="6" width="{w-12}" height="{h-12}" rx="10" fill="#f6f0dc" stroke="{OUT}" stroke-width="7"/><rect x="26" y="26" width="{w-52}" height="86" fill="#2a1c14"/>'
    svg+=f'<rect x="26" y="232" width="{w-52}" height="4" fill="{OUT}"/>'
    for i in range(7): svg+=f'<rect x="{40}" y="{262+i*30}" width="{r.randint(180,300)}" height="10" rx="4" fill="#8d8470" opacity=".7"/>'
    for i in range(7): svg+=f'<rect x="{w-300}" y="{262+i*30}" width="{r.randint(140,250)}" height="10" rx="4" fill="#8d8470" opacity=".7"/>'
    svg+='</svg>'
    return render(svg,w,h)
