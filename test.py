# Power E - Installation & Testing Helper
# Use this to verify everything works correctly

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python():
    """Check Python version"""
    print_header("Checking Python Installation")
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("✅ Python version OK")
        return True
    else:
        print("❌ Python 3.7+ required")
        return False

def check_tkinter():
    """Check if Tkinter is available"""
    print_header("Checking Tkinter")
    
    try:
        import tkinter
        print("✅ Tkinter is available")
        
        # Test basic window
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
        print("✅ Tkinter window creation works")
        return True
    except ImportError:
        print("❌ Tkinter not found")
        print("Install: pip install tk")
        return False
    except Exception as e:
        print(f"❌ Tkinter error: {e}")
        return False

def check_files():
    """Check if required files exist"""
    print_header("Checking Files")
    
    required = ['PowerE.py', 'PowerE.bat']
    all_found = True
    
    for file in required:
        if Path(file).exists():
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
            all_found = False
    
    return all_found

def check_task_scheduler():
    """Check if Task Scheduler is accessible"""
    print_header("Checking Task Scheduler")
    
    if platform.system() != "Windows":
        print("⚠️  Task Scheduler only available on Windows")
        return False
    
    try:
        result = subprocess.run(
            ['schtasks', '/?'],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ Task Scheduler accessible")
            return True
        else:
            print("❌ Task Scheduler not accessible")
            return False
    
    except FileNotFoundError:
        print("❌ schtasks command not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_shutdown_command():
    """Test if shutdown command works (doesn't execute, just checks)"""
    print_header("Testing Shutdown Command")
    
    if platform.system() == "Windows":
        cmd = ['shutdown', '/?']
    else:
        cmd = ['shutdown', '--help']
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ Shutdown command available")
            return True
        else:
            print("⚠️  Shutdown command may require admin privileges")
            return True  # Still OK, just needs admin
    
    except FileNotFoundError:
        print("❌ Shutdown command not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_config_location():
    """Check config file location"""
    print_header("Checking Config Location")
    
    if platform.system() == "Windows":
        base = Path(os.getenv("APPDATA", Path.home()))
    else:
        base = Path.home()
    
    config_dir = base / "PowerE"
    config_file = config_dir / "config.json"
    
    print(f"Config directory: {config_dir}")
    
    if config_dir.exists():
        print(f"✅ Directory exists")
        
        if config_file.exists():
            print(f"✅ Config file exists")
            try:
                with open(config_file, 'r') as f:
                    import json
                    config = json.load(f)
                    print(f"   Shutdown time: {config.get('hour')}:{config.get('minute')} {config.get('ampm')}")
                    print(f"   Enabled: {config.get('enabled')}")
            except:
                print("⚠️  Config file exists but may be corrupted")
        else:
            print("ℹ️  No config file yet (will be created on first use)")
    else:
        print("ℹ️  Config directory will be created on first use")
    
    # Check if writable
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        test_file = config_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        print("✅ Config directory is writable")
        return True
    except Exception as e:
        print(f"❌ Config directory not writable: {e}")
        return False

def test_gui():
    """Test GUI launch"""
    print_header("Testing GUI Launch")
    
    print("Attempting to launch GUI...")
    print("(A window should appear. Close it to continue.)")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, 'PowerE.py'],
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ GUI launched successfully")
            return True
        else:
            print(f"⚠️  GUI exited with code: {result.returncode}")
            return True
    
    except subprocess.TimeoutExpired:
        print("⚠️  GUI still running (timeout). Please close it.")
        return True
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        return False

def run_all_tests():
    """Run all verification tests"""
    print("\n" + "█"*60)
    print("█" + " "*20 + "Power E v3.0" + " "*27 + "█")
    print("█" + " "*14 + "Installation & Test Helper" + " "*19 + "█")
    print("█"*60)
    
    tests = [
        ("Python Version", check_python),
        ("Tkinter Library", check_tkinter),
        ("Required Files", check_files),
        ("Task Scheduler", check_task_scheduler),
        ("Shutdown Command", test_shutdown_command),
        ("Config Location", check_config_location),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! PowerE is ready to use.")
        print("\nNext steps:")
        print("1. Double-click PowerE.bat")
        print("2. Set your shutdown time")
        print("3. Click 'Create Schedule'")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    # Optional GUI test
    print("\n" + "-"*60)
    response = input("\nWould you like to test the GUI? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        test_gui()
    
    print("\n" + "█"*60)
    print("Test complete. Press Enter to exit...")
    input()

if __name__ == "__main__":
    run_all_tests()




