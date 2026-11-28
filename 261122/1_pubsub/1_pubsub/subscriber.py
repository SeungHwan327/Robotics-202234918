import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int64MultiArray


class Subscriber(Node):
    def __init__(self):
        super().__init__('subscriber')
        self.subscription_ = self.create_subscription(Int64MultiArray, '/coordinate_topic', self.callback, 10)
        self.subscription_

    def callback(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')

def main():
    rclpy.init()
    node = Subscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
