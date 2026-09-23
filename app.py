import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ ميثاق | Methaq")
st.subheader("المنصة الذكية للتدقيق والامتثال للأنظمة السعودية")

st.write(
    "منصة أولية تساعد المنشآت والمتاجر على مراجعة "
    "سياسات الخصوصية واكتشاف بعض جوانب النقص."
)

# ==========================================
# المتطلبات التي يبحث عنها النموذج الأولي
# ==========================================

requirements = {
    "تحديد البيانات الشخصية التي يتم جمعها": {
        "keywords": [
            "البيانات الشخصية",
            "بيانات",
            "المعلومات الشخصية"
        ],
        "suggestion": "يوصى بتوضيح أنواع البيانات الشخصية التي يتم جمعها من المستخدم."
    },

    "توضيح الغرض من جمع البيانات": {
        "keywords": [
            "الغرض",
            "أغراض",
            "استخدام البيانات"
        ],
        "suggestion": "يوصى بتوضيح الأغراض التي يتم من أجلها جمع واستخدام البيانات."
    },

    "توضيح مدة الاحتفاظ بالبيانات": {
        "keywords": [
            "الاحتفاظ",
            "تحتفظ",
            "مدة الاحتفاظ",
            "مدة حفظ",
            "حفظ البيانات"
        ],
        "suggestion": "يوصى بتوضيح مدة الاحتفاظ بالبيانات أو المعايير المستخدمة لتحديد مدة الاحتفاظ."
    },

    "توضيح مشاركة البيانات مع أطراف أخرى": {
        "keywords": [
            "مشاركة البيانات",
            "مشاركة",
            "أطراف ثالثة"
        ],
        "suggestion": "يوصى بتوضيح ما إذا كانت البيانات تتم مشاركتها مع أطراف أخرى والجهات ذات العلاقة."
    },

    "توضيح حقوق صاحب البيانات": {
        "keywords": [
            "حقوق",
            "حق الوصول",
            "طلب الوصول",
            "تصحيح البيانات"
        ],
        "suggestion": "يوصى بتوضيح حقوق صاحب البيانات وطريقة ممارسة هذه الحقوق."
    }
}


# ==========================================
# دالة التحليل
# ==========================================

def analyze_policy(policy_text):

    passed = []
    missing = []

    text_lower = policy_text.lower()

    for requirement, details in requirements.items():

        found = any(
            keyword.lower() in text_lower
            for keyword in details["keywords"]
        )

        if found:
            passed.append(requirement)
        else:
            missing.append(requirement)

    score = int(
        (len(passed) / len(requirements)) * 100
    )

    return score, passed, missing


# ==========================================
# اختيار طريقة التدقيق
# ==========================================

option = st.radio(
    "اختر طريقة التدقيق:",
    [
        "🛒 رابط المتجر",
        "📄 نص سياسة الخصوصية"
    ]
)


# ==========================================
# رابط المتجر
# ==========================================

if option == "🛒 رابط المتجر":

    store_url = st.text_input(
        "🔗 أدخل رابط المتجر",
        placeholder="https://example.com"
    )

    if st.button("🔍 فحص المتجر"):

        if not store_url.strip():

            st.warning(
                "⚠️ الرجاء إدخال رابط المتجر."
            )

        else:

            if not store_url.startswith(
                ("http://", "https://")
            ):
                store_url = "https://" + store_url

            try:

                headers = {
                    "User-Agent": "Mozilla/5.0"
                }

                response = requests.get(
                    store_url,
                    headers=headers,
                    timeout=15
                )

                response.raise_for_status()

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                st.success(
                    "✅ تم الوصول إلى المتجر."
                )

                privacy_link = None

                keywords = [
                    "privacy",
                    "privacy-policy",
                    "سياسة الخصوصية",
                    "الخصوصية"
                ]

                for link in soup.find_all(
                    "a",
                    href=True
                ):

                    link_text = link.get_text(
                        " ",
                        strip=True
                    ).lower()

                    href = link.get(
                        "href",
                        ""
                    ).lower()

                    if any(
                        keyword in link_text
                        or keyword in href
                        for keyword in keywords
                    ):

                        privacy_link = urljoin(
                            store_url,
                            link.get("href")
                        )

                        break

                if privacy_link:

                    st.success(
                        "📄 تم العثور على صفحة سياسة الخصوصية."
                    )

                    st.write(
                        f"🔗 صفحة السياسة: {privacy_link}"
                    )

                    try:

                        privacy_response = requests.get(
                            privacy_link,
                            headers=headers,
                            timeout=15
                        )

                        privacy_response.raise_for_status()

                        privacy_soup = BeautifulSoup(
                            privacy_response.text,
                            "html.parser"
                        )

                        policy_text = privacy_soup.get_text(
                            " ",
                            strip=True
                        )

                        # التحليل
                        score, passed, missing = analyze_policy(
                            policy_text
                        )

                        st.divider()

                        st.header("📊 تقرير ميثاق")

                        st.metric(
                            "درجة الامتثال المبدئية",
                            f"{score}%"
                        )

                        st.progress(
                            score / 100
                        )

                        # حالة الدرجة
                        if score >= 80:

                            st.success(
                                "🟢 تم العثور على معظم العناصر المحددة."
                            )

                        elif score >= 50:

                            st.warning(
                                "🟡 توجد بعض العناصر التي تحتاج إلى مراجعة."
                            )

                        else:

                            st.error(
                                "🔴 توجد عدة عناصر تحتاج إلى مراجعة."
                            )

                        # الموجود
                        st.subheader(
                            "✅ العناصر التي تم العثور عليها"
                        )

                        if passed:

                            for item in passed:
                                st.write(
                                    f"✅ {item}"
                                )

                        else:

                            st.write(
                                "لم يتم العثور على عناصر مطابقة."
                            )

                        # الناقص
                        st.subheader(
                            "⚠️ العناصر التي تحتاج إلى مراجعة"
                        )

                        if missing:

                            for item in missing:

                                st.write(
                                    f"❌ {item}"
                                )

                                st.info(
                                    requirements[item]["suggestion"]
                                )

                        else:

                            st.success(
                                "🎉 تم العثور على جميع العناصر المحددة."
                            )

                    except Exception:

                        st.error(
                            "❌ تم العثور على صفحة الخصوصية "
                            "لكن تعذر تحليل محتواها."
                        )

                else:

                    st.warning(
                        "⚠️ لم يتم العثور تلقائيًا "
                        "على صفحة سياسة الخصوصية."
                    )

                    st.info(
                        "💡 يمكنك استخدام خيار "
                        "«نص سياسة الخصوصية» وإدخال النص يدويًا."
                    )

            except Exception:

                st.error(
                    "❌ تعذر الوصول إلى المتجر. "
                    "تأكد من صحة الرابط وأن الموقع متاح."
                )


# ==========================================
# نص سياسة الخصوصية
# ==========================================

else:

    policy_text = st.text_area(
        "📄 الصق سياسة الخصوصية هنا",
        height=300,
        placeholder="الصق نص سياسة الخصوصية هنا..."
    )

    if st.button("🔍 ابدأ التدقيق"):

        if not policy_text.strip():

            st.warning(
                "⚠️ الرجاء إدخال نص سياسة الخصوصية أولًا."
            )

        else:

            score, passed, missing = analyze_policy(
                policy_text
            )

            st.divider()

            st.header("📊 تقرير ميثاق")

            st.metric(
                "درجة الامتثال المبدئية",
                f"{score}%"
            )

            st.progress(
                score / 100
            )

            if score >= 80:

                st.success(
                    "🟢 تم العثور على معظم العناصر المحددة."
                )

            elif score >= 50:

                st.warning(
                    "🟡 توجد بعض العناصر التي تحتاج إلى مراجعة."
                )

            else:

                st.error(
                    "🔴 توجد عدة عناصر تحتاج إلى مراجعة."
                )

            st.subheader(
                "✅ العناصر التي تم العثور عليها"
            )

            for item in passed:

                st.write(
                    f"✅ {item}"
                )

            st.subheader(
                "⚠️ العناصر التي تحتاج إلى مراجعة"
            )

            if missing:

                for item in missing:

                    st.write(
                        f"❌ {item}"
                    )

                    st.info(
                        requirements[item]["suggestion"]
                    )

            else:

                st.success(
                    "🎉 تم العثور على جميع العناصر المحددة."
                )


# ==========================================
# تنبيه النموذج الأولي
# ==========================================

st.divider()

st.caption(
    "⚠️ ميثاق نموذج أولي تجريبي. "
    "النتائج لا تمثل استشارة قانونية ولا تضمن الامتثال للأنظمة."
)
