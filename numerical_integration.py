def NumericalIntegration(method, particle, dt):
    if method=="ExEulerIntegration":
        return EulerIntegration(particle, dt)
    elif method=="VerletIntegration":
        return VerletIntegration(particle, dt)

def EulerIntegration(particle, dt):
    particle.accel = particle.F / particle.mass
    particle.vel += particle.accel * dt
    particle.pos += particle.vel * dt
    #return particle

def VerletIntegration(particle, dt):
    particle.accel = particle.F / particle.mass
    temp = particle.pos
    particle.pos = particle.pos *2  - particle.prev_pos + (particle.accel * pow(dt,2)) 
    particle.prev_pos = temp
    
    particle.vel += particle.accel * dt
    #return particle