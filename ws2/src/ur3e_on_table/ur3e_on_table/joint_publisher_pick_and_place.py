import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import pkg_resources
import numpy as np

def linear_interpolate(p1, p2, a):
    return (1-a)*p1 + a*p2

class JointPublisherPickAndPlace(Node):

    def __init__(self):
        super().__init__('joint_publisher_pick_and_place')
        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)
        timer_period = 0.1 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0
        self.t = 0
        self.timer_period = timer_period
        
        # define your start/end points
        self.p1 = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
        self.p2 = np.array([-1.0,-1.0,-1.0,-1.0,-1.0,-1.0])

    def timer_callback(self):

        # 0..5 seconds: stay at p1
        # 5..10 seconds: move towards p2
        # 10..15 seconds: stay at p2
        # 15..20 seconds:: move towards p1
        if self.t < 5:
            a = 0
        elif self.t < 10:
            a = (self.t - 5)/5
        elif self.t < 15:
            a = 1
        elif self.t < 20:
            a = 1 - (self.t - 15)/5
        
        p = linear_interpolate(self.p1, self.p2, a).tolist()

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                    'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
        msg.position = p
        msg.velocity = []
        msg.effort = []

        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing position: "{msg.position}"')
        # reset self.t after 20 seconds are up
        self.t += self.timer_period
        if self.t >= 20:
            self.t = 0


def main(args=None):
    rclpy.init(args=args)

    joint_publisher_pick_and_place_node = JointPublisherPickAndPlace()

    rclpy.spin(joint_publisher_pick_and_place_node)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    joint_publisher_pick_and_place_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()