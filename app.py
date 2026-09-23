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

st.title("⚖️ ميثاق | Methaq")
st.subheader("منصة ذكية للفحص الأولي للامتثال في المتاجر الإلكترونية السعودية")

st.write(
    "يساعد ميثاق على فحص النصوص المنشورة في المتجر "
    "واكتشاف المؤشرات التي قد تحتاج إلى مراجعة."
)

st.info(
    "⚠️ ميثاق نموذج أولي تجريبي. نتائج الفحص آلية ومبدئية، "
    "ولا تمثل استشارة قانونية أو حكمًا نهائيًا بالامتثال."
)


# =========================================================
# محرك قواعد سياسة الخصوصية
# =========================================================

PRIVACY_RULES = {

    "تحديد البيانات الشخصية التي يتم جمعها": {
        "patterns": [
            ["البيانات الشخصية"],
            ["المعلومات الشخصية"],
            ["بيانات المستخدم"],
            ["بيانات العميل"],
            ["البيانات التي نجمعها"],
            ["المعلومات التي نجمعها"],
            ["أنواع البيانات"],
            ["نوع البيانات"]
        ],
        "suggestion":
            "يوصى بتوضيح أنواع البيانات الشخصية التي يتم جمعها."
    },

    "توضيح الغرض من جمع البيانات": {
        "patterns": [
            ["الغرض", "جمع"],
            ["أغراض", "جمع"],
            ["الغرض", "استخدام"],
            ["أغراض", "استخدام"],
            ["الغرض", "معالجة"],
            ["أغراض", "معالجة"],
            ["نستخدم البيانات"],
            ["استخدام البيانات"],
            ["معالجة البيانات", "الغرض"]
        ],
        "suggestion":
            "يوصى بتوضيح الأغراض التي يتم من أجلها جمع أو استخدام أو معالجة البيانات."
    },

    "توضيح طريقة جمع البيانات": {
        "patterns": [
            ["طريقة جمع"],
            ["طرق جمع"],
            ["كيفية جمع"],
            ["يتم جمع البيانات"],
            ["نجمع البيانات"],
            ["مصادر البيانات"],
            ["مصدر البيانات"]
        ],
        "suggestion":
            "يوصى بتوضيح الطريقة أو الوسائل التي يتم من خلالها جمع البيانات."
    },

    "توضيح كيفية معالجة البيانات": {
        "patterns": [
            ["معالجة البيانات"],
            ["معالجة المعلومات"],
            ["تتم معالجة"],
            ["يتم معالجة"],
            ["نقوم بمعالجة"],
            ["عمليات المعالجة"],
            ["استخدام", "معالجة"]
        ],
        "suggestion":
            "يوصى بتوضيح كيفية معالجة البيانات والأغراض المرتبطة بالمعالجة."
    },

    "توضيح وسيلة حفظ وتخزين البيانات": {
        "patterns": [
            ["حفظ البيانات"],
            ["حفظ المعلومات"],
            ["تخزين البيانات"],
            ["تخزين المعلومات"],
            ["يتم تخزين", "بيانات"],
            ["يتم حفظ", "بيانات"],
            ["نخزن البيانات"],
            ["نحتفظ بالبيانات", "تخزين"],
            ["أنظمة", "تخزين", "بيانات"],
            ["أنظمة إلكترونية", "بيانات"]
        ],
        "suggestion":
            "يوصى بتوضيح كيفية حفظ وتخزين البيانات الشخصية."
    },

    "توضيح مدة الاحتفاظ بالبيانات": {
        "patterns": [
            ["مدة", "الاحتفاظ"],
            ["فترة", "الاحتفاظ"],
            ["مدة", "حفظ", "البيانات"],
            ["فترة", "حفظ", "البيانات"],
            ["نحتفظ بالبيانات", "مدة"],
            ["نحتفظ بها", "مدة"],
            ["نحتفظ بها", "المدة"],
            ["للمدة اللازمة"],
            ["المدة اللازمة"],
            ["حتى انتهاء", "الغرض"],
            ["حتى تنتهي", "الحاجة"],
            ["طالما كانت هناك حاجة"],
            ["طالما", "الحاجة"],
            ["إلى حين انتهاء", "الحاجة"],
            ["يتم الاحتفاظ بها", "مدة"],
            ["يتم الاحتفاظ", "المدة"]
        ],
        "suggestion":
            "يوصى بتوضيح مدة الاحتفاظ بالبيانات أو المعايير المستخدمة لتحديد مدة الاحتفاظ."
    },

    "توضيح كيفية إتلاف أو حذف البيانات": {
        "patterns": [
            ["إتلاف البيانات"],
            ["إتلاف المعلومات"],
            ["حذف البيانات"],
            ["حذف المعلومات"],
            ["التخلص من البيانات"],
            ["تدمير البيانات"],
            ["إتلافها"],
            ["حذفها"],
            ["بعد انتهاء", "حذف"],
            ["بعد انتهاء", "إتلاف"]
        ],
        "suggestion":
            "يوصى بتوضيح كيفية إتلاف أو حذف البيانات عند انتهاء الحاجة إليها."
    },

    "توضيح حقوق صاحب البيانات": {
        "patterns": [
            ["حقوق صاحب البيانات"],
            ["حقوق أصحاب البيانات"],
            ["حقوق المستخدم"],
            ["حقوق العميل"],
            ["حقوقك", "البيانات"],
            ["حق الوصول"],
            ["الوصول إلى البيانات"],
            ["تصحيح البيانات"],
            ["تعديل البيانات"],
            ["حذف البيانات"],
            ["الاعتراض", "البيانات"]
        ],
        "suggestion":
            "يوصى بتوضيح حقوق صاحب البيانات المتعلقة ببياناته الشخصية."
    },

    "توضيح طريقة ممارسة حقوق صاحب البيانات": {
        "patterns": [
            ["ممارسة حقوقك"],
            ["ممارسة حقوق", "البيانات"],
            ["ممارسة هذه الحقوق"],
            ["كيفية ممارسة الحقوق"],
            ["طريقة ممارسة الحقوق"],
            ["لممارسة حقوقك"],
            ["لممارسة هذه الحقوق"],
            ["تقديم طلب", "حقوق"],
            ["طلب الوصول"],
            ["التواصل", "ممارسة", "الحقوق"],
            ["التواصل معنا", "حقوق"],
            ["عبر البريد الإلكتروني", "حقوق"],
            ["من خلال التواصل", "حقوق"]
        ],
        "suggestion":
            "يوصى بتوضيح الطريقة والقنوات التي يستطيع من خلالها صاحب البيانات ممارسة حقوقه."
    },

    "توضيح المسوغ النظامي لجمع أو معالجة البيانات": {
        "patterns": [
            ["المسوغ النظامي"],
            ["المسوغ القانوني"],
            ["الأساس النظامي", "جمع"],
            ["الأساس النظامي", "معالجة"],
            ["الأساس القانوني", "جمع"],
            ["الأساس القانوني", "معالجة"],
            ["الأساس", "النظامي", "البيانات"],
            ["الأساس", "القانوني", "البيانات"],
            ["بموجب", "نظام", "معالجة"],
            ["بموجب", "النظام", "معالجة"],
            ["وفق", "النظام", "معالجة"]
        ],
        "suggestion":
            "يوصى بمراجعة وبيان الأساس أو المسوغ النظامي ذي الصلة بجمع أو معالجة البيانات."
    },

    "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات": {
        "patterns": [
            ["الإفصاح عن البيانات"],
            ["الإفصاح عن المعلومات"],
            ["مشاركة البيانات"],
            ["مشاركة المعلومات"],
            ["مشاركة بيانات المستخدم"],
            ["مشاركة بيانات العملاء"],
            ["أطراف أخرى", "بيانات"],
            ["أطراف ثالثة", "بيانات"],
            ["جهات أخرى", "بيانات"],
            ["مزودي الخدمات", "بيانات"],
            ["مقدمي الخدمات", "بيانات"],
            ["الجهات الحكومية", "بيانات"],
            ["الإفصاح", "مزودي الخدمات"],
            ["الإفصاح", "مقدمي الخدمات"]
        ],
        "suggestion":
            "يوصى بتوضيح الجهات أو الفئات التي قد يتم الإفصاح لها عن البيانات الشخصية."
    },

    "توضيح النقل أو المعالجة خارج المملكة": {
        "patterns": [
            ["خارج المملكة", "بيانات"],
            ["خارج السعودية", "بيانات"],
            ["نقل البيانات", "خارج"],
            ["نقل", "البيانات", "الخارج"],
            ["معالجة", "خارج المملكة"],
            ["معالجة", "خارج السعودية"],
            ["نقل أو إفصاح", "خارج"],
            ["النقل الدولي", "البيانات"]
        ],
        "suggestion":
            "يوصى بمراجعة ما إذا كانت البيانات تُنقل أو تُعالج خارج المملكة."
    }
}


# =========================================================
# قواعد المتجر
# =========================================================

STORE_RULES = {

    "وجود سياسة الخصوصية": {
        "patterns": [
            ["سياسة الخصوصية"],
            ["الخصوصية"],
            ["privacy policy"],
            ["privacy"]
        ],
        "suggestion":
            "يوصى بتوفير سياسة واضحة للخصوصية وحماية بيانات المستهلك."
    },

    "وجود سياسة الاستبدال والاسترجاع واسترداد الأموال": {
        "patterns": [
            ["سياسة الاستبدال"],
            ["سياسة الاسترجاع"],
            ["الاستبدال", "الاسترجاع"],
            ["استرداد الأموال"],
            ["استرداد المبلغ"],
            ["refund"],
            ["return policy"]
        ],
        "suggestion":
            "يوصى بتوفير سياسة واضحة للاستبدال والاسترجاع واسترداد الأموال."
    },

    "وجود سياسة الشحن والتوصيل": {
        "patterns": [
            ["سياسة الشحن"],
            ["سياسة التوصيل"],
            ["الشحن", "التوصيل"],
            ["مدة التوصيل"],
            ["تكلفة الشحن"],
            ["shipping"],
            ["delivery"]
        ],
        "suggestion":
            "يوصى بتوضيح أحكام الشحن والتوصيل."
    },

    "وجود سياسة للشكاوى والمقترحات": {
        "patterns": [
            ["الشكاوى"],
            ["تقديم شكوى"],
            ["تقديم الشكوى"],
            ["الشكاوى والمقترحات"],
            ["الاقتراحات"],
            ["complaint"]
        ],
        "suggestion":
            "يوصى بتوفير آلية واضحة لتقديم الشكاوى والمقترحات."
    },

    "وجود وسيلة واضحة للتواصل": {
        "patterns": [
            ["تواصل معنا"],
            ["اتصل بنا"],
            ["خدمة العملاء"],
            ["البريد الإلكتروني"],
            ["رقم الهاتف"],
            ["واتساب"],
            ["contact us"],
            ["email"]
        ],
        "suggestion":
            "يوصى بتوفير وسيلة واضحة ومباشرة للتواصل مع المتجر."
    },

    "وجود بيانات المنشأة أو السجل التجاري": {
        "patterns": [
            ["السجل التجاري"],
            ["رقم السجل"],
            ["بيانات المنشأة"],
            ["commercial registration"],
            ["cr number"]
        ],
        "suggestion":
            "يوصى بمراجعة ظهور بيانات المنشأة أو السجل التجاري المطلوبة."
    },

    "وجود الرقم الضريبي": {
        "patterns": [
            ["الرقم الضريبي"],
            ["الرقم الضريبي الموحد"],
            ["الرقم الضريبي للمنشأة"],
            ["vat number"],
            ["vat"]
        ],
        "suggestion":
            "يوصى بمراجعة ظهور الرقم الضريبي عند انطباق المتطلب."
    }
}


# =========================================================
# تطبيع النص
# =========================================================

def normalize_text(text):

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

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# تقسيم النص إلى جمل
# =========================================================

def split_sentences(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    sentences = re.split(
        r"(?<=[.!؟؛])\s+|[\n\r]+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# =========================================================
# تحليل السياق
# =========================================================

def analyze_rule(text, rule):

    sentences = split_sentences(text)

    normalized_sentences = [
        normalize_text(sentence)
        for sentence in sentences
    ]

    best_match = None
    best_score = 0
    best_pattern = None

    for index, sentence in enumerate(normalized_sentences):

        for pattern in rule["patterns"]:

            normalized_pattern = [
                normalize_text(part)
                for part in pattern
            ]

            matched_parts = 0

            for part in normalized_pattern:

                if part in sentence:
                    matched_parts += 1

            if not normalized_pattern:
                continue

            match_ratio = (
                matched_parts /
                len(normalized_pattern)
            )

            # إذا تحقق كل المؤشرات
            if match_ratio == 1:

                score = 100

            # إذا تحقق أكثر من نصف المؤشرات
            elif match_ratio >= 0.5:

                score = 60

            else:

                score = 0

            if score > best_score:

                best_score = score
                best_match = sentences[index]
                best_pattern = pattern

    # -----------------------------------------------------
    # إذا لم نجد شيئًا في جملة واحدة،
    # نحاول البحث داخل نافذة من جملتين متجاورتين
    # -----------------------------------------------------

    if best_score < 100:

        for index in range(
            len(normalized_sentences) - 1
        ):

            combined = (
                normalized_sentences[index]
                + " "
                + normalized_sentences[index + 1]
            )

            for pattern in rule["patterns"]:

                normalized_pattern = [
                    normalize_text(part)
                    for part in pattern
                ]

                matched_parts = sum(
                    1
                    for part in normalized_pattern
                    if part in combined
                )

                if not normalized_pattern:
                    continue

                ratio = (
                    matched_parts /
                    len(normalized_pattern)
                )

                if ratio == 1:

                    score = 100

                elif ratio >= 0.5:

                    score = 60

                else:

                    score = 0

                if score > best_score:

                    best_score = score

                    best_match = (
                        sentences[index]
                        + " "
                        + sentences[index + 1]
                    )

                    best_pattern = pattern

    if best_score >= 100:

        return {
            "status": "clear",
            "score": 100,
            "evidence": best_match,
            "pattern": best_pattern
        }

    if best_score >= 60:

        return {
            "status": "review",
            "score": 60,
            "evidence": best_match,
            "pattern": best_pattern
        }

    return {
        "status": "not_found",
        "score": 0,
        "evidence": None,
        "pattern": None
    }


# =========================================================
# تحليل مجموعة كاملة
# =========================================================

def analyze_document(text, rules):

    results = {}

    for name, rule in rules.items():

        results[name] = analyze_rule(
            text,
            rule
        )

    return results


# =========================================================
# حساب المؤشر
# =========================================================

def calculate_score(results):

    if not results:
        return 0

    total = len(results)

    points = 0

    for result in results.values():

        if result["status"] == "clear":

            points += 1

        elif result["status"] == "review":

            points += 0.5

    return round(
        (points / total) * 100
    )


# =========================================================
# مستوى المراجعة
# =========================================================

def risk_level(score):

    if score >= 80:

        return (
            "🟢 منخفض نسبيًا",
            "تم العثور على معظم المؤشرات."
        )

    if score >= 60:

        return (
            "🟡 يحتاج مراجعة",
            "تم العثور على جزء من المؤشرات."
        )

    return (
        "🔴 يحتاج مراجعة موسعة",
        "لم يتم العثور على عدد كافٍ من المؤشرات."
    )


# =========================================================
# جلب الصفحة
# =========================================================

def get_page(url):

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
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

    text = soup.get_text(
        " ",
        strip=True
    )

    return soup, text


# =========================================================
# استخراج الروابط
# =========================================================

def get_links(soup, base_url):

    links = []

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = link.get(
            "href",
            ""
        ).strip()

        if not href:
            continue

        full_url = urljoin(
            base_url,
            href
        )

        text = link.get_text(
            " ",
            strip=True
        )

        links.append(
            {
                "url": full_url,
                "text": text
            }
        )

    return links


# =========================================================
# العثور على سياسة الخصوصية
# =========================================================

def find_privacy_page(
    soup,
    base_url
):

    words = [
        "privacy",
        "privacy-policy",
        "الخصوصية",
        "سياسة الخصوصية"
    ]

    links = get_links(
        soup,
        base_url
    )

    for link in links:

        combined = (
            link["text"]
            + " "
            + link["url"]
        ).lower()

        if any(
            word.lower() in combined
            for word in words
        ):

            return link["url"]

    return None


# =========================================================
# واجهة التطبيق
# =========================================================

st.divider()

mode = st.radio(
    "اختر طريقة الفحص:",
    [
        "🛒 فحص رابط المتجر",
        "📄 فحص سياسة الخصوصية"
    ],
    horizontal=True
)


# =========================================================
# فحص سياسة الخصوصية
# =========================================================

if mode == "📄 فحص سياسة الخصوصية":

    st.header(
        "📄 تحليل سياسة الخصوصية"
    )

    policy_text = st.text_area(
        "الصق سياسة الخصوصية هنا",
        height=400,
        placeholder="الصق النص هنا..."
    )

    if st.button(
        "🔍 ابدأ التحليل",
        type="primary"
    ):

        if not policy_text.strip():

            st.warning(
                "⚠️ الصق سياسة الخصوصية أولًا."
            )

        else:

            results = analyze_document(
                policy_text,
                PRIVACY_RULES
            )

            score = calculate_score(
                results
            )

            level, description = risk_level(
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
                    "حالة المراجعة",
                    level
                )

            st.progress(
                score / 100
            )

            st.caption(
                description
            )

            # -------------------------------------------------
            # النتائج
            # -------------------------------------------------

            st.divider()

            st.subheader(
                "نتائج المحرك"
            )

            for name, result in results.items():

                if result["status"] == "clear":

                    st.success(
                        f"🟢 {name}"
                    )

                    if result["evidence"]:

                        with st.expander(
                            "عرض الدليل النصي"
                        ):

                            st.write(
                                result["evidence"]
                            )

                            st.caption(
                                "تم العثور على مؤشرات نصية واضحة مرتبطة بهذا المتطلب."
                            )

                elif result["status"] == "review":

                    st.warning(
                        f"🟡 {name}"
                    )

                    if result["evidence"]:

                        with st.expander(
                            "عرض النص الذي يحتاج مراجعة"
                        ):

                            st.write(
                                result["evidence"]
                            )

                    st.info(
                        PRIVACY_RULES[name]["suggestion"]
                    )

                else:

                    st.error(
                        f"⚪ لم يتم العثور على مؤشر كافٍ: {name}"
                    )

                    st.info(
                        PRIVACY_RULES[name]["suggestion"]
                    )

            # -------------------------------------------------
            # ملخص
            # -------------------------------------------------

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

            st.subheader(
                "📌 ملخص التحليل"
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "مؤشرات واضحة",
                    clear_count
                )

            with c2:

                st.metric(
                    "تحتاج مراجعة",
                    review_count
                )

            with c3:

                st.metric(
                    "لم يتم العثور عليها",
                    missing_count
                )

            st.caption(
                "وجود مؤشر نصي لا يعني بالضرورة تحقق المتطلب نظاميًا؛ "
                "النتيجة تحتاج إلى مراجعة بشرية عند الحاجة."
            )


# =========================================================
# فحص رابط المتجر
# =========================================================

else:

    st.header(
        "🛒 فحص المتجر الإلكتروني"
    )

    store_url = st.text_input(
        "رابط المتجر",
        placeholder="https://example.com"
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

                store_url = (
                    "https://" + store_url
                )

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

                    soup, homepage_text = get_page(
                        store_url
                    )

                st.success(
                    "✅ تم الوصول إلى المتجر."
                )

                # -------------------------------------------------
                # فحص المتجر
                # -------------------------------------------------

                store_results = analyze_document(
                    homepage_text,
                    STORE_RULES
                )

                store_score = calculate_score(
                    store_results
                )

                # -------------------------------------------------
                # HTTPS
                # -------------------------------------------------

                https_ok = store_url.startswith(
                    "https://"
                )

                # -------------------------------------------------
                # البحث عن سياسة الخصوصية
                # -------------------------------------------------

                privacy_url = find_privacy_page(
                    soup,
                    store_url
                )

                privacy_results = None
                privacy_score = None

                if privacy_url:

                    try:

                        with st.spinner(
                            "جاري تحليل سياسة الخصوصية..."
                        ):

                            _, privacy_text = get_page(
                                privacy_url
                            )

                        privacy_results = analyze_document(
                            privacy_text,
                            PRIVACY_RULES
                        )

                        privacy_score = calculate_score(
                            privacy_results
                        )

                    except Exception:

                        privacy_url = None

                # -------------------------------------------------
                # النتيجة العامة
                # -------------------------------------------------

                if privacy_score is not None:

                    overall_score = round(
                        (
                            store_score
                            + privacy_score
                        ) / 2
                    )

                else:

                    overall_score = store_score

                level, description = risk_level(
                    overall_score
                )

                st.divider()

                st.header(
                    "📊 تقرير ميثاق"
                )

                a, b, c = st.columns(3)

                with a:

                    st.metric(
                        "المؤشر العام",
                        f"{overall_score}%"
                    )

                with b:

                    st.metric(
                        "فحص المتجر",
                        f"{store_score}%"
                    )

                with c:

                    if privacy_score is not None:

                        st.metric(
                            "فحص الخصوصية",
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
                    level
                )

                st.caption(
                    description
                )

                # -------------------------------------------------
                # HTTPS
                # -------------------------------------------------

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
                        "🔴 لم يتم استخدام HTTPS في الرابط المفحوص."
                    )

                # -------------------------------------------------
                # سياسة الخصوصية
                # -------------------------------------------------

                st.divider()

                st.header(
                    "🔐 سياسة الخصوصية"
                )

                if privacy_results is not None:

                    st.success(
                        "✅ تم العثور على صفحة سياسة الخصوصية."
                    )

                    st.write(
                        f"🔗 {privacy_url}"
                    )

                    st.metric(
                        "مؤشر فحص السياسة",
                        f"{privacy_score}%"
                    )

                    for name, result in privacy_results.items():

                        if result["status"] == "clear":

                            st.success(
                                f"🟢 {name}"
                            )

                            if result["evidence"]:

                                with st.expander(
                                    "عرض الدليل"
                                ):

                                    st.write(
                                        result["evidence"]
                                    )

                        elif result["status"] == "review":

                            st.warning(
                                f"🟡 {name}"
                            )

                            if result["evidence"]:

                                with st.expander(
                                    "عرض النص"
                                ):

                                    st.write(
                                        result["evidence"]
                                    )

                            st.info(
                                PRIVACY_RULES[name]["suggestion"]
                            )

                        else:

                            st.error(
                                f"⚪ لم يتم العثور على مؤشر كافٍ: {name}"
                            )

                            st.info(
                                PRIVACY_RULES[name]["suggestion"]
                            )

                else:

                    st.warning(
                        "⚠️ لم يتم العثور تلقائيًا على صفحة سياسة الخصوصية."
                    )

                    st.info(
                        "يمكنك فحص نص السياسة يدويًا من خيار «فحص سياسة الخصوصية»."
                    )

                # -------------------------------------------------
                # فحص المتجر
                # -------------------------------------------------

                st.divider()

                st.header(
                    "🛍️ عناصر المتجر"
                )

                for name, result in store_results.items():

                    if result["status"] == "clear":

                        st.success(
                            f"🟢 {name}"
                        )

                        if result["evidence"]:

                            with st.expander(
                                "عرض الدليل"
                            ):

                                st.write(
                                    result["evidence"]
                                )

                    elif result["status"] == "review":

                        st.warning(
                            f"🟡 {name}"
                        )

                        if result["evidence"]:

                            with st.expander(
                                "عرض النص"
                            ):

                                st.write(
                                    result["evidence"]
                                )

                        st.info(
                            STORE_RULES[name]["suggestion"]
                        )

                    else:

                        st.error(
                            f"⚪ لم يتم العثور على مؤشر كافٍ: {name}"
                        )

                        st.info(
                            STORE_RULES[name]["suggestion"]
                        )

                # -------------------------------------------------
                # تحقق خارجي
                # -------------------------------------------------

                st.divider()

                st.header(
                    "🔎 عناصر تحتاج تحققًا خارجيًا"
                )

                st.warning(
                    "هذه العناصر لا يستطيع ميثاق إثباتها بمجرد قراءة الصفحة العامة."
                )

                st.write(
                    "• حالة التوثيق الرسمي للمتجر"
                )

                st.write(
                    "• صحة بيانات المنشأة الرسمية"
                )

                st.write(
                    "• صحة التراخيص أو التسجيلات الرسمية"
                )

                st.write(
                    "• وجود مخالفات أو إجراءات نظامية خارج نطاق الموقع"
                )

                # -------------------------------------------------
                # الخلاصة
                # -------------------------------------------------

                st.divider()

                st.header(
                    "📝 خلاصة ميثاق"
                )

                if overall_score >= 80:

                    st.success(
                        "أظهر الفحص وجود عدد مرتفع من المؤشرات المطلوبة، "
                        "مع بقاء بعض العناصر التي قد تحتاج إلى مراجعة."
                    )

                elif overall_score >= 60:

                    st.warning(
                        "أظهر الفحص وجود عدد متوسط من المؤشرات، "
                        "وتوجد عناصر تحتاج إلى مراجعة."
                    )

                else:

                    st.error(
                        "أظهر الفحص وجود عدد من العناصر التي تحتاج إلى مراجعة."
                    )

            except requests.exceptions.RequestException:

                st.error(
                    "❌ تعذر الوصول إلى المتجر. تأكدي من صحة الرابط."
                )

            except Exception as error:

                st.error(
                    "❌ حدث خطأ أثناء الفحص."
                )

                st.caption(
                    f"تفاصيل تقنية: {error}"
                )


# =========================================================
# التذييل
# =========================================================

st.divider()

st.caption(
    "⚖️ ميثاق | Methaq — MVP تجريبي للفحص الأولي."
)

st.caption(
    "النتائج آلية ومبدئية ولا تمثل استشارة قانونية أو ضمانًا للامتثال."
)
