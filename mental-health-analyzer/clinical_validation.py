import logging

def validate_clinical_assessment(domains_data):
    """Validate and adjust the clinical assessment for consistency and accuracy."""
    
    logger = logging.getLogger(__name__)
    validated_data = domains_data.copy()
    
    # Known clinical correlations between domains (simplified)
    domain_correlations = {
        "Depression": ["Suicidal Ideation", "Sleep Problems", "Memory"],
        "Anxiety": ["Sleep Problems", "Somatic Symptoms"],
        "Psychosis": ["Dissociation"],
        "Mania": ["Sleep Problems"]
    }
    
    # Get domain scores dict for easier reference
    domain_scores = {domain["name"]: {
        "total": domain["total"],
        "max_score": sum([4] * len(domain["scores"])),  # 4 is max score per question
        "percentage": domain["total"] / sum([4] * len(domain["scores"])) * 100 if sum([4] * len(domain["scores"])) > 0 else 0,
        "scores": domain["scores"]
    } for domain in validated_data}
    
    # Check for clinical inconsistencies
    for primary_domain, related_domains in domain_correlations.items():
        if primary_domain not in domain_scores:
            continue
            
        primary_percentage = domain_scores[primary_domain]["percentage"]
        
        # If primary domain has high score, check related domains
        if primary_percentage > 50:  # More than half the max score
            for related_domain in related_domains:
                if related_domain not in domain_scores:
                    continue
                    
                related_percentage = domain_scores[related_domain]["percentage"]
                
                # Flag potential inconsistency if related domain is much lower
                if related_percentage < 15 and primary_percentage > 60:
                    logger.warning(
                        f"Clinical inconsistency detected: {primary_domain} is high ({primary_percentage:.1f}%) "
                        f"but {related_domain} is very low ({related_percentage:.1f}%)"
                    )
                    
                    # Add a note about this inconsistency
                    for domain in validated_data:
                        if domain["name"] == related_domain:
                            if "clinical_notes" not in domain:
                                domain["clinical_notes"] = []
                            domain["clinical_notes"].append(
                                f"Potential underestimation - high {primary_domain} scores often correlate with {related_domain} symptoms"
                            )
    
    # Check for extreme outliers in individual question scores within domains
    for domain in validated_data:
        scores = domain["scores"]
        if len(scores) > 1:  # Only check domains with multiple questions
            max_score = max(scores)
            min_score = min(scores)
            
            # Check for high variance within domain questions
            if max_score >= 3 and min_score == 0:
                if "clinical_notes" not in domain:
                    domain["clinical_notes"] = []
                domain["clinical_notes"].append(
                    "High variance in question scores may indicate incomplete assessment"
                )
    
    # Add confidence ratings
    for domain in validated_data:
        # Calculate confidence based on evidence quality
        evidence_quality = []
        for ev in domain["evidence"]:
            if "No explicit evidence" in ev or not ev:
                evidence_quality.append(0)
            elif len(ev) < 20:
                evidence_quality.append(1)
            else:
                evidence_quality.append(2)
        
        avg_evidence_quality = sum(evidence_quality) / len(evidence_quality) if evidence_quality else 0
        max_score = max(domain["scores"]) if domain["scores"] else 0
        
        # Higher confidence for domains with better evidence
        if avg_evidence_quality > 1.5:
            domain["confidence"] = "High"
        elif avg_evidence_quality > 0.5 or max_score >= 3:
            domain["confidence"] = "Medium"
        else:
            domain["confidence"] = "Low"
    
    return validated_data