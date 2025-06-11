#!/usr/bin/env python3
"""
Standalone Dashboard Generator - Whop Store Ready

Generates HTML dashboard for embedding in Whop store.
"""

from dashboard import generate_dashboard

def main():
    """Generate dashboard and open in browser"""
    print("🌐 Generating MLB Predictor Dashboard...")
    print("📊 Optimized for Whop store embedding")
    
    success = generate_dashboard('mlb_dashboard.html', open_browser=True)
    
    if success:
        print("\n✅ Dashboard generated successfully!")
        print("📄 File: mlb_dashboard.html")
        print("🔗 Ready for Whop store embedding")
        print("\n📝 Integration Instructions:")
        print("1. Upload mlb_dashboard.html to your web server")
        print("2. Use iframe to embed in Whop store:")
        print('   <iframe src="your-server/mlb_dashboard.html" width="100%" height="800px"></iframe>')
        print("3. Set auto-refresh for live updates")
    else:
        print("❌ Dashboard generation failed")

if __name__ == "__main__":
    main()
