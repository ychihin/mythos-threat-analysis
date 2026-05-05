# Mythos Threat Analysis: NLP-Driven Risk Assessment

## Project Overview
This repository contains a technical pipeline designed to evaluate the risks of Anthropic's **Mythos** model and **Project Glasswing**. Instead of evaluating public "feelings," this project uses **Zero-Shot NLP Classification** to extract predicted threat models from expert discourse (Hacker News and Cybersecurity forums).

## 🚀 Key Technical Features
- **Expert Discourse Scraper:** Targeted extraction of titles and full comment bodies from Hacker News and Reddit.
- **Metal Acceleration (MPS):** Optimized for **Apple M1 Pro GPU** using PyTorch to handle large-scale NLP inference.
- **Dual-Vector Extraction:** Uses `facebook/bart-large-mnli` to autonomously categorize discussions into:
    - **Predicted Victims:** (Healthcare, Financial Institutions, Critical Infrastructure, etc.)
    - **Predicted Harms:** (Autonomous Sabotage, Zero-Day Exploitation, Financial Fraud, etc.)
- **Temporal Sentiment Mapping:** Tracks the "expert outlook" over time to identify volatility during model leaks or misuse events.

## 📈 Preliminary Findings (May 2026)
- **Primary Concern:** **Autonomous Sabotage** is the most predicted harm, appearing in 75% of expert discussions.
- **Highest Risk Sector:** **Financial Institutions** represent the only victim category with an average negative sentiment, indicating high-stakes systemic fear.
- **Sentiment Split":** A significant sentiment split (50% Pos / 29% Neg) exists between those viewing Mythos as a defensive "immune system" (citing the 271 Firefox fixes) and those viewing it as an uncontrollable cyberweapon (citing the Discord breach).

## 🛠 Setup & Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` with Reddit API keys (optional, script fallbacks to HN/Mock data).
3. Run analysis: `python mythos_analyzer.py`

## ⚖️ Conclusion
**Is Mythos Dangerous?** Yes. The data confirms that while defensive utility is high, the "Asymmetry of Speed" in autonomous exploit generation creates a permanent instability in global digital infrastructure that human-centric patch cycles cannot resolve.
