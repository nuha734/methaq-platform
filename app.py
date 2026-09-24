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


# =========================
# أدوات معالجة النص
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

    # إزالة التشكيل
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)

    # توحيد المسافات
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def split_sentences(text):
    return [
        s.strip()
        for s in re.split(r"[.!؟؛\n]+", text)
        if s.strip()
    ]


def contains_any(text, patterns):
    return any(pattern in text for pattern in patterns)


def find_evidence(text, patterns):
    sentences = split_sentences(text)

    for sentence in sentences:
        normalized_sentence = normalize_text(sentence)

        if contains_any(normalized_sentence, patterns):
            return sentence

    return None


# =========================
# قواعد فحص الخصوصية
# =========================

PRIVACY_RULES = [

    {
        "name": "تحديد البيانات الشخصية التي يتم جمعها",
        "patterns": [
            "البيانات الشخصية",
            "بيانات العملاء",
            "الاسم",
            "رقم الجوال",
            "رقم الهاتف",
            "البريد الالكتروني",
            "عنوان التوصيل",
            "بيانات الطلب",
        ],
    },

    {
        "name": "توضيح الغرض من جمع البيانات",
        "patterns": [
            "نستخدم البيانات",
            "استخدام البيانات",
            "الغرض من جمع",
            "لغرض",
            "تنفيذ الطلبات",
            "تقديم الخدمات",
            "تحسين الخدمات",
            "تحسين تجربة المستخدم",
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
            "يتم جمع",
            "نجمع",
            "تسجيل المستخدم",
            "النماذج الالكترونية",
            "عمليات الشراء",
            "التواصل مع خدمة العملاء",
        ],
    },

    {
        "name": "توضيح كيفية معالجة البيانات",
        "patterns": [
            "معالجة البيانات",
            "معالجه البيانات",
            "تتم معالجة",
            "كيفية معالجة",
            "أغراض المعالجة",
            "معالجة البيانات الشخصية",
        ],
    },

    {
        "name": "توضيح وسيلة حفظ وتخزين البيانات",
        "patterns": [
            "حفظ البيانات",
            "تخزين البيانات",
            "يتم حفظ",
            "يتم تخزين",
            "قاعدة البيانات",
            "النسخ الاحتياطية",
            "أنظمة الكترونية آمنة",
        ],
    },

    # ==================================================
    # مهم:
    # مدة الاحتفاظ لا تعتمد على كلمة "نحتفظ" وحدها.
    # يجب وجود مدة أو فترة أو شرط زمني واضح.
    # ==================================================
    {
        "name": "توضيح مدة الاحتفاظ بالبيانات",
        "patterns": [
            "مدة الاحتفاظ",
            "فترة الاحتفاظ",
            "المدة اللازمة للاحتفاظ",
            "للمدة اللازمة",
            "نحتفظ بالبيانات لمدة",
            "نحتفظ بالبيانات للمدة",
            "يتم الاحتفاظ بالبيانات لمدة",
            "يتم الاحتفاظ بالبيانات للمدة",
            "حتى انتهاء الغرض",
            "حتى انتهاء الحاجة",
            "لفترة محددة",
            "لفترة زمنية",
            "عدد سنوات",
            "سنوات",
            "اشهر",
            "أشهر",
            "سنة",
            "عام",
            "عامين",
            "ثلاث سنوات",
            "خمس سنوات",
        ],
    },

    {
        "name": "توضيح كيفية إتلاف أو حذف البيانات",
        "patterns": [
            "حذف البيانات",
            "حذفها",
            "يتم حذف",
            "اتلاف البيانات",
            "إتلاف البيانات",
            "اتلافها",
            "إتلافها",
            "يتم اتلاف",
            "يتم إتلاف",
            "التخلص من البيانات",
            "انتهاء الحاجة إلى البيانات",
        ],
    },

    {
        "name": "توضيح حقوق صاحب البيانات",
        "patterns": [
            "حقوق صاحب البيانات",
            "حقوق الافراد",
            "حقوق المستخدم",
            "الوصول الى بياناته",
            "الوصول إلى بياناته",
            "تصحيح بياناته",
            "تحديث بياناته",
            "حذف بياناته",
            "الاعتراض على المعالجة",
            "الاعتراض على بعض أوجه المعالجة",
        ],
    },

    {
        "name": "توضيح طريقة ممارسة حقوق صاحب البيانات",
        "patterns": [
            "ممارسة حقوقه",
            "ممارسة حقوق صاحب البيانات",
            "يمكنه ممارسة حقوقه",
            "يمكن لصاحب البيانات ممارسة",
            "من خلال التواصل",
            "التواصل مع المتجر",
            "التواصل معنا",
            "عبر البريد الالكتروني",
            "عبر البريد الإلكتروني",
            "وسائل التواصل",
            "تقديم طلب",
            "تقديم طلب لممارسة",
        ],
    },

    {
        "name": "توضيح المسوغ النظامي لجمع أو معالجة البيانات",
        "patterns": [
            "المسوغ النظامي",
            "الاساس النظامي",
            "الأساس النظامي",
            "المسوغ القانوني",
            "الاساس القانوني",
            "الأساس القانوني",
            "الالتزام بالانظمة",
            "الالتزام بالأنظمة",
            "متطلبات نظامية",
            "المتطلبات النظامية",
            "وفق النظام",
            "وفقا للنظام",
            "وفقًا للنظام",
        ],
    },

    {
        "name": "توضيح الجهات التي قد يتم الإفصاح لها عن البيانات",
        "patterns": [
            "الافصاح عن البيانات",
            "الإفصاح عن البيانات",
            "الافصاح عن بعض البيانات",
            "الإفصاح عن بعض البيانات",
            "مشاركة البيانات",
            "مشاركة بعض البيانات",
            "قد يتم مشاركة",
            "قد يتم الافصاح",
            "قد يتم الإفصاح",
            "مقدمي الخدمات",
            "مقدمي الخدمة",
            "الجهات ذات العلاقة",
            "الجهات الحكومية",
            "شركاء الخدمة",
            "أطراف اخرى",
            "أطراف أخرى",
        ],
    },

    {
        "name": "توضيح النقل أو المعالجة خارج المملكة",
        "patterns": [
            "خارج المملكة",
            "خارج المملكه",
            "نقل البيانات خارج",
            "نقل أو معالجة خارج",
            "نقل البيانات الى خارج",
            "نقل البيانات إلى خارج",
            "معالجة البيانات خارج",
            "معالجة خارج المملكة",
            "نقل دولي للبيانات",
        ],
    },
]


# =========================
# تحليل الخصوصية
# =========================

def analyze_privacy(text):

    normalized_full_text = normalize_text(text)

    results = []

    for rule in PRIVACY_RULES:

        patterns = [normalize_text(p) for p in rule["patterns"]]

        matched_sentences = []

        for sentence in split_sentences(text):

            normalized_sentence = normalize_text(sentence)

            matches = [
                pattern
                for pattern in patterns
                if pattern in normalized_sentence
            ]

            if matches:
                matched_sentences.append(sentence)

        # عدد الأنماط المختلفة التي ظهرت في نفس النص
        full_matches = [
            pattern
            for pattern in patterns
            if pattern in normalized_full_text
        ]

        unique_full_matches = set(full_matches)

        # ==========================================
        # قاعدة خاصة لمدة الاحتفاظ:
        # لا نعتبر كلمة "نحتفظ" وحدها دليلاً.
        # ==========================================
        if rule["name"] == "توضيح مدة الاحتفاظ بالبيانات":

            duration_patterns = [
                "مدة الاحتفاظ",
                "فترة الاحتفاظ",
                "للمدة اللازمة",
                "المدة اللازمة",
                "نحتفظ بالبيانات لمدة",
                "نحتفظ بالبيانات للمدة",
                "يتم الاحتفاظ بالبيانات لمدة",
                "يتم الاحتفاظ بالبيانات للمدة",
                "حتى انتهاء الغرض",
                "حتى انتهاء الحاجة",
                "لفترة محددة",
                "لفترة زمنية",
                "عدد سنوات",
                "سنوات",
                "اشهر",
                "أشهر",
                "سنة",
                "عام",
                "عامين",
                "ثلاث سنوات",
                "خمس سنوات",
            ]

            duration_matches = [
                p for p in duration_patterns
                if normalize_text(p) in normalized_full_text
            ]

            # إذا لم توجد أي إشارة زمنية حقيقية
            if not duration_matches:
                results.append({
                    "name": rule["name"],
                    "status": "🟡",
                    "evidence": None,
                })
                continue

        # ==========================================
        # القاعدة العامة
        # ==========================================

        if matched_sentences and len(unique_full_matches) >= 2:
            status = "🟢"

        elif matched_sentences:
            status = "🟡"

        elif len(unique_full_matches) >= 2:
            status = "🟢"

        elif len(unique_full_matches) == 1:
            status = "🟡"

        else:
            status = "🔴"

        evidence = matched_sentences[0] if matched_sentences else None

        results.append({
            "name": rule["name"],
            "status": status,
            "evidence": evidence,
        })

    return results


# =========================
# فحص المتجر
# =========================

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
            "الاستبدال والاسترجاع",
            "الاستبدال والاسترجاع واسترداد الأموال",
            "الاسترجاع والاستبدال",
            "استرداد الأموال",
            "استرجاع المبلغ",
            "سياسة الاسترجاع",
            "سياسة الاستبدال",
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


def analyze_store(text):

    normalized_text = normalize_text(text)

    results = []

    for rule in STORE_RULES:

        matched_pattern = None

        for pattern in rule["patterns"]:

            normalized_pattern = normalize_text(pattern)

            if normalized_pattern in normalized_text:
                matched_pattern = pattern
                break

        if matched_pattern:

            evidence = find_evidence(
                text,
                [matched_pattern]
            )

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
# استخراج النص والروابط
# =========================

def extract_page_data(html, base_url):

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(
        ["script", "style", "noscript", "svg"]
    ):
        tag.decompose()

    text = soup.get_text(" ", strip=True)

    links = []

    for a in soup.find_all("a", href=True):

        label = a.get_text(" ", strip=True)

        href = urljoin(
            base_url,
            a["href"]
        )

        links.append({
            "label": label,
            "url": href
        })

    return text, links


# =========================
# العثور على سياسة الخصوصية
# =========================

def find_privacy_page(links):

    keywords = [
        "سياسة الخصوصية",
        "سياسه الخصوصيه",
        "privacy policy",
        "privacy",
        "privacy-policy",
    ]

    for link in links:

        label = normalize_text(link["label"])
        url = normalize_text(link["url"])

        for keyword in keywords:

            if normalize_text(keyword) in label:
                return link["url"]

            if normalize_text(keyword) in url:
                return link["url"]

    return None


# =========================
# الأدلة والنتائج
# =========================

def display_result(result):

    st.write(
        f"{result['status']}  "
        f"{result['name']}"
    )

    if result.get("evidence"):

        with st.expander("🔎 عرض الدليل"):

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


# =========================
# حساب الدرجات
# =========================

def privacy_score(results):

    values = []

    for result in results:

        if result["status"] == "🟢":
            values.append(1)

        elif result["status"] == "🟡":
            values.append(0.5)

        else:
            values.append(0)

    if not values:
        return 0

    return round(
        sum(values) / len(values) * 100
    )


def store_score(results):

    values = []

    for result in results:

        if result["status"] == "🟢":
            values.append(1)

        else:
            values.append(0)

    if not values:
        return 0

    return round(
        sum(values) / len(values) * 100
    )


# =========================
# واجهة ميثاق
# =========================

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="wide",
)


st.title("⚖️ ميثاق | Methaq")

st.caption(
    "منصة ذكية للتدقيق والامتثال للأنظمة السعودية"
)


st.info(
    "نتائج ميثاق مؤشرات فحص أولية وليست "
    "حكمًا قانونيًا أو استشارة قانونية."
)


tab1, tab2 = st.tabs([
    "🔎 فحص متجر",
    "📄 فحص سياسة الخصوصية",
])


# ==================================================
# فحص المتجر
# ==================================================

with tab1:

    st.subheader("🔎 فحص متجر")

    store_url = st.text_input(
        "أدخل رابط المتجر",
        placeholder="https://example.com"
    )

    if st.button(
        "ابدأ الفحص",
        key="scan_store"
    ):

        if not store_url:

            st.warning(
                "أدخل رابط المتجر أولًا."
            )

        else:

            if not store_url.startswith("http"):

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

                # روابط الصفحات
                link_text = " ".join(
                    [
                        f"{x['label']} {x['url']}"
                        for x in links
                    ]
                )

                store_results = analyze_store(
                    page_text + " " + link_text
                )

                store_score_value = (
                    store_score(
                        store_results
                    )
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

                    overall_score = (
                        store_score_value
                    )

                # النتائج الرئيسية

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
                    st.metric(
                        "فحص الخصوصية",
                        (
                            f"{privacy_score_value}%"
                            if privacy_results
                            else "غير متاح"
                        )
                    )

                st.divider()

                st.subheader(
                    "نتائج فحص المتجر"
                )

                for result in store_results:
                    display_result(result)

                st.divider()

                if privacy_results:

                    st.subheader(
                        "نتائج فحص الخصوصية"
                    )

                    for result in privacy_results:
                        display_result(result)

                else:

                    st.warning(
                        "لم يتم العثور على صفحة "
                        "سياسة خصوصية واضحة."
                    )

                st.divider()

                st.subheader(
                    "🔵 عناصر تحتاج تحققًا خارجيًا"
                )

                external_checks = [
                    "التحقق من صحة السجل التجاري",
                    "التحقق من الرقم الضريبي عند انطباقه",
                    "التحقق من بيانات المنشأة من مصدر رسمي",
                    "التحقق من أي تراخيص أو متطلبات خاصة بنشاط المتجر",
                ]

                for item in external_checks:

                    st.write(
                        f"🔵 {item}"
                    )


# ==================================================
# فحص سياسة الخصوصية يدويًا
# ==================================================

with tab2:

    st.subheader(
        "📄 فحص سياسة الخصوصية"
    )

    privacy_text = st.text_area(
        "الصق نص سياسة الخصوصية هنا",
        height=350,
        placeholder="الصق سياسة الخصوصية..."
    )

    if st.button(
        "فحص السياسة",
        key="scan_privacy"
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
