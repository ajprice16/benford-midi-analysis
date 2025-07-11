#!/usr/bin/env bash
# GitHub Actions Testing Helper Script

echo "🚀 GitHub Actions Testing Options"
echo "=================================="
echo ""

echo "1. 📋 Local Testing (Current)"
echo "   ./ci_test.py                     # Run enhanced local CI tests"
echo "   python ci_test.py               # Same as above"
echo ""

echo "2. 🎯 Manual GitHub Actions Trigger"
echo "   1. Push the workflow file once:  git push origin main"
echo "   2. Go to: https://github.com/$(git config remote.origin.url | sed 's/.*github.com[:/]\(.*\).git/\1/')/actions"
echo "   3. Select 'CI/CD Pipeline' workflow"
echo "   4. Click 'Run workflow' button"
echo "   5. Select branch and click 'Run workflow'"
echo ""

echo "3. 🐳 Local GitHub Actions with 'act'"
if command -v act &> /dev/null; then
    echo "   ✅ 'act' is installed!"
    echo "   act push                        # Simulate push event"
    echo "   act workflow_dispatch          # Simulate manual trigger"
    echo "   act pull_request               # Simulate PR event"
else
    echo "   ❌ 'act' not installed. Install with:"
    echo "   brew install act               # Requires Docker"
    echo "   Then run: act push"
fi
echo ""

echo "4. 📝 Draft Pull Request Method"
echo "   git checkout -b test-ci-$(date +%s)"
echo "   git add ."
echo "   git commit -m 'Test CI workflow'"
echo "   git push origin test-ci-$(date +%s)"
echo "   # Create draft PR on GitHub"
echo ""

echo "5. 🏷️  Test Specific Python Versions"
echo "   # GitHub Actions tests Python 3.8-3.13"
echo "   # Use pyenv to test locally:"
echo "   pyenv install 3.8.18 3.9.18 3.10.13 3.11.7 3.12.1 3.13.0"
echo "   for version in 3.8.18 3.9.18 3.10.13 3.11.7 3.12.1 3.13.0; do"
echo "       pyenv shell \$version"
echo "       python ci_test.py"
echo "   done"
echo ""

echo "💡 Recommendation: Use option 2 (Manual Trigger) for testing without commits"
echo "   This is the cleanest way to test GitHub Actions without polluting git history"
