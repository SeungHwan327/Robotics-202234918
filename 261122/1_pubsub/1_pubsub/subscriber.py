import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64MultiArray


class Subscriber(Node):

    def __init__(self):
        super().__init__('subscriber')
        self.subscription_ = self.create_subscription(
            Int64MultiArray,
            '/coordinate_topic',
            self.callback,
            10,
        )

    def callback(self, msg):
        if len(msg.data) != 2:
            self.get_logger().warning(
                'Expected two coordinates: [x, y]'
            )
            return

        x, y = msg.data
        self.get_logger().info(f'Position: x={x}, y={y}')


def main(args=None):
    rclpy.init(args=args)
    node = Subscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
