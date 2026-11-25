import sys, os, math, random, json, subprocess, wave
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import make2 as m
from art3 import *
from scenery import clouds as mk_clouds, shadow_img, puff_img, M, W, H, HOR
from make2 import clamp, lerp, ease, easeout, bounce, F_MID, F_SM, F_BIG, FONT, positions, textimg, pill, puff, confetti

m.SCENES=[
 "По легенде, в британском Дели развелось слишком много кобр. И чиновники придумали гениальный план.",
 "За каждую мёртвую кобру город платил награду. Горожане взялись за дело, и сначала всё работало.",
 "Но потом кто-то понял: ловить кобр опасно. А вот разводить их дома, в корзинах, гораздо проще.",
 "Так появились змеиные фермы. Люди растили кобр, сдавали за награду и снова растили. Чиновники радовались отчётам.",
 "Но скоро власти раскусили схему и отменили награду. Змеи вдруг стали никому не нужны.",
 "И тогда хозяева ферм просто выпустили их на улицы. Кобр в городе стало больше, чем когда-либо.",
 "План против кобр умножил кобр. Это называют эффектом кобры: решение, которое делает проблему только хуже.",
]
m.DURS=[m.dur(s) for s in m.SCENES]
if os.path.exists("durs.json"): m.DURS=json.load(open("durs.json"))
m.TOTAL=sum(m.DURS)
DURS=m.DURS

# ------------------------------------------------------------ assets
SIGN=None; BUBBLE=None
def init3():
    m.SH=shadow_img(); m.PUFF=puff_img(); m.CLOUDS=mk_clouds(5)
    spec=[("day",1,(820,400)),("day",2,(300,380)),("noon",3,(760,350)),("noon",4,(280,360)),("dusk",5,(780,780)),("dusk",6,(300,760)),("day",7,(540,380))]
    for i,(n,sd,sun) in enumerate(spec):
        m.BG[i]=city_street(n,sd,sun).convert("RGB"); m.FG[i]=fg_city(n,sd+10)
    global SIGN
    SIGN=render(sign_svg(),int(440*m.RS),int(680*m.RS)); d=ImageDraw.Draw(SIGN); R=m.RS
    f1=ImageFont.truetype(FONT,int(46*R)); f2=ImageFont.truetype(FONT,int(52*R))
    d.text((220*R,104*R),"ЗА КОБРУ",font=f1,fill=(60,36,20),anchor="mm")
    d.text((220*R,176*R),"НАГРАДА!",font=f2,fill=(200,40,40),anchor="mm")
    coin=render(coin_svg(),int(70*R),int(70*R)); SIGN.paste(coin,(int(185*R),int(235*R)),coin)

def base3(i,t,cl=True):
    F=m.Fr(m.BG[i].crop((M,0,M+W,H)))
    if cl:
        ox=int((-t*14+200*i)%(W+2*M)); c=m.CLOUDS
        for sx in (ox-(W+2*M),ox): F.im.paste(c,(sx-M,90),c)
    return F

# ------------------------------------------------------------ draw helpers
def C(F,x,y,s,sway=0.0,rise=1.0,mood="sly",tongue=0,flare=1.0,coil=True,flip=False,sh=True,rot=0):
    si=int(round(clamp(sway,-1,1)*3)); ri=int(round(clamp(rise,0.3,1)*4))
    key=("cobra",si,ri,mood,tongue,round(flare,1),coil)
    img=m.sprite(key,lambda:cobra_up_svg(si/3,ri/4,mood,tongue,flare,coil),460,640)
    if sh and coil: m.shadow(F,x,y+4,300*s)
    F.put(img,x,y,230,590,s,flip,rot,key=key)
def Cs(F,x,y,s,ph,flip=False,tongue=0):
    pi=int(ph*12)%12
    key=("cs",pi,tongue); img=m.sprite(key,lambda:cobra_slither_svg(pi/12,"sly",tongue),620,330)
    m.shadow(F,x,y+6,330*s,0.9)
    F.put(img,x,y,300,300,s,flip,key=key)
def Bk(F,x,y,s,cobra=True,sway=0.0,rise=0.8,mood="sly",tongue=0,flip=False):
    if s<0.08: return
    back=m.sprite("bkb",lambda:basket_svg("back"),260,210); front=m.sprite("bkf",lambda:basket_svg("front"),260,210)
    m.shadow(F,x,y+6,250*s)
    F.put(back,x,y,130,190,s,key="bkb")
    if cobra: C(F,x,y-84*s,s*0.72,sway,rise,mood,tongue,1.0,False,flip,sh=False)
    F.put(front,x,y,130,190,s,key="bkf")
def bulb(F,x,y,t0,t,sc=1.0):
    dt=t-t0
    if dt<0: return
    k=bounce(dt*2.0)*sc*(1+0.04*math.sin(dt*14))
    img=m.sprite("bulb",lambda:bulb_svg(),240,280)
    F.put(img,x,y,120,140,k*0.9,key="bulb")
def coin(F,x,y,s=0.5,ph=0.0,alpha=1.0):
    img=m.sprite("coin",lambda:coin_svg(),120,120)
    w=abs(math.cos(ph*math.pi*2))*0.9+0.1
    im=m.sized("coin",img,s/m.RS*1.0); im=im.resize((max(2,int(im.width*w)),im.height),Image.BICUBIC)
    if alpha<1:
        a=im.getchannel("A").point(lambda v:int(v*alpha)); im=im.copy(); im.putalpha(a)
    F.im.paste(im,(int(x-im.width/2),int(y-im.height/2)),im)
def coin_fly(F,t,a,b,t0,dur=0.9,hgt=220):
    u=(t-t0)/dur
    if u<0 or u>1: return False
    x=lerp(a[0],b[0],u); y=lerp(a[1],b[1],u)-hgt*4*u*(1-u)
    coin(F,x,y,1.0,t*2.2,1.0); return True
def thought(F,cx,cy,k):
    if k<=0.02: return
    rx,ry=250*k,170*k; ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for (px,py,r) in ((cx-170*k,cy+215*k,22*k),(cx-120*k,cy+175*k,34*k)):
        d.ellipse([px-r-5,py-r-5,px+r+5,py+r+5],fill=(30,20,12,255)); d.ellipse([px-r,py-r,px+r,py+r],fill=(255,255,255,255))
    d.ellipse([cx-rx-6,cy-ry-6,cx+rx+6,cy+ry+6],fill=(30,20,12,255)); d.ellipse([cx-rx,cy-ry,cx+rx,cy+ry],fill=(255,255,255,255))
    F.im.paste(ov,(0,0),ov)

# ------------------------------------------------------------ scenes
def c1(t,D):
    F=base3(0,t); p=t/D
    for k in range(4):
        dirn=1 if k%2 else -1
        x=(((t*190+k*330)%1500)-200) if dirn>0 else 1300-((t*190+k*330)%1500)
        m.Pn(F,"local" if k%2 else "local2",x,1035+k*9,0.4,t*2.6+k*.3,"flail","shock",flip=dirn<0,mouth=0.8)
    C(F,730,1370,1.35+0.015*math.sin(t*2),sway=math.sin(t*1.7)*0.8,rise=1.0,mood="sly",tongue=1 if (t%1.4)<0.32 else 0)
    m.Pn(F,"official",230,1350,1.05,0,"hips","smile")
    bulb(F,240,690,D*0.52,t)
    m.fg(F,0)
    ts=bounce((t-0.25)/0.55)
    if t>0.25: textimg(F,"ДЕЛИ",540,330,F_BIG,(255,236,120),1.0*ts,rot=-4,stroke=16)
    if t>0.7: pill(F,540,505,"БРИТАНСКАЯ ИНДИЯ",F_SM,sc=bounce((t-0.7)/0.45))
    return F,(1.0+0.05*p,640,1100,0,0)
def c2(t,D):
    F=base3(1,t); p=t/D
    m.shadow(F,200,1336,230)
    F.put(SIGN,200,1330,220,670,0.95)
    m.Pn(F,"official",560,1335,1.05,0,"hips","smile",flip=False)
    xs=[(790,1290,.9),(920,1270,.85),(1030,1250,.8)]
    for k,(x,y,s) in enumerate(xs):
        bob=math.sin(t*3+k)*3
        m.Pn(F,"local" if k!=1 else "local2",x,y+bob,s,0,"idle","smile",flip=True)
        Bk(F,x-100*s,y-10*s+bob,0.34*s/0.9,True,math.sin(t*2.2+k)*0.8,0.7,"sly",1 if (t*1.5+k)%2<0.3 else 0)
    cyc=1.05
    for k in range(3):
        for rep in range(int(D/cyc)+1):
            t0=0.8+rep*cyc+k*0.35
            if coin_fly(F,t,(640,1060),(xs[k][0]-30,1060),t0,0.85,210):
                pass
    m.fg(F,1)
    return F,(1.0+0.05*p,640,1100,0,0)
def c3(t,D):
    F=base3(2,t); p=t/D; sp=0.46*D
    if t<sp:
        u=t/sp; x=lerp(-160,830,u)
        m.Pn(F,"local",x,1270,1.0,t*3.2,"flail","shock",sweat=True,mouth=0.9)
        Cs(F,x-300,1285,0.85,t*2.4,False,1 if (t%0.9)<0.25 else 0)
        m.pops(F,x+70,700,0.4,t,"!",(255,90,90),120)
    else:
        tt=t-sp
        m.Pn(F,"local",740,1270,1.0,0,"idle","smile" if tt>0.9 else "worried")
        m.Pn(F,"local2",330,1280,0.95,0,"idle","smile",flip=False)
        bulb(F,760,640,sp+0.4,t)
        k=bounce((tt-1.1)/0.7)
        if tt>1.1:
            thought(F,640,350,k)
            Bk(F,500,470,0.46*k+0.001,True,math.sin(t*2)*0.6,0.7)
            ov=ImageDraw.Draw(F.im)
            ax=ease((tt-1.8)/0.5)
            if ax>0:
                ov.line([590,380,690+60*ax*0,380],fill=(40,28,20),width=9) if False else None
                ov.line([600,400,700,400],fill=(40,28,20),width=10); ov.polygon([(715,400),(690,380),(690,420)],fill=(40,28,20))
                coin(F,790,400,1.1*k,0.0)
    m.fg(F,2)
    return F,(1.0+0.05*p,640,1100,0,0)
def c4(t,D):
    F=base3(3,t); p=t/D
    items=[]
    r=random.Random(7)
    for row,(y,sc,n,x0) in enumerate(((1130,0.5,6,170),(1220,0.62,6,120),(1310,0.76,5,200))):
        for k in range(n):
            x=x0+k*(900/ n)+row*40+r.uniform(-14,14); items.append((y,x,sc,k+row*3))
    for y,x,sc,k in sorted(items,key=lambda a:a[0]):
        Bk(F,x,y,sc,True,math.sin(t*2.1+k*1.3)*0.9,0.65+0.3*abs(math.sin(t*1.2+k)),"sly" if k%3 else "happy",1 if (t*1.4+k*.37)%2<0.25 else 0)
    m.Pn(F,"official",150,1345,1.05,0,"hips","smile")
    m.Pn(F,"local",640,1060,0.6,0,"hips","smile",flip=True); m.Pn(F,"local2",900,1050,0.58,0,"hips","smile",flip=True)
    for rep in range(int(D/0.9)+1):
        t0=0.4+rep*0.9; u=(t-t0)/1.2
        if 0<u<1: coin(F,150+math.sin(rep*2.3)*60,820-u*260,0.9,t*2,1-u)
    m.fg(F,3)
    n=int(1200*ease((t-0.2)/(D-0.8)))
    pill(F,540,330,"СДАНО КОБР: "+f"{n:,}".replace(","," "),F_MID if False else ImageFont.truetype(FONT,80),sc=bounce(t/0.5))
    return F,(1.0+0.05*p,540,1150,0,0)
def c5(t,D):
    F=base3(4,t,False); p=t/D
    m.shadow(F,200,1336,230); F.put(SIGN,200,1330,220,670,0.95)
    ts=t-1.3
    if ts>0:
        k=1+2.2*max(0,1-ts*5)
        textimg(F,"ОТМЕНЕНО",205,870,ImageFont.truetype(FONT,58),(225,40,50),k*bounce(ts*3.2),rot=-14,stroke=8)
    mood="shock" if t<1.6 else "sad"
    m.Pn(F,"official",600,1340,1.1,0,"flail" if 1.3<t<2.4 else "hips",mood,sweat=True,mouth=0.7 if mood=="shock" else 0)
    for k,x in enumerate((880,1010)):
        m.Pn(F,"local" if k==0 else "local2",x,1280-k*20,0.85,0,"idle","sad",flip=True)
        Bk(F,x-90,1270-k*20,0.3,True,math.sin(t*1.4+k)*0.5,0.5,"sly")
    m.fg(F,4)
    shake=(random.Random(int(t*30)).uniform(-16,16),random.Random(int(t*30)+9).uniform(-12,12)) if 1.3<t<1.8 else (0,0)
    return F,(1.0+0.05*p,640,1100,shake[0],shake[1])
def c6(t,D):
    F=base3(5,t,False); p=t/D
    r=random.Random(21); items=[]
    for k in range(20):
        side=-1 if k%2 else 1; ts=0.7+k*0.13; v=r.uniform(190,420); x0=540+r.uniform(-120,120); y=r.uniform(1010,1330)
        if t<ts: continue
        x=x0+side*v*(t-ts)
        if x<-250 or x>1330: continue
        items.append((y,x,side,r.uniform(0,1),0.4+0.5*(y-1010)/320))
    for k,bx in enumerate((300,440,640,780)):
        Bk(F,bx,1300-(k%2)*30,0.7,cobra=(t<0.7+k*0.2),sway=math.sin(t*3)*0.5,rise=0.7)
    for y,x,side,ph,sc in sorted(items,key=lambda a:a[0]):
        Cs(F,x,y,sc,t*2.6+ph,flip=side<0,tongue=1 if (t*2+ph*5)%1<0.3 else 0)
    # owners flee
    for k,(x0,sd) in enumerate(((330,-1),(740,1))):
        fl=t>0.7
        x=x0+(sd*(t-0.7)*420 if fl else 0)
        if -200<x<1300: m.Pn(F,"local" if k==0 else "local2",x,1190,0.75,t*3.2,"flail" if fl else "idle","shock" if fl else "smile",mouth=0.8 if fl else 0,flip=(sd<0) if fl else False)
    m.fg(F,5)
    n=int(600*ease((t-0.7)/(D-1.2)))+40
    pill(F,540,330,"ЗМЕЙ НА УЛИЦАХ: "+f"{n:,}".replace(","," "),ImageFont.truetype(FONT,72),sc=bounce(t/0.5))
    shake=(math.sin(t*40)*4,math.cos(t*37)*4) if t>0.7 else (0,0)
    return F,(1.0+0.05*p,540,1100,shake[0],shake[1])
def c7(t,D):
    F=base3(6,t); p=t/D; r=random.Random(5); items=[]
    for k in range(16):
        y=r.uniform(1010,1330); x=r.uniform(40,1040); sc=0.4+0.55*(y-1010)/320
        items.append((y,x,sc,k))
    for y,x,sc,k in sorted(items,key=lambda a:a[0]):
        if k%5==0: Cs(F,x,y,sc*0.8,t*2.4+k,flip=bool(k%2),tongue=1 if (t+k*.3)%1.2<0.3 else 0)
        else: C(F,x,y,sc*0.8,math.sin(t*2+k)*0.8,0.8+0.2*math.sin(t+k),"happy" if k%3==0 else "sly",1 if (t*1.3+k*.4)%2<0.25 else 0)
    m.Pn(F,"official",300,1360,1.15,0,"shrug","sad",sweat=True)
    m.fg(F,6)
    if t>0.8:
        ts=bounce((t-0.8)/0.5)
        textimg(F,"ЭФФЕКТ",540,300,ImageFont.truetype(FONT,190),(255,236,120),ts,rot=-4,stroke=15)
        textimg(F,"КОБРЫ",540,480,ImageFont.truetype(FONT,190),(255,110,90),ts,rot=-4,stroke=15)
    return F,(1.0+0.05*p,540,1100,0,0)
m.SCENE_FN=[c1,c2,c3,c4,c5,c6,c7]

# ------------------------------------------------------------ audio
def audio3(path):
    sr=44100; TOTAL=m.TOTAL; n=int((TOTAL+0.2)*sr); t=np.arange(n)/sr; out=np.zeros(n); bpm=104; beat=60/bpm
    D2=73.4; sc=[293.7,311.1,370.0,392.0,440.0,466.2,523.3,587.3]
    mel=[0,2,3,4,3,2,1,0, 2,3,4,6,4,3,2,0]
    def add(s,sig):
        s=int(s*sr)
        if s<0 or s>=n: return
        e=min(n,s+len(sig)); out[s:e]+=sig[:e-s]
    out+=np.sin(2*np.pi*D2*t)*0.09+np.sin(2*np.pi*D2*1.5*t)*0.04
    for k in range(int(TOTAL/beat)+2):
        tt=k*beat
        if k%2==0:
            L=int(0.3*sr); x=np.arange(L)/sr; add(tt,np.sin(2*np.pi*(80-30*x)*x*3)*np.exp(-x*12)*0.35)
        if k%4 in (1,3):
            L=int(0.12*sr); x=np.arange(L)/sr; add(tt+beat/2,np.sin(2*np.pi*620*x)*np.exp(-x*40)*0.12+np.random.RandomState(k).randn(L)*np.exp(-x*50)*0.06)
        for h in (0,1):
            idx=mel[(k*2+h)%16]
            L2=int(beat*0.5*sr); x2=np.arange(L2)/sr; fq=sc[idx]*(1 if (k//8)%2==0 else 1)
            sig=(np.sin(2*np.pi*fq*x2)+0.6*np.sin(2*np.pi*fq*2*x2)*np.exp(-x2*10)+0.3*np.sin(2*np.pi*fq*3.01*x2))*np.exp(-x2*7)
            if idx or h==0: add(tt+h*beat/2,sig*0.11)
    acc=0
    for i,d in enumerate(DURS):
        if i>0:
            L=int(0.35*sr); x=np.arange(L)/sr; nz=np.random.RandomState(i).randn(L); env=np.sin(np.pi*x/0.35)**2
            k=int(30+200*x[-1]); add(acc-0.1,np.convolve(nz,np.ones(k)/k,mode="same")*env*0.45)
        acc+=d
    def ping(ts,f0=1318,vol=0.22):
        L=int(0.5*sr); x=np.arange(L)/sr; add(ts,(np.sin(2*np.pi*f0*x)+0.4*np.sin(2*np.pi*f0*2.7*x))*np.exp(-x*9)*vol)
    st=[sum(DURS[:i]) for i in range(7)]
    L=int(0.3*sr); x=np.arange(L)/sr; add(st[0]+0.25,np.sin(2*np.pi*(90-60*x)*x*3)*np.exp(-x*12)*0.7)
    ping(st[0]+DURS[0]*0.52,1568,0.3)
    for rep in range(int(DURS[1]/1.05)+1):
        for k in range(3): ping(st[1]+0.8+rep*1.05+k*0.35+0.85,1760+k*120,0.13)
    ping(st[2]+0.46*DURS[2]+0.4,1568,0.3)
    for rep in range(int(DURS[3]/0.9)+1): ping(st[3]+0.4+rep*0.9+0.4,1900,0.12)
    L=int(0.5*sr); x=np.arange(L)/sr; add(st[4]+1.3,np.sin(2*np.pi*(120-70*x)*x*3)*np.exp(-x*9)*0.9)
    L=int(2.6*sr); x=np.arange(L)/sr; nz=np.random.RandomState(3).randn(L); hp=nz-np.convolve(nz,np.ones(8)/8,mode="same"); add(st[5]+0.7,hp*np.sin(np.pi*x/2.6)**2*0.28)
    L=int(0.6*sr); x=np.arange(L)/sr; add(st[6]+0.8,np.sin(2*np.pi*(100-60*x)*x*3)*np.exp(-x*8)*0.8)
    out*=np.minimum(1,np.minimum(t/0.4,(TOTAL+0.2-t)/1.0))
    out=np.tanh(out*1.1)*0.85
    pcm=(np.clip(out,-1,1)*32767).astype(np.int16)
    with wave.open(path,"wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())

if __name__=="__main__":
    init3(); m.post_init()
    if sys.argv[1]=="preview":
        sel=[(0,1.8),(0,5.5),(1,3.0),(2,1.5),(2,5.5),(3,4.0),(4,3.0),(5,3.5),(6,3.5)]
        if len(sys.argv)>2: sel=eval(sys.argv[2])
        ims=[Image.fromarray(m.frame(i,t)).resize((360,640)) for i,t in sel]
        cols=5; rows=(len(ims)+cols-1)//cols; sh=Image.new("RGB",(360*cols,640*rows))
        for k,im in enumerate(ims): sh.paste(im,((k%cols)*360,(k//cols)*640))
        sh.save("preview.png"); print(m.DURS,m.TOTAL)
    else:
        audio3("a.wav")
        cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-","-i","a.wav","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart","tmp.mp4"]
        pr=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for i in range(len(m.SCENES)):
            for fi in range(int(DURS[i]*30)): pr.stdin.write(m.frame(i,fi/30).tobytes())
        pr.stdin.close(); print("rc",pr.wait())
