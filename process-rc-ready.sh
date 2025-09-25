#!/bin/bash
# Process all RC Ready issues for release 7.9.0
# Issues from: project IN (SAAS) AND (fixVersion = 7.9.0) and labels = rcready_sep10

echo "🚀 Processing RC Ready Issues for Release 7.9.0"
echo "=================================================="

ISSUES=(
  "SAAS-41"
  "SAAS-392"
  "SAAS-615"
  "SAAS-751"
  "SAAS-803"
  "SAAS-1390"
  "SAAS-1569"
  "SAAS-1578"
  "SAAS-1629"
  "SAAS-1703"
  "SAAS-1774"
  "SAAS-1787"
  "SAAS-1919"
  "SAAS-2039"
  "SAAS-2041"
)

SUCCESS_COUNT=0
ERROR_COUNT=0
ERRORS=()

for issue in "${ISSUES[@]}"; do
  echo ""
  echo "📝 Processing $issue ($(($SUCCESS_COUNT + $ERROR_COUNT + 1))/15)..."
  echo "----------------------------------------"
  
  if ./cj-release "$issue"; then
    echo "✅ Successfully processed $issue"
    ((SUCCESS_COUNT++))
  else
    echo "❌ Failed to process $issue"
    ((ERROR_COUNT++))
    ERRORS+=("$issue")
  fi
  
  echo "----------------------------------------"
done

echo ""
echo "🏁 SUMMARY"
echo "=========="
echo "✅ Successfully processed: $SUCCESS_COUNT/15"
echo "❌ Failed: $ERROR_COUNT/15"

if [ ${#ERRORS[@]} -gt 0 ]; then
  echo ""
  echo "❌ Failed issues:"
  for error in "${ERRORS[@]}"; do
    echo "   - $error"
  done
fi

echo ""
echo "🎯 All RC Ready issues processed!"