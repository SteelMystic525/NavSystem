# NavSystem — ArUco Marker Navigation for TurtleBot3

A ROS 2 package that enables a TurtleBot3 to localise itself relative to ArUco fiducial markers using a depth camera.  The system detects **DICT_6X6_250** markers, estimates their 6-DoF pose, and publishes world-frame coordinates via TF2 transforms.  A companion Gazebo model lets you test the full pipeline in simulation before deploying on hardware.

---

## Features

- **Real-time marker detection** at up to 10 Hz using OpenCV's ArUco module
- **Full 6-DoF pose estimation** (position + orientation) per detected marker
- **TF2 integration** — automatically transforms marker coordinates from the camera frame to the world frame
- **Configurable marker size** via a ROS 2 parameter (no rebuild required)
- **Gazebo simulation model** — a 20 × 20 cm textured ArUco marker ready to drop into any world file
- **Hexagonal search pattern** support for systematic area coverage

---

## Architecture

```
/camera/image_raw ──────┐
                         ▼
/camera/camera_info ──► ArucoDetectionNode ──► /aruco_marker_coordinates
                         │
                    TF2 lookup
                  (world ← camera_frame)
```

| Topic | Direction | Type | Description |
|---|---|---|---|
| `/camera/image_raw` | Sub | `sensor_msgs/Image` | Raw colour frames |
| `/camera/camera_info` | Sub | `sensor_msgs/CameraInfo` | Camera intrinsics |
| `/aruco_marker_coordinates` | Pub | `std_msgs/String` | World-frame marker pose |

---

## Prerequisites

| Dependency | Version |
|---|---|
| ROS 2 | Humble or later |
| Python | 3.10+ |
| OpenCV | 4.x (with `contrib` for ArUco) |
| `cv_bridge` | ≥ 3.x |
| `tf2_ros` | Comes with `ros-humble-tf2-ros` |
| `scipy` | ≥ 1.9 |

Install system dependencies:

```bash
sudo apt update
sudo apt install -y \
    ros-humble-cv-bridge \
    ros-humble-tf2-ros \
    python3-opencv \
    python3-scipy
```

---

## Installation

```bash
# 1. Clone into your workspace
cd ~/ros2_ws/src
git clone https://github.com/<your-org>/NavSystem.git

# 2. Install Python dependencies
pip install opencv-contrib-python scipy

# 3. Build
cd ~/ros2_ws
colcon build --packages-select aruco_marker_detection
source install/setup.bash
```

---

## Usage

### Running the detection node

```bash
ros2 run aruco_marker_detection aruco_detection_node
```

### Adjusting marker size at runtime

```bash
ros2 param set /aruco_detection_node marker_size 0.10   # 10 cm marker
```

### Gazebo simulation

Drop the bundled ArUco marker model into your world:

```xml
<!-- Inside your .world file -->
<include>
  <uri>model://aruco_marker</uri>
  <pose>2.0 0.0 0.1 0 0 0</pose>
</include>
```

Add `src/turtlebot3_gazebo/models` to your `GAZEBO_MODEL_PATH`:

```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$(ros2 pkg prefix aruco_marker_detection)/../turtlebot3_gazebo/models
```

---

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `marker_size` | `double` | `0.05` | Physical side-length of the ArUco marker (metres) |

---

## Package Structure

```
NavSystem/
├── src/
│   ├── aruco_marker_detection/          # ROS 2 Python package
│   │   ├── aruco_marker_detection/
│   │   │   ├── __init__.py
│   │   │   └── aruco_detection_node.py  # Main detection node
│   │   ├── test/                        # Linting & style tests
│   │   ├── package.xml
│   │   ├── setup.cfg
│   │   └── setup.py
│   └── turtlebot3_gazebo/
│       └── models/
│           └── aruco_marker/            # Gazebo model
│               ├── model.sdf
│               └── materials/
│                   ├── scripts/
│                   └── textures/
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## Running Tests

```bash
cd ~/ros2_ws
colcon test --packages-select aruco_marker_detection
colcon test-result --verbose
```

The test suite checks PEP 257 docstrings, Flake8 style, and copyright headers.

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

---

## License

This project is licensed under the Apache 2.0 License — see [LICENSE](LICENSE) for details.
