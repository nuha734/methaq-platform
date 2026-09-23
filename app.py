import re
from urllib.parse import urljoin, urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup


# =========================================================
# إعداد الصفحة
# =========================================================

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="wide"
)


# =========================================================
# العنوان
# =========================================================

st.title("⚖️ ميثاق | Methaq")
st.subheader("منصة ذكية للفحص الأولي للامتثال في المتاجر الإلكترونية السعودية")

st.write(
    """
    يساعدك ميثاق على فحص المتجر الإلكتروني وسياسات الخصوصية
    واكتشاف بعض المتطلبات التي قد تحتاج إلى مراجعة.
    """
)

st.info(
    "⚠️ ميثاق نموذج أولي تجريبي. النتائج مؤشر فحص أولي وليست استشارة "
    "قانونية ولا تمثل حكمًا نهائيًا بالامتثال."
)


# =========================================================
# المتطلبات
# =========================================================

PRIVACY_REQUIREMENTS = {

    "تحديد البيانات الشخصية التي يتم جمعها": {
        "keywords": [
            "البيانات الشخصية",
            "المعلومات الشخصية",
            "بيانات العميل",
            "بيانات المستخدم",
            "البيانات التي نجمعها",
            "المعلومات التي نجمعها",
            "نوع البيانات",
            "أنواع البيانات"
        ],
        "suggestion":
            "يوصى بتوضيح أنواع البيانات الشخصية التي يتم جمعها من صاحب البيانات."
    },

    "توضيح الغرض من جمع البيانات": {
        "keywords": [
            "الغرض من جمع",
            "أغراض جمع",
            "أغراض استخدام",
            "الغرض من استخدام",
            "استخدام البيانات",
            "نستخدم البيانات",
            "تستخدم البيانات",
            "أغراض المعالجة",
            "الغرض من المعالجة"
        ],
        "suggestion":
            "يوصى بتوضيح الأغراض التي يتم من أجلها جمع البيانات الشخصية واستخدامها."
    },

    "توضيح طريقة جمع البيانات": {
        "keywords": [
            "طريقة جمع",
            "طرق جمع",
            "كيفية جمع",
            "مصادر البيانات",
            "نجمع البيانات",
            "يتم جمع البيانات",
            "جمع البيانات"
        ],
        "suggestion":
            "يوصى بتوضيح الطريقة أو الوسائل التي يتم من خلالها جمع البيانات الشخصية."
    },

    "توضيح كيفية معالجة البيانات": {
        "keywords": [
            "معالجة البيانات",
            "معالجة المعلومات",
            "نقوم بمعالجة",
            "تتم معالجة",
            "استخدام ومعالجة",
            "عمليات المعالجة"
        ],
        "suggestion":
            "يوصى بتوضيح كيفية معالجة البيانات الشخصية والأغراض المرتبطة بالمعالجة."
    },

    "توضيح وسيلة حفظ وتخزين البيانات": {
        "keywords": [
            "حفظ البيانات",
            "تخزين البيانات",
            "نخزن البيانات",
            "يتم تخزين",
            "تخزين المعلومات",
            "حفظ المعلومات",
            "وسيلة حفظ",
            "مكان تخزين"
        ],
        "suggestion":
            "يوصى بتوضيح كيفية حفظ وتخزين البيانات الشخصية."
    },

    "توضيح مدة الاحتفاظ بالبيانات": {
        "keywords": [
            "مدة الاحتفاظ",
            "فترة الاحتفاظ",
            "مدة حفظ البيانات",
            "فترة حفظ البيانات",
            "نحتفظ بالبيانات",
            "الاحتفاظ بالبيانات",
            "يتم الاحتفاظ",
            "فترة الاحتفاظ"
        ],
        "suggestion":
            "يوصى بتوضيح مدة الاحتفاظ بالبيانات أو المعايير المستخدمة لتحديد مدة الاحتفاظ."
    },

    "توضيح كيفية إتلاف أو حذف البيانات": {
        "keywords": [
            "إتلاف البيانات",
            "إتلاف المعلومات",
            "حذف البيانات",
            "حذف المعلومات",
            "التخلص من البيانات",
            "تدمير البيانات",
            "إتلافها",
            "حذفها"
        ],
        "suggestion":
            "يوصى بتوضيح كيفية إتلاف أو حذف البيانات عند انتهاء الحاجة إليها وفقًا للمتطلبات ذات الصلة."
    },

    "توضيح حقوق صاحب البيانات": {
        "keywords": [
            "حقوق صاحب البيانات",
            "حقوق المستخدم",
            "حقوق العميل",
            "حقوق أصحاب البيانات",
            "حق الوصول",
            "الوصول إلى البيانات",
            "تصحيح البيانات",
            "تعديل البيانات",
            "حذف البيانات",
            "الاعتراض"
        ],
        "suggestion":
            "يوصى بتوضيح حقوق صاحب البيانات المتعلقة ببياناته الشخصية."
    },

    "توضيح طريقة ممارسة حقوق صاحب البيانات": {
        "keywords": [
            "كيفية ممارسة الحقوق",
            "ممارسة حقوقك",
            "ممارسة الحقوق",
            "طلب الوصول",
            "تقديم طلب",
            "طلبات أصحاب البيانات",
            "التواصل لممارسة",
            "لممارسة حقوقك"
        ],
        "suggestion":
            "يوصى بتوضيح الطريقة والقنوات التي يستطيع من خلالها صاحب البيانات ممارسة حقوقه."
    },

    "توضيح المسوغ النظامي لجمع البيانات": {
        "keywords": [
            "المسوغ النظامي",
            "الأساس النظامي",
            "الأساس القانوني",
            "الأساس النظامي لجمع",
            "المسوغ القانوني",
            "الأساس لمعالجة"
        ],
        "suggestion":
            "يوصى بمراجعة بيان المسوغ النظامي أو الأساس الذي يستند إليه جمع أو معالجة البيانات."
    },

    "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات": {
        "keywords": [
            "الإفصاح عن البيانات",
            "الإفصاح عن المعلومات",
            "مشاركة البيانات",
            "مشاركة المعلومات",
            "مشاركة بيانات المستخدم",
            "مشاركة بيانات العملاء",
            "أطراف أخرى",
            "أطراف ثالثة",
            "جهات أخرى",
            "مزودي الخدمات",
            "مقدمي الخدمات",
            "الجهات الحكومية"
        ],
        "suggestion":
            "يوصى بتوضيح الجهات أو الفئات التي قد يتم الإفصاح لها عن البيانات الشخصية."
    },

    "توضيح النقل أو المعالجة خارج المملكة": {
        "keywords": [
            "خارج المملكة",
            "خارج السعودية",
            "نقل البيانات خارج",
            "نقل البيانات إلى الخارج",
            "معالجة خارج المملكة",
            "معالجة خارج السعودية",
            "نقل أو إفصاح",
            "النقل الدولي للبيانات"
        ],
        "suggestion":
            "يوصى بمراجعة ما إذا كانت البيانات تُنقل أو يُفصح عنها أو تُعالج خارج المملكة."
    }
}


# =========================================================
# متطلبات المتجر
# =========================================================

STORE_REQUIREMENTS = {

    "وجود سياسة الخصوصية": {
        "keywords": [
            "سياسة الخصوصية",
            "الخصوصية",
            "privacy policy",
            "privacy"
        ],
        "suggestion":
            "يوصى بتوفير سياسة واضحة لحماية بيانات المستهلك والخصوصية."
    },

    "وجود سياسة الاستبدال والاسترجاع واسترداد الأموال": {
        "keywords": [
            "الاستبدال",
            "الاسترجاع",
            "استرداد الأموال",
            "استرداد المبلغ",
            "سياسة الاسترجاع",
            "سياسة الاستبدال",
            "refund",
            "return policy"
        ],
        "suggestion":
            "يوصى بتوفير سياسة واضحة للاستبدال والاسترجاع واسترداد الأموال."
    },

    "وجود سياسة الشحن والتوصيل": {
        "keywords": [
            "الشحن",
            "التوصيل",
            "سياسة الشحن",
            "سياسة التوصيل",
            "مدة التوصيل",
            "تكلفة الشحن",
            "delivery",
            "shipping"
        ],
        "suggestion":
            "يوصى بتوضيح حقوق وواجبات المستهلك المتعلقة بالشحن والتوصيل."
    },

    "وجود سياسة للشكاوى والمقترحات": {
        "keywords": [
            "الشكاوى",
            "الشكاوى والمقترحات",
            "تقديم شكوى",
            "تقديم الشكوى",
            "الاقتراحات",
            "خدمة العملاء",
            "complaint"
        ],
        "suggestion":
            "يوصى بتوفير آلية واضحة لتقديم الشكاوى والمقترحات ومعالجتها."
    },

    "وجود وسيلة واضحة للتواصل": {
        "keywords": [
            "تواصل معنا",
            "اتصل بنا",
            "خدمة العملاء",
            "البريد الإلكتروني",
            "البريد الالكتروني",
            "رقم الهاتف",
            "واتساب",
            "contact us",
            "email"
        ],
        "suggestion":
            "يوصى بتوفير وسيلة واضحة ومباشرة للتواصل مع المتجر."
    },

    "وجود بيانات المنشأة أو السجل التجاري": {
        "keywords": [
            "السجل التجاري",
            "رقم السجل",
            "السجل",
            "commercial registration",
            "cr number"
        ],
        "suggestion":
            "يوصى بمراجعة ظهور بيانات السجل التجاري أو بيانات المنشأة المطلوبة."
    },

    "وجود الرقم الضريبي": {
        "keywords": [
            "الرقم الضريبي",
            "الرقم الضريبي الموحد",
            "الرقم الضريبي للمنشأة",
            "vat",
            "vat number"
        ],
        "suggestion":
            "يوصى بمراجعة ظهور الرقم الضريبي عند انطباق المتطلب على المنشأة."
    }
}


# =========================================================
# أدوات مساعدة
# =========================================================

def normalize_text(text):
    """تبسيط النص العربي لتقليل اختلافات الكتابة."""
    if not text:
        return ""

    text = text.lower()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ة": "ه",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
        "ـ": ""
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def find_evidence(policy_text, keywords):
    """
    العثور على مقطع من النص يشرح سبب اعتبار المتطلب موجودًا.
    """

    original_text = re.sub(
        r"\s+",
        " ",
        policy_text
    ).strip()

    normalized = normalize_text(original_text)

    for keyword in keywords:

        keyword_normalized = normalize_text(keyword)

        position = normalized.find(
            keyword_normalized
        )

        if position != -1:

            start = max(
                0,
                position - 120
            )

            end = min(
                len(original_text),
                position + len(keyword) + 180
            )

            evidence = original_text[start:end]

            return evidence

    return None


def analyze_requirements(text, requirements):
    """
    تحليل المتطلبات وإرجاع:
    - الموجود
    - غير الموجود
    - الأدلة
    """

    passed = []
    missing = []
    evidence = {}

    normalized_text = normalize_text(text)

    for requirement, details in requirements.items():

        found_keyword = None

        for keyword in details["keywords"]:

            if normalize_text(keyword) in normalized_text:

                found_keyword = keyword
                break

        if found_keyword:

            passed.append(requirement)

            snippet = find_evidence(
                text,
                details["keywords"]
            )

            evidence[requirement] = {
                "keyword": found_keyword,
                "snippet": snippet
            }

        else:

            missing.append(requirement)

    total = len(requirements)

    score = round(
        (len(passed) / total) * 100
    ) if total else 0

    return score, passed, missing, evidence


def get_risk_level(score):

    if score >= 80:
        return "منخفض نسبيًا", "🟢"

    if score >= 60:
        return "متوسط", "🟡"

    return "مرتفع", "🔴"


def get_page_text(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    return soup, soup.get_text(
        " ",
        strip=True
    )


def find_links(soup, base_url):

    links = []

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = link.get("href", "").strip()

        text = link.get_text(
            " ",
            strip=True
        )

        if not href:
            continue

        full_url = urljoin(
            base_url,
            href
        )

        links.append(
            {
                "url": full_url,
                "text": text
            }
        )

    return links


def find_privacy_page(soup, base_url):

    privacy_words = [
        "privacy",
        "privacy-policy",
        "سياسة الخصوصية",
        "الخصوصية"
    ]

    links = find_links(
        soup,
        base_url
    )

    for item in links:

        combined = (
            item["text"] + " " + item["url"]
        ).lower()

        if any(
            word.lower() in combined
            for word in privacy_words
        ):

            return item["url"]

    return None


def find_policy_pages(soup, base_url):

    results = []

    target_words = [
        "return",
        "refund",
        "exchange",
        "استبدال",
        "استرجاع",
        "استرداد",
        "shipping",
        "delivery",
        "الشحن",
        "التوصيل",
        "complaint",
        "شكاوى",
        "شكوى",
        "contact",
        "تواصل",
        "اتصل",
        "privacy",
        "الخصوصية"
    ]

    links = find_links(
        soup,
        base_url
    )

    for item in links:

        combined = (
            item["text"] + " " + item["url"]
        ).lower()

        if any(
            word.lower() in combined
            for word in target_words
        ):

            if item["url"] not in [
                x["url"] for x in results
            ]:

                results.append(item)

    return results


# =========================================================
# واجهة الاختيار
# =========================================================

st.divider()

option = st.radio(
    "اختر طريقة الفحص:",
    [
        "🛒 فحص رابط المتجر",
        "📄 فحص سياسة الخصوصية"
    ],
    horizontal=True
)


# =========================================================
# فحص رابط المتجر
# =========================================================

if option == "🛒 فحص رابط المتجر":

    st.header("🛒 فحص المتجر الإلكتروني")

    store_url = st.text_input(
        "رابط المتجر",
        placeholder="https://example.com"
    )

    st.caption(
        "أدخل الرابط الرئيسي للمتجر، وسيحاول ميثاق قراءة الصفحات العامة "
        "والبحث عن السياسات والبيانات المهمة."
    )

    if st.button(
        "🔍 ابدأ فحص المتجر",
        type="primary"
    ):

        if not store_url.strip():

            st.warning(
                "⚠️ أدخل رابط المتجر أولًا."
            )

        else:

            if not store_url.startswith(
                ("http://", "https://")
            ):

                store_url = "https://" + store_url

            try:

                parsed = urlparse(
                    store_url
                )

                if not parsed.netloc:

                    st.error(
                        "❌ الرابط غير صحيح."
                    )

                    st.stop()

                with st.spinner(
                    "جاري فحص المتجر..."
                ):

                    soup, homepage_text = get_page_text(
                        store_url
                    )

                st.success(
                    "✅ تم الوصول إلى الصفحة الرئيسية."
                )

                # -------------------------------------------------
                # HTTPS
                # -------------------------------------------------

                https_passed = store_url.startswith(
                    "https://"
                )

                # -------------------------------------------------
                # فحص الصفحة الرئيسية
                # -------------------------------------------------

                store_score, store_passed, store_missing, store_evidence = (
                    analyze_requirements(
                        homepage_text,
                        STORE_REQUIREMENTS
                    )
                )

                # -------------------------------------------------
                # البحث عن سياسة الخصوصية
                # -------------------------------------------------

                privacy_url = find_privacy_page(
                    soup,
                    store_url
                )

                privacy_score = None
                privacy_passed = []
                privacy_missing = []
                privacy_evidence = {}

                privacy_text = ""

                if privacy_url:

                    try:

                        with st.spinner(
                            "جاري تحليل سياسة الخصوصية..."
                        ):

                            privacy_soup, privacy_text = get_page_text(
                                privacy_url
                            )

                        privacy_score, privacy_passed, privacy_missing, privacy_evidence = (
                            analyze_requirements(
                                privacy_text,
                                PRIVACY_REQUIREMENTS
                            )
                        )

                    except Exception:

                        privacy_url = None

                # -------------------------------------------------
                # النتيجة العامة
                # -------------------------------------------------

                st.divider()

                st.header("📊 تقرير ميثاق")

                if privacy_score is not None:

                    overall_score = round(
                        (
                            store_score +
                            privacy_score
                        ) / 2
                    )

                else:

                    overall_score = store_score

                risk_text, risk_icon = get_risk_level(
                    overall_score
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "مؤشر الفحص المبدئي",
                        f"{overall_score}%"
                    )

                with col2:

                    st.metric(
                        "مؤشر المتجر",
                        f"{store_score}%"
                    )

                with col3:

                    if privacy_score is not None:

                        st.metric(
                            "مؤشر سياسة الخصوصية",
                            f"{privacy_score}%"
                        )

                    else:

                        st.metric(
                            "سياسة الخصوصية",
                            "غير مكتشفة"
                        )

                st.progress(
                    overall_score / 100
                )

                st.subheader(
                    f"{risk_icon} مستوى المراجعة: {risk_text}"
                )

                # -------------------------------------------------
                # HTTPS
                # -------------------------------------------------

                st.divider()

                st.subheader(
                    "🔐 أمان الرابط"
                )

                if https_passed:

                    st.success(
                        "✅ المتجر يستخدم HTTPS."
                    )

                else:

                    st.error(
                        "❌ الرابط لا يستخدم HTTPS."
                    )

                # -------------------------------------------------
                # سياسة الخصوصية
                # -------------------------------------------------

                st.divider()

                st.header(
                    "🔐 تحليل سياسة الخصوصية"
                )

                if privacy_url:

                    st.success(
                        "✅ تم العثور على صفحة سياسة الخصوصية."
                    )

                    st.write(
                        f"🔗 {privacy_url}"
                    )

                    st.progress(
                        privacy_score / 100
                    )

                    st.subheader(
                        "✅ العناصر التي تم العثور عليها"
                    )

                    for item in privacy_passed:

                        st.write(
                            f"✅ {item}"
                        )

                        if privacy_evidence.get(item):

                            with st.expander(
                                "عرض الدليل النصي"
                            ):

                                st.caption(
                                    privacy_evidence[item]["snippet"]
                                )

                    st.subheader(
                        "⚠️ العناصر التي تحتاج إلى مراجعة"
                    )

                    if privacy_missing:

                        for item in privacy_missing:

                            st.error(
                                f"❌ {item}"
                            )

                            st.info(
                                PRIVACY_REQUIREMENTS[item]["suggestion"]
                            )

                    else:

                        st.success(
                            "🎉 لم يتم العثور على متطلبات مفقودة ضمن قائمة الفحص الحالية."
                        )

                else:

                    st.warning(
                        "⚠️ لم يتم العثور تلقائيًا على صفحة سياسة الخصوصية."
                    )

                    st.info(
                        "يمكنك تجربة فحص سياسة الخصوصية يدويًا من الخيار الآخر."
                    )

                # -------------------------------------------------
                # متطلبات المتجر
                # -------------------------------------------------

                st.divider()

                st.header(
                    "🛍️ متطلبات المتجر"
                )

                st.caption(
                    "هذه نتيجة فحص للصفحة العامة وليست تحققًا رسميًا من الجهات الحكومية."
                )

                st.subheader(
                    "✅ العناصر التي تم العثور عليها"
                )

                for item in store_passed:

                    st.write(
                        f"✅ {item}"
                    )

                    if store_evidence.get(item):

                        with st.expander(
                            "عرض الدليل النصي"
                        ):

                            st.caption(
                                store_evidence[item]["snippet"]
                            )

                st.subheader(
                    "⚠️ العناصر التي تحتاج إلى مراجعة"
                )

                if store_missing:

                    for item in store_missing:

                        st.error(
                            f"❌ {item}"
                        )

                        st.info(
                            STORE_REQUIREMENTS[item]["suggestion"]
                        )

                else:

                    st.success(
                        "🎉 تم العثور على جميع العناصر المحددة في الصفحة المفحوصة."
                    )

                # -------------------------------------------------
                # التحقق الخارجي
                # -------------------------------------------------

                st.divider()

                st.header(
                    "🔎 عناصر تحتاج تحققًا خارجيًا"
                )

                st.warning(
                    """
                    بعض عناصر الامتثال لا يمكن إثباتها بمجرد قراءة الموقع،
                    مثل حالة التوثيق الرسمية أو وجود مخالفات غير مسددة.
                    لذلك يعرضها ميثاق كعناصر تحتاج تحققًا خارجيًا بدل إعطاء نتيجة مضللة.
                    """
                )

                st.write(
                    "• توثيق المتجر في المنصات الرسمية"
                )

                st.write(
                    "• توثيق رابط المتجر في السجل التجاري"
                )

                st.write(
                    "• حالة التراخيص والبيانات الرسمية"
                )

                st.write(
                    "• وجود مخالفات غير مسددة"
                )

                # -------------------------------------------------
                # خلاصة
                # -------------------------------------------------

                st.divider()

                st.header(
                    "📝 خلاصة ميثاق"
                )

                if overall_score >= 80:

                    st.success(
                        "تم العثور على نسبة مرتفعة من العناصر المحددة في الفحص الأولي، "
                        "مع ضرورة مراجعة العناصر التي تتطلب تحققًا خارجيًا."
                    )

                elif overall_score >= 60:

                    st.warning(
                        "تم العثور على جزء من العناصر المحددة، "
                        "وتوجد نقاط تحتاج إلى مراجعة قبل اعتبار المتجر مستوفيًا."
                    )

                else:

                    st.error(
                        "أظهر الفحص الأولي عدة نقاط تحتاج إلى مراجعة."
                    )

            except requests.exceptions.RequestException:

                st.error(
                    "❌ تعذر الوصول إلى المتجر. تأكدي من صحة الرابط وأن الموقع متاح."
                )

            except Exception as error:

                st.error(
                    "❌ حدث خطأ أثناء الفحص."
                )

                st.caption(
                    f"تفاصيل تقنية: {error}"
                )


# =========================================================
# فحص نص سياسة الخصوصية
# =========================================================

else:

    st.header(
        "📄 فحص سياسة الخصوصية"
    )

    policy_text = st.text_area(
        "الصق سياسة الخصوصية هنا",
        height=400,
        placeholder="الصق نص سياسة الخصوصية هنا..."
    )

    if st.button(
        "🔍 ابدأ تحليل السياسة",
        type="primary"
    ):

        if not policy_text.strip():

            st.warning(
                "⚠️ الصق نص سياسة الخصوصية أولًا."
            )

        else:

            score, passed, missing, evidence = (
                analyze_requirements(
                    policy_text,
                    PRIVACY_REQUIREMENTS
                )
            )

            risk_text, risk_icon = get_risk_level(
                score
            )

            st.divider()

            st.header(
                "📊 تقرير ميثاق"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "مؤشر الفحص المبدئي",
                    f"{score}%"
                )

            with col2:

                st.metric(
                    "مستوى المراجعة",
                    f"{risk_icon} {risk_text}"
                )

            st.progress(
                score / 100
            )

            # -------------------------------------------------
            # الموجود
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "✅ المتطلبات التي تم العثور عليها"
            )

            if passed:

                for item in passed:

                    st.success(
                        f"✅ {item}"
                    )

                    if evidence.get(item):

                        with st.expander(
                            "عرض الدليل من النص"
                        ):

                            st.write(
                                evidence[item]["snippet"]
                            )

                            st.caption(
                                "تم اكتشاف هذا المتطلب بناءً على مؤشرات نصية في السياسة."
                            )

            else:

                st.write(
                    "لم يتم العثور على عناصر مطابقة."
                )

            # -------------------------------------------------
            # الناقص
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "⚠️ المتطلبات التي تحتاج إلى مراجعة"
            )

            if missing:

                for item in missing:

                    st.error(
                        f"❌ {item}"
                    )

                    st.info(
                        PRIVACY_REQUIREMENTS[item]["suggestion"]
                    )

            else:

                st.success(
                    "🎉 لم يتم العثور على متطلبات مفقودة ضمن قائمة الفحص الحالية."
                )

            # -------------------------------------------------
            # خلاصة
            # -------------------------------------------------

            st.divider()

            st.header(
                "📝 خلاصة التحليل"
            )

            if score >= 80:

                st.success(
                    "السياسة تحتوي على معظم العناصر التي يبحث عنها النموذج الأولي."
                )

            elif score >= 60:

                st.warning(
                    "السياسة تحتوي على عدد من العناصر، لكنها تحتاج إلى مراجعة إضافية."
                )

            else:

                st.error(
                    "السياسة تحتاج إلى مراجعة عدد من العناصر الأساسية."
                )

            st.caption(
                "ملاحظة: وجود عبارة أو كلمة في السياسة لا يعني وحده تحقق المتطلب نظاميًا؛ "
                "هذا النموذج الأولي يستخدم التحليل النصي للمساعدة في الفحص الأولي."
            )


# =========================================================
# تذييل
# =========================================================

st.divider()

st.caption(
    "⚖️ ميثاق | Methaq — MVP تجريبي للفحص الأولي للامتثال."
)

st.caption(
    "النتائج لا تمثل استشارة قانونية ولا تضمن الامتثال للأنظمة."
)
