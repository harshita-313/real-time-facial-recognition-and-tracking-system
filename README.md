# Real-Time Facial Recognition & Tracking System

## Overview

This project is a real-time facial recognition and tracking system built
using Python. It detects and recognizes employees from live camera
streams and logs their entry and exit times in a database.

The system can be used in office environments to track employee presence
and calculate working hours based on IN and OUT timestamps.

It uses AI-based facial recognition (ArcFace model via DeepFace) to
identify individuals and automatically log events without manual input.

------------------------------------------------------------------------

## Features

-   Real-time face detection and recognition
-   Multi-camera support (IN / OUT cameras)
-   RTSP stream and webcam compatibility
-   Automatic entry and exit logging
-   MySQL database integration
-   Absence timeout handling (prevents duplicate logs)
-   Embedding averaging for better recognition accuracy

------------------------------------------------------------------------

## How It Works

### 1. Employee Registration (register.py)

-   Reads employee images from the `employees/` folder
-   Generates facial embeddings using DeepFace (ArcFace model)
-   Averages embeddings for better accuracy
-   Stores employee name and embedding in MySQL database

This step is done once before starting live tracking.

------------------------------------------------------------------------

### 2. Real-Time Tracking (live_stream.py)

-   Connects to IN and OUT cameras using RTSP
-   Detects faces in live frames
-   Converts faces to embeddings
-   Compares with stored employee embeddings
-   If similarity is above threshold:
    -   Logs entry or exit event
    -   Stores timestamp in attendance_logs table

------------------------------------------------------------------------

### 3. Database Handling (`mysql_db.py`)

- Manages database connection
- Inserts employees
- Logs attendance events
- Fetches stored employee embeddings

------------------------------------------------------------------------

## Tech Stack

-   Python
-   DeepFace (ArcFace model)
-   OpenCV
-   NumPy
-   MySQL
-   dotenv (environment variables)
-   Multi-threading (for camera streaming)

------------------------------------------------------------------------

## Database Structure

### employees table

  Column      Description
  ----------- --------------------------------
  id          Employee ID
  name        Employee Name
  embedding   Facial embedding (JSON format)
  created_at  Record creation timestamp

### attendance_logs table

  Column        Description
  ------------- --------------------
  id            Log ID
  employee_id   Employee reference
  camera_name   IN / OUT camera
  direction     IN or OUT
  timestamp     Date & Time

------------------------------------------------------------------------

## Setup Instructions

### 1. Clone the repository

git clone `<your-repo-url>`{=html} cd `<repo-folder>`{=html}

### 2. Create virtual environment

python -m venv venv venv`\Scripts`{=tex}`\activate`{=tex}

### 3. Install dependencies

pip install -r requirements.txt

------------------------------------------------------------------------

## Environment Variables

Create a `.env` file in the root folder:

RTSP_IN=0 RTSP_OUT=rtsp://your_camera_stream

-   Use `0` for webcam
-   Use RTSP URL for IP camera

------------------------------------------------------------------------

## How to Run

### Step 1: Register Employees

Place employee images inside:

employees/ 
  ├── Employee1/
  ├── Employee2/

Then run:

python register.py

------------------------------------------------------------------------

### Step 2: Start Live Tracking

python live_stream.py

Press `q` to stop the system.

------------------------------------------------------------------------

## Office Use Case

This system can be used in office environments to:

-   Automatically detect when employees enter and leave
-   Store accurate timestamps
-   Later calculate working hours
-   Reduce manual attendance marking
-   Improve monitoring accuracy

------------------------------------------------------------------------

## Future Improvements

-   Work hours calculation
-   Dashboard interface
-   REST API integration
-   Docker deployment
-   Cloud database support
-   Role-based access control

------------------------------------------------------------------------

