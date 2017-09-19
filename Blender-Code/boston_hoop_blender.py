# boston_hoop_blender.py
#
# By Filip Strand and Jakob Arnoldsson
# May 2016
# (used with Blender 2.76) 
# 
# This script is most easily run by
# starting up blender with the
# --python flag via the command line.
# The script assumes that there is a file
# called 'maple_data.txt' containing the
# information about the generalized
# coordinates in the following format
# (columns are separated by space):
# 
# | t   | q_1 | ... | q_n | u_1 | ... | u_n |
# |-----+-----+-----+-----+-----+-----+-----|
# | t_0 |     |     |     |     |     |     |
# | t_1 |     |     |     |     |     |     |
# | .   |     |     |     |     |     |     |
# | .   |     |     |     |     |     |     |
# | t_k |     |     |     |     |     |     |
# 
# To start the animation, press alt-A or manually
# move through the timeline. 

import bpy
import math
import mathutils

# IMPORTANT: Set the rendering engine to CYCLES
scn = bpy.context.scene
scn.render.engine = 'CYCLES'

# Geometric Constants
R = 5
r = 0.6
H0 = math.pi-0.1
H1 = math.pi+0.1
l0 = 5*math.pi/2
l1 = 5*math.pi/2
m0 = 100
m1 = 10
k0 = 900
k1 = 300
g = 9.82

# Read the 'maple_data.txt' file
dat=open("/path/to/maple_data.txt","r")
t=[]
q1=[]
q2=[]
q3=[]
for line in dat.readlines():
        row=list(map(float,line.split()))
        t.append(row[0])
        q1.append(row[1])
        q2.append(row[2])
        q3.append(row[3])
dat.close()


# Set the number of frame to be the same
# as the amount of rows in the data file 
scn = bpy.context.scene 
scn.frame_end = len(t)    


# ----------Build Geometric Primitives-----------------
# IMPORANT!: Do not change the order in which these
# objects are made, this will cause mixups in referring
# to the correct objects later.

# Remove the default cube at the start
bpy.ops.object.delete()

# add Plane
bpy.ops.mesh.primitive_plane_add(radius = 100)
plane = bpy.data.objects.get("Plane")

# add Plane.001
bpy.ops.mesh.primitive_plane_add(radius = 100)
plane_001 = bpy.data.objects.get("Plane.001")

# add Cube
bpy.ops.mesh.primitive_cube_add()
cube = bpy.data.objects.get("Cube")

# add Cylinder
bpy.ops.mesh.primitive_cylinder_add(radius = r,
                                    depth = 3)
cylinder = bpy.data.objects.get("Cylinder")

# Add Shpere (moving)
bpy.ops.mesh.primitive_uv_sphere_add(segments = 50,
                                     ring_count = 50,
                                     size = r-0.1)
sphere = bpy.data.objects.get("Sphere")

# Add Shpere.001 (moving)
bpy.ops.mesh.primitive_uv_sphere_add(segments = 50,
                                     ring_count = 50,
                                     size = r-0.1)
sphere_001 = bpy.data.objects.get("Sphere.001")

# Add Torus (moving)
bpy.ops.mesh.primitive_torus_add(major_radius = R,
                                 minor_radius = r,
                                 major_segments=300,
                                 minor_segments=30)
torus = bpy.data.objects.get("Torus")
# ----------Build Geometric Primitives-----------------



# :::::::: MAKING MATERIALS::::::::::::::::::::::::::::
# Here we merely construct and assign empty materials
# to every object that we will later change in the Blender GUI.
# The only important property at this stage is the
# unique name for the different materials.

plane.data.materials.append(bpy.data.materials.new(name="Material1"))
plane_001.data.materials.append(bpy.data.materials.new(name="Material2"))
cube.data.materials.append(bpy.data.materials.new(name="Material3"))
cylinder.data.materials.append(bpy.data.materials.new(name="Material4"))
sphere.data.materials.append(bpy.data.materials.new(name="Material5"))
sphere_001.data.materials.append(bpy.data.materials.new(name="Material6"))
torus.data.materials.append(bpy.data.materials.new(name="Material7"))

# Material for the springs (it is set later in update_springs(scene,n))
material8 = bpy.data.materials.new(name="Material8")
# :::::::: MAKING MATERIALS::::::::::::::::::::::::::::


# This function draws the first spring for each frame.
# The mesh is unfortunately redrawn completely for every
# frame making it very expensive to animate. As shown later
# we recommend to disable this function for performance 
# reasons when working and re-enabling it when rendering.
# (NOTE: The springs are math-surfaces generated by the
# plug-in 'bpy.ops.mesh.primitive_xyz_function_surface'
# which is included in Blender but have to be activated
# in settings.)
def set_spring_1_position(n):

        # Spring properties
        spiral_radius = 0.25
        wire_radius = 0.1
        coils_number = 25
        spring_height = ((l0/R)+q1[n])*R*2*math.pi/coils_number

        # Change to polar coordinates          
        alpha_1 = "((" + str(spring_height) + "/(2*pi))*u +" + str(wire_radius) + "*sin(2*pi*v))"
        alpha_2 = "(("  + str(spiral_radius) + "+" + str(wire_radius) + "*cos(2*pi*v))*cos(2*pi*u))"
        alpha_3 = "(("  + str(spiral_radius) + "+" + str(wire_radius) + "*cos(2*pi*v))*sin(2*pi*u))"

        beta_1 = "(-(" + str(R) +  "-" + alpha_3 + ")*cos(" + str(-H0-math.pi) +  " + (" + alpha_1 + "/" + str(R)  + ")))"
        beta_2 = alpha_2
        beta_3 = "((" + str(R) +  "-" + alpha_3 + ")*sin(" + str(-H0-math.pi) + " + (" + alpha_1 + "/" + str(R)  + ")) +" + str(R) + ")"

        beta_1_rot =  "cos(" + str(q2[n])  + ")*" + beta_1 + "- sin(" + str(q2[n])  + ")*" + beta_2 
        beta_2_rot =  "sin(" + str(q2[n])  + ")*" + beta_1 + "+ cos(" + str(q2[n])  + ")*" + beta_2
        beta_3_rot = beta_3
        
        bpy.ops.mesh.primitive_xyz_function_surface(x_eq = beta_1_rot,
                                                    y_eq= beta_2_rot,
                                                    z_eq= beta_3_rot,
                                                    range_u_min = 0,
                                                    range_u_max = coils_number,
                                                    range_v_min = 0,
                                                    range_v_max = 1,
                                                    wrap_u = False,
                                                    wrap_v = False,
                                                    range_u_step = 200,
                                                    range_v_step = 200)


        for item in bpy.data.objects:  
                 if item.type == "MESH" and item.name.startswith("XYZ"):
                         item.name = "spring_1"



# Identical function as before but for the second spring
# The difference is in the X,Y,Z coordinate description 
def set_spring_2_position(n):

        # Spring properties
        spiral_radius = 0.25
        wire_radius = 0.1
        coils_number = 25
        spring_height = (-(l1/R)-q3[n])*R*2*math.pi/coils_number

        # Change to polar coordinates          
        alpha_1 = "((" + str(spring_height) + "/(2*pi))*u +" + str(wire_radius) + "*sin(2*pi*v))"
        alpha_2 = "(("  + str(spiral_radius) + "+" + str(wire_radius) + "*cos(2*pi*v))*cos(2*pi*u))"
        alpha_3 = "(("  + str(spiral_radius) + "+" + str(wire_radius) + "*cos(2*pi*v))*sin(2*pi*u))"

        beta_1 = "(" + str(R) +  "-" + alpha_3 + ")*cos(" + str(H1) + " - (" + alpha_1 + "/" + str(R)  + "))"
        beta_2 = alpha_2
        beta_3 = "(" + str(R) +  "-" + alpha_3 + ")*sin(" + str(H1) + " - (" + alpha_1 + "/" + str(R)  + ")) +" + str(R)

        beta_1_rot =  "cos(" + str(q2[n])  + ")*" + beta_1 + "- sin(" + str(q2[n])  + ")*" + beta_2 
        beta_2_rot =  "sin(" + str(q2[n])  + ")*" + beta_1 + "+ cos(" + str(q2[n])  + ")*" + beta_2
        beta_3_rot = beta_3

        
        bpy.ops.mesh.primitive_xyz_function_surface(x_eq = beta_1_rot,
                                                    y_eq= beta_2_rot,
                                                    z_eq= beta_3_rot,
                                                    range_u_min = 0,
                                                    range_u_max = coils_number,
                                                    range_v_min = 0,
                                                    range_v_max = 1,
                                                    wrap_u = False,
                                                    wrap_v = False,
                                                    range_u_step = 200,
                                                    range_v_step = 200)


        for item in bpy.data.objects:  
         if item.type == "MESH" and item.name.startswith("XYZ"):
                 item.name = "spring_2"


        

# This function updates the two spring positions for every
# frame. The function can be commented out for performance
# reasons as the redrawing of the springs are slow
def update_springs(scene,n):

        # Remove the previous two springs from the last frame
        bpy.ops.object.select_all(action='DESELECT')
        loopindex = 0 
        for item in bpy.data.objects:  
                 if item.type == "MESH" and item.name.startswith("spring"):  
                        bpy.data.objects[item.name].select = True;
                        try:
                                scene.objects.unlink(bpy.data.objects[item.name])                                
                                bpy.data.objects.remove(item)
                        except:
                                pass
                        loopindex = loopindex + 1
                                
        set_spring_1_position(n)
        set_spring_2_position(n)

        spring_1 = bpy.data.objects.get("spring_1")
        spring_2 = bpy.data.objects.get("spring_2")

        spring_1.data.materials.append(material8)
        spring_2.data.materials.append(material8)
                
        bpy.ops.object.select_all(action='DESELECT')


# -------------Set the geometry for the objects----------- 
def set_plane():        
        plane.location = (0,0,-3.8)
        
def set_plane_001():
        plane_001.location = (0,18,0)
        plane_001.rotation_euler = (0,math.pi/2,math.pi/2)

def set_cube():
        cube.location = (0,0,-3.5)
        cube.scale = (3, 2, 0.3)
        
def set_cylinder(n):
        cylinder.location = (0, 0, -3.5/2)
        cylinder.rotation_euler = (0, 0, q2[n])

def set_sphere(n):
        X = R*math.cos(H0-l0/R-q1[n])
        Y = 0
        Z = R*math.sin(H0-l0/R-q1[n])+R
        X_rot = math.cos(q2[n])*X - math.sin(q2[n])*Y
        Y_rot = math.sin(q2[n])*X + math.cos(q2[n])*Y
        Z_rot = Z
        sphere.location = (X_rot, Y_rot, Z_rot)
        
def set_sphere_001(n):
        X = R*math.cos(H1+l1/R+q3[n])
        Y = 0
        Z = R*math.sin(H1+l1/R+q3[n])+R
        X_rot = math.cos(q2[n])*X - math.sin(q2[n])*Y
        Y_rot = math.sin(q2[n])*X + math.cos(q2[n])*Y
        Z_rot = Z
        sphere_001.location = (X_rot, Y_rot, Z_rot)

def set_torus(n):
        torus.location = (0,0,R)
        torus.rotation_euler  = (math.pi/2,0,q2[n])
# -------------Set the geometry for the objects-----------

# Setting the static geometry
def setStaticGeometry():
        set_plane()
        set_plane_001()
        set_cube()
                
# This function gets called every time the frame updates
def my_handler(scene):
    n = int(scene.frame_current)
    updateMovingGeometry(scene,n)

# Setting the moving geometry
def updateMovingGeometry(scene,n):
        set_sphere(n)
        set_sphere_001(n)
        set_torus(n)
        set_cylinder(n)
        update_springs(scene,n)
        # Comment out 'update_springs(scene,n)' to remove the drawing of the springs
        # These are made using custom MATH-SURFACE method and are slow to render
        # A tip can be to disable these during modeling and reanableing the springs
        # when a final render is to be made


# Set the static geometry at startup
setStaticGeometry()
# Set the geometry update to the first frame
updateMovingGeometry(my_handler,1)
# Run every time the frame is chnaged
bpy.app.handlers.frame_change_pre.append(my_handler) 