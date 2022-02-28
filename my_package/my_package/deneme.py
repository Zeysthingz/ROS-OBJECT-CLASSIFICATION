import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from darknet_ros_msgs.msg import BoundingBoxes
from sensor_msgs.msg import Image
import message_filters
from vision_msgs.msg import Classification2D
from vision_msgs.msg import ObjectHypothesis
import numpy as np
from .ros_model import Classifier


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.model = Classifier()
        bbox_sub = message_filters.Subscriber(self, BoundingBoxes, '/darknet_ros/bounding_boxes')
        self.corrected_image = self.create_subscription(Image, '/image_raw/camera0_sec/uncompressed',
                                                        self.listener_callback, 10)
        self.published_image = self.create_publisher(Image, '/edited_image_time', 10)
        image_sub = message_filters.Subscriber(self, Image, '/edited_image_time')

        # Maximum queue size of 10.
        synchronizer = message_filters.ApproximateTimeSynchronizer([image_sub, bbox_sub], queue=10, slop=0.5)
        synchronizer.registerCallback(self.callback)
        self.published_image = self.create_publisher(Classification2D, '/results', 10)

    def listener_callback(self, image_data):
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        image_data.header = header
        self.  self.published_image.publish(image_data)

    def callback(self, image_data, bbox_data):
        # 3.boyutu senin için konfigure ediyor içinde
        image = np.asarray(image_data.data, dtype=np.uint8).reshape(image_data.height, image_data.width, -1)
        bboxes = bbox_data.bounding_boxes

        for bbox in bboxes:
            if ("traffic light" == bbox.class_id):
                x1, y1, x2, y2 = bbox.xmin, bbox.ymin, bbox.xmax, bbox.ymax
                cropped_img = image[y1:y2, x1:x2, :]
                name, score = self.model.prediction(cropped_img)
                print("class_name & score : {}  {}".format(name, score))
                ## This result does not contain any position information. It is designed for
                # classifiers, which simply provide class probabilities given a source image.
                published_message = Classification2D()
                # takes name and score information
                object_message = ObjectHypothesis()
                object_message.id = name
                object_message.score = score
                published_message.results = [object_message]
                published_message.source_img = image_data
                self.published_image.publish(published_message)


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
