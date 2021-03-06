import rospy
import tf2_ros as tf2
import math
from tf.transformations import quaternion_from_euler
from tf2_geometry_msgs import PoseStamped
from geometry_msgs.msg import Point, Quaternion
from tf.transformations import quaternion_from_euler

from dynamic_stack_decider.abstract_action_element import AbstractActionElement


class GoToBall(AbstractActionElement):
    def __init__(self, blackboard, dsd, parameters=None):
        super(GoToBall, self).__init__(blackboard, dsd, parameters)

        if 'target' not in parameters.keys():
            rospy.logerr('The parameter \'{}\' could not be used to decide whether map information is accesible'.format(parameters['target']))
        else:
            self.target = parameters['target']

        self.approach_distance = blackboard.config['ball_approach_distance']

    def perform(self, reevaluate=False):
        ball_position = self.blackboard.world_model.get_ball_position_uv()
        if not ball_position:
            return
        ball_u, ball_v = ball_position

        if 'map_goal' == self.target:
            ball_point = (ball_u, ball_v, self.blackboard.world_model.get_map_based_opp_goal_angle_from_ball())
        elif 'detection_goal' == self.target:
            x_dist = self.blackboard.world_model.get_detection_based_goal_position_uv()[0] - \
                     self.blackboard.world_model.get_ball_position_uv()[0]
            y_dist = self.blackboard.world_model.get_detection_based_goal_position_uv()[1] - \
                     self.blackboard.world_model.get_ball_position_uv()[1]
            angle = math.atan2(y_dist, x_dist)
            ball_point = (ball_u, ball_v, angle)
        elif 'none' == self.target or 'current_orientation' == self.target:
            ball_point = (ball_u, ball_v, 0)
        elif 'close' == self.target:
            angle = math.atan2(ball_v, ball_u)
            ball_point = (ball_u, ball_v, angle)
        else:
            rospy.logerr("Target %s for go_to_ball action not specified.", self.target)
            return
        point = align(Point(*ball_point), self.approach_distance)

        pose_msg = PoseStamped()
        pose_msg.header.stamp = rospy.Time.now()
        pose_msg.header.frame_id = 'base_footprint'

        pose_msg.pose.position = Point(point.x, point.y, 0)

        quaternion = quaternion_from_euler(0, 0, point.z)
        pose_msg.pose.orientation.x = quaternion[0]
        pose_msg.pose.orientation.y = quaternion[1]
        pose_msg.pose.orientation.z = quaternion[2]
        pose_msg.pose.orientation.w = quaternion[3]

        self.blackboard.pathfinding.publish(pose_msg)


def align(pose_point, distance):
    # type: (Point, float) -> Point
    point = Point()
    point.x = pose_point.x - distance * math.cos(pose_point.z)
    point.y = pose_point.y - distance * math.sin(pose_point.z)
    point.z = pose_point.z
    return point
