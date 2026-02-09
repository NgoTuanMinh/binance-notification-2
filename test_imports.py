#!/usr/bin/env python3
"""Test if all required packages are installed."""

def test_imports():
    """Test importing all required packages."""
    errors = []
    
    print("🧪 Testing package imports...\n")
    
    # Test ccxt
    try:
        import ccxt
        print(f"✅ ccxt {ccxt.__version__}")
    except ImportError as e:
        errors.append(("ccxt", str(e)))
        print(f"❌ ccxt: {e}")
    
    # Test pandas
    try:
        import pandas as pd
        print(f"✅ pandas {pd.__version__}")
    except ImportError as e:
        errors.append(("pandas", str(e)))
        print(f"❌ pandas: {e}")
    
    # Test pandas_ta
    try:
        import pandas_ta as ta
        print(f"✅ pandas_ta installed")
    except ImportError as e:
        errors.append(("pandas_ta", str(e)))
        print(f"❌ pandas_ta: {e}")
    
    # Test aiohttp
    try:
        import aiohttp
        print(f"✅ aiohttp {aiohttp.__version__}")
    except ImportError as e:
        errors.append(("aiohttp", str(e)))
        print(f"❌ aiohttp: {e}")
    
    # Test python-dotenv
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv")
    except ImportError as e:
        errors.append(("python-dotenv", str(e)))
        print(f"❌ python-dotenv: {e}")
    
    # Test numpy
    try:
        import numpy as np
        print(f"✅ numpy {np.__version__}")
    except ImportError as e:
        errors.append(("numpy", str(e)))
        print(f"❌ numpy: {e}")
    
    # Test asyncio (built-in)
    try:
        import asyncio
        print("✅ asyncio (built-in)")
    except ImportError as e:
        errors.append(("asyncio", str(e)))
        print(f"❌ asyncio: {e}")
    
    print("\n" + "="*60)
    
    if errors:
        print("❌ INSTALLATION INCOMPLETE\n")
        print("Missing packages:")
        for pkg, error in errors:
            print(f"  • {pkg}")
        
        print("\n💡 To fix:")
        print("  1. Check INSTALLATION_FIX.md for troubleshooting")
        print("  2. Try: pip install -r requirements.txt")
        print("  3. Or install manually: pip install <package_name>")
        return False
    else:
        print("🎉 ALL PACKAGES INSTALLED SUCCESSFULLY!")
        print("\n✅ You can now run:")
        print("  python test_setup.py")
        print("  python main.py --once")
        return True


if __name__ == "__main__":
    import sys
    success = test_imports()
    sys.exit(0 if success else 1)
