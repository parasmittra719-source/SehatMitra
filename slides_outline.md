# Pitch Slides Outline

## Slide 1: Title Slide
*   **Headline:** SehatMitra: An Offline AI Health Assistant
*   **Sub-headline:** Health information for every Indian, everywhere.
*   **Speaker Notes:** Introduce yourself and state the core mission: bridging the healthcare information gap using advanced, on-device AI.

## Slide 2: The Problem
*   **Bullets:**
    *   70%+ of Indians lack reliable internet access.
    *   Rural health clinics are often scarce and understaffed.
    *   Health literacy in regional languages is low.
*   **Visual:** A powerful image or infographic showing the digital divide and healthcare access disparity in India.
*   **Speaker Notes:** Tell the story of a rural user who needs immediate health advice but faces connectivity and language barriers.

## Slide 3: The Solution - SehatMitra
*   **Bullets:**
    *   **Offline-First:** Runs entirely on-device, no internet required.
    *   **Powered by Gemma 4:** Leverages advanced AI for multilingual understanding (Hindi/English).
    *   **Grounded Answers:** Uses local RAG (Retrieval-Augmented Generation) against vetted health guidelines.
*   **Visual:** Mockups of the SehatMitra mobile/web interface.
*   **Speaker Notes:** Explain how SehatMitra solves the problem by putting a knowledgeable, offline assistant in their pocket.

## Slide 4: Architecture & Technology
*   **Bullets:**
    *   Frontend: Responsive, lightweight HTML/JS/CSS (Glassmorphism UI).
    *   Backend: Python Flask API.
    *   AI Engine: Gemma 4 (8B-it) via Hugging Face Transformers.
    *   Knowledge Base: Local vector DB for retrieving WHO/Gov guidelines.
*   **Visual:** A clear, simple Mermaid architecture diagram showing the data flow.
*   **Speaker Notes:** Highlight the technical depth. Emphasize that Gemma 4 is doing the heavy lifting locally and that RAG prevents hallucination.

## Slide 5: Demo Snapshot
*   **Bullets:**
    *   Seamless Hindi Q&A.
    *   Instant context retrieval.
    *   Clear, actionable advice.
*   **Visual:** A GIF or side-by-side screenshots showing a query ("मुझे बुखार है") and the AI's response.
*   **Speaker Notes:** Walk through what happens during a typical interaction, reinforcing the speed and reliability of the system.

## Slide 6: Impact & Future Roadmap
*   **Bullets:**
    *   **Current Impact:** Built in 16 hours; proves viable offline AI healthcare.
    *   **Next Steps:**
        *   Integrate Voice I/O (Speech-to-Text).
        *   Expand local dialect support.
        *   Implement Image Input for visual symptoms (rashes, etc.).
*   **Visual:** Icons representing voice, camera, and multiple languages.
*   **Speaker Notes:** Conclude with the vision for the future. SehatMitra isn't just a hackathon project; it's a scalable solution for global health equality.

## Slide 7: Thank You
*   **Bullets:**
    *   Link to Kaggle Submission
    *   Link to GitHub Repo
    *   Contact Information
*   **Speaker Notes:** Thank the judges and invite them to review the code and try the live demo.
