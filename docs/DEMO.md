# Demo Guide

This guide explains how to demo the SahaiSetu AI Triage System to stakeholders, judges, or evaluators.

## Demo Walkthrough (15-20 minutes)

### Setup
1. Open the system at http://localhost:3000
2. Have both the victim and officer views ready in different browser tabs/windows

### Part 1: Victim Interaction (5 min)
1. Go to the **Victim Landing Page** (http://localhost:3000)
2. Click "Start" to begin a new interaction
3. **Select a language** (English, Hindi, Bengali, etc.)
4. **Choose input method** - either text or audio
5. **Type/speak a sample scenario**:
   - "I'm scared, my husband has been threatening me. I don't know what to do."
   - Or for critical: "I think he might hurt me tonight. I'm alone with the children."
6. **Submit** the interaction
7. Show the **AI assessment result** - the SVI score, risk level, indicators
8. Show the **anonymized case ID** generated

### Part 2: Officer Dashboard (10 min)
1. Switch to the **Officer Dashboard** (http://localhost:3000/officer)
2. Login as `officer1` / `demo123`
3. **Dashboard view** - Show summary stats, risk distribution charts
4. **Priority Cases** - Show the case you just submitted, now ranked by priority
5. **Case Details** - Click on the case to see:
   - AI-generated risk assessment
   - Detected indicators (threat, fear, distress, etc.)
   - Recommended actions (counselling, safety assessment, legal support, etc.)
   - The officer can add a review/decision
6. **Add a review** - Mark the case as confirmed, modified, etc.
7. **Analytics** - Show the trends, language distribution, AI vs human comparison

### Part 3: Key Features to Highlight (5 min)
- **Multi-language support** - Switch to Hindi or Bengali
- **Multi-modal input** - Audio vs text
- **SVI scoring** - Explain the Social Vulnerability Index
- **Recommendation engine** - Show how different risk levels generate different recommendations
- **Audit logging** - Every action is logged
- **Role-based access** - Different roles see different things
- **Demo mode** - Explain that real AI models can be plugged in

## Key Talking Points

### Problem Statement
- India receives millions of calls to helplines like 14443
- Officers need to prioritize cases based on vulnerability and risk
- Manual prioritization is slow, inconsistent, and stressful
- AI-assisted triage helps officers focus on the most urgent cases

### Solution Highlights
- **Anonymized**: No PII is stored - only anonymized case IDs
- **Multi-modal**: Audio + Text + Context
- **Multi-lingual**: Supports 13 Indian languages
- **Decision-support**: AI suggests, humans decide
- **Transparent**: Officers see all the AI's reasoning
- **Auditable**: Every action is logged for accountability

### Ethical Considerations
- AI is a tool, not a decision-maker
- All cases require human review
- Synthetic data only in demo mode
- Privacy by design (anonymization, encryption)
- Clear disclaimers throughout the UI

## Sample Demo Scenarios

### Scenario 1: Domestic Distress (HIGH)
- Language: Hindi
- Text: "Mujhe dar lag raha hai, mera pati mujhpe haath utha raha hai" (I'm scared, my husband is hitting me)
- Expected: HIGH risk, indicators: threat, fear, distress
- Recommendations: Safety assessment, counselling, legal support

### Scenario 2: Mental Health Crisis (CRITICAL)
- Language: English
- Text: "I don't want to live anymore. I've been thinking about ending it all."
- Expected: CRITICAL risk, indicators: distress, hopelessness
- Recommendations: Emergency mental health support, immediate human review

### Scenario 3: Child Safety Concern (CRITICAL)
- Language: Bengali
- Text: "Ami onek bhoy paichi, amar baccha ke niye kothao jete parchi na" (I'm very scared, I can't go anywhere with my child)
- Expected: CRITICAL risk
- Recommendations: Child safety services, immediate review

### Scenario 4: General Inquiry (LOW)
- Language: English
- Text: "I just wanted information about your services"
- Expected: LOW risk
- Recommendations: Standard information referral

## Reset Demo State

To reset all demo data:
```bash
docker compose down -v
docker compose up -d
```

This will clear the database and re-seed demo cases.

## Notes for the Judges

- The system is a **prototype** for evaluation purposes
- All data shown is **synthetic** - no real victim information
- The AI in demo mode is **rule-based** but the architecture supports real ML models
- The codebase is **production-quality** with proper error handling, logging, testing
- We prioritize **safety, ethics, and privacy** by design
