#!/usr/bin/env python3
"""
Test script for meeting analytics integration.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.main import MoMGenerator

def test_analytics_integration():
    """Test the analytics integration with a sample transcript."""
    
    # Sample meeting transcript
    sample_transcript = """
    John Smith: Good morning everyone, let's start our weekly team meeting. Today we need to discuss the project timeline and budget allocation.
    
    Sarah Johnson: Thanks John. I've reviewed the current project status and we're about 20% behind schedule on the development phase.
    
    Mike Davis: That's concerning. What are the main blockers we're facing?
    
    Sarah Johnson: The main issues are resource allocation and some technical challenges with the new API integration. We need to assign more developers to this task.
    
    John Smith: I agree. Mike, can you take the lead on reassigning team members? We need this completed by next Friday.
    
    Mike Davis: Absolutely. I'll work with HR to get two additional developers assigned to the project by Wednesday.
    
    Sarah Johnson: That would be great. Also, we should schedule a follow-up meeting next week to review progress.
    
    John Smith: Good idea. Let's schedule that for next Tuesday at 2 PM. Any other concerns?
    
    Mike Davis: Just one thing - we need to update the client on the delay. Should we send them a status report?
    
    John Smith: Yes, I'll handle that. I'll send them an update by end of day today.
    
    Sarah Johnson: Perfect. I think that covers everything for today.
    
    John Smith: Great, thanks everyone. Meeting adjourned.
    """
    
    try:
        # Initialize MoM generator
        print("Initializing MoM Generator...")
        generator = MoMGenerator()
        
        # Test analytics generation
        print("Generating meeting analytics...")
        analytics = generator.get_meeting_analytics(sample_transcript)
        
        print("\n=== MEETING ANALYTICS RESULTS ===")
        
        # Display speaking time distribution
        if 'speaking_time' in analytics:
            print("\nSpeaking Time Distribution:")
            for speaker, percentage in analytics['speaking_time'].items():
                if speaker != "Unknown":
                    print(f"  {speaker}: {percentage:.1f}%")
        
        # Display topics
        if 'topics' in analytics:
            print(f"\nMain Topics ({len(analytics['topics'])} identified):")
            for i, topic in enumerate(analytics['topics'][:5], 1):
                print(f"  {i}. {topic['topic']} (relevance: {topic.get('relevance', 0):.1f}%)")
        
        # Display efficiency metrics
        if 'efficiency_metrics' in analytics:
            metrics = analytics['efficiency_metrics']
            print(f"\nEfficiency Metrics:")
            print(f"  Overall Efficiency Score: {metrics.get('efficiency_score', 0):.1f}/100")
            print(f"  Participation Balance: {metrics.get('participation_balance', 0):.1f}/100")
            print(f"  Engagement Score: {metrics.get('engagement_score', 0):.1f}/100")
            print(f"  Content Density: {metrics.get('content_density', 0):.1f}%")
        
        # Display suggestions
        if 'suggestions' in analytics:
            print(f"\nImprovement Suggestions ({len(analytics['suggestions'])} total):")
            for i, suggestion in enumerate(analytics['suggestions'][:3], 1):
                print(f"  {i}. {suggestion['suggestion']}")
                if 'reason' in suggestion:
                    print(f"     Reason: {suggestion['reason']}")
        
        # Test full MoM generation with analytics
        print("\n=== TESTING FULL MOM WITH ANALYTICS ===")
        
        options = {
            'include_analytics': True,
            'include_sentiment': True,
            'structured_output': True
        }
        
        mom_with_analytics = generator.generate_mom_with_analytics(sample_transcript, options)
        
        print(f"\nMoM Data Keys: {list(mom_with_analytics.keys())}")
        
        if 'analytics' in mom_with_analytics:
            print("✓ Analytics successfully integrated into MoM data")
        else:
            print("✗ Analytics not found in MoM data")
        
        if 'metadata' in mom_with_analytics and 'analytics_summary' in mom_with_analytics['metadata']:
            print("✓ Analytics summary added to metadata")
        else:
            print("✗ Analytics summary not found in metadata")
        
        print("\n=== TEST COMPLETED SUCCESSFULLY ===")
        return True
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analytics_integration()
    sys.exit(0 if success else 1)