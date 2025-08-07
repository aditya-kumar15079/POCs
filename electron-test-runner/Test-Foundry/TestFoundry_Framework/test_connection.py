#!/usr/bin/env python3
"""
TestFoundry Framework - Enhanced API Connection Tester
Test your OpenAI or Azure OpenAI connection with detailed diagnostics
"""

import asyncio
import yaml
import sys
import os
import platform
import socket
from pathlib import Path
import ssl
import certifi

# Add src directory to path
sys.path.insert(0, 'src')

def check_system_info():
    """Check and display system information"""
    print("🖥️  System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Python: {platform.python_version()}")
    print(f"   Architecture: {platform.machine()}")
    
    # Check SSL/TLS
    try:
        ssl_version = ssl.OPENSSL_VERSION
        print(f"   SSL Version: {ssl_version}")
    except:
        print("   SSL Version: Unknown")
    
    print()

def check_network_connectivity():
    """Check basic network connectivity"""
    print("🌐 Network Connectivity Check:")
    
    # Test DNS resolution
    try:
        socket.gethostbyname('api.openai.com')
        print("   ✅ DNS resolution: OK")
    except Exception as e:
        print(f"   ❌ DNS resolution: FAILED - {e}")
        return False
    
    # Test basic connectivity
    try:
        sock = socket.create_connection(("api.openai.com", 443), timeout=10)
        sock.close()
        print("   ✅ TCP connection to api.openai.com:443: OK")
    except Exception as e:
        print(f"   ❌ TCP connection: FAILED - {e}")
        return False
    
    # Check proxy settings
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False
    for var in proxy_vars:
        if os.environ.get(var):
            print(f"   🔧 Proxy detected: {var}={os.environ[var]}")
            proxy_found = True
    
    if not proxy_found:
        print("   ℹ️  No proxy detected")
    
    print()
    return True

async def test_openai_simple():
    """Test OpenAI with minimal setup"""
    print("🧪 Testing OpenAI with minimal configuration...")
    
    try:
        import openai
        
        # Load config
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        api_key = config['ai_service']['openai']['api_key']
        model = config['ai_service']['openai'].get('model', 'gpt-3.5-turbo')
        
        # Simple synchronous test first
        print(f"   Using model: {model}")
        print(f"   API key starts with: {api_key[:10]}...")
        
        # Create client with minimal settings
        client = openai.AsyncOpenAI(
            api_key=api_key,
            timeout=30.0,
            max_retries=0
        )
        
        # Test request
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Reply with exactly: TEST_OK"}],
            max_tokens=10,
            temperature=0
        )
        
        if response.choices:
            result = response.choices[0].message.content
            print(f"   ✅ Response received: {result}")
            return True
        else:
            print("   ❌ No response content")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Detailed error analysis
        error_str = str(e).lower()
        if "authentication" in error_str or "401" in error_str:
            print("   💡 SOLUTION: Check your API key")
            print("      - Verify the key is correct in config.yaml")
            print("      - Check your OpenAI account is active")
        elif "connection" in error_str or "timeout" in error_str:
            print("   💡 SOLUTION: Network/Connection issue")
            print("      - Check your internet connection")
            print("      - Try disabling VPN if using one")
            print("      - Check firewall/antivirus settings")
        elif "rate" in error_str or "429" in error_str:
            print("   💡 SOLUTION: Rate limit exceeded")
            print("      - Wait 1 minute and try again")
        elif "ssl" in error_str or "certificate" in error_str:
            print("   💡 SOLUTION: SSL/Certificate issue")
            print("      - Update your system certificates")
            print("      - Try: pip install --upgrade certifi")
        else:
            print("   💡 GENERAL SOLUTIONS:")
            print("      - Update OpenAI package: pip install --upgrade openai")
            print("      - Check your internet connection")
            print("      - Try using a different network")
        
        return False

async def test_with_different_models():
    """Test with different models to isolate issues"""
    print("🎯 Testing different models...")
    
    models_to_test = ['gpt-3.5-turbo', 'gpt-3.5-turbo-0125', 'gpt-4o-mini']
    
    try:
        import openai
        
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        api_key = config['ai_service']['openai']['api_key']
        
        for model in models_to_test:
            try:
                print(f"   Testing {model}...")
                
                client = openai.AsyncOpenAI(api_key=api_key, timeout=20.0)
                
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                
                if response.choices:
                    print(f"   ✅ {model}: OK")
                    return model
                    
            except Exception as e:
                print(f"   ❌ {model}: {e}")
                continue
        
        print("   ❌ All models failed")
        return None
        
    except Exception as e:
        print(f"   ❌ Model testing error: {e}")
        return None

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ config.yaml not found!")
        print("💡 Make sure you're running this from the TestFoundry_Framework directory")
        return None
    except Exception as e:
        print(f"❌ Error loading config.yaml: {e}")
        return None

def validate_config(config):
    """Validate configuration"""
    print("🔧 Configuration Validation:")
    
    issues = []
    
    # Check AI service config
    ai_service = config.get('ai_service', {})
    provider = ai_service.get('provider', '')
    
    if provider == 'openai':
        openai_config = ai_service.get('openai', {})
        api_key = openai_config.get('api_key', '')
        model = openai_config.get('model', '')
        
        print(f"   Provider: {provider}")
        print(f"   Model: {model}")
        print(f"   API Key: {api_key[:20]}..." if len(api_key) > 20 else f"   API Key: {api_key}")
        
        if not api_key:
            issues.append("Missing OpenAI API key")
        elif not api_key.startswith(('sk-', 'sk-proj-')):
            issues.append("Invalid OpenAI API key format")
        
        if not model:
            issues.append("Missing model specification")
        
    else:
        issues.append(f"Unsupported provider: {provider}")
    
    if issues:
        print("   ❌ Configuration issues found:")
        for issue in issues:
            print(f"      - {issue}")
        return False
    else:
        print("   ✅ Configuration looks good")
        return True

async def main():
    """Main test function with comprehensive diagnostics"""
    print("=" * 70)
    print("🚀 TestFoundry Framework - Enhanced Connection Diagnostics")
    print("=" * 70)
    print()
    
    # System information
    check_system_info()
    
    # Load and validate configuration
    config = load_config()
    if not config:
        return
    
    config_valid = validate_config(config)
    print()
    
    if not config_valid:
        print("❌ Fix configuration issues before proceeding")
        return
    
    # Network connectivity check
    network_ok = check_network_connectivity()
    if not network_ok:
        print("❌ Network connectivity issues detected")
        print("💡 Fix network issues before testing API")
        return
    
    # Test sequence
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Simple OpenAI test
    if await test_openai_simple():
        tests_passed += 1
    print()
    
    # Test 2: Model compatibility test
    working_model = await test_with_different_models()
    if working_model:
        tests_passed += 1
        print(f"   💡 Recommended model: {working_model}")
    print()
    
    # Final results
    print("=" * 70)
    print("📊 DIAGNOSTIC RESULTS")
    print("=" * 70)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed >= 1:
        print("🎉 Connection tests SUCCESSFUL!")
        print("✅ You should be able to run the framework")
        print("▶️  Run: python main.py")
        
        if working_model and working_model != config['ai_service']['openai'].get('model'):
            print(f"💡 Consider updating your config.yaml to use model: {working_model}")
    
    else:
        print("❌ ALL TESTS FAILED")
        print("🔧 TROUBLESHOOTING STEPS:")
        print("   1. Check your API key is correct and active")
        print("   2. Verify your internet connection")
        print("   3. Try a different network (mobile hotspot)")
        print("   4. Check firewall/antivirus settings")
        print("   5. Update packages: pip install --upgrade openai")
        print("   6. Contact your IT department about network restrictions")
    
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())#!/usr/bin/env python3
"""
TestFoundry Framework - API Connection Tester
Test your OpenAI or Azure OpenAI connection before running the full framework
"""

import asyncio
import yaml
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, 'src')

async def test_openai_connection(config):
    """Test OpenAI API connection"""
    print("🧪 Testing OpenAI API connection...")
    
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=config['api_key'])
        
        # Test with a simple completion
        response = await client.chat.completions.create(
            model=config.get('model', 'gpt-3.5-turbo'),
            messages=[
                {"role": "user", "content": "Say 'Hello, TestFoundry!' if you can hear me."}
            ],
            max_tokens=50,
            timeout=30
        )
        
        if response.choices:
            result = response.choices[0].message.content
            print(f"✅ OpenAI API connection successful!")
            print(f"📝 Response: {result}")
            return True
        else:
            print("❌ OpenAI API responded but no content received")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Detailed error analysis
        if "authentication" in str(e).lower() or "401" in str(e):
            print("💡 Suggestion: Check your API key is correct and active")
        elif "connection" in str(e).lower() or "timeout" in str(e).lower():
            print("💡 Suggestion: Check your internet connection and firewall settings")
        elif "rate" in str(e).lower() or "429" in str(e):
            print("💡 Suggestion: You've hit rate limits, wait a few minutes")
        elif "billing" in str(e).lower() or "quota" in str(e).lower():
            print("💡 Suggestion: Check your OpenAI billing and credit balance")
        
        return False

async def test_azure_openai_connection(config):
    """Test Azure OpenAI API connection"""
    print("🧪 Testing Azure OpenAI API connection...")
    
    try:
        from openai import AsyncAzureOpenAI
        
        client = AsyncAzureOpenAI(
            api_key=config['api_key'],
            azure_endpoint=config['endpoint'],
            api_version=config.get('api_version', '2024-02-15-preview')
        )
        
        # Test with a simple completion
        response = await client.chat.completions.create(
            model=config['deployment_name'],
            messages=[
                {"role": "user", "content": "Say 'Hello, TestFoundry!' if you can hear me."}
            ],
            max_tokens=50,
            timeout=30
        )
        
        if response.choices:
            result = response.choices[0].message.content
            print(f"✅ Azure OpenAI API connection successful!")
            print(f"📝 Response: {result}")
            return True
        else:
            print("❌ Azure OpenAI API responded but no content received")
            return False
            
    except Exception as e:
        print(f"❌ Azure OpenAI API connection failed: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Detailed error analysis
        if "authentication" in str(e).lower() or "401" in str(e):
            print("💡 Suggestion: Check your API key and Azure endpoint are correct")
        elif "deployment" in str(e).lower() or "404" in str(e):
            print("💡 Suggestion: Check your deployment name is correct and active")
        elif "connection" in str(e).lower() or "timeout" in str(e).lower():
            print("💡 Suggestion: Check your internet connection and Azure endpoint")
        elif "rate" in str(e).lower() or "429" in str(e):
            print("💡 Suggestion: You've hit rate limits, wait a few minutes")
        
        return False

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ config.yaml not found!")
        print("💡 Make sure you're running this from the TestFoundry_Framework directory")
        return None
    except Exception as e:
        print(f"❌ Error loading config.yaml: {e}")
        return None

def print_config_info(config):
    """Print configuration information"""
    ai_service = config.get('ai_service', {})
    provider = ai_service.get('provider', 'unknown')
    
    print(f"🔧 Configuration Summary:")
    print(f"   Provider: {provider}")
    
    if provider == 'openai':
        openai_config = ai_service.get('openai', {})
        api_key = openai_config.get('api_key', '')
        model = openai_config.get('model', 'unknown')
        print(f"   Model: {model}")
        print(f"   API Key: {api_key[:20]}..." if len(api_key) > 20 else f"   API Key: {api_key}")
    
    elif provider == 'azure_openai':
        azure_config = ai_service.get('azure_openai', {})
        endpoint = azure_config.get('endpoint', 'unknown')
        deployment = azure_config.get('deployment_name', 'unknown')
        api_key = azure_config.get('api_key', '')
        print(f"   Endpoint: {endpoint}")
        print(f"   Deployment: {deployment}")
        print(f"   API Key: {api_key[:20]}..." if len(api_key) > 20 else f"   API Key: {api_key}")

async def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 TestFoundry Framework - API Connection Tester")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        return
    
    print_config_info(config)
    print()
    
    # Get AI service configuration
    ai_service = config.get('ai_service', {})
    provider = ai_service.get('provider', '').lower()
    
    success = False
    
    if provider == 'openai':
        openai_config = ai_service.get('openai', {})
        if not openai_config.get('api_key'):
            print("❌ OpenAI API key not found in config!")
            return
        success = await test_openai_connection(openai_config)
    
    elif provider == 'azure_openai':
        azure_config = ai_service.get('azure_openai', {})
        required_fields = ['api_key', 'endpoint', 'deployment_name']
        missing = [field for field in required_fields if not azure_config.get(field)]
        
        if missing:
            print(f"❌ Missing Azure OpenAI configuration: {', '.join(missing)}")
            return
        success = await test_azure_openai_connection(azure_config)
    
    else:
        print(f"❌ Unknown AI provider: {provider}")
        print("💡 Set provider to 'openai' or 'azure_openai' in config.yaml")
        return
    
    print()
    print("=" * 60)
    if success:
        print("🎉 Connection test PASSED! You can run the full framework.")
        print("▶️  Run: python main.py")
    else:
        print("❌ Connection test FAILED! Fix the issues above before running the framework.")
        print("📖 Check the README.md for detailed setup instructions.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())