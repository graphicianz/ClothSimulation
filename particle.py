from cgkit.cgtypes import vec3
from math import pow
from numerical_integration import *
import sys, random

class particle(object):
    def __init__ (self, mass=1, index=(0,0), pos=(0,0,0), vel=(0,0,0), F=(0,0,0), accel=(0,0,0), nm=[["ExEulerIntegration",1]]):
        #physical properties
        self.mass = mass
        self.index = index
        self.pos = vec3(pos)
        self.prev_pos = vec3(pos)
        self.vel = vec3(vel)
        self.F = vec3(F)
        self.accel = vec3(accel)
        self.nm = [method[0] for method in nm if method[1]==1][0]
        
        self.pin = False
        self.col = vec3(1,1,1)
        
        #springs
        self.structural_springs = []
        self.shear_springs = []
        self.flexion_springs = [] #bending spring
        
    def addSpring(self, spring):
        if spring.spring_type=="structural":
            self.structural_springs.append(spring)
        elif spring.spring_type=="shear":
            self.shear_springs.append(spring)
        elif spring.spring_type=="flexion":
            self.flexion_springs.append(spring)
            
    def getAllSprings(self):
        return self.structural_springs + self.shear_springs + self.flexion_springs
        
    def update_spring(self, ball, k, rest_len, kd, gravity):
        u = self.pos - ball.pos
        d = u.length() - rest_len
        un = u.normalize()
        f_gravity = ((ball.mass+self.mass)/2) * vec3(gravity)
        
        #deltaV = self.vel-ball.vel
        #damperF = sum(p*q for p,q in zip(un, deltaV))
        #damperF *= kd
        #damperF = un * 
        #damper = kd * ball.vel
        deltaV = self.vel-ball.vel
        damper = kd * ball.vel
        F = -k * d * un + f_gravity + damper
        self.F = F
        ball.F = -F
        
    def update_location(self, dt):
        
        if not self.pin:
            self = NumericalIntegration(self.nt, self, dt)
        
        #Semi-Implicit Euler Integration
        #self.accel = self.F / self.mass
        #self.vel += self.accel * dt
        #self.pos += self.vel * dt
       
    def update_location2(self, dt):
        #Verlet Integration
        self.accel = self.F / self.mass
        temp = self.pos
        self.pos = self.pos + self.pos - self.prev_pos + (self.accel * pow(dt,2)) 
        self.prev_pos = temp
        
        self.vel += self.accel * dt