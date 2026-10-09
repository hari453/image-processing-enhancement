# Web-Based Image Processing & Enhancement

A responsive Flask web application for uploading images, applying enhancement controls, previewing the output, and downloading the processed result.

## Features

- Upload PNG, JPG, JPEG, or WEBP images
- Adjust brightness, contrast, sharpness, saturation, and blur
- Apply grayscale, invert, edge detection, and emboss operations
- Preview original and processed images side by side
- Download the processed image
- Responsive HTML, CSS, and JavaScript frontend

## Tech Stack

- Python
- Flask
- Pillow
- HTML
- CSS
- JavaScript

## Setup

```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Project Structure

```text
image-processing-enhancement/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
├── uploads/
└── processed/
```
