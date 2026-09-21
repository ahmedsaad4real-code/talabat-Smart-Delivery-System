<div dir="rtl">

# Initial Data Understanding Report — Phase 1

## 1. إحنا بنبص على إيه؟

الـproject dataset اللي اشتغلنا عليه هو `Order_delivery.csv`.

في Phase 1 كان الهدف الأساسي إننا نفهم الـraw dataset كويس قبل ما نلمس أي value أو نبدأ Cleaning. يعني عرفنا شكل الداتا، كل column بيمثل إيه، إيه حالة الـData Quality، وإيه العلاقات المهمة بين الأعمدة.

الـraw dataset فيها:

- `100,002 rows`
- `23 columns`
- CSV file
- UTF-8 encoding
- comma `,` delimiter

والـraw file نفسه ما اتعدلش أثناء Phase 1.

---

## 2. الصورة السريعة للـDataset

الداتا عبارة عن order/delivery records، وكل row بتمثل order واحدة، وفيها معلومات عن:

- الـorder والـentities المرتبطة بيها
- item وquantity وprice
- order/delivery times
- delivery duration
- city وpayment method وorder status
- driver والـvehicle
- restaurant/customer/driver locations
- delivery distance
- traffic وdriver availability

من ناحية structure، عندنا `Order_ID` unique لكل row، بينما `User_ID`, `Restaurant_ID`, و`Driver_ID` بيتكرروا لأن نفس user أو restaurant أو driver ممكن يظهر في أكتر من order.

وده مهم جدًا: **repeated IDs هنا مش معناها duplicate rows.**

---

## 3. فهم الـColumns

اتراجعنا على كل الـ23 columns، وحددنا لكل واحدة الـcurrent dtype والـlogical type والاستخدام المتوقع.

أهم الحاجات اللي طلعت:

- الـIDs: `Order_ID`, `User_ID`, `Restaurant_ID`, `Driver_ID`
- الـcategorical columns الأساسية: `City`, `Payment_Method`, `Order_Status`, `Driver_Vehicle`, `Traffic_Level`, `Driver_Availability`
- `Item_Name` فيه `9` values وبيتصرف عمليًا كـcategorical/text
- `Quantity` من `1` لـ`5`
- `Total_Price` من `30.0` لـ`750.0`
- `Delivery_Duration_Minutes` من `15` لـ`60`
- `Order_Time` و`Delivery_Time` مقروءين حاليًا كـ`str`، لكن منطقيًا هما `Datetime`
- الـLatitude/Longitude columns مقروءة كـ`float64` وده مناسب لطبيعتها
- `Delivery_Distance_km` continuous numerical variable

التفاصيل الكاملة لكل column موجودة في الـData Dictionary.

---

## 4. Data Quality — هل الداتا فيها مشاكل واضحة؟

### Missing Values

دي من أنظف الحاجات اللي ظهرت في الفحص:

- Total Missing Values = `0`
- Columns with Missing Values = `0`
- كل الـ23 columns فيها `100,002` non-missing values.

يعني من ناحية الـmissingness، مفيش حاجة محتاجة treatment.

### Exact Duplicates

عملنا check على الـfull row بكل الـ23 columns.

النتيجة:

- Unique rows = `100,002`
- Exact Full-Row Duplicates = `0`
- Duplicate percentage = `0.000000%`

فمفيش duplicate cleaning مطلوب بناءً على الفحص ده.

وبرضه تكرار `User_ID` أو `Restaurant_ID` أو `Driver_ID` مش بنعتبره duplicate، لأن ده جزء طبيعي من شكل الداتا.

---

## 5. Value-Level Inspection

بعد ما بصّينا على الـunique values والـcategories، مفيش مشكلة واضحة في الـlabels.

الـcategorical values الأساسية كانت:

- `City`: `7` cities
- `Payment_Method`: `Cash`, `Credit Card`, `Wallet`
- `Order_Status`: `Delivered`, `Cancelled`, `In Transit`
- `Driver_Vehicle`: `Bicycle`, `Car`, `Motorbike`
- `Traffic_Level`: `Low`, `Medium`, `High`
- `Driver_Availability`: `Online`, `Offline`

ومفيش obvious signs of:

- spelling/capitalization variants
- leading/trailing spaces
- suspicious placeholders زي `Unknown`, `N/A`, `-`

كمان الـbasic numerical/geographic sanity checks ما أظهرتش values مستحيلة بشكل واضح.

---

## 6. Preliminary Outliers

عملنا preliminary IQR screening على الأربع variables اللي مفهوم الـoutlier ينطبق عليها بشكل مباشر:

- `Quantity`
- `Total_Price`
- `Delivery_Duration_Minutes`
- `Delivery_Distance_km`

النتيجة:

| Column | IQR Flags |
| --- | ---: |
| `Quantity` | `0` |
| `Total_Price` | `0` |
| `Delivery_Duration_Minutes` | `0` |
| `Delivery_Distance_km` | `30` |

الـ30 flagged values في `Delivery_Distance_km` بيمثلوا تقريبًا `0.03%` من الداتا.

المهم هنا إن:

**Outlier ≠ Invalid Value**

يعني الـ30 values unusual statistically، لكن مفيش دليل كافي إنها غلط. أعلى distance موجودة هي `5.597928 km`، وده مش رقم مستحيل من غير business context إضافي.

لذلك ماعملناش أي deletion أو modification.

وبالنسبة للـcoordinates، عدد الـinvalid latitude/longitude values كان `0`.

---

## 7. العلاقات المهمة بين الـColumns

### Order / Entity Relationships

`Order_ID` unique لكل row.

وفي المقابل:

- `9,000` users
- `1,000` restaurants
- `500` drivers

وده معناه إن الـdataset بتسجل repeated activity لنفس الـentities على مدار orders مختلفة.

---

### Time Relationship

العلاقة الأساسية:

`Order_Time → Delivery_Time → Delivery_Duration_Minutes`

الـtimestamps اتعمل لها parsing بدون failures، ومفيش حالة واحدة فيها `Delivery_Time` قبل `Order_Time`.

الأهم إن الفرق بين `Delivery_Time` و`Order_Time` متطابق مع `Delivery_Duration_Minutes` في كل:

`100,002 rows`

يعني من الناحية دي مفيش duration mismatch محتاج cleaning.

---

### Geographic / Distance Relationship

اتحسبت Haversine distance بين restaurant وcustomer coordinates، واتقارنت بالـ`Delivery_Distance_km`.

النتيجة كانت متوافقة جدًا بشكل عام:

- `100,000` rows داخل فرق `0.10 km`
- `2` rows فقط فوق فرق `0.10 km`
- mean absolute difference = `0.003671 km`

فـ`Delivery_Distance_km` شكلها broadly consistent مع الـcoordinates.

الـ2 rows دول مجرد cases تستحق review later لو precision بتاعة distance هتفرق في التحليل.

---

### Business Logic Relationships

فيه observation محتاجة business context:

`Cancelled` و`In Transit` rows عندها `Delivery_Time` و`Delivery_Duration_Minutes`.

ده ممكن يبان unusual، لكن مش هنقول إنه error؛ لأن الـCSV لوحده مش بيحدد business rule واضح يشرح معنى `Delivery_Time` في كل status.

نفس الفكرة مع `Driver_Availability`: الـOnline والـOffline موجودين مع كل أنواع `Order_Status`، لكن مش واضح من الداتا لو availability بتشير للحظة الطلب، لحظة التوصيل، ولا status عام.

فدي **semantic questions** مش data errors مؤكدة.

---

## 8. إيه اللي طلعنا بيه من Phase 1؟

بعد الفحص، الصورة العامة كالتالي:

- الـdataset كاملة من ناحية missing values.
- مفيش exact full-row duplicates.
- الـIDs واضحة ومفهوم استخدامها.
- الـcategorical labels شكلها consistent.
- الـnumeric ranges اللي اتفحصت مفيهاش impossible values واضحة.
- الـtime relationship قوية جدًا ومتطابقة في كل الـrows.
- الـdistance relationship متماسكة جدًا مع restaurant/customer coordinates.
- فيه عدد صغير جدًا من unusual `Delivery_Distance_km` values، لكن مش عندنا دليل إنها invalid.
- فيه شوية business semantics محتاجة clarification قبل ما ناخد cleaning decisions عليها.

---

## 9. Phase 2 Considerations

إحنا لسه **ماعملناش Cleaning**، لكن Phase 1 بينت لنا شوية حاجات ناخد بالنا منها لما نبدأ:

1. `Order_Time` و`Delivery_Time` غالبًا محتاجين يتحولوا لـ`Datetime` لو هنستخدمهم في time analysis.
2. الـIDs لازم تفضل identifiers، وماتدخلش كـnumerical measures.
3. الـ30 IQR flags في `Delivery_Distance_km` محتاجين review قبل أي قرار حذف أو treatment.
4. الـ2 rows اللي عندها فرق أكبر من `0.10 km` بين calculated Haversine distance والـreported distance ممكن تتراجع لو distance precision مهمة.
5. معنى `Delivery_Time` في `Cancelled` و`In Transit` محتاج business rule واضح قبل أي cleaning.
6. معنى `Driver_Availability` محتاج يتحدد بالنسبة للـevent/time المقصود.

**مفيش حاجة من دول اتصلحت في Phase 1.** هي بس points هنرجع لها في Phase 2 لو كانت مؤثرة فعلًا في التحليل.

---

## 10. Conclusion

بشكل عام، الـraw dataset حالتها كويسة جدًا من ناحية الـbasic data quality checks اللي عملناها.

مفيش Missing Values، مفيش Exact Duplicates، والـvalues والـrelationships الأساسية متماسكة. أهم حاجتين محتاجين attention بعدين هما الـsmall set of unusual delivery distances وبعض الـbusiness semantics اللي مش ممكن نحكم عليها من الـCSV لوحده.

وبالتالي إحنا دلوقتي فاهمين شكل الداتا والعلاقات الأساسية بما يكفي إننا ندخل Phase 2 بشكل منظم، **من غير ما نكون عملنا Cleaning أو غيرنا الـraw data أثناء Phase 1.**

---

## Phase 1 Validation

| Item | Status |
| --- | --- |
| Raw dataset verified | ✅ |
| All 23 columns understood | ✅ |
| Missing Values checked | ✅ |
| Exact Duplicates checked | ✅ |
| Unique Values inspected | ✅ |
| Preliminary Outliers checked | ✅ |
| Column Relationships checked | ✅ |
| Data Dictionary prepared | ✅ |
| Raw Dataset modified | ❌ |
| Cleaning performed | ❌ |
| EDA performed | ❌ |
| Phase 1 | **READY FOR HANDOFF** |

</div>
