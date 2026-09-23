import re
from urllib.parse import urljoin

import requests
import streamlit as st
from bs4 import BeautifulSoup


# =========================
# إعداد الصفحة
# =========================

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ ميثاق | Methaq")
st.caption("منصة ذكية للفحص الأولي لمؤشرات الامتثال في المتاجر والسياسات")

st.info(
    "تنبيه: النتائج آلية ومبدئية، ولا تمثل استشارة قانونية أو ضمانًا للامتثال."
)


# =========================
# قواعد فحص الخصوصية
# =========================

PRIVACY_RULES = {

    "تحديد البيانات الشخصية التي يتم جمعها": {
        "patterns": [
            ["البيانات الشخصية"],
            ["نجمع", "البيانات"],
            ["جمع", "البيانات"],
            ["مثل الاسم"],
            ["رقم الجوال"],
            ["البريد الإلكتروني"],
            ["عنوان التوصيل"],
        ],
        "suggestion": "يُوصى بتوضيح أنواع البيانات الشخصية التي يتم جمعها."
    },

    "توضيح الغرض من جمع البيانات": {
        "patterns": [
            ["نستخدم البيانات"],
            ["استخدام البيانات"],
            ["الغرض من جمع"],
            ["أغراض جمع"],
            ["لتقديم الخدمات"],
            ["لتنفيذ الطلبات"],
            ["تحسين تجربة المستخدم"],
        ],
        "suggestion": "يُوصى بتوضيح أغراض جمع واستخدام البيانات."
    },

    "توضيح طريقة جمع البيانات": {
        "patterns": [
            ["يتم جمع البيانات"],
            ["يتم جمع", "البيانات"],
            ["نجمع البيانات", "من خلال"],
            ["من خلال النماذج"],
            ["النماذج الإلكترونية"],
            ["عمليات الشراء"],
            ["عبر الموقع"],
            ["من خلال الموقع"],
            ["عند استخدام خدماتنا"],
        ],
        "suggestion": "يُوصى بتوضيح الطريقة أو الوسائل التي يتم من خلالها جمع البيانات."
    },

    "توضيح كيفية معالجة البيانات": {
        "patterns": [
            ["معالجة البيانات"],
            ["تتم معالجة البيانات"],
            ["نعالج البيانات"],
            ["معالجة البيانات الشخصية"],
            ["استخدام ومعالجة البيانات"],
        ],
        "suggestion": "يُوصى بتوضيح كيفية معالجة البيانات الشخصية."
    },

    "توضيح وسيلة حفظ وتخزين البيانات": {
        "patterns": [
            ["حفظ", "البيانات"],
            ["تخزين", "البيانات"],
            ["يتم حفظ وتخزين"],
            ["أنظمة إلكترونية"],
            ["خوادم"],
            ["وسائل آمنة"],
        ],
        "suggestion": "يُوصى بتوضيح كيفية حفظ وتخزين البيانات."
    },

    "توضيح مدة الاحتفاظ بالبيانات": {
        "patterns": [
            ["نحتفظ بها", "المدة"],
            ["المدة اللازمة"],
            ["مدة الاحتفاظ"],
            ["الاحتفاظ بالبيانات"],
            ["نحتفظ بالبيانات"],
            ["لفترة محددة"],
        ],
        "suggestion": "يُوصى بتوضيح مدة الاحتفاظ بالبيانات أو معيار تحديدها."
    },

    "توضيح كيفية إتلاف أو حذف البيانات": {
        "patterns": [
            ["إتلاف", "البيانات"],
            ["حذف", "البيانات"],
            ["يتم إتلافها"],
            ["يتم حذفها"],
            ["حذف البيانات الشخصية"],
            ["إتلاف البيانات الشخصية"],
        ],
        "suggestion": "يُوصى بتوضيح آلية إتلاف أو حذف البيانات."
    },

    "توضيح حقوق صاحب البيانات": {
        "patterns": [
            ["حقوق صاحب البيانات"],
            ["حقوق أصحاب البيانات"],
            ["حق الوصول"],
            ["حق التصحيح"],
            ["حق الحذف"],
            ["يتمتع صاحب البيانات"],
            ["يحق لصاحب البيانات"],
        ],
        "suggestion": "يُوصى بتوضيح حقوق صاحب البيانات."
    },

    "توضيح طريقة ممارسة حقوق صاحب البيانات": {
        "patterns": [
            ["ممارسة حقوقه"],
            ["ممارسة حقوقها"],
            ["ممارسة حقوقك"],
            ["ممارسة حقوق"],
            ["كيفية ممارسة الحقوق"],
            ["طريقة ممارسة الحقوق"],
            ["لممارسة حقوق"],
            ["تقديم طلب", "حقوق"],
            ["من خلال التواصل", "ممارسة"],
            ["عبر البريد الإلكتروني", "ممارسة"],
            ["التواصل", "حقوق"],
        ],
        "suggestion": "يُوصى بتوضيح الطريقة التي يستطيع من خلالها صاحب البيانات ممارسة حقوقه."
    },

    "توضيح المسوغ النظامي لجمع أو معالجة البيانات": {
        "patterns": [
            ["المسوغ النظامي"],
            ["الأساس النظامي"],
            ["الأساس القانوني"],
            ["مسوغ قانوني"],
            ["وفقًا للنظام"],
            ["وفق النظام"],
            ["بموجب النظام"],
            ["الموافقة", "معالجة البيانات"],
            ["الموافقة", "جمع البيانات"],
        ],
        "suggestion": "يُوصى بتوضيح الأساس أو المسوغ النظامي لجمع أو معالجة البيانات."
    },

    "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات": {
        "patterns": [
            ["الإفصاح عن البيانات"],
            ["الإفصاح", "البيانات"],
            ["قد يتم الإفصاح"],
            ["مشاركة البيانات"],
            ["مشاركة", "البيانات"],
            ["مقدمي الخدمات"],
            ["مقدمي الخدمة"],
            ["الجهات ذات العلاقة"],
            ["أطراف أخرى"],
            ["أطراف ثالثة"],
        ],
        "suggestion": "يُوصى بتوضيح الجهات أو الفئات التي قد يتم الإفصاح لها عن البيانات."
    },

    "توضيح النقل أو المعالجة خارج المملكة": {
        "patterns": [
            ["خارج المملكة"],
            ["خارج السعودية"],
            ["نقل البيانات خارج"],
            ["نقل أو معالجة", "خارج"],
            ["معالجة البيانات خارج"],
            ["دول أخرى"],
        ],
        "suggestion": "يُوصى بتوضيح النقل أو المعالجة خارج المملكة عند انطباق ذلك."
    },
}


# =========================
# قواعد فحص المتجر
# =========================

STORE_RULES = {

    "وجود سياسة الخصوصية": {
        "keywords": [
            "سياسة الخصوصية",
            "الخصوصية",
            "سياسات الخصوصية",
            "privacy policy",
            "privacy"
        ],
        "suggestion": "يُوصى بوجود صفحة واضحة لسياسة الخصوصية."
    },

    "وجود سياسة الاستبدال والاسترجاع واسترداد الأموال": {
        "keywords": [
            "الاستبدال",
            "الاسترجاع",
            "الإرجاع",
            "استرداد الأموال",
            "استرداد المبلغ",
            "استرجاع المبلغ",
            "سياسة الاسترجاع",
            "سياسة الاستبدال",
            "refund",
            "returns",
            "return policy"
        ],
        "suggestion": "يُوصى بوجود صفحة واضحة للاستبدال والاسترجاع واسترداد الأموال."
    },

    "وجود سياسة الشحن والتوصيل": {
        "keywords": [
            "الشحن",
            "التوصيل",
            "الشحن والتوصيل",
            "سياسة الشحن",
            "مواعيد التوصيل",
            "delivery",
            "shipping"
        ],
        "suggestion": "يُوصى بتوضيح سياسات الشحن والتوصيل."
    },

    "وجود سياسة الشكاوى والمقترحات": {
        "keywords": [
            "الشكاوى",
            "الشكاوي",
            "المقترحات",
            "تقديم شكوى",
            "تقديم الشكاوى",
            "خدمة العملاء",
            "complaints"
        ],
        "suggestion": "يُوصى بتوفير وسيلة واضحة لتقديم الشكاوى والمقترحات."
    },

    "وجود بيانات التواصل": {
        "keywords": [
            "تواصل معنا",
            "اتصل بنا",
            "معلومات التواصل",
            "بيانات التواصل",
            "خدمة العملاء",
            "البريد الإلكتروني",
            "رقم الهاتف",
            "واتساب",
            "contact us",
            "contact"
        ],
        "suggestion": "يُوصى بإظهار بيانات تواصل واضحة مع المتجر."
    },

    "وجود بيانات المنشأة أو السجل التجاري": {
        "keywords": [
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
        ],
        "suggestion": "يُوصى بإظهار بيانات المنشأة أو بيانات السجل التجاري."
    },

    "وجود الرقم الضريبي": {
        "keywords": [
            "الرقم الضريبي",
            "رقم ضريبي",
            "الرقم المميز",
            "ضريبة القيمة المضافة",
            "VAT",
            "VAT number",
            "tax number"
        ],
        "suggestion": "يُوصى بالتحقق من ظهور الرقم الضريبي عند انطباقه."
    },
}


# =========================
# معالجة النص
# =========================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text):

    sentences = re.split(
        r"[.!؟?\n]+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def find_evidence(text, keywords):

    sentences = split_sentences(text)

    for keyword in keywords:

        normalized_keyword = normalize_text(
            keyword
        )

        for sentence in sentences:

            if normalized_keyword in normalize_text(
                sentence
            ):

                return sentence.strip()

    return None


# =========================
# تحليل قاعدة الخصوصية
# =========================

def analyze_rule(text, rule):

    normalized_text = normalize_text(text)

    sentences = split_sentences(text)

    matches = []

    evidence = []

    for pattern_group in rule["patterns"]:

        normalized_patterns = [
            normalize_text(pattern)
            for pattern in pattern_group
        ]

        found = False

        # البحث داخل الجملة
        for sentence in sentences:

            normalized_sentence = normalize_text(
                sentence
            )

            if all(
                pattern in normalized_sentence
                for pattern in normalized_patterns
            ):

                found = True

                evidence.append(
                    sentence.strip()
                )

                break

        # البحث في كامل النص
        if not found:

            if all(
                pattern in normalized_text
                for pattern in normalized_patterns
            ):

                found = True

                for sentence in sentences:

                    normalized_sentence = normalize_text(
                        sentence
                    )

                    if any(
                        pattern in normalized_sentence
                        for pattern in normalized_patterns
                    ):

                        evidence.append(
                            sentence.strip()
                        )

                        break

        if found:
            matches.append(pattern_group)

    total = len(rule["patterns"])

    found_count = len(matches)

    if found_count == 0:

        status = "not_found"
        score = 0

    elif found_count >= max(
        1,
        total * 0.5
    ):

        status = "clear"
        score = 100

    else:

        status = "review"
        score = 60

    evidence = list(
        dict.fromkeys(evidence)
    )

    return {
        "status": status,
        "score": score,
        "evidence": evidence[:3],
        "suggestion": rule["suggestion"]
    }


def analyze_document(text, rules):

    results = {}

    for name, rule in rules.items():

        results[name] = analyze_rule(
            text,
            rule
        )

    return results


# =========================
# حساب النتيجة
# =========================

def calculate_score(results):

    if not results:
        return 0

    total = 0

    for result in results.values():

        if result["status"] == "clear":
            total += 1

        elif result["status"] == "review":
            total += 0.5

    return round(
        (total / len(results)) * 100
    )


def risk_level(score):

    if score >= 80:

        return "🟢 مؤشر أولي جيد"

    elif score >= 60:

        return "🟡 يحتاج مراجعة"

    else:

        return "🔴 يحتاج مراجعة موسعة"


# =========================
# جلب الصفحة
# =========================

def get_page(url):

    try:

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for tag in soup.find_all(
            ["script", "style", "noscript"]
        ):

            tag.decompose()

        text = soup.get_text(
            " ",
            strip=True
        )

        return (
            text,
            soup,
            response.url
        )

    except Exception:

        return (
            None,
            None,
            None
        )


# =========================
# استخراج الروابط
# =========================

def get_links(soup, base_url):

    links = []

    if not soup:
        return links

    for a in soup.find_all(
        "a",
        href=True
    ):

        href = a.get(
            "href"
        )

        text = a.get_text(
            " ",
            strip=True
        )

        full_url = urljoin(
            base_url,
            href
        )

        links.append({
            "text": text,
            "url": full_url
        })

    return links


# =========================
# البحث عن صفحة الخصوصية
# =========================

def find_privacy_page(links):

    privacy_words = [
        "الخصوصية",
        "سياسة الخصوصية",
        "privacy",
        "privacy policy"
    ]

    for link in links:

        combined = normalize_text(
            link["text"]
            + " "
            + link["url"]
        )

        for word in privacy_words:

            if normalize_text(
                word
            ) in combined:

                return link["url"]

    return None


# =========================
# تحليل المتجر
# =========================

def analyze_store(
    text,
    links
):

    normalized_text = normalize_text(
        text
    )

    link_text = " ".join(
        [
            f"{item['text']} {item['url']}"
            for item in links
        ]
    )

    searchable_text = (
        normalized_text
        + " "
        + normalize_text(link_text)
    )

    results = {}

    for name, rule in STORE_RULES.items():

        found_keyword = None

        for keyword in rule["keywords"]:

            if normalize_text(
                keyword
            ) in searchable_text:

                found_keyword = keyword

                break

        if found_keyword:

            evidence = find_evidence(
                text,
                [found_keyword]
            )

            if not evidence:

                for link in links:

                    combined = normalize_text(
                        link["text"]
                        + " "
                        + link["url"]
                    )

                    if normalize_text(
                        found_keyword
                    ) in combined:

                        evidence = (
                            "رابط/صفحة مرتبطة: "
                            + (
                                link["text"]
                                or link["url"]
                            )
                        )

                        break

            results[name] = {
                "status": "clear",
                "score": 100,
                "evidence": (
                    [evidence]
                    if evidence
                    else []
                ),
                "suggestion": rule["suggestion"]
            }

        else:

            results[name] = {
                "status": "not_found",
                "score": 0,
                "evidence": [],
                "suggestion": rule["suggestion"]
            }

    return results


# =========================
# الواجهة
# =========================

mode = st.radio(
    "اختر نوع الفحص:",
    [
        "🛒 فحص رابط المتجر",
        "📄 فحص سياسة الخصوصية"
    ]
)


# =====================================================
# فحص سياسة الخصوصية
# =====================================================

if mode == "📄 فحص سياسة الخصوصية":

    st.subheader(
        "📄 فحص سياسة الخصوصية"
    )

    privacy_text = st.text_area(
        "ألصق نص سياسة الخصوصية هنا:",
        height=300
    )

    if st.button(
        "🔍 بدء فحص الخصوصية",
        use_container_width=True
    ):

        if not privacy_text.strip():

            st.warning(
                "أدخل نص سياسة الخصوصية أولًا."
            )

        else:

            results = analyze_document(
                privacy_text,
                PRIVACY_RULES
            )

            score = calculate_score(
                results
            )

            st.metric(
                "المؤشر الأولي",
                f"{score}%"
            )

            st.write(
                risk_level(score)
            )

            st.divider()

            for name, result in results.items():

                if result["status"] == "clear":

                    st.success(
                        f"🟢 {name}"
                    )

                    for evidence in result[
                        "evidence"
                    ]:

                        st.caption(
                            f"الدليل: {evidence}"
                        )

                elif result["status"] == "review":

                    st.warning(
                        f"🟡 يحتاج مراجعة: {name}"
                    )

                    for evidence in result[
                        "evidence"
                    ]:

                        st.caption(
                            f"المؤشر: {evidence}"
                        )

                    st.caption(
                        result["suggestion"]
                    )

                else:

                    st.error(
                        f"🔴 لم يتم العثور على مؤشر كافٍ: {name}"
                    )

                    st.caption(
                        result["suggestion"]
                    )

            st.divider()

            clear_count = sum(
                1
                for result in results.values()
                if result["status"] == "clear"
            )

            review_count = sum(
                1
                for result in results.values()
                if result["status"] == "review"
            )

            missing_count = sum(
                1
                for result in results.values()
                if result["status"] == "not_found"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "مؤشرات واضحة",
                clear_count
            )

            col2.metric(
                "تحتاج مراجعة",
                review_count
            )

            col3.metric(
                "لم يتم العثور عليها",
                missing_count
            )


# =====================================================
# فحص رابط المتجر
# =====================================================

else:

    st.subheader(
        "🛒 فحص رابط المتجر"
    )

    store_url = st.text_input(
        "أدخل رابط المتجر:",
        placeholder="https://example.com"
    )

    if st.button(
        "🔍 فحص المتجر",
        use_container_width=True
    ):

        if not store_url.strip():

            st.warning(
                "أدخل رابط المتجر أولًا."
            )

        else:

            if not store_url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                store_url = (
                    "https://"
                    + store_url
                )

            with st.spinner(
                "جارٍ تحليل المتجر..."
            ):

                page_text, soup, final_url = (
                    get_page(
                        store_url
                    )
                )

            if not page_text:

                st.error(
                    "تعذر الوصول إلى المتجر أو قراءة محتواه."
                )

            else:

                st.success(
                    "تم الوصول إلى المتجر وبدء الفحص."
                )

                # HTTPS
                https_ok = final_url.startswith(
                    "https://"
                )

                # الروابط
                links = get_links(
                    soup,
                    final_url
                )

                # فحص المتجر
                store_results = analyze_store(
                    page_text,
                    links
                )

                store_score = calculate_score(
                    store_results
                )

                # البحث عن سياسة الخصوصية
                privacy_url = find_privacy_page(
                    links
                )

                privacy_results = None
                privacy_score = 0

                if privacy_url:

                    privacy_text, _, _ = (
                        get_page(
                            privacy_url
                        )
                    )

                    if privacy_text:

                        privacy_results = (
                            analyze_document(
                                privacy_text,
                                PRIVACY_RULES
                            )
                        )

                        privacy_score = (
                            calculate_score(
                                privacy_results
                            )
                        )

                # المؤشر العام
                if privacy_results:

                    overall_score = round(
                        (
                            store_score
                            + privacy_score
                        ) / 2
                    )

                else:

                    overall_score = store_score

                # المؤشرات
                st.divider()

                st.subheader(
                    "📊 المؤشرات"
                )

                col1, col2, col3 = st.columns(
                    3
                )

                col1.metric(
                    "المؤشر العام",
                    f"{overall_score}%"
                )

                col2.metric(
                    "فحص المتجر",
                    f"{store_score}%"
                )

                col3.metric(
                    "فحص الخصوصية",
                    (
                        f"{privacy_score}%"
                        if privacy_results
                        else "غير متاح"
                    )
                )

                st.write(
                    risk_level(
                        overall_score
                    )
                )

                # عناصر المتجر
                st.divider()

                st.subheader(
                    "🛒 عناصر المتجر"
                )

                for name, result in (
                    store_results.items()
                ):

                    if result["status"] == "clear":

                        st.success(
                            f"🟢 {name}"
                        )

                        for evidence in result[
                            "evidence"
                        ]:

                            st.caption(
                                f"الدليل: {evidence}"
                            )

                    else:

                        st.error(
                            f"⚪️ لم يتم العثور على مؤشر كافٍ: {name}"
                        )

                        st.caption(
                            result["suggestion"]
                        )

                # HTTPS
                st.divider()

                st.subheader(
                    "🔐 أمان الاتصال"
                )

                if https_ok:

                    st.success(
                        "🟢 يستخدم المتجر HTTPS."
                    )

                else:

                    st.error(
                        "🔴 لم يتم التحقق من استخدام HTTPS."
                    )

                # سياسة الخصوصية
                st.divider()

                st.subheader(
                    "📄 فحص سياسة الخصوصية"
                )

                if privacy_url:

                    st.success(
                        "🟢 تم العثور على صفحة مرتبطة بسياسة الخصوصية."
                    )

                    st.write(
                        privacy_url
                    )

                    if privacy_results:

                        for name, result in (
                            privacy_results.items()
                        ):

                            if result["status"] == "clear":

                                st.success(
                                    f"🟢 {name}"
                                )

                                for evidence in result[
                                    "evidence"
                                ]:

                                    st.caption(
                                        f"الدليل: {evidence}"
                                    )

                            elif result["status"] == "review":

                                st.warning(
                                    f"🟡 يحتاج مراجعة: {name}"
                                )

                                for evidence in result[
                                    "evidence"
                                ]:

                                    st.caption(
                                        f"المؤشر: {evidence}"
                                    )

                                st.caption(
                                    result["suggestion"]
                                )

                            else:

                                st.error(
                                    f"🔴 لم يتم العثور على مؤشر كافٍ: {name}"
                                )

                                st.caption(
                                    result["suggestion"]
                                )

                else:

                    st.warning(
                        "🟡 لم يتم العثور تلقائيًا على صفحة واضحة لسياسة الخصوصية."
                    )

                # التحقق الخارجي
                st.divider()

                st.subheader(
                    "🔎 عناصر تحتاج تحققًا خارجيًا"
                )

                external_checks = [
                    "التحقق من صحة السجل التجاري",
                    "التحقق من الرقم الضريبي عند انطباقه",
                    "التحقق من بيانات المنشأة من مصدر رسمي",
                    "التحقق من أي تراخيص أو متطلبات خاصة بنشاط المتجر"
                ]

                for item in external_checks:

                    st.info(
                        f"🔵 {item}"
                    )

                st.divider()

                st.caption(
                    "ميثاق يقدم مؤشر فحص أولي آليًا، "
                    "ولا يثبت وحده وجود مخالفة أو تحقق الامتثال النظامي."
                )
