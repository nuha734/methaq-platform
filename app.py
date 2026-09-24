import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="wide"
)

# =========================
# CSS
# =========================

st.markdown("""
<style>

.stApp {
    background-color: #000000;
    color: white;
}

* {
    color: white;
}

.main-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #aaaaaa !important;
    text-align: center;
}

.hero-box {
    background-color: #111111;
    border: 1px solid #333333;
    border-radius: 18px;
    padding: 25px;
    margin-top: 25px;
    margin-bottom: 25px;
}

.hero-title {
    font-size: 26px;
    font-weight: 700;
    margin-bottom: 10px;
}

.hero-text {
    color: #cccccc !important;
    font-size: 16px;
    line-height: 1.8;
    font-weight: 500;
}

.metric-card {
    background-color: #111111;
    border: 1px solid #333333;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
}

.result-box {
    background-color: #111111;
    border: 1px solid #333333;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}

.result-name {
    font-size: 18px;
    font-weight: 700;
}

.evidence-box {
    background-color: #191919;
    border-right: 4px solid #666666;
    border-radius: 8px;
    padding: 12px;
    margin-top: 10px;
    line-height: 1.8;
}

.recommendation-box {
    background-color: #161616;
    border-radius: 8px;
    padding: 12px;
    margin-top: 10px;
    line-height: 1.8;
}

.footer {
    text-align: center;
    color: #888888 !important;
    margin-top: 40px;
    padding: 20px;
}

textarea,
input {
    background-color: #111111 !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
}

.stTextInput input,
.stTextArea textarea {
    color: white !important;
    -webkit-text-fill-color: white !important;
}

button {
    border-radius: 10px !important;
}

.stAlert {
    background-color: #111111 !important;
}

details {
    background-color: #111111 !important;
}

</style>
""", unsafe_allow_html=True)


# =========================
# Header
# =========================

st.markdown(
    '<div class="main-title">⚖️ ميثاق | Methaq</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">منصة ذكية للتدقيق والامتثال للأنظمة السعودية</div>',
    unsafe_allow_html=True
)


# =========================
# Hero
# =========================

st.markdown("""
<div class="hero-box">

<div class="hero-title">
منصة ميثاق
</div>

<div class="hero-text">
تساعد المنشآت على إجراء فحص أولي لسياسات الخصوصية ومتطلبات المتجر،
مع عرض الأدلة والعناصر التي تحتاج إلى مراجعة أو تحقق خارجي.
</div>

</div>
""", unsafe_allow_html=True)


st.warning(
    "⚠️ نتائج ميثاق هي مؤشر فحص مبدئي لأغراض تجريبية، "
    "ولا تُعد استشارة قانونية أو حكمًا نهائيًا بالامتثال."
)


# =========================
# Tabs
# =========================

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "store"

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "🔎 فحص متجر",
        key="tab_store",
        use_container_width=True
    ):
        st.session_state.active_tab = "store"

with col2:
    if st.button(
        "📄 فحص سياسة الخصوصية",
        key="tab_privacy",
        use_container_width=True
    ):
        st.session_state.active_tab = "privacy"


# =========================
# Privacy Rules
# =========================

PRIVACY_RULES = [

    {
        "name": "تحديد البيانات الشخصية التي يتم جمعها",
        "patterns": [
            r"نجمع",
            r"البيانات الشخصية",
            r"المعلومات الشخصية",
            r"بياناتك",
            r"بيانات المستخدم"
        ],
        "recommendation":
            "يُفضّل توضيح أنواع البيانات الشخصية التي يتم جمعها ومتى يتم جمع كل نوع."
    },

    {
        "name": "توضيح الغرض من جمع البيانات",
        "patterns": [
            r"الغرض",
            r"أغراض",
            r"نستخدم البيانات",
            r"نستخدم المعلومات",
            r"لأغراض"
        ],
        "recommendation":
            "يُفضّل توضيح الغرض من جمع كل نوع من البيانات وربطه بالاستخدام المقصود."
    },

    {
        "name": "توضيح طريقة جمع البيانات",
        "patterns": [
            r"عند إنشاء الحساب",
            r"عند التسجيل",
            r"عند الشراء",
            r"النماذج",
            r"يتم جمع",
            r"نجمع من خلال"
        ],
        "recommendation":
            "يُفضّل توضيح الوسائل أو المصادر التي تُجمع منها البيانات، مثل التسجيل أو النماذج أو عمليات الشراء."
    },

    {
        "name": "توضيح كيفية معالجة البيانات",
        "patterns": [
            r"معالجة البيانات",
            r"نعالج",
            r"معالجة معلوماتك",
            r"استخدام البيانات"
        ],
        "recommendation":
            "يُفضّل توضيح كيفية استخدام البيانات ومعالجتها بعد جمعها."
    },

    {
        "name": "توضيح وسيلة حفظ وتخزين البيانات",
        "patterns": [
            r"تخزين",
            r"نخزن",
            r"حفظ البيانات",
            r"حماية البيانات",
            r"أمن المعلومات"
        ],
        "recommendation":
            "يُفضّل توضيح كيفية حفظ وتخزين البيانات والضوابط المتخذة لحمايتها."
    },

    {
        "name": "توضيح مدة الاحتفاظ بالبيانات",
        "patterns": [
            r"الاحتفاظ",
            r"مدة الاحتفاظ",
            r"نحتفظ",
            r"فترة الاحتفاظ"
        ],
        "duration_patterns": [
            r"سنة",
            r"سنوات",
            r"أشهر",
            r"أيام",
            r"حتى انتهاء",
            r"طالما"
        ],
        "recommendation":
            "يُفضّل توضيح مدة الاحتفاظ بالبيانات أو المعيار المستخدم لتحديد مدة الاحتفاظ بها."
    },

    {
        "name": "توضيح كيفية إتلاف أو حذف البيانات",
        "patterns": [
            r"حذف البيانات",
            r"حذف معلوماتك",
            r"إتلاف البيانات",
            r"إتلاف المعلومات",
            r"حذفها"
        ],
        "recommendation":
            "يُفضّل توضيح متى وكيف يتم حذف أو إتلاف البيانات بعد انتهاء الحاجة إليها."
    },

    {
        "name": "توضيح حقوق صاحب البيانات",
        "patterns": [
            r"حقوق صاحب البيانات",
            r"حقوق المستخدم",
            r"حقوقك",
            r"حقوق العميل",
            r"الوصول إلى بياناتك",
            r"تصحيح بياناتك"
        ],
        "recommendation":
            "يُفضّل توضيح حقوق صاحب البيانات المتاحة له بصورة واضحة."
    },

    {
        "name": "توضيح طريقة ممارسة حقوق صاحب البيانات",
        "patterns": [
            r"طلب ممارسة",
            r"تقديم طلب",
            r"التواصل معنا",
            r"طلبات الحقوق",
            r"ممارسة حقوقك"
        ],
        "recommendation":
            "يُفضّل توضيح طريقة تقديم طلب لممارسة الحقوق ووسيلة التواصل المخصصة لذلك."
    },

    {
        "name": "توضيح المسوغ النظامي لجمع أو معالجة البيانات",
        "patterns": [
            r"مسوغ نظامي",
            r"أساس نظامي",
            r"الأساس القانوني",
            r"المسوغ",
            r"المتطلبات النظامية"
        ],
        "recommendation":
            "يُفضّل توضيح المسوغ النظامي المحدد الذي تستند إليه معالجة البيانات، بدل الاكتفاء بذكر المتطلبات النظامية."
    },

    {
        "name": "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات",
        "patterns": [
            r"الإفصاح",
            r"نفصح",
            r"مشاركة البيانات",
            r"نشارك البيانات",
            r"جهات خارجية",
            r"طرف ثالث",
            r"أطراف ثالثة"
        ],
        "third_party_patterns": [
            r"طرف ثالث",
            r"أطراف ثالثة",
            r"جهات خارجية",
            r"مزودي الخدمات"
        ],
        "recommendation":
            "يُفضّل توضيح الجهات أو الفئات التي قد تُفصح لها البيانات والحالات التي يتم فيها الإفصاح."
    },

    {
        "name": "توضيح النقل أو المعالجة خارج المملكة",
        "patterns": [
            r"خارج المملكة",
            r"خارج السعودية",
            r"نقل البيانات",
            r"النقل الدولي",
            r"دولة أخرى",
            r"دول أخرى"
        ],
        "recommendation":
            "يُفضّل توضيح حالات النقل أو المعالجة خارج المملكة والضوابط المطبقة عليها."
    }

]


# =========================
# Helper Functions
# =========================

def normalize_text(text):

    text = text or ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def split_sentences(text):

    text = normalize_text(text)

    sentences = re.split(
        r"[.!؟\n]+",
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def sentence_has_patterns(sentence, patterns):

    matches = []

    for pattern in patterns:

        if re.search(
            pattern,
            sentence,
            re.IGNORECASE
        ):
            matches.append(pattern)

    return matches


def get_evidence(
    text,
    patterns
):

    sentences = split_sentences(text)

    for sentence in sentences:

        matches = sentence_has_patterns(
            sentence,
            patterns
        )

        if matches:

            return sentence

    return ""


def analyze_privacy(text):

    results = []

    text = normalize_text(text)

    for rule in PRIVACY_RULES:

        name = rule["name"]

        patterns = rule["patterns"]

        evidence = ""

        matched_count = 0

        matched_sentences = []

        for sentence in split_sentences(text):

            matches = sentence_has_patterns(
                sentence,
                patterns
            )

            if matches:

                matched_count += len(
                    set(matches)
                )

                matched_sentences.append(
                    sentence
                )

        if name == "توضيح مدة الاحتفاظ بالبيانات":

            retention_found = any(
                re.search(
                    p,
                    text,
                    re.IGNORECASE
                )
                for p in patterns
            )

            duration_found = any(
                re.search(
                    p,
                    text,
                    re.IGNORECASE
                )
                for p in rule["duration_patterns"]
            )

            if retention_found and duration_found:

                status = "🟢"

                evidence = get_evidence(
                    text,
                    patterns +
                    rule["duration_patterns"]
                )

            elif retention_found:

                status = "🟡"

                evidence = get_evidence(
                    text,
                    patterns
                )

            else:

                status = "🔴"

        elif name == "توضيح طريقة جمع البيانات":

            strong_collection_patterns = [
                r"عند إنشاء الحساب",
                r"عند التسجيل",
                r"عند الشراء",
                r"من خلال النماذج",
                r"يتم جمع.*من خلال",
                r"نجمع.*عند"
            ]

            strong_found = any(
                re.search(
                    p,
                    text,
                    re.IGNORECASE
                )
                for p in strong_collection_patterns
            )

            if strong_found:

                status = "🟢"

                evidence = get_evidence(
                    text,
                    strong_collection_patterns
                )

            elif matched_count >= 2:

                status = "🟢"

                evidence = (
                    matched_sentences[0]
                    if matched_sentences
                    else ""
                )

            elif matched_count == 1:

                status = "🟡"

                evidence = (
                    matched_sentences[0]
                    if matched_sentences
                    else ""
                )

            else:

                status = "🔴"

        elif name == "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات":

            third_party_found = any(
                re.search(
                    p,
                    text,
                    re.IGNORECASE
                )
                for p in rule["third_party_patterns"]
            )

            disclosure_patterns = [
                r"الإفصاح",
                r"نفصح",
                r"مشاركة البيانات",
                r"نشارك البيانات"
            ]

            disclosure_found = any(
                re.search(
                    p,
                    text,
                    re.IGNORECASE
                )
                for p in disclosure_patterns
            )

            if disclosure_found and matched_count >= 2:

                status = "🟢"

                evidence = get_evidence(
                    text,
                    patterns
                )

            elif third_party_found:

                status = "🟡"

                evidence = get_evidence(
                    text,
                    rule["third_party_patterns"]
                )

            elif matched_count == 1:

                status = "🟡"

                evidence = get_evidence(
                    text,
                    patterns
                )

            else:

                status = "🔴"

        else:

            if matched_count >= 2:

                status = "🟢"

                evidence = (
                    matched_sentences[0]
                    if matched_sentences
                    else ""
                )

            elif matched_count == 1:

                status = "🟡"

                evidence = (
                    matched_sentences[0]
                    if matched_sentences
                    else ""
                )

            else:

                status = "🔴"

        results.append(
            {
                "name": name,
                "status": status,
                "evidence": evidence,
                "recommendation":
                    rule["recommendation"]
            }
        )

    return results


def privacy_score(results):

    total = len(results)

    if total == 0:

        return 0

    points = 0

    for result in results:

        if result["status"] == "🟢":

            points += 1

        elif result["status"] == "🟡":

            points += 0.5

    return round(
        (points / total) * 100
    )


# =========================
# Store Rules
# =========================

STORE_RULES = [

    "وجود سياسة الخصوصية",

    "وجود سياسة الاستبدال والاسترجاع واسترداد الأموال",

    "وجود سياسة الشحن والتوصيل",

    "وجود سياسة الشكاوى والمقترحات",

    "وجود بيانات التواصل",

    "وجود بيانات المنشأة أو السجل التجاري",

    "وجود الرقم الضريبي"

]


def analyze_store(text):

    text = normalize_text(text)

    results = []

    for rule in STORE_RULES:

        patterns = []

        if rule == "وجود سياسة الخصوصية":

            patterns = [
                r"سياسة الخصوصية",
                r"الخصوصية"
            ]

        elif rule == "وجود سياسة الاستبدال والاسترجاع واسترداد الأموال":

            patterns = [
                r"الاستبدال",
                r"الاسترجاع",
                r"استرداد الأموال",
                r"استرجاع الأموال"
            ]

        elif rule == "وجود سياسة الشحن والتوصيل":

            patterns = [
                r"الشحن",
                r"التوصيل",
                r"سياسة الشحن"
            ]

        elif rule == "وجود سياسة الشكاوى والمقترحات":

            patterns = [
                r"الشكاوى",
                r"الشكاوى والمقترحات",
                r"المقترحات"
            ]

        elif rule == "وجود بيانات التواصل":

            patterns = [
                r"تواصل معنا",
                r"اتصل بنا",
                r"البريد الإلكتروني",
                r"رقم الهاتف",
                r"الهاتف"
            ]

        elif rule == "وجود بيانات المنشأة أو السجل التجاري":

            patterns = [
                r"السجل التجاري",
                r"رقم السجل",
                r"اسم المنشأة",
                r"المنشأة"
            ]

        elif rule == "وجود الرقم الضريبي":

            patterns = [
                r"الرقم الضريبي",
                r"رقم ضريبي",
                r"ضريبة القيمة المضافة",
                r"VAT"
            ]

        evidence = get_evidence(
            text,
            patterns
        )

        if evidence:

            status = "🟢"

            recommendation = (
                "يظهر في المحتوى مؤشر مرتبط بهذا المتطلب."
            )

        else:

            status = "⚪"

            recommendation = (
                "لم يظهر في المحتوى المتاح مؤشر واضح لهذا المتطلب، "
                "ويُفضّل مراجعته والتحقق منه."
            )

        results.append(
            {
                "name": rule,
                "status": status,
                "evidence": evidence,
                "recommendation": recommendation
            }
        )

    return results


def store_score(results):

    if not results:

        return 0

    found = sum(
        1
        for result in results
        if result["status"] == "🟢"
    )

    return round(
        (found / len(results)) * 100
    )


# =========================
# Web Functions
# =========================

def fetch_page(url):

    headers = {
        "User-Agent":
            "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    return response.text


def extract_page_data(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    for element in soup(
        ["script", "style", "noscript"]
    ):

        element.decompose()

    text = soup.get_text(
        " ",
        strip=True
    )

    links = []

    for a in soup.find_all("a", href=True):

        links.append(
            {
                "text":
                    a.get_text(
                        " ",
                        strip=True
                    ),
                "href":
                    a["href"]
            }
        )

    return text, links


def find_privacy_page(
    base_url,
    links
):

    privacy_words = [
        "الخصوصية",
        "سياسة الخصوصية",
        "privacy",
        "privacy-policy"
    ]

    for link in links:

        link_text = (
            link["text"]
            or ""
        ).lower()

        href = (
            link["href"]
            or ""
        ).lower()

        if any(
            word.lower() in link_text
            or word.lower() in href
            for word in privacy_words
        ):

            href = link["href"]

            if href.startswith("http"):

                return href

            if href.startswith("/"):

                base = (
                    base_url.rstrip("/")
                )

                return base + href

    return None


# =========================
# Display Result
# =========================

def display_result(result):

    st.markdown(
        '<div class="result-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="result-name">'
        f'{result["status"]} {result["name"]}'
        f'</div>',
        unsafe_allow_html=True
    )

    if result.get("evidence"):

        with st.expander(
            "🔎 عرض الدليل"
        ):

            st.markdown(
                f'<div class="evidence-box">'
                f'{result["evidence"]}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="recommendation-box">'
                f'<b>💡 التوصية:</b><br>'
                f'{result["recommendation"]}'
                f'</div>',
                unsafe_allow_html=True
            )

    else:

        with st.expander(
            "🔎 لماذا ظهرت هذه النتيجة؟"
        ):

            st.markdown(
                f'<div class="recommendation-box">'
                f'<b>💡 التوصية:</b><br>'
                f'{result["recommendation"]}'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================
# STORE TAB
# =========================

if st.session_state.active_tab == "store":

    st.markdown(
        '<div class="section-title">'
        '🔎 فحص متجر'
        '</div>',
        unsafe_allow_html=True
    )

    store_url = st.text_input(
        "رابط المتجر",
        placeholder="https://example.com"
    )

    if st.button(
        "🚀 ابدأ الفحص",
        use_container_width=True
    ):

        if not store_url:

            st.error(
                "فضلاً أدخل رابط المتجر."
            )

        else:

            try:

                with st.spinner(
                    "جاري فحص المتجر..."
                ):

                    html = fetch_page(
                        store_url
                    )

                    page_text, links = (
                        extract_page_data(
                            html
                        )
                    )

                    privacy_url = (
                        find_privacy_page(
                            store_url,
                            links
                        )
                    )

                    privacy_text = ""

                    if privacy_url:

                        try:

                            privacy_html = (
                                fetch_page(
                                    privacy_url
                                )
                            )

                            privacy_text, _ = (
                                extract_page_data(
                                    privacy_html
                                )
                            )

                        except Exception:

                            privacy_text = ""

                    store_results = (
                        analyze_store(
                            page_text
                        )
                    )

                    if privacy_text:

                        privacy_results = (
                            analyze_privacy(
                                privacy_text
                            )
                        )

                    else:

                        privacy_results = (
                            analyze_privacy(
                                page_text
                            )
                        )

                    s_score = store_score(
                        store_results
                    )

                    p_score = privacy_score(
                        privacy_results
                    )

                    overall = round(
                        (
                            s_score +
                            p_score
                        ) / 2
                    )

                st.success(
                    "تم الانتهاء من الفحص المبدئي."
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.markdown(
                        f"""
                        <div class="metric-card">
                        <div>المؤشر العام</div>
                        <h2>{overall}%</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:

                    st.markdown(
                        f"""
                        <div class="metric-card">
                        <div>فحص المتجر</div>
                        <h2>{s_score}%</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col3:

                    st.markdown(
                        f"""
                        <div class="metric-card">
                        <div>فحص الخصوصية</div>
                        <h2>{p_score}%</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    '<div class="section-title">'
                    '🏪 نتائج فحص المتجر'
                    '</div>',
                    unsafe_allow_html=True
                )

                for result in store_results:

                    display_result(
                        result
                    )

                st.markdown(
                    '<div class="section-title">'
                    '📄 نتائج فحص سياسة الخصوصية'
                    '</div>',
                    unsafe_allow_html=True
                )

                if privacy_url:

                    st.info(
                        f"تم العثور على صفحة الخصوصية تلقائيًا: {privacy_url}"
                    )

                else:

                    st.warning(
                        "لم يتم العثور على صفحة خصوصية واضحة، "
                        "وتم الفحص من المحتوى المتاح."
                    )

                for result in privacy_results:

                    display_result(
                        result
                    )

                st.markdown(
                    '<div class="section-title">'
                    '🌐 عناصر تحتاج تحقق خارجي'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.info(
                    "بعض المتطلبات لا يمكن التحقق منها بالكامل "
                    "من محتوى الموقع فقط، وقد تحتاج إلى تحقق خارجي."
                )

            except Exception as e:

                st.error(
                    f"تعذر إتمام الفحص: {e}"
                )


# =========================
# PRIVACY TAB
# =========================

if st.session_state.active_tab == "privacy":

    st.markdown(
        '<div class="section-title">'
        '📄 فحص سياسة الخصوصية'
        '</div>',
        unsafe_allow_html=True
    )

    privacy_input = st.text_area(
        "الصق نص سياسة الخصوصية هنا",
        height=300,
        placeholder="ألصق نص سياسة الخصوصية..."
    )

    if st.button(
        "🔍 فحص السياسة",
        use_container_width=True
    ):

        if not privacy_input.strip():

            st.error(
                "فضلاً أضف نص سياسة الخصوصية."
            )

        else:

            results = analyze_privacy(
                privacy_input
            )

            score = privacy_score(
                results
            )

            green = sum(
                1
                for r in results
                if r["status"] == "🟢"
            )

            yellow = sum(
                1
                for r in results
                if r["status"] == "🟡"
            )

            red = sum(
                1
                for r in results
                if r["status"] == "🔴"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.markdown(
                    f"""
                    <div class="metric-card">
                    <div>المؤشر</div>
                    <h2>{score}%</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col2:

                st.markdown(
                    f"""
                    <div class="metric-card">
                    <div>مؤشرات واضحة</div>
                    <h2>{green}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:

                st.markdown(
                    f"""
                    <div class="metric-card">
                    <div>تحتاج مراجعة</div>
                    <h2>{yellow}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col4:

                st.markdown(
                    f"""
                    <div class="metric-card">
                    <div>لم يتم العثور عليها</div>
                    <h2>{red}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(
                '<div class="section-title">'
                '📋 تفاصيل الفحص'
                '</div>',
                unsafe_allow_html=True
            )

            for result in results:

                display_result(
                    result
                )


# =========================
# Footer
# =========================

st.markdown(
    """
    <div class="footer">
        ⚖️ ميثاق | Methaq<br>
        نموذج أولي تجريبي - LegalTech
    </div>
    """,
    unsafe_allow_html=True
)
