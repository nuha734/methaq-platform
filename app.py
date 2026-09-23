
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
    "حل رقمي يساعد المتاجر والمنشآت على المراجعة المبدئية "
    "لسياسات الخصوصية واكتشاف بعض جوانب النقص."
)

option = st.radio(
    "اختر طريقة التدقيق:",
    ["🛒 رابط المتجر", "📄 نص سياسة الخصوصية"]
)

policy_text = ""

# =========================
# خيار رابط المتجر
# =========================

if option == "🛒 رابط المتجر":

    store_url = st.text_input(
        "🔗 أدخل رابط المتجر",
        placeholder="https://example.com"
    )

    if st.button("🔍 فحص المتجر"):

        if not store_url.strip():
            st.warning("⚠️ الرجاء إدخال رابط المتجر.")

        else:

            if not store_url.startswith(("http://", "https://")):
                store_url = "https://" + store_url

            try:

                headers = {
                    "User-Agent": "Mozilla/5.0"
                }

                response = requests.get(
                    store_url,
                    headers=headers,
                    timeout=10
                )

                response.raise_for_status()

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                page_text = soup.get_text(
                    " ",
                    strip=True
                )

                st.success("✅ تم الوصول إلى صفحة المتجر.")

                # البحث عن روابط سياسة الخصوصية
                privacy_link = None

                keywords = [
                    "privacy",
                    "privacy-policy",
                    "سياسة الخصوصية",
                    "الخصوصية"
                ]

                for link in soup.find_all("a", href=True):

                    link_text = link.get_text(
                        " ",
                        strip=True
                    ).lower()

                    href = link.get("href", "").lower()

                    if any(
                        keyword in link_text or keyword in href
                        for keyword in keywords
                    ):
                        privacy_link = urljoin(
                            store_url,
                            link.get("href")
                        )
                        break

                if privacy_link:

                    st.info(
                        "🔎 تم العثور على صفحة سياسة الخصوصية."
                    )

                    try:

                        privacy_response = requests.get(
                            privacy_link,
                            headers=headers,
                            timeout=10
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

                        st.write(
                            f"📄 صفحة السياسة المكتشفة: {privacy_link}"
                        )

                    except Exception:

                        st.warning(
                            "⚠️ تم العثور على صفحة السياسة، "
                            "لكن تعذر قراءتها."
                        )

                else:

                    st.warning(
                        "⚠️ لم يتم العثور تلقائيًا على صفحة سياسة الخصوصية."
                    )

                    st.info(
                        "💡 يمكنك استخدام خيار «نص سياسة الخصوصية» "
                        "ولصق النص يدويًا."
                    )

            except Exception as e:

                st.error(
                    "❌ تعذر الوصول إلى المتجر. "
                    "تأكد من صحة الرابط وأن الموقع متاح."
                )


# =========================
# خيار نص سياسة الخصوصية
# =========================

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

            st.session_state["analyze"] = True


# =========================
# تحليل السياسة
# =========================

if policy_text.strip():

    st.divider()

    st.header("📊 تحليل ميثاق")

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

    text_lower = policy_text.lower()

    for requirement, keywords in requirements.items():

        found = any(
            keyword.lower() in text_lower
            for keyword in keywords
        )

        if found:
            passed.append(requirement)
        else:
            missing.append(requirement)

    score = int(
        (len(passed) / len(requirements)) * 100
    )

    st.metric(
        "درجة الامتثال المبدئية",
        f"{score}%"
    )

    st.progress(score / 100)

    if score >= 80:

        st.success(
            "🟢 مستوى الامتثال المبدئي جيد."
        )

    elif score >= 50:

        st.warning(
            "🟡 توجد بعض الجوانب التي تحتاج إلى تحسين."
        )

    else:

        st.error(
            "🔴 توجد عدة جوانب تحتاج إلى مراجعة."
        )

    st.subheader("✅ العناصر التي تم العثور عليها")

    if passed:

        for item in passed:
            st.write(f"✅ {item}")

    else:

        st.write(
            "لم يتم العثور على عناصر مطابقة."
        )

    st.subheader("⚠️ العناصر التي تحتاج إلى مراجعة")

    if missing:

        for item in missing:
            st.write(f"❌ {item}")

        st.info(
            "💡 يُنصح بمراجعة هذه العناصر وإضافة "
            "النصوص المناسبة إلى سياسة الخصوصية."
        )

    else:

        st.success(
            "🎉 تم العثور على جميع العناصر المحددة "
            "في النموذج الأولي."
        )

    st.divider()

    st.caption(
        "هذه النتيجة تجريبية لأغراض النموذج الأولي "
        "وليست استشارة قانونية ولا تعني ضمان الامتثال."
    )
