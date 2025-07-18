# FocusAI
A focus timer website equipped with an AI accountability system to keep you on track while studying, so your study sessions can't turn into scrolling sessions, and you can motivate yourself by seeing your progress visually on graphs!
---

## Features

###  **AI-Powered Phone Detection**
- Real-time phone detection using computer vision
- Smart thresholding for reliable results
- Keras model trained using Teachable Machine

### **Focus Timer**
- Clean, distraction-free interface
- Visual countdown display
- Session completion tracking

### **Analytics Dashboard**
- Average phone confidence metrics
- High confidence detection count
- Real-time statistics display
- Performance tracking over time

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Computer Vision**: OpenCV, Keras model (Teachable Machine)
- **Deployment**: Local Server

## Prerequisites

Before running the application, ensure you have:

- Python 3.8 or higher
- Webcam/Camera access
- Modern web browser (Chrome, Firefox, Safari)
- Internet connection for model downloads


## Usage

 **To start a streamlit based application, you will need to run the following command**
   ```bash
   streamlit run timer.py
   ```

## How It Works

1. The app accesses your webcam feed and the model analyzes each frame for phone presence
3. Each detection gets a confidence score (0.0 - 1.0)
4. App tracks when phones are detected during focus sessions by using a combination of average phone class' confidence and the number of times the phone class' confidence > 0.7
5. Real-time analytics show your focus patterns like total focus time over the week and how many times your phone has been detected
6. A "Falsely Detected?" button is included whenever a the AI stops your timer, this gives the user a chance to continue their session just in case the model made a mistake, this button only works for 5 seconds
   after your timer has been stopped by the model.

## Key Metrics

- **Average Phone Confidence**: Mean confidence score of all detections
- **High Confidence Count**: Number of detections above threshold (>0.7)
- **Focus Time**: Total time spent in focus mode
- **Interruption Rate**: Frequency of phone-related distractions

## Customization

### Modify Thresholds
```python
# In timer.py
 high_conf_count = sum(conf > 0.7 for conf in st.session_state.recent_confidences)  # Adjust between 0.0 - 1.0
if avg_conf > 0.7 and high_conf_count >= 2: # also adjustable
```



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
