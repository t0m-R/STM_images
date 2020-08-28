# Jupyter notebooks

These notebooks provide the code relevant to the analysis on the STM images dataset from the initial exploration till the analysis of extracted features by transfer learning techniques. There are four notebooks:


- `data_visualization_functions.ipynb`, functions to interact with STM images dataFrame, visualize and save plots with different metadata, number of images and preprocessing steps

- `make_training_set_multicore.ipynb`, show the process of creating the training dataset of 224x224 images by using multiprocessing on the STM metadata dataFrame with 24 cores

- `features_extraction_distance_analysis.ipynb`, show the STM images features extracted from a Resnet50 pretrained on ImageNet, the analysis of these features using distance metrics and intrinsic dimension

- `cluster_visualization.ipynb`, contains code for visualize and save plots obtained by running Advanced Density Peaks (DPA ) on STM images features
