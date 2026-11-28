import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64MultiArray, String


class Processor(Node):
    
    def __init__(self):
        super().__init__('processor')

        self.pos = [0, 0]
        self.step = 1

        self.publisher_ = self.create_publisher(
            Int64MultiArray, '/coordinate_topic', 10
        )
        self.subscription_ = self.create_subscription(
            String, '/command_topic', self.callback, 10
        )

    def callback(self, msg):
        command = msg.data.strip().lower()

        if command == 'w':
            self.pos[1] += self.step
        elif command == 'a':
            self.pos[0] -= self.step
        elif command == 's':
            self.pos[1] -= self.step
        elif command == 'd':
            self.pos[0] += self.step
        else:
            self.get_logger().warning(
                f'Invalid command: {msg.data!r}'
            )
            return

        result = Int64MultiArray()
        result.data = self.pos.copy()
        self.publisher_.publish(result)

        self.get_logger().info(
            f'Command: {command}, position: {self.pos}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = Processor()

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
