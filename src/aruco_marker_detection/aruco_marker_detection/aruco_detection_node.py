"""ROS 2 node for ArUco marker detection and world-frame coordinate publishing.

Detects ArUco markers (DICT_6X6_250) via a depth camera, estimates 6-DoF pose
for each detected marker, and publishes world-frame coordinates using TF2 transforms.

Topics
------
Subscribed:
  /camera/image_raw   (sensor_msgs/Image)
  /camera/camera_info (sensor_msgs/CameraInfo)

Published:
  /aruco_marker_coordinates (std_msgs/String)

Parameters
----------
  marker_size (float, default 0.05)  – Physical side length of the marker in metres.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from std_msgs.msg import String
import cv2
from cv_bridge import CvBridge
import numpy as np
import tf2_ros
from scipy.spatial.transform import Rotation as R


class ArucoDetectionNode(Node):
    """Detects ArUco markers and publishes their world-frame coordinates."""

    def __init__(self):
        """Initialise subscriptions, publisher, TF2 listener, and processing timer."""
        super().__init__('aruco_detection_node')

        self.bridge = CvBridge()
        self.camera_matrix = None
        self.dist_coeffs = None
        self.latest_image = None

        # TF2 listener
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Subscriptions
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10,
        )
        self.camera_info_sub = self.create_subscription(
            CameraInfo,
            '/camera/camera_info',
            self.camera_info_callback,
            10,
        )

        # Publisher
        self.marker_pub = self.create_publisher(String, '/aruco_marker_coordinates', 10)

        # Parameters
        self.declare_parameter('marker_size', 0.05)

        # Processing timer – limits detection to 10 Hz to avoid CPU saturation
        self.processing_timer = self.create_timer(0.1, self.process_images)

        self.get_logger().info('ArUco Detection Node initialised.')

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def camera_info_callback(self, msg: CameraInfo) -> None:
        """Initialise the camera intrinsic matrix once on first receipt."""
        if self.camera_matrix is None:
            self.camera_matrix = np.array(msg.k).reshape((3, 3))
            self.dist_coeffs = np.array(msg.d)
            self.get_logger().info('Camera intrinsics received.')

    def image_callback(self, msg: Image) -> None:
        """Buffer the most recent image for processing."""
        self.latest_image = msg

    # ------------------------------------------------------------------
    # Core processing
    # ------------------------------------------------------------------

    def process_images(self) -> None:
        """Detect markers in the buffered image and publish world coordinates."""
        if self.latest_image is None:
            return

        if self.camera_matrix is None:
            self.get_logger().warn('Camera info not yet received – skipping frame.')
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(self.latest_image, 'bgr8')
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
            parameters = cv2.aruco.DetectorParameters()

            corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            if ids is None:
                return

            cv2.aruco.drawDetectedMarkers(cv_image, corners, ids)

            marker_size = self.get_parameter('marker_size').get_parameter_value().double_value
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, marker_size, self.camera_matrix, self.dist_coeffs
            )

            for i, marker_id in enumerate(ids):
                tvec = tvecs[i][0]
                rvec = rvecs[i][0]
                distance = float(np.linalg.norm(tvec))

                self.get_logger().info(
                    f'Marker {marker_id[0]} | xyz={tvec} | dist={distance:.3f} m'
                )

                self._publish_world_coords(marker_id[0], tvec)

                cv2.drawFrameAxes(
                    cv_image, self.camera_matrix, self.dist_coeffs, rvec, tvec, 0.1
                )

            cv2.imshow('ArUco Detection', cv_image)
            cv2.waitKey(1)

        except Exception as exc:  # pylint: disable=broad-except
            self.get_logger().error(f'Error processing image: {exc}')

    def _publish_world_coords(self, marker_id: int, tvec: np.ndarray) -> None:
        """Look up the camera→world transform and publish the marker world position."""
        try:
            transform = self.tf_buffer.lookup_transform(
                'world',
                'camera_frame',
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=2.0),
            )
            world_pos = self._transform_to_world(tvec, transform)
            msg = String(data=f'Marker ID: {marker_id}, World Position: {world_pos}')
            self.marker_pub.publish(msg)
            self.get_logger().info(str(msg.data))

        except tf2_ros.TransformException as exc:
            self.get_logger().warn(f'TF transform failed: {exc}')

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _transform_to_world(tvec: np.ndarray, transform) -> np.ndarray:
        """
        Convert a camera-frame translation vector to the world frame.

        Parameters
        ----------
        tvec:
            3-element translation vector in the camera frame.
        transform:
            geometry_msgs/TransformStamped from TF2.

        Returns
        -------
        np.ndarray
            3-element translation vector in the world frame.
        """
        t = transform.transform.translation
        q = transform.transform.rotation
        translation = np.array([t.x, t.y, t.z])
        rotation = R.from_quat([q.x, q.y, q.z, q.w]).as_matrix()
        return rotation @ tvec + translation

    def destroy_node(self) -> None:
        """Close OpenCV windows and cleanly shut down the node."""
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None) -> None:
    """Initialise rclpy, spin the detection node, and shut down cleanly."""
    rclpy.init(args=args)
    node = ArucoDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down ArUco Detection Node.')
    finally:
        node.destroy_node()
        rclpy.shutdown()
