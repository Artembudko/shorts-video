import sys, math, random, json, subprocess, wave, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0,os.path.dirname(__file__))
from art import *
from scenery import *

W,H,FPS=1080,1920,30
FONT="/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_CAP=ImageFont.truetype(FONT,84); F_BIG=ImageFont.truetype(FONT,250); F_MID=ImageFont.truetype(FONT,110); F_SM=ImageFont.truetype(FONT,54)

SCENES=[
 "В 1932 году австралийская армия пошла на войну. С птицами.",
 "Двадцать тысяч эму уничтожали фермерскую пшеницу. Тогда правительство отправило солдат, два пулемёта и одного очень уверенного майора.",
 "План был простой. Эму ходят огромными стаями. Целься в стаю. Что может пойти не так?",
 "Но у эму тоже был план. Стоило достать оружие, как стая разбегалась на мелкие группы во все стороны.",
 "Тогда солдаты поставили пулемёт на грузовик и погнались за птицами. Но грузовик был медленным, земля ухабистой, а эму бегают очень быстро.",
 "Через несколько дней армия отступила. Птицы остались. Газеты были в восторге.",
 "Армия вернулась во втором раунде. И эму снова победили. Итоговый счёт: птицы один, армия ноль.",
]
def dur(s): return len(s.split())/2.35+0.8
DURS=[dur(s) for s in SCENES]
if os.path.exists("durs.json"): DURS=json.load(open("durs.json"))
TOTAL=sum(DURS)

def clamp(x,a=0.,b=1.): return max(a,min(b,x))
def lerp(a,b,t): return a+(b-a)*t
def ease(t): t=clamp(t); return t*t*(3-2*t)
def easeout(t): t=clamp(t); return 1-(1-t)**3
def bounce(t):
    t=clamp(t); return 1-math.exp(-6*t)*math.cos(10*t)

# ------------------------------------------------------------ sprite cache
RS=1.25
_sp={}; _rs={}
def sprite(key,fn,w,h):
    if key not in _sp: _sp[key]=render(fn(),int(w*RS),int(h*RS))
    return _sp[key]
def sized(key,img,k):
    kk=(key,round(k,2))
    if kk not in _rs:
        if len(_rs)>6000: _rs.clear()
        w=max(1,int(img.width*k)); h=max(1,int(img.height*k))
        _rs[kk]=img.resize((w,h),Image.LANCZOS if k<1 else Image.BICUBIC)
    return _rs[kk]

def emu_img(p,mood,dip,beak,medal,stride,blink=0):
    pi=int(p*12)%12; di=int(round(dip*6)); bi=int(round(beak*2))
    key=("emu",pi,mood,di,bi,medal,round(stride,2),blink)
    return key,sprite(key,lambda:emu_svg(p=pi/12,mood=mood,dip=di/6,beak=bi/2,medal=medal,stride=stride,blink=blink),560,640)
def person_img(kind,p,arms,mood,sweat,mouth=0):
    pi=int(p*12)%12
    key=("per",kind,pi,arms,mood,sweat,round(mouth,1))
    return key,sprite(key,lambda:person_svg(kind,p=pi/12,arms=arms,mood=mood,sweat=sweat,mouth_open=mouth),360,640)

class Fr:
    def __init__(s,bg): s.im=bg.copy(); s.q=[]
    def put(s,img,x,y,ax,ay,sc,flip=False,rot=0,alpha=1.0,key=None,ysort=None):
        """draw sprite (rendered at RS) with anchor (ax,ay) in viewbox units at screen x,y; sc=px per unit"""
        k=sc/RS; im=sized(key,img,k) if key else img.resize((max(1,int(img.width*k)),max(1,int(img.height*k))),Image.BICUBIC)
        w,h=im.size; axp,ayp=ax*sc,ay*sc
        if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT); axp=w-axp
        if rot:
            pad=int(max(w,h)*0.6); big=Image.new("RGBA",(w+2*pad,h+2*pad),(0,0,0,0)); big.paste(im,(pad,pad))
            big=big.rotate(-rot,resample=Image.BICUBIC,center=(axp+pad,ayp+pad)); im=big; axp+=pad; ayp+=pad
        if alpha<1:
            a=im.getchannel("A").point(lambda v:int(v*alpha)); im=im.copy(); im.putalpha(a)
        s.im.paste(im,(int(x-axp),int(y-ayp)),im)
def shadow(F,x,y,w,a=1.0):
    sh=SH; k=w/sh.width; im=sh.resize((int(w),max(1,int(sh.height*k))),Image.BILINEAR)
    if a<1:
        al=im.getchannel("A").point(lambda v:int(v*a)); im.putalpha(al)
    F.im.paste(im,(int(x-im.width/2),int(y-im.height/2)),im)

SH=None; PUFF=None; ROCK=None; TUMB=None; BOARD=None; PAPER=None; BG={}; FG={}; CLOUDS=None
def init():
    global SH,PUFF,ROCK,TUMB,BOARD,PAPER,CLOUDS
    SH=shadow_img(); PUFF=puff_img(); ROCK=rock_img(); TUMB=tumbleweed_img(); BOARD=board_img(); PAPER=paper_img(); CLOUDS=clouds(5)
    spec=[("dawn",1,(780,770),150),("day",2,(820,420),110),("day",3,(300,380),110),("noon",4,(800,330),100),("noon",6,(240,360),100),("dusk",7,(760,790),150),("day",8,(540,420),120)]
    for i,(n,sd,sun,sr) in enumerate(spec):
        BG[i]=make_bg(n,sd,sun,sr).convert("RGB")
        FG[i]=fg_layer(n,sd+10)

def base(i,t=0.0,cloud=True):
    F=Fr(BG[i].crop((M,0,M+W,H)))
    if cloud and i not in (0,5):
        ox=int((-t*14+200*i)%(W+2*M)); c=CLOUDS
        for sx in (ox-(W+2*M),ox):
            F.im.paste(c,(sx-M,120),c)
    return F
def fg(F,i,dx=0):
    im=FG[i]; F.im.paste(im.crop((M-dx,0,M-dx+W,im.height)),(0,H-im.height),im.crop((M-dx,0,M-dx+W,im.height)))

# ------------------------------------------------------------ draw helpers
def E(F,x,y,s=1.0,p=0.0,mood="smug",dip=0.0,beak=0.0,flip=False,medal=False,stride=1.0,rot=0,blink=0,sh=True):
    key,img=emu_img(p,mood,dip,beak,medal,stride,blink)
    if sh: shadow(F,x,y+4,330*s)
    F.put(img,x,y,225,600,s,flip,rot,key=key)
def Pn(F,kind,x,y,s=1.0,p=0.0,arms="walk",mood="determined",sweat=False,flip=False,rot=0,mouth=0,sh=True):
    key,img=person_img(kind,p,arms,mood,sweat,mouth)
    if sh: shadow(F,x,y+4,230*s)
    F.put(img,x,y,170,610,s,flip,rot,key=key)
def pops(F,x,y,t0,t,txt="!",col=(255,226,58),size=110):
    dt=t-t0
    if dt<0 or dt>1.0: return
    sc=bounce(dt*2.2)*(1-clamp((dt-0.7)/0.3))
    if sc<=0.02: return
    textimg(F,txt,x,y-dt*30,F_MID if size==110 else ImageFont.truetype(FONT,size),col,sc,rot=math.sin(dt*14)*6)
_wc={}
def textimg(F,txt,x,y,font,col=(255,255,255),sc=1.0,rot=0,stroke=12,shadow_=True,alpha=1.0):
    k=(txt,id(font),col,stroke)
    if k not in _wc:
        d=ImageDraw.Draw(Image.new("RGBA",(4,4)))
        bb=d.textbbox((0,0),txt,font=font,stroke_width=stroke); w=bb[2]-bb[0]+40; h=bb[3]-bb[1]+40
        im=Image.new("RGBA",(w,h),(0,0,0,0)); dd=ImageDraw.Draw(im)
        if shadow_: dd.text((20-bb[0]+0,20-bb[1]+9),txt,font=font,fill=(0,0,0,120),stroke_width=stroke,stroke_fill=(0,0,0,120))
        dd.text((20-bb[0],20-bb[1]),txt,font=font,fill=col+(255,),stroke_width=stroke,stroke_fill=(32,20,12,255))
        _wc[k]=im
    im=_wc[k]
    if sc!=1.0: im=im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BICUBIC)
    if rot: im=im.rotate(rot,resample=Image.BICUBIC,expand=True)
    if alpha<1:
        a=im.getchannel("A").point(lambda v:int(v*alpha)); im=im.copy(); im.putalpha(a)
    F.im.paste(im,(int(x-im.width/2),int(y-im.height/2)),im)

_pc={}
def puff(F,x,y,r,a):
    if a<=0.02 or r<2: return
    kk=(int(r/6),int(a*8))
    if kk not in _pc:
        im=PUFF.resize((int(kk[0]*12+12),)*2,Image.BILINEAR); al=im.getchannel("A").point(lambda v:int(v*min(1,kk[1]/8))); im.putalpha(al); _pc[kk]=im
    im=_pc[kk]; F.im.paste(im,(int(x-im.width/2),int(y-im.height/2)),im)
def dust_trail(F,x,y,t,n=9,size=70,dirn=-1,spread=300,speed=1.4):
    for i in range(n):
        u=(t*speed+i/n)%1.0
        puff(F,x+dirn*u*spread,y-18-u*70,size*(0.5+u),(1-u)*0.9)
def speed_lines(F,t,y0,y1,n=14,seed=1,col=(255,255,255),al=90):
    r=random.Random(seed); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for i in range(n):
        y=r.uniform(y0,y1); L=r.uniform(180,420); sp=r.uniform(1800,2800); x=((r.uniform(0,W+L)-t*sp)%(W+L+200))-L
        d.line([x,y,x+L,y],fill=col+(al,),width=int(r.uniform(3,7)))
    F.im.paste(ov,(0,0),ov)

def confetti(F,t,n=60):
    r=random.Random(9); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    cols=[(255,214,60),(255,90,100),(90,200,255),(130,230,120),(255,255,255),(255,150,60)]
    for i in range(n):
        x0=r.uniform(0,W); sp=r.uniform(260,520); ph=r.uniform(0,6); y=((t*sp+r.uniform(0,H+200))%(H+200))-100
        x=x0+math.sin(t*3+ph)*40; a=t*6+ph; w=r.uniform(14,26); h=w*0.5
        c=r.choice(cols)
        pts=[(x+math.cos(a)*w*sx-math.sin(a)*h*sy,y+math.sin(a)*w*sx+math.cos(a)*h*sy) for sx,sy in((-1,-1),(1,-1),(1,1),(-1,1))]
        d.polygon(pts,fill=c+(255,))
    F.im.paste(ov,(0,0),ov)

def pill(F,x,y,txt,font,fill=(30,22,16),fg_=(255,226,58),pad=34,sc=1.0,al=1.0):
    d0=ImageDraw.Draw(Image.new("RGBA",(4,4))); bb=d0.textbbox((0,0),txt,font=font); w=bb[2]-bb[0]+pad*2; h=bb[3]-bb[1]+pad
    ov=Image.new("RGBA",(w+8,h+8),(0,0,0,0)); d=ImageDraw.Draw(ov)
    d.rounded_rectangle([4,4+8,w+4,h+4+8],radius=h//2,fill=(0,0,0,110))
    d.rounded_rectangle([4,4,w+4,h+4],radius=h//2,fill=fill+(255,),outline=(255,255,255,255),width=5)
    d.text((4+pad-bb[0],4+pad//2-bb[1]),txt,font=font,fill=fg_+(255,))
    if sc!=1: ov=ov.resize((max(1,int(ov.width*sc)),max(1,int(ov.height*sc))),Image.BICUBIC)
    F.im.paste(ov,(int(x-ov.width/2),int(y-ov.height/2)),ov)

def positions(n,seed,x0,x1,y0,y1):
    r=random.Random(seed); return [(r.uniform(x0,x1),r.uniform(y0,y1),r.uniform(0,1)) for _ in range(n)]
def depth_s(y,lo=0.36,hi=0.82,y0=980,y1=1300): return lerp(lo,hi,clamp((y-y0)/(y1-y0)))

# ------------------------------------------------------------ scenes (return F, camera)
def s1(t,D):
    F=base(0,t); p=t/D
    # distant marching column
    for k in range(5):
        x=-120+((t*130+k*215)%1500)-200+200
        Pn(F,"major" if k==0 else "soldier",x,1010,0.52,t*1.6+k*.3,"walk","determined")
    # hero emu
    ex=lerp(840,770,easeout(t/1.4)); bl=1 if (t%3.2)>3.05 else 0
    E(F,ex,1380,1.55+0.03*math.sin(t*2),0.25,"smug",0.0,0,flip=True,stride=0.1,blink=bl,rot=math.sin(t*1.6)*1.2)
    fg(F,0)
    # title stamp
    ts=bounce((t-0.25)/0.55)
    if t>0.25: textimg(F,"1932",540,420,F_BIG,(255,236,120),1.12*ts,rot=-5,stroke=16)
    cam=(1.0+0.05*p,ex,1000,0,0)
    return F,cam
def s2(t,D):
    F=base(1,t); p=t/D
    arrive=ease((p-0.52)/0.3)
    ems=positions(15,3,70,1010,990,1250); ems.sort(key=lambda a:a[1])
    items=[]
    for k,(x,y,ph) in enumerate(ems):
        sc=depth_s(y,0.34,0.72,990,1250)
        alert=arrive>0.05
        dp=0.5-0.5*math.cos(2*math.pi*(t/1.7+ph)); dp=0.0 if alert else dp
        bk=1 if (not alert and dp>0.7 and math.sin(t*16+ph*9)>0) else 0
        items.append((y,lambda F,x=x,y=y,sc=sc,dp=dp,bk=bk,k=k,alert=alert:E(F,x,y,sc,0.25,"shock" if alert else "derp",dp,bk,flip=bool(k%2),stride=0.12)))
    items.append((1290,lambda F:Pn(F,"farmer",lerp(-250,210,easeout(t/1.1)),1290,0.92,0,"fist","angry",rot=math.sin(t*12)*2.5)))
    mx=lerp(1400,780,arrive)
    if arrive>0:
        items.append((1330,lambda F:Pn(F,"major",mx,1330,1.0,t*1.8,"walk" if arrive<0.98 else "point","smile")))
        items.append((1290,lambda F:Pn(F,"soldier",mx+220,1290,0.9,t*1.8+.4,"walk","determined")))
        items.append((1260,lambda F:Pn(F,"soldier",mx+400,1260,0.84,t*1.8+.2,"walk","determined")))
    for y,fn in sorted(items,key=lambda a:a[0]): fn(F)
    fg(F,1)
    n=int(20000*ease(t/3.0)); pill(F,540,330,f"{n:,}".replace(","," ")+" ЭМУ",F_MID,sc=bounce(t/0.5))
    cam=(1.0+0.05*p,540,1100,0,0); return F,cam
def s3(t,D):
    F=base(2,t); p=t/D
    # board
    bx,by=400,1290
    F.put(BOARD,bx,by,280,548,1.0,key="board",sh=None) if False else None
    shadow(F,bx,by+6,440)
    bimg=BOARD.copy(); d=ImageDraw.Draw(bimg)
    def chalk(pts,w=7): d.line(pts,fill=(246,246,240,235),width=w,joint="curve")
    # flock icons
    ic=[(160,250),(210,230),(260,255),(190,290),(245,300),(305,275),(150,300)]
    q=ease((t-0.4)/1.0)
    for i,(x,y) in enumerate(ic):
        if q*len(ic)>i:
            d.ellipse([x-22,y-12,x+22,y+14],outline=(246,246,240,235),width=5); d.line([x+14,y-8,x+24,y-40],fill=(246,246,240,235),width=5); d.ellipse([x+16,y-48,x+32,y-36],outline=(246,246,240,235),width=4)
    c=ease((t-1.6)/1.1)
    if c>0:
        pts=[(228+105*math.cos(a),270+66*math.sin(a)) for a in [ -1.2+6.6*c*i/40 for i in range(41)]]; chalk(pts,8)
    a2=ease((t-2.9)/0.7)
    if a2>0:
        chalk([(345,320),(345+80*a2,320+0)],8)
        if a2>0.9: chalk([(425,320),(405,300)],8); chalk([(425,320),(405,340)],8)
    tt=ease((t-0.2)/0.8)
    d.text((280,82),"ПЛАН",font=ImageFont.truetype(FONT,84),fill=(255,236,120,int(255*tt)),anchor="mm")
    F.im.paste(bimg,(int(bx-280),int(by-548)),bimg)
    # major
    Pn(F,"major",110,1300,1.05,0,"point" if t>0.8 else "idle","smile" if t<4 else "determined")
    # flock huddle
    fl=positions(8,4,760,1010,1040,1250); fl.sort(key=lambda a:a[1])
    for k,(x,y,ph) in enumerate(fl):
        sc=depth_s(y,0.55,0.8,1040,1250)
        E(F,x,y+math.sin(t*3+ph*6)*2,sc,0.25,"smug" if t<D-1.8 else "shock",0.0,0,flip=True,stride=0.12,blink=1 if (t*1.3+ph)%2.4>2.3 else 0)
    # target ring around flock
    rr=ease((t-D*0.62)/0.4)
    if rr>0:
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); cx,cy=880,1050; R=int(260*rr*(1+0.04*math.sin(t*9)))
        for w_,col in ((16,(0,0,0,150)),(9,(235,40,50,255))):
            d.ellipse([cx-R,cy-R*0.75,cx+R,cy+R*0.75],outline=col,width=w_)
            d.line([cx-R-40,cy,cx+R+40,cy],fill=col,width=w_//2+1); d.line([cx,cy-R*0.75-40,cx,cy+R*0.75+40],fill=col,width=w_//2+1)
        F.im.paste(ov,(0,0),ov)
    fg(F,2); cam=(1.0+0.06*p,540,1080,0,0); return F,cam
def s4(t,D):
    F=base(3,t); p=t/D
    T0=1.0
    r=random.Random(12); items=[]
    for k in range(15):
        a=r.uniform(0,6.28); V=r.uniform(520,980); x0=540+r.uniform(-130,130); y0=1100+r.uniform(-60,110); vy=r.uniform(-200,230)
        ph=r.uniform(0,1)
        if t<T0:
            x,y=x0,y0; mood="smug"; run=0
        else:
            dt=t-T0; vx=math.cos(a)*V; x=x0+vx*dt; y=clamp(y0+vy*dt,960,1330); mood="shock" if dt<0.5 else "derp"; run=1
        if x<-300 or x>1380: continue
        sc=depth_s(y,0.4,0.88,960,1330)
        items.append((y,x,sc,mood,run,ph,math.cos(a)<0))
    for y,x,sc,mood,run,ph,fl in sorted(items,key=lambda a:a[0]):
        if run: E(F,x,y,sc,t*(2.6)+ph,mood,0,0.5 if mood=="shock" else 0,flip=fl,stride=1.1)
        else: E(F,x,y,sc,0.25,mood,0,0,flip=bool(ph>0.5),stride=0.12,blink=1 if (t*1.3+ph)%2.4>2.3 else 0)
    # dust burst at scatter
    if t>T0:
        dt=t-T0
        for i in range(10):
            a=i*0.63; puff(F,540+math.cos(a)*dt*330,1140+math.sin(a)*dt*60,70+dt*100,max(0,1-dt/1.1)*0.9)
    # soldiers confused
    sh=ease((t-T0-0.3)/0.3)
    for k,x in enumerate((150,330,500)):
        Pn(F,"soldier",x,1300+k*12,0.95-k*0.05,0,"flail" if t>T0 else "idle","shock" if t>T0 else "determined",sweat=t>T0+0.6,mouth=0.6 if t>T0 else 0)
    if t>T0: 
        pops(F,170,760,T0+0.2,t,"?!",(255,226,58),120); pops(F,360,800,T0+0.6,t,"?",(255,255,255),130); pops(F,520,840,T0+0.9,t,"!",(255,90,90),130)
    # tumbleweed
    tw=lerp(1300,-400,clamp((t-D*0.55)/(D*0.45)))
    if t>D*0.55: F.put(TUMB.rotate(-(t*260)%360,resample=Image.BICUBIC),tw,1330,130,130,0.8*RS/RS*1.0) if False else F.im.paste((lambda im:im)(TUMB.resize((200,200)).rotate(-(t*260)%360,resample=Image.BICUBIC)),(int(tw-100),1200),TUMB.resize((200,200)).rotate(-(t*260)%360,resample=Image.BICUBIC))
    fg(F,3)
    shake=(random.Random(int(t*30)).uniform(-14,14),random.Random(int(t*30)+99).uniform(-10,10)) if T0<t<T0+0.5 else (0,0)
    cam=(1.0+0.05*p+(0.08*math.exp(-(t-T0)*6) if t>T0 else 0),540,1100,shake[0],shake[1]); return F,cam
def s5(t,D):
    p=t/D; bg=BG[4]; F=Fr(Image.new("RGB",(W,H)))
    sx=M+int(min(t*18,190)); F.im.paste(bg.crop((sx,0,sx+W,H)),(0,0))
    ox=int((-t*14+400)%(W+2*M)); 
    for sx in (ox-(W+2*M),ox): F.im.paste(CLOUDS,(sx-M,120),CLOUDS)
    # emus ahead
    tx=lerp(330,90,ease(p)); tyy=1250
    ems=[(820,1180,0.0),(940,1250,0.3),(1040,1160,0.6),(880,1215,0.15)]
    for k,(x,y,ph) in enumerate(sorted(ems,key=lambda a:a[1])):
        xx=x+t*lerp(18,60,p)*(1+k*0.2)
        mood="happy" if k==1 and t>D*0.5 else "smug"
        E(F,xx,y+math.sin(t*20+ph*6)*3,0.78 if y>1200 else 0.66,t*2.6+ph,mood,0,0.3 if k==3 else 0,stride=1.2)
        dust_trail(F,xx-80,y+4,t+ph,6,40,-1,200)
    # rock jolt
    rt=D*0.42; jolt=max(0,1-abs(t-rt)/0.28)
    rx=lerp(1500,-500,clamp((t-(rt-1.5))/3.0))
    tk=sprite(("truck",int(t*8)%8),lambda:truck_svg((int(t*8)%8)/8),760,430)
    dust_trail(F,tx-150,tyy+6,t,10,90,-1,420,1.8)
    shadow(F,tx,tyy+10,520)
    F.put(tk,tx,tyy-jolt*60,380,400,0.95,False,-jolt*3,key=("truck",int(t*8)%8))
    F.im.paste(ROCK.resize((260,173)),(int(rx-130),1258),ROCK.resize((260,173)))
    speed_lines(F,t,1000,1500,16,3)
    # foreground scrolling tufts
    fgl=FG[4]; sc=int(t*520)%(W+2*M)
    strip=Image.new("RGBA",(W+2*M,fgl.height)); strip.paste(fgl,(-sc,0)); strip.paste(fgl,(W+2*M-sc,0))
    F.im.paste(strip.crop((M,0,M+W,fgl.height)),(0,H-fgl.height),strip.crop((M,0,M+W,fgl.height)))
    if t>0.5 and t<2.0: pass
    shake=(math.sin(t*50)*5,math.cos(t*43)*5) 
    cam=(1.04,540,1150,shake[0]*(1+jolt*2),shake[1]*(1+jolt*2)); return F,cam
def s6(t,D):
    F=base(5,t); p=t/D
    tx=lerp(620,-450,ease((t-0.2)/(D*0.75))); 
    tk=sprite(("truck",int(t*6)%8),lambda:truck_svg((int(t*6)%8)/8),760,430)
    dust_trail(F,tx+200,1262,t,8,80,+1,360,1.2)
    shadow(F,tx,1272,520); F.put(tk,tx,1262,380,400,0.95,True,key=("truck",int(t*6)%8))
    ems=positions(6,5,560,1020,1060,1280); ems.sort(key=lambda a:a[1])
    for k,(x,y,ph) in enumerate(ems):
        hop=abs(math.sin(t*5+ph*6))*14 if t>0.8 else 0
        E(F,x,y-hop,depth_s(y,.6,.82,1060,1280),0.25,"happy" if t>0.8 else "smug",0.0,0.5 if int(t*6+ph*5)%2 else 0,flip=True,stride=0.12)
    fg(F,5)
    ps=bounce((t-1.2)/0.5)
    if t>1.2:
        pimg=PAPER.copy(); d=ImageDraw.Draw(pimg)
        d.text((360,70),"ВЕСТИ ДНЯ",font=ImageFont.truetype(FONT,60),fill=(246,240,220),anchor="mm")
        d.text((360,170),"АРМИЯ ОТСТУПАЕТ!",font=ImageFont.truetype(FONT,54),fill=(190,40,40),anchor="mm")
        ek,ei=emu_img(0.25,"happy",0,0.5,False,0.12); em=ei.resize((190,217),Image.LANCZOS); pimg.paste(em,(500,300),em)
        F.put(pimg,540,520,360,280,1.0*ps,False,rot=(1-ps)*-540+math.sin(t*2)*2)
    cam=(1.0+0.05*p,540,1100,0,0); return F,cam
def s7(t,D):
    F=base(6,t); p=t/D
    # soldiers sulking in back
    for k,x in enumerate((130,300)):
        Pn(F,"soldier",x,1130+k*20,0.62,0,"shrug" if k==0 else "idle","sad")
    Pn(F,"major",470,1100,0.6,0,"shrug","sad")
    jump=abs(math.sin(t*3.2))*30 if t>1.4 else 0
    E(F,720,1340-jump,1.45,0.25,"happy" if int(t*1.2)%2==0 else "smug",0.0,0.0,flip=True,medal=True,stride=0.1)
    fg(F,6)
    confetti(F,t) if t>1.2 else None
    sb=easeout((t-1.0)/0.6)
    if sb>0:
        ov=Image.new("RGBA",(W,300),(0,0,0,0)); d=ImageDraw.Draw(ov)
        d.rounded_rectangle([60,14,1020,284],radius=40,fill=(0,0,0,120)); d.rounded_rectangle([60,0,1020,270],radius=40,fill=(32,24,18,255),outline=(255,226,58,255),width=8)
        d.text((130,70),"ПТИЦЫ",font=F_MID,fill=(255,255,255),anchor="lm"); d.text((130,196),"АРМИЯ",font=ImageFont.truetype(FONT,84),fill=(190,190,190),anchor="lm")
        sc1=1+0.35*math.exp(-(t-D*0.62)*5) if t>D*0.62 else 1
        d.text((910,70),"1" if t>D*0.62 else "0",font=ImageFont.truetype(FONT,int(120*sc1)),fill=(255,226,58),anchor="mm"); d.text((910,196),"0",font=ImageFont.truetype(FONT,84),fill=(190,190,190),anchor="mm")
        F.im.paste(ov,(0,int(lerp(-320,180,sb))),ov)
    # round-two banner at start
    if t<1.5:
        bx=lerp(1400,-700,clamp(t/1.3)); 
        textimg(F,"РАУНД 2",bx,520,F_BIG if False else ImageFont.truetype(FONT,190),(255,90,100),1.0,rot=-4,stroke=14)
    cam=(1.0+0.05*p,540,1100,0,0); return F,cam

SCENE_FN=[s1,s2,s3,s4,s5,s6,s7]

# ------------------------------------------------------------ captions
_wimg={}
def wimg(w,col):
    k=(w,col)
    if k not in _wimg:
        d0=ImageDraw.Draw(Image.new("RGBA",(4,4))); bb=d0.textbbox((0,0),w,font=F_CAP,stroke_width=14)
        im=Image.new("RGBA",(bb[2]-bb[0]+24,bb[3]-bb[1]+24),(0,0,0,0)); d=ImageDraw.Draw(im)
        d.text((12-bb[0],12-bb[1]+8),w,font=F_CAP,fill=(0,0,0,140),stroke_width=14,stroke_fill=(0,0,0,140))
        d.text((12-bb[0],12-bb[1]),w,font=F_CAP,fill=col+(255,),stroke_width=14,stroke_fill=(30,18,10,255))
        _wimg[k]=(im,bb[2]-bb[0],bb[3]-bb[1])
    return _wimg[k]
def chunks_for(words):
    ch=[];k=0;d0=ImageDraw.Draw(Image.new("RGBA",(4,4)))
    while k<len(words):
        n=1
        while n<3 and k+n<len(words) and d0.textlength(" ".join(words[k:k+n+1]).upper(),font=F_CAP)<=860: n+=1
        if k+n<len(words) and n==1 and len(words[k+1])<=3: n=2
        ch.append((k,k+n)); k+=n
    return ch
def caption(F,i,t):
    words=SCENES[i].split(); T=DURS[i]-0.55
    wt=[len(w)+(7 if w[-1] in ".!?" else 3 if w[-1] in ",:" else 0)+2 for w in words]; tot=sum(wt); st=[];acc=0
    for w in wt: st.append(0.18+acc/tot*T); acc+=w
    cur=max([k for k,s in enumerate(st) if s<=t] or [0]); dt=t-st[cur]
    a,b=[c for c in chunks_for(words) if c[0]<=cur<c[1]][0]
    ws=[x.upper() for x in words[a:b]]
    ims=[wimg(w,(255,224,58) if a+j==cur else (255,255,255)) for j,w in enumerate(ws)]
    sp=26; tw=sum(m[1] for m in ims)+sp*(len(ims)-1); x=(W-tw)/2; y=1500
    for j,(im,w,h) in enumerate(ims):
        if a+j==cur:
            k=1+0.16*math.exp(-dt*14)
            im2=im.resize((int(im.width*k),int(im.height*k)),Image.BICUBIC)
            F.im.paste(im2,(int(x+w/2-im2.width/2),int(y-im2.height/2-6)),im2)
        else: F.im.paste(im,(int(x-12),int(y-im.height/2)),im)
        x+=w+sp

# ------------------------------------------------------------ post
VIG=None; NOISE=None
def post_init():
    global VIG,NOISE
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); d=np.sqrt(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.7))**2)
    VIG=(1-0.38*np.clip(d-0.35,0,1)**1.6)[...,None]
    NOISE=[(np.random.RandomState(s).randn(H//2,W//2)*1.1).astype(np.float32) for s in range(6)]
def post(img,cam,k):
    z,cx,cy,dx,dy=cam
    a=np.asarray(img.im)
    if z!=1.0 or dx or dy:
        M_=np.float32([[z,0,(1-z)*cx+dx],[0,z,(1-z)*cy+dy]]); a=cv2.warpAffine(a,M_,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    a=a.astype(np.float32)*VIG
    n=cv2.resize(NOISE[k%6],(W,H),interpolation=cv2.INTER_NEAREST)[...,None]
    return np.clip(a+n,0,255).astype(np.uint8)

def frame(i,t):
    F,cam=SCENE_FN[i](t,DURS[i]); caption(F,i,t)
    kick=1.0+0.07*math.exp(-t*10); cam=(cam[0]*kick,)+cam[1:]
    a=post(F,cam,int(t*FPS))
    if t<0.18 and i>0: a=(a*(t/0.18)).astype(np.uint8)
    if i==len(SCENES)-1 and DURS[i]-t<0.4: a=(a*max(0,(DURS[i]-t)/0.4)).astype(np.uint8)
    return a

# ------------------------------------------------------------ audio
def audio(path):
    sr=44100; n=int((TOTAL+0.2)*sr); t=np.arange(n)/sr; out=np.zeros(n); bpm=116; beat=60/bpm
    bass=[110,110,146.8,130.8,110,110,164.8,146.8]; mel=[440,523,587,523,440,392,440,0, 440,523,659,587,523,440,392,0]
    def add(s,sig):
        s=int(s*sr)
        if s<0 or s>=n: return
        e=min(n,s+len(sig)); out[s:e]+=sig[:e-s]
    for k in range(int(TOTAL/beat)+2):
        tt=k*beat; L=int(beat*0.85*sr); x=np.arange(L)/sr; f=bass[k%8]
        add(tt,(np.sin(2*np.pi*f*x)+0.35*np.sin(4*np.pi*f*x))*np.exp(-x*6)*0.30)
        fm=mel[(k*2)%16]
        for h in (0,1):
            fm=mel[(k*2+h)%16]
            if fm:
                L2=int(beat*0.5*sr); x2=np.arange(L2)/sr
                add(tt+h*beat/2,(np.sin(2*np.pi*fm*x2)+0.5*np.sin(2*np.pi*fm*3.99*x2)*np.exp(-x2*30))*np.exp(-x2*9)*0.10)
        if k%2==1:
            L3=int(0.12*sr); x3=np.arange(L3)/sr; add(tt,np.random.RandomState(k).randn(L3)*np.exp(-x3*28)*0.12)
        L4=int(0.04*sr); x4=np.arange(L4)/sr; add(tt+beat/2,np.random.RandomState(k+50).randn(L4)*np.exp(-x4*90)*0.06)
    # sfx
    acc=0
    for i,d in enumerate(DURS):
        if i>0:
            L=int(0.35*sr); x=np.arange(L)/sr; nz=np.random.RandomState(i).randn(L); env=np.sin(np.pi*x/0.35)**2
            w=np.convolve(nz,np.ones(int(30+200*x[-1]))/ (30+200*x[-1]),mode="same")*env*0.45; add(acc-0.1,w)
        acc+=d
    L=int(0.3*sr); x=np.arange(L)/sr; add(0.25,np.sin(2*np.pi*(90-60*x)*x*3)*np.exp(-x*12)*0.7)       # stamp thud
    st=sum(DURS[:3])+1.0; L=int(0.5*sr); x=np.arange(L)/sr; add(st,np.sin(2*np.pi*(300+500*x)*x)*np.exp(-x*7)*0.35)  # scatter boing
    en=sum(DURS[:6])+DURS[6]*0.62; L=int(0.9*sr); x=np.arange(L)/sr
    for j,fq in enumerate((523,659,784,1046)): add(en+j*0.09,np.sin(2*np.pi*fq*x[:L-int(j*0.09*sr)])*np.exp(-x[:L-int(j*0.09*sr)]*4)*0.18)
    out*=np.minimum(1,np.minimum(t/0.4,(TOTAL+0.2-t)/1.0))
    out=np.tanh(out*1.1)*0.85
    pcm=(np.clip(out,-1,1)*32767).astype(np.int16)
    with wave.open(path,"wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())

if __name__=="__main__":
    init(); post_init()
    mode=sys.argv[1]
    if mode=="preview":
        sel=[(0,1.6),(1,1.5),(1,6.0),(2,5.5),(3,1.6),(4,3.0),(5,3.0),(6,4.5)]
        ims=[Image.fromarray(frame(i,t)).resize((405,720)) for i,t in sel]
        sheet=Image.new("RGB",(405*4,720*2))
        for k,im in enumerate(ims): sheet.paste(im,((k%4)*405,(k//4)*720))
        sheet.save("preview.png"); print(DURS,TOTAL)
    elif mode=="render":
        audio("a.wav")
        cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i","a.wav","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart","tmp.mp4"]
        pr=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for i in range(len(SCENES)):
            for fi in range(int(DURS[i]*FPS)): pr.stdin.write(frame(i,fi/FPS).tobytes())
        pr.stdin.close(); print("rc",pr.wait())
