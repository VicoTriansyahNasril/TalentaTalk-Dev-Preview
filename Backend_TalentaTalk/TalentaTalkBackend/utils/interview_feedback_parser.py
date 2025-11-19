# TalentaTalkBackend/utils/interview_feedback_parser.py - FINAL IMPROVED VERSION

import re
import json
from typing import Dict, List

class InterviewFeedbackParser:
    @staticmethod
    def parse_feedback_to_components(feedback_text: str) -> Dict[str, str]:
        if not feedback_text or not feedback_text.strip():
            return {
                "strength": "Not available",
                "weakness": "Not available",
                "performance": "Not available"
            }
        
        feedback_text = feedback_text.strip()

        if feedback_text.startswith('{') and feedback_text.endswith('}'):
            try:
                data = json.loads(feedback_text)
                return {
                    "strength": data.get("strength", "Not specified"),
                    "weakness": data.get("weakness", "Not specified"),
                    "performance": data.get("performance", "Not specified")
                }
            except json.JSONDecodeError:
                pass

        strength = InterviewFeedbackParser._extract_section(
            feedback_text,
            ["STRENGTHS:", "(STRENGTHS)", "STRENGTH:"]
        )
        weakness = InterviewFeedbackParser._extract_section(
            feedback_text,
            ["AREAS FOR IMPROVEMENT:", "(WEAKNESS)", "WEAKNESS:"]
        )
        performance = InterviewFeedbackParser._extract_section(
            feedback_text,
            ["OVERALL PERFORMANCE:", "(PERFORMANCE)", "PERFORMANCE:"]
        )

        if strength or weakness or performance:
            return {
                "strength": strength or "Not evaluated",
                "weakness": weakness or "Not evaluated",
                "performance": performance or "Not evaluated"
            }

        strength_match = re.search(r'strength:\s*([^|]+)', feedback_text, re.IGNORECASE)
        weakness_match = re.search(r'weakness:\s*([^|]+)', feedback_text, re.IGNORECASE)
        performance_match = re.search(r'performance:\s*([^|]+)', feedback_text, re.IGNORECASE)
        
        if strength_match and weakness_match and performance_match:
            return {
                "strength": strength_match.group(1).strip(),
                "weakness": weakness_match.group(1).strip(),
                "performance": performance_match.group(1).strip()
            }
            
        return {
            "strength": "Not evaluated",
            "weakness": "Not evaluated",
            "performance": feedback_text
        }
    
    @staticmethod
    def _extract_section(text: str, headers: List[str]) -> str:
        try:
            header_pattern = '|'.join([re.escape(h) for h in headers])
            header_match = re.search(header_pattern, text, re.IGNORECASE)
            
            if not header_match:
                return ""

            start_pos = header_match.end()
            remaining_text = text[start_pos:]

            all_headers = [
                "STRENGTHS:", "(STRENGTHS)", "STRENGTH:",
                "AREAS FOR IMPROVEMENT:", "(WEAKNESS)", "WEAKNESS:",
                "OVERALL PERFORMANCE:", "(PERFORMANCE)", "PERFORMANCE:",
                "INTERVIEW STATISTICS:"
            ]
            
            next_section_pos = len(remaining_text)
            
            for next_header in all_headers:
                next_match = re.search(re.escape(next_header), remaining_text, re.IGNORECASE)
                if next_match:
                    next_section_pos = min(next_section_pos, next_match.start())
            
            section_content = remaining_text[:next_section_pos]
            
            # Clean up content
            cleaned_content = re.sub(r'^[•\-\*:\s]+', '', section_content.strip())
            cleaned_content = cleaned_content.replace('\n', ' ').strip()
            
            return cleaned_content if len(cleaned_content) >= 5 else "Not evaluated"
            
        except Exception as e:
            print(f"Error extracting section with headers {headers}: {e}")
            return "Not evaluated"