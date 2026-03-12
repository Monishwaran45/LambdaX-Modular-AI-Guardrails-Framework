"""Test all imports to ensure no missing dependencies or syntax errors."""

import sys
import traceback

def test_import(module_name, description):
    """Test importing a module."""
    try:
        __import__(module_name)
        print(f"[PASS] {description}: {module_name}")
        return True
    except Exception as e:
        print(f"[FAIL] {description}: {module_name}")
        print(f"  Error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all import tests."""
    print("=" * 60)
    print("Testing LambdaX Imports")
    print("=" * 60)
    
    tests = [
        # Core modules
        ("lambdax.core.exceptions", "Core Exceptions"),
        ("lambdax.core.context", "Request Context"),
        ("lambdax.core.guard", "Guard Base Class"),
        ("lambdax.core.policy", "Policy Engine"),
        ("lambdax.core.orchestrator", "Orchestrator"),
        
        # Guards
        ("lambdax.guards.input_sanitizer", "Input Sanitizer Guard"),
        ("lambdax.guards.prompt_injection", "Prompt Injection Guard"),
        ("lambdax.guards.toxicity", "Toxicity Guard"),
        ("lambdax.guards.privacy", "Privacy Guard"),
        ("lambdax.guards.format_validator", "Format Validator Guard"),
        
        # Utils
        ("lambdax.utils.logging", "Logging Utils"),
        ("lambdax.utils.audit", "Audit Logger"),
        
        # API
        ("lambdax.api.app", "FastAPI App"),
        ("lambdax.api.routes", "API Routes"),
        
        # CLI
        ("lambdax.cli.main", "CLI Main"),
        
        # Main package
        ("lambdax", "Main Package"),
    ]
    
    passed = 0
    failed = 0
    
    for module, desc in tests:
        if test_import(module, desc):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
