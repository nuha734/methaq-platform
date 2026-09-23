import streamlit as st

st.set_page_config(
    page_title="ميثاق | Methaq",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ ميثاق")
st.subheader("المنصة الذكية للتدقيق والامتثال للأنظمة السعودية")

st.write(
    "حل رقمي يساعد المنشآت على فحص سياساتها واكتشاف "
    "الثغرات النظامية بطريقة مبسطة وسريعة."
)

st.divider()

st.header("ابدأ فحص الامتثال")

input_type = st.radio(
    "اختر طريقة الفحص:",
    ["رابط المتجر", "نص سياسة الخصوصية"]
)

if input_type == "رابط المتجر":
    store_url = st.text_input(
        "أدخل رابط متجرك الإلكتروني",
        placeholder="https://example.com"
    )
else:
    policy_text = st.text_area(
        "الصق سياسة الخصوصية هنا",
        height=200,
        placeholder="الصق نص سياسة الخصوصية..."
    )

if st.button("🔍 ابدأ التدقيق", use_container_width=True):
    st.info("سيتم تحليل المحتوى ومطابقته مع المتطلبات النظامية.")
