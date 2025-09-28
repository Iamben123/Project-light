# Project Light (Team Lighthouse)

## AI-Powered Smart Glasses for Enhanced Awareness


---

### 💡 Project Overview

Project Light is an innovative, affordable AI-powered smart glass system designed to empower individuals with visual and hearing impairments. Our solution leverages real-time computer vision and audio analysis to provide critical environmental information and safety alerts, fostering greater independence and awareness.

This project was conceived and developed from scratch, evolving into a functional prototype that demonstrates the power of AI to create impactful assistive technology.

---

### ✨ Key Features

1.  **AI-Assisted Text Reader (OCR):**
    * **Intelligent Targeting System:** Our unique system actively analyzes the camera feed for clarity and stability, guiding the user to achieve optimal shots before initiating OCR. This drastically improves reading accuracy in dynamic, real-world conditions.
    * Reads text from signs, documents, menus, and more, providing instant audio feedback.
    * *Technology:* OpenCV, EasyOCR.

2.  **Environmental Sound Awareness:**
    * **Proactive Safety Alerts:** Continuously monitors the environment for over 500 types of sounds. Provides instant, on-screen alerts for critical sounds like sirens, car horns, fire alarms, and even general sounds like dogs barking.
    * *Technology:* TensorFlow (YAMNet model), PyAudio.

3.  **Offline Functionality:**
    * All core AI processing for OCR and sound detection runs directly on the device (Raspberry Pi), ensuring reliability and privacy without requiring an internet connection.

---

### 🚀 Current Prototype Status (Stage 1 Submission)

We currently have a **fully functional software prototype** demonstrating both the AI-Assisted Text Reader and Environmental Sound Awareness features. This prototype is developed for and runs efficiently on a Raspberry Pi-powered setup.

* **Development Platform:** Python 3.11, Tkinter (UI), Multi-threaded architecture.
* **Hardware (Development):** Raspberry Pi (for core logic), Pi Camera, USB Microphone.
* **Demo Mode:** Features a split-screen UI for live demonstration, showing raw camera input and the smart glass output simultaneously.

---

### 🛣️ Roadmap & Future Scope

Our vision for Project Light is continuous innovation:

* **Short-Term (Next 3-6 Months):**
    * **Voice Control:** Integrate offline speech-to-text (Vosk) for hands-free command input.
    * **Haptic Feedback:** Implement vibration alerts for discreet notifications.
    * **Wearable Form Factor:** Transition software to a compact Raspberry Pi Compute Module integrated into smart glasses.
* **Mid-Term (Next 6-12 Months):**
    * **Object & Obstacle Detection:** Integrate YOLO for real-time identification of objects and hazards.
    * **Indian Sign Language (ISL) Recognition:** Begin training custom AI models for ISL interpretation.
* **Long-Term Vision:**
    * Refined, sleek, and discreet hardware design.
    * Open-source ecosystem for community-driven development.
    * Pilot programs with NGOs for widespread deployment and impact.

---

### 🛠️ Technology Stack

* **Hardware (Target):** Raspberry Pi Compute Module 4, Mini Camera Module, Mini Microphone Module, Integrated Eyeglass Frame, LiPo Battery.
* **Core Software:** Python 3.11, Tkinter (GUI), OpenCV (Computer Vision), PyAudio (Audio Processing).
* **AI Frameworks:** EasyOCR (Text Recognition), TensorFlow (Sound Classification - YAMNet).

---

### 👨‍💻 Getting Started (For Contributors/Reviewers)


    ```
1.  **Set up a Python Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Install Tesseract OCR (if not already installed, for `vision_services.py` if using Tesseract):**
    * Download from: [https://tesseract-ocr.github.io/tessdoc/Installation.html](https://tesseract-ocr.github.io/tessdoc/Installation.html)
    * Ensure `pytesseract.pytesseract.tesseract_cmd` in `vision_services.py` points to your `tesseract.exe` path.
4.  **Run the application:**
    ```bash
    python main.py
    ```

---

### 👥 Team Lighthouse

* **Benjamin:** 

---

### 📄 License

This project is licensed under MIT License. See the `LICENSE` file for details.

---
