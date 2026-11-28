import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Publisher(Node):

    def __init__(self):
        super().__init__('publisher')
        self.publisher_ = self.create_publisher(
            String, '/command_topic', 10
        )

    def send_command(self, command):
        msg = String()
        msg.data = command
        self.publisher_.publish(msg)

        self.get_logger().info(f'Publishing: {command}')


def main(args=None):
    rclpy.init(args=args)
    node = Publisher()

    try:
        node.get_logger().info('Waiting for processor...')

        while rclpy.ok():
            if node.publisher_.get_subscription_count() > 0:
                break
            rclpy.spin_once(node, timeout_sec=0.1)

        while rclpy.ok():
            command = input(
                'W/A/S/D input and Enter, Terminate Q: '
            ).strip().lower()

            if command == 'q':
                break

            if command not in ('w', 'a', 's', 'd'):
                print('input W, A, S, D')
                continue

            node.send_command(command)
            rclpy.spin_once(node, timeout_sec=0.0)

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
