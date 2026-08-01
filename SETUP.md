# SETUP — دقايق معدودة (مرة واحدة بس)

## الخطوة 1: إنشاء الريبو (github.com — متصفح)
1. ادخل على https://github.com/new
2. اسم الريبو: `walednet-store`
3. اختار **Public** (أو Private — الاتنين شغالين)
4. **لا تنشئ README أو .gitignore أو license** (الريبو الفاضي)
5. اضغط **Create repository**

## الخطوة 2: إضافة المفتاحين (مرة واحدة)
1. افتح الريبو → تبويب **Settings** → **Secrets and variables** → **Actions**
2. اضغط **New repository secret** مرتين وأنشئ:
   - `ZENMUX_KEY` ← القيمة من `D:\GOAL_DOLLAR\autostore\config.json` (سطر `zenmux_key`)
   - `DEVTO_KEY` ← القيمة من نفس الملف (سطر `devto_key`)
3. **الأمان:** الملف config.json ده **ممنوع يترفع** أبدًا — الـ .gitignore مستثنيه تلقائيًا

## الخطوة 3: الرفع من الجهاز (مرة واحدة)
- ارجع هنا واضغط `push.bat` (دابل كليك)
- أول مرة هيسألك عن رابط الريبو: الصق الرابط بتاعك
- أول مرة GitHub هيطلب تسجيل دخول: اتفضل قم بصفحة تسجيل الدخول (Credential Manager هيحفظه بعدها للأبد)

## الخطوة 4: تفعيل النشر التلقائي
1. افتح الريبو → تبويب **Actions** → هنشوف "AutoPublish Dev.to"
2. اضغط **Run workflow** (التجربة الأولى — لازم تنشر مقال فورًا)
3. بعده: كرون يومي 06:00 UTC بيشتغل لوحده للأبد
4. التحقق: https://dev.to/dashboard — أول مقال هيظهر هناك

## الخطوة 5 (اختياري لكن مهم): استضافة صفحة الهبوط مجانًا
1. سجّل على https://dash.cloudflare.com (إيميل فقط — مجاني)
2. القائمة → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. اربط GitHub → اختار `walednet-store` → في **Build command** اكتب `echo ok` وكله فاضي (site ثابتة)
4. **Save and Deploy** → الصفحة هتفتح على رابط `https://walednet-store.pages.dev`
5. ده الرابط اللي بيتبعت في البينز والمقالات (بدل لينك البوت مباشرة)

## Pinterest (سليديول آمن — النشر الأتوماتيك الكامل بيقفل الحساب)
1. اعمل حساب Pinterest جديد
2. أنشئ اللوحات الست من `autopublisher/pinterest/keywords.md`
3. الصور جاهزة: `autopublisher/pinterest/images/pin_01.jpg ... pin_15.jpg`
4. النصوص جاهزة: `autopublisher/pinterest/pins.md`
5. سجّل في Tailwind (مجاني — مرتبط بآبي Pinterest الرسمي) وارفع الصور + النصوص
6. رتب سليديول يومي من اللوحات — هو ينشر لوحده
