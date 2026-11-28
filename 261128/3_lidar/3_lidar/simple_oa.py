import math
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped
import rclpy
from rclpy.node import Node


class SimpleObstacleAvoider(Node):
    def __init__(self):
        super().__init__('simple_obstacle_avoider')

        self.cmd_pub = ...
        self.scan_sub = ...

        self.front_threshold = 0.25
        self.linear_speed = 0.2
        self.angular_speed = 0.5

    def scan_callback(self, scan: LaserScan):
        left_vals = [distance for distance in scan.ranges[:31] if math.isfinite(distance)]
        left_avg = sum(left_vals) / 30

        right_vals = [distance for distance in scan.ranges[-30:] if math.isfinite(distance)]
        right_avg = sum(right_vals) / 30

        front_vals = left_vals + right_vals
        front_min = min(front_vals) if front_vals else float('inf')

        ts = TwistStamped() #message envelop / find needed value and insert

        if front_vals > self.front_threshold:
            Go!!
            #ts.djfklsfh.djfklsfh.dataname = ...
            #ts._ = ...
        else:
            stop!!
            if (left_avg > right_avg) turn left 30 radian!! and go!!
            else turn right 30 radian!! and go!!

        ...  # 값이 설정된 TwistStamped 메세지를 Publish
        #self.publisher_.publish(ts)


def main():
    rclpy.init()
    node = SimpleObstacleAvoider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
