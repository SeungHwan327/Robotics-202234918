import math
import time

import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class ReverseObstacleAvoider(Node):
    def __init__(self):
        super().__init__('reverse_obstacle_avoider')
        self.cmd_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, qos_profile_sensor_data)

        self.front_limit = 0.35      
        self.back_limit = 0.30        
        self.forward_speed = 0.15    
        self.back_speed = 0.10       
        self.turn_speed = 0.60       
        self.back_time = 1.0         
        self.turn_time = 1.5         
        self.scan_timeout = 0.5      
        self.inf_is_clear = False   

        self.state = 'MOVE'
        self.until = 0.0
        self.turn_dir = 1.0
        self.front = self.back = self.left = self.right = None
        self.last_scan = None
        self.timer = self.create_timer(0.05, self.control)

    def sector_min(self, scan, center_deg):
        center = math.radians(center_deg)
        values = []
        for i, distance in enumerate(scan.ranges):
            angle = scan.angle_min + i * scan.angle_increment
            offset = math.atan2(math.sin(angle - center),
                                math.cos(angle - center))
            if abs(offset) > math.radians(30):
                continue
            if distance == math.inf and self.inf_is_clear:
                distance = scan.range_max
            if math.isfinite(distance) and distance >= 0:
                if distance < scan.range_min:
                    values.append(0.0)
                elif distance <= scan.range_max:
                    values.append(distance)
        return min(values) if values else None

    def scan_callback(self, scan):
        self.last_scan = time.monotonic()
        if (not math.isfinite(scan.angle_increment) or
                len(scan.ranges) * abs(scan.angle_increment) < 2 * math.pi - 0.05):
            self.front = self.back = self.left = self.right = None
            return
        self.front = self.sector_min(scan, 0)
        self.left = self.sector_min(scan, 90)
        self.right = self.sector_min(scan, -90)
        self.back = self.sector_min(scan, 180)

    def send(self, linear=0.0, angular=0.0):
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = float(linear)
        msg.twist.angular.z = float(angular)
        self.cmd_pub.publish(msg)

    def start_turn(self, now):
        self.state = 'TURN'
        self.until = now + self.turn_time
        self.get_logger().info('TURN')

    def control(self):
        now = time.monotonic()
        linear = angular = 0.0
        if (self.last_scan is None or
                now - self.last_scan > self.scan_timeout or self.front is None):
            self.state = 'MOVE'
            self.send()
            return

        if self.state == 'MOVE':
            if self.front > self.front_limit:
                linear = self.forward_speed
            elif self.left is not None and self.right is not None:
                self.turn_dir = 1.0 if self.left > self.right else -1.0
                self.state = 'BACK'
                self.until = now + self.back_time
                self.get_logger().info('BACK')

        elif self.state == 'BACK':
            if self.back is None:
                self.state = 'MOVE'  
            elif self.back <= self.back_limit:
                self.start_turn(now)
            elif now < self.until:
                linear = -self.back_speed
            else:
                self.start_turn(now)

        elif self.state == 'TURN':
            if now < self.until:
                angular = self.turn_speed * self.turn_dir
            else:
                self.state = 'MOVE'

        self.send(linear, angular)


def main(args=None):
    rclpy.init(args=args)
    node = ReverseObstacleAvoider()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.send()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
