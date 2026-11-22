import rclpy
from rclpy.node import Node
from custom_interfaces.srv import MoveRobot
import math


class MoveRobotServer(Node):
    def __init__(self):
        super().__init__('srv_server')

        self.srv = self.create_service(MoveRobot, '/move_robots', self.srv_callback)
        self.get_logger().info('Srv Server Ready.')

    def srv_callback(self, request, response):
        pose = request.current_pose
        distance = request.distance
        result = response.result_pose
        result.x = pose.x + distance * math.cos(pose.theta)
        result.y = pose.y + distance * math.sin(pose.theta)
        result.theta = pose.theta
        response.success = True

        self.get_logger().info(
            f'Incoming request: x={pose.x}, y={pose.y}, theta={pose.theta}, distance={distance}'
        )
        self.get_logger().info(f'Sending back response: [{response.result_pose}, {response.success}]')

        return response


def main():
    rclpy.init()
    node = MoveRobotServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
