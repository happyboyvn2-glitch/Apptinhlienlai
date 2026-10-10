import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math

# Page config
st.set_page_config(
    page_title="Tính Lãi Tiết Kiệm Ngân Hàng | Fintech Mini App",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional bank-like look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0a2540 0%, #1a5276 50%, #1abc9c 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(10, 37, 64, 0.25);
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        font-size: 1.05rem;
        opacity: 0.92;
        margin-top: 0.5rem;
    }
    
    .metric-card {
        background: white;
        border: 1px solid #e8eef3;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        text-align: center;
        height: 100%;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0a2540;
        margin: 0.3rem 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .interest-highlight {
        color: #16a34a !important;
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #0a2540;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1abc9c;
        display: inline-block;
    }
    
    .info-box {
        background: #f0f9ff;
        border-left: 4px solid #0ea5e9;
        padding: 1rem 1.25rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
        font-size: 0.95rem;
        color: #0c4a6e;
    }
    
    .warning-box {
        background: #fefce8;
        border-left: 4px solid #eab308;
        padding: 1rem 1.25rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #713f12;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #0a2540, #1a5276);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.8rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1a5276, #1abc9c);
        box-shadow: 0 6px 16px rgba(26, 82, 118, 0.3);
    }
    
    .sidebar .stSelectbox, .sidebar .stNumberInput, .sidebar .stRadio {
        margin-bottom: 0.8rem;
    }
    
    div[data-testid="stSidebar"] {
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 2rem;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Chat styling */
    .stChatMessage {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>💰 Tính Lãi Tiết Kiệm Ngân Hàng</h1>
    <p>Công cụ Fintech giúp bạn tính toán chính xác tiền lãi cuối kỳ – Đơn giản • Minh bạch • Tin cậy</p>
</div>
""", unsafe_allow_html=True)

# Sidebar inputs
with st.sidebar:
    st.markdown("### ⚙️ Thông số gửi tiết kiệm")
    st.markdown("---")
    
    principal = st.number_input(
        "Số tiền gửi (VND)",
        min_value=1_000_000,
        max_value=10_000_000_000,
        value=100_000_000,
        step=1_000_000,
        format="%d",
        help="Số tiền bạn muốn gửi tiết kiệm"
    )
    
    term_months = st.selectbox(
        "Kỳ hạn gửi",
        options=[1, 2, 3, 6, 9, 12, 18, 24, 36],
        index=5,
        format_func=lambda x: f"{x} tháng",
        help="Thời gian gửi tiền"
    )
    
    interest_rate = st.number_input(
        "Lãi suất (%/năm)",
        min_value=0.1,
        max_value=15.0,
        value=5.5,
        step=0.1,
        format="%.2f",
        help="Lãi suất niêm yết của ngân hàng"
    )
    
    interest_type = st.radio(
        "Loại lãi",
        options=["Lãi đơn (Simple)", "Lãi kép (Compound)"],
        index=1,
        help="Lãi đơn: chỉ tính trên gốc. Lãi kép: lãi sinh lãi."
    )
    
    compounding = "Hàng năm"
    if "kép" in interest_type:
        compounding = st.selectbox(
            "Tần suất ghép lãi",
            options=["Hàng tháng", "Hàng quý", "Hàng năm"],
            index=0,
            help="Số lần lãi được cộng vào gốc trong năm"
        )
    
    st.markdown("---")
    calculate = st.button("🚀 Tính toán ngay", use_container_width=True)
    
    st.markdown("""
    <div class="info-box" style="font-size:0.8rem; margin-top:1.5rem;">
        <strong>📌 Lưu ý:</strong><br>
        • Kết quả mang tính tham khảo.<br>
        • Lãi suất thực tế có thể thay đổi theo chính sách ngân hàng.<br>
        • Nên đối chiếu với bảng lãi suất chính thức.
    </div>
    """, unsafe_allow_html=True)

# Calculation functions
def calculate_simple_interest(P, r, t_years):
    """Lãi đơn: I = P * r * t"""
    interest = P * (r / 100) * t_years
    total = P + interest
    return interest, total

def calculate_compound_interest(P, r, t_years, n):
    """Lãi kép: A = P * (1 + r/n)^(n*t)"""
    rate = r / 100
    amount = P * (1 + rate / n) ** (n * t_years)
    interest = amount - P
    return interest, amount

# Main content
col1, col2 = st.columns([1.1, 0.9])

with col1:
    st.markdown('<div class="section-title">📊 Kết quả tính toán</div>', unsafe_allow_html=True)
    
    t_years = term_months / 12.0
    n_map = {"Hàng tháng": 12, "Hàng quý": 4, "Hàng năm": 1}
    
    if calculate or True:  # Always show for demo feel
        if "đơn" in interest_type:
            interest, total = calculate_simple_interest(principal, interest_rate, t_years)
            formula_text = f"I = P × r × t = {principal:,.0f} × {interest_rate/100:.4f} × {t_years:.2f}"
        else:
            n = n_map.get(compounding, 12)
            interest, total = calculate_compound_interest(principal, interest_rate, t_years, n)
            formula_text = f"A = P × (1 + r/n)^(n×t)"
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Số tiền gửi</div>
                <div class="metric-value">{principal:,.0f} ₫</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Tiền lãi nhận được</div>
                <div class="metric-value interest-highlight">+{interest:,.0f} ₫</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Tổng nhận cuối kỳ</div>
                <div class="metric-value" style="color:#0ea5e9;">{total:,.0f} ₫</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Summary table
        summary_data = {
            "Hạng mục": ["Số tiền gốc", "Kỳ hạn", "Lãi suất", "Loại lãi", "Tiền lãi", "Tổng cuối kỳ"],
            "Chi tiết": [
                f"{principal:,.0f} VND",
                f"{term_months} tháng ({t_years:.2f} năm)",
                f"{interest_rate:.2f}% / năm",
                interest_type + (f" ({compounding})" if "kép" in interest_type else ""),
                f"{interest:,.0f} VND",
                f"{total:,.0f} VND"
            ]
        }
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
        
        # Growth chart for compound or multi-period
        st.markdown('<div class="section-title">📈 Biểu đồ tăng trưởng</div>', unsafe_allow_html=True)
        
        periods = list(range(0, term_months + 1))
        balances = []
        for m in periods:
            ty = m / 12.0
            if "đơn" in interest_type:
                _, bal = calculate_simple_interest(principal, interest_rate, ty)
            else:
                n = n_map.get(compounding, 12)
                _, bal = calculate_compound_interest(principal, interest_rate, ty, n)
            balances.append(bal)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=periods, y=balances,
            mode='lines+markers',
            name='Số dư',
            line=dict(color='#1abc9c', width=3),
            marker=dict(size=6, color='#0a2540'),
            fill='tozeroy',
            fillcolor='rgba(26, 188, 156, 0.15)'
        ))
        fig.update_layout(
            title=dict(text="Sự tăng trưởng số dư theo thời gian", font=dict(size=16, color='#0a2540')),
            xaxis_title="Tháng",
            yaxis_title="Số dư (VND)",
            template="plotly_white",
            height=380,
            margin=dict(l=40, r=40, t=50, b=40),
            hovermode="x unified"
        )
        fig.update_yaxes(tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">🤖 Trợ lý tư vấn tiết kiệm</div>', unsafe_allow_html=True)
    
    # Chatbot
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Xin chào! Tôi là trợ lý Fintech của bạn. Bạn có thể hỏi tôi về:\n- Lãi đơn vs lãi kép\n- Cách chọn kỳ hạn phù hợp\n- Lời khuyên gửi tiết kiệm\n- So sánh các sản phẩm\nHãy hỏi bất kỳ điều gì!"}
        ]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Simple rule-based + keyword chatbot
    def get_bot_response(user_input):
        q = user_input.lower().strip()
        
        if any(k in q for k in ["lãi đơn", "simple", "lãi kép", "compound", "khác nhau"]):
            return """**Lãi đơn (Simple Interest):**  
Chỉ tính lãi trên số tiền gốc ban đầu. Công thức: **I = P × r × t**  

**Lãi kép (Compound Interest):**  
Lãi được cộng vào gốc và tiếp tục sinh lãi. Công thức: **A = P × (1 + r/n)^(n×t)**  

💡 *Lời khuyên:* Với kỳ hạn dài (>12 tháng), lãi kép mang lại lợi ích rõ rệt hơn. Nhiều ngân hàng Việt Nam áp dụng lãi kép theo tháng hoặc quý."""
        
        elif any(k in q for k in ["kỳ hạn", "thời gian", "bao lâu", "chọn kỳ"]):
            return """**Gợi ý chọn kỳ hạn:**  
• **1–3 tháng**: Linh hoạt, lãi suất thấp hơn, phù hợp nhu cầu rút vốn ngắn hạn.  
• **6–12 tháng**: Cân bằng tốt giữa lãi suất và thanh khoản.  
• **18–36 tháng**: Lãi suất cao nhất, phù hợp mục tiêu dài hạn (mua nhà, học tập…).  

⚠️ Lưu ý: Rút trước hạn thường bị áp dụng lãi suất không kỳ hạn (rất thấp)."""
        
        elif any(k in q for k in ["lời khuyên", "nên", "tư vấn", "làm sao"]):
            return f"""**Lời khuyên dành cho bạn:**  
1. So sánh lãi suất giữa các ngân hàng (Vietcombank, Techcombank, MB, VPBank…).  
2. Ưu tiên kỳ hạn phù hợp kế hoạch tài chính, tránh rút sớm.  
3. Với số tiền {principal:,.0f} VND, lãi kép {term_months} tháng có thể mang lại khoảng **{interest:,.0f} VND**.  
4. Cân nhắc phân bổ: một phần gửi ngắn hạn (thanh khoản), một phần dài hạn (tối ưu lãi).  
5. Theo dõi chính sách lãi suất thay đổi theo quý."""
        
        elif any(k in q for k in ["an toàn", "rủi ro", "bảo hiểm", "tin tưởng"]):
            return """**An toàn tiền gửi tại Việt Nam:**  
• Tiền gửi tiết kiệm được Bảo hiểm tiền gửi Việt Nam bảo vệ (mức bảo hiểm hiện hành theo quy định).  
• Chọn ngân hàng có uy tín, xếp hạng tín nhiệm tốt.  
• App này chỉ hỗ trợ tính toán – không thu thập hay lưu trữ dữ liệu cá nhân của bạn.  
• Kết quả mang tính tham khảo, luôn đối chiếu với hợp đồng ngân hàng."""
        
        elif any(k in q for k in ["cảm ơn", "thanks", "ok", "được"]):
            return "Rất vui được hỗ trợ bạn! Nếu cần tính lại hoặc hỏi thêm, cứ nhắn nhé. Chúc bạn đầu tư tiết kiệm hiệu quả! 💰"
        
        else:
            return """Tôi có thể giúp bạn hiểu rõ hơn về:  
• Sự khác biệt lãi đơn & lãi kép  
• Cách chọn kỳ hạn tối ưu  
• Lời khuyên gửi tiết kiệm thực tế  
• Mức độ an toàn của tiền gửi  

Bạn hãy hỏi cụ thể hơn nhé!"""
    
    if prompt := st.chat_input("Hỏi trợ lý về tiết kiệm..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        response = get_bot_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

# Additional educational section
st.markdown("---")
st.markdown('<div class="section-title">📚 Kiến thức Fintech: Lãi suất tiết kiệm</div>', unsafe_allow_html=True)

edu1, edu2 = st.columns(2)
with edu1:
    st.markdown("""
    <div class="info-box">
        <strong>Công thức Lãi đơn</strong><br>
        I = P × r × t<br>
        Trong đó: P = gốc, r = lãi suất năm, t = số năm
    </div>
    """, unsafe_allow_html=True)
with edu2:
    st.markdown("""
    <div class="info-box">
        <strong>Công thức Lãi kép</strong><br>
        A = P × (1 + r/n)<sup>n×t</sup><br>
        n = số lần ghép lãi trong năm
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="warning-box">
    <strong>⚠️ Tuyên bố miễn trừ trách nhiệm:</strong> Ứng dụng này được phát triển cho mục đích học tập và thuyết trình môn Công nghệ Tài chính. 
    Kết quả tính toán chỉ mang tính tham khảo. Vui lòng kiểm tra lãi suất và điều kiện chính thức tại ngân hàng trước khi quyết định gửi tiền.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <strong>Fintech Mini App – Tính Lãi Tiết Kiệm</strong><br>
    Phát triển cho môn học Công nghệ Tài chính | TS. Vũ Đức Bình<br>
    © 2026 | Thiết kế chuyên nghiệp • Dễ sử dụng • Minh bạch
</div>
""", unsafe_allow_html=True)
