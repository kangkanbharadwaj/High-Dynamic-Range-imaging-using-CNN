# Learning HDR Imaging from Synthetic data


## Objective

1.  Creation of a static dataset using blender
2.  Learn a model on the data
3.  Use the model to test real scenes

## Introduction

  *  LDR: Images of 0-255 pixel range, can be displayed on a standard device.
  *  HDR: Range of luminance that is equivalent to the one experienced by a human eye (upto 105).
  *  Tone-mapping: The scene with original irradiance(linear space) is mapped to pixel values of (0-255).

<br />

<p align="center">
<img style="border: 1px solid grey" src="images/1.png" alt="image segmentation vs semantic segmentation" width="400" height="300"/>
</ p>

<br />
<br />

## Motivation

  *  Image from DSLR camera cannot capture much details in very dark or very bright regions in one exposure setting.
  *  Surveillance or medical applications
  
<img style="border: 1px solid grey" src="images/2.png" alt="image segmentation vs semantic segmentation" width="800" height="500"/>
<br />
<br />
