# Micro-Mobility Device Tracker

## Project Introduction

Micro-mobility device theft is a prevalent issue on the UC San Diego campus, where limited tracking and monitoring make it challenging to prevent or resolve stolen e-scooters and bikes. Our project aims to develop an intelligent anti-theft system that integrates motion detection, GPS tracking, facial recognition, and real-time alerts to enhance the security of personal transportation devices.

## Demo
[Demo Video](https://youtu.be/tMmxK_fiTrU?si=Ada6vppus1BcTzrK)

## Firmware
The firmware of our device is in this repository
[Firmware Repository](https://github.com/Serenity0204/Anti-Theft-Device-Firmware)

## Project Detail
For more detailed information, please visit our [Proposed Solution Page](https://serenity0204.github.io/ece196-problem-page-website/proposed-solution.html).

## Enclosure
Access the 3D model of our device enclosure here:
[Onshape Workspace Link](https://cad.onshape.com/documents/6a18173cd1a9dbaad74988c4/w/51ca01253f3a29c57be8f8d5/e/47abb33ad29e609b7f89fbcf?renderMode=0&uiState=683bdfefe829063e4b120cb7)

## Quick Start

To set up and run the project, follow the steps:
1. Create virtual environment 
2. run the following commands
```
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Features

* **Motion Detection**: Utilizes an accelerometer and gyroscope to detect unauthorized movement.
* **GPS Tracking**: Provides real-time location updates of the device.
* **Facial Recognition**: Employs a camera module and machine learning to verify the identity of the user.
* **Audible Alarm**: Triggers a buzzer when unauthorized access is detected.
* **Web Interface**: Allows users to monitor and control the system remotely.

## Technological Components

* **Microcontroller**: ESP32 with built-in Wi-Fi for communication.
* **Sensors**: Accelerometer and gyroscope for motion detection.
* **GPS Module**: For tracking the device's location.
* **Camera Module**: ESP32-CAM for capturing images.
* **Machine Learning**: ResNet-34 CNN for facial recognition, generating 128-dimensional embeddings.
* **Web Server**: Cloud-hosted interface interacting with the ESP32 microcontroller.
* **Alarm Module**: Buzzer to alert nearby individuals of theft attempts.

## System Workflow

1. The accelerometer detects motion when the device is moved.
2. The system captures an image using the camera module.
3. Facial recognition verifies if the user is authorized.
4. If unauthorized, the system triggers the alarm and sends an alert via the web interface.
5. The GPS module provides real-time location tracking of the device.

## Contributions

* **PCB Design**: Linfeng Zhang, Yu-Heng Lin
* **Enclosure Design**: Linfeng Zhang
* **Firmware and System Integration**: Yu-Heng Lin, Linfeng Zhang
* **Computer Vision Model**: Sihan Wang
* **Django Website Building**: Sihan Wang, Yu-Heng Lin
* **Proposed Solution website**: Sihan Wang


