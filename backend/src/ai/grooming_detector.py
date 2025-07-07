"""
SafeGuardian AI Grooming Detection System
Advanced NLP-based detection of potential grooming behaviors in online communications
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class GroomingPattern(Enum):
    TRUST_BUILDING = "trust_building"
    ISOLATION = "isolation"
    DEPENDENCY = "dependency"
    RISK_ASSESSMENT = "risk_assessment"
    EXCLUSIVITY = "exclusivity"
    SEXUAL_CONTENT = "sexual_content"
    MEETING_REQUEST = "meeting_request"
    SECRECY = "secrecy"
    GIFT_OFFERING = "gift_offering"
    PERSONAL_INFO_REQUEST = "personal_info_request"

@dataclass
class DetectionResult:
    risk_level: RiskLevel
    confidence: float
    patterns_detected: List[GroomingPattern]
    risk_factors: List[str]
    explanation: str
    recommendations: List[str]
    timestamp: datetime
    message_hash: str

class GroomingDetector:
    """
    Advanced AI-powered grooming detection system using pattern recognition,
    linguistic analysis, and behavioral modeling.
    """
    
    def __init__(self):
        self.patterns = self._load_grooming_patterns()
        self.risk_keywords = self._load_risk_keywords()
        self.conversation_context = {}
        
    def _load_grooming_patterns(self) -> Dict[GroomingPattern, Dict]:
        """Load predefined grooming patterns and their indicators"""
        return {
            GroomingPattern.TRUST_BUILDING: {
                "keywords": [
                    "trust me", "you can tell me anything", "i understand you",
                    "nobody understands you like i do", "you're so mature",
                    "you're different from other kids", "special connection",
                    "i care about you", "you're so smart", "wise beyond your years"
                ],
                "phrases": [
                    r"you can trust me",
                    r"i would never hurt you",
                    r"you're so mature for your age",
                    r"nobody gets you like i do",
                    r"you're not like other \w+ your age"
                ],
                "weight": 0.7
            },
            
            GroomingPattern.ISOLATION: {
                "keywords": [
                    "don't tell", "keep this between us", "our secret",
                    "your parents wouldn't understand", "they don't get you",
                    "nobody else needs to know", "just between you and me",
                    "your friends are jealous", "they're trying to control you"
                ],
                "phrases": [
                    r"don't tell (anyone|your parents|your friends)",
                    r"keep this (secret|between us)",
                    r"your (parents|family) (wouldn't|don't) understand",
                    r"they're just trying to control you",
                    r"you don't need them"
                ],
                "weight": 0.9
            },
            
            GroomingPattern.DEPENDENCY: {
                "keywords": [
                    "i'm here for you", "you need me", "i'm the only one",
                    "depend on me", "i'll take care of you", "you can rely on me",
                    "i'll protect you", "i'm all you need", "lean on me"
                ],
                "phrases": [
                    r"i'm (here|there) for you",
                    r"you (need|can depend on) me",
                    r"i'll (take care of|protect) you",
                    r"i'm (all you need|the only one)"
                ],
                "weight": 0.8
            },
            
            GroomingPattern.SEXUAL_CONTENT: {
                "keywords": [
                    "sexy", "hot", "beautiful body", "mature", "developed",
                    "curious about sex", "sexual experience", "intimate",
                    "physical relationship", "body", "private parts"
                ],
                "phrases": [
                    r"you're so (sexy|hot|beautiful)",
                    r"have you ever (kissed|been intimate)",
                    r"curious about (sex|your body)",
                    r"want to (touch|feel|see) you",
                    r"show me your"
                ],
                "weight": 1.0
            },
            
            GroomingPattern.MEETING_REQUEST: {
                "keywords": [
                    "meet in person", "come over", "visit me", "hang out",
                    "see you alone", "private meeting", "just us two",
                    "pick you up", "come to my place", "meet somewhere"
                ],
                "phrases": [
                    r"want to meet (in person|up)",
                    r"come (over|to my place)",
                    r"see you (alone|in private)",
                    r"pick you up",
                    r"let's meet (somewhere|at)"
                ],
                "weight": 0.95
            },
            
            GroomingPattern.SECRECY: {
                "keywords": [
                    "secret", "don't tell anyone", "between us", "private",
                    "confidential", "our little secret", "keep quiet",
                    "don't mention", "nobody knows", "just for us"
                ],
                "phrases": [
                    r"(keep|this is) (our|a) secret",
                    r"don't (tell|mention) (this|anyone)",
                    r"between (you and me|us)",
                    r"nobody (else )?knows",
                    r"keep (this|it) (quiet|private)"
                ],
                "weight": 0.85
            },
            
            GroomingPattern.GIFT_OFFERING: {
                "keywords": [
                    "buy you", "gift for you", "present", "money",
                    "treat you", "spoil you", "get you something",
                    "surprise for you", "special gift", "reward"
                ],
                "phrases": [
                    r"(buy|get) you (something|a gift)",
                    r"have a (present|surprise) for you",
                    r"want to (treat|spoil) you",
                    r"give you (money|cash)",
                    r"special (gift|present) for you"
                ],
                "weight": 0.6
            },
            
            GroomingPattern.PERSONAL_INFO_REQUEST: {
                "keywords": [
                    "where do you live", "what school", "home address",
                    "phone number", "when are you alone", "parents work",
                    "schedule", "routine", "when nobody's home"
                ],
                "phrases": [
                    r"where do you (live|go to school)",
                    r"what's your (address|phone number)",
                    r"when are you (alone|home alone)",
                    r"when do your parents (work|leave)",
                    r"what's your (schedule|routine)"
                ],
                "weight": 0.8
            }
        }
    
    def _load_risk_keywords(self) -> Dict[str, float]:
        """Load risk keywords with associated weights"""
        return {
            # High risk keywords
            "nude": 1.0, "naked": 1.0, "undress": 1.0, "strip": 1.0,
            "webcam": 0.8, "camera": 0.6, "photo": 0.5, "picture": 0.4,
            "secret": 0.7, "private": 0.5, "alone": 0.6, "meet": 0.7,
            "age": 0.4, "mature": 0.6, "special": 0.5, "different": 0.4,
            "understand": 0.5, "trust": 0.6, "love": 0.5, "care": 0.4,
            
            # Location/meeting related
            "address": 0.8, "location": 0.7, "home": 0.5, "school": 0.6,
            "parents": 0.4, "family": 0.4, "friends": 0.3,
            
            # Gift/money related
            "money": 0.7, "gift": 0.6, "buy": 0.5, "present": 0.6,
            "treat": 0.5, "spoil": 0.6, "reward": 0.5,
            
            # Communication secrecy
            "delete": 0.7, "hide": 0.7, "clear": 0.5, "erase": 0.7,
            "history": 0.6, "messages": 0.4, "chat": 0.3
        }
    
    def analyze_message(self, message: str, sender_age: Optional[int] = None, 
                       recipient_age: Optional[int] = None, 
                       conversation_id: str = None) -> DetectionResult:
        """
        Analyze a single message for grooming indicators
        
        Args:
            message: The message text to analyze
            sender_age: Age of the message sender (if known)
            recipient_age: Age of the message recipient (if known)
            conversation_id: Unique identifier for the conversation
            
        Returns:
            DetectionResult with risk assessment and recommendations
        """
        message_lower = message.lower()
        message_hash = hashlib.md5(message.encode()).hexdigest()
        
        # Initialize detection results
        detected_patterns = []
        risk_factors = []
        total_risk_score = 0.0
        confidence = 0.0
        
        # Age gap analysis
        age_gap_risk = self._analyze_age_gap(sender_age, recipient_age)
        if age_gap_risk > 0:
            risk_factors.append(f"Significant age gap detected: {age_gap_risk}")
            total_risk_score += age_gap_risk * 0.3
        
        # Pattern detection
        for pattern, config in self.patterns.items():
            pattern_score = self._detect_pattern(message_lower, config)
            if pattern_score > 0.3:  # Threshold for pattern detection
                detected_patterns.append(pattern)
                risk_factors.append(f"{pattern.value}: {pattern_score:.2f}")
                total_risk_score += pattern_score * config["weight"]
        
        # Keyword analysis
        keyword_score = self._analyze_keywords(message_lower)
        if keyword_score > 0.2:
            risk_factors.append(f"Risk keywords detected: {keyword_score:.2f}")
            total_risk_score += keyword_score * 0.4
        
        # Linguistic analysis
        linguistic_score = self._analyze_linguistics(message)
        if linguistic_score > 0.3:
            risk_factors.append(f"Suspicious linguistic patterns: {linguistic_score:.2f}")
            total_risk_score += linguistic_score * 0.3
        
        # Context analysis (if conversation history available)
        if conversation_id:
            context_score = self._analyze_conversation_context(
                message, conversation_id, detected_patterns
            )
            total_risk_score += context_score * 0.2
        
        # Determine risk level and confidence
        risk_level, confidence = self._calculate_risk_level(total_risk_score, len(detected_patterns))
        
        # Generate explanation and recommendations
        explanation = self._generate_explanation(detected_patterns, risk_factors, total_risk_score)
        recommendations = self._generate_recommendations(risk_level, detected_patterns)
        
        return DetectionResult(
            risk_level=risk_level,
            confidence=confidence,
            patterns_detected=detected_patterns,
            risk_factors=risk_factors,
            explanation=explanation,
            recommendations=recommendations,
            timestamp=datetime.now(),
            message_hash=message_hash
        )
    
    def _detect_pattern(self, message: str, config: Dict) -> float:
        """Detect specific grooming patterns in message"""
        score = 0.0
        matches = 0
        
        # Check keywords
        for keyword in config["keywords"]:
            if keyword in message:
                score += 0.1
                matches += 1
        
        # Check regex patterns
        for phrase_pattern in config.get("phrases", []):
            if re.search(phrase_pattern, message, re.IGNORECASE):
                score += 0.3
                matches += 1
        
        # Normalize score
        if matches > 0:
            score = min(score, 1.0)
        
        return score
    
    def _analyze_keywords(self, message: str) -> float:
        """Analyze message for risk keywords"""
        total_score = 0.0
        word_count = len(message.split())
        
        for keyword, weight in self.risk_keywords.items():
            if keyword in message:
                # Consider keyword frequency and context
                frequency = message.count(keyword)
                context_multiplier = 1.0
                
                # Increase weight if keyword appears multiple times
                if frequency > 1:
                    context_multiplier = 1.0 + (frequency - 1) * 0.2
                
                total_score += weight * context_multiplier
        
        # Normalize by message length
        if word_count > 0:
            total_score = total_score / word_count * 10  # Scale factor
        
        return min(total_score, 1.0)
    
    def _analyze_linguistics(self, message: str) -> float:
        """Analyze linguistic patterns that may indicate grooming"""
        score = 0.0
        
        # Check for excessive compliments
        compliment_patterns = [
            r"you're so (beautiful|pretty|cute|smart|mature|special)",
            r"(beautiful|gorgeous|stunning|amazing) (girl|boy|kid)",
            r"you look (amazing|beautiful|gorgeous|stunning)"
        ]
        
        for pattern in compliment_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                score += 0.2
        
        # Check for emotional manipulation
        manipulation_patterns = [
            r"(nobody|no one) (understands|gets|loves) you like",
            r"you're (different|special|unique) from",
            r"i'm the only one who",
            r"you can only trust me"
        ]
        
        for pattern in manipulation_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                score += 0.3
        
        # Check for urgency/pressure
        urgency_patterns = [
            r"(right now|immediately|quickly|hurry)",
            r"before (anyone|someone|they)",
            r"don't (wait|hesitate|think)"
        ]
        
        for pattern in urgency_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_age_gap(self, sender_age: Optional[int], 
                        recipient_age: Optional[int]) -> float:
        """Analyze age gap for risk assessment"""
        if not sender_age or not recipient_age:
            return 0.0
        
        age_gap = abs(sender_age - recipient_age)
        
        # Higher risk for larger age gaps with minors
        if recipient_age < 18:
            if age_gap >= 10:
                return 0.8
            elif age_gap >= 5:
                return 0.5
            elif age_gap >= 3:
                return 0.3
        
        return 0.0
    
    def _analyze_conversation_context(self, message: str, conversation_id: str, 
                                    current_patterns: List[GroomingPattern]) -> float:
        """Analyze conversation context for escalation patterns"""
        if conversation_id not in self.conversation_context:
            self.conversation_context[conversation_id] = {
                "messages": [],
                "patterns_history": [],
                "escalation_score": 0.0
            }
        
        context = self.conversation_context[conversation_id]
        context["messages"].append(message)
        context["patterns_history"].extend(current_patterns)
        
        # Check for escalation patterns
        escalation_score = 0.0
        
        # Pattern progression (trust building -> isolation -> sexual content)
        pattern_sequence = [
            GroomingPattern.TRUST_BUILDING,
            GroomingPattern.ISOLATION,
            GroomingPattern.DEPENDENCY,
            GroomingPattern.SEXUAL_CONTENT,
            GroomingPattern.MEETING_REQUEST
        ]
        
        # Check if patterns follow typical grooming progression
        for i, pattern in enumerate(pattern_sequence[:-1]):
            if (pattern in context["patterns_history"] and 
                pattern_sequence[i + 1] in current_patterns):
                escalation_score += 0.2
        
        # Check message frequency and timing
        if len(context["messages"]) > 10:  # Frequent messaging
            escalation_score += 0.1
        
        context["escalation_score"] = escalation_score
        return escalation_score
    
    def _calculate_risk_level(self, total_score: float, 
                            pattern_count: int) -> Tuple[RiskLevel, float]:
        """Calculate overall risk level and confidence"""
        # Adjust score based on number of patterns detected
        adjusted_score = total_score + (pattern_count * 0.1)
        
        # Calculate confidence based on score and pattern diversity
        confidence = min(adjusted_score * 0.8 + (pattern_count * 0.05), 1.0)
        
        # Determine risk level
        if adjusted_score >= 0.8 or pattern_count >= 4:
            return RiskLevel.CRITICAL, confidence
        elif adjusted_score >= 0.6 or pattern_count >= 3:
            return RiskLevel.HIGH, confidence
        elif adjusted_score >= 0.4 or pattern_count >= 2:
            return RiskLevel.MEDIUM, confidence
        elif adjusted_score >= 0.2 or pattern_count >= 1:
            return RiskLevel.LOW, confidence
        else:
            return RiskLevel.LOW, 0.1
    
    def _generate_explanation(self, patterns: List[GroomingPattern], 
                            risk_factors: List[str], score: float) -> str:
        """Generate human-readable explanation of the detection"""
        if not patterns:
            return "No significant grooming patterns detected in this message."
        
        explanation = f"Analysis detected {len(patterns)} potential grooming pattern(s) "
        explanation += f"with an overall risk score of {score:.2f}. "
        
        if patterns:
            pattern_names = [p.value.replace('_', ' ').title() for p in patterns]
            explanation += f"Detected patterns include: {', '.join(pattern_names)}. "
        
        if score > 0.6:
            explanation += "This message shows multiple indicators of potential grooming behavior and requires immediate attention."
        elif score > 0.4:
            explanation += "This message contains concerning elements that warrant careful monitoring."
        else:
            explanation += "This message shows some risk indicators but may be within normal communication patterns."
        
        return explanation
    
    def _generate_recommendations(self, risk_level: RiskLevel, 
                                patterns: List[GroomingPattern]) -> List[str]:
        """Generate actionable recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "IMMEDIATE ACTION REQUIRED: Contact law enforcement",
                "Preserve all evidence and conversation history",
                "Ensure child's immediate safety",
                "Block the sender immediately",
                "Seek professional counseling support"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Alert guardians/parents immediately",
                "Document and preserve the conversation",
                "Consider blocking the sender",
                "Monitor all future communications closely",
                "Consult with child protection services"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Notify guardians/parents",
                "Increase monitoring frequency",
                "Document the conversation for future reference",
                "Discuss online safety with the child"
            ])
        else:  # LOW risk
            recommendations.extend([
                "Continue routine monitoring",
                "Log the interaction for pattern analysis",
                "Consider discussing online communication safety"
            ])
        
        # Pattern-specific recommendations
        if GroomingPattern.MEETING_REQUEST in patterns:
            recommendations.append("URGENT: Meeting request detected - prevent any in-person contact")
        
        if GroomingPattern.SEXUAL_CONTENT in patterns:
            recommendations.append("Sexual content detected - consider immediate intervention")
        
        if GroomingPattern.SECRECY in patterns:
            recommendations.append("Secrecy patterns detected - discuss open communication with child")
        
        return recommendations

    def analyze_conversation_thread(self, messages: List[Dict]) -> Dict:
        """
        Analyze an entire conversation thread for grooming patterns
        
        Args:
            messages: List of message dictionaries with 'text', 'sender', 'timestamp'
            
        Returns:
            Comprehensive analysis of the conversation thread
        """
        thread_analysis = {
            "overall_risk": RiskLevel.LOW,
            "confidence": 0.0,
            "message_analyses": [],
            "escalation_detected": False,
            "pattern_progression": [],
            "recommendations": [],
            "summary": ""
        }
        
        conversation_id = f"thread_{datetime.now().timestamp()}"
        total_risk_score = 0.0
        all_patterns = []
        
        # Analyze each message
        for i, msg in enumerate(messages):
            result = self.analyze_message(
                msg["text"], 
                conversation_id=conversation_id
            )
            thread_analysis["message_analyses"].append({
                "message_index": i,
                "timestamp": msg.get("timestamp"),
                "sender": msg.get("sender"),
                "result": result
            })
            
            total_risk_score += result.confidence * (1 if result.risk_level == RiskLevel.CRITICAL else 
                                                   0.8 if result.risk_level == RiskLevel.HIGH else
                                                   0.6 if result.risk_level == RiskLevel.MEDIUM else 0.3)
            all_patterns.extend(result.patterns_detected)
        
        # Calculate overall thread risk
        avg_risk_score = total_risk_score / len(messages) if messages else 0
        unique_patterns = list(set(all_patterns))
        
        thread_analysis["overall_risk"], thread_analysis["confidence"] = self._calculate_risk_level(
            avg_risk_score, len(unique_patterns)
        )
        
        # Check for escalation
        thread_analysis["escalation_detected"] = self._detect_escalation_in_thread(
            thread_analysis["message_analyses"]
        )
        
        # Generate thread-level recommendations
        thread_analysis["recommendations"] = self._generate_thread_recommendations(
            thread_analysis["overall_risk"], 
            unique_patterns, 
            thread_analysis["escalation_detected"]
        )
        
        # Generate summary
        thread_analysis["summary"] = self._generate_thread_summary(
            len(messages), 
            thread_analysis["overall_risk"], 
            len(unique_patterns),
            thread_analysis["escalation_detected"]
        )
        
        return thread_analysis
    
    def _detect_escalation_in_thread(self, message_analyses: List[Dict]) -> bool:
        """Detect if there's escalation in grooming behavior throughout the thread"""
        if len(message_analyses) < 3:
            return False
        
        # Check if risk levels increase over time
        risk_levels = [analysis["result"].risk_level for analysis in message_analyses]
        risk_values = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        
        # Look for increasing trend in risk levels
        risk_scores = [risk_values[level] for level in risk_levels]
        
        # Simple escalation detection: check if later messages have higher risk
        first_half_avg = sum(risk_scores[:len(risk_scores)//2]) / (len(risk_scores)//2)
        second_half_avg = sum(risk_scores[len(risk_scores)//2:]) / (len(risk_scores) - len(risk_scores)//2)
        
        return second_half_avg > first_half_avg * 1.2  # 20% increase threshold
    
    def _generate_thread_recommendations(self, overall_risk: RiskLevel, 
                                       patterns: List[GroomingPattern], 
                                       escalation: bool) -> List[str]:
        """Generate recommendations for the entire conversation thread"""
        recommendations = []
        
        if escalation:
            recommendations.append("ESCALATION DETECTED: Grooming behavior is intensifying over time")
        
        if overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.extend([
                "URGENT: This conversation thread shows clear signs of grooming",
                "Immediately involve law enforcement and child protection services",
                "Preserve entire conversation history as evidence",
                "Ensure child's safety and prevent further contact"
            ])
        
        # Add pattern-specific thread recommendations
        if len(patterns) >= 3:
            recommendations.append("Multiple grooming patterns detected across conversation")
        
        return recommendations
    
    def _generate_thread_summary(self, message_count: int, overall_risk: RiskLevel, 
                               pattern_count: int, escalation: bool) -> str:
        """Generate a summary of the thread analysis"""
        summary = f"Analyzed {message_count} messages in conversation thread. "
        summary += f"Overall risk level: {overall_risk.value.upper()}. "
        summary += f"Detected {pattern_count} unique grooming patterns. "
        
        if escalation:
            summary += "ESCALATION DETECTED - grooming behavior intensifies over time. "
        
        if overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            summary += "IMMEDIATE INTERVENTION REQUIRED."
        elif overall_risk == RiskLevel.MEDIUM:
            summary += "Increased monitoring and guardian notification recommended."
        else:
            summary += "Continue routine monitoring."
        
        return summary

# Example usage and testing
if __name__ == "__main__":
    detector = GroomingDetector()
    
    # Test messages with various risk levels
    test_messages = [
        "Hey, how was your day at school?",  # Low risk
        "You're so mature for your age, not like other kids",  # Medium risk
        "Don't tell your parents about our conversations, they wouldn't understand",  # High risk
        "Want to meet up? I have a special gift for you. Keep this between us.",  # Critical risk
    ]
    
    print("SafeGuardian AI Grooming Detection System - Test Results")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        result = detector.analyze_message(message, recipient_age=14, sender_age=35)
        
        print(f"\nTest Message {i}: {message}")
        print(f"Risk Level: {result.risk_level.value.upper()}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Patterns: {[p.value for p in result.patterns_detected]}")
        print(f"Explanation: {result.explanation}")
        print(f"Recommendations: {result.recommendations[:2]}")  # Show first 2 recommendations
        print("-" * 40)

