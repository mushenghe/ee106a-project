#!/usr/bin/env python
from ar_track_alvar_msgs.msg import AlvarMarkers
from geometry_msgs.msg import PoseStamped
import intera_external_devices
import intera_interface
from intera_interface import CHECK_VERSION
import moveit_commander
from moveit_msgs.msg import OrientationConstraint, Constraints
import numpy as np
import rospy
import sys
import time
import tf

class doctor_sawyer:
    def __init__(self, side):
        self.ar_track_data = []
        self.table_x, self.table_y, self.table_z = 0, 0, 0
        self.limb = intera_interface.Limb(side)

    # call back function for ar tag tracking
    def ar_track_callback(self, data):
        # If already get enough data, ignore it
        if len(self.ar_track_data) > 10:
            return

        if len(data.markers) == 0:
            return

        rospy.logdebug("Received AR track data")
        pos = data.markers[0].pose.pose.position
        self.ar_track_data.append((pos.x, pos.y, pos.z))

        if len(self.ar_track_data) == 10:
            # Average the received data
            # might need to filter out outliers in the future
            self.table_x = np.mean([pos[0] for pos in self.ar_track_data])        
            self.table_y = np.mean([pos[1] for pos in self.ar_track_data])        
            self.table_z = np.mean([pos[2] for pos in self.ar_track_data])    
            rospy.logwarn("Table center found at: %s", str([self.table_x, self.table_y, self.table_z]))   
#            print("Table center found at: " + str([self.table_x, self.table_y, self.table_z]))
#            listener = tf.TransformListener()
#            print(listener.allFramesAsString())
#
#            while not rospy.is_shutdown():
#                try:
#                    (trans,rot) = listener.lookupTransform('/head_camera', '/base', rospy.Time(0))
#                    break
#                except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
#                    continue
    
            # Look up TF transform
#            g = listener.fromTranslationRotation(trans, rot)
#            point_camera_frame = np.array([camera_x, camera_y, camera_z, 1])
#            print(point_camera_frame)
#            print(g.dot(point_camera_frame))


    # Find an AR tag that designates the center of camera
    def find_table(self):
        # Capture output from topic 'visualization_marker'
        rospy.Subscriber("ar_pose_marker", AlvarMarkers, self.ar_track_callback)

        # Call TF to transform to coordinate w.r.t. base frame

    def poke_at(self, arm, x, y):
        #First goal pose ------------------------------------------------------
        goal = PoseStamped()
        goal.header.frame_id = "base"
    
        #x, y, and z position
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.position.z = self.table_z + 0.30
        
        #Orientation as a quaternion
        goal.pose.orientation.x = 0.0
        goal.pose.orientation.y = -1.0
        goal.pose.orientation.z = 0.0
        goal.pose.orientation.w = 0.0
    
        #Set the goal state to the pose you just defined
        #arm.set_pose_target(goal)
        arm.set_position_target([x, y, self.table_z + 0.30])
    
        #Set the start state for the right arm
        arm.set_start_state_to_current_state()
        

        #Plan a path
        right_plan = arm.plan()
    
        #Execute the plan
        confirmed = raw_input('Execute? y/n')
        if confirmed == "y":
            arm.execute(right_plan)
        else:
            print("Aborted")
            return "Failed to poke at " + str(x) + "," + str(y)

        #Start poking down in the z-direction using torque control
        rospy.sleep(1)
        force = self.limb.endpoint_effort()['force']
        torque = self.limb.endpoint_effort()['torque']

        # Keep poking down as long as force within threshold
        thres = 5.0 #threshold in Newton
        while (force.x ** 2 + force.y ** 2 + force.z ** 2 < thres ** 2):
            rospy.sleep(1)
            force = self.limb.endpoint_effort()['force']
            torque = self.limb.endpoint_effort()['torque']
            rospy.logdebug("End Effector Force is: " + str([force.x, force.y, force.z]))
            goal.pose.position.z = goal.pose.position.z - 0.02
            arm.set_pose_target(goal)
            arm.set_start_state_to_current_state()        
            right_plan = arm.plan()
    
            #Execute the plan
            confirmed = raw_input('Keep probing downwards? y/n')
            if confirmed == "y":
                arm.execute(right_plan)
            else:
                break

        rospy.logdebug("Starting to probe in a new position") 


    # Outputs a 2D array of hardness in each point probed
    # Parameters: nx, ny, dx, dy
    # Probes at [table_x-nx*dx, table_x + nx*dx]
    # Returns a dictionary with key as (x, y) and value as something representing hardness
    def probe(self, nx, ny, dx, dy):
        #Initialize arms
        robot = moveit_commander.RobotCommander()
        scene = moveit_commander.PlanningSceneInterface()


        right_arm = moveit_commander.MoveGroupCommander('right_arm')
        right_arm.set_planner_id('RRTConnectkConfigDefault')
        right_arm.set_planning_time(15)

        # Set constraints
        rospy.sleep(2)

        # Assuming you're facing the wall, looking at the robot
        # And the robot's computer is to your left
        # Then Wall 1 is the wall on "your" right
        # Wall 2 is the wall to "your" left
        # Wall 3 is the wall in the back
        #raw_input("press any key to add wall 1")
        p = PoseStamped()
        p.header.frame_id = robot.get_planning_frame()
        p.pose.position.x = 0.7
        p.pose.position.y = 0.
        p.pose.position.z = 0.
        scene.add_box("wall1", p, (0.1, 5, 5))


        #raw_input("press any key to add wall 2")
        p = PoseStamped()
        p.header.frame_id = robot.get_planning_frame()
        p.pose.position.x = -1
        p.pose.position.y = 0.
        p.pose.position.z = 0.
        scene.add_box("wall2", p, (0.1, 5, 5))


        #raw_input("press any key to add wall 3")
        p = PoseStamped()
        p.header.frame_id = robot.get_planning_frame()
        p.pose.position.x = 0
        p.pose.position.y = 0.7
        p.pose.position.z = 0.
        scene.add_box("wall3", p, (5, 0.1, 5))

        #raw_input("press any key to add patient")
        p = PoseStamped()
        p.header.frame_id = robot.get_planning_frame()
        p.pose.position.x = self.table_x
        p.pose.position.y = self.table_y
        p.pose.position.z = self.table_z / 2.0
        scene.add_box("patient", p, (0.3, 0.3, self.table_z / 2.0))

        orien_const = OrientationConstraint()
        orien_const.link_name = "right_gripper";
        orien_const.header.frame_id = "base";
        orien_const.orientation.y = -1.0;
        orien_const.absolute_x_axis_tolerance = 0.1;
        orien_const.absolute_y_axis_tolerance = 0.1;
        orien_const.absolute_z_axis_tolerance = 50;
        orien_const.weight = .5;
        consts = Constraints()
        consts.orientation_constraints = [orien_const]
        right_arm.set_path_constraints(consts)

        ans = {} # start with empty dictionary
        for i in range(-nx, nx+1):
            for j in range(-nx, nx+1):
                ans[(i, j)] = self.poke_at(right_arm, self.table_x + i * dx, self.table_y + j * dy)
        return ans

    # Outputs temperature measure
    def measure_temperature(self):
        pass

    def measure_pulse(self):
        pass


def main():
    rp = intera_interface.RobotParams()
    valid_limbs = rp.get_limb_names()
    rospy.init_node('doctor', log_level=rospy.DEBUG)        

    moveit_commander.roscpp_initialize(sys.argv)
    rs = intera_interface.RobotEnable(CHECK_VERSION)
    init_state = rs.state().enabled

    rs.enable()

    rospy.logdebug("Closing gripper...")
    #raw_input("Press any key to close gripper")
    right_gripper = intera_interface.gripper.Gripper('right')
    right_gripper.calibrate()    
    #rospy.sleep(2.0)
    #raw_input("Press any key to close gripper")
    right_gripper.close()
    #rospy.sleep(2.0)
    rospy.logdebug("Gripper closed")
    doctor = doctor_sawyer(valid_limbs[0])
    doctor.find_table()


    while (not rospy.is_shutdown()):
        action = raw_input("(P)oke, (H)eartbeat, (T)emperature?")
        if (action == "P"):
            print(doctor.probe(2, 2, 0.05, 0.05))

    rospy.spin()


if __name__ == '__main__':
    main()
