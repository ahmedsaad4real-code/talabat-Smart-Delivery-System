<div dir="rtl" markdown="1">

# Step 7 — Data Dictionary

## Quick Overview

الـData Dictionary ده بيجمع فهمنا لكل columns في `Order_delivery.csv` بعد Phase 1 لحد Step 6.  
الهدف منه إن أي حد في التيم يفتح الملف يعرف بسرعة كل column معناها إيه، نوعها الحالي، نوعها المنطقي في التحليل، وأي ملاحظات مهمة قبل Phase 2.

مهم: ده مش cleaning، ومفيش أي قيم اتغيرت. إحنا بس بنوثّق اللي اتأكدنا منه في التقارير السابقة.

### Dataset facts ثابتة

- الداتا فيها `100,002 rows` و`23 columns`.
- كل الـ23 columns عندهم `0 missing values`.
- مفيش `Exact Full-Row Duplicates`.
- `Order_ID` unique لكل row.
- `User_ID`, `Restaurant_ID`, و`Driver_ID` بيتكرروا عادي لأن نفس الكيانات ممكن تظهر في أكتر من order.
- `Order_Time` و`Delivery_Time` بيتقرأوا بنجاح، والفرق بينهم مطابق لـ`Delivery_Duration_Minutes` في كل الـ`100,002 rows`.
- `Delivery_Distance_km` متسقة بشكل عام مع restaurant/customer coordinates، وفيه `2 rows` بس الفرق فيهم أكبر من `0.10 km`.
- `Delivery_Distance_km` فيها `30` IQR-flagged observations، حوالي `0.03%`، ودي unusual statistically مش invalid تلقائيًا.
- كل Latitude/Longitude columns عندها `0 invalid coordinate values`.
- `Cancelled` و`In Transit` rows فيها delivery timestamps/durations، لكن الـCSV لوحده مش كفاية عشان نحدد هل ده behavior صحيح ولا مشكلة، لأننا محتاجين business rule واضح.

---

## Order & Entity Information

### 1. `Order_ID`

| Field | Details |
| --- | --- |
| Current Data Type | `int64` |
| Logical Data Type | Identifier |
| What does it mean? | ده الـunique identifier الخاص بكل order. كل `Order_ID` بيمثل order واحدة. |
| Role in Dataset | Order identifier |
| Example Values | `1`, `2`, `3`, `4`, `5` |
| Cardinality | `100,002` unique values من `100,002 rows` |
| Relationship / Dependency | order-level key؛ مفيش repeated `Order_ID`. |
| Data Quality Note | `0 missing values`، وبيتصرف كـunique ID مش numerical measure. |
| Phase 2 Note | يتعامل كـIdentifier فقط، وميدخلش كمتغير رقمي تحليلي. |

### 2. `User_ID`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Identifier |
| What does it mean? | ده ID للمستخدم اللي عمل order. |
| Role in Dataset | Entity identifier |
| Example Values | `U3522`, `U9214`, `U7307`, `U3612`, `U3492` |
| Cardinality | `9,000` unique users |
| Relationship / Dependency | نفس `User_ID` ممكن يظهر في أكتر من order؛ متوسط orders لكل user حوالي `11.1113`. |
| Data Quality Note | `0 missing values`. repeated IDs هنا repeated activity مش duplicates. |
| Phase 2 Note | يتعامل كـIdentifier، وأي تجميع على user-level يبقى قرار تحليلي لاحق. |

### 3. `Restaurant_ID`

| Field | Details |
| --- | --- |
| Current Data Type | `int64` |
| Logical Data Type | Identifier |
| What does it mean? | ID للمطعم المرتبط بالطلب. |
| Role in Dataset | Entity identifier |
| Example Values | `358`, `316`, `357`, `420`, `73` |
| Cardinality | `1,000` unique restaurants |
| Relationship / Dependency | نفس المطعم ممكن يظهر في orders كتير؛ متوسط orders لكل restaurant حوالي `100.002`. |
| Data Quality Note | `0 missing values`. رغم إنه مقروء كـ`int64`، منطقيًا هو ID مش رقم تحليلي. |
| Phase 2 Note | يتعامل كـIdentifier، مش كـNumerical feature. |

### 4. `Driver_ID`

| Field | Details |
| --- | --- |
| Current Data Type | `int64` |
| Logical Data Type | Identifier |
| What does it mean? | ID للسائق المرتبط بالتوصيل. |
| Role in Dataset | Entity identifier |
| Example Values | `485`, `65`, `309`, `32`, `364` |
| Cardinality | `500` unique drivers |
| Relationship / Dependency | نفس driver ممكن يظهر في orders كتير؛ متوسط orders لكل driver حوالي `200.004`. |
| Data Quality Note | `0 missing values`. repeated `Driver_ID` مش duplicate. |
| Phase 2 Note | يتعامل كـIdentifier، ومحتاجين نفصله عن أي numerical analysis. |

### 5. `Item_Name`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Categorical / Text |
| What does it mean? | اسم الـfood item المطلوب في order. |
| Role in Dataset | Order attribute |
| Example Values | `Fried Chicken`, `Sandwich`, `Koshary`, `Sushi`, `Shawarma` |
| Cardinality | `9` unique values |
| Relationship / Dependency | مفيش relationship مؤكدة مع column تانية في Step 6. |
| Data Quality Note | `0 missing values`، ومفيش inconsistent labels واضحة. |
| Phase 2 Note | غالبًا يتعامل كـcategorical text لو دخل في EDA أو modeling. |

---

## Order & Payment Information

### 6. `Quantity`

| Field | Details |
| --- | --- |
| Current Data Type | `int64` |
| Logical Data Type | Discrete numerical |
| What does it mean? | عدد القطع/الوحدات في الطلب. |
| Role in Dataset | Order attribute |
| Example Values | `3`, `2`, `5`, `1`, `4` |
| Cardinality | `5` unique values |
| Relationship / Dependency | مفيش dependency مؤكدة في Step 6. |
| Data Quality Note | `0 missing values`، القيم من `1` لـ`5`، ومفيش IQR flags. |
| Phase 2 Note | مفيش action واضح مطلوب حاليًا. |

### 7. `Total_Price`

| Field | Details |
| --- | --- |
| Current Data Type | `float64` |
| Logical Data Type | Continuous numerical |
| What does it mean? | إجمالي سعر الطلب. |
| Role in Dataset | Order monetary metric |
| Example Values | `273.72`, `365.82`, `401.94`, `221.18`, `355.55` |
| Cardinality | `35,618` unique values |
| Relationship / Dependency | مفيش relationship مؤكدة اتوثقت في Step 6. |
| Data Quality Note | `0 missing values`، range من `30.0` لـ`750.0`، ومفيش IQR flags. |
| Phase 2 Note | مفيش outlier action واضح من Phase 1. |

### 8. `Payment_Method`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Categorical |
| What does it mean? | طريقة الدفع المستخدمة في order. |
| Role in Dataset | Categorical order attribute |
| Example Values | `Wallet`, `Credit Card`, `Cash` |
| Cardinality | `3` unique values |
| Relationship / Dependency | مفيش relationship مؤكدة اتوثقت في Step 6. |
| Data Quality Note | `0 missing values`، ومفيش labels inconsistent واضحة. |
| Phase 2 Note | لو هتدخل في modeling/EDA، تتعامل كـcategorical variable. |

### 9. `Order_Status`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Categorical / outcome-related |
| What does it mean? | حالة الطلب: مثل `Delivered`, `Cancelled`, `In Transit`. |
| Role in Dataset | Outcome-related variable |
| Example Values | `Delivered`, `In Transit`, `Cancelled` |
| Cardinality | `3` unique values |
| Relationship / Dependency | مرتبط منطقيًا بـ`Delivery_Time` و`Delivery_Duration_Minutes`، لكن business rule مش مؤكد من الـCSV لوحده. |
| Data Quality Note | `0 missing values`. `Cancelled` و`In Transit` rows عندهم delivery timestamps/durations، ومش هنعتبر ده error بدون business rule. |
| Phase 2 Note | محتاج confirmation لمعنى statuses قبل أي cleaning decision. |

---

## Time & Delivery

### 10. `Order_Time`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Datetime |
| What does it mean? | وقت عمل order. |
| Role in Dataset | Order timestamp |
| Example Values | `16-06-2025 08:32`, `03-06-2025 21:27`, `01-06-2025 14:48` |
| Cardinality | `21,367` unique values |
| Relationship / Dependency | مرتبط مباشرة بـ`Delivery_Time` و`Delivery_Duration_Minutes`. |
| Data Quality Note | `0 missing values`. parsing بصيغة `dd-mm-yyyy hh:mm` نجح، ومفيش parse failures. |
| Phase 2 Note | يتحول لـDatetime فقط لما نبدأ cleaning/preparation. |

### 11. `Delivery_Time`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Datetime |
| What does it mean? | وقت التوصيل أو وقت تسجيل التوصيل في الداتا. |
| Role in Dataset | Delivery timestamp / outcome-related |
| Example Values | `16-06-2025 09:11`, `03-06-2025 22:00`, `01-06-2025 15:26` |
| Cardinality | `21,396` unique values |
| Relationship / Dependency | `Delivery_Time - Order_Time` مطابق لـ`Delivery_Duration_Minutes` في كل الـ`100,002 rows`. |
| Data Quality Note | `0 missing values`. مفيش delivery قبل order. |
| Phase 2 Note | يتحول لـDatetime لاحقًا، ومع `Order_Status` محتاج business interpretation. |

### 12. `Delivery_Duration_Minutes`

| Field | Details |
| --- | --- |
| Current Data Type | `int64` |
| Logical Data Type | Duration / numerical |
| What does it mean? | مدة التوصيل بالدقائق. |
| Role in Dataset | Delivery metric / outcome-related variable |
| Example Values | `39`, `33`, `38`, `52`, `44` |
| Cardinality | `46` unique values |
| Relationship / Dependency | محسوبة منطقيًا من الفرق بين `Delivery_Time` و`Order_Time`، والفحص أكد التطابق في كل rows. |
| Data Quality Note | `0 missing values`، range من `15` لـ`60`، ومفيش IQR flags. |
| Phase 2 Note | مهم جدًا لو الهدف متعلق بسرعة التوصيل، لكن مفيش discrepancy محتاج cleaning من Phase 1. |

### 13. `Delivery_Distance_km`

| Field | Details |
| --- | --- |
| Current Data Type | `float64` |
| Logical Data Type | Continuous numerical |
| What does it mean? | مسافة التوصيل بالكيلومتر. |
| Role in Dataset | Delivery distance metric |
| Example Values | `1.666106279`, `2.738697528`, `2.929078717`, `0.677497944`, `1.994768748` |
| Cardinality | `100,001` unique values |
| Relationship / Dependency | broadly consistent مع restaurant/customer Haversine distance؛ `2 rows` بس الفرق فيهم أكبر من `0.10 km`. |
| Data Quality Note | `0 missing values`. فيه `30` IQR-flagged observations، حوالي `0.03%`، ودي unusual statistically مش invalid تلقائيًا. |
| Phase 2 Note | يستحق review بسيط في Phase 2 لو دقة المسافة مهمة للتحليل. |

---

## Location

### 14. `City`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Categorical / geographic label |
| What does it mean? | المدينة المرتبطة بالطلب/التوصيل. |
| Role in Dataset | Location information |
| Example Values | `Alexandria`, `Zagazig`, `Assiut`, `Mansoura`, `Cairo` |
| Cardinality | `7` unique cities |
| Relationship / Dependency | مفيش relationship مؤكدة اتوثقت في Step 6 مع باقي location columns. |
| Data Quality Note | `0 missing values`، ومفيش inconsistent city labels واضحة. |
| Phase 2 Note | تتعامل كـcategorical geographic label. |

### 15. `Restaurant_Lat`

| Field | Details |
| --- | --- |
| Current Data Type | `float64` |
| Logical Data Type | Geographic coordinate / Latitude |
| What does it mean? | Latitude الخاص بالمطعم. |
| Role in Dataset | Location information |
| Example Values | `31.1950816`, `30.60572857`, `27.19017976` |
| Cardinality | High-cardinality coordinate؛ `99,833` unique values |
| Relationship / Dependency | مع `Restaurant_Lon` بيمثلوا restaurant location، واتقارنوا مع customer coordinates و`Delivery_Distance_km`. |
| Data Quality Note | `0 missing values`، و`0 invalid coordinate values`. |
| Phase 2 Note | مفيش correction واضح، بس تستخدم بحذر كـcoordinate. |

### 16. `Restaurant_Lon`

| Field | Details |
| --- | --- |
| Current Data Type | `float64` |
| Logical Data Type | Geographic coordinate / Longitude |
| What does it mean? | Longitude الخاص بالمطعم. |
| Role in Dataset | Location information |
| Example Values | `29.92193116`, `31.50307887`, `31.17774148` |
| Cardinality | High-cardinality coordinate؛ `99,785` unique values |
| Relationship / Dependency | مع `Restaurant_Lat` بيمثلوا restaurant location. |
| Data Quality Note | `0 missing values`، و`0 invalid coordinate values`. |
| Phase 2 Note | مفيش action واضح مطلوب حاليًا. |

### 17. `Customer_Lat`

| Field | Details |
| --- | --- |
| Current Data Type | `float64` |
| Logical Data Type | Geographic coordinate / Latitude |
| What does it mean? | Latitude الخاص بمكان العميل. |
| Role in Dataset | Location information |
| Example Values | `31.19140352`, `30.58604706`, `27.16486862` |
| Cardinality | High-cardinality coordinate؛ `99,840` unique values |
| Relationship / Dependency | مع `Customer_Lon` بيمثلوا customer location، ومرتبطين بفحص `Delivery_Distance_km`. |
| Data Quality Note | `0 missing values`، و`0 invalid coordinate values`. |
| Phase 2 Note | مفيش correction واضح، بس ممكن تستخدم في distance/location analysis لاحقًا. |

### 18. `Customer_Lon`

| Field | Details |
| --- | --- |
| Current Data Type | `float64` |
| Logical Data Type | Geographic coordinate / Longitude |
| What does it mean? | Longitude الخاص بمكان العميل. |
| Role in Dataset | Location information |
| Example Values | `29.90498216`, `31.48582035`, `31.16921757` |
| Cardinality | High-cardinality coordinate؛ `99,780` unique values |
| Relationship / Dependency | مع `Customer_Lat` بيمثلوا customer location. |
| Data Quality Note | `0 missing values`، و`0 invalid coordinate values`. |
| Phase 2 Note | مفيش action واضح مطلوب حاليًا. |

### 19. `Driver_Lat`

| Field | Details |
| --- | --- |
| Current Data Type | `float64` |
| Logical Data Type | Geographic coordinate / Latitude |
| What does it mean? | Latitude الخاص بالسائق. |
| Role in Dataset | Location information |
| Example Values | `31.21565812`, `30.58032854`, `27.16297639` |
| Cardinality | High-cardinality coordinate؛ `99,827` unique values |
| Relationship / Dependency | مع `Driver_Lon` بيمثلوا driver location. Step 6 ما استخدمهمش لتأكيد road distance، بس اتفهموا كجزء من location structure. |
| Data Quality Note | `0 missing values`، و`0 invalid coordinate values`. |
| Phase 2 Note | نحتاج نفهم توقيت driver location لو هيتستخدم تحليليًا. |

### 20. `Driver_Lon`

| Field | Details |
| --- | --- |
| Current Data Type | `float64` |
| Logical Data Type | Geographic coordinate / Longitude |
| What does it mean? | Longitude الخاص بالسائق. |
| Role in Dataset | Location information |
| Example Values | `29.9106644`, `31.5023799`, `31.18945766` |
| Cardinality | High-cardinality coordinate؛ `99,758` unique values |
| Relationship / Dependency | مع `Driver_Lat` بيمثلوا driver location. |
| Data Quality Note | `0 missing values`، و`0 invalid coordinate values`. |
| Phase 2 Note | مفيش invalid coordinate issue، لكن معنى توقيت location محتاج سياق لو هيتستخدم. |

---

## Delivery Context

### 21. `Driver_Vehicle`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Categorical |
| What does it mean? | نوع وسيلة التوصيل اللي السائق بيستخدمها. |
| Role in Dataset | Delivery context attribute |
| Example Values | `Motorbike`, `Car`, `Bicycle` |
| Cardinality | `3` unique values |
| Relationship / Dependency | مفيش dependency مؤكدة اتوثقت في Step 6. |
| Data Quality Note | `0 missing values`، ومفيش inconsistent labels واضحة. |
| Phase 2 Note | تتعامل كـcategorical variable لو دخلت في analysis. |

### 22. `Traffic_Level`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Ordinal categorical |
| What does it mean? | مستوى الزحمة المرتبط بالتوصيل. |
| Role in Dataset | Delivery context attribute |
| Example Values | `High`, `Low`, `Medium` |
| Cardinality | `3` unique values |
| Relationship / Dependency | مفيش business dependency مؤكدة اتوثقت في Step 6. |
| Data Quality Note | `0 missing values`، والقيم consistent: `Low`, `Medium`, `High`. |
| Phase 2 Note | لو استخدمناه، ناخد بالنا إنه ordinal categorical. |

### 23. `Driver_Availability`

| Field | Details |
| --- | --- |
| Current Data Type | `str` |
| Logical Data Type | Binary categorical |
| What does it mean? | حالة توفر السائق: `Online` أو `Offline`. |
| Role in Dataset | Delivery context / driver status attribute |
| Example Values | `Offline`, `Online` |
| Cardinality | `2` unique values |
| Relationship / Dependency | ظهر مع كل `Order_Status` categories، لكن مفيش contradiction مؤكد لأن توقيت availability مش واضح من الـCSV لوحده. |
| Data Quality Note | `0 missing values`، ومفيش inconsistent labels واضحة. |
| Phase 2 Note | محتاجين نفهم هل availability دي وقت الطلب، وقت التوصيل، ولا status عام قبل استخدامها كـbusiness rule. |

---

## Quick Takeaways

- الـdataset كاملة من ناحية `Missing Values`: كل الأعمدة فيها `0 missing values`.
- مفيش `Exact Full-Row Duplicates`.
- IDs واضحة: `Order_ID` unique، وباقي IDs بتتكرر طبيعي عشان تمثل repeated activity.
- الـtime relationship متماسكة: `Delivery_Time - Order_Time` مطابق لـ`Delivery_Duration_Minutes` في كل الـ`100,002 rows`.
- `Delivery_Distance_km` متسقة بشكل عام مع coordinates، لكن فيه `2 rows` فرقهم أكبر من `0.10 km`، وده يتحط في الاعتبار لو دقة المسافة مهمة.
- Outliers في Phase 1 ظهرت بس في `Delivery_Distance_km`: عددهم `30 rows`، حوالي `0.03%`، وده unusual statistically مش invalid تلقائيًا.
- Latitude/Longitude columns كلها valid من ناحية ranges الأساسية.
- بعض business rules محتاجة confirmation من project context، خصوصًا معنى `Cancelled` و`In Transit` مع وجود delivery timestamps/durations.

## Step 7 Validation

- Columns documented: `23 / 23`
- Source findings preserved: `YES`
- Unsupported assumptions added: `NO`
- RTL formatting: `YES`
- Natural Arabic-English style: `YES`
- Raw dataset modified: `NO`
- Cleaning performed: `NO`
- Step 7 status: `VALIDATED`

</div>
