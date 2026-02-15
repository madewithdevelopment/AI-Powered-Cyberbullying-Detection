from flask import Flask, request, jsonify, render_template, session
from transformers import pipeline
import numpy as np
import re
import os
import random
import uuid
from datetime import datetime, timedelta

import sys
# Force UTF-8 encoding for stdout on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# --------- FLASK APP ----------
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.secret_key = "cybershield-dextrix-secret-2025"

# --------- MODELS ----------
print("Loading toxic-bert model...")
try:
    bully_detector = pipeline("text-classification", model="unitary/toxic-bert")
    print("[OK] Model loaded!")
except Exception as e:
    print(f"[!] Model loading failed: {e}")
    print("[!] Running in SAFE MODE with mock detection.")
    # Fallback to mock if loading fails
    class MockPipeline:
        def __call__(self, text):
            # Simple keyword-based mock data for testing
            text_lower = text.lower()
            if any(w in text_lower for w in ["hate", "stupid", "idiot", "kill", "ugly"]):
                return [{"label": "toxic", "score": 0.95}]
            return [{"label": "neutral", "score": 0.05}]
            
    bully_detector = MockPipeline()
    


# --------- MEME RESPONSES ----------
MEME_SAFE = [
    "You're literally the main character. Keep going! 💅",
    "Wholesome energy detected. We stan. 🫶",
    "This is giving kindness era ✨",
    "POV: you're the friend everyone needs 🥺",
    "Certified good vibes only 🌈",
]
MEME_SARCASTIC = [
    "Hmm, that's kinda sus… 🤨",
    "The sass is giving mean girl energy 😏",
    "Not the passive aggression… 👀",
    "Tell me you're sarcastic without telling me 💀",
]
MEME_RISKY = [
    "Bestie, this is giving red flag vibes 🚩",
    "Whoa 👀 that escalated quickly…",
    "Not very sigma behavior tbh 🐺",
    "This ain't it, chief 😬",
]
MEME_TOXIC = [
    "Oof. That's not the vibe, fam 💀",
    "Main villain energy detected 🦹",
    "Be the main character, not the villain ⚔️",
    "Sir/Ma'am this is a Wendy's. Calm down 🍔",
]
MEME_ULTRA = [
    "DEFCON 1 activated. Touch grass immediately 🌿",
    "💀💀💀 The toxicity is off the charts",
    "Bro really woke up and chose violence 😤",
    "This is giving final boss energy… and not in a good way 👹",
]

# --------- MENTAL HEALTH MESSAGES ----------
MENTAL_HEALTH_MSGS = [
    "Hey, are you okay? Words come from somewhere. 💙",
    "It seems like you might be going through something. You're not alone. 🤗",
    "If you need someone to talk to: iCall helpline 9152987821 📞",
    "Remember: being kind online starts with being kind to yourself. 🌱",
]

# --------- POLITE REWRITES ----------
TOXIC_REWRITES = {
    "useless": "could improve with some guidance",
    "stupid": "still learning",
    "idiot": "someone who might need help",
    "ugly": "unique in their own way",
    "dumb": "still figuring things out",
    "loser": "someone going through a tough time",
    "hate": "strongly disagree with",
    "shut up": "I'd appreciate some quiet",
    "die": "take a break",
    "kill": "step away from",
    "fat": "body-positive",
    "trash": "not quite there yet",
    "pathetic": "still growing",
    "worst": "not the best right now",
    "disgusting": "not my preference",
    "terrible": "needs some work",
    "horrible": "could be better",
    "fool": "someone still learning",
    "weak": "building strength",
    "boring": "calm and steady",
    "creep": "someone I'm uncomfortable with",
    "freak": "someone unique",
    "worthless": "still finding their value",
    "suck": "aren't great at",
    "moron": "someone who made a mistake",
}

POLITE_TEMPLATES = [
    "I think {rewrite}. Let's work on it together. 🤝",
    "Hey, maybe {rewrite}. We can all grow! 🌱",
    "What if we said: {rewrite}? Sounds better, right? ✨",
    "{rewrite} — that's a kinder way to put it. 💙",
]

# --------- CHALLENGE POSITIVES ----------
CHALLENGE_HINTS = [
    "Try focusing on what could be improved instead of attacking the person.",
    "What if you expressed frustration without targeting someone?",
    "Can you turn this into constructive feedback?",
    "Think: would you say this to someone you care about?",
]


# ═══════════════════════════════════════════════════════════
#  PLATFORM INTEGRATION — Social Media Monitoring Engine
# ═══════════════════════════════════════════════════════════

# --------- FRAUD DETECTION PATTERNS ----------
FRAUD_PATTERNS = [
    r'(?i)(click\s+(?:here|this|link)|bit\.ly|tinyurl|goo\.gl)',
    r'(?i)(free\s+(?:iphone|money|gift|prize|bitcoin|crypto))',
    r'(?i)(congrat(?:ulation)?s?\s*!?\s*you\s+(?:won|have\s+been\s+selected))',
    r'(?i)(send\s+(?:me\s+)?(?:money|bank|account|card|otp|password|pin))',
    r'(?i)(urgent|act\s+now|limited\s+time|don.?t\s+miss|hurry)',
    r'(?i)(verify\s+(?:your|account)|confirm\s+(?:identity|payment))',
    r'(?i)(earn\s+\$?\d+\s*(?:per|a)\s*(?:day|hour|week))',
    r'(?i)(work\s+from\s+home\s+(?:earn|make|job))',
    r'(?i)(lottery|jackpot|winning|claim\s+your)',
    r'(?i)(nigerian?\s+prince|inheritance|beneficiary)',
    r'(?i)(invest\s+(?:now|today).*(?:guaranteed|profit|return))',
    r'(?i)(impersonat|fake\s+(?:profile|account|identity))',
]

FAKE_MEDIA_INDICATORS = [
    r'(?i)(deepfake|ai\s+generated|fake\s+video|morphed|manipulated)',
    r'(?i)(this\s+(?:video|image|photo)\s+(?:is|was)\s+(?:fake|doctored|edited))',
    r'(?i)(don.?t\s+believe|not\s+real|fabricated|hoax)',
    r'(?i)(photoshopped|face\s*swap|voice\s*clone)',
    r'(?i)(misinformation|disinformation|propaganda|conspiracy)',
    r'(?i)(unverified|unconfirmed|rumor|false\s+(?:claim|news|info))',
]

# --------- SIMULATED SOCIAL MEDIA POSTS ----------
SIMULATED_POSTS = {
    "whatsapp": [
        {"user": "Unknown +91-XXX", "content": "Congratulations! You won ₹50,000! Click here to claim: bit.ly/win-now 🎉", "type": "message", "media": None},
        {"user": "Group: College Friends", "content": "You're so useless, just leave the group nobody wants you here 😂", "type": "group_message", "media": None},
        {"user": "Unknown +44-XXX", "content": "URGENT: Your bank account will be blocked. Send OTP to verify: 1800-XXX-XXX", "type": "message", "media": None},
        {"user": "Riya 💕", "content": "Hey! Great work on the project today. Really proud of you! 🌟", "type": "message", "media": None},
        {"user": "Group: School Batch", "content": "Look at this deepfake video of our teacher 💀💀 so funny", "type": "group_message", "media": "video_attachment"},
        {"user": "Unknown +1-XXX", "content": "Work from home and earn $5000/day! Guaranteed returns, invest now!", "type": "message", "media": None},
        {"user": "Brother", "content": "Come home for dinner, mom made your favorite 🍲", "type": "message", "media": None},
        {"user": "Unknown +91-XXX", "content": "I have your private photos. Send ₹10,000 or I will share them everywhere.", "type": "message", "media": None},
    ],
    "instagram": [
        {"user": "@toxic_troll_42", "content": "You're the ugliest person I've ever seen. Delete your account loser 🗑️", "type": "comment", "media": None},
        {"user": "@crypto_king_real", "content": "DM me for FREE BITCOIN! I turned $100 into $50,000 in just 1 week! 🚀💰", "type": "dm", "media": "image_proof"},
        {"user": "@bestie_forever", "content": "You look amazing in this photo! Keep shining ✨💫", "type": "comment", "media": None},
        {"user": "@news_breaker_x", "content": "BREAKING: This AI-generated video shows politician doing [fake activity]. Share before it gets deleted!", "type": "story_reply", "media": "fake_video"},
        {"user": "@anon_hater", "content": "Everyone in your school thinks you're pathetic. Just give up already 💀", "type": "dm", "media": None},
        {"user": "@free_gifts_2025", "content": "🎁 FREE iPhone 16! Just follow, like, and send your address + card details to claim!", "type": "comment", "media": None},
        {"user": "@classmate_raj", "content": "Great presentation today! You really nailed the delivery 👏", "type": "comment", "media": None},
        {"user": "@fake_celeb_acc", "content": "I'm giving away $10,000 to my followers! Send $50 processing fee to claim!", "type": "dm", "media": None},
    ],
    "twitter": [
        {"user": "@hate_spreader", "content": "People like you don't deserve to exist. The world would be better without you.", "type": "reply", "media": None},
        {"user": "@tech_daily", "content": "Great thread on AI safety! We need more conversations like this 🤖", "type": "mention", "media": None},
        {"user": "@scam_lottery", "content": "You've been selected as our WINNER! DM us with your bank details to receive $100,000! 🎰", "type": "dm", "media": None},
        {"user": "@misinfo_bot", "content": "This manipulated video proves the conspiracy! Don't believe mainstream media. SHARE NOW!", "type": "tweet", "media": "manipulated_video"},
        {"user": "@school_bully99", "content": "Lmao look at this loser trying to be smart 😂😂 you're so dumb it hurts", "type": "reply", "media": None},
        {"user": "@supportive_ally", "content": "Your art is incredible! Don't listen to the haters, keep creating 🎨💪", "type": "reply", "media": None},
        {"user": "@phishing_link", "content": "Your Twitter account has been compromised! Verify now: twiter-security.fake.com/verify", "type": "dm", "media": None},
        {"user": "@troll_army", "content": "This is the worst take I've ever seen. You should be ashamed. Disgusting human being.", "type": "reply", "media": None},
    ],
}

# --------- CYBER HUB REPORTS (in-memory store) ----------
cyberhub_reports = []

# --------- FRAUD DETECTION ----------
def detect_fraud(text):
    """Detect fraud/scam patterns in text."""
    fraud_score = 0.0
    matched_patterns = []

    for pattern in FRAUD_PATTERNS:
        if re.search(pattern, text):
            fraud_score += 0.25
            matched_patterns.append(re.search(pattern, text).group(0))

    fraud_score = min(fraud_score, 1.0)
    return {
        "score": round(fraud_score, 4),
        "is_fraud": fraud_score > 0.3,
        "matched_patterns": matched_patterns[:3],
    }

# --------- FAKE MEDIA DETECTION ----------
def detect_fake_media(text, media_type=None):
    """Detect fake/manipulated media indicators."""
    fake_score = 0.0
    indicators = []

    for pattern in FAKE_MEDIA_INDICATORS:
        if re.search(pattern, text):
            fake_score += 0.3
            indicators.append(re.search(pattern, text).group(0))

    # Boost if media attachment is present with suspicious keywords
    if media_type and media_type in ['video_attachment', 'fake_video', 'manipulated_video', 'image_proof']:
        fake_score += 0.3
        indicators.append(f"Suspicious media: {media_type}")

    fake_score = min(fake_score, 1.0)
    return {
        "score": round(fake_score, 4),
        "is_fake": fake_score > 0.25,
        "indicators": indicators[:3],
    }

# --------- EXTENDED CONTENT ANALYSIS ----------
def analyze_content(text, media_type=None):
    """Full content analysis: toxicity + fraud + fake media."""
    # Run existing toxicity detection
    toxicity_result = detect(text)

    # Run fraud detection
    fraud_result = detect_fraud(text)

    # Run fake media detection
    fake_result = detect_fake_media(text, media_type)

    # Determine primary threat category
    threats = []
    if toxicity_result["risk"] > 0.4:
        threats.append({"type": "toxicity", "severity": toxicity_result["risk"],
                       "detail": toxicity_result["explanation"]})
    if fraud_result["is_fraud"]:
        threats.append({"type": "fraud", "severity": fraud_result["score"],
                       "detail": f"Scam patterns detected: {', '.join(fraud_result['matched_patterns'])}"})
    if fake_result["is_fake"]:
        threats.append({"type": "fake_media", "severity": fake_result["score"],
                       "detail": f"Fake content indicators: {', '.join(fake_result['indicators'])}"})
    if toxicity_result["risk"] > 0.65:
        threats.append({"type": "harassment", "severity": toxicity_result["risk"],
                       "detail": "Severe harassment or bullying detected"})

    # Overall threat level
    max_severity = max([t["severity"] for t in threats]) if threats else 0
    if not threats:
        primary_category = "safe"
    else:
        primary_category = max(threats, key=lambda t: t["severity"])["type"]

    return {
        **toxicity_result,
        "fraud": fraud_result,
        "fake_media": fake_result,
        "threats": threats,
        "primary_category": primary_category,
        "overall_severity": round(max_severity, 4),
    }

# --------- AI AUTO-ACTION ENGINE ----------
def decide_action(analysis, platform, user):
    """AI decides what action to take based on analysis."""
    severity = analysis["overall_severity"]
    threats = analysis["threats"]
    category = analysis["primary_category"]

    if severity < 0.25:
        action = "monitor"
        action_icon = "👁️"
        explanation = "Content appears safe. Continuing passive monitoring."
        auto_report = False
    elif severity < 0.5:
        action = "flag"
        action_icon = "🚩"
        explanation = f"Content flagged for review. Detected: {category}."
        auto_report = False
    elif severity < 0.75:
        action = "block"
        action_icon = "🛑"
        explanation = f"Content blocked automatically. High-risk {category} detected from {user}."
        auto_report = True
    else:
        action = "report_to_cyberhub"
        action_icon = "🚨"
        explanation = f"CRITICAL THREAT. Auto-reported to Cyber Hub. Severe {category} from {user} on {platform}."
        auto_report = True

    # Auto-report to Cyber Hub if needed
    report_id = None
    if auto_report and threats:
        report_id = submit_cyberhub_report(
            platform=platform,
            user=user,
            content=analysis.get("meme", ""),
            threats=threats,
            severity=severity,
            action_taken=action
        )

    return {
        "action": action,
        "action_icon": action_icon,
        "explanation": explanation,
        "auto_reported": auto_report,
        "report_id": report_id,
    }

# --------- CYBER HUB REPORTING ----------
def submit_cyberhub_report(platform, user, content, threats, severity, action_taken):
    """Submit a report to the Cyber Hub."""
    report_id = f"CH-{uuid.uuid4().hex[:8].upper()}"
    report = {
        "id": report_id,
        "timestamp": datetime.now().isoformat(),
        "platform": platform,
        "reported_user": user,
        "content_snippet": content[:100] if content else "N/A",
        "threats": [{"type": t["type"], "severity": round(t["severity"], 2)} for t in threats],
        "overall_severity": round(severity, 2),
        "action_taken": action_taken,
        "status": "submitted",
        "status_icon": "📤",
        "priority": "critical" if severity > 0.75 else "high" if severity > 0.5 else "medium",
    }
    cyberhub_reports.insert(0, report)
    print(f"[REPORT] CYBER HUB REPORT {report_id}: {platform} | {user} | Severity: {severity:.2f} | Action: {action_taken}")
    return report_id

# --------- SCAN PLATFORM ----------
def scan_platform(platform_name):
    """Scan a platform's simulated feed and analyze all posts."""
    posts = SIMULATED_POSTS.get(platform_name, [])
    results = []

    for post in posts:
        analysis = analyze_content(post["content"], post.get("media"))
        action = decide_action(analysis, platform_name, post["user"])

        results.append({
            "platform": platform_name,
            "user": post["user"],
            "content": post["content"],
            "type": post["type"],
            "media": post.get("media"),
            "analysis": {
                "risk": analysis["risk"],
                "level": analysis["level"],
                "roast_icon": analysis["roast_icon"],
                "primary_category": analysis["primary_category"],
                "overall_severity": analysis["overall_severity"],
                "threats": analysis["threats"],
                "fraud": analysis["fraud"],
                "fake_media": analysis["fake_media"],
                "explanation": analysis["explanation"],
            },
            "action": action,
        })

    return results


# --------- DETECTION LOGIC ----------
def detect(text):
    sarcasm_keywords = ['smart', 'great', 'nice', 'good', 'perfect', 'awesome',
                        'genius', 'wah', 'kya baat']
    sarcasm_emojis = ['😂', '😏', '🙄', '🤦', '😉']

    sarcasm_score = 0.2
    if any(word in text.lower() for word in sarcasm_keywords):
        sarcasm_score += 0.4
    emoji_count = len(re.findall('[' + ''.join(sarcasm_emojis) + ']', text))
    sarcasm_score += 0.3 * emoji_count
    sarcasm_score = min(0.95, sarcasm_score)

    bully = bully_detector(text)[0]
    bully_score = bully['score'] if bully['label'] == 'toxic' else 0.1

    risk = float(np.clip(
        (bully_score * 0.6 + sarcasm_score * 1.2) / 2
        + np.random.normal(0, 0.03),
        0, 1
    ))

    # 5-level roast meter
    if risk > 0.85:
        level = "Ultra Toxic"
        roast_icon = "💀"
        meme = random.choice(MEME_ULTRA)
    elif risk > 0.65:
        level = "Toxic"
        roast_icon = "🔴"
        meme = random.choice(MEME_TOXIC)
    elif risk > 0.45:
        level = "Risky"
        roast_icon = "🟠"
        meme = random.choice(MEME_RISKY)
    elif risk > 0.25:
        level = "Sarcastic"
        roast_icon = "🟡"
        meme = random.choice(MEME_SARCASTIC)
    else:
        level = "Safe"
        roast_icon = "🔵"
        meme = random.choice(MEME_SAFE)

    # Explanation with Gen Z microcopy
    if risk > 0.85:
        explanation = "💀 YIKES. Maximum toxicity detected. Not the vibe at all."
    elif risk > 0.65:
        explanation = "🔴 This is giving toxic energy. Words hurt, bestie."
    elif risk > 0.45:
        explanation = "🟠 Whoa 👀 that escalated quickly… tread carefully."
    elif risk > 0.25:
        explanation = "🟡 The sarcasm is strong with this one. Proceed with caution."
    else:
        explanation = "🔵 All clear! Wholesome energy detected ✨"

    mood = "🙂" if risk < 0.25 else "😏" if risk < 0.45 else "😬" if risk < 0.65 else "😡" if risk < 0.85 else "💀"

    # Empathy / Respect / Risk scores for Kindness dashboard
    empathy = round(max(0, 1 - risk - 0.1 * sarcasm_score + np.random.normal(0, 0.05)), 4)
    empathy = float(np.clip(empathy, 0, 1))
    respect = round(max(0, 1 - bully_score * 0.8 + np.random.normal(0, 0.03)), 4)
    respect = float(np.clip(respect, 0, 1))

    # Mental health trigger
    mental_health_msg = None
    if risk > 0.7:
        mental_health_msg = random.choice(MENTAL_HEALTH_MSGS)

    # Mood flip (polite rewrite)
    polite_rewrite = generate_polite_rewrite(text, risk)

    # Challenge hint
    challenge_hint = None
    if risk > 0.4:
        challenge_hint = random.choice(CHALLENGE_HINTS)

    return {
        "risk": round(risk, 4),
        "level": level,
        "roast_icon": roast_icon,
        "sarcasm_score": round(sarcasm_score, 4),
        "toxicity_score": round(bully_score, 4),
        "explanation": explanation,
        "mood": mood,
        "meme": meme,
        "empathy_score": empathy,
        "respect_score": respect,
        "mental_health": mental_health_msg,
        "polite_rewrite": polite_rewrite,
        "challenge_hint": challenge_hint,
    }


def generate_polite_rewrite(text, risk):
    """Generate a polite version of toxic text."""
    if risk < 0.3:
        return None  # already safe

    rewritten = text.lower()
    changed = False
    for toxic, polite in TOXIC_REWRITES.items():
        if toxic in rewritten:
            rewritten = rewritten.replace(toxic, polite)
            changed = True

    if changed:
        # Clean up and capitalize
        rewritten = rewritten.strip().capitalize()
        if not rewritten.endswith('.'):
            rewritten += '.'
        template = random.choice(POLITE_TEMPLATES)
        return template.format(rewrite=rewritten)
    else:
        # Generic rewrite
        return f"This sounds harsh. Maybe try expressing your feelings without targeting someone? 💙"


# --------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    result = detect(text)
    return jsonify(result)


@app.route("/report", methods=["POST"])
def report():
    """Anonymous reporting endpoint."""
    data = request.get_json(force=True)
    message = data.get("message", "").strip()
    context = data.get("context", "").strip()
    if not message:
        return jsonify({"error": "No message to report"}), 400
    # In production, save to database. For hackathon, just acknowledge.
    print(f"[REPORT] ANONYMOUS REPORT: {message} | Context: {context}")
    return jsonify({
        "success": True,
        "response": "Report submitted anonymously. Stay safe, we've got your back. 🛡️"
    })


@app.route("/challenge", methods=["POST"])
def challenge():
    """Check if user's rewrite is positive enough."""
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    result = detect(text)
    passed = result["risk"] < 0.3
    return jsonify({
        "passed": passed,
        "risk": result["risk"],
        "level": result["level"],
        "feedback": "🎉 Nailed it! That's the positive energy we need! ✨" if passed
                    else "Almost there! Try making it even more positive and encouraging. 💪",
    })


# ═══════════════════════════════════════════════════════════
#  PLATFORM API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.route("/api/platform/feed", methods=["GET"])
def platform_feed():
    """Get analyzed feed from all or specific platform."""
    platform = request.args.get("platform", "all")
    all_results = []

    if platform == "all":
        for p in ["whatsapp", "instagram", "twitter"]:
            all_results.extend(scan_platform(p))
    else:
        all_results = scan_platform(platform)

    # Sort by severity (most dangerous first)
    all_results.sort(key=lambda x: x["analysis"]["overall_severity"], reverse=True)

    response_data = {
        "feed": all_results,
        "total": len(all_results),
        "threats_found": sum(1 for r in all_results if r["analysis"]["primary_category"] != "safe"),
        "auto_actions": sum(1 for r in all_results if r["action"]["action"] in ["block", "report_to_cyberhub"]),
    }
    import json as json_module
    json_str = json_module.dumps(response_data, default=str)
    return app.response_class(
        response=json_str,
        status=200,
        mimetype='application/json'
    )


@app.route("/api/platform/scan", methods=["POST"])
def platform_scan():
    """Trigger a scan on a specific platform."""
    try:
        data = request.get_json(force=True)
        platform = data.get("platform", "all")

        all_results = []
        if platform == "all":
            for p in ["whatsapp", "instagram", "twitter"]:
                all_results.extend(scan_platform(p))
        else:
            all_results = scan_platform(platform)

        all_results.sort(key=lambda x: x["analysis"]["overall_severity"], reverse=True)

        response_data = {
            "feed": all_results,
            "total": len(all_results),
            "threats_found": sum(1 for r in all_results if r["analysis"]["primary_category"] != "safe"),
            "auto_actions": sum(1 for r in all_results if r["action"]["action"] in ["block", "report_to_cyberhub"]),
            "scan_complete": True,
        }
        # Use json.dumps with default=str to handle any non-serializable types
        import json as json_module
        json_str = json_module.dumps(response_data, default=str)
        return app.response_class(
            response=json_str,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print("ERROR in platform_scan:", str(e))
        error_response = {"error": "Internal server error", "detail": str(e)}
        import json as json_module
        return app.response_class(
            response=json_module.dumps(error_response),
            status=500,
            mimetype='application/json'
        )


@app.route("/api/platform/stats", methods=["GET"])
def platform_stats():
    """Get platform-level statistics."""
    stats = {}
    for p in ["whatsapp", "instagram", "twitter"]:
        results = scan_platform(p)
        threats = [r for r in results if r["analysis"]["primary_category"] != "safe"]
        stats[p] = {
            "total_scanned": len(results),
            "threats_found": len(threats),
            "blocked": sum(1 for r in results if r["action"]["action"] == "block"),
            "reported": sum(1 for r in results if r["action"]["action"] == "report_to_cyberhub"),
            "threat_types": list(set(r["analysis"]["primary_category"] for r in threats)),
        }

    response_data = {
        "platforms": stats,
        "total_reports": len(cyberhub_reports),
    }
    import json as json_module
    json_str = json_module.dumps(response_data, default=str)
    return app.response_class(
        response=json_str,
        status=200,
        mimetype='application/json'
    )


@app.route("/api/cyberhub/reports", methods=["GET"])
def get_cyberhub_reports():
    """Get all Cyber Hub reports."""
    return jsonify({
        "reports": cyberhub_reports,
        "total": len(cyberhub_reports),
        "critical": sum(1 for r in cyberhub_reports if r["priority"] == "critical"),
        "high": sum(1 for r in cyberhub_reports if r["priority"] == "high"),
        "medium": sum(1 for r in cyberhub_reports if r["priority"] == "medium"),
    })


@app.route("/api/cyberhub/report", methods=["POST"])
def manual_cyberhub_report():
    """Submit a manual Cyber Hub report."""
    data = request.get_json(force=True)
    platform = data.get("platform", "unknown")
    user = data.get("user", "anonymous")
    content = data.get("content", "")
    threat_type = data.get("threat_type", "harassment")

    if not content:
        return jsonify({"error": "No content provided"}), 400

    analysis = analyze_content(content)
    report_id = submit_cyberhub_report(
        platform=platform,
        user=user,
        content=content,
        threats=analysis["threats"] or [{"type": threat_type, "severity": 0.7}],
        severity=analysis["overall_severity"] or 0.7,
        action_taken="manual_report"
    )

    response_data = {
        "success": True,
        "report_id": report_id,
        "message": f"Report {report_id} submitted to Cyber Hub successfully. 🛡️",
    }
    import json as json_module
    json_str = json_module.dumps(response_data, default=str)
    return app.response_class(
        response=json_str,
        status=200,
        mimetype='application/json'
    )


# --------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
