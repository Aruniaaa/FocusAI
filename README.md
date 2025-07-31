# FocusAI

A focus timer website equipped with an AI accountability system to keep you on track while studying, so your study sessions can't turn into scrolling sessions, and you can motivate yourself by seeing your progress visually on graphs!

---

## Features

### **AI-Powered Phone Detection**

* Real-time phone detection using computer vision
* Smart thresholding for reliable results
* Keras model trained using Teachable Machine

### **Focus Timer**

* Clean, distraction-free interface
* Visual countdown display
* Session completion tracking

### **Analytics Dashboard**

* Average phone confidence metrics
* High confidence detection count
* Real-time statistics display
* Performance tracking over time
* Visualizations via bar graphs, line charts, and more to better understand your focus behavior

### **To-Do List Page**

* Add, delete, and mark tasks as complete
* One-click cleanup of completed tasks
* Perfect for staying focused with a clear goal in mind

## Tech Stack

* **Frontend**: Streamlit
* **Backend**: Python
* **Computer Vision**: OpenCV, Keras model (Teachable Machine)
* **Deployment**: Local Server

## Prerequisites

Before running the application, ensure you have:

* **Python 3.10** *(older versions will not work; newer versions may cause compatibility issues)*
* **Virtual Environment** *(highly recommended)*
* **TensorFlow 2.13.0**
* **Keras 2.13.1** *(to match TensorFlow versioning)*
* **OpenCV, Streamlit, NumPy, etc.** *(full list in requirements.txt)*
* Webcam/Camera access
* Modern web browser (Chrome, Firefox, Safari)
* Internet connection for model downloads

## Setup Guide

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/FocusAI.git
   cd FocusAI
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Mac/Linux
   source venv/bin/activate
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run timer.py
   ```

## How It Works

1. The app accesses your webcam feed and the model analyzes each frame for phone presence
2. Each detection gets a confidence score (0.0 - 1.0)
3. App tracks when phones are detected during focus sessions by using a combination of average phone class' confidence and the number of times the phone class' confidence > 0.7
4. Real-time analytics show your focus patterns like total focus time over the week and how many times your phone has been detected, there is a separated page dedicated to show your stats
5. A "Falsely Detected?" button is included whenever the AI stops your timer. This gives the user a chance to continue their session in case the model made a mistake. This button is only active for 5 seconds after your timer has been stopped.
6. To Do lists in which you can add tasks, delete tasks, check them off, and clean up all the completed tasks—with just one click. Also in a separated page you can access and start using

## Key Metrics

* **Average Phone Confidence**: Mean confidence score of all detections
* **High Confidence Count**: Number of detections above threshold (>0.7)
* **Focus Time**: Total time spent in focus mode
* **Interruption Rate**: Frequency of phone-related distractions

## Customization

### Modify Thresholds

```python
# In app.py
high_conf_count = sum(conf > 0.7 for conf in st.session_state.recent_confidences)  # Adjust between 0.0 - 1.0, line 729
if avg_conf > 0.7 and high_conf_count >= 2: # also adjustable, line 748
```

### Want to Use a Different Model?

Replace the `.h5` model file with your own exported model trained using Teachable Machine or any Keras-compatible tool. Just ensure the input shape and class indexing match.

## Troubleshooting

* **ModuleNotFoundError**: Make sure you're inside the virtual environment before installing or running the app
* **TensorFlow Import Issues**: Confirm you’re using Python 3.10 with TensorFlow 2.13.0 and matching Keras version
* **Camera Access Issues**: Ensure your browser/OS grants permission to access the webcam

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
