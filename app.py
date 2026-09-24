import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


# =========================
# تصميم الصفحة
# =========================

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="wide"
)

st.markdown(
    """
    <style>

    .stApp {
        background: #0f172a;
        color: #f8fafc !important;
    }

    .hero {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 18px;
        padding: 35px;
        margin-bottom: 20px;
    }

    .hero h1 {
        color: #f8fafc;
        font-size: 42px;
        margin-bottom: 10px;
    }

    .hero p {
        color: #cbd5e1;
        font-size: 18px;
    }

    .info-box {
        background: #172033;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px;
        margin: 15px 0;
        color: #cbd5e1;
    }

    .metric-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 22px;
        text-align: center;
    }

    .metric-title {
        color: #94a3b8;
        font-size: 15px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 32px;
        font-weight: bold;
    }

    .result-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px;
        margin: 10px 0;
    }

    .recommendation-box {
        background: #172033;
        border-left: 4px solid #64748b;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
        color: #cbd5e1;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# العنوان
# =========================

st.markdown(
    """
    <div class="hero">
        <h1>⚖️ ميثاق | Methaq</h1>
        <p>
            منصة ذكية للفحص المبدئي لمدى اكتمال متطلبات الخصوصية
            وبعض متطلبات المتاجر الإلكترونية.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-box">
        ⚠️ نتائج المنصة تمثل مؤشر فحص مبدئي لأغراض تجريبية،
        ولا تُعد استشارة قانونية أو إثباتًا نهائيًا للامتثال.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================
# معالجة النصوص
# =========================

def normalize_text(text):
    text = text.lower()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[\u064B-\u065F]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text):
    return [
        sentence.strip()
        for sentence in re.split(r"[.!؟؛\n]+", text)
        if sentence.strip()
    ]


def sentence_has_patterns(sentence, patterns):
    normalized = normalize_text(sentence)

    return any(
        normalize_text(pattern) in normalized
        for pattern in patterns
    )


# =========================
# قواعد سياسة الخصوصية
# =========================

PRIVACY_RULES = [

    {
        "name": "تحديد البيانات الشخصية التي يتم جمعها",
        "patterns": [
            "البيانات الشخصية",
            "بياناتك الشخصية",
            "الاسم",
            "البريد الإلكتروني",
            "رقم الجوال",
            "رقم الهاتف",
            "عنوان التوصيل",
            "بيانات الدفع",
        ],
        "recommendation":
            "وضح أنواع البيانات الشخصية التي يتم جمعها من المستخدم."
    },

    {
        "name": "توضيح الغرض من جمع البيانات",
        "patterns": [
            "الغرض من جمع البيانات",
            "نستخدم البيانات من اجل",
            "تستخدم البيانات من اجل",
            "جمع البيانات بهدف",
            "لغرض",
            "تنفيذ الطلبات",
            "تقديم الخدمات",
            "تحسين تجربة المستخدم",
        ],
        "recommendation":
            "وضح الأغراض التي يتم جمع البيانات الشخصية من أجلها."
    },

    {
        "name": "توضيح طريقة جمع البيانات",
        "patterns": [
            "طريقة جمع البيانات",
            "يتم جمع البيانات",
            "نجمع البيانات",
            "عند إنشاء الحساب نجمع",
            "من خلال التسجيل",
            "من خلال النماذج",
            "عمليات الشراء",
            "عند استخدام الموقع",
        ],
        "recommendation":
            "وضح الوسائل أو الطرق التي يتم من خلالها جمع البيانات الشخصية."
    },

    {
        "name": "توضيح كيفية معالجة البيانات",
        "patterns": [
            "معالجة البيانات",
            "معالجة البيانات الشخصية",
            "تتم معالجة",
            "نقوم بمعالجة",
            "معالجة معلوماتك",
        ],
        "recommendation":
            "وضح كيفية استخدام ومعالجة البيانات الشخصية."
    },

    {
        "name": "توضيح وسيلة حفظ وتخزين البيانات",
        "patterns": [
            "حفظ وتخزين البيانات",
            "تخزين البيانات",
            "حفظ البيانات",
            "قواعد بيانات",
            "انظمة تخزين",
            "نسخ احتياطية",
        ],
        "recommendation":
            "وضح كيفية ومكان حفظ وتخزين البيانات الشخصية."
    },

    {
        "name": "توضيح مدة الاحتفاظ بالبيانات",
        "special": "retention",
        "recommendation":
            "وضح مدة الاحتفاظ بالبيانات أو المدة اللازمة لتحقيق الغرض منها."
    },

    {
        "name": "توضيح كيفية إتلاف أو حذف البيانات",
        "patterns": [
            "حذف البيانات",
            "اتلاف البيانات",
            "إتلاف البيانات",
            "يتم حذف البيانات",
            "يتم اتلاف البيانات",
            "انتهاء الحاجة",
        ],
        "recommendation":
            "وضح متى وكيف يتم حذف أو إتلاف البيانات الشخصية."
    },

    {
        "name": "توضيح حقوق صاحب البيانات",
        "patterns": [
            "حقوق صاحب البيانات",
            "حقوقك",
            "الوصول الى بياناتك",
            "تصحيح البيانات",
            "تحديث البيانات",
            "حذف البيانات",
            "سحب الموافقة",
        ],
        "recommendation":
            "وضح حقوق صاحب البيانات الشخصية بشكل واضح."
    },

    {
        "name": "توضيح طريقة ممارسة حقوق صاحب البيانات",
        "patterns": [
            "ممارسة حقوقك",
            "ممارسة الحقوق",
            "طلب ممارسة الحقوق",
            "التواصل معنا",
            "البريد الإلكتروني",
            "صفحة التواصل",
            "تقديم طلب",
        ],
        "recommendation":
            "وضح الطريقة والقنوات التي يمكن من خلالها ممارسة حقوق صاحب البيانات."
    },

    {
        "name": "توضيح المسوغ النظامي لجمع أو معالجة البيانات",
        "patterns": [
            "المسوغ النظامي",
            "الاساس النظامي",
            "الأساس النظامي",
            "الاساس القانوني",
            "الأساس القانوني",
            "المتطلبات النظامية",
            "وفقًا للنظام",
            "وفقا للنظام",
        ],
        "recommendation":
            "وضح الأساس أو المسوغ النظامي الذي تستند إليه عملية الجمع أو المعالجة."
    },

    {
        "name": "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات",
        "patterns": [
            "الإفصاح عن البيانات",
            "الافصاح عن البيانات",
            "مشاركة البيانات",
            "مشاركة بعض البيانات",
            "مقدمي الخدمات",
            "مزودي الدفع",
            "الجهات المختصة",
        ],
        "third_party_only": True,
        "recommendation":
            "وضح الجهات أو الأطراف التي قد يتم الإفصاح لها عن البيانات والظروف التي يتم فيها ذلك."
    },

    {
        "name": "توضيح النقل أو المعالجة خارج المملكة",
        "patterns": [
            "خارج المملكة",
            "خارج السعودية",
            "النقل خارج المملكة",
            "نقل البيانات",
            "معالجة البيانات خارج",
            "نقل أو معالجة البيانات خارج",
        ],
        "recommendation":
            "وضح ما إذا كانت البيانات قد تُنقل أو تُعالج خارج المملكة والضوابط ذات العلاقة."
    },

]


# =========================
# قواعد المتجر
# =========================

STORE_RULES = [

    {
        "name": "وجود سياسة الاستبدال والاسترجاع واسترداد الأموال",
        "patterns": [
            "الاستبدال والاسترجاع",
            "الاستبدال",
            "الاسترجاع",
            "استرداد الأموال",
            "استرداد المبلغ",
            "سياسة الاسترجاع",
        ],
        "recommendation":
            "أضف سياسة واضحة للاستبدال والاسترجاع واسترداد الأموال."
    },

    {
        "name": "وجود سياسة الشحن والتوصيل",
        "patterns": [
            "الشحن",
            "التوصيل",
            "سياسة الشحن",
            "مدة التوصيل",
            "تكلفة الشحن",
            "شركات الشحن",
        ],
        "recommendation":
            "وضح معلومات الشحن والتوصيل ومدده وتكاليفه."
    },

    {
        "name": "وجود وسيلة للشكاوى والاقتراحات",
        "patterns": [
            "الشكاوى",
            "الشكاوي",
            "الاقتراحات",
            "تقديم شكوى",
            "تقديم الشكوى",
        ],
        "recommendation":
            "وفر وسيلة واضحة لاستقبال الشكاوى والاقتراحات."
    },

    {
        "name": "وجود بيانات التواصل",
        "patterns": [
            "تواصل معنا",
            "اتصل بنا",
            "البريد الإلكتروني",
            "رقم الهاتف",
            "رقم الجوال",
            "واتساب",
        ],
        "recommendation":
            "أضف بيانات تواصل واضحة وسهلة الوصول."
    },

    {
        "name": "وجود بيانات المنشأة أو السجل التجاري",
        "patterns": [
            "السجل التجاري",
            "سجل تجاري",
            "رقم السجل",
            "بيانات المنشأة",
            "اسم المنشأة",
        ],
        "recommendation":
            "أظهر بيانات المنشأة والسجل التجاري عند انطباق المتطلبات."
    },

    {
        "name": "وجود بيانات الرقم الضريبي",
        "patterns": [
            "الرقم الضريبي",
            "رقم ضريبي",
            "ضريبة القيمة المضافة",
            "ضريبة القيمة المضافه",
            "vat",
        ],
        "recommendation":
            "أظهر الرقم الضريبي وبيانات ضريبة القيمة المضافة عند انطباقها."
    },

    {
        "name": "وجود سياسة الخصوصية",
        "patterns": [
            "سياسة الخصوصية",
            "سياسه الخصوصيه",
            "سياسة حماية البيانات",
            "حماية الخصوصية",
            "حماية البيانات",
        ],
        "recommendation":
            "أضف سياسة خصوصية واضحة وسهلة الوصول."
    },

]


# =========================
# فحص سياسة الخصوصية
# =========================

def analyze_privacy(text):

    normalized = normalize_text(text)
    sentences = split_sentences(text)

    results = []

    for rule in PRIVACY_RULES:

        evidence = None
        status = "🔴"

        # =========================
        # إصلاح فحص مدة الاحتفاظ
        # =========================

        if rule.get("special") == "retention":

            retention_patterns = [
                "مدة الاحتفاظ",
                "فترة الاحتفاظ",
                "مدة حفظ البيانات",
                "فترة حفظ البيانات",
                "نحتفظ بالبيانات لمدة",
                "نحتفظ بالبيانات للمدة",
                "نحتفظ ببياناتك لمدة",
                "نحتفظ ببياناتك للمدة",
                "يتم الاحتفاظ بالبيانات لمدة",
                "يتم الاحتفاظ بالبيانات للمدة",
                "للمدة اللازمة لتحقيق الغرض",
                "للمدة اللازمة للغرض",
                "حتى انتهاء الغرض",
                "حتى انتهاء الحاجة",
                "حتى تحقيق الغرض",
                "لفترة محددة",
                "لفترة زمنية محددة",
                "لمدة محددة",
                "لمدة زمنية محددة",
            ]

            duration_patterns = [
                "30 يوم",
                "60 يوم",
                "90 يوم",
                "180 يوم",
                "400 يوم",
                "يوم",
                "يوما",
                "يومًا",
                "شهر",
                "اشهر",
                "أشهر",
                "سنة",
                "سنوات",
                "عام",
                "اعوام",
                "أعوام",
                "مدة محددة",
                "فترة محددة",
                "فترة زمنية محددة",
                "للمدة اللازمة",
                "حتى انتهاء",
                "حتى تحقيق",
            ]

            for sentence in sentences:

                sentence_normalized = normalize_text(sentence)

                direct_match = any(
                    normalize_text(pattern) in sentence_normalized
                    for pattern in retention_patterns
                )

                duration_match = any(
                    normalize_text(pattern) in sentence_normalized
                    for pattern in duration_patterns
                )

                has_retention_word = any(
                    word in sentence_normalized
                    for word in [
                        "احتفاظ",
                        "نحتفظ",
                        "يتم الاحتفاظ",
                        "حفظ البيانات",
                    ]
                )

                if direct_match or (
                    has_retention_word and duration_match
                ):
                    evidence = sentence
                    status = "🟢"
                    break

            if not evidence:
                status = "🔴"

            results.append({
                "name": rule["name"],
                "status": status,
                "evidence": evidence,
                "recommendation": rule["recommendation"],
            })

            continue

        # =========================
        # القواعد الأخرى
        # =========================

        matched_patterns = []

        for pattern in rule.get("patterns", []):

            normalized_pattern = normalize_text(pattern)

            if normalized_pattern in normalized:
                matched_patterns.append(pattern)

        # طريقة جمع البيانات
        if rule["name"] == "توضيح طريقة جمع البيانات":

            strong_patterns = [
                "عند إنشاء الحساب نجمع",
                "يتم جمع البيانات من خلال التسجيل",
                "من خلال التسجيل وإنشاء الحساب",
                "من خلال النماذج وعمليات الشراء",
            ]

            if any(
                normalize_text(pattern) in normalized
                for pattern in strong_patterns
            ):
                status = "🟢"

            elif len(set(matched_patterns)) >= 2:
                status = "🟢"

            elif len(set(matched_patterns)) == 1:
                status = "🟡"

        # الإفصاح عن البيانات
        elif rule.get("third_party_only"):

            explicit_disclosure_patterns = [
                "مشاركة البيانات",
                "مشاركة بعض البيانات",
                "الافصاح عن البيانات",
                "الإفصاح عن البيانات",
            ]

            third_party_patterns = [
                "مقدمي الخدمات",
                "مزودي الدفع",
                "الجهات المختصة",
                "طرف ثالث",
                "طرف ثالث",
                "نماذج من طرف ثالث",
            ]

            has_explicit_disclosure = any(
                normalize_text(pattern) in normalized
                for pattern in explicit_disclosure_patterns
            )

            has_third_party = any(
                normalize_text(pattern) in normalized
                for pattern in third_party_patterns
            )

            if has_explicit_disclosure and has_third_party:
                status = "🟢"

            elif has_third_party:
                status = "🟡"

            elif len(set(matched_patterns)) >= 2:
                status = "🟢"

            elif len(set(matched_patterns)) == 1:
                status = "🟡"

        else:

            unique_matches = set(matched_patterns)

            if len(unique_matches) >= 2:
                status = "🟢"

            elif len(unique_matches) == 1:
                status = "🟡"

        if matched_patterns:
            evidence = None

            for sentence in sentences:
                if sentence_has_patterns(
                    sentence,
                    matched_patterns
                ):
                    evidence = sentence
                    break

        results.append({
            "name": rule["name"],
            "status": status,
            "evidence": evidence,
            "recommendation": rule["recommendation"],
        })

    return results


# =========================
# فحص المتجر
# =========================

def analyze_store(text):

    normalized = normalize_text(text)

    results = []

    for rule in STORE_RULES:

        matched = None

        for pattern in rule["patterns"]:

            normalized_pattern = normalize_text(pattern)

            if normalized_pattern in normalized:
                matched = pattern
                break

        if matched:
            status = "🟢"
            evidence = matched
        else:
            status = "⚪"
            evidence = None

        results.append({
            "name": rule["name"],
            "status": status,
            "evidence": evidence,
            "recommendation": rule["recommendation"],
        })

    return results


# =========================
# جلب الصفحة
# =========================

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


# =========================
# استخراج البيانات
# =========================

def extract_page_data(html, base_url):

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

    for link in soup.find_all("a", href=True):

        href = urljoin(
            base_url,
            link["href"]
        )

        label = link.get_text(
            " ",
            strip=True
        )

        links.append(
            (label, href)
        )

    return text, links


# =========================
# العثور على سياسة الخصوصية
# =========================

def find_privacy_page(
    base_url,
    links
):

    keywords = [
        "سياسة الخصوصية",
        "الخصوصية",
        "سياسه الخصوصيه",
        "privacy",
        "privacy policy",
    ]

    for label, href in links:

        combined = normalize_text(
            f"{label} {href}"
        )

        if any(
            normalize_text(keyword) in combined
            for keyword in keywords
        ):
            return href

    return None


# =========================
# عرض النتائج
# =========================

def display_result(result):

    st.markdown(
        f"""
        <div class="result-box">
            <h4>
                {result["status"]} {result["name"]}
            </h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    if result["evidence"]:

        with st.expander("🔎 عرض الدليل"):

            st.write(
                result["evidence"]
            )

    else:

        with st.expander(
            "🔎 لماذا ظهرت هذه النتيجة؟"
        ):

            st.write(
                "لم يعثر المحرك على دليل كافٍ في النص أو الصفحة التي تم فحصها."
            )

    st.markdown(
        f"""
        <div class="recommendation-box">
            💡 <b>التوصية:</b><br>
            {result["recommendation"]}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# حساب النسبة
# =========================

def privacy_score(results):

    if not results:
        return 0

    total = 0

    for result in results:

        if result["status"] == "🟢":
            total += 1

        elif result["status"] == "🟡":
            total += 0.5

    return round(
        (total / len(results)) * 100
    )


def store_score(results):

    if not results:
        return 0

    total = sum(
        1
        for result in results
        if result["status"] == "🟢"
    )

    return round(
        (total / len(results)) * 100
    )


# =========================
# الواجهة
# =========================

tab1, tab2 = st.tabs(
    [
        "🔎 فحص متجر",
        "📄 فحص سياسة الخصوصية"
    ]
)


# =========================
# فحص المتجر
# =========================

with tab1:

    st.subheader(
        "🔎 فحص المتجر الإلكتروني"
    )

    store_url = st.text_input(
        "رابط المتجر",
        placeholder="https://example.com"
    )

    if st.button(
        "بدء الفحص",
        type="primary"
    ):

        if not store_url.strip():

            st.warning(
                "أدخل رابط المتجر أولًا."
            )

        else:

            if not store_url.startswith(
                ("http://", "https://")
            ):
                store_url = (
                    "https://" + store_url
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

                page_text, links = (
                    extract_page_data(
                        html,
                        store_url
                    )
                )

                privacy_url = (
                    find_privacy_page(
                        store_url,
                        links
                    )
                )

                privacy_text = page_text

                if privacy_url:

                    privacy_html = fetch_page(
                        privacy_url
                    )

                    if privacy_html:

                        privacy_text, _ = (
                            extract_page_data(
                                privacy_html,
                                privacy_url
                            )
                        )

                privacy_results = (
                    analyze_privacy(
                        privacy_text
                    )
                )

                store_results = (
                    analyze_store(
                        page_text
                    )
                )

                p_score = privacy_score(
                    privacy_results
                )

                s_score = store_score(
                    store_results
                )

                overall_score = round(
                    (
                        p_score + s_score
                    ) / 2
                )

                st.markdown(
                    "### 📊 ملخص الفحص"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.markdown(
                        f"""
                        <div class="metric-box">
                            <div class="metric-title">
                                المؤشر العام
                            </div>
                            <div class="metric-value">
                                {overall_score}%
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:

                    st.markdown(
                        f"""
                        <div class="metric-box">
                            <div class="metric-title">
                                فحص المتجر
                            </div>
                            <div class="metric-value">
                                {s_score}%
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col3:

                    st.markdown(
                        f"""
                        <div class="metric-box">
                            <div class="metric-title">
                                فحص الخصوصية
                            </div>
                            <div class="metric-value">
                                {p_score}%
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    "### 📄 نتائج فحص سياسة الخصوصية"
                )

                for result in privacy_results:
                    display_result(
                        result
                    )

                st.markdown(
                    "### 🛒 نتائج فحص المتجر"
                )

                for result in store_results:
                    display_result(
                        result
                    )

                st.markdown(
                    "### 🔐 عناصر تحتاج تحققًا خارجيًا"
                )

                external_checks = [
                    "التحقق من صحة السجل التجاري",
                    "التحقق من الرقم الضريبي عند انطباقه",
                    "التحقق من بيانات المنشأة من مصدر رسمي",
                    "التحقق من أي تراخيص أو متطلبات خاصة بنشاط المتجر",
                ]

                for item in external_checks:

                    st.markdown(
                        f"⚪ {item}"
                    )


# =========================
# فحص سياسة الخصوصية
# =========================

with tab2:

    st.subheader(
        "📄 فحص سياسة الخصوصية"
    )

    privacy_input = st.text_area(
        "الصق نص سياسة الخصوصية هنا",
        height=350,
        placeholder="الصق سياسة الخصوصية..."
    )

    if st.button(
        "فحص سياسة الخصوصية",
        type="primary"
    ):

        if not privacy_input.strip():

            st.warning(
                "أدخل نص سياسة الخصوصية أولًا."
            )

        else:

            results = analyze_privacy(
                privacy_input
            )

            score = privacy_score(
                results
            )

            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-title">
                        مؤشر فحص الخصوصية
                    </div>
                    <div class="metric-value">
                        {score}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                "### 🔎 نتائج الفحص"
            )

            for result in results:
                display_result(
                    result
                )


# =========================
# التذييل
# =========================

st.markdown(
    """
    <div class="info-box">
        ⚖️ ميثاق | Methaq — نموذج أولي تجريبي
        <br>
        النتائج لأغراض الفحص المبدئي ولا تُعد استشارة قانونية.
    </div>
    """,
    unsafe_allow_html=True
)
