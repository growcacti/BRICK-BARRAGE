import pygame as p, random, math, json
from pathlib import Path
p.init()
W,H=720,900
screen=p.display.set_mode((W,H),p.RESIZABLE); p.display.set_caption('Brick Barrage')
canvas=p.Surface((W,H)); clock=p.time.Clock(); font=p.font.SysFont('dejavusans',22); small=p.font.SysFont('dejavusans',16); big=p.font.SysFont('dejavusans',38,bold=True)
SAVE=Path.home()/'.brick_barrage.json'
try: saved=json.loads(SAVE.read_text())
except Exception: saved={}
record=int(saved.get('record',0)); speed=1; difficulty='Normal'; paused=False; fullscreen=False
LEFT,RIGHT,TOP,FLOOR=24,696,150,790
CELL=84; ROW=58; R=6
colors=[(44,190,170),(65,140,240),(160,100,235),(245,155,60),(235,80,110)]
def save():
    try: SAVE.write_text(json.dumps(dict(record=record,level=level,count=count,score=score,origin=origin,bricks=bricks,difficulty=difficulty)))
    except OSError: pass

def newrow():
    cols=random.sample(range(8),random.randint(3,6))
    for c in cols:
        kind=random.choices(['brick','extra','bomb'],[75,17,8])[0]
        hp=max(1,int(level*{'Easy':.7,'Normal':1,'Hard':1.5}[difficulty]*random.uniform(.65,1.4)))
        bricks.append(dict(c=c,y=TOP,kind=kind,hp=hp if kind=='brick' else 1))

def reset():
    global level,count,score,origin,bricks,balls,pending,phase,landing,delay,elapsed
    level=1; count=12; score=0; origin=W/2; bricks=[]; balls=[]; pending=0; phase='aim'; landing=None; delay=0; elapsed=0
    newrow(); save()

def rect(b): return p.Rect(LEFT+b['c']*CELL+4,b['y']+4,CELL-8,ROW-8)
def finish():
    global level,origin,phase,record
    origin=landing if landing is not None else origin; level+=1
    for b in bricks: b['y']+=ROW
    newrow(); phase='over' if any(b['y']+ROW>=FLOOR and b['kind']!='extra' for b in bricks) else 'aim'
    bricks[:]=[b for b in bricks if b['y']+ROW<FLOOR or b['kind']!='extra']; record=max(record,score); save()

def text(s,x,y,f=font,color=(230,240,255),center=False):
    t=f.render(str(s),True,color); canvas.blit(t,t.get_rect(center=(x,y)) if center else (x,y))

def aim(mx,my):
    v=p.Vector2(mx-origin,min(-45,my-FLOOR)); return v.normalize()*620

def hit(b):
    global score,count,record
    if b not in bricks:return
    b['hp']-=1; score+=1
    if b['hp']<=0:
        bricks.remove(b); score+=5
        if b['kind']=='extra':count+=1
        if b['kind']=='bomb':
            for other in bricks[:]:
                if abs(other['c']-b['c'])<=1 and abs(other['y']-b['y'])<=ROW: hit(other)
    record=max(record,score)

reset_needed=not saved.get('bricks')
if reset_needed: reset()
else:
    try:
        level=int(saved['level']); count=int(saved['count']); score=int(saved['score']); origin=float(saved['origin']); bricks=saved['bricks']; difficulty=saved.get('difficulty','Normal'); balls=[]; pending=0; phase='over' if any(b['y']+ROW>=FLOOR and b['kind']!='extra' for b in bricks) else 'aim'; landing=None; delay=0; elapsed=0
    except Exception: reset()
run=True
while run:
    dt=min(clock.tick(60)/1000,.04); sw,sh=screen.get_size(); scale=min(sw/W,sh/H); ox=(sw-W*scale)/2; oy=(sh-H*scale)/2
    mx,my=p.mouse.get_pos(); mx=(mx-ox)/scale; my=(my-oy)/scale
    for e in p.event.get():
        if e.type==p.QUIT:run=False
        if e.type==p.KEYDOWN:
            if e.key==p.K_ESCAPE:run=False
            if e.key==p.K_p:paused=not paused
            if e.key==p.K_f:
                fullscreen=not fullscreen; screen=p.display.set_mode((0,0),p.FULLSCREEN) if fullscreen else p.display.set_mode((W,H),p.RESIZABLE)
            if e.key==p.K_n:reset(); paused=False
            if e.key==p.K_s:speed={1:2,2:4,4:1}[speed]
            if e.key==p.K_d and phase!='fire':difficulty={'Easy':'Normal','Normal':'Hard','Hard':'Easy'}[difficulty]; save()
            if e.key==p.K_r and phase=='fire':pending=0; balls.clear(); finish()
        if e.type==p.MOUSEBUTTONDOWN and e.button==1 and not paused and phase=='aim' and TOP<my<FLOOR:
            velocity=aim(mx,my); pending=count; balls=[]; landing=None; delay=0; elapsed=0; phase='fire'
    if phase=='fire' and not paused:
        remain=dt*speed
        while remain>0 and phase=='fire':
            step=min(remain,1/240); remain-=step; delay-=step; elapsed+=step
            if pending and delay<=0:
                balls.append([p.Vector2(origin,FLOOR-R-1),velocity.copy()]); pending-=1; delay+=.055
            for ball in balls[:]:
                pos,v=ball; old=pos.copy(); pos+=v*step
                if pos.x<LEFT+R:pos.x=LEFT+R; v.x=abs(v.x)
                if pos.x>RIGHT-R:pos.x=RIGHT-R; v.x=-abs(v.x)
                if pos.y<TOP+R:pos.y=TOP+R; v.y=abs(v.y)
                if pos.y>=FLOOR and v.y>0:
                    if landing is None:landing=max(LEFT+R,min(RIGHT-R,pos.x))
                    balls.remove(ball); continue
                for b in bricks[:]:
                    rr=rect(b).inflate(R*2,R*2)
                    if rr.collidepoint(pos.x,pos.y):
                        if b['kind']=='extra':hit(b); continue
                        if old.x<=rr.left or old.x>=rr.right:v.x=-v.x
                        elif old.y<=rr.top or old.y>=rr.bottom:v.y=-v.y
                        else:
                            if min(abs(pos.x-rr.left),abs(pos.x-rr.right))<min(abs(pos.y-rr.top),abs(pos.y-rr.bottom)):v.x=-v.x
                            else:v.y=-v.y
                        pos.update(old); hit(b); break
            if (not balls and not pending) or elapsed>45:balls.clear(); pending=0; finish()
    canvas.fill((13,20,36)); text('BRICK BARRAGE',24,18,big); text(f'Level {level}     Score {score}     Best {record}',24,72); text(f'Balls {count}   •   {difficulty}   •   Speed {speed}x',24,108,small)
    p.draw.rect(canvas,(23,34,55),(LEFT,TOP,RIGHT-LEFT,FLOOR-TOP),border_radius=8)
    for c in range(9):p.draw.line(canvas,(30,43,65),(LEFT+c*CELL,TOP),(LEFT+c*CELL,FLOOR))
    for b in bricks:
        rr=rect(b); kind=b['kind']; color=colors[min(4,b['hp']//max(1,level//2+1))]
        if kind=='extra':p.draw.circle(canvas,(75,225,145),rr.center,17); text('+1',*rr.center,small,(12,35,25),True)
        else:
            if kind=='bomb':color=(235,75,65)
            p.draw.rect(canvas,color,rr,border_radius=8); p.draw.rect(canvas,(255,255,255),rr,1,border_radius=8); text('BOOM' if kind=='bomb' else b['hp'],*rr.center,small if kind=='bomb' else font,(12,20,35),True)
    p.draw.line(canvas,(100,130,160),(LEFT,FLOOR),(RIGHT,FLOOR),2)
    if phase=='aim':
        pos=p.Vector2(origin,FLOOR-8); v=aim(mx,my).normalize()*12
        for i in range(85):
            pos+=v
            if pos.x<LEFT+R or pos.x>RIGHT-R:v.x=-v.x; pos.x=max(LEFT+R,min(RIGHT-R,pos.x))
            if pos.y<TOP+R or any(rect(b).inflate(12,12).collidepoint(pos.x,pos.y) for b in bricks if b['kind']!='extra'):break
            if i%2==0:p.draw.circle(canvas,(130,205,255),pos,3)
        p.draw.circle(canvas,(255,245,200),(origin,FLOOR-7),8)
    for pos,v in balls:p.draw.circle(canvas,(255,245,200),pos,R)
    if landing is not None and phase=='fire':p.draw.circle(canvas,(100,230,170),(landing,FLOOR),7)
    text('Click to aim & fire   |   R: recall balls   |   S: speed',24,810,small); text('P: pause   N: new game   D: difficulty   F: fullscreen',24,840,small); text('Esc: quit  •  Progress saved after each round',24,868,small)
    if paused or phase=='over':
        overlay=p.Surface((W,H),p.SRCALPHA); overlay.fill((0,0,0,175)); canvas.blit(overlay,(0,0)); text('PAUSED' if paused else 'GAME OVER',W/2,H/2-35,big,center=True); text('Press P to resume' if paused else 'Press N for a new game',W/2,H/2+20,center=True)
    screen.fill((5,8,15)); screen.blit(p.transform.smoothscale(canvas,(max(1,int(W*scale)),max(1,int(H*scale)))),(int(ox),int(oy))); p.display.flip()
if phase!='fire':save()
p.quit()
