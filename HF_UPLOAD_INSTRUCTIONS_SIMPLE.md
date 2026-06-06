# 🚀 Hugging Face Upload - Simplified Instructions

## ✅ Good News!

The `data/chroma/` folder is not in your HF Space, which means you can upload fresh files without worrying about old data!

---

## 📋 Simple Upload Steps

### Step 1: Go to Your Space
https://huggingface.co/spaces/Rukhsar24081998/hdfc-mf-faq-api

---

### Step 2: Upload Files

1. Click **"Files"** tab (at the top)

2. You'll see your current files. Now we need to upload the updated ones.

3. Click **"Add file"** button → Select **"Upload files"**

4. Drag and drop ALL files from this folder on your Desktop:
   ```
   ~/Desktop/hf-upload-fixed/
   ```

5. **IMPORTANT:** When uploading, make sure folder structure is maintained:
   - `api/main.py`
   - `rag/assembler.py`
   - `scheduler/core.py`
   - `scheduler/jobs.py`
   - `ingest/fetcher.py`
   - etc.

6. Scroll down and click **"Commit changes to main"**

---

### Step 3: Trigger Rebuild

**Option A: Edit a file to trigger rebuild**
1. In "Files" tab, click on `app.py`
2. Click "Edit" button
3. At the very top, add a comment line:
   ```python
   # Updated June 6, 2026
   ```
4. Click "Commit changes to main"

**Option B: Factory Reboot (if available)**
1. Click "Settings" tab
2. Look for "Factory reboot" section
3. Click "Reboot this Space"

---

### Step 4: Watch the Build

1. Click **"Logs"** tab (next to Files)

2. You should see output like:
   ```
   ====================================
   HDFC Mutual Fund FAQ API - First-time setup
   ====================================
   
   📥 Running data ingest pipeline...
   
   ▶ Fetching sources...
   ✓ Fetching sources complete
   
   ▶ Extracting text...
   ✓ Extracting text complete
   
   ▶ Chunking documents...
   ✓ Chunking documents complete
   
   ▶ Building embeddings...
   ✓ Building embeddings complete
   
   ====================================
   ✅ Data pipeline complete!
   ====================================
   
   🚀 Starting FastAPI server...
   ```

3. **Wait ~5-10 minutes** for this process to complete

---

### Step 5: Verify It Works

Once the logs show "Starting FastAPI server...", test it:

**Test 1: Health Check**
```bash
curl https://rukhsar24081998-hdfc-mf-faq-api.hf.space/health
```
Should return: `{"status":"healthy",...}`

**Test 2: Data Accuracy** (MOST IMPORTANT)
```bash
curl -X POST https://rukhsar24081998-hdfc-mf-faq-api.hf.space/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the expense ratio of HDFC Flexi Cap Fund?"}'
```
Should return answer containing: **"0.68%"** ✅ (not "0.85%")

---

## 🎯 Quick Checklist

- [ ] Go to HF Space Files tab
- [ ] Upload ALL files from `~/Desktop/hf-upload-fixed/`
- [ ] Commit changes
- [ ] Trigger rebuild (edit app.py or factory reboot)
- [ ] Watch logs for "Building embeddings..."
- [ ] Wait ~5-10 minutes
- [ ] Test: Health endpoint works
- [ ] Test: Returns 0.68% (not 0.85%)

---

## ❓ What if...

### Q: I don't see "Add file" button
**A:** Make sure you're logged into Hugging Face and you own this Space.

### Q: Upload fails or times out
**A:** Upload files in smaller batches:
1. First: Upload `app.py`, `requirements.txt`
2. Then: Upload `api/` folder
3. Then: Upload `rag/` folder
4. Then: Upload `scheduler/` and `ingest/` folders
5. Then: Upload remaining files

### Q: Space shows "Runtime Error"
**A:** Click on "Logs" tab to see the error message. Common issues:
- Missing files: Make sure all files uploaded
- Wrong folder structure: Check paths match
- API key missing: Set `GROQ_API_KEY` in Settings → Repository secrets

### Q: Still returns 0.85% after rebuild
**A:** 
1. Check logs - did "Building embeddings" complete successfully?
2. Check if `rag/assembler.py` was uploaded correctly
3. Check if `custom_facts.txt` was uploaded
4. Try factory reboot again

---

## 🎉 Success Looks Like

When everything works:
- ✅ Space status: "Running"
- ✅ Logs show: "Starting FastAPI server..."
- ✅ Health endpoint returns 200
- ✅ Query returns "0.68%" (correct data!)
- ✅ No error messages in logs

---

## 📞 Files to Upload

These are in `~/Desktop/hf-upload-fixed/`:

```
hf-upload-fixed/
├── api/
│   ├── __init__.py
│   └── main.py (UPDATED - has refresh endpoint)
├── rag/
│   └── assembler.py (UPDATED - has correct data)
├── scheduler/
│   ├── __init__.py
│   ├── core.py (UPDATED - monthly refresh)
│   └── jobs.py (NEW - refresh function)
├── ingest/
│   ├── __init__.py
│   ├── fetcher.py (UPDATED - has --force flag)
│   ├── extractor.py
│   ├── chunker.py
│   └── embedder.py
├── data/
│   └── extracted/
│       └── custom_facts.txt (UPDATED)
├── app.py (Entry point)
├── custom_facts.txt (UPDATED)
├── requirements.txt
└── .env.example
```

---

## ⏰ Timeline

| Step | Time |
|------|------|
| Upload files | 2-3 minutes |
| Trigger rebuild | 1 minute |
| Space rebuilds | 5-10 minutes |
| Testing | 2 minutes |
| **Total** | **10-15 minutes** |

---

## 🚀 After HF is Fixed

Once your backend returns "0.68%":

**Next: Deploy Frontend to Vercel**

See: `VERCEL_DEPLOYMENT_GUIDE.md`

Quick steps:
1. Go to https://vercel.com/dashboard
2. Import from GitHub
3. Set Root Directory: `frontend`
4. Deploy

---

**You've got this! 🎯**

Just upload the files from Desktop, trigger rebuild, and wait for the magic to happen!
