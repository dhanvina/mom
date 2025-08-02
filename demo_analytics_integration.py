#!/usr/bin/env python3
"""
Demo script showing the complete meeting analytics integration.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def demo_analytics_integration():
    """Demonstrate the complete analytics integration."""
    
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
    
    print("=== MEETING ANALYTICS INTEGRATION DEMO ===\n")
    
    try:
        # Test 1: Direct Analytics Generation
        print("1. DIRECT ANALYTICS GENERATION")
        print("-" * 40)
        
        from app.analyzer.meeting_analytics import MeetingAnalytics
        
        analytics_engine = MeetingAnalytics()
        analytics = analytics_engine.analyze(sample_transcript)
        
        print(f"✓ Generated analytics with {len(analytics)} main sections")
        print(f"  - Speaking time data for {len(analytics['speaking_time'])} participants")
        print(f"  - Identified {len(analytics['topics'])} topics")
        print(f"  - Generated {len(analytics['suggestions'])} improvement suggestions")
        print(f"  - Overall efficiency score: {analytics['efficiency_metrics']['efficiency_score']:.1f}/100")
        
        # Test 2: Analytics Formatting
        print("\n2. ANALYTICS FORMATTING")
        print("-" * 40)
        
        from app.formatter.analytics_formatter import AnalyticsFormatter
        
        formatter = AnalyticsFormatter()
        
        # Test different formats
        text_output = formatter.format_analytics(analytics, "text")
        html_output = formatter.format_analytics(analytics, "html")
        markdown_output = formatter.format_analytics(analytics, "markdown")
        
        print(f"✓ Generated text format ({len(text_output)} characters)")
        print(f"✓ Generated HTML format ({len(html_output)} characters)")
        print(f"✓ Generated Markdown format ({len(markdown_output)} characters)")
        
        # Test analytics summary
        summary = formatter.format_analytics_summary(analytics)
        print(f"✓ Generated analytics summary with efficiency rating: {summary['efficiency_rating']}")
        
        # Test visualization data
        viz_data = formatter.create_visualization_data(analytics)
        print(f"✓ Generated visualization data with {len(viz_data)} chart types")
        
        # Test 3: MoM Extractor Integration
        print("\n3. MOM EXTRACTOR INTEGRATION")
        print("-" * 40)
        
        from app.extractor.mom_extractor import MoMExtractor
        
        # Test with analytics enabled
        extractor = MoMExtractor(config={})
        
        mom_data = extractor.extract(
            transcript=sample_transcript,
            include_analytics=True,
            include_speakers=True,
            structured_output=True
        )
        
        if 'analytics' in mom_data:
            print("✓ Analytics successfully integrated into MoM extraction")
            print(f"  - Analytics data includes: {list(mom_data['analytics'].keys())}")
        else:
            print("✗ Analytics not found in MoM data")
        
        if 'speakers' in mom_data:
            print(f"✓ Detected {len(mom_data['speakers'])} speakers")
        
        # Test 4: Analytics Integration with MoM Data
        print("\n4. ANALYTICS INTEGRATION WITH MOM DATA")
        print("-" * 40)
        
        # Create sample MoM data
        sample_mom_data = {
            "meeting_title": "Weekly Team Meeting",
            "attendees": ["John Smith", "Sarah Johnson", "Mike Davis"],
            "action_items": [
                "Mike to reassign team members by Wednesday",
                "John to send client update by end of day"
            ],
            "decisions": [
                "Assign two additional developers to the project",
                "Schedule follow-up meeting for next Tuesday at 2 PM"
            ],
            "discussion_points": [
                "Project is 20% behind schedule",
                "Resource allocation issues identified",
                "Technical challenges with API integration"
            ]
        }
        
        # Integrate analytics with MoM data
        integrated_data = formatter.integrate_with_mom_data(sample_mom_data, analytics)
        
        print(f"✓ Integrated analytics with MoM data")
        print(f"  - Original MoM keys: {list(sample_mom_data.keys())}")
        print(f"  - Integrated MoM keys: {list(integrated_data.keys())}")
        
        if 'metadata' in integrated_data and 'analytics_summary' in integrated_data['metadata']:
            print("✓ Analytics summary added to metadata")
        
        # Check if attendees were enhanced with participation data
        if 'attendees' in integrated_data:
            first_attendee = integrated_data['attendees'][0]
            if isinstance(first_attendee, dict) and 'participation_percentage' in first_attendee:
                print("✓ Attendees enhanced with participation data")
            else:
                print("ℹ Attendees not enhanced (may be in simple format)")
        
        # Test 5: Comprehensive Analytics Section
        print("\n5. COMPREHENSIVE ANALYTICS SECTION")
        print("-" * 40)
        
        analytics_section = formatter.create_analytics_section(
            analytics, 
            format_type="text", 
            include_visualizations=True
        )
        
        print(f"✓ Created comprehensive analytics section")
        print(f"  - Section keys: {list(analytics_section.keys())}")
        print(f"  - Content length: {len(analytics_section['content'])} characters")
        
        if 'visualizations' in analytics_section:
            viz_keys = list(analytics_section['visualizations'].keys())
            print(f"  - Visualization types: {viz_keys}")
        
        if 'efficiency_report' in analytics_section:
            report = analytics_section['efficiency_report']
            print(f"  - Efficiency report rating: {report['overall_rating']['rating']}")
        
        # Test 6: Display Sample Results
        print("\n6. SAMPLE ANALYTICS RESULTS")
        print("-" * 40)
        
        print("\nSpeaking Time Distribution:")
        for speaker, percentage in analytics['speaking_time'].items():
            if speaker != "Unknown":
                print(f"  {speaker}: {percentage:.1f}%")
        
        print(f"\nTop 3 Topics:")
        for i, topic in enumerate(analytics['topics'][:3], 1):
            print(f"  {i}. {topic['topic']} ({topic.get('relevance', 0):.1f}%)")
        
        print(f"\nTop 3 Suggestions:")
        for i, suggestion in enumerate(analytics['suggestions'][:3], 1):
            print(f"  {i}. {suggestion['suggestion']}")
        
        print(f"\nEfficiency Metrics:")
        metrics = analytics['efficiency_metrics']
        print(f"  Overall Score: {metrics.get('efficiency_score', 0):.1f}/100")
        print(f"  Participation Balance: {metrics.get('participation_balance', 0):.1f}/100")
        print(f"  Engagement: {metrics.get('engagement_score', 0):.1f}/100")
        
        print("\n=== DEMO COMPLETED SUCCESSFULLY ===")
        return True
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_analytics_integration()
    sys.exit(0 if success else 1)