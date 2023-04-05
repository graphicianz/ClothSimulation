from cgkit.cgtypes import vec3

class spring(object):
    def __init__(self, p1, p2, rest_len, current_len, spring_type, col=vec3(0,0,0)):
        self.p1 = p1 #particle
        self.p2 = p2 #particle
        self.rest_len = rest_len #float
        self.current_len = current_len #float
        self.spring_type = spring_type #string
        
        if spring_type=="structural":
            self.col = vec3(0,0,1)
            self.old_col = vec3(0,0,1)
        elif spring_type=="shear":
            self.col = vec3(0,0,1)
            self.old_col = vec3(0,0,1)
        elif spring_type=="flexion":
            self.col = vec3(.3,.3,0)
            self.old_col = vec3(.3,.3,0)