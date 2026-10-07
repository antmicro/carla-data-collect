# CARLA data collector

A script designed to collect sensory data from [CARLA simulation](https://carla.org/).

## Prerequisites

Script requires CARLA Python API to work, alongside with `pygame` to handle client side of the application.
`pandas` package is used for handling CSV files and `pyyaml` for handling YAML based config files.
All other prerequisites are specified in the `pyproject.toml` file in dependencies section. 
In order to install all dependencies type:
``` bash
uv sync
```

## Quickstart

Download CARLA simulator from https://carla.readthedocs.io/en/0.9.16/download/ then unzip archive containing the simulator.
Then, go to the directory containing CARLA and type into the terminal:

``` bash
./CarlaUE4.sh &
```
then, in CARLA data collector directory, run 
``` bash
python main.py sim --cfg config.yml
```
A window should open up showing a view from simulation and data should be written into a `sample.csv` file.
In order to finish collecting data simply close the window.

## Synchronous mode

By default application and simulation runs asynchronously, it is possible to synchronize simulation update loop with application using `--sync` argument.
``` bash
python main.py sim --cfg config.yml --sync
```
In sync mode application update loop refresh rate is restricted to simulation frames per seconds.

## Sensor definition

It is possible to define a configuration file with sensor definition from which data will be collected.
Example configuration file:
``` yaml
sensors:
  - type: IMUSensor
    name: "imu_1"
    transform:
      translate: 
        x: 0
        y: 0
        z: 0
      rotation:
        pitch: 0
        yaw: 0
        roll: 0
    attributes:
      something: "example"
```
- `type` - it is the sensor type
- `name` - a name of the sensor
- `transform` - defines position and rotation of the sensor on a target vehicle, relative to vehicle's origin
- `attributes` - additional attributes for sensors

## Supported sensors

Data collector supports specified sensors:
- `GnssSensor` - represents GPS sensor and collects information about longitude and latitude
- `IMUSensor` - represents IMu sensor and collects information about acceleration, angular velocity and orientation
- `BrakeSensor` - collects information about vehicle's braking pedal state and handbrake state
- `SpeedSensor` - collects information about vehicle's linear speed value

## Output file format

Data are collected to CSV file, by default it is `sample.csv` file but it is possible to change output file path:

``` bash
python main.py sim --cfg config.yml --output recordings.csv
```

The first column in the file is always `timestamp`, it holds time stamps in which data has been collected.
Rest of the columns are sensory data with name:
```
<sensor_name>_<attribute_name>
```
- `sensor_name` - name of the sensor
- `attribute_name` - name of the sensor's attribute

for example column for `x` value of acceleration from imu sensor called `imu_1` will be:
```
imu_1_accel_x
```

## Dataset generation

Script has the option to convert collected data to a selected dataset format. 
The first necessary configuration must be specified in configuration file:
``` yaml
dataset:
  type: IMUAnomalyDataset
  attributes:
    output_path: imu_anomaly.csv 
    sep: ','
    sensor_imu_name: "imu_1"
    accel_threshold: 20.0
```
In which:
- `type` - defines target dataset type
- `attributes` - defines input attributes used by dataset, for example `IMUAnomalyDataset` dataset it is:
  - `output_path` - path to the file in which dataset is going to be saved
  - `sep` - CSV file separator character
  - `sensor_imu_name` - name of the sensor whose readings are going to be used to generate dataset
  - `accel_threshold` - acceleration value above which readings are treated as an anomaly

Then, to generate dataset type:
``` bash
python main.py dataset --cfg config.yml
```
By default, readings from `sample.csv` will be used but it is possible to use any input path:
``` bash
python main.py dataset --cfg config.yml --input recordings.csv
```

## Manual

Script has the option to display information about each implemented sensor or datasets.
In order to display information about `IMUAnomalyDataset` dataset type:
``` bash
python main.py man IMUAnomalyDataset
```