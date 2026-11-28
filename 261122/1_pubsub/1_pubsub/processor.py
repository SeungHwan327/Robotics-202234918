import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Int64MultiArray


class Processor(Node):
    def __init__(self):
        super().__init__('processor')
        x=0, y=0
        self.pos = [x,y]
        self.step = 1
        self.subscriber_ = self.create_subscriber(String, '/demo_topic', self.callback, 10)
        self.subscriber_
        

    def publish_message(self):
        if msg.data == 'w': 
            pos = [x,y+step]
        elif msg.data == 'a': 
            pos = [x-step, y]
        elif msg.data == 's': 
            pos = [x,y-step]
        elif msg.data == 'd':
            pos = [x+step, y]

        
        

        self.publisher_ = self.create_publisher(Int64MultiArray, '/coordinate_topic', 10)
    
        
    def callback(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')

def main():
    rclpy.init()
    node = Processor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
