import streamlit as st

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ ميثاق | Methaq")
st.subheader("المنصة الذكية للتدقيق والامتثال للأنظمة السعودية")

st.write(
    "أدخل نص سياسة الخصوصية، وستقوم المنصة بتحليله "
    "مبدئيًا واكتشاف بعض العناصر المهمة."
)

policy_text = st.text_area(
    "📄 الصق سياسة الخصوصية هنا",
    height=300,
    placeholder="الصق نص سياسة الخصوصية هنا..."
)

if st.button("🔍 ابدأ التدقيق"):

    if not policy_text.strip():
        st.warning("⚠️ الرجاء إدخال نص سياسة الخصوصية أولًا.")

    else:

        requirements = {
            "تحديد البيانات الشخصية التي يتم جمعها": [
                "البيانات الشخصية",
                "بيانات",
                "المعلومات الشخصية"
            ],

            "توضيح الغرض من جمع البيانات": [
                "الغرض",
                "أغراض",
                "استخدام البيانات"
            ],

            "توضيح مدة الاحتفاظ بالبيانات": [
                "الاحتفاظ",
                "تحتفظ",
                "مدة الاحتفاظ",
                "مدة حفظ",
                "حفظ البيانات"
            ],

            "توضيح مشاركة البيانات مع أطراف أخرى": [
                "مشاركة البيانات",
                "مشاركة",
                "أطراف ثالثة"
            ],

            "توضيح حقوق صاحب البيانات": [
                "حقوق",
                "حق الوصول",
                "طلب الوصول",
                "تصحيح البيانات"
            ]
        }

        passed = []
        missing = []

        for requirement, keywords in requirements.items():

            found = any(
                keyword.lower() in policy_text.lower()
                for keyword in keywords
            )

            if found:
                passed.append(requirement)
            else:
                missing.append(requirement)

        score = int((len(passed) / len(requirements)) * 100)

        st.divider()

        st.header("📊 نتيجة التدقيق")

        st.metric(
            "درجة الامتثال المبدئية",
            f"{score}%"
        )

        st.progress(score / 100)

        if score >= 80:
            st.success("🟢 مستوى الامتثال المبدئي جيد.")
        elif score >= 50:
            st.warning("🟡 توجد بعض الجوانب التي تحتاج إلى تحسين.")
        else:
            st.error("🔴 توجد عدة جوانب تحتاج إلى مراجعة.")

        st.subheader("✅ العناصر التي تم العثور عليها")

        if passed:
            for item in passed:
                st.write(f"✅ {item}")
        else:
            st.write("لم يتم العثور على عناصر مطابقة.")

        st.subheader("⚠️ العناصر التي تحتاج إلى مراجعة")

        if missing:
            for item in missing:
                st.write(f"❌ {item}")

            st.info(
                "💡 يُنصح بمراجعة هذه العناصر وإضافة النصوص المناسبة "
                "إلى سياسة الخصوصية."
            )
        else:
            st.success(
                "🎉 تم العثور على جميع العناصر المحددة في النموذج الأولي."
            )

        st.divider()

        st.caption(
            "هذه النتيجة تجريبية لأغراض النموذج الأولي وليست استشارة قانونية "
            "ولا تعني ضمان الامتثال للأنظمة."
        )
