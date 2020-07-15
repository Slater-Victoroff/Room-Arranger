from visual import *
from visual.controls import *
import math

class Colliding:
    def find_corners(self,*things):
        '''Find the corners you need to project on axes for the separating axis theorem.
            Works for boxes and cylinders only, and only in the xy plane (cylinders must be a circle in the xy plane).
            For cylinders, finds the points on the circumfrence along the axis pointing towards the boxes center.
            For boxes, finds the corners.'''
        res = []
        for thing in things:
            if thing.__class__.__name__ == 'box':
                ax = thing.axis
                p = [.5*vector(thing.size.x,thing.size.y,0), #makes a list of the corner points assuming a box at (0,0,0) perpendicular to x and y axes
                     .5*vector(thing.size.x,-1*thing.size.y,0),
                     .5*vector(-1*thing.size.x,-1*thing.size.y,0),
                     .5*vector(-1*thing.size.x,thing.size.y,0)]
                angle = ax.diff_angle(vector(1,0,0))
                for i in range(len(p)): #rotate and shift the box
                    p[i] = rotate(p[i], angle = angle, axis = (0,0,1))
                    p[i] = p[i] + thing.pos
                res.append(p)
            elif thing.__class__.__name__ == 'cylinder':
                if thing.axis.x==0 and thing.axis.y==0:
                    p = []
                    for thing2 in things:
                        if thing2 != thing:
                            ax = thing.pos - thing2.pos
                            vec = vector(ax.x,ax.y,0)
                            vec.mag = thing.radius
                            p.append(thing.pos + vec)
                            p.append(thing.pos - vec)
                    res.append(p)
        return tuple(res)

    def has_intersect_xy(self,p1,p2):
        '''takes two lists of the vectors that are the corners of two concave shapes
            and finds if the shapes intersect using the separating axis theorem.
            Has some bug I haven't found yet - doesn't detect collsion in all cases.'''
        Flag = 0
        for i in range(len(p1)):
            proj1 = [] #initialize lists to hold the projections of the corners onto the vectors
            proj2 = []
            side = p1[i] - p1[i-1] #find the sides we need to check along
            if len(p1)<3 and i==1: #basically if this a cylinder and the second time through
                vec = side #also check the vector going through the center
            else: 
                vec = cross(side,vector(0,0,1)) #the vector you need to check, in general, is the one perpendicular to the side
            for j in range(len(p1)): #find all the projections of p1 onto the vector
                proj1.append(dot(p1[j],vec))
            for k in range(len(p2)): #find all the projections of p2 onto the vector
                proj2.append(dot(p2[k],vec))
            if not ((max(proj2) > max(proj1) and min(proj2) > max(proj1)) or (max(proj2) < min(proj1) and min(proj2) < min(proj1))): #if the aren't disjoint
                Flag += 1
        for i in range(len(p2)): # do the same as above, with the second object's points
            proj1 = []
            proj2 = []
            side = p2[i] - p2[i-1]
            if len(p2)<3 and i==1:
                vec = side
            else:
                vec = cross(side,vector(0,0,1))
            for j in range(len(p1)):
                proj1.append(dot(p1[j],vec))
            for k in range(len(p2)):
                proj2.append(dot(p2[k],vec))
            if not ((max(proj2) > max(proj1) and min(proj2) > max(proj1)) or (max(proj2) < min(proj1) and min(proj2) < min(proj1))):
                Flag += 1
        if Flag == len(p1)+len(p2): #if they have overlapped on every vector, they collide (in the x,y plane)
            return True
        else:
            return False

    def has_intersect_z(self,*things):
        '''finds if two objects (cylinders or boxes that have their vertical orientation parallel
            to (0,0,1)) intersect vertically (on the z axis)'''
        things = list(things)
        while len(things) > 1:#while there remain two objects that have not been checked against each other
            thing1 = things.pop(0)
            if thing1.__class__.__name__ == 'box':
                center1 = thing1.pos.z
                dist1 = abs(.5*thing1.size.z) #the distance to the top and bottom from the center
            if thing1.__class__.__name__ == 'cylinder' and thing1.axis.x == 0 and thing1.axis.y == 0: #if this is a vertically oriented cylinder
                dist1 = abs(.5*thing1.length)
                center1 = thing1.pos.z + (dist1 * (thing1.axis.z/abs(thing1.axis.z))) #the vertical center of the cylinder
                for thing2 in things: #same as above
                    if thing2.__class__.__name__ == 'box':
                        center2 = thing2.pos.z
                        dist2 = abs(.5*thing2.size.z)
                    if (
                        thing2.__class__.__name__ == 'cylinder'
                        and thing2.axis.x == 0
                    ):
                        dist2 = abs(.5*thing2.length)
                        center2 = thing2.pos.z + (dist2 * (thing2.axis.z/abs(thing2.axis.z)))
                    if center1+dist1-.01 > center2-dist2 and center1-dist1+.01 < center2+dist2: #If the two vertical spans are not disjoint
                        return True
        return False
            


    def collide(self,thing1,thing2):
        '''only works for boxes and cylinders with axis n*(0,0,1).
            Finds if they collide in the x, y, and z directions'''
        p1,p2 = self.find_corners(thing1,thing2)
        if self.has_intersect_xy(p1,p2):
            return self.has_intersect_z(thing1,thing2)
        return False

    def are_colliding(self,thing1,thing2):
        '''takes things with object list and tests every thing in each object list against each other for a collision.'''
        try:
            for subthing1 in thing1.ObjectList:
                try:
                    for subthing2 in thing2.ObjectList:
                        if self.collide(subthing1,subthing2):
                            return True
                except:
                    return False
        except:
            return False
        return False

    def collide_with_room(self,thing, room):
        return any(
            other_thing != thing and self.are_colliding(thing, other_thing)
            for other_thing in room.ObjectList
        )

class Room(object):
    def __init__(self,width=15,height=10,length=12,ambient=0.2,lights=[0.5*norm(vector(0,0,-2)),0.25*norm(vector(0,0.5,2))],autoscale=False,walls=True):
        self.Width = width
        self.Height = height
        self.Length = length
        self.Display = display(center = (width/2.,height/2.,length/2.), #create the display window
            uniform = True,
            range = (width,height,length),
            autoscale = autoscale,
            ambient = ambient,
            lights = lights,
            up = (0,0,1))
        self.Walls = Walls(width, height, length, walls) #create the walls
        self.ObjectList = [self.Walls] #add the walls to the object list - room object list should only contain things with an object list. Those object lists should only contain objects

    def handler(self): #take input, call interaction functions as appropriate
        if self.Display.kb.keys: # if the keyboard's been used
            k = self.Display.kb.getkey()
            if k == 'x' or k =='y' or k == 'z': #if the x,y,or z keys were pressed, call snap to view
                self.snap_to_view(k)
            if k =='s': #if the s key was pressed, called snap to grid (right now, it just snaps everything to grid.  if we want to change that, we can use the picking code below
                for thing in self.ObjectList[1:]:
                    thing.Snap_To_Grid(self.Display)
        m1 = self.Display.mouse.getevent() #get any mouse events
        for thing in self.ObjectList[1:]: #if an object is picked, or is currently being dragged or turned, call drag (currently a little buggy - try it out and you'll see what i mean)
            picked= False
            for part in thing.ObjectList:
                picked = (self.Display.mouse.pick == part) or picked
                if picked or thing.DragSettings[0] or thing.DragSettings[3]:
                    thing.drag(self,m1)
            print thing, picked
            
                
        
    def walls_view(self): #make the walls disappear if they're between the viewer and the center
        try:
            if self.Display.forward.x>.01:
                self.Walls.WestWall.visible = False
                self.Walls.EastWall.visible = True
            if self.Display.forward.x<-.01:
                self.Walls.EastWall.visible = False
                self.Walls.WestWall.visible = True
            if self.Display.forward.y>.01:
                self.Walls.NorthWall.visible = False
                self.Walls.SouthWall.visible = True
            if self.Display.forward.y<-.01:
                self.Walls.SouthWall.visible = False
                self.Walls.NorthWall.visible = True
            if self.Display.forward.z>0.23:
                self.Walls.Floor.visible = False
                self.Walls.Ceiling.visible = True
            if self.Display.forward.z<0.23:
                self.Walls.Ceiling.visible = False
                self.Walls.Floor.visible = True
        except:
            return
        
    def snap_to_view(self,k):
        if k == 'x':
            self.Display.forward = vector(1,0,0)
        elif k == 'y':
            self.Display.forward = vector(0,1,0)
        elif k == 'z':
            self.Display.forward = vector(0,0,-1)


class Walls: #class only to be called by room function to create walls
    def __init__(self,width, height, length, walls, material=materials.wood): #width = x, height = z, length = y, walls = boolean
        self.Floor = box(pos=(width/2.,length/2.,0), axis = (1,0,0), size=(width,length,.01), color=(1,0,0),material=materials.wood)
        self.ObjectList = [self.Floor]
        if walls:
            self.Ceiling = box(pos=(width/2.,length/2.,height), axis = (1,0,0), size=(width,length,.01),material=materials.wood)
            self.NorthWall = box(pos=(width/2.,0,height/2.), axis=(1,0,0), size = (width,.01,height),material=materials.wood)
            self.EastWall = box(pos=(width,length/2.,height/2.), axis=(1,0,0), size = (.01,length,height),material=materials.wood)
            self.SouthWall = box(pos=(width/2.,length,height/2.), axis=(1,0,0), size = (width,.01,height),material=materials.wood)
            self.WestWall = box(pos=(0,length/2.,height/2.), axis=(1,0,0),size = (.01,length,height),material=materials.wood)
            self.ObjectList += [
                self.Ceiling,
                self.NorthWall,
                self.EastWall,
                self.SouthWall,
                self.WestWall,
            ]


class DormRoom(Room):
    def __init__(self):
        Room.__init__(self, length = 18)
        self.Walls.DivWall1 = box(pos=(self.Width-4.5,12,self.Height/2.), axis=(1,0,0), size = (9,.01,self.Height),material=materials.wood)
        self.Walls.DivWall2 = box(pos=(1.5,12,self.Height/2.), axis=(1,0,0), size = (3,.01,self.Height),material=materials.wood)
        self.Walls.SinkBack = box(pos=(self.Width-7,self.Length-4.5,self.Height/2.), axis=(1,0,0), size = (.01,3,self.Height),material=materials.wood)
        self.Walls.SinkSide = box(pos=(self.Width-8,self.Length-3,self.Height/2.), axis=(1,0,0), size = (2,.01,self.Height),material=materials.wood)
        self.Walls.Sink = box(pos=(self.Width-8,self.Length-4.5,2.), axis=(1,0,0), size = (2,3,4),material=materials.earth)
        self.Walls.Window = box(pos=(self.Width/2.,0.01,6), axis=(1,0,0), size = (4.5,.01,5.5), color=color.yellow, material = materials.emissive)
        self.Walls.ObjectList = self.Walls.ObjectList + [self.Walls.DivWall1,self.Walls.DivWall2,self.Walls.SinkBack,self.Walls.SinkSide,self.Walls.Sink,self.Walls.Window]
    def walls_view(self):
        if self.Display.forward.x>.01:
            self.Walls.WestWall.visible = False
            self.Walls.EastWall.visible = True
        if self.Display.forward.x<-.01:
            self.Walls.EastWall.visible = False
            self.Walls.WestWall.visible = True
        if self.Display.forward.y>.01:
            self.Walls.NorthWall.visible = False
            self.Walls.Window.visible = False
            self.Walls.SouthWall.visible = True
        if self.Display.forward.y<-.01:
            self.Walls.SouthWall.visible = False
            self.Walls.NorthWall.visible = True
            self.Walls.Window.visible = True
        if self.Display.forward.z>0.23:
            self.Walls.Floor.visible = False
            self.Walls.Ceiling.visible = True
        if self.Display.forward.z<0.23:
            self.Walls.Ceiling.visible = False
            self.Walls.Floor.visible = True
    
class Furniture:
    def __init__(self, Room, Width, Length, Height, Position = []):
        Room.Display.select()
        self.Width = Width
        self.Length = Length
        self.Height = Height
        self.ObjectList = []
        self.Grid_Resolution = 1./6
        self.DragSettings = (False,None,None,False,None,None,None) #inital values for the drag function
        self.Collide = Colliding()
        self.Pos = vector(0,0,Height) if Position == [] else Position
        Room.ObjectList = Room.ObjectList + [self]

    def drag(self, room, m):
        drag, New_Pos, Drag_Pos, turn, Turn_Start, Turn_End, m1 = self.DragSettings
        m1 = m
        scene = room.Display
        if m1.click:
            drag = False
            turn = False
        elif m1.press  and not m1.alt: #If mousebutton is pressed and alt is not
            #If cursor position is within the bounds of the tabletop
            for part in self.ObjectList:
                drag = (m1.pick == part) or drag
            if drag:
                Drag_Pos = m1.pos #saves initial location
            picked = False
        elif m1.press: #If mousebutton is pressed and alt is also
            for part in self.ObjectList:
                turn = (m1.pick==part) or turn
            if turn:
                Turn_Start = m1.pos
            picked = False

        if drag:
            New_Pos = scene.mouse.pos
            if m1.drop or m1.click:
                drag = False
        while New_Pos and Drag_Pos and New_Pos!= Drag_Pos: #if the cursor has move from its initial location
            Move = New_Pos - Drag_Pos
            Drag_Pos = New_Pos #save new position
            #Move object to the new location
            for part in self.ObjectList:
                part.pos += Move
            '''if self.Collide.collide_with_room(self, room):
                for part in self.ObjectList:
                    part.pos -= Move'''

        if turn:
            Turn_End = scene.mouse.pos
            if m1.drop or m1.click:
                turn = False
        while Turn_End and Turn_Start and Turn_End!=Turn_Start:
            Distance = Turn_End.x - Turn_Start.x
            Turn_Start = Turn_End
            Spin = math.pi*(Distance/((self.Width+self.Length)))
            for part in self.ObjectList:
                part.rotate(angle = Spin, axis = (0,0,1), origin = self.ObjectList[0].pos)
        self.DragSettings = (drag, New_Pos, Drag_Pos, turn, Turn_Start, Turn_End, m1)
        
    def Snap_To_Grid(self, scene):
        Grid_X = int(self.ObjectList[0].pos.x/self.Grid_Resolution)
        Grid_Y = int(self.ObjectList[0].pos.y/self.Grid_Resolution)
        Grid_Z = int(self.ObjectList[0].pos.z/self.Grid_Resolution)
        Move_Pos = vector(self.ObjectList[0].pos.x- Grid_X*self.Grid_Resolution, \
                          self.ObjectList[0].pos.y- Grid_Y*self.Grid_Resolution, \
                          self.ObjectList[0].pos.z- Grid_Z*self.Grid_Resolution,)
        for part in self.ObjectList:
            part.pos -= Move_Pos
        self.picked = False
                        
                    


class Table(Furniture):
    def __init__(self, Room, Width,Length, Height, Wood_Thickness, Position = [], Leg_Radius = 0.5,\
                 Wood_Color = (255,0,0), Leg_Color = (0,255,0)):
        Furniture.__init__(self, Room, Width, Length, Height, Position)
        self.Wood_Thickness = Wood_Thickness
        self.X_Margin = Width/10. #Distance from leg center to edge
        self.Y_Margin = Length/10. #Distance from leg center to edge
        self.Leg_Radius = Leg_Radius
        self.Wood_Color = Wood_Color
        self.Leg_Color = Leg_Color
        self.CounterTop = box(pos = (self.Pos), size = (self.Width, self.Length, self.Wood_Thickness), \
                         color = self.Wood_Color, material = materials.wood)
        #Dimensions for the table legs
        self.Leg_Height = (self.Height - self.Wood_Thickness/2.)
        # Indicated side for indicated dimension (Left side, X dimension = Left_X
        self.Left_X = self.Pos[0] - (self.Width/2.) + self.X_Margin 
        self.Right_X = self.Pos[0] + (self.Width/2.) - self.X_Margin
        self.Top_Y = self.Pos[1] + (self.Length/2.) - self.Y_Margin
        self.Bottom_Y = self.Pos[1] - (self.Length/2.) + self.Y_Margin
        self.Leg1 = cylinder(pos = (self.Left_X, self.Top_Y, (self.Pos[2]-(self.Wood_Thickness/2.))), \
                        axis = (0,0,-self.Leg_Height), radius = self.Leg_Radius, color = self.Leg_Color)
        self.Leg2 = cylinder(pos = (self.Right_X, self.Top_Y, (self.Pos[2]-(self.Wood_Thickness/2.))), \
                        axis = (0,0,-self.Leg_Height), radius = self.Leg_Radius, color = self.Leg_Color)
        self.Leg3 = cylinder(pos = (self.Left_X, self.Bottom_Y, (self.Pos[2]-(self.Wood_Thickness/2.))), \
                        axis = (0,0,-self.Leg_Height), radius = self.Leg_Radius, color = self.Leg_Color)
        self.Leg4 = cylinder(pos = (self.Right_X, self.Bottom_Y, (self.Pos[2]-(self.Wood_Thickness/2.))), \
                        axis = (0,0,-self.Leg_Height), radius = self.Leg_Radius, color = self.Leg_Color)
        self.ObjectList = [self.CounterTop, self.Leg1, self.Leg2, self.Leg3, self.Leg4]
        

                        
class Chair(Table):
    def __init__(self, Room, Width, Length, Stool_Height, Back_Height, Wood_Thickness, Position = [],):
        Table.__init__(self, Room, Width, Length, Stool_Height, Wood_Thickness, Position,)
        self.Back_Height = Back_Height
        self.Seat_Color = (255, 255, 0)
        self.Back_Color = (0, 255, 255)
        self.Leg_Color = (0, 0, 255)
        Back_Y = self.Pos[1]+(self.Width/2.)-(self.Wood_Thickness/2.)
        Back_Z = self.Pos[2]+(self.Back_Height/2.)+(self.Wood_Thickness/2)
        self.Back = box(pos = (self.Pos[0], Back_Y, Back_Z),\
                   size = (self.Width, self.Wood_Thickness, self.Back_Height), material = materials.wood)
        self.ObjectList = self.ObjectList + [self.Back]


class Refrigerator(Furniture):
    def __init__(self, Room, Width, Length, Height, Position = [],):
        Furniture.__init__(self, Room, Width, Length, Height, Position)
        self.Body = box(pos = self.Pos, size = (self.Width, self.Length, self.Height))
        self.ObjectList = [self.Body]

class Bed(Furniture):
    def __init__(self, Room, Width,Length, Height, Back_Height, Wood_Thickness, Mattress_Thickness = 8./12, Position = [], Leg_Radius = 0.5,\
                 Wood_Color = (255,0,0), Sheet_Color = (255, 255, 255)):
        Furniture.__init__(self, Room, Width, Length, Height, Position)
        self.Mattress_Thickness = Mattress_Thickness
        self.Back_Height = Back_Height
        self.Sheet_Color = Sheet_Color
        self.Wood_Thickness = Wood_Thickness
        self.Wood_Color = Wood_Color
        self.Mattress = box(pos = (self.Pos), size = (self.Width, self.Length, self.Mattress_Thickness), \
                         color = self.Sheet_Color)
        self.Head_Pos = self.Pos+vector(0, self.Length/2., self.Back_Height/2.- self.Height)
        self.Foot_Pos = self.Pos+vector(0, -self.Length/2., self.Back_Height/2.- self.Height)
        self.HeadBoard = box(pos = self.Head_Pos, size = (self.Width, self.Wood_Thickness, self.Back_Height),\
                             color = self.Wood_Color, material = materials.wood)
        self.FootBoard = box(pos = self.Foot_Pos, size = (self.Width, self.Wood_Thickness, self.Back_Height),\
                             color = self.Wood_Color, material = materials.wood)        
        self.ObjectList = [self.Mattress, self.HeadBoard, self. FootBoard]

class BookShelf(Furniture):
    def __init__(self, Room, Width, Length, Height, Shelf_Number, Wood_Thickness,\
                 Position = [], Wood_Color = (255, 0, 0)):
        Furniture.__init__(self, Room, Width, Length, Height, Position)
        self.Pos = vector(0,0,0) if Position == [] else Position
        self.Wood_Thickness = Wood_Thickness
        self.Shelf_Number = Shelf_Number
        self.Wood_Color = Wood_Color
        self.Back_Pos = self.Pos + vector(0, Length, Height/2.)
        self.Backing = box(pos = self.Back_Pos, size = (self.Width,\
                       self.Wood_Thickness, self.Height), color = self.Wood_Color,\
                       material = materials.wood)
        self.Left_Pos = self.Pos + vector(Width/2., Length/2., Height/2.)
        self.Right_Pos = self.Pos + vector(-Width/2., Length/2., Height/2.)
        self.Left_Wall = box(pos = self.Left_Pos, size = (self.Wood_Thickness, \
                         self.Length, self.Height), color = self.Wood_Color,\
                         material = materials.wood)
        self.Right_Wall = box(pos = self.Right_Pos, size = (self.Wood_Thickness, \
                         self.Length, self.Height), color = self.Wood_Color,\
                         material = materials.wood)
        self.ObjectList = [self.Backing, self.Left_Wall, self.Right_Wall]
        self.Shelf_Increment = self.Height/float(self.Shelf_Number)
        for step in range(Shelf_Number):
            self.ObjectList.append(box(pos = self.Pos + vector(0, Length/2.,\
                                    step*self.Shelf_Increment), size = (self.Width, \
                                    self.Length, self.Wood_Thickness), color = self.Wood_Color,\
                                    material = materials.wood))

class Closet(BookShelf):
    def __init__(self, Room, Width, Length, Height, Wood_Thickness, Hanger_Height = None, Open = False,
                 Position = [],Wood_Color = (255, 0, 0), Hanger_Radius = 1./12):
        BookShelf.__init__(self, Room, Width, Length, Height, 1, Wood_Thickness,
                           Position, Wood_Color)
        self.Open = Open
        self.Hanger_Radius = Hanger_Radius
        self.Hanger_Height = Height*0.8 if Hanger_Height is None else Hanger_Height
        self.Top_Pos = vector(0, Length/2., self.Height)
        self.Top = box(pos = self.Top_Pos, size = (self.Width, self.Length, self.Wood_Thickness),
                       color = self.Wood_Color, material = materials.wood)
        if not self.Open:
            self.Left_Front_Pos = (self.Width/4., 0, self.Height/2.)
            self.Right_Front_Pos = (-self.Width/4., 0, self.Height/2.)
            self.Front_Size = (self.Width/2., self.Wood_Thickness, self.Height)
        else:
            self.Left_Front_Pos = (self.Width/2., -self.Width/4., self.Height/2.)
            self.Right_Front_Pos = (-self.Width/2., -self.Width/4., self.Height/2.)
            self.Front_Size = (self.Wood_Thickness, self.Width/2., self.Height)

        self.Left_Front = box(pos= self.Left_Front_Pos, size = self.Front_Size,
                              color = self.Wood_Color, material = materials.wood)
        self.Right_Front = box(pos = self.Right_Front_Pos, size= self.Front_Size,
                               color = self.Wood_Color, material = materials.wood)
        self.Hanger_Bar = cylinder(pos = (self.Right_Pos.x, self.Right_Pos.y, self.Hanger_Height),\
                                   axis = (self.Width, 0, 0), radius = self.Hanger_Radius, \
                                   color = self.Wood_Color, material = materials.wood)
        self.ObjectList.append(self.Top)
        self.ObjectList.append(self.Left_Front)
        self.ObjectList.append(self.Right_Front)
        self.ObjectList.append(self.Hanger_Bar)

    '''def spread(self, scene):
        clicked = False
        if scene.mouse.events: #If something with the mouse happens
            m1 = scene.mouse.getevent() #Figure out what happened
            if m1.press  and m1.ctrl: #If mousebutton is pressed and alt is not
                for part in self.ObjectList:
                    clicked = (m1.pick == part) or clicked
            if clicked:
                self.Open = not self.Open
                clicked = False'''

class Lamp(Furniture):
    def __init__(self, Room, Height, Base_Radius, Base_Height, Shade_Max_Radius, Shade_Min_Radius,
                 Shade_Height, Shade_Base=[], Shade_Thickness=0.5/12, Stand_Radius=1./12, Position = []):
        Furniture.__init__(self, Room, 1, 1, Height, Position)
        self.Base_Radius = Base_Radius
        self.Base_Height = Base_Height
        self.Shade_Max_Radius = Shade_Max_Radius
        self.Shade_Min_Radius = Shade_Min_Radius
        self.Stand_Radius = Stand_Radius
        self.Shade_Height = Shade_Height
        if Shade_Base == []:
            self.Shade_Base = 0.9 * self.Height
        else:
            self.Shade_Base = Shade_Base
        self.Shade_Thickness = Shade_Thickness
        self.Stand = cylinder(pos = self.Pos, axis = (0, 0, -self.Height), radius = self.Stand_Radius,\
                              material = materials.chrome)
        self.Shade_Scale = float(self.Shade_Min_Radius)/self.Shade_Max_Radius
        self.Shade_Shape = shapes.circle(radius = self.Shade_Max_Radius, np = 50,
                                         thickness = self.Shade_Thickness)
        self.Lamp_Shade = extrusion(pos = [(0, 0, self.Shade_Base), (0, 0, self.Shade_Base+self.Shade_Height)], \
                                    shape = self.Shade_Shape, color = (255,0,0),
                                    scale = [(1.0, 1.0), (self.Shade_Scale, self.Shade_Scale)])
        self.Radius_of_Circle = Base_Height*5. #Radius of the arc to make the cross section, should be
                                               #Calculated in a more rigorous way.
        self.Base_Circle = shapes.circle(pos = (-self.Base_Radius/2., -self.Radius_of_Circle + (self.Base_Height/2.)),\
                                  radius = self.Radius_of_Circle, np=60)
        self.Base_Rectangle = shapes.rectangle(width = self.Base_Radius, height = self.Base_Height)
        self.Base_Shape =self.Base_Circle&self.Base_Rectangle
        self.Base = extrusion(pos = paths.circle(up = (0,0,1), radius = self.Base_Radius/2., np = 50),
                              shape = self.Base_Shape, material = materials.wood)
        self.Shade_Cylinder = cylinder(pos = (0,0,self.Shade_Base), axis = (0,0,self.Shade_Height),
                                       radius  = self.Shade_Max_Radius, opacity = 0)
        self.Base_Cylinder = cylinder(pos = (0,0,0), axis = (0,0, self.Base_Height),
                                      radius = self.Base_Radius, opacity = 0)
        self.ObjectList = [self.Stand, self.Lamp_Shade, self.Base, self.Base_Cylinder, self.Shade_Cylinder]

class Handle(Furniture):
    def __init__(self, Room, Length, Handle_Orientation = (0,0,1),Clearance = 3./12, Handle_Radius = 0.5/12,
                 Strut_Radius = 0.5/12, Strut_Orientation = (0,1,0), Position = []):
        Furniture.__init__(self, Room, 1, Length, 1, Position)
        self.Handle_Orientation = Handle_Orientation
        self.Strut_Orientation = Strut_Orientation
        self.Clearance = Clearance
        self.Handle_Radius = Handle_Radius
        self.Strut_Radius = Strut_Radius
        self.Clearance_Offset = vector(0,0,0)
        self.Strut_Axis = vector(0,0,0)
        self.Main_Axis = vector(0,0,0)
        self.Handle_Pos = vector(0,0,0)
        for i in range(3):
            if self.Strut_Orientation[i] != 0:
                self.Clearance_Offset[i] = -self.Strut_Orientation[i]*self.Clearance
                self.Strut_Axis[i] = self.Strut_Orientation[i]*self.Clearance
            if self.Handle_Orientation[i] != 0:
                self.Main_Axis[i] = self.Handle_Orientation[i]*self.Length
                self.Handle_Pos[i] = (-self.Length/2.*self.Handle_Orientation[i])
        self.Handle = cylinder(pos = self.Handle_Pos, axis = self.Main_Axis, radius = self.Handle_Radius,
                               material = materials.wood)
        self.Strut1 = cylinder(pos = self.Handle_Pos, axis = self.Strut_Axis, radius = self.Strut_Radius,
                               material = materials.wood)
        self.Strut2 = cylinder(pos = self.Handle_Pos + self.Main_Axis, axis = self.Strut_Axis,
                               radius = self.Strut_Radius, material = materials.wood)
        self.ObjectList = [self.Handle, self.Strut1, self.Strut2]
        

