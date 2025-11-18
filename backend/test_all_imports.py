#!/usr/bin/env python3
"""
Comprehensive import test for agent-pipeline
Tests all agent services and identifies import issues
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_model_imports():
    """Test importing all data models"""
    print("\n" + "=" * 60)
    print("TESTING DATA MODELS")
    print("=" * 60)

    models_to_test = [
        "Project", "ProjectCreate", "ProjectStatus",
        "QCFeedback", "QCRequest",
        "AudioAnalysis", "AudioUploadRequest",
        "Scene", "SceneBreakdown", "SceneBreakdownRequest",
        "StyleAnchor", "StyleAnchorRequest",
        "VideoPrompt", "VideoPromptRequest",
        "PromptRefinement", "PromptRefinementRequest",
        "VideoProductionPlan",
        "StoryboardResponse",
        "OrchestrationRequest",
        "APIResponse", "ErrorResponse",
        "SunoPromptExample", "SunoPromptRequest", "SunoPromptResponse",
        "FewShotLearningStats"
    ]

    try:
        import app.models.data_models as dm

        failed_models = []
        for model_name in models_to_test:
            if not hasattr(dm, model_name):
                failed_models.append(model_name)
                print(f"❌ MISSING: {model_name}")
            else:
                print(f"✅ {model_name}")

        if failed_models:
            print(f"\n❌ FAILED: {len(failed_models)} models missing")
            return False
        else:
            print(f"\n✅ SUCCESS: All {len(models_to_test)} models found")
            return True

    except Exception as e:
        print(f"❌ FAILED to import data_models: {e}")
        return False


def test_agent_syntax():
    """Test Python syntax of all agent service files"""
    print("\n" + "=" * 60)
    print("TESTING AGENT SERVICE SYNTAX")
    print("=" * 60)

    import py_compile

    agent_services = list(Path("app/agents").rglob("service.py"))

    passed = 0
    failed = 0

    for service_file in sorted(agent_services):
        agent_name = service_file.parent.name
        try:
            py_compile.compile(str(service_file), doraise=True)
            print(f"✅ {agent_name}")
            passed += 1
        except py_compile.PyCompileError as e:
            print(f"❌ {agent_name}: {e}")
            failed += 1

    print(f"\n📊 RESULTS: {passed} passed, {failed} failed")
    return failed == 0


def test_specific_imports():
    """Test specific problematic imports"""
    print("\n" + "=" * 60)
    print("TESTING SPECIFIC IMPORTS")
    print("=" * 60)

    tests = [
        ("SceneBreakdown from data_models",
         "from app.models.data_models import SceneBreakdown"),

        ("Project from data_models",
         "from app.models.data_models import Project"),

        ("APIResponse from data_models",
         "from app.models.data_models import APIResponse"),
    ]

    passed = 0
    failed = 0

    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            failed += 1

    print(f"\n📊 RESULTS: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all tests"""
    print("=" * 60)
    print("AGENT-PIPELINE IMPORT TEST SUITE")
    print("=" * 60)

    results = []

    # Test 1: Data models
    results.append(("Data Models", test_model_imports()))

    # Test 2: Agent syntax
    results.append(("Agent Syntax", test_agent_syntax()))

    # Test 3: Specific imports
    results.append(("Specific Imports", test_specific_imports()))

    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("🎉 ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
