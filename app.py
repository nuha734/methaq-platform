import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="wide"
)


# =========================================================
# إعدادات عامة
# =========================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


# =========================================================
# أدوات تنظيف وتحليل النص
# =========================================================

def normalize_text(text):
    if not text:
        return ""

    text = text.lower()

    # توحيد أشكال الهمزات
    text = text.replace("أ", "ا")
    text = text.replace("إ", "ا")
    text = text.replace("آ", "ا")

    # إزالة التشكيل
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)

    # توحيد المسافات
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text):
    if not text:
        return []

    parts = re.split(r"[.!؟?\n\r؛;]+", text)

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def contains_any(text, patterns):
    normalized = normalize_text(text)

    for pattern in patterns:
        if isinstance(pattern, list):
            if all(normalize_text(x) in normalized for x in pattern):
                return True
        else:
            if normalize_text(pattern) in normalized:
                return True

    return False


def find_evidence(text, patterns):
    """
    البحث عن الجملة التي تحتوي على دليل مرتبط بالمتطلب.
    """
    sentences = split_sentences(text)

    for sentence in sentences:
        if contains_any(sentence, patterns):
            return sentence

    return None


# =========================================================
# قواعد الخصوصية
# =========================================================

PRIVACY_RULES = [
    {
        "name": "تحديد البيانات الشخصية التي يتم جمعها",
        "patterns": [
            ["البيانات", "الاسم"],
            ["البيانات", "رقم الجوال"],
            ["البيانات", "البريد الالكتروني"],
            ["البيانات", "عنوان"],
            ["نجمع", "البيانات"],
            ["جمع", "البيانات الشخصية"],
            "البيانات الشخصية تشمل",
            "البيانات التي قد نجمعها",
            "المعلومات التي نجمعها"
        ]
    },

    {
        "name": "توضيح الغرض من جمع البيانات",
        "patterns": [
            ["نستخدم", "البيانات", "تنفيذ الطلبات"],
            ["نستخدم", "البيانات", "تقديم الخدمات"],
            ["الغرض", "البيانات"],
            ["اغراض", "جمع البيانات"],
            ["لغرض", "البيانات"],
            ["تستخدم البيانات", "الخدمات"],
            ["تستخدم البيانات", "الطلبات"],
            ["معالجة", "المدفوعات"],
            ["تحسين", "تجربة المستخدم"],
            "تنفيذ الطلبات وتقديم الخدمات",
            "لتقديم الخدمات",
            "لتحسين خدمات المتجر"
        ]
    },

    {
        "name": "توضيح طريقة جمع البيانات",
        "patterns": [
            ["يتم جمع", "البيانات"],
            ["نقوم بجمع", "البيانات"],
            ["نجمع البيانات", "من خلال"],
            ["جمع البيانات", "من خلال"],
            ["طريقة جمع", "البيانات"],
            ["وسائل جمع", "البيانات"],
            ["النماذج الالكترونية", "البيانات"],
            ["عمليات الشراء", "البيانات"],
            ["تسجيل المستخدم", "البيانات"],
            ["التواصل مع خدمة العملاء", "البيانات"]
        ]
    },

    {
        "name": "توضيح كيفية معالجة البيانات",
        "patterns": [
            ["تتم معالجة", "البيانات"],
            ["معالجة البيانات الشخصية"],
            ["نقوم بمعالجة", "البيانات"],
            ["كيفية معالجة", "البيانات"],
            ["معالجة", "البيانات", "تقديم الخدمات"],
            ["معالجة", "البيانات", "تنفيذ الطلبات"],
            ["معالجة المدفوعات"],
            ["اغراض المعالجة"],
            ["أوجه المعالجة"]
        ]
    },

    {
        "name": "توضيح وسيلة حفظ وتخزين البيانات",
        "patterns": [
            ["حفظ", "البيانات"],
            ["تخزين", "البيانات"],
            ["حفظ البيانات", "انظمة"],
            ["تخزين البيانات", "انظمة"],
            ["يتم حفظ", "البيانات"],
            ["يتم تخزين", "البيانات"],
            ["انظمة الكترونية", "البيانات"],
            ["وسيلة حفظ", "البيانات"],
            ["طريقة تخزين", "البيانات"]
        ]
    },

    {
        "name": "توضيح مدة الاحتفاظ بالبيانات",
        "patterns": [
            ["نحتفظ", "البيانات"],
            ["المدة اللازمة", "البيانات"],
            ["مدة الاحتفاظ", "البيانات"],
            ["مدة حفظ", "البيانات"],
            ["يتم الاحتفاظ", "البيانات"],
            ["للمدة التي", "البيانات"],
            ["المدة التي تقتضيها", "الانظمة"],
            ["حتى انتهاء", "الحاجة"],
            ["انتهاء الحاجة", "البيانات"]
        ]
    },

    {
        "name": "توضيح كيفية إتلاف أو حذف البيانات",
        "patterns": [
            ["يتم حذف", "البيانات"],
            ["حذف البيانات"],
            ["اتلاف", "البيانات"],
            ["يتم اتلاف", "البيانات"],
            ["حذفها", "البيانات"],
            ["اتلافها", "البيانات"],
            ["انتهاء الحاجة", "حذف"],
            ["انتهاء الحاجة", "اتلاف"],
            ["طريقة امنة", "حذف"],
            ["طريقة امنة", "اتلاف"]
        ]
    },

    {
        "name": "توضيح حقوق صاحب البيانات",
        "patterns": [
            ["حقوق صاحب البيانات"],
            ["يحق لصاحب البيانات"],
            ["يتمتع صاحب البيانات"],
            ["حقوق المستخدم"],
            ["حقوق العميل"],
            ["الوصول", "بياناته"],
            ["تصحيح", "بياناته"],
            ["تحديث", "بياناته"],
            ["حذف", "بياناته"],
            ["الاعتراض", "المعالجة"]
        ]
    },

    {
        "name": "توضيح طريقة ممارسة حقوق صاحب البيانات",
        "patterns": [
            ["ممارسة حقوقه"],
            ["ممارسة حقوقها"],
            ["ممارسة حقوقك"],
            ["ممارسة حقوق", "التواصل"],
            ["ممارسة حقوق", "البريد الالكتروني"],
            ["حقوقه", "التواصل"],
            ["حقوقه", "البريد الالكتروني"],
            ["حقوقه", "وسائل التواصل"],
            ["يمكن لصاحب البيانات", "التواصل"],
            ["طلب", "من خلال التواصل"]
        ]
    },

    {
        "name": "توضيح المسوغ النظامي لجمع أو معالجة البيانات",
        "patterns": [
            ["وفق النظام"],
            ["وفقا للنظام"],
            ["وفق الانظمة"],
            ["وفقا للانظمة"],
            ["المتطلبات النظامية"],
            ["الضوابط النظامية"],
            ["المتطلبات والضوابط النظامية"],
            ["الاساس النظامي"],
            ["المسوغ النظامي"],
            ["الالتزام بالانظمة"],
            ["الالتزام بالمتطلبات النظامية"],
            ["بموجب النظام"],
            ["بموجب الانظمة"],
            ["وفقا للمتطلبات"],
            ["وفق الضوابط"]
        ]
    },

    {
        "name": "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات",
        "patterns": [
            ["يتم الافصاح", "البيانات"],
            ["قد يتم الافصاح", "البيانات"],
            ["الافصاح عن", "البيانات"],
            ["مشاركة", "البيانات"],
            ["مشاركة بعض البيانات"],
            ["مقدمي الخدمات"],
            ["الجهات", "البيانات"],
            ["الجهات ذات العلاقة"],
            ["اطراف اخرى", "البيانات"],
            ["الاطراف", "البيانات"]
        ]
    },

    {
        "name": "توضيح النقل أو المعالجة خارج المملكة",
        "patterns": [
            ["خارج المملكة"],
            ["خارج المملكه"],
            ["نقل", "خارج المملكة"],
            ["نقل البيانات", "خارج"],
            ["معالجة", "خارج المملكة"],
            ["معالجة البيانات", "خارج"],
            ["نقل او معالجة", "خارج"],
            ["نقل أو معالجة", "خارج"],
            ["نقل البيانات الى الخارج"],
            ["معالجة البيانات خارج المملكة"]
        ]
    }
]


# =========================================================
# تحليل متطلبات الخصوصية
# =========================================================

def analyze_privacy(text):
    results = []

    normalized_full = normalize_text(text)
    sentences = split_sentences(text)

    for rule in PRIVACY_RULES:

        matched_sentences = []
        matched_patterns = 0

        for sentence in sentences:
            sentence_matches = 0

            for pattern in rule["patterns"]:
                if contains_any(sentence, [pattern]):
                    sentence_matches += 1

            if sentence_matches > 0:
                matched_sentences.append(sentence)
                matched_patterns += sentence_matches

        # البحث أيضًا في النص الكامل
        full_matches = 0

        for pattern in rule["patterns"]:
            if contains_any(normalized_full, [pattern]):
                full_matches += 1

        # -----------------------------------------
        # تحديد مستوى الثقة
        # -----------------------------------------

        if matched_sentences:

            # وجود أكثر من مؤشر مستقل
            if matched_patterns >= 2:
                status = "🟢"
                label = "مؤشر واضح"

            else:
                status = "🟡"
                label = "يحتاج مراجعة"

        elif full_matches >= 2:
            status = "🟢"
            label = "مؤشر واضح"

        elif full_matches == 1:
            status = "🟡"
            label = "يحتاج مراجعة"

        else:
            status = "🔴"
            label = "لم يتم العثور على مؤشر كافٍ"

        evidence = None

        if matched_sentences:
            evidence = matched_sentences[0]

        results.append({
            "name": rule["name"],
            "status": status,
            "label": label,
            "evidence": evidence
        })

    return results


# =========================================================
# قواعد فحص المتجر
# =========================================================

STORE_RULES = [
    {
        "name": "وجود سياسة الخصوصية",
        "patterns": [
            "سياسة الخصوصية",
            "سياسات الخصوصية",
            "الخصوصية",
            "privacy policy",
            "privacy"
        ]
    },

    {
        "name": "وجود سياسة الاستبدال والاسترجاع واسترداد الأموال",
        "patterns": [
            "الاستبدال",
            "الاسترجاع",
            "الارجاع",
            "استرداد الأموال",
            "استرداد المبلغ",
            "استرجاع المبلغ",
            "سياسة الاسترجاع",
            "سياسة الاستبدال",
            "refund",
            "returns",
            "return policy"
        ]
    },

    {
        "name": "وجود سياسة الشحن والتوصيل",
        "patterns": [
            "الشحن",
            "التوصيل",
            "الشحن والتوصيل",
            "سياسة الشحن",
            "مواعيد التوصيل",
            "delivery",
            "shipping"
        ]
    },

    {
        "name": "وجود سياسة الشكاوى والمقترحات",
        "patterns": [
            "الشكاوى",
            "الشكاوي",
            "المقترحات",
            "تقديم شكوى",
            "تقديم الشكاوى",
            "خدمة العملاء",
            "complaints"
        ]
    },

    {
        "name": "وجود بيانات التواصل",
        "patterns": [
            "تواصل معنا",
            "اتصل بنا",
            "معلومات التواصل",
            "بيانات التواصل",
            "خدمة العملاء",
            "البريد الإلكتروني",
            "البريد الالكتروني",
            "رقم الهاتف",
            "واتساب",
            "contact us",
            "contact"
        ]
    },

    {
        "name": "وجود بيانات المنشأة أو السجل التجاري",
        "patterns": [
            "السجل التجاري",
            "سجل تجاري",
            "رقم السجل",
            "رقم السجل التجاري",
            "بيانات المنشأة",
            "اسم المنشأة",
            "المنشأة",
            "الرقم الموحد",
            "commercial registration",
            "cr number"
        ]
    },

    {
        "name": "وجود الرقم الضريبي",
        "patterns": [
            "الرقم الضريبي",
            "رقم ضريبي",
            "الرقم المميز",
            "ضريبة القيمة المضافة",
            "vat",
            "vat number",
            "tax number"
        ]
    }
]


# =========================================================
# جلب الموقع
# =========================================================

def fetch_page(url):
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        return response.text

    except Exception:
        return None


def extract_page_data(html, base_url):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    page_text = soup.get_text(" ", strip=True)

    links = []

    for a in soup.find_all("a", href=True):

        text = a.get_text(" ", strip=True)

        href = a.get("href")

        if not href:
            continue

        absolute_url = urljoin(base_url, href)

        links.append({
            "text": text,
            "url": absolute_url
        })

    return page_text, links


# =========================================================
# اكتشاف صفحة الخصوصية
# =========================================================

def find_privacy_page(home_url, html):
    page_text, links = extract_page_data(
        html,
        home_url
    )

    privacy_words = [
        "سياسة الخصوصية",
        "سياسات الخصوصية",
        "الخصوصية",
        "privacy policy",
        "privacy"
    ]

    for link in links:

        combined = normalize_text(
            f"{link['text']} {link['url']}"
        )

        for word in privacy_words:

            if normalize_text(word) in combined:

                return link["url"]

    return None


# =========================================================
# تحليل المتجر
# =========================================================

def analyze_store(home_url, html):

    page_text, links = extract_page_data(
        html,
        home_url
    )

    combined_text = page_text + " "

    for link in links:

        combined_text += " "
        combined_text += link["text"]
        combined_text += " "
        combined_text += link["url"]

    results = []

    for rule in STORE_RULES:

        found = contains_any(
            combined_text,
            rule["patterns"]
        )

        if found:

            results.append({
                "name": rule["name"],
                "status": "🟢",
                "label": "مؤشر واضح"
            })

        else:

            results.append({
                "name": rule["name"],
                "status": "⚪",
                "label": "لم يتم العثور على مؤشر كافٍ"
            })

    return results


# =========================================================
# المؤشرات الخارجية
# =========================================================

EXTERNAL_CHECKS = [
    "التحقق من صحة السجل التجاري",
    "التحقق من الرقم الضريبي عند انطباقه",
    "التحقق من بيانات المنشأة من مصدر رسمي",
    "التحقق من أي تراخيص أو متطلبات خاصة بنشاط المتجر"
]


# =========================================================
# حساب النسب
# =========================================================

def calculate_privacy_score(results):

    if not results:
        return 0

    score = 0

    for result in results:

        if result["status"] == "🟢":
            score += 1

        elif result["status"] == "🟡":
            score += 0.5

    return round(
        (score / len(results)) * 100
    )


def calculate_store_score(results):

    if not results:
        return 0

    score = sum(
        1
        for result in results
        if result["status"] == "🟢"
    )

    return round(
        (score / len(results)) * 100
    )


# =========================================================
# واجهة ميثاق
# =========================================================

st.title("⚖️ ميثاق | Methaq")

st.write(
    "منصة أولية لفحص مؤشرات الخصوصية والامتثال في المتاجر الإلكترونية."
)

st.info(
    "نتائج ميثاق مؤشرات فحص أولية وليست حكمًا قانونيًا أو استشارة قانونية."
)


tab1, tab2 = st.tabs([
    "🔎 فحص متجر",
    "📄 فحص سياسة الخصوصية"
])


# =========================================================
# فحص المتجر
# =========================================================

with tab1:

    st.subheader("🔎 فحص متجر إلكتروني")

    store_url = st.text_input(
        "أدخل رابط المتجر",
        placeholder="https://example.com"
    )

    if st.button(
        "بدء فحص المتجر",
        type="primary"
    ):

        if not store_url:

            st.warning(
                "أدخل رابط المتجر أولًا."
            )

        else:

            if not store_url.startswith(
                ("http://", "https://")
            ):

                store_url = "https://" + store_url

            with st.spinner(
                "جاري فحص المتجر..."
            ):

                html = fetch_page(
                    store_url
                )

            if not html:

                st.error(
                    "تعذر الوصول إلى المتجر."
                )

            else:

                store_results = analyze_store(
                    store_url,
                    html
                )

                privacy_url = find_privacy_page(
                    store_url,
                    html
                )

                store_score = calculate_store_score(
                    store_results
                )

                privacy_score = None

                privacy_results = []

                if privacy_url:

                    privacy_html = fetch_page(
                        privacy_url
                    )

                    if privacy_html:

                        privacy_text, _ = extract_page_data(
                            privacy_html,
                            privacy_url
                        )

                        privacy_results = analyze_privacy(
                            privacy_text
                        )

                        privacy_score = calculate_privacy_score(
                            privacy_results
                        )

                if privacy_score is not None:

                    overall_score = round(
                        (store_score + privacy_score) / 2
                    )

                else:

                    overall_score = store_score

                st.divider()

                st.subheader("📊 المؤشرات")

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "المؤشر العام",
                    f"{overall_score}%"
                )

                c2.metric(
                    "فحص المتجر",
                    f"{store_score}%"
                )

                if privacy_score is not None:

                    c3.metric(
                        "فحص الخصوصية",
                        f"{privacy_score}%"
                    )

                else:

                    c3.metric(
                        "فحص الخصوصية",
                        "غير متوفر"
                    )

                if overall_score >= 80:

                    st.success(
                        "🟢 مؤشرات جيدة — مع استمرار الحاجة للمراجعة النظامية."
                    )

                elif overall_score >= 60:

                    st.warning(
                        "🟡 توجد مؤشرات تحتاج إلى مراجعة."
                    )

                else:

                    st.error(
                        "🔴 يحتاج مراجعة موسعة."
                    )

                # -----------------------------
                # فحص المتجر
                # -----------------------------

                st.divider()

                st.subheader("🏪 فحص المتجر")

                for result in store_results:

                    if result["status"] == "🟢":

                        st.success(
                            f"{result['status']} {result['label']}: "
                            f"{result['name']}"
                        )

                    else:

                        st.warning(
                            f"{result['status']} {result['label']}: "
                            f"{result['name']}"
                        )

                # -----------------------------
                # الخصوصية
                # -----------------------------

                if privacy_url:

                    st.divider()

                    st.subheader(
                        "📄 فحص سياسة الخصوصية"
                    )

                    st.caption(
                        f"تم العثور على صفحة الخصوصية: {privacy_url}"
                    )

                    for result in privacy_results:

                        if result["status"] == "🟢":

                            st.success(
                                f"{result['status']} "
                                f"{result['label']}: "
                                f"{result['name']}"
                            )

                        elif result["status"] == "🟡":

                            st.warning(
                                f"{result['status']} "
                                f"{result['label']}: "
                                f"{result['name']}"
                            )

                        else:

                            st.error(
                                f"{result['status']} "
                                f"{result['label']}: "
                                f"{result['name']}"
                            )

                        if result["evidence"]:

                            st.caption(
                                f"الدليل: {result['evidence']}"
                            )

                else:

                    st.divider()

                    st.warning(
                        "لم يتم العثور تلقائيًا على صفحة سياسة الخصوصية."
                    )

                # -----------------------------
                # تحقق خارجي
                # -----------------------------

                st.divider()

                st.subheader(
                    "🔵 عناصر تحتاج تحققًا خارجيًا"
                )

                for item in EXTERNAL_CHECKS:

                    st.info(
                        f"🔵 {item}"
                    )


# =========================================================
# فحص سياسة الخصوصية يدويًا
# =========================================================

with tab2:

    st.subheader(
        "📄 فحص سياسة الخصوصية"
    )

    privacy_text_input = st.text_area(
        "الصق نص سياسة الخصوصية هنا",
        height=350,
        placeholder="الصق سياسة الخصوصية هنا..."
    )

    if st.button(
        "تحليل سياسة الخصوصية",
        type="primary"
    ):

        if not privacy_text_input.strip():

            st.warning(
                "الصق نص سياسة الخصوصية أولًا."
            )

        else:

            results = analyze_privacy(
                privacy_text_input
            )

            score = calculate_privacy_score(
                results
            )

            clear_count = sum(
                1
                for r in results
                if r["status"] == "🟢"
            )

            review_count = sum(
                1
                for r in results
                if r["status"] == "🟡"
            )

            missing_count = sum(
                1
                for r in results
                if r["status"] == "🔴"
            )

            st.divider()

            st.subheader(
                f"المؤشر الأولي: {score}%"
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "مؤشرات واضحة",
                clear_count
            )

            c2.metric(
                "تحتاج مراجعة",
                review_count
            )

            c3.metric(
                "لم يتم العثور عليها",
                missing_count
            )

            if score >= 80:

                st.success(
                    "🟢 توجد مؤشرات واضحة على معظم المتطلبات."
                )

            elif score >= 60:

                st.warning(
                    "🟡 توجد مؤشرات، لكن بعض المتطلبات تحتاج مراجعة."
                )

            else:

                st.error(
                    "🔴 يحتاج مراجعة موسعة."
                )

            st.divider()

            for result in results:

                if result["status"] == "🟢":

                    st.success(
                        f"{result['status']} "
                        f"{result['label']}: "
                        f"{result['name']}"
                    )

                elif result["status"] == "🟡":

                    st.warning(
                        f"{result['status']} "
                        f"{result['label']}: "
                        f"{result['name']}"
                    )

                else:

                    st.error(
                        f"{result['status']} "
                        f"{result['label']}: "
                        f"{result['name']}"
                    )

                if result["evidence"]:

                    st.caption(
                        f"الدليل الذي تم العثور عليه: "
                        f"{result['evidence']}"
                    )

            st.divider()

            st.info(
                "ملاحظة: المؤشر أولي ويعتمد على النص المتاح، "
                "ولا يثبت وحده تحقق المتطلبات النظامية."
            )
