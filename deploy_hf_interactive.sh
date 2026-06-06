#!/bin/bash

# Interactive Hugging Face Deployment Script
# This script guides you through deploying to HF Space

set -e

echo "🚀 Hugging Face Space Deployment Helper"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if files are ready
if [ ! -d "$HOME/Desktop/hf-upload-fixed" ]; then
    echo -e "${RED}❌ Error: Files not found on Desktop${NC}"
    echo "Expected: ~/Desktop/hf-upload-fixed/"
    exit 1
fi

echo -e "${GREEN}✅ Files found on Desktop${NC}"
echo ""

# Instructions
echo "📋 INSTRUCTIONS:"
echo "==============="
echo ""
echo "I'll open the following for you:"
echo "  1. Hugging Face Space (in browser)"
echo "  2. Desktop folder with files (in Finder)"
echo "  3. This terminal (to run tests)"
echo ""
echo "Then YOU need to:"
echo "  1. In HF Space → Files tab → Add file → Upload files"
echo "  2. Drag ALL files from the Finder window"
echo "  3. Commit changes"
echo "  4. Come back here and press ENTER"
echo ""

read -p "Press ENTER to open HF Space and Finder..." 

# Open HF Space
echo ""
echo "📂 Opening Hugging Face Space..."
open "https://huggingface.co/spaces/Rukhsar24081998/hdfc-mf-faq-api/tree/main"

sleep 2

# Open Finder
echo "📂 Opening files folder..."
open "$HOME/Desktop/hf-upload-fixed"

echo ""
echo -e "${YELLOW}⏸️  PAUSED - Waiting for you to upload files${NC}"
echo ""
echo "✅ Steps:"
echo "   1. In the browser (HF Space):"
echo "      → Click 'Files' tab"
echo "      → Click 'Add file' → 'Upload files'"
echo "      → Drag files from Finder window"
echo "      → Click 'Commit changes to main'"
echo ""
echo "   2. After upload, go to 'Logs' tab"
echo "      → Wait for build to complete (~5-10 min)"
echo "      → Look for: '✅ Data pipeline complete!'"
echo ""
echo "   3. Come back here and press ENTER"
echo ""

read -p "Have you uploaded files and HF Space is building? Press ENTER..." 

echo ""
echo "⏰ Waiting for HF Space to build (checking every 30 seconds)..."
echo ""

# Wait and check
COUNTER=0
MAX_ATTEMPTS=20 # 10 minutes

while [ $COUNTER -lt $MAX_ATTEMPTS ]; do
    echo -n "Attempt $((COUNTER + 1))/$MAX_ATTEMPTS: Checking health... "
    
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time 10 \
        https://rukhsar24081998-hdfc-mf-faq-api.hf.space/health 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Space is live!${NC}"
        break
    else
        echo "⏳ Not ready yet (got $HTTP_CODE)"
        sleep 30
        COUNTER=$((COUNTER + 1))
    fi
done

if [ $COUNTER -eq $MAX_ATTEMPTS ]; then
    echo ""
    echo -e "${RED}❌ Timeout: Space didn't respond after 10 minutes${NC}"
    echo "Please check HF Space logs manually"
    exit 1
fi

echo ""
echo "🧪 Testing data accuracy..."
echo "=========================="
echo ""

# Test 1: Health
echo "Test 1: Health Check"
HEALTH=$(curl -s https://rukhsar24081998-hdfc-mf-faq-api.hf.space/health | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'unknown'))" 2>/dev/null || echo "failed")

if [ "$HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
fi

echo ""

# Test 2: Expense Ratio
echo "Test 2: Expense Ratio (should be 0.68% not 0.85%)"
RESPONSE=$(curl -s -X POST https://rukhsar24081998-hdfc-mf-faq-api.hf.space/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "What is the expense ratio of HDFC Flexi Cap Fund?"}')

ANSWER=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('answer', '')[:300])" 2>/dev/null || echo "Error parsing")

echo "Answer excerpt:"
echo "$ANSWER"
echo ""

if echo "$ANSWER" | grep -q "0.68"; then
    echo -e "${GREEN}✅ CORRECT: Returns 0.68%${NC}"
    DATA_CORRECT=true
elif echo "$ANSWER" | grep -q "0.85"; then
    echo -e "${RED}❌ WRONG: Still returns 0.85% (old data)${NC}"
    DATA_CORRECT=false
else
    echo -e "${YELLOW}⚠️  UNCLEAR: Couldn't determine expense ratio${NC}"
    DATA_CORRECT=false
fi

echo ""
echo "========================================="
echo ""

if [ "$DATA_CORRECT" = true ]; then
    echo -e "${GREEN}🎉 SUCCESS! Backend is fixed!${NC}"
    echo ""
    echo "✅ Next Steps:"
    echo "   1. Deploy frontend to Vercel"
    echo "   2. See: VERCEL_DEPLOYMENT_GUIDE.md"
    echo ""
    echo "📍 Vercel URL: https://vercel.com/dashboard"
    echo ""
    read -p "Open Vercel dashboard? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "https://vercel.com/dashboard"
        echo ""
        echo "📋 Vercel Steps:"
        echo "   1. Add New → Project"
        echo "   2. Import: RAG-based-Mutual-Fund-FAQ-Chatbot"
        echo "   3. Root Directory: frontend"
        echo "   4. Deploy"
    fi
else
    echo -e "${RED}❌ Backend still has old data${NC}"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Check HF Space logs for errors"
    echo "   2. Verify all files were uploaded correctly"
    echo "   3. Make sure 'Building embeddings...' completed"
    echo "   4. Try Factory Reboot in Settings"
    echo ""
    echo "📖 See: HF_DEPLOYMENT_FIX.md for detailed help"
fi

echo ""
echo "Done! 🚀"
