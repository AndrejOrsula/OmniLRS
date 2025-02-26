## Environment Modes Configurations

Modes are what allows the user to use the same environment for different purposes. Say you want to use the lunalab to run a robotic task, you can use the ROS1 or ROS2 modes. But if you wanted to use this environment to generate a dataset for rock detection, you could use the SDG mode.

As of now we support 3 modes:
- ROS1: Noetic
- ROS2: Foxy, or Humble, also compatible with SpaceROS!
- SDG: Synthetic Data Generation

As ROS1 is no longer supported, and is no longer shipped with the latest ubuntu releases, it will be phased out with the next release. Having both ROS1 and ROS2 creates more work when adding new features, but also makes docker container generation more complicated.

Future release will include:
- SDG_SLAM: A mode to generate image sequence to evaluate SLAM & 3D reconstruction algorithms.
- SDG_LRO: A mode to generate LRO like images to test different set of algorithms.

### ROS1
This mode launches the simulation in ROS1 mode. This means that both the robots and the labs inside the simulation will be running using ROS1 nodes. There is no specific parameters for it.

Example:
```yaml
name: ROS1
```

<span style="color: red;">**Important**:</span>
- When loading a robot, make sure it's OmniGraphs (the recommended way to acquire sensors outputs for ROS) are ROS1 compatible. Not sure what they are? Check Nvidia's tutorials.
- Do not source ROS1 when running this simulation.

This mode can be selected like so:
```bash
python.sh mode=ROS1
```

### ROS2
This mode launches the simulation in ROS2 mode. This means that both the robots and the labs inside the simulation will be running using ROS2 nodes. There are 3 available parameters:

Arguments:
- name: (str), ROS2. It must be ROS2 nothing else.
- ROS_DOMAIN_ID: (int), A positive integer, denoting the ROS_DOMAIN_ID to use. Right now this is not functional.
- bridge_name: (str), either "foxy" or "humble". In the docker, the bridge must be humble. In a native installation, it can be either. It depends on which version of ROS2 is installed on your system.

Example:
```yaml
name: ROS2
ROS_DOMAIN_ID: 0
bridge_name: humble
```

<span style="color: red;">**Important**:</span>
- When loading a robot, make sure it's OmniGraphs (the recommended way to acquire sensors outputs for ROS) are ROS2 compatible. Not sure what they are? Check Nvidia's tutorials.
- Before running the simulation make sure ROS2 is sourced. If you are using the foxy bridge source foxy, if you are using the humble bridge, source humbe.
- If you don't see the ROS2 topics make sure you followed the procedure to change the DDS to FastDDS. See the isaac instalation steps [here](). If this is happening in docker as well please let us know.

This mode can be selected like so:
```bash
python.sh mode=ROS2
```

### SDG
This mode launches the simulation in synthetic data generation mode. It's meant to be used to create datasets for object detection or semantic segmentation. For that it builds on top of replicator's data-acquisition pipeline, the part of replicator that focuses on getting data from sensors. 

Arguments:
- `num_images`: `(int)`, The total number of image to capture.
- `prim_path`: `(str)`, The path of a prim containing the camera. The scene will be traversed from here and the prims matching `camera_name` will be used to acquire data. Note, `camera_name` is a list. This can be used to do stereo imaging to train a depth network for instance.
- `camera_name`: `(list(str))`, A list of camera name to acquire data from.
- `camera_resolution`: `(list((int, int)))`, A list of camera resolutions. Must be the same length as `camera_name`.
- `data_dir`: `(str)`, The folder in which the data will be saved. Note that the recorded data will not be stored directly in it. Instead the simulation will create a folder with a random name to enable multiple runs without changing the name.
- `annotator_list`: `(list(list(str)))`, A list of list of annotators name. Assigns a list of annotators to be collected by the cameras. Must be the same length as `camera_name`. To know more about available annotators see below.
- `image_format`: `(list(str))`, Tells the simulation in which format to save the rgb or ir images.
- `annot_format`: `(list(str))`, Tells the simulation in which format to save the "boundingboxes".
- `element_per_folder`: `(str)`, Number of image to be stored in each folder. Setting this to 1000 can help reduce I/Os.

Supported annotators:
- `RGB`: RGB image.
- `IR`: Gray scale RGB.
- `Depth`: Depth image which contains the raw distance. Saved as `npz`.
- `Pose`: The pose of the sensor in the global frame. Saved as a `csv`.
- `InstanceSemanticSegmentation`: 
- `SemanticSegmentation`:

> The simulation will automatically save the intrisics of your cameras when initialized.

If there is no camera in the scene by default you can also create one. To do so, you'll need to create a `camera_setting` object inside the mode config file.

Arguments:
- `camera_path`: `str`, The path at which the camera should be created.
- `focal_length`: `float`, The focal length of the camera. In cm.
- `horizontal_aperture`: `float`, The horizontal aperture of the camera. In cm.
- `vertical_aperture`: `float`, The vertical aperture. This is ignored, and the resolution is used instead.
- `fstop`: `float`, The fstop of the camera, set to 0.0 to disable.
- `focus_distance`: `float`, The focus distance in meters. Disabled if fstop is nulle.
- `clipping_range`: `((float, float))`, clipping range in meters.

Example:
```yaml
name: SDG
generation_settings:
  num_images: 1000
  prim_path: Camera
  camera_name: [camera_annotations]
  camera_resolution: [[640,480]]
  data_dir: data
  annotator_list: [["rgb", "semantic_segmentation", "instance_segmentation"]]
  image_format: [png]
  annot_format: [json]
  element_per_folder: 1000

camera_settings:
  camera_path: Camera/camera_annotations
  focal_length: 1.93
  horizontal_aperture: 3.6
  vertical_aperture: 2.7
  fstop: 0.0
  focus_distance: 10.0
  clipping_range: ${as_tuple:0.01, 1000000.0}
```
