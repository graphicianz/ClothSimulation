import OpenGL, sys, random, time
from math import sqrt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import *
from cgkit.all import *
from cgkit.cgtypes import vec3
from particle import particle
from spring import spring
from numerical_integration import *
import colorsys

dt = 0.4
m, n = 10,10
damp = 0.2
k1 = 0.3 #k for structural spring
k2 = 0.3 #k for shear spring
k3 = 0.3 #k for  flexion spring
#rest_len1 = 1 #natural length of structural spring
#rest_len2 = sqrt(2) #natural length of shear spring
#rest_len3 = 2 #natural length of flexion spring
gravity = (0,-0.098,0)
Tc = 0.1 # critical deformation rate (10%)

isStructuralEnable = True
isShearEnable = True
isFlexionEnable = True

isParticleDraw = True
isStructuralDraw = True
isShearDraw = True
isFlexionDraw = True
isSpeedDraw = True

isCheckDRStructural = True  #check deformation rate for structural spring
isCheckDRShear = True       #check deformation rate for shear spring

isBlendColDR = False         #blend color from old color to red when deformation rate exceed

fix_framerate = False
FRAME_PER_SECOND = 60
SKIP_TICKS = 1000/FRAME_PER_SECOND

time_display_prev = 0.0

particle_radius = 90 #for click
nm = [["ExEulerIntegration",1],
      ["VerletIntegration",0]
      ]

windows_h, windows_w = 512, 512
fps = 0.0
frames = 0
previousTime = 0.0
t = 0.0
onscreen_fps = 0.0
onscreen_display_time = 0.0
onscreen_int_time = 0.0
timeclock = time.time()
prev_time = time.time()
count_time = 0.0
sum_time_for_calc = 0.0
time_for_calc = 0.0
time_display1=time_display2=time_display3 = 0.0

timeInterval = 0.0
#f = open("./fps_analysis.txt","w")
#f.write("frames count_time fps time_for_calc sum_time_for_calc currentTime previousTime timeInterval time_display1 time_display2 time_display3\n")
currentTime = previousTime = 0.0

mouse_button = [GLUT_UP, GLUT_UP, GLUT_UP, GLUT_UP, GLUT_UP]

#init particle
#ball_1 = particle(mass=1,pos=(0,0,0))
#ball_2 = particle(mass=1,pos=(3,-10,0))



def initCloth():
    global particles,neibors
    particles = []
    
    #init particles
    for i in range(m):
        particles.append([])
        for j in range(n):
            particles[i].append(particle(index=(i,j), pos=(j-(n/2),-i,0),nm=nm))
            
    #init structural springs
    springs = []
    for i in range(m):
        for j in range(n):
            
            if j!=0:
                length = (particles[i][j].pos - particles[i][j-1].pos).length()                
                springs.append(spring(particles[i][j], particles[i][j-1], length, length, "structural"))
                #neibors.append([particles[i][j-1], length])
            if j<n-1:
                length = (particles[i][j].pos - particles[i][j+1].pos).length()
                springs.append(spring(particles[i][j], particles[i][j+1], length, length, "structural"))
                #neibors.append([particles[i][j+1], length])
            if i!=0:
                length = (particles[i][j].pos - particles[i-1][j].pos).length()
                springs.append(spring(particles[i][j], particles[i-1][j], length, length, "structural"))
                #neibors.append([particles[i-1][j], length])
            if i<m-1:
                length = (particles[i][j].pos - particles[i+1][j].pos).length()
                springs.append(spring(particles[i][j], particles[i+1][j], length, length, "structural"))
                #neibors.append([particles[i+1][j], length])
            
            for sp in springs:
                particles[i][j].addSpring(sp)
            springs = []
            
    #init shear springs
    springs = []
    for i in range(m-1):
        for j in range(n):    
            
            if i!=0 and j<n-1:
                length = (particles[i][j].pos - particles[i-1][j+1].pos).length()
                springs.append(spring(particles[i][j], particles[i-1][j+1], length, length, "shear"))
                #springs.append([particles[i-1][j+1], length])
                
            if i!=0 and j!=0:
                length = (particles[i][j].pos - particles[i-1][j-1].pos).length()
                springs.append(spring(particles[i][j], particles[i-1][j-1], length, length, "shear"))
                #springs.append([particles[i-1][j-1], length])
            
            if j!=0:
                length = (particles[i][j].pos - particles[i+1][j-1].pos).length()
                springs.append(spring(particles[i][j], particles[i+1][j-1], length, length, "shear"))
                #springs.append([particles[i+1][j-1], length])
            
            if j<n-1:
                length = (particles[i][j].pos - particles[i+1][j+1].pos).length()
                springs.append(spring(particles[i][j], particles[i+1][j+1], length, length, "shear"))
                #springs.append([particles[i+1][j+1], length])
                
            for sp in springs:
                particles[i][j].addSpring(sp)
            springs = []     
            
    #init flexion springs
    springs = []
    for i in range(m):
        for j in range(n):
            #right
            if j<n-2:
                length = (particles[i][j].pos - particles[i][j+2].pos).length()
                springs.append(spring(particles[i][j], particles[i][j+2], length, length, "flexion"))
                #neibors.append([particles[i][j+2], length])
            #left
            if j>1:
                length = (particles[i][j].pos - particles[i][j-2].pos).length()
                springs.append(spring(particles[i][j], particles[i][j-2], length, length, "flexion"))
                #neibors.append([particles[i][j-2], length])
            #upper
            if i>1:
                length = (particles[i][j].pos - particles[i-2][j].pos).length()
                springs.append(spring(particles[i][j], particles[i-2][j], length, length, "flexion"))
                #neibors.append([particles[i-2][j], length])
            #lower
            if i<m-2:
                length = (particles[i][j].pos - particles[i+2][j].pos).length()
                springs.append(spring(particles[i][j], particles[i+2][j], length, length, "flexion"))
                #neibors.append([particles[i+2][j], length])
                
            for sp in springs:
                particles[i][j].addSpring(sp)
            springs = []

    particles[0][0].pin = True
    particles[0][n-1].pin = True
    #particles[m-1][0].pin = True
    
#    particles[m-1][0].pin = True
#    particles[m-1][n-1].pin = True

def screenDisplay(data):
    x = 20
    y = 20
    for d in data:
        text = str(d[0])+' : '+str(d[1])
        writeMessage(text,x=x,y=y,stroke=False)
        y += 20


#def accumulateForce(Pij, Pkl, K, L0, Cdis, gravtiy):
    #accumulateForce(st_spring, k1, damp)
def accumulateForce(spring, K, Cdis):
    Pij = spring.p1
    Pkl = spring.p2
    L0 = spring.rest_len
        
    
    #Internal Force (Hooke's law)
    L = (Pij.pos - Pkl.pos)
    F_int = -K * ((L.length()-L0)*L.normalize())
        
    #Viscous damping
    F_dis = Cdis * Pkl.vel
    
    F_total = F_int + F_dis
    
    Pij.F += F_total
    Pkl.F += -F_total
    
    spring.current_len = L.length()
    
    #Deformation Rate and assign color
    deformation_rate = (L.length()-L0)/L0
    if isBlendColDR:
        #deformation rate <= 0 -> blue
        #deformation rate >= Tc -> red
        if deformation_rate < 0:
            spring.col = spring.old_col
        elif deformation_rate >= Tc:
            spring.col = vec3(1,0,0)
        else:
            h = colorsys.rgb_to_hsv(0, 0, 1)[0]
            spring.col = vec3(colorsys.hsv_to_rgb(h-deformation_rate/Tc*h, 1.0, 1.0))
    else:
        if isCheckDRStructural and spring.spring_type=="structural" and deformation_rate > Tc:
            spring.col = vec3(1,0,0)
        elif isCheckDRShear and spring.spring_type=="shear" and deformation_rate > Tc:
            spring.col = vec3(1,0,0)
        else:
            spring.col = spring.old_col          

def integrate(p, dt):
    if not p.pin:
        NumericalIntegration(p.nm, p, dt)

def myIdle():
    global prev_time, dt, neibors, count_time, fps, t, time_for_calc, sum_time_for_calc, f
    cur_time = time.time()

    time_for_calc = time.time()
    #calculate structural
    for i in range(len(particles)):
        for j in range(len(particles[i])):
            
            cur_particle = particles[i][j]
            
            #Gravity
            F_gr = cur_particle.mass * gravity
            cur_particle.F +=  F_gr
            
            #Internal Force and Vicous Damping
#            for dest_particle in cur_particle.getAllSprings():
#                accumulateForce(cur_particle, dest_particle[0], k1, dest_particle[1], damp, gravity)
            
            #calculate for structural spring
            for st_spring in cur_particle.structural_springs:
                #accumulateForce(cur_particle, dest_particle[0], k1, dest_particle[1], damp, gravity)
                accumulateForce(st_spring, k1, damp)
            #calculate for shear spring
            for sh_spring in cur_particle.shear_springs:
                #accumulateForce(cur_particle, dest_particle[0], k2, dest_particle[1], damp, gravity)
                accumulateForce(sh_spring, k2, damp)            
            #calculate for flexion spring
            for fl_spring in cur_particle.flexion_springs:
                #accumulateForce(cur_particle, dest_particle[0], k3, dest_particle[1], damp, gravity)
                accumulateForce(fl_spring, k3, damp)            

    time_for_calc = time.time()-time_for_calc   

    #Integration
    for i in range(len(particles)):
        for j in range(len(particles[i])):
            integrate(particles[i][j], dt)   
            
    #Clear force
    for i in range(len(particles)):
        for j in range(len(particles[i])):
            particles[i][j].F = vec3(0,0,0)            
                         
            
     
    
    sum_time_for_calc += time_for_calc    
    fps = calculateFPS()
    #print("fps: {0}".format(type(fps)))

    count_time += dt
    
    #debug
    #text = "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10}".format(frames,count_time,fps,time_for_calc,sum_time_for_calc,currentTime,previousTime,timeInterval,time_display1,time_display2,time_display3)
    
    #f.write(text+"\n")
    #print(text)
    
    
    glutPostRedisplay()
    
    
#    time_thisframe = time.time()-cur_time
#    fps = 1/(( time_thisframe*0.9) + (time_lastframe*0.1))
#    #print("frame:{0} curT:{1} t:{2} fps:{3} : {4} {5} {6}".format(frames,count_time,t,round(fps,2),cur_time,time.time(),time.time()-cur_time))
#    #print(1/fps)
#    count_time += dt     
#    
#    time_lastframe = time_thisframe
#    print(glutGet(GLUT_ELAPSED_TIME))
    #time.sleep(0.01)
    
#    if frames==0:
#        t = time.time()
#    frames += 1
#    if frames >= 5:
#        fps = (frames/ (time.time()-t))
#        #onscreen_fps = fps
#        frames = 0
#        print("")
#        #print("fps = {0}").format(fps)    

def calculateFPS():
    global previousTime, frames, fps, sum_time_for_calc, timeInterval, currentTime, previousTime
    frames +=1
    currentTime = glutGet(GLUT_ELAPSED_TIME)
    #Calculate time passed
    timeInterval = currentTime - previousTime
    
    if timeInterval > 1000:
        #print("frames:{0}".format(frames))
        #print("timeInterval:{0}".format(timeInterval))
        fps = frames / (timeInterval / 1000.0)
        previousTime = currentTime
        
        frames = 0
        sum_time_for_calc = 0.0
        #print("fps: {0}".format(type(fps)))
    return fps

def GetOGLPos(x,y):
    
    modelviewMat = glGetDoublev(GL_MODELVIEW_MATRIX)
    projectionMat = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    
    winX = float(x)
    winY = float(viewport[3]) - float(y)
    #glReadPixels( x, int(winY), 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, &winZ )
    winZ = glReadPixels(x, int(winY), 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
    #gluUnProject( winX, winY, winZ, modelview, projection, viewport, &posX, &posY, &posZ)
    pos = gluUnProject( winX, winY, winZ, modelviewMat, projectionMat, viewport)
    
    return vec3(pos)

def myDisplay():
    global onscreen_fps, timeclock, next_game_tick
    global time_display1, time_display2, time_display3, time_display_prev, onscreen_display_time, onscreen_int_time
    #time_display = 0.0
    time_display1 = time.time()
  
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if time.time()-timeclock >= 1:
        onscreen_fps = fps
        onscreen_display_time = time_display_prev
        onscreen_int_time = time_for_calc
        timeclock = time.time()
        
    time_display2 = time.time()
#    try:
    screenDisplay([['FPS',round(onscreen_fps,2)],
                   #['K',k] , ['Rest_len',rest_len], 
                   ['CurrentT',count_time], 
                   ['DeltaT',dt],
                   ['NM',[n[0] for n in nm if n[1]==1][0]],
                   ['Display time',round(onscreen_display_time*1000,3)],
                   ['Accumulate Force',round(onscreen_int_time*1000,3)]
                   ])
#    except:
#        print("onscreen_fps")
#        print(onscreen_fps)
#        print(type(onscreen_fps))
#        print("fps")
#        print(fps)
#        print(type(fps))
    #writeMessage("FPS : {0}".format(str(round(onscreen_fps,2))), stroke=False, win_w=windows_w, win_h=windows_h)
    time_display2 = time.time()-time_display2
    
    time_display3 = time.time()  
    
    glPushMatrix()
    gluLookAt(0, -5, 25, 0, -5, 0, 0, 1, 0)
    
    time_display3 =time.time()-time_display3

    axis_size = 5
    #draw center point
    glPointSize(5)
    glColor3f(1,0,0)
    glBegin(GL_POINTS)
    glVertex3f(0,0,0)
    glEnd()  
    
    #draw x-axis
    glPointSize(1)
    glColor3f(1,0,0)
    glBegin(GL_LINES)
    glVertex3f(0,0,0)
    glVertex3f(axis_size,0,0)
    glEnd()
    #draw y-axis
    glColor3f(0,1,0)
    glBegin(GL_LINES)
    glVertex3f(0,0,0)
    glVertex3f(0,axis_size,0)
    glEnd() 
    #draw z-axis
    glColor3f(0,0,1)
    glBegin(GL_LINES)
    glVertex3f(0,0,0)
    glVertex3f(0,0,axis_size)
    glEnd()     
        
    if isParticleDraw:
        glPointSize(particles[0][0].mass*3)
        glBegin(GL_POINTS)
        #draw paticles
        for i in range(len(particles)):
            for j in range(len(particles[i])):
                
                
                glColor3f(*particles[i][j].col)
                glVertex3f(*particles[i][j].pos)
        glEnd()
            
    #draw structural spring      
    if isStructuralDraw:
        glPointSize(1)
        glBegin(GL_LINES)
        #glColor3f(0,0,1)
        for i in range(len(particles)):
            for j in range(len(particles[i])):
                if (i%2==0 and j%2==0) or ((i+1)%2==0 and (j+1)%2==0):
                    #for structural_particle in particles[i][j].structural_springs:
                    for st_spring in particles[i][j].structural_springs:
                        glColor3f(*st_spring.col)
                        glVertex3f(*st_spring.p1.pos)
                        glVertex3f(*st_spring.p2.pos)                        
        glEnd()
    
    #draw shear spring   
    if isShearDraw:
        glPointSize(1)
        glBegin(GL_LINES)
        #glColor3f(0,1,0)
        for i in range(0,len(particles),2):
            for j in range(len(particles[i])):
                for sh_spring in particles[i][j].shear_springs:
                    glColor3f(*sh_spring.col)
                    glVertex3f(*sh_spring.p1.pos)
                    glVertex3f(*sh_spring.p2.pos)
        glEnd()        
    
    #draw flexion spring
    if isFlexionDraw:
        glPointSize(1)
        glBegin(GL_LINES)
        
        #fix color
        glColor3f(*particles[0][0].flexion_springs[0].col)
        even_triggeri, odd_triggeri = True,True
        even_triggerj, odd_triggerj = True,True
        i_cond, j_cond = False,False
        for i in range(len(particles)):
            for j in range(len(particles[i])):
                
                if i%2==0:
                    if even_triggeri:
                        i_cond = 0
                        even_triggeri = False
                    else:
                        even_triggeri = True
                        
                elif (i+1)%2==0:
                    if odd_triggeri:
                        i_cond = 1
                        odd_triggeri = False
                    else:
                        odd_triggeri = True
                        
                if j%2==0:
                    if even_triggerj:
                        j_cond = 0
                        even_triggerj = False
                    else:
                        even_triggerj = True
                        
                elif (j+1)%2==0:
                    if odd_triggerj:
                        j_cond = 1
                        odd_triggerj = False
                    else:
                        odd_triggerj = True                        
                        
                if i_cond == j_cond:
                    for fl_spring in particles[i][j].flexion_springs:
                        glVertex3f(*fl_spring.p1.pos)
                        glVertex3f(*fl_spring.p2.pos)
                        
                i_cond, j_cond = False, False
        glEnd() 
        
             
    #draw line
#    for i in range(len(particles)-1):
#        glBegin(GL_LINES)
#        glColor3f(1,0,0)
#        glVertex3f(*particles[i].pos)
#        glVertex3f(*particles[i+1].pos)
#        glEnd()
        
    
    #########
#        
    if isSpeedDraw:
        glColor3f(1,0,1)
        glBegin(GL_LINES)
        for i in range(len(particles)):
            for j in range(len(particles[i])):
                try:
                    v = particles[i][j].vel*2#.normalize()
                except:
                    v = vec3(0,0,0)
                glVertex3f(*particles[i][j].pos)
                glVertex3f(*(particles[i][j].pos-v))
        glEnd()   
#    #ball1
#    glPointSize(ball_1.mass*10)
#    glBegin(GL_POINTS)
#    glColor3f(1,1,1)
#    glVertex3f(*ball_1.pos)
#    glEnd()
#    
#    #ball2
#    glPointSize(ball_2.mass*10)
#    glBegin(GL_POINTS)
#    glColor3f(1,1,1)
#    glVertex3f(*ball_2.pos)
#    glEnd()   
#      
#    
#    #line ball1 >> ball2
#    glBegin(GL_LINES)
#    glVertex3f(*ball_1.pos)
#    glVertex3f(*ball_2.pos) 
#    glEnd() 
        
#    for i in range(1000):
#        glPointSize(random.random()*5)
#        glColor3f(random.random(),random.random(),random.random())
#        glBegin(GL_POINTS)
#        glVertex3f(random.random()*5-2.5,random.random()*5-2.5,0)
#        glEnd()    

    glPopMatrix()
    
    if fix_framerate:
        next_game_tick += SKIP_TICKS
        sleep_time = next_game_tick - glutGet(GLUT_ELAPSED_TIME)
        if sleep_time >= 0:
            time.sleep(sleep_time/1000.0)    
    
    glutSwapBuffers() 
    

    
#    if frames==0:
#        t = time.time()
#    frames += 1
#    if frames >= 5:
#        fps = (frames/ (time.time()-t))
#        #onscreen_fps = fps
#        frames = 0
#        #print("fps = {0}").format(fps)

    time_display_prev = time.time()-time_display1
        
def myMotion(x, y):
    global rot_x, rot_y, mouse_button, mouse_sensitive, mouse_x, mouse_y
    if mouse_button[GLUT_LEFT_BUTTON] == GLUT_DOWN:
        pass
#        click_pos = GetOGLPos(x,y)
#        nearest_point = getNearestPoint(click_pos,particle_radius)
#        if nearest_point != None:
#            nearest_point.pin = True


        #rot_y += ((x - mouse_x) * mouse_sensitive)
        #rot_x += ((y - mouse_y) * mouse_sensitive)
        #print("rot_x:{0} rot_y:{1}".format(rot_x, rot_y))

    #mouse_x = x
    #mouse_y = y  

def getNearestPoint(cp, r):
    nearest_dist = 99999
    nearest_point = None
    for p in particles:
        dist = (cp - p.pos).length()
        if dist < nearest_dist:
            nearest_dist = dist
            nearest_point = p
          
    #print(nearest_dist)  
    if nearest_dist<=r:
        return nearest_point
    else:
        return None

def myMouse(button, state, x, y):
    mouse_button[button] = state
#    if mouse_button[GLUT_LEFT_BUTTON] == GLUT_DOWN:
#        click_pos = GetOGLPos(x,y)
#        nearest_point = getNearestPoint(click_pos,particle_radius)
#        if nearest_point != None:
#            nearest_point.pin = True
#            nearest_point.col = vec3(1,0,0)
#            
#    elif mouse_button[GLUT_RIGHT_BUTTON] == GLUT_DOWN:
#        click_pos = GetOGLPos(x,y)
#        nearest_point = getNearestPoint(click_pos,particle_radius)
#        if nearest_point != None:
#            nearest_point.pin = False   
#            nearest_point.col = vec3(1,1,1)             

def myReshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50.0, float(w)/float(h), 0.01, 100.0)
    glMatrixMode(GL_MODELVIEW) 

def init_gl(r, g, b, a, smooth=True, depth=False):
    glClearColor(r, g, b, a)
    glShadeModel(GL_SMOOTH if smooth else GL_FLAT)
    if depth:
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)
    lists = [['Vendor', GL_VENDOR], ['Renderer',GL_RENDERER],
             ['OpenGL Version', GL_VERSION], 
             ['GLSL Version', GL_SHADING_LANGUAGE_VERSION]]
    
def main():
    global next_game_tick
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH) # Add Depth View to Color
    glutInitWindowSize(512,512)
    glutInitWindowPosition(100,100)
    glutCreateWindow(b"Mass-Spring Models Provot 0.2 (29-11-56)")
    glutInit()
    glutDisplayFunc(myDisplay)
    glutIdleFunc(myIdle) 
    glutReshapeFunc(myReshape)  
    glutMouseFunc(myMouse)
    glutMotionFunc(myMotion)     
    glEnable(GL_DEPTH_TEST) #Use Depth Function  to enable view
    init_gl(0, 0, 0, 1, depth=True, smooth=False)
    glClear(GL_COLOR_BUFFER_BIT)  
    
    initCloth()
    
    next_game_tick = glutGet(GLUT_ELAPSED_TIME)
    
    glutMainLoop() 
   
def writeStrokeString(x, y, msg, font=GLUT_STROKE_ROMAN):
    prev_width = glGetFloatv(GL_LINE_WIDTH)
    glTranslatef(x, y, 0)
    glScalef(0.25, 0.15, 0.25)
    glLineWidth(2.0)
    glEnable(GL_LINE_SMOOTH)
    for i in msg:
        glutStrokeCharacter(font, ord(i))        
    glLineWidth(prev_width)
    glDisable(GL_LINE_SMOOTH)

def writeBitmapString(x, y, msg, font=GLUT_BITMAP_8_BY_13):
    glRasterPos2f(x, y)
    for i in msg:
        glutBitmapCharacter(font, ord(i))

def writeMessage(msg, x=20, y=20, stroke=False,
                 win_w=640, win_h=480, color=[0,1,0]):
    prev_mode = glGetIntegerv(GL_MATRIX_MODE)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, win_w, 0, win_h, -1, 1)
    glColor3fv(color)
    if stroke:
        writeStrokeString(x, y, msg)
    else:
        writeBitmapString(x, y, msg)
    glPopMatrix()
    glMatrixMode(prev_mode)  
       
if __name__ == "__main__":
    main()      
