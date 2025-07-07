from datetime import datetime
from enum import Enum
from src.models import db, generate_uuid

class AnalysisType(Enum):
    GROOMING_DETECTION = 'grooming_detection'
    SENTIMENT_ANALYSIS = 'sentiment_analysis'
    INTENT_CLASSIFICATION = 'intent_classification'
    ENTITY_EXTRACTION = 'entity_extraction'
    TOXICITY_DETECTION = 'toxicity_detection'
    AGE_VERIFICATION = 'age_verification'
    RISK_ASSESSMENT = 'risk_assessment'

class SentimentType(Enum):
    POSITIVE = 'positive'
    NEGATIVE = 'negative'
    NEUTRAL = 'neutral'
    MIXED = 'mixed'

class AIAnalysis(db.Model):
    __tablename__ = 'ai_analysis'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    message_id = db.Column(db.String(36), db.ForeignKey('messages.id'), nullable=True)
    session_id = db.Column(db.String(36), db.ForeignKey('monitoring_sessions.id'), nullable=True)
    analysis_type = db.Column(db.Enum(AnalysisType), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    model_version = db.Column(db.String(50), nullable=False)
    confidence_score = db.Column(db.Numeric(5, 4), nullable=False)
    risk_score = db.Column(db.Numeric(3, 2), nullable=False)
    sentiment = db.Column(db.Enum(SentimentType), nullable=True)
    intent = db.Column(db.String(255), nullable=True)
    entities = db.Column(db.JSON, default=lambda: [])
    topics = db.Column(db.JSON, default=lambda: [])
    language = db.Column(db.String(10), nullable=True)
    toxicity_score = db.Column(db.Numeric(5, 4), nullable=True)
    grooming_indicators = db.Column(db.JSON, default=lambda: [])
    risk_factors = db.Column(db.JSON, default=lambda: [])
    recommendations = db.Column(db.JSON, default=lambda: [])
    raw_output = db.Column(db.JSON, nullable=True)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    message = db.relationship('Message', back_populates='ai_analyses')
    session = db.relationship('MonitoringSession', back_populates='ai_analyses')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('confidence_score >= 0.0000 AND confidence_score <= 1.0000', name='chk_confidence_score'),
        db.CheckConstraint('risk_score >= 0.00 AND risk_score <= 10.00', name='chk_risk_score'),
        db.CheckConstraint('toxicity_score IS NULL OR (toxicity_score >= 0.0000 AND toxicity_score <= 1.0000)', name='chk_toxicity_score'),
        db.CheckConstraint('(message_id IS NOT NULL AND session_id IS NULL) OR (message_id IS NULL AND session_id IS NOT NULL)', name='chk_analysis_target')
    )
    
    def get_risk_level(self):
        """Get risk level based on risk score."""
        if self.risk_score >= 8.0:
            return 'critical'
        elif self.risk_score >= 6.0:
            return 'high'
        elif self.risk_score >= 4.0:
            return 'medium'
        elif self.risk_score >= 2.0:
            return 'low'
        else:
            return 'minimal'
    
    def get_confidence_level(self):
        """Get confidence level based on confidence score."""
        if self.confidence_score >= 0.9:
            return 'very_high'
        elif self.confidence_score >= 0.8:
            return 'high'
        elif self.confidence_score >= 0.7:
            return 'medium'
        elif self.confidence_score >= 0.6:
            return 'low'
        else:
            return 'very_low'
    
    def extract_grooming_patterns(self):
        """Extract specific grooming patterns from the analysis."""
        patterns = []
        
        # Check for common grooming indicators
        if self.grooming_indicators:
            for indicator in self.grooming_indicators:
                if indicator.get('confidence', 0) > 0.7:
                    patterns.append({
                        'pattern': indicator.get('type'),
                        'description': indicator.get('description'),
                        'confidence': indicator.get('confidence'),
                        'severity': self._get_pattern_severity(indicator.get('type'))
                    })
        
        # Check entities for concerning content
        if self.entities:
            for entity in self.entities:
                if entity.get('label') in ['PERSON', 'LOCATION', 'PHONE', 'EMAIL']:
                    if entity.get('confidence', 0) > 0.8:
                        patterns.append({
                            'pattern': 'personal_info_sharing',
                            'description': f"Potential {entity.get('label').lower()} sharing: {entity.get('text')}",
                            'confidence': entity.get('confidence'),
                            'severity': 'medium'
                        })
        
        return patterns
    
    def _get_pattern_severity(self, pattern_type):
        """Get severity level for grooming pattern type."""
        severity_map = {
            'isolation_attempt': 'high',
            'secret_keeping': 'high',
            'gift_offering': 'medium',
            'meeting_request': 'critical',
            'personal_questions': 'medium',
            'compliment_bombing': 'low',
            'trust_building': 'low',
            'boundary_testing': 'medium',
            'sexual_content': 'critical',
            'threat_making': 'critical'
        }
        return severity_map.get(pattern_type, 'low')
    
    def generate_alert_if_needed(self):
        """Generate alert if analysis indicates high risk."""
        from src.models.alert import Alert, AlertType, AlertSeverity
        
        # Don't create alerts for low-risk or low-confidence analyses
        if self.risk_score < 5.0 or self.confidence_score < 0.7:
            return None
        
        # Determine alert type based on analysis
        alert_type = self._determine_alert_type()
        if not alert_type:
            return None
        
        # Determine severity
        severity = self._determine_alert_severity()
        
        # Create alert
        alert = Alert(
            session_id=self.session_id,
            message_id=self.message_id,
            child_id=self.session.child_id if self.session else self.message.session.child_id,
            guardian_id=self.session.child.guardian_id if self.session else self.message.session.child.guardian_id,
            alert_type=alert_type,
            severity=severity,
            title=self._generate_alert_title(),
            description=self._generate_alert_description(),
            risk_score=self.risk_score,
            confidence_score=self.confidence_score,
            triggered_by={
                'ai_analysis_id': self.id,
                'model_name': self.model_name,
                'analysis_type': self.analysis_type.value
            },
            evidence={
                'grooming_indicators': self.grooming_indicators,
                'risk_factors': self.risk_factors,
                'entities': self.entities,
                'sentiment': self.sentiment.value if self.sentiment else None,
                'toxicity_score': float(self.toxicity_score) if self.toxicity_score else None
            }
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return alert
    
    def _determine_alert_type(self):
        """Determine alert type based on analysis results."""
        from src.models.alert import AlertType
        
        if self.analysis_type == AnalysisType.GROOMING_DETECTION and self.risk_score >= 6.0:
            return AlertType.GROOMING_DETECTED
        elif self.toxicity_score and self.toxicity_score >= 0.8:
            return AlertType.INAPPROPRIATE_CONTENT
        elif self.entities and any(e.get('label') in ['PHONE', 'EMAIL', 'ADDRESS'] for e in self.entities):
            return AlertType.PERSONAL_INFO_REQUEST
        elif self.grooming_indicators and any(g.get('type') == 'meeting_request' for g in self.grooming_indicators):
            return AlertType.MEETING_REQUEST
        elif self.sentiment == SentimentType.NEGATIVE and self.risk_score >= 5.0:
            return AlertType.CYBERBULLYING
        
        return None
    
    def _determine_alert_severity(self):
        """Determine alert severity based on risk score and indicators."""
        from src.models.alert import AlertSeverity
        
        if self.risk_score >= 9.0:
            return AlertSeverity.EMERGENCY
        elif self.risk_score >= 7.0:
            return AlertSeverity.CRITICAL
        elif self.risk_score >= 5.0:
            return AlertSeverity.HIGH
        elif self.risk_score >= 3.0:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW
    
    def _generate_alert_title(self):
        """Generate alert title based on analysis."""
        if self.analysis_type == AnalysisType.GROOMING_DETECTION:
            return f"Potential Grooming Detected (Risk: {self.risk_score}/10)"
        elif self.toxicity_score and self.toxicity_score >= 0.8:
            return f"Inappropriate Content Detected (Toxicity: {self.toxicity_score:.2f})"
        else:
            return f"Suspicious Activity Detected (Risk: {self.risk_score}/10)"
    
    def _generate_alert_description(self):
        """Generate alert description based on analysis."""
        description_parts = []
        
        if self.grooming_indicators:
            indicators = [g.get('type', 'unknown') for g in self.grooming_indicators]
            description_parts.append(f"Grooming indicators detected: {', '.join(indicators)}")
        
        if self.risk_factors:
            factors = [rf.get('type', 'unknown') for rf in self.risk_factors]
            description_parts.append(f"Risk factors: {', '.join(factors)}")
        
        if self.sentiment and self.sentiment != SentimentType.NEUTRAL:
            description_parts.append(f"Sentiment: {self.sentiment.value}")
        
        if self.toxicity_score and self.toxicity_score > 0.5:
            description_parts.append(f"Toxicity score: {self.toxicity_score:.2f}")
        
        description_parts.append(f"Confidence: {self.confidence_score:.2f}")
        description_parts.append(f"Model: {self.model_name} v{self.model_version}")
        
        return ". ".join(description_parts)
    
    def to_dict(self, include_raw_output=False):
        """Convert AI analysis to dictionary representation."""
        data = {
            'id': self.id,
            'message_id': self.message_id,
            'session_id': self.session_id,
            'analysis_type': self.analysis_type.value,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'confidence_score': float(self.confidence_score),
            'confidence_level': self.get_confidence_level(),
            'risk_score': float(self.risk_score),
            'risk_level': self.get_risk_level(),
            'sentiment': self.sentiment.value if self.sentiment else None,
            'intent': self.intent,
            'entities': self.entities,
            'topics': self.topics,
            'language': self.language,
            'toxicity_score': float(self.toxicity_score) if self.toxicity_score else None,
            'grooming_indicators': self.grooming_indicators,
            'grooming_patterns': self.extract_grooming_patterns(),
            'risk_factors': self.risk_factors,
            'recommendations': self.recommendations,
            'processing_time_ms': self.processing_time_ms,
            'created_at': self.created_at.isoformat()
        }
        
        if include_raw_output:
            data['raw_output'] = self.raw_output
        
        return data
    
    def __repr__(self):
        return f'<AIAnalysis {self.analysis_type.value} (Risk: {self.risk_score})>'

