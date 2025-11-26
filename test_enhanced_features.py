"""
Test script for enhanced HospAgent features
Run this to verify all new functionality works correctly
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api/enhanced"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_risk_assessment():
    print_section("1. Testing Risk Assessment")
    try:
        response = requests.get(f"{BASE_URL}/risk-assessment")
        data = response.json()
        
        if data['status'] == 'success':
            risk = data['data']
            print(f"✅ Risk Level: {risk['risk_level'].upper()}")
            print(f"✅ Risk Score: {risk['composite_risk_score']}/100")
            print(f"✅ Risk Factors: {', '.join(risk['risk_factors'])}")
            print(f"✅ Surge Multiplier: {risk['predicted_surge_multiplier']:.2f}x")
            return True
        else:
            print(f"❌ Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_aqi_data():
    print_section("2. Testing AQI Data")
    try:
        response = requests.get(f"{BASE_URL}/aqi/current?city=Mumbai")
        data = response.json()
        
        if data['status'] == 'success':
            aqi = data['data']
            print(f"✅ City: {aqi['city']}")
            print(f"✅ AQI: {aqi['aqi']}")
            print(f"✅ PM2.5: {aqi.get('pm25', 'N/A')}")
            print(f"✅ Source: {aqi['source']}")
            return True
        else:
            print(f"❌ Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_weather_forecast():
    print_section("3. Testing Weather Forecast")
    try:
        response = requests.get(f"{BASE_URL}/weather/forecast?city=Mumbai&days=7")
        data = response.json()
        
        if data['status'] == 'success':
            forecast = data['data']
            print(f"✅ Forecast for next {len(forecast)} days:")
            for day in forecast[:3]:  # Show first 3 days
                print(f"   {day['date']}: {day['temperature']}°C, {day['description']}")
            return True
        else:
            print(f"❌ Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_festivals():
    print_section("4. Testing Festival Calendar")
    try:
        response = requests.get(f"{BASE_URL}/festivals/upcoming?days_ahead=90")
        data = response.json()
        
        if data['status'] == 'success':
            festivals = data['data']
            print(f"✅ Upcoming festivals: {len(festivals)}")
            for fest in festivals[:3]:  # Show first 3
                print(f"   {fest['name']} - {fest['days_until']} days away")
                print(f"      Expected surge: {fest['expected_surge']}x")
                print(f"      Health impact: {fest['health_impact']}")
            return True
        else:
            print(f"❌ Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_epidemic_trends():
    print_section("5. Testing Epidemic Surveillance")
    try:
        response = requests.get(f"{BASE_URL}/epidemics/trends")
        data = response.json()
        
        if data['status'] == 'success':
            epidemics = data['data']
            print(f"✅ Total cases this week: {epidemics['total_cases']}")
            print(f"✅ Active outbreaks: {len(epidemics['active_outbreaks'])}")
            for outbreak in epidemics['active_outbreaks']:
                print(f"   {outbreak['name']}: {outbreak['cases_this_week']} cases ({outbreak['trend']})")
            return True
        else:
            print(f"❌ Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_auto_advisories():
    print_section("6. Testing Auto-Generated Advisories")
    try:
        response = requests.get(f"{BASE_URL}/advisories/auto-generate")
        data = response.json()
        
        if data['status'] == 'success':
            result = data['data']
            advisories = result['advisories']
            print(f"✅ Generated {result['total_advisories']} advisories")
            print(f"✅ Risk level: {result['risk_level']}")
            
            for i, adv in enumerate(advisories[:3], 1):  # Show first 3
                print(f"\n   Advisory {i}: {adv['title']}")
                print(f"      Severity: {adv['severity']}")
                print(f"      Channels: {', '.join(adv['channels'])}")
                print(f"      Target: {', '.join(adv['target_audience'])}")
            return True
        else:
            print(f"❌ Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_coordination_status():
    print_section("7. Testing Agentic Coordination")
    try:
        response = requests.get(f"{BASE_URL}/coordination/status")
        data = response.json()
        
        if data['status'] == 'success':
            coord = data['data']
            print(f"✅ Registered agents: {len(coord['registered_agents'])}")
            print(f"✅ Active subscriptions: {sum(coord['active_subscriptions'].values())}")
            print(f"✅ Recent events: {len(coord['recent_events'])}")
            print(f"✅ Coordination rules: {len(coord['coordination_rules'])}")
            return True
        else:
            print(f"❌ Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_trigger_event():
    print_section("8. Testing Event Triggering")
    try:
        payload = {
            "event_type": "SURGE_PREDICTED",
            "data": {
                "predicted_patients": 250,
                "department": "ER",
                "confidence": 0.92
            },
            "priority": 9
        }
        
        response = requests.post(
            f"{BASE_URL}/coordination/trigger-event",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['status'] == 'success':
            event = data['data']['event']
            print(f"✅ Event triggered: {event['event_type']}")
            print(f"✅ Priority: {event['priority']}")
            print(f"✅ Timestamp: {event['timestamp']}")
            return True
        else:
            print(f"❌ Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_enhanced_dashboard():
    print_section("9. Testing Enhanced Dashboard")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/enhanced")
        data = response.json()
        
        if data['status'] == 'success':
            dashboard = data['data']
            print(f"✅ Risk level: {dashboard['risk_assessment']['risk_level']}")
            print(f"✅ Active advisories: {len(dashboard['active_advisories'])}")
            print(f"✅ Active agents: {dashboard['coordination_status']['active_agents']}")
            print(f"✅ Data sources active: {dashboard['system_health']['data_sources_active']}")
            print(f"✅ System healthy: {dashboard['system_health']['agents_coordinating']}")
            return True
        else:
            print(f"❌ Error: {data.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def run_all_tests():
    print("\n" + "🚀 HospAgent Enhanced Features Test Suite")
    print("Testing all new functionality...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Risk Assessment", test_risk_assessment),
        ("AQI Data", test_aqi_data),
        ("Weather Forecast", test_weather_forecast),
        ("Festival Calendar", test_festivals),
        ("Epidemic Surveillance", test_epidemic_trends),
        ("Auto Advisories", test_auto_advisories),
        ("Coordination Status", test_coordination_status),
        ("Event Triggering", test_trigger_event),
        ("Enhanced Dashboard", test_enhanced_dashboard)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\n" + "="*60)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! HospAgent enhanced features are working perfectly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the backend logs for details.")

if __name__ == "__main__":
    print("\n⚠️  Make sure the backend is running on http://localhost:5000")
    input("Press Enter to start tests...")
    run_all_tests()
