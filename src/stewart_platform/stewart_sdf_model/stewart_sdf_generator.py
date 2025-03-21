
from sdf_generator import CreateRobotSDF
import math
from piston_balls_pose import balls_link_pose,  piston_link_pose

# Define base platform parameters
base_height = 0.001
base_radius = 0.103   
base_mass = 0.00

# Define top platform parameters
platform_height = 0.001  
platform_radius = 0.0965
platform_mass = 0.0

# Docking element
platform_cyl_rad = 0.02
platform_cyl_len = 0.03
platform_sphere_rad = 0.02

# Define top and bottom balls parameters 
ball_radius = 0.0
platform_balls_radius = 0.0

# Define attachment angles between balls of base and moiving platform
attachment_angle_top = 15   
attachment_angle_bottom = 100

# Define distance between base and moving platform
base_platform_distance = 0.27
base_plat_dis = base_platform_distance  - 0.5*base_height - 0.5*platform_height - platform_balls_radius -ball_radius

# Rotation offset
offset = 0


# Now define piston (cylinder and shaft) radius , length and pose based on the above parameters
piston_radius = 0.005
piston_cylinder_link_pose , piston_length = piston_link_pose(radi_b=base_radius,radi_p=platform_radius,theta_b=attachment_angle_bottom,theta_p=attachment_angle_top,base_platform_distance=base_plat_dis,base_height=base_height, ball_radius=ball_radius, offset=offset) 



"""
Initialize stewart platform model and add control plugin 
"""
# Creat model object 
stewart_model = CreateRobotSDF()
# add plugin
stewart_model.add_plugin(name="gz::sim::systems::PosePublisher", filename="gz-sim-pose-publisher-system", publish_link_pose="true", use_pose_vector_msg="true", static_publisher="false", static_update_frequency="1")

stewart_model.add_jsp_plugin(name="gz::sim::systems::JointStatePublisher", filename="gz-sim-joint-state-publisher-system")


"""
First, Define all Joints:

1- prismatic joints - 6 numbers - type = prismatic
2- bottom ball joints - 6 numbers - type = universal
3- piston bottom pitch joints - 6 numbers - type = revolute
4- top ball joints - 6 numbers -type = revolute2
5- piston top pitch joints - 6 numbers - type = revolute

"""
# define prismatic joints , total number 6 legs
p_p_joint_vel_limit = str(1)
p_p_joint_eff_limit = str(100000)
p_p_joint_day_damping = str(1)
p_p_joint_axis_lower_limit = "0.0"
p_p_joint_axis_upper_limit = str(0.12)

for i in range(1,7): # parent, child
    stewart_model.add_joint(f"piston{i}_prismatic_joint",'prismatic' ,f"piston{i}_cylinder_link", f"piston{i}_shaft_linkL", pose="0 0 0 0 0 0", axis_xyz="0 0 1", axis_limit_lower_param=p_p_joint_axis_lower_limit,axis_limit_upper_param=p_p_joint_axis_upper_limit,axis_limit_velocity_param=p_p_joint_vel_limit,axis_limit_effort_param=p_p_joint_eff_limit,axis_dynamics_damping_param=p_p_joint_day_damping)

# define all joints movement limit 
lower_limit_angle = str(math.radians(-30)) # -30 degree
upper_limit_angle = str(math.radians(30))  # 30 degree
velocity_limit_on_balls = str(1)


# define bottom ball joints
for i in range(1,7):
    stewart_model.add_joint(f"bottom_ball{i}_joint","revolute","base_link",f"bottom_ball{i}_link",pose="0 0 0 0 0 0", axis_xyz="0 1 0", axis_limit_lower_param=lower_limit_angle,axis_limit_upper_param=upper_limit_angle,axis_limit_velocity_param=velocity_limit_on_balls)

# define piston bottom pitch joints
piston_bottom_pose = "0 0 "+str(-0.5*piston_length)+" 0 0 0"

for i in range(1,7):
    stewart_model.add_joint(f"piston{i}_bottom_pitch_joint","ball",f"bottom_ball{i}_link",f"piston{i}_cylinder_link",pose=piston_bottom_pose, axis_xyz="1 0 0")


# define top ball joints
for i in range(1,7):
    stewart_model.add_joint(f"top_ball{i}_joint","revolute","platform_link",f"top_ball{i}_link",pose="0 0 0 0 0 0", axis_xyz="0 1 0", axis_limit_lower_param=lower_limit_angle,axis_limit_upper_param=upper_limit_angle,axis_limit_velocity_param=velocity_limit_on_balls,axis_name_2="axis2",axis_name_2_xyz="0 0 1")


# define piston top pitch joints
piston_top_pose = "0 0 " + str(0.5*piston_length) +" 0 0 0"

for i in range(1,7):
    stewart_model.add_joint(f"piston{i}_top_pitch_joint","universal",f"top_ball{i}_link",f"piston{i}_shaft_linkU",pose=piston_top_pose, axis_xyz="1 0 0", axis_limit_lower_param=lower_limit_angle,axis_limit_upper_param=upper_limit_angle)



"""
Second, Define all Links:

1- base link - type = cylinder
2- platform link - type = cylinder
3- bottom ball links - 6 numbers - type = sphere
4- top ball links - 6 numbers - type = sphere
5- cylinder link - 6 numbers - type = cylinder
6- shaft link - 6 numbers - type = cylinder

"""
# add base link 
base_link_pose = "0 0 " + str(0.5*base_height) +" 0 0 0"
stewart_model.add_link("base_link",base_link_pose, 'cylinder',mass=base_mass,radius= base_radius,length=base_height,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Trunk") # Trunk Farina gole

# add platform link
platform_link_pose = "0 0 " + str(0.5*base_height+base_platform_distance) +" 0 0 0"  #-0.5*platform_height
stewart_model.add_link("platform_link",platform_link_pose, 'cylinder',mass=platform_mass,radius= platform_radius,length=platform_height,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Footway")

stewart_model.add_link("platform_cyl", "0 0 " +str(0.5*base_height+base_platform_distance + platform_cyl_len/2)+" 0 0 0", "cylinder", 0, platform_cyl_rad, platform_cyl_len - 0.001, "file://media/materials/scripts/gazebo.material", "Gazebo/Gold");

stewart_model.add_link("platform_sphere", "0 0 " +str(0.5*base_height+base_platform_distance + platform_cyl_len)+" 0 0 0", "sphere", 0, platform_sphere_rad, 0, "file://media/materials/scripts/gazebo.material", "Gazebo/Gold");

stewart_model.add_joint("plat_link_to_plat_cyl", "fixed", "platform_link", "platform_cyl", "0 0 0 0 0 0")
stewart_model.add_joint("plat_link_to_plat_sphere", "fixed", "platform_link", "platform_sphere", "0 0 0 0 0 0")

# add bottom ball links pose
_, bottom_balls_link_pose = balls_link_pose(base_radius,attachment_angle_bottom, base_height,0, offset=offset)
for i in range(1,7):
    stewart_model.add_link(f"bottom_ball{i}_link",bottom_balls_link_pose[f"ball{i}_link_pose"],geometry='sphere', mass=0.7,radius=ball_radius,length=0.1,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Gold")

# add top ball links pose
top_ball_height = 0.5*base_height+base_platform_distance - platform_height
_, top_balls_link_pose = balls_link_pose(platform_radius,attachment_angle_top,top_ball_height,0, offset=offset)

for i in range(1,7):
    stewart_model.add_link(f"top_ball{i}_link",top_balls_link_pose[f"ball{i}_link_pose"],geometry='sphere', mass=0.7,radius=platform_balls_radius,length=0.1,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/White")


for i in range(1,7):
    if i == 1:
        stewart_model.add_link(f"piston{i}_cylinder_link",piston_cylinder_link_pose[f"piston{i}_link_pose"],geometry='cylinder', mass=0.7,radius=piston_radius,length=piston_length,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Red")
    elif i == 2:
        stewart_model.add_link(f"piston{i}_cylinder_link",piston_cylinder_link_pose[f"piston{i}_link_pose"],geometry='cylinder', mass=0.7,radius=piston_radius,length=piston_length,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Green")
    elif i == 3:
        stewart_model.add_link(f"piston{i}_cylinder_link",piston_cylinder_link_pose[f"piston{i}_link_pose"],geometry='cylinder', mass=0.7,radius=piston_radius,length=piston_length,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Yellow")
    elif i == 4:
        stewart_model.add_link(f"piston{i}_cylinder_link",piston_cylinder_link_pose[f"piston{i}_link_pose"],geometry='cylinder', mass=0.7,radius=piston_radius,length=piston_length,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Purple")
    elif i == 5:
        stewart_model.add_link(f"piston{i}_cylinder_link",piston_cylinder_link_pose[f"piston{i}_link_pose"],geometry='cylinder', mass=0.7,radius=piston_radius,length=piston_length,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/White")
    elif i == 6:
        stewart_model.add_link(f"piston{i}_cylinder_link",piston_cylinder_link_pose[f"piston{i}_link_pose"],geometry='cylinder', mass=0.7,radius=piston_radius,length=piston_length,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Blue")
    else:
        stewart_model.add_link(f"piston{i}_cylinder_link",piston_cylinder_link_pose[f"piston{i}_link_pose"],geometry='cylinder', mass=0.7,radius=piston_radius,length=piston_length,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/DarkGrey")

# define piston shaft link pose 
# note: piston shaft pose is equal to piston cylinder link pose

for i in range(1,7):
    stewart_model.add_link(f"piston{i}_shaft_linkU", piston_cylinder_link_pose[f"piston{i}_link_pose"],geometry='cylinder', mass=0.7,radius=0.5*piston_radius,length=piston_length,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Black")

for i in range(1,7):
    stewart_model.add_link(f"piston{i}_shaft_linkL", piston_cylinder_link_pose[f"piston{i}_link_pose"],geometry='cylinder', mass=0.7,radius=0.5*piston_radius,length=piston_length,material_script_uri_param="file://media/materials/scripts/gazebo.material",material_script_name_param="Gazebo/Black")


for i in range(1,7):
    stewart_model.add_glue("stewart", f"piston{i}_shaft_linkL", f"piston{i}_shaft_linkU")

for i in range(1,7):
    stewart_model.add_control(f"piston{i}_prismatic_joint", str(50000), str(10000), str(1000))

# finally, save the model in sdf format
stewart_model.save_model("stewart_sdf")
