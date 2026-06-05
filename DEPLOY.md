# 🚀 Sam Houston Downloader - Cloud Version

برنامه دانلود ویدیو با MongoDB و Cloud Deployment

---

## **مراحل Deploy روی Render.com:**

### **Step 1: GitHub Repository**

1. تمام فایل‌ها رو برای GitHub آماده کن:
   - `app_cloud.py` (نام تغییر بده به `app.py`)
   - `requirements.txt`
   - `.env.example`

2. Repository جدید بساز:
   - github.com → `+` → New repository
   - نام: `samhouston-downloader-cloud`
   - Public
   - فایل‌ها رو بالا بیار

---

### **Step 2: MongoDB Connection String**

Connection string رو برای MongoDB Atlas کپی کردی:

```
mongodb+srv://sam:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

**اطمینان دار:** username و password صحیح‌اند!

---

### **Step 3: Render.com Deploy**

1. برو: https://render.com
2. **Sign up** (رایگان)
3. **New** → **Web Service**
4. GitHub repository رو انتخاب کن
5. **Deploy**

---

### **Step 4: Environment Variables**

توی Render dashboard:
1. **Settings** → **Environment**
2. **Add Environment Variable**
   - **Key:** `MONGO_URI`
   - **Value:** `mongodb+srv://sam:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
3. **Save**

---

### **Step 5: تمام شد!**

- برنامه روی `https://your-app.onrender.com` اجرا میشه
- بقیه می‌تونن استفاده کنند! 🎉

---

## **Local Testing**

```bash
pip install -r requirements.txt
cp .env.example .env
# .env رو edit کن و MongoDB connection string بنویس
python app.py
# http://localhost:7070 رو بز
```

---

## **Features**

✅ دانلود از 1000+ سایت  
✅ MongoDB history tracking  
✅ Cloud deployment  
✅ بدون نیاز به کامپیوتر  
✅ رایگان (Render.com)

---

## **درباره**

Sam Houston Downloader  
نسخه Cloud  
✨ بهینه‌شده برای تمام دنیا
