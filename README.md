# DevOps Certification Exam - Dash Application

This project is an interactive quiz web application built with [Dash](https://dash.plotly.com/) and [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/).  
It is designed to simulate a DevOps certification exam with a beautiful UI, timer, progress tracking, and submission feature.

---

## Features

- Load and parse multiple-choice questions from a CSV file.
- Clean and modern UI with a premium "Lux" Bootstrap theme.
- Question timer with countdown display.
- Progress bar showing how far the user is into the exam.
- Navigation buttons: **Previous**, **Next**, and **Submit Exam**.
- Option selection with hover and selection effects.
- Responsive layout and mobile-friendly.
- Shows final results after exam submission.

---
## structure 
CSV Format
The questions are loaded from a CSV file located in the domainQuestions/ folder.
Each row should have at least two columns:

question: A text block with the question and options (formatted with newlines \n).
answer: A string indicating the correct option(s), like "A", "BC", "D".
Example structure inside domainQuestions CSV:

## dependancies :
pip install dash dash-bootstrap-components pandas

## How to run :
python dash_app.py

# helper files :

## 1. capture_images.py
Video Frame Capture Tool
This script captures frames from a video file at specific times based on a starting minute, starting second, and a capture interval in minutes.

Dependencies:
- OpenCV (cv2)
- os (standard library)

Usage:
- Adjust the `video_file` and `output_dir` paths.
- Run the script to extract frames at the defined intervals.

## 2. image_extractor.py
# Image Question Extractor and Classifier

This file automates the extraction of questions, multiple-choice options, answers, and domain classifications from images using AWS Bedrock and Anthropic models.

---

## Features
- Uploads and processes images containing MCQ (Multiple Choice Questions).
- Sends images and prompts to a Bedrock model for inference.
- Extracts and structures the response into JSON.
- Matches each question to one of six pre-defined domains.
- Saves the processed results into a CSV file.

---

## Requirements
- Python 3.8+
- boto3
- Pillow (PIL)

Install required packages:
```bash

### setup 
pip install boto3 pillow

Setup
AWS Credentials:
Set your AWS credentials via environment variables or provide them directly in the script:
Set the model_inference_Id with the Bedrock model you want to use.

How it Works
  Converts an image to a base64 format.
  Send Request:
  Sends the image along with a detailed prompt to Bedrock for processing.
  Parse Response:
  Extracts structured JSON from the model's text response.
  JSON structure expected:
  Save to CSV:
  Saves all valid extracted data to a CSV file.
