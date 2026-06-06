# 📸 Visual Guide: Upload Files to Hugging Face

## 🎯 Goal
Replace old files in HF Space with updated files from your Desktop

---

## ✅ What I've Done For You

1. ✅ Prepared all files on your Desktop: `~/Desktop/hf-upload-fixed/`
2. ✅ Opened HF Space in browser
3. ✅ Opened Finder with files ready

---

## 📋 Step-by-Step Instructions

### STEP 1: Go to Your HF Space Files

1. Browser should be open at: https://huggingface.co/spaces/Rukhsar24081998/hdfc-mf-faq-api
2. Click the **"Files and versions"** tab (or just "Files")
3. You'll see your current files listed

---

### STEP 2: Upload Method A - Individual Files (RECOMMENDED)

**Why this method:** It ensures files overwrite correctly

For each important file, do this:

#### File 1: `rag/assembler.py` (MOST IMPORTANT)
1. In HF Space Files tab, navigate to `rag/` folder
2. Click on `assembler.py`
3. Click the **"✏️ Edit"** button (pencil icon)
4. Delete ALL content
5. Open `~/Desktop/hf-upload-fixed/rag/assembler.py` on your computer
6. Copy ALL content
7. Paste into HF Space editor
8. Click **"Commit changes to main"**

#### File 2: `custom_facts.txt`
1. In HF Space Files tab, click on `custom_facts.txt`
2. Click **"✏️ Edit"**
3. Delete all content
4. Open `~/Desktop/hf-upload-fixed/custom_facts.txt`
5. Copy all content
6. Paste into HF Space
7. Commit changes

#### File 3: `api/main.py`
1. Navigate to `api/` folder
2. Click `main.py`
3. Edit → delete → copy from Desktop → paste → commit

#### File 4: `scheduler/core.py`
1. Navigate to `scheduler/` folder  
2. Click `core.py`
3. Edit → delete → copy from Desktop → paste → commit

#### File 5: `scheduler/jobs.py`
1. Still in `scheduler/` folder
2. Click `jobs.py`
3. Edit → delete → copy from Desktop → paste → commit

#### File 6: `ingest/fetcher.py`
1. Navigate to `ingest/` folder
2. Click `fetcher.py`
3. Edit → delete → copy from Desktop → paste → commit

---

### STEP 3: Force Rebuild

After uploading files, you MUST trigger a rebuild:

**Method A: Edit app.py**
1. In HF Space Files tab, click `app.py`
2. Click **"✏️ Edit"**
3. At line 1, change:
   ```python
   """
   ```
   To:
   ```python
   # Updated June 6, 2026 - Force rebuild
   """
   ```
4. Commit changes

**Method B: Factory Reboot (if available)**
1. Click **"Settings"** tab
2. Scroll to "Factory reboot" section
3. Click **"Reboot this Space"**

---

### STEP 4: Watch the Build

1. Click **"Logs"** tab in HF Space
2. Wait for these messages:
   ```
   📥 Running data ingest pipeline...
   ▶ Fetching sources...
   ▶ Extracting text...
   ▶ Chunking documents...
   ▶ Building embeddings...   ← This takes ~5 minutes
   ✅ Data pipeline complete!
   🚀 Starting FastAPI server...
   ```

3. **IMPORTANT:** Wait until you see "Starting FastAPI server..."

---

### STEP 5: Test It Works

**In Terminal:**
```bash
curl -X POST https://rukhsar24081998-hdfc-mf-faq-api.hf.space/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the expense ratio of HDFC Flexi Cap Fund?"}'
```

**Expected:** Should contain **"0.68%"** (not "0.85%")

---

## 🚨 Alternative: Upload Method B - Bulk Upload

If you prefer to upload all at once:

1. In HF Space → Files tab
2. Click **"Add file"** dropdown
3. Select **"Upload files"**
4. From Finder (which should be open), drag these folders:
   - `api/`
   - `rag/`
   - `scheduler/`
   - `ingest/`
5. Also drag these individual files:
   - `app.py`
   - `custom_facts.txt`
6. Click **"Commit changes to main"**

**⚠️ WARNING:** This might not overwrite existing files correctly. Use Method A if Method B doesn't work.

---

## 🔍 Verify Files Were Uploaded

After upload, check in HF Space Files tab:

1. Click `rag/assembler.py`
2. Scroll to line 60
3. Should see:
   ```python
   "expense_ratio": "0.68%",  # Updated June 2026
   ```

4. If you see `"expense_ratio": "0.85%"`, the file wasn't updated!

---

## ❓ Troubleshooting

### Issue: Files don't seem to upload
**Solution:**
- Try Method A (edit individual files)
- Make sure you click "Commit changes" after each edit

### Issue: Space shows "Building" forever
**Solution:**
- Check "Logs" tab for error messages
- Look for Python errors or missing dependencies

### Issue: Still returns 0.85% after rebuild
**Solution:**
1. Verify `rag/assembler.py` was actually updated (check line 60)
2. Check logs for "Building embeddings..." completed
3. Try Factory Reboot again
4. Make sure `custom_facts.txt` was also updated

### Issue: Can't find "Edit" button
**Solution:**
- Make sure you're logged into HF
- Make sure you own this Space
- Try refreshing the page

---

## ✅ Success Checklist

- [ ] Uploaded `rag/assembler.py`
- [ ] Uploaded `custom_facts.txt`
- [ ] Uploaded `api/main.py`
- [ ] Uploaded `scheduler/core.py`
- [ ] Uploaded `scheduler/jobs.py`
- [ ] Uploaded `ingest/fetcher.py`
- [ ] Triggered rebuild (edited app.py or factory reboot)
- [ ] Watched logs - saw "Building embeddings..."
- [ ] Logs show "✅ Data pipeline complete!"
- [ ] Logs show "🚀 Starting FastAPI server..."
- [ ] Tested - returns 0.68% ✅

---

## 🎯 Most Important File

If you can only update ONE file to test:

**Update: `rag/assembler.py`**

This file contains the SCHEME_DATA with expense ratios. If this file is updated correctly, you should see different results immediately (no rebuild needed for this part).

---

## 📞 After Success

Once you see 0.68% in the response:

✅ **Backend is FIXED!**

Next step: Deploy frontend to Vercel

See: `VERCEL_DEPLOYMENT_GUIDE.md`

---

**You can do this! Just follow the steps carefully. 💪**
