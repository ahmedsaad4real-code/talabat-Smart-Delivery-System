# 🛵 Delivery Delay Predictor — Streamlit App

مشروع تخرج NTI — تطبيق Streamlit للتنبؤ بتأخير توصيل الطلبات، مبني على الموديل والخطوات الموجودة في `NTI_Graduation_Final.ipynb`.

## المحتوى
- `app.py` — تطبيق Streamlit الرئيسي (واجهة تنبؤ + رسوم بيانية + insights)
- `train_model.py` — سكريبت تدريب الموديل (RandomForest) وحفظه كـ `.pkl`
- `requirements.txt` — المكتبات المطلوبة
- عند تشغيل التطبيق لأول مرة، لو ملف الموديل غير موجود، هيتدرّب تلقائيًا (باستخدام `Order_delivery.csv` لو موجود، أو بيانات مولّدة تلقائيًا لو الملف غير متاح)

## 1) التشغيل محليًا

```bash
pip install -r requirements.txt
streamlit run app.py
```

لو عندك ملف `Order_delivery.csv` الحقيقي، ضعه في نفس المجلد قبل التشغيل عشان يتدرّب على البيانات الفعلية.

## 2) رفع المشروع على GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git
git branch -M main
git push -u origin main
```

## 3) النشر على Streamlit Community Cloud

1. افتح https://streamlit.io/cloud وسجّل دخول بحساب GitHub.
2. اضغط **New app**.
3. اختر الـ repository والـ branch (main).
4. حدد المسار: `app.py`.
5. اضغط **Deploy**.

## 4) تحديث التطبيق بعد أي تعديل

```bash
git add .
git commit -m "Update app"
git push origin main
```

Streamlit Cloud هيعمل redeploy تلقائيًا.
