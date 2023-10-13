YOLOv5 README
This README provides a step-by-step guide to setting up and using YOLOv5 for object detection tasks using custom data. YOLOv5 is a fast and efficient object detection model developed by Ultralytics. In this guide, we'll walk you through the process of cloning the YOLOv5 repository, creating a custom dataset configuration file, creating a Conda environment, training the model, and evaluating its performance.

Pretrained Data:
Step 1: Open the terminal in the vscode to clone the YOLOv5 repository from GitHub (https://github.com/ultralytics/yolov5) and install the required dependencies. Type the below commands in the terminal.

> git clone https://github.com/ultralytics/yolov5 
> cd yolov5'

Step 2: This YOLOv5 will have pre trained data(coco128.yaml) file which we will use to detect the objects with the command 

> python detect.py --source 0


Customized Data:
Table of Contents
Installation
Creating Custom Dataset Configuration
Setting Up Conda Environment
Training the Model
Evaluating the Model
Installation


1. Open Visual Studio Code (VSCode) and create a new workspace. Add your training data folder (traindata1) to the workspace.
2. Open the integrated terminal in VSCode and clone the YOLOv5 repository from GitHub using the following commands:

> git clone https://github.com/ultralytics/yolov5

> cd yolov5

Creating Custom Dataset Configuration
1. In the yolov5/data folder, create a copy of the coco128.yaml file and rename it as custom_data.yaml.
2. Open custom_data.yaml and update it with the relative paths to your training and validation image folders, the number of classes (nc), and the class names.
3. Select the YOLOv5 model configuration that suits your requirements. In this guide, we'll use YOLOv5s for its efficiency.
Setting Up Conda Environment
1. Create a Conda environment named yolov5 with Python 3.8 using the following command:

> conda create --name yolov5 python=3.8

Activate the created Conda environment:

> conda activate yolov5

2. Install the required dependencies from the requirements.txt file:

> pip install -r requirements.txt

Note: If you encounter any errors, consider using Anaconda Navigator to open VSCode and retry from step 2.


Training the Model
1. To train the model using the custom dataset configuration, run the following command:

> python train.py --img 640 --batch 2 --epochs 100 --data custom_data.yaml --weights yolov5s.pt --cache

Adjust the parameters (img, batch, epochs, etc.) as needed for your training scenario.
2. The training process will generate a best.pt file which represents the trained model.


Evaluating the Model
1. After training, you can evaluate the model's performance using the detect.py script.
2. Create a separate folder named test and include it in the same workspace.
3. To use the trained model to detect objects, run the following command for webcam input:

> python detect.py --weights path/to/best.pt --source 0

If you want to detect objects in images from the test folder, use:

> python detect.py --weights path/to/best.pt --source path/to/test

The detection results will be displayed or saved based on the specified parameters.

This README provides a comprehensive guide to setting up and utilizing YOLOv5 for object detection tasks using custom data. Make sure to tailor the commands and configurations according to your specific dataset and requirements. For more advanced usage and options, refer to the official YOLOv5 documentation: https://github.com/ultralytics/yolov5.