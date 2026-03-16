# 🔄 ReLoop — Circular Economy & Industrial Symbiosis Platform

> **Revolutionizing Industrial Waste Management through AI-Powered Matchmaking and End-to-End Encrypted Negotiations.**

ReLoop is a state-of-the-art platform designed to bridge the gap between waste generators and recyclers. By treating one industry's waste as another's raw material, ReLoop facilitates **Industrial Symbiosis**—reducing landfill waste, cutting carbon emissions, and creating new economic value from scrap.

---

## 🌍 Societal & Environmental Impact

ReLoop isn't just a marketplace; it's a tool for global sustainability.

### 🍃 Environmental Conservation
- **Waste Diversion**: Directs hundreds of tons of industrial scrap away from landfills and into production cycles.
- **Carbon Reduction**: By localized sourcing of recycled materials, ReLoop significantly reduces the CO2 footprint associated with raw material extraction and long-distance transport.
- **Resource Efficiency**: Promotes the reuse of precious metals, plastics, and chemicals, preserving the planet's finite resources.

### 💰 Economic Empowerment
- **New Revenue Streams**: Industries can turn disposal costs into profits by selling their waste.
- **Lower Raw Material Costs**: Recyclers and manufacturers gain access to high-quality secondary materials at a fraction of the cost of virgin resources.
- **Job Creation**: Supports the growth of the green-tech sector and local recycling local economies.

### 🔒 Privacy & Trust (E2EE)
- **Safe Negotiations**: Our **End-to-End Encryption (E2EE)** ensures that sensitive business negotiations, pricing, and pickup addresses are visible **only** to the buyer and seller. Not even the ReLoop server can read your messages.

---

## ✨ Key Features

### 🤖 AI Matchmaking Engine
Our Scikit-learn powered engine uses **TF-IDF Vectorization** and **Cosine Similarity** to analyze material descriptions and recommend the most compatible industries for reuse, ensuring waste finds its perfect home.

### 📊 Real-time Impact Analytics
Every transaction calculates a real-world impact score:
- **CO2 Saved** (kg)
- **Energy Saved** (kWh)
- **Landfill Volume Avoided** (tons)

### 💬 Secure E2EE Chat
Built with **TweetNaCl**, our chat system provides military-grade security for industrial negotiations. Private keys are stored locally in your browser, ensuring total privacy.

---

## 📖 Step-by-Step Usage Guide

To experience the full potential of ReLoop, follow this workflow:

### 1. User Onboarding
- **Register**: Create two accounts (e.g., "SteelWorks Inc" as a Seller and "GreenRecycling" as a Buyer).
- **Secure Login**: Upon login, the system automatically generates your unique E2EE key pair. Your private key is stored safely in your browser's `localStorage`.

### 2. The Marketplace Flow
- **Seller**: Go to the **Marketplace**, click **➕ Create Listing**, and add a material (e.g., "1 Ton Scrap Steel"). Our AI engine will instantly analyze your description.
- **Buyer**: Browse the Marketplace. Click on the Steel listing to see **AI-Recommended Industries** that can reuse this material and the projected **Environmental Impact Score**.

### 3. Secure Negotiation
- **Buyer**: Click **🛒 Request Material**. This notifies the seller and creates a private, encrypted channel.
- **Negotiate**: Go to your **Dashboard**. Click **💬 Chat** to open the E2EE negotiation window. Share sensitive details like pickup address or price bargains with total privacy.

### 4. Closing the Loop
- **Seller**: Review incoming requests on your Dashboard and click **Accept** once you've reached an agreement in chat.
- **Buyer**: After receiving the material, click **✅ Mark Received**. This finalizes the transaction, marks the listing as **SOLD**, and adds the diverted waste to the global platform impact stats.

---

## 🛠️ Step-by-Step Installation

### Backend Setup (FastAPI)
1.  **Navigate**: `cd backend`
2.  **Environment**: Create a `.env` file:
    ```env
    DATABASE_URL=sqlite:///./reloop.db
    SECRET_KEY=generate_a_secure_random_string
    ALGORITHM=HS256
    ```
3.  **Install**: `pip install -r requirements.txt`
4.  **Launch**: `python -m uvicorn app.main:app --reload --port 8000`

### Frontend Setup (React)
1.  **Navigate**: `cd frontend`
2.  **Install**: `npm install` (Installs `tweetnacl`, `axios`, and `react-router`)
3.  **Launch**: `npm run dev`
4.  **Access**: Visit `http://localhost:5173`

*(Note: Ensure the AI Engine is initialized via `python training/train_model.py` in the `ai-engine` folder to enable recommendations.)*

---

## 📂 Project Structure

- `/backend`: FastAPI application, SQLite database, and JWT security.
- `/frontend`: React dashboard, Marketplace UI, and E2EE Chat components.
- `/ai-engine`: Python scripts for TF-IDF training and inference.
- `/infrastructure`: Docker configurations for containerized deployment.

---

## 🤝 Contributing
Join us in building a zero-waste future! Feel free to fork the repo and submit pull requests.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
