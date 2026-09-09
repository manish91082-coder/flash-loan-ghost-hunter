"""
PhantomX Windows Sleep Prevention Utility (prevent_sleep.py)
==================================================================================================
Uses Win32 API SetThreadExecutionState to keep system alive and prevent Windows from sleeping
or hibernating during 24/7 continuous AI testing and live execution.
Allow screen turn off while keeping CPU, Network, and System Threads active 24/7.
"""

import sys
import ctypes
import time
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Execution State Flags
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_AWAYMODE_REQUIRED = 0x00000040

def prevent_system_sleep():
    """
    Prevents Windows from entering Sleep Mode or Hibernation.
    Returns True if successfully set.
    """
    if os.name == 'nt':
        try:
            # Set continuous system required flag
            res = ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
            )
            if res != 0:
                print("🛡️ [Windows Stay-Awake Active] System sleep & hibernation PREVENTED 24/7!")
                return True
            else:
                print("⚠️ [Windows Stay-Awake Warning] SetThreadExecutionState returned 0.")
                return False
        except Exception as e:
            print(f"⚠️ [Windows Stay-Awake Exception] {e}")
            return False
    else:
        print("ℹ️ Non-Windows system detected. Sleep prevention skipped.")
        return True

def restore_system_sleep():
    """
    Restores normal Windows power saving mode when process finishes.
    """
    if os.name == 'nt':
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            print("💤 [Windows Stay-Awake] Restored normal power saving settings.")
        except Exception as e:
            print(f"⚠️ Error restoring sleep mode: {e}")

if __name__ == "__main__":
    print("================================================================================")
    print("🛡️ PhantomX Windows 24/7 System Stay-Awake Protection Test")
    print("================================================================================")
    success = prevent_system_sleep()
    if success:
        print("⚡ System is now locked in High-Performance 24/7 Execution Mode.")
        print("   (Screen can safely turn off without stopping AI or background tasks).")
    time.sleep(2)
