import re
import requests
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
# إعدادات الواجهة
# =========================================================

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>

    .stApp {
        background: #f7f8fb;
        color: #1f2937 !important;
    }

    .main-title {
        text-align: center;
        padding: 20px 0 5px 0;
        color: #1f2937 !important;
    }

    .main-title h1 {
        font-size: 42px;
        margin-bottom: 5px;
        font-weight: 800;
        color: #1f2937 !important;
    }

    .main-title p {
        color: #667085 !important;
        font-size: 17px;
        margin-top: 0;
    }

    .hero-box {
        background: white;
        color: #1f2937 !important;
        padding: 28px;
        border-radius: 18px;
        border: 1px solid #e6e8ee;
        margin: 10px 0 25px 0;
        box-shadow: 0 4px 18px rgba(0,0,0,0.04);
    }

    .hero-box b {
        color: #1f2937 !important;
    }

    .section-title {
        font-size: 24px;
        font-weight: 750;
        margin-top: 10px;
        margin-bottom: 12px;
        color: #1f2937 !important;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e6e8ee;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.03);
    }

    div[data-testid="stMetric"] label {
        color: #475467 !important;
    }

    div[data-testid="stMetric"] div {
        color: #1f2937 !important;
    }

    .result-box {
        background: white;
        color: #1f2937 !important;
        border: 1px solid #e6e8ee;
        border-radius: 14px;
        padding: 14px 18px;
        margin: 8px 0;
    }

    .result-box p,
    .result-box span,
    .result-box div {
        color: #1f2937 !important;
    }

    /* =====================================================
       جميع الأزرار: أسود + نص أبيض
       ===================================================== */

    .stButton > button {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border: 1px solid #1f2937 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    .stButton > button p {
        color: #ffffff !important;
    }

    .stButton > button span {
        color: #ffffff !important;
    }

    .stButton > button div {
        color: #ffffff !important;
    }

    .stButton > button:hover {
        background-color: #111827 !important;
        color: #ffffff !important;
        border-color: #111827 !important;
    }

    .stButton > button:hover p,
    .stButton > button:hover span,
    .stButton > button:hover div {
        color: #ffffff !important;
    }

    .footer-note {
        text-align: center;
        color: #667085 !important;
        font-size: 13px;
        margin-top: 30px;
        padding: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# معالجة النص
# =========================================================

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
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text):

    parts = re.split(
        r"[.!؟؛\n]+",
        text
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def sentence_has_patterns(sentence, patterns):

    normalized = normalize_text(sentence)

    return any(
        normalize_text(pattern) in normalized
        for pattern in patterns
    )


# =========================================================
# قواعد الخصوصية
# =========================================================

PRIVACY_RULES = [

    {
        "name": "تحديد البيانات الشخصية التي يتم جمعها",
        "patterns": [
            "البيانات التي نجمعها",
            "البيانات التي قد نجمعها",
            "البيانات الشخصية التي نجمعها",
            "نجمع الاسم",
            "نجمع البيانات",
            "عند إنشاء الحساب نجمع",
            "عند انشاء الحساب نجمع",
            "بيانات التجار",
            "الاسم والبريد الإلكتروني",
            "الاسم والبريد الالكتروني",
            "رقم الجوال",
            "رقم الهاتف",
            "عنوان التوصيل",
            "بيانات الدفع",
            "بيانات الطلب",
        ],
    },

    {
        "name": "توضيح الغرض من جمع البيانات",
        "patterns": [
            "الغرض من جمع",
            "الغرض من الجمع",
            "نستخدم البيانات من اجل",
            "نستخدم البيانات لأجل",
            "نستخدم البيانات لغرض",
            "تستخدم البيانات من اجل",
            "تستخدم البيانات لأجل",
            "الهدف من جمع",
            "اغراض جمع البيانات",
            "أغراض جمع البيانات",
            "للتحقق من هوية",
            "الحد من الاحتيال",
            "غسل الاموال",
            "غسل الأموال",
            "تنفيذ الطلبات",
            "تقديم الخدمات",
            "تحسين الخدمات",
            "تحسين تجربة المستخدم",
            "معالجة المدفوعات",
        ],
    },

    {
        "name": "توضيح طريقة جمع البيانات",
        "patterns": [
            "نجمع البيانات من خلال",
            "يتم جمع البيانات من خلال",
            "طريقة جمع البيانات",
            "طرق جمع البيانات",
            "مصادر جمع البيانات",
            "عند إنشاء الحساب نجمع",
            "عند انشاء الحساب نجمع",
            "عند إنشاء حساب نجمع",
            "عند انشاء حساب نجمع",
            "عند التسجيل نجمع",
            "عند التسجيل يتم جمع",
            "من خلال التسجيل",
            "من خلال إنشاء الحساب",
            "من خلال انشاء الحساب",
            "من خلال النماذج",
            "من خلال عمليات الشراء",
            "من خلال التواصل",
            "عند استخدام المنصة",
            "عند استخدام الموقع",
        ],

        "strong_patterns": [
            "عند إنشاء الحساب نجمع",
            "عند انشاء الحساب نجمع",
            "عند إنشاء حساب نجمع",
            "عند انشاء حساب نجمع",
            "يتم جمع البيانات من خلال",
            "نجمع البيانات من خلال",
            "من خلال التسجيل",
            "من خلال إنشاء الحساب",
            "من خلال انشاء الحساب",
        ],
    },

    {
        "name": "توضيح كيفية معالجة البيانات",
        "patterns": [
            "تتم معالجة البيانات",
            "معالجة البيانات الشخصية",
            "كيفية معالجة البيانات",
            "معالجة بياناتك",
            "معالجة البيانات",
            "نقوم بمعالجة",
            "تتم معالجة",
            "اغراض المعالجة",
            "أغراض المعالجة",
            "طريقة معالجة البيانات",
        ],
    },

    {
        "name": "توضيح وسيلة حفظ وتخزين البيانات",
        "patterns": [
            "حفظ البيانات",
            "تخزين البيانات",
            "يتم حفظ البيانات",
            "يتم تخزين البيانات",
            "تخزين بياناتك",
            "حفظ بياناتك",
            "قاعدة البيانات",
            "قواعد البيانات",
            "النسخ الاحتياطية",
            "نظام التخزين",
            "أنظمة التخزين",
        ],
    },

    {
        "name": "توضيح مدة الاحتفاظ بالبيانات",
        "patterns": [
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
            "يتم الاحتفاظ ببياناتك لمدة",
            "يتم الاحتفاظ ببياناتك للمدة",
            "للمدة اللازمة لتحقيق الغرض",
            "للمدة اللازمة للغرض",
            "حتى انتهاء الغرض",
            "حتى انتهاء الحاجة",
            "حتى تحقيق الغرض",
            "لفترة محددة",
            "لفترة زمنية محددة",
            "لمدة محددة",
            "30 يوم",
            "30 يوما",
            "30 يومًا",
            "60 يوم",
            "60 يوما",
            "60 يومًا",
            "90 يوم",
            "90 يوما",
            "90 يومًا",
            "180 يوم",
            "180 يوما",
            "180 يومًا",
            "400 يوم",
            "400 يوما",
            "400 يومًا",
            "سنة",
            "سنوات",
            "اشهر",
            "أشهر",
            "شهر",
            "عام",
            "اعوام",
            "أعوام",
        ],

        "special": "retention",
    },

    {
        "name": "توضيح كيفية إتلاف أو حذف البيانات",
        "patterns": [
            "حذف البيانات",
            "حذفها",
            "حذف بياناتك",
            "يتم حذف البيانات",
            "يتم حذفها",
            "اتلاف البيانات",
            "إتلاف البيانات",
            "اتلافها",
            "إتلافها",
            "يتم اتلاف",
            "يتم إتلاف",
            "التخلص من البيانات",
            "التخلص من بياناتك",
            "بعد انتهاء الحاجة",
            "عند انتهاء الحاجة",
        ],
    },

    {
        "name": "توضيح حقوق صاحب البيانات",
        "patterns": [
            "حقوق صاحب البيانات",
            "حقوق أصحاب البيانات",
            "حقوق الافراد",
            "حقوق الأفراد",
            "حقوق المستخدم",
            "حقوق المستخدمين",
            "حقوقك",
            "حقك في الوصول",
            "الحق في الوصول",
            "الوصول الى بياناتك",
            "الوصول إلى بياناتك",
            "الوصول الى بياناته",
            "الوصول إلى بياناته",
            "تصحيح البيانات",
            "تصحيح بياناتك",
            "تصحيح بياناته",
            "تحديث البيانات",
            "تحديث بياناتك",
            "حذف بياناتك",
            "الاعتراض على المعالجة",
            "الاعتراض على معالجة",
            "سحب الموافقة",
            "طلب نسخة من البيانات",
            "نقل البيانات",
        ],
    },

    {
        "name": "توضيح طريقة ممارسة حقوق صاحب البيانات",
        "patterns": [
            "ممارسة حقوقك",
            "ممارسة حقوقه",
            "ممارسة حقوق صاحب البيانات",
            "يمكنك ممارسة حقوقك",
            "يمكن لصاحب البيانات ممارسة",
            "لتقديم طلب",
            "تقديم طلب لممارسة",
            "تقديم طلب لممارسة حقوقك",
            "من خلال التواصل معنا",
            "من خلال التواصل مع",
            "عبر البريد الالكتروني",
            "عبر البريد الإلكتروني",
            "من خلال صفحة التواصل",
            "صفحة التواصل",
            "وسائل التواصل",
            "مسؤول حماية البيانات",
            "مسؤول حماية البيانات الشخصية",
            "طلبات أصحاب البيانات",
            "طلبات صاحب البيانات",
        ],
    },

    {
        "name": "توضيح المسوغ النظامي لجمع أو معالجة البيانات",
        "patterns": [
            "المسوغ النظامي",
            "المسوغ القانوني",
            "الاساس النظامي",
            "الأساس النظامي",
            "الاساس القانوني",
            "الأساس القانوني",
            "الاساس النظامي للمعالجة",
            "الأساس النظامي للمعالجة",
            "الالتزام بالانظمة",
            "الالتزام بالأنظمة",
            "المتطلبات النظامية",
            "متطلبات نظامية",
            "وفقا للنظام",
            "وفقًا للنظام",
            "بموجب النظام",
            "بموجب الأنظمة",
            "بموجب الانظمة",
        ],
    },

    {
        "name": "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات",
        "patterns": [
            "الافصاح عن البيانات",
            "الإفصاح عن البيانات",
            "الافصاح عن بعض البيانات",
            "الإفصاح عن بعض البيانات",
            "قد يتم الافصاح",
            "قد يتم الإفصاح",
            "مشاركة البيانات",
            "مشاركة بعض البيانات",
            "قد تتم مشاركة",
            "قد يتم مشاركة",
            "مقدمي الخدمات",
            "مقدمي الخدمة",
            "مزودي الخدمات",
            "مزودي الخدمة",
            "الجهات الحكومية",
            "الجهات ذات العلاقة",
            "الجهات المختصة",
            "شركاء الخدمة",
            "اطراف اخرى",
            "أطراف أخرى",
            "أطراف ثالثة",
            "طرف ثالث",
            "البنوك",
            "بوابات الدفع",
            "مزودي الدفع",
            "مقدمي الدفع",
        ],

        "third_party_only": [
            "طرف ثالث",
            "أطراف ثالثة",
            "نماذج ذكاء اصطناعي من طرف ثالث",
            "خدمات من طرف ثالث",
        ],
    },

    {
        "name": "توضيح النقل أو المعالجة خارج المملكة",
        "patterns": [
            "خارج المملكة",
            "خارج المملكه",
            "نقل البيانات خارج",
            "نقل البيانات الى خارج",
            "نقل البيانات إلى خارج",
            "معالجة البيانات خارج",
            "معالجة خارج المملكة",
            "نقل او معالجة خارج",
            "نقل أو معالجة خارج",
            "نقل دولي للبيانات",
            "دول اخرى",
            "دول أخرى",
            "خارج السعودية",
        ],
    },
]


# =========================================================
# تحليل سياسة الخصوصية
# =========================================================

def analyze_privacy(text):

    results = []
    sentences = split_sentences(text)

    for rule in PRIVACY_RULES:

        name = rule["name"]
        patterns = rule["patterns"]

        if rule.get("special") == "retention":

            evidence = None

            for sentence in sentences:

                normalized = normalize_text(sentence)

                has_retention = any(
                    word in normalized
                    for word in [
                        "احتفاظ",
                        "نحتفظ",
                        "يتم الاحتفاظ",
                        "حفظ البيانات",
                    ]
                )

                has_duration = any(
                    word in normalized
                    for word in [
                        "مدة",
                        "فترة",
                        "لمدة",
                        "للمدة",
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
                        "حتى انتهاء",
                        "حتى تحقيق",
                        "للمدة اللازمة",
                    ]
                )

                if has_retention and has_duration:
                    evidence = sentence
                    break

            if evidence:

                results.append({
                    "name": name,
                    "status": "🟢",
                    "evidence": evidence,
                })

            else:

                results.append({
                    "name": name,
                    "status": "🔴",
                    "evidence": None,
                })

            continue

        matched_sentences = []

        for sentence in sentences:

            normalized_sentence = normalize_text(sentence)
            matched = []

            for pattern in patterns:

                normalized_pattern = normalize_text(pattern)

                if normalized_pattern in normalized_sentence:
                    matched.append(pattern)

            if matched:
                matched_sentences.append(
                    (sentence, matched)
                )

        if name == "توضيح طريقة جمع البيانات":

            strong_patterns = rule.get(
                "strong_patterns",
                []
            )

            strong_evidence = None

            for sentence in sentences:

                if sentence_has_patterns(
                    sentence,
                    strong_patterns
                ):

                    strong_evidence = sentence
                    break

            if strong_evidence:

                results.append({
                    "name": name,
                    "status": "🟢",
                    "evidence": strong_evidence,
                })

                continue

        if name == (
            "توضيح الجهات التي قد يتم الإفصاح "
            "لها عن البيانات"
        ):

            third_party_only = rule.get(
                "third_party_only",
                []
            )

            only_third_party = False

            for sentence in sentences:

                normalized = normalize_text(sentence)

                has_third_party = any(
                    normalize_text(x) in normalized
                    for x in third_party_only
                )

                has_data_context = any(
                    word in normalized
                    for word in [
                        "بيانات",
                        "معلومات",
                        "بياناتك",
                        "بيانات المستخدم",
                        "بيانات المستخدمين",
                    ]
                )

                has_sharing = any(
                    word in normalized
                    for word in [
                        "مشاركة",
                        "يفصح",
                        "الافصاح",
                        "الإفصاح",
                        "نشارك",
                        "تشارك",
                    ]
                )

                if (
                    has_third_party
                    and not (
                        has_data_context
                        and has_sharing
                    )
                ):

                    only_third_party = True

            if only_third_party:

                results.append({
                    "name": name,
                    "status": "🟡",
                    "evidence": (
                        matched_sentences[0][0]
                        if matched_sentences
                        else None
                    ),
                })

                continue

        unique_matches = set()

        for _, matches in matched_sentences:

            for match in matches:

                unique_matches.add(
                    normalize_text(match)
                )

        if matched_sentences:

            if len(unique_matches) >= 2:
                status = "🟢"
            else:
                status = "🟡"

            evidence = matched_sentences[0][0]

        else:

            status = "🔴"
            evidence = None

        results.append({
            "name": name,
            "status": status,
            "evidence": evidence,
        })

    return results


# =========================================================
# قواعد المتجر
# =========================================================

STORE_RULES = [

    {
        "name": "وجود سياسة الخصوصية",
        "patterns": [
            "سياسة الخصوصية",
            "سياسه الخصوصيه",
            "privacy policy",
            "privacy-policy",
        ],
    },

    {
        "name": "وجود سياسة الاستبدال والاسترجاع واسترداد الأموال",
        "patterns": [
            "سياسة الاستبدال والاسترجاع",
            "الاستبدال والاسترجاع",
            "الاسترجاع والاستبدال",
            "استرداد الأموال",
            "استرجاع المبلغ",
            "سياسة الاسترجاع",
            "سياسة الاستبدال",
            "سياسة الاسترداد",
            "الاسترداد",
            "refund",
            "returns",
        ],
    },

    {
        "name": "وجود سياسة الشحن والتوصيل",
        "patterns": [
            "سياسة الشحن",
            "الشحن والتوصيل",
            "الشحن",
            "التوصيل",
            "مواعيد التوصيل",
            "shipping",
            "delivery",
        ],
    },

    {
        "name": "وجود سياسة الشكاوى والمقترحات",
        "patterns": [
            "الشكاوى",
            "المقترحات",
            "تقديم شكوى",
            "تقديم الشكاوى",
            "خدمة العملاء",
            "complaints",
        ],
    },

    {
        "name": "وجود بيانات التواصل",
        "patterns": [
            "تواصل معنا",
            "اتصل بنا",
            "البريد الالكتروني",
            "البريد الإلكتروني",
            "رقم الهاتف",
            "رقم الجوال",
            "واتساب",
            "contact",
        ],
    },

    {
        "name": "وجود بيانات المنشأة أو السجل التجاري",
        "patterns": [
            "السجل التجاري",
            "رقم السجل التجاري",
            "رقم السجل",
            "سجل تجاري",
            "بيانات المنشأة",
            "اسم المنشأة",
            "المنشأة",
            "commercial registration",
        ],
    },

    {
        "name": "وجود الرقم الضريبي",
        "patterns": [
            "الرقم الضريبي",
            "رقم ضريبي",
            "ضريبة القيمة المضافة",
            "القيمة المضافة",
            "vat",
            "tax number",
        ],
    },
]


# =========================================================
# تحليل المتجر
# =========================================================

def analyze_store(text):

    results = []
    sentences = split_sentences(text)

    for rule in STORE_RULES:

        evidence = None

        for sentence in sentences:

            if sentence_has_patterns(
                sentence,
                rule["patterns"]
            ):

                evidence = sentence
                break

        if evidence:

            results.append({
                "name": rule["name"],
                "status": "🟢",
                "evidence": evidence,
            })

        else:

            results.append({
                "name": rule["name"],
                "status": "⚪",
                "evidence": None,
            })

    return results


# =========================================================
# جلب الصفحة
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


# =========================================================
# استخراج الصفحة
# =========================================================

def extract_page_data(html, base_url):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
        ]
    ):

        tag.decompose()

    text = soup.get_text(
        " ",
        strip=True
    )

    links = []

    for a in soup.find_all(
        "a",
        href=True
    ):

        label = a.get_text(
            " ",
            strip=True
        )

        href = urljoin(
            base_url,
            a["href"]
        )

        links.append({
            "label": label,
            "url": href,
        })

    return text, links


# =========================================================
# العثور على سياسة الخصوصية
# =========================================================

def find_privacy_page(links):

    keywords = [
        "سياسة الخصوصية",
        "سياسه الخصوصيه",
        "privacy policy",
        "privacy",
        "privacy-policy",
    ]

    for link in links:

        label = normalize_text(
            link["label"]
        )

        url = normalize_text(
            link["url"]
        )

        for keyword in keywords:

            normalized_keyword = normalize_text(
                keyword
            )

            if normalized_keyword in label:
                return link["url"]

            if normalized_keyword in url:
                return link["url"]

    return None


# =========================================================
# عرض النتائج
# =========================================================

def display_result(result):

    st.markdown(
        '<div class="result-box">',
        unsafe_allow_html=True
    )

    st.write(
        f"{result['status']} "
        f"{result['name']}"
    )

    if result.get("evidence"):

        with st.expander(
            "🔎 عرض الدليل"
        ):

            st.write(
                result["evidence"]
            )

    else:

        with st.expander(
            "🔎 لماذا ظهرت هذه النتيجة؟"
        ):

            st.write(
                "لم يعثر المحرك في النص المتاح "
                "على مؤشر كافٍ لهذا المتطلب."
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# الدرجات
# =========================================================

def privacy_score(results):

    if not results:
        return 0

    values = []

    for result in results:

        if result["status"] == "🟢":
            values.append(1)

        elif result["status"] == "🟡":
            values.append(0.5)

        else:
            values.append(0)

    return round(
        sum(values)
        / len(values)
        * 100
    )


def store_score(results):

    if not results:
        return 0

    values = []

    for result in results:

        if result["status"] == "🟢":
            values.append(1)

        else:
            values.append(0)

    return round(
        sum(values)
        / len(values)
        * 100
    )


# =========================================================
# رأس الصفحة
# =========================================================

st.markdown(
    """
    <div class="main-title">
        <h1>⚖️ ميثاق | Methaq</h1>
        <p>
            منصة ذكية للتدقيق والامتثال للأنظمة السعودية
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-box">
        <b>منصة ميثاق</b><br>
        تساعد المنشآت على إجراء فحص أولي لسياسات الخصوصية
        ومتطلبات المتجر، مع عرض الأدلة والعناصر التي تحتاج
        إلى مراجعة أو تحقق خارجي.
    </div>
    """,
    unsafe_allow_html=True
)

st.info(
    "نتائج ميثاق مؤشرات فحص أولية وليست "
    "حكمًا قانونيًا أو استشارة قانونية."
)


# =========================================================
# التبويبات
# =========================================================

tab1, tab2 = st.tabs(
    [
        "🔎 فحص متجر",
        "📄 فحص سياسة الخصوصية",
    ]
)


# =========================================================
# فحص المتجر
# =========================================================

with tab1:

    st.markdown(
        '<div class="section-title">🔎 فحص متجر</div>',
        unsafe_allow_html=True
    )

    store_url = st.text_input(
        "أدخل رابط المتجر",
        placeholder="https://example.com",
    )

    if st.button(
        "🚀 ابدأ الفحص",
        key="scan_store",
        use_container_width=True,
    ):

        if not store_url:

            st.warning(
                "أدخل رابط المتجر أولًا."
            )

        else:

            if not store_url.startswith("http"):

                store_url = (
                    "https://"
                    + store_url
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

                link_text = " ".join(
                    [
                        item["label"]
                        + " "
                        + item["url"]
                        for item in links
                    ]
                )

                store_results = analyze_store(
                    page_text
                    + " "
                    + link_text
                )

                store_score_value = store_score(
                    store_results
                )

                privacy_url = find_privacy_page(
                    links
                )

                privacy_results = []

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

                if privacy_results:

                    privacy_score_value = (
                        privacy_score(
                            privacy_results
                        )
                    )

                    overall_score = round(
                        (
                            store_score_value
                            + privacy_score_value
                        ) / 2
                    )

                else:

                    privacy_score_value = 0
                    overall_score = store_score_value

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "المؤشر العام",
                        f"{overall_score}%"
                    )

                with col2:

                    st.metric(
                        "فحص المتجر",
                        f"{store_score_value}%"
                    )

                with col3:

                    if privacy_results:

                        st.metric(
                            "فحص الخصوصية",
                            f"{privacy_score_value}%"
                        )

                    else:

                        st.metric(
                            "فحص الخصوصية",
                            "غير متاح"
                        )

                st.divider()

                st.markdown(
                    '<div class="section-title">نتائج فحص المتجر</div>',
                    unsafe_allow_html=True
                )

                for result in store_results:
                    display_result(result)

                st.divider()

                if privacy_results:

                    st.markdown(
                        '<div class="section-title">نتائج فحص الخصوصية</div>',
                        unsafe_allow_html=True
                    )

                    for result in privacy_results:
                        display_result(result)

                else:

                    st.warning(
                        "لم يتم العثور على صفحة "
                        "سياسة خصوصية واضحة."
                    )

                st.divider()

                st.markdown(
                    '<div class="section-title">🔵 عناصر تحتاج تحققًا خارجيًا</div>',
                    unsafe_allow_html=True
                )

                external_checks = [

                    "التحقق من صحة السجل التجاري",

                    "التحقق من الرقم الضريبي "
                    "عند انطباقه",

                    "التحقق من بيانات المنشأة "
                    "من مصدر رسمي",

                    "التحقق من أي تراخيص أو "
                    "متطلبات خاصة بنشاط المتجر",
                ]

                for item in external_checks:

                    st.write(
                        f"🔵 {item}"
                    )


# =========================================================
# فحص سياسة الخصوصية
# =========================================================

with tab2:

    st.markdown(
        '<div class="section-title">📄 فحص سياسة الخصوصية</div>',
        unsafe_allow_html=True
    )

    privacy_text = st.text_area(
        "الصق نص سياسة الخصوصية هنا",
        height=350,
        placeholder="الصق سياسة الخصوصية هنا...",
    )

    if st.button(
        "🔍 فحص السياسة",
        key="scan_privacy",
        use_container_width=True,
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

            clear_count = sum(
                1
                for result in results
                if result["status"] == "🟢"
            )

            review_count = sum(
                1
                for result in results
                if result["status"] == "🟡"
            )

            missing_count = sum(
                1
                for result in results
                if result["status"] == "🔴"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "المؤشر",
                    f"{score}%"
                )

            with col2:

                st.metric(
                    "مؤشرات واضحة",
                    clear_count
                )

            with col3:

                st.metric(
                    "تحتاج مراجعة",
                    review_count
                )

            with col4:

                st.metric(
                    "لم يتم العثور عليها",
                    missing_count
                )

            st.divider()

            for result in results:
                display_result(result)


# =========================================================
# التذييل
# =========================================================

st.markdown(
    """
    <div class="footer-note">
        ⚖️ ميثاق | Methaq — نموذج أولي تجريبي
        <br>
        النتائج لأغراض الفحص الأولي ولا تُعد استشارة قانونية.
    </div>
    """,
    unsafe_allow_html=True
)
