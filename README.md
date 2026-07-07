# NOCT Creative Dispatch

**Part of the NOCT Design Exercise for the Monsoon Internship.**

This is a prototype of a better workflow for AI Video Generation. Instead of blindly running expensive AI video generation models, this workflow helps designers improve cost efficiency and generate higher-quality prompts by providing rich visual and textual context.

## Core Design Concepts

- **Designer-Driven Context:** Combines a product image, optional style-reference keyframes, and the designer's intent.
- **Prompt Workspace:** Utilizes a Vision Language Model (Gemini 2.5 Flash) to analyze the assets and generate highly structured, spatially aware prompt scripts. Designers can preview and tweak this script before any video model runs.
- **Cost & Quality Tiering:** Offers clear tier choices to balance visual realism, precision camera movements, and computing cost.
- **Pre-existing Asset Matching (Demo Mode):** Intelligently matches product name keywords and requested tiers to pre-generated videos, saving compute and time during the design validation phase.

---

## Workspace Screenshot Gallery

Below are screenshots demonstrating the horizontal stepper workflow:

### Step 1: Asset Assembly

![Asset Assembly](frontend/public/ss1.png)

### Step 2 & 3: Prompt Workspace & Generation Engine

![Prompt Workspace & Engine](frontend/public/ss2.png)

### Step 4: Archive & Delivery

![Archive & Delivery](frontend/public/ss3.png)

---

## Technical Stack

- **Frontend:** React, Tailwind CSS, Vite.
- **Backend:** FastAPI, Python (handling prompt compilation and video metadata matching).
- **VLM Integration:** Gemini 2.5 Flash (via direct API fetch or backend proxy).
- **Storage Archive:** Google Drive API Integration.

## Deployment Link

- **Live Prototype Demo:** [noct-creative-dispatch-prod.vercel.app](https://noct-creative-dispatch-prod.vercel.app)
