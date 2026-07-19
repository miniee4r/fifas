#!/usr/bin/env python3
"""
Unified Test Runner — FIFA WC 2026 Smart Stadium
==================================================
Runs backend tests with coverage and guides frontend testing.
Ensures repo size remains compliant with 10MB limit.
"""

import subprocess
import sys
import os

def check_repo_size():
    """Calculates approximate repo size, ignoring git metadata and virtual environments."""
    total_size = 0
    for dirpath, _, filenames in os.walk('.'):
        if any(exc in dirpath for exc in ['.git', 'venv', 'node_modules', '__pycache__', '.pytest_cache']):
            continue
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size / 1024 # KB

def main():
    print("══════════════════════════════════════════════════════")
    print("  🏟️ FIFA WC 2026 — Smart Stadium Test Suite")
    print("══════════════════════════════════════════════════════\n")

    print("  Phase 1: Backend Tests (pytest)")
    print("  ─────────────────────────────────────────────────")
    print("  Running: pytest backend/tests/ -v --cov=backend\n")
    
    # Run pytest with coverage
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/tests/", "-v", "--cov=backend", "--cov-report=term-missing"],
        capture_output=False # Stream directly to console
    )
    
    backend_passed = result.returncode == 0

    print("\n  Phase 2: Frontend Tests")
    print("  ─────────────────────────────────────────────────")
    ui_test_path = os.path.join('frontend', 'tests', 'test_ui.html')
    if os.path.exists(ui_test_path):
        print(f"  ✅ {ui_test_path} exists")
        print("  ℹ️  Open this file in your browser to run DOM + A11y tests")
    else:
        print(f"  ❌ {ui_test_path} missing")
        backend_passed = False

    print("\n  Phase 3: Summary")
    print("  ─────────────────────────────────────────────────")
    print(f"  Backend:  {'✅ Passed' if backend_passed else '❌ Failed'}")
    
    size_kb = check_repo_size()
    size_limit_kb = 10240 # 10 MB
    print(f"  Repo size: ~{size_kb:.1f} KB (limit: {size_limit_kb} KB)", end=" ")
    if size_kb < size_limit_kb:
        print("✅")
    else:
        print("❌ OVERWEIGHT")

    print("══════════════════════════════════════════════════════")
    if backend_passed and size_kb < size_limit_kb:
        print("  🎉 ALL SYSTEMS GO — Ready for judge evaluation")
    else:
        print("  ⚠️ ISSUES DETECTED — Fix failing tests or size limit")
    print("══════════════════════════════════════════════════════")
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
