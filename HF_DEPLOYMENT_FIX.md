# Hugging Face Deployment Fix Guide

## 🚨 Current Issue

Your HF Space is running but returning **OLD DATA**:
- **Expected:** Expense ratio = 0.68%
- **Actual:** Expense ratio = 0.85% ❌

**Root Cause:** The old ChromaDB database was uploaded, and the updated Python files were not uploaded correctly.

---

## ✅ Solution: Re-upload ALL Updated Files

You need to upload these **specific files** that contain the fixes:

### Step 1: Go to Your HF Space
https://huggingface.co/spaces/Rukhsar24081998/hdfc-mf-faq-api

### Step 2: Click "Files" Tab

### Step 3: Delete Old ChromaDB (CRITICAL)
**Delete this entire folder:**
```
data/chroma/
```

This folder contains stale data. We'll rebuild it with fresh data.

### Step 4: Upload These Updated Files

Upload these files from your local project to HF Space:

#### Core Files (MUST UPLOAD):
1. **rag/assembler.py** - Contains fixed SCHEME_DATA with 0.68% expense ratio
2. **api/main.py** - Contains /scheduler/refresh-now endpoint
3. **scheduler/core.py** - Contains monthly refresh job
4. **scheduler/jobs.py** - Contains refresh function
5. **ingest/fetcher.py** - Contains --force flag for re-downloading
6. **app.py** - Entry point (already uploaded, but re-upload to be sure)

#### Data Files (MUST UPLOAD):
7. **custom_facts.txt** - Contains updated facts with correct values
8. **data/extracted/custom_facts.txt** - Same as above

### Step 5: Force Rebuild (CRITICAL)

After uploading all files:

1. In HF Space, click "Settings" tab
2. Scroll to "Factory reboot"
3. Click "Reboot this Space"

OR

1. Click "Files" tab
2. Edit `app.py`
3. Add a comment like `# Force rebuild` at the top
4. Commit changes

This will trigger a complete rebuild that will:
- Delete old ChromaDB
- Run ingest pipeline fresh
- Build new embeddings with correct data

---

## 🔍 Verification After Reboot

Wait ~5-10 minutes for the Space to rebuild, then test:

```bash
# Test 1: Health check
curl https://rukhsar24081998-hdfc-mf-faq-api.hf.space/health

# Test 2: Check expense ratio (MUST return 0.68%)
curl -X POST https://rukhsar24081998-hdfc-mf-faq-api.hf.space/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the expense ratio of HDFC Flexi Cap Fund?"}'

# Expected output should contain: "0.68%" ✅
```

---

## 📋 Alternative: Use Git Sync (EASIER)

Instead of manual upload, connect HF Space to GitHub:

### Option A: GitHub Sync (RECOMMENDED)

1. Go to HF Space Settings
2. Look for "Git repository" or "Repository" section
3. Click "Connect to Git provider"
4. Select "GitHub"
5. Authorize Hugging Face
6. Select repository: `RAG-based-Mutual-Fund-FAQ-Chatbot`
7. HF will automatically sync ALL files from GitHub

**BUT FIRST:** Delete `data/chroma/` folder from HF Space manually (this folder is too large and contains old data)

---

## 🎯 Quick Fix (If You're in a Hurry)

If you don't want to re-upload everything:

### Minimal Fix:
1. Delete `data/chroma/` folder in HF Space
2. Upload only `rag/assembler.py` (contains the fix)
3. Reboot the Space

This will:
- Force ChromaDB rebuild
- Use updated SCHEME_DATA with correct values

---

## 🚨 Common Mistakes to Avoid

❌ **Don't:** Upload the local `data/chroma/` folder - it's too large and contains stale data  
✅ **Do:** Delete it and let the Space rebuild it fresh

❌ **Don't:** Upload only some files  
✅ **Do:** Upload ALL updated Python files to ensure consistency

❌ **Don't:** Skip the reboot/rebuild step  
✅ **Do:** Always reboot after uploading files

---

## 📞 Need Help?

If the Space is still returning old data after following these steps:

1. Check HF Space logs (click "Logs" tab)
2. Look for ingest pipeline output
3. Verify ChromaDB was rebuilt (should show "Building embeddings...")
4. Check for any error messages

---

## ✅ Success Criteria

Your deployment is successful when:

- ✅ Health endpoint returns 200
- ✅ Expense ratio query returns "0.68%"
- ✅ Minimum SIP for Defence Fund returns "₹100"
- ✅ Fund Manager for Flexi Cap returns "Amit Ganatra"
- ✅ /scheduler/status endpoint works
- ✅ Space logs show successful ingest pipeline

---

**Once HF is fixed, we'll deploy the frontend to Vercel! 🚀**
