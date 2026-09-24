import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# =========================================================
# إعداد الصفحة
# =========================================================

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="wide"
)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #000000 !important;
    color: #ffffff !important;
}

html, body, [class*="css"] {
    color: #ffffff !important;
}

h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #ffffff;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
    color: #ffffff !important;
}

.subtitle {
    text-align: center;
    color: #cccccc !important;
    font-size: 18px;
    margin-bottom: 25px;
}

.hero-box {
    background: #111111;
    border: 1px solid #333333;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    margin-bottom: 20px;
}

.hero-title {
    font-size: 26px;
    font-weight: 700;
    color: #ffffff !important;
}

.hero-text {
    color: #cccccc !important;
    font-size: 16px;
}

.metric-card {
    background: #111111;
    border: 1px solid #333333;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    margin-bottom: 15px;
}

.metric-number {
    font-size: 32px;
    font-weight: 800;
    color: #ffffff !important;
}

.metric-label {
    font-size: 14px;
    color: #aaaaaa !important;
}

.section-title {
    font-size: 24px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
    color: #ffffff !important;
}

.result-box {
    background: #111111;
    border: 1px solid #333333;
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 10px;
}

.result-name {
    font-size: 17px;
    font-weight: 600;
    color: #ffffff !important;
}

.evidence-box {
    background: #191919;
    border: 1px solid #444444;
    border-radius: 10px;
    padding: 12px;
    margin-top: 10px;
    color: #dddddd !important;
    line-height: 1.8;
}

.recommendation-box {
    background: #151515;
    border-right: 3px solid #777777;
    border-radius: 8px;
    padding: 12px;
    margin-top: 10px;
    color: #eeeeee !important;
    line-height: 1.8;
}

.footer {
    text-align: center;
    color: #777777 !important;
    margin-top: 40px;
    padding: 20px;
}

textarea, input {
    background-color: #111111 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

textarea::placeholder,
input::placeholder {
    color: #888888 !important;
    -webkit-text-fill-color: #888888 !important;
}

.stTextInput > div > div > input {
    background-color: #111111 !important;
    color: #ffffff !important;
}

.stTextArea textarea {
    background-color: #111111 !important;
    color: #ffffff !important;
}

button {
    border-radius: 10px !important;
}

.stAlert {
    background-color: #111111 !important;
    color: #ffffff !important;
}

div[data-testid="stExpander"] {
    background-color: #111111 !important;
    border: 1px solid #333333 !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# العنوان والنص الأصلي
# =========================================================

st.markdown(
    '<div class="main-title">⚖️ ميثاق | Methaq</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">منصة ذكية للتدقيق والامتثال للأنظمة السعودية</div>',
    unsafe_allow_html=True
)

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

st.info(
    "⚠️ نتائج ميثاق هي مؤشر فحص مبدئي لأغراض تجريبية، "
    "ولا تُعد استشارة قانونية أو حكمًا نهائيًا بالامتثال."
)


# =========================================================
# أدوات النص
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.replace("\u200f", " ")
    text = text.replace("\u200e", " ")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text):

    text = normalize_text(text)

    parts = re.split(
        r"(?<=[\.\!\؟\?؛;])\s+",
        text
    )

    return [
        p.strip()
        for p in parts
        if p.strip()
    ]


def sentence_has_patterns(sentence, patterns):

    for pattern in patterns:

        if re.search(
            pattern,
            sentence,
            re.IGNORECASE
        ):
            return True

    return False


def get_evidence(text, patterns):

    sentences = split_sentences(text)

    for sentence in sentences:

        if sentence_has_patterns(
            sentence,
            patterns
        ):
            return sentence

    return ""


# =========================================================
# قواعد الخصوصية
# =========================================================

PRIVACY_RULES = [

    {
        "name": "تحديد البيانات الشخصية التي يتم جمعها",
        "patterns": [
            r"بيانات.*شخصية",
            r"المعلومات.*الشخصية",
            r"نجمع.*بيانات",
            r"نجمع.*معلومات",
            r"الاسم",
            r"رقم.*الهاتف",
            r"البريد.*الإلكتروني",
            r"عنوان.*الشحن"
        ],
        "recommendation":
            "يُفضّل توضيح أنواع البيانات الشخصية التي يتم جمعها ومتى يتم جمع كل نوع."
    },

    {
        "name": "توضيح الغرض من جمع البيانات",
        "patterns": [
            r"الغرض",
            r"أغراض.*جمع",
            r"لأغراض",
            r"تقديم.*الخدمات",
            r"تنفيذ.*الطلبات",
            r"تحسين.*الخدمات",
            r"التواصل.*مع.*المستخدم"
        ],
        "recommendation":
            "يُفضّل توضيح الغرض من جمع كل نوع من البيانات وربطه بالاستخدام المقصود."
    },

    {
        "name": "توضيح طريقة جمع البيانات",
        "patterns": [
            r"عند.*إنشاء.*الحساب",
            r"عند.*التسجيل",
            r"عند.*الشراء",
            r"عند.*إتمام.*الطلب",
            r"من.*خلال.*النماذج",
            r"من.*المستخدم",
            r"ملفات.*الارتباط",
            r"ملفات.*تعريف.*الارتباط"
        ],
        "strong_patterns": [
            r"عند.*إنشاء.*الحساب.*نجمع",
            r"عند.*التسجيل.*نجمع",
            r"عند.*الشراء.*نجمع",
            r"من.*خلال.*النماذج.*نجمع",
            r"يجمع.*من.*المستخدم"
        ],
        "recommendation":
            "يُفضّل توضيح الوسائل أو المصادر التي تُجمع منها البيانات، مثل التسجيل أو النماذج أو عمليات الشراء."
    },

    {
        "name": "توضيح كيفية معالجة البيانات",
        "patterns": [
            r"معالجة.*البيانات",
            r"نعالج.*البيانات",
            r"استخدام.*البيانات",
            r"تستخدم.*البيانات",
            r"تحليل.*البيانات",
            r"معالجة.*المعلومات"
        ],
        "recommendation":
            "يُفضّل توضيح كيفية استخدام البيانات ومعالجتها بعد جمعها."
    },

    {
        "name": "توضيح وسيلة حفظ وتخزين البيانات",
        "patterns": [
            r"تخزين.*البيانات",
            r"حفظ.*البيانات",
            r"تُحفظ.*البيانات",
            r"تخزن.*البيانات",
            r"خوادم",
            r"وسائل.*الحماية",
            r"إجراءات.*الأمان",
            r"أمن.*المعلومات"
        ],
        "recommendation":
            "يُفضّل توضيح كيفية حفظ وتخزين البيانات والضوابط المتخذة لحمايتها."
    },

    {
        "name": "توضيح مدة الاحتفاظ بالبيانات",
        "special": "retention",
        "patterns": [
            r"الاحتفاظ",
            r"نحتفظ",
            r"مدة.*الاحتفاظ",
            r"فترة.*الاحتفاظ",
            r"البيانات.*لمدة"
        ],
        "duration_patterns": [
            r"\d+\s*(?:يوم|أيام|شهر|أشهر|سنة|سنوات)",
            r"حتى.*انتهاء",
            r"طوال.*مدة",
            r"عند.*انتهاء.*الحاجة",
            r"طالما.*ضرورية"
        ],
        "recommendation":
            "يُفضّل توضيح مدة الاحتفاظ بالبيانات أو المعيار المستخدم لتحديد مدة الاحتفاظ بها."
    },

    {
        "name": "توضيح كيفية إتلاف أو حذف البيانات",
        "patterns": [
            r"حذف.*البيانات",
            r"إتلاف.*البيانات",
            r"حذف.*المعلومات",
            r"إتلاف.*المعلومات",
            r"التخلص.*من.*البيانات",
            r"مسح.*البيانات"
        ],
        "recommendation":
            "يُفضّل توضيح متى وكيف يتم حذف أو إتلاف البيانات بعد انتهاء الحاجة إليها."
    },

    {
        "name": "توضيح حقوق صاحب البيانات",
        "patterns": [
            r"حقوق.*صاحب.*البيانات",
            r"حقوق.*المستخدم",
            r"حق.*الوصول",
            r"حق.*التصحيح",
            r"حق.*الحذف",
            r"حق.*الاعتراض",
            r"حق.*سحب.*الموافقة"
        ],
        "recommendation":
            "يُفضّل توضيح حقوق صاحب البيانات المتاحة له بصورة واضحة."
    },

    {
        "name": "توضيح طريقة ممارسة حقوق صاحب البيانات",
        "patterns": [
            r"ممارسة.*الحقوق",
            r"طلب.*الوصول",
            r"طلب.*التصحيح",
            r"طلب.*الحذف",
            r"يمكن.*للمستخدم.*طلب",
            r"التواصل.*لممارسة.*الحقوق",
            r"طلبات.*البيانات"
        ],
        "recommendation":
            "يُفضّل توضيح طريقة تقديم طلب لممارسة الحقوق ووسيلة التواصل المخصصة لذلك."
    },

    {
        "name": "توضيح المسوغ النظامي لجمع أو معالجة البيانات",
        "patterns": [
            r"المسوغ.*النظامي",
            r"الأساس.*النظامي",
            r"الأساس.*القانوني",
            r"المسوغ.*القانوني",
            r"الموافقة",
            r"الالتزام.*النظامي",
            r"متطلبات.*نظامية"
        ],
        "recommendation":
            "يُفضّل توضيح المسوغ النظامي المحدد الذي تستند إليه معالجة البيانات، بدل الاكتفاء بذكر المتطلبات النظامية."
    },

    {
        "name": "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات",
        "patterns": [
            r"الإفصاح.*عن.*البيانات",
            r"مشاركة.*البيانات",
            r"نشارك.*البيانات",
            r"نُفصح.*عن.*البيانات",
            r"الجهات.*التي",
            r"أطراف.*ثالثة",
            r"طرف.*ثالث",
            r"مقدمي.*الخدمات",
            r"مزودي.*الخدمات"
        ],
        "third_party_only": True,
        "recommendation":
            "يُفضّل توضيح الجهات أو الفئات التي قد تُفصح لها البيانات والحالات التي يتم فيها الإفصاح."
    },

    {
        "name": "توضيح النقل أو المعالجة خارج المملكة",
        "patterns": [
            r"خارج.*المملكة",
            r"خارج.*السعودية",
            r"نقل.*البيانات.*خارج",
            r"معالجة.*البيانات.*خارج",
            r"نقل.*البيانات.*دولي",
            r"النقل.*الدولي"
        ],
        "recommendation":
            "يُفضّل توضيح حالات النقل أو المعالجة خارج المملكة والضوابط المطبقة عليها."
    }

]


# =========================================================
# فحص الخصوصية
# =========================================================

def analyze_privacy(text):

    text = normalize_text(text)

    results = []

    for rule in PRIVACY_RULES:

        name = rule["name"]
        patterns = rule["patterns"]

        evidence = ""
        status = "🔴"

        # الاحتفاظ
        if rule.get("special") == "retention":

            has_retention = any(
                re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )
                for pattern in patterns
            )

            has_duration = any(
                re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )
                for pattern in rule["duration_patterns"]
            )

            if has_retention and has_duration:

                status = "🟢"

                for sentence in split_sentences(text):

                    if (
                        sentence_has_patterns(
                            sentence,
                            patterns
                        )
                        and
                        sentence_has_patterns(
                            sentence,
                            rule["duration_patterns"]
                        )
                    ):
                        evidence = sentence
                        break

            elif has_retention:

                status = "🟡"

                evidence = get_evidence(
                    text,
                    patterns
                )

        # طريقة الجمع
        elif "strong_patterns" in rule:

            strong_match = any(
                re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )
                for pattern in rule["strong_patterns"]
            )

            if strong_match:

                status = "🟢"

                evidence = get_evidence(
                    text,
                    rule["strong_patterns"]
                )

            else:

                matches = []

                for pattern in patterns:

                    if re.search(
                        pattern,
                        text,
                        re.IGNORECASE
                    ):
                        matches.append(pattern)

                if len(set(matches)) >= 2:

                    status = "🟢"

                    evidence = get_evidence(
                        text,
                        patterns
                    )

                elif len(set(matches)) == 1:

                    status = "🟡"

                    evidence = get_evidence(
                        text,
                        patterns
                    )

        # الإفصاح للجهات الأخرى
        elif rule.get("third_party_only"):

            third_party_patterns = [
                r"أطراف.*ثالثة",
                r"طرف.*ثالث",
                r"مقدمي.*الخدمات",
                r"مزودي.*الخدمات",
                r"نماذج.*من.*طرف.*ثالث"
            ]

            disclosure_patterns = [
                r"الإفصاح",
                r"مشاركة.*البيانات",
                r"نشارك.*البيانات",
                r"نُفصح.*عن.*البيانات"
            ]

            has_third_party = any(
                re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )
                for pattern in third_party_patterns
            )

            has_disclosure = any(
                re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )
                for pattern in disclosure_patterns
            )

            if has_disclosure:

                status = "🟢"

                evidence = get_evidence(
                    text,
                    disclosure_patterns
                )

            elif has_third_party:

                status = "🟡"

                evidence = get_evidence(
                    text,
                    third_party_patterns
                )

        # القواعد العادية
        else:

            matches = []

            for pattern in patterns:

                if re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                ):
                    matches.append(pattern)

            unique_matches = len(
                set(matches)
            )

            if unique_matches >= 2:

                status = "🟢"

                evidence = get_evidence(
                    text,
                    patterns
                )

            elif unique_matches == 1:

                status = "🟡"

                evidence = get_evidence(
                    text,
                    patterns
                )

        results.append({
            "name": name,
            "status": status,
            "evidence": evidence,
            "recommendation":
                rule["recommendation"]
        })

    return results


# =========================================================
# قواعد المتجر
# =========================================================

STORE_RULES = [

    {
        "name": "وجود سياسة الخصوصية",
        "patterns": [
            r"سياسة الخصوصية",
            r"الخصوصية",
            r"privacy policy"
        ]
    },

    {
        "name": "وجود سياسة الاستبدال والاسترجاع واسترداد الأموال",
        "patterns": [
            r"الاستبدال",
            r"الاسترجاع",
            r"استرداد.*الأموال",
            r"استرداد.*المبلغ",
            r"refund",
            r"return"
        ]
    },

    {
        "name": "وجود سياسة الشحن والتوصيل",
        "patterns": [
            r"الشحن",
            r"التوصيل",
            r"التسليم",
            r"delivery",
            r"shipping"
        ]
    },

    {
        "name": "وجود سياسة الشكاوى والمقترحات",
        "patterns": [
            r"الشكاوى",
            r"الشكوى",
            r"المقترحات",
            r"خدمة العملاء"
        ]
    },

    {
        "name": "وجود بيانات التواصل",
        "patterns": [
            r"تواصل معنا",
            r"اتصل بنا",
            r"البريد الإلكتروني",
            r"رقم الهاتف",
            r"واتساب",
            r"contact"
        ]
    },

    {
        "name": "وجود بيانات المنشأة أو السجل التجاري",
        "patterns": [
            r"السجل التجاري",
            r"سجل تجاري",
            r"رقم.*السجل",
            r"بيانات.*المنشأة",
            r"اسم.*المنشأة"
        ]
    },

    {
        "name": "وجود الرقم الضريبي",
        "patterns": [
            r"الرقم الضريبي",
            r"رقم.*ضريبي",
            r"ضريبة القيمة المضافة",
            r"VAT"
        ]
    }

]


def analyze_store(text):

    text = normalize_text(text)

    results = []

    for rule in STORE_RULES:

        evidence = get_evidence(
            text,
            rule["patterns"]
        )

        status = "🟢" if evidence else "⚪"

        if evidence:

            recommendation = (
                "يظهر في المحتوى مؤشر مرتبط بهذا المتطلب."
            )

        else:

            recommendation = (
                "لم يظهر في المحتوى المتاح مؤشر واضح لهذا المتطلب، "
                "ويُفضّل مراجعته والتحقق منه."
            )

        results.append({
            "name": rule["name"],
            "status": status,
            "evidence": evidence,
            "recommendation": recommendation
        })

    return results


# =========================================================
# جلب الموقع
# =========================================================

def fetch_page(url):

    try:

        headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        return response.text

    except Exception:

        return ""


# =========================================================
# استخراج بيانات الصفحة
# =========================================================

def extract_page_data(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg"
    ]):
        tag.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    links = []

    for a in soup.find_all(
        "a",
        href=True
    ):

        title = a.get_text(
            " ",
            strip=True
        )

        href = a.get("href")

        if href:

            links.append({
                "title": title,
                "href": href
            })

    return text, links


# =========================================================
# البحث عن سياسة الخصوصية
# =========================================================

def find_privacy_page(
    base_url,
    links
):

    keywords = [
        "سياسة الخصوصية",
        "الخصوصية",
        "privacy",
        "privacy-policy"
    ]

    for link in links:

        title = normalize_text(
            link["title"]
        ).lower()

        href = link["href"].lower()

        for keyword in keywords:

            if (
                keyword.lower() in title
                or
                keyword.lower() in href
            ):

                return urljoin(
                    base_url,
                    link["href"]
                )

    return None


# =========================================================
# عرض النتيجة
# =========================================================

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


# =========================================================
# حساب الدرجات
# =========================================================

def privacy_score(results):

    if not results:
        return 0

    points = 0

    for result in results:

        if result["status"] == "🟢":
            points += 1

        elif result["status"] == "🟡":
            points += 0.5

    return round(
        (points / len(results)) * 100
    )


def store_score(results):

    if not results:
        return 0

    passed = sum(
        1
        for result in results
        if result["status"] == "🟢"
    )

    return round(
        (passed / len(results)) * 100
    )


# =========================================================
# التبويبات
# =========================================================

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


# =========================================================
# فحص المتجر
# =========================================================

if st.session_state.active_tab == "store":

    st.markdown(
        '<div class="section-title">'
        '🔎 فحص المتجر'
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

            st.warning(
                "أدخل رابط المتجر أولًا."
            )

        else:

            if not store_url.startswith(
                ("http://", "https://")
            ):

                store_url = (
                    "https://" +
                    store_url
                )

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

                store_text, links = extract_page_data(
                    html
                )

                privacy_url = find_privacy_page(
                    store_url,
                    links
                )

                store_results = analyze_store(
                    store_text
                )

                s_score = store_score(
                    store_results
                )

                privacy_results = []

                if privacy_url:

                    privacy_html = fetch_page(
                        privacy_url
                    )

                    if privacy_html:

                        privacy_text, _ = extract_page_data(
                            privacy_html
                        )

                        privacy_results = analyze_privacy(
                            privacy_text
                        )

                p_score = privacy_score(
                    privacy_results
                )

                if privacy_results:

                    overall = round(
                        (s_score + p_score) / 2
                    )

                else:

                    overall = s_score

                st.markdown(
                    '<div class="section-title">'
                    '📊 ملخص الفحص'
                    '</div>',
                    unsafe_allow_html=True
                )

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-number">
                                {overall}%
                            </div>
                            <div class="metric-label">
                                المؤشر العام
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c2:

                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-number">
                                {s_score}%
                            </div>
                            <div class="metric-label">
                                فحص المتجر
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c3:

                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div class="metric-number">
                                {p_score}%
                            </div>
                            <div class="metric-label">
                                فحص الخصوصية
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    '<div class="section-title">'
                    '🔍 تفاصيل فحص المتجر'
                    '</div>',
                    unsafe_allow_html=True
                )

                for result in store_results:

                    display_result(
                        result
                    )

                st.markdown(
                    '<div class="section-title">'
                    '📄 فحص سياسة الخصوصية'
                    '</div>',
                    unsafe_allow_html=True
                )

                if privacy_url:

                    st.success(
                        "تم العثور على صفحة سياسة الخصوصية وفحص محتواها."
                    )

                    st.caption(
                        f"صفحة الخصوصية المكتشفة: {privacy_url}"
                    )

                    for result in privacy_results:

                        display_result(
                            result
                        )

                else:

                    st.warning(
                        "لم يتم العثور تلقائيًا على صفحة واضحة لسياسة الخصوصية."
                    )

                st.markdown(
                    '<div class="section-title">'
                    '🌐 عناصر تحتاج تحققًا خارجيًا'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.info(
                    "بعض المتطلبات لا يمكن التحقق منها من محتوى الموقع فقط، "
                    "مثل بعض بيانات التسجيل أو المعلومات الرسمية، "
                    "ولذلك تحتاج إلى تحقق خارجي."
                )


# =========================================================
# فحص السياسة يدويًا
# =========================================================

if st.session_state.active_tab == "privacy":

    st.markdown(
        '<div class="section-title">'
        '📄 فحص سياسة الخصوصية'
        '</div>',
        unsafe_allow_html=True
    )

    privacy_text = st.text_area(
        "الصق نص سياسة الخصوصية هنا",
        height=400,
        placeholder="الصق نص سياسة الخصوصية هنا..."
    )

    if st.button(
        "🔍 فحص السياسة",
        use_container_width=True
    ):

        if not privacy_text.strip():

            st.warning(
                "الصق نص سياسة الخصوصية أولًا."
            )

        else:

            results = analyze_privacy(
                privacy_text
            )

            score = privacy_score(
                results
            )

            clear = sum(
                1
                for result in results
                if result["status"] == "🟢"
            )

            review = sum(
                1
                for result in results
                if result["status"] == "🟡"
            )

            missing = sum(
                1
                for result in results
                if result["status"] == "🔴"
            )

            st.markdown(
                '<div class="section-title">'
                '📊 ملخص الفحص'
                '</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-number">
                            {score}%
                        </div>
                        <div class="metric-label">
                            المؤشر
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c2:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-number">
                            {clear}
                        </div>
                        <div class="metric-label">
                            مؤشرات واضحة
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c3:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-number">
                            {review}
                        </div>
                        <div class="metric-label">
                            تحتاج مراجعة
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c4:

                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-number">
                            {missing}
                        </div>
                        <div class="metric-label">
                            لم يتم العثور عليها
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown(
                '<div class="section-title">'
                '🔍 تفاصيل الفحص'
                '</div>',
                unsafe_allow_html=True
            )

            for result in results:

                display_result(
                    result
                )


# =========================================================
# التذييل
# =========================================================

st.markdown("""
<div class="footer">
    ⚖️ ميثاق | Methaq
    <br>
    نموذج أولي تجريبي - LegalTech
</div>
""", unsafe_allow_html=True)
