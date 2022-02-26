import rclpy
from rclpy.node import Node
import numpy as np
from .ros_model import Classifier
from std_msgs.msg import String
from darknet_ros_msgs.msg import BoundingBoxes
from vision_msgs.msg import Classification2D
from sensor_msgs.msg import Image
import message_filters



class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.ros_model = Classifier()
        bbox = message_filters.Subscriber(self, BoundingBoxes, '/darknet_ros/bounding_boxes')
        image = message_filters.Subscriber(self, Image, '/darknet_ros/detection_image')
        synchronizer = message_filters.TimeSynchronizer([bbox, image], 10)
        # synchronizer = message_filters.ApproximateTimeSynchronizer([image, bbox], 5, 0.1)
        synchronizer.registerCallback(self.callback)

    def callback(self, image, bbox):
        images = np.asarray(image.data, dtype=np.uint8).reshape(image.height, image.width, -1)
        bboxes = bbox.bounding_boxes
        for bbox in bboxes:
            if "traffic light" == bbox.class_id:
                x1, y1, x2, y2 = bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax
                cropped_img = images[y1:y2, x1:x2, :]
                name, score = self.ros_model.prediction(cropped_img)
                print("traffic_light & score : {}  {}".format(name, score))



def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
