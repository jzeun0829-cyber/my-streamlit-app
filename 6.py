import streamlit as st
import pandas as pd
from PIL import Image
import plotly.graph_objects as go

# CSS 스타일
st.markdown("""
<style>
.reward-badge { display:inline-block; background:#FF4B4B; color:white !important;
font-weight:700; padding:5px 12px; border-radius:20px; margin-right:12px;
font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
box-shadow:0 0 10px #FF6B6B88; vertical-align:middle; font-size:0.9em; letter-spacing:1.5px;}
.benefit-title { display:inline-block; background:linear-gradient(90deg, #667eea, #764ba2);
color:white !important; padding:8px 15px; border-radius:8px; font-weight:700; font-size:1.3em;
margin-bottom:10px; box-shadow:0 4px 12px rgba(102, 126, 234, 0.4);
font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; vertical-align:middle; border:2px dotted #a3b1ff;}
.benefit-box { background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color:white !important; padding:15px 20px; margin-bottom:20px; border-radius:12px;
box-shadow:0 8px 24px rgba(102, 126, 234, 0.3); font-weight:600;
font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
.benefit-box li { margin-bottom:10px; line-height:1.4;}
.detail-list { padding-left:1.2rem; color:white !important; font-size:0.95rem; line-height:1.5;}
.total-sales-highlight {
  font-size: 48px;
  font-weight: bold;
  color: #4B8BF4;
  margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

DATA_PATH = r"C:\Users\LG\OneDrive\Desktop\archive\olist\seller_summary_with_trust_score.csv"
seller_summary = pd.read_csv(DATA_PATH)
seller_summary["seller_num"] = range(1, len(seller_summary) + 1)

q90 = seller_summary["trust_score"].dropna().quantile(0.9)
q70 = seller_summary["trust_score"].dropna().quantile(0.7)
q30 = seller_summary["trust_score"].dropna().quantile(0.3)

top10_group = seller_summary[seller_summary["trust_score"] >= q90]
top10_avg = top10_group[["total_sales", "avg_growth_rate", "repurchase_rate", "avg_review_score", "delay_rate"]].mean().fillna(0)

explanations_simple = {
    "total_sales": "총매출",
    "avg_growth_rate": "매출 성장률",
    "repurchase_rate": "재구매율",
    "avg_review_score": "리뷰 점수",
    "delay_rate": "배송 지연율"
}
explanations_detail = {
    "total_sales": "총매출 : 판매자의 전체 매출 규모",
    "avg_growth_rate": "매출 성장률 : 최근 매출 증가율 (높을수록 성장성 큼)",
    "repurchase_rate": "재구매율 : 동일 고객의 반복 구매 비율 (충성 고객 지표)",
    "avg_review_score": "리뷰 점수 : 고객 평균 리뷰 점수 (품질·만족도 반영)",
    "delay_rate": "배송 지연율 : 배송 지연 비율 (낮을수록 신뢰도 높음)"
}

grade_benefits = {
    "Platinum": ["플랫폼 수수료 할인", "우수 판매자 배지(검색 상위 노출, 신뢰 마크)", "Olist 공식 프로모션 참여 기회 제공"],
    "Gold": ["광고비 지원 크레딧 지급", "리뷰 관리 툴 무료 제공"],
    "Silver": ["개선 리포트 제공 (개선 포인트 피드백)", "성장률 좋은 판매자 사례 공유"],
    "Bronze": ["개선 프로그램 필수 참여 (물류/고객응대 교육)", "성과 개선 시 인센티브 지급"]
}

def display_grade_benefits(grade):
    benefits = grade_benefits.get(grade, [])
    if benefits:
        st.markdown(
            f"<div><span class='reward-badge'>👑 REWARD</span><span class='benefit-title'>{grade} 등급 혜택</span></div>",
            unsafe_allow_html=True,
        )
        benefits_html = "<ul class='benefit-box'>"
        for b in benefits:
            benefits_html += f"<li>{b}</li>"
        benefits_html += "</ul>"
        st.markdown(benefits_html, unsafe_allow_html=True)

def get_grade(score):
    if score >= q90:
        return "Platinum"
    elif score >= q70:
        return "Gold"
    elif score >= q30:
        return "Silver"
    else:
        return "Bronze"

def evaluate_columns(row, grade):
    results = {}
    for col, desc in explanations_detail.items():
        seller_val = round(row[col] if pd.notna(row[col]) else 0, 3)
        top10_val = round(top10_avg[col] if pd.notna(top10_avg[col]) else 0, 3)
        if grade == "Platinum":
            result = f"(내 점수: {seller_val}, 상위 10% 평균: {top10_val}) → 양호"
        else:
            if col == "delay_rate":
                if seller_val > top10_val:
                    result = f"(내 점수: {seller_val}, 상위 10% 평균: {top10_val}) → 개선 필요"
                else:
                    result = f"(내 점수: {seller_val}, 상위 10% 평균: {top10_val}) → 양호"
            else:
                if seller_val < top10_val:
                    result = f"(내 점수: {seller_val}, 상위 10% 평균: {top10_val}) → 개선 필요"
                else:
                    result = f"(내 점수: {seller_val}, 상위 10% 평균: {top10_val}) → 양호"
        results[desc] = result
    return results

def get_seller_report_by_id(seller_id, df):
    if seller_id not in df["seller_id"].values:
        return None
    row = df[df["seller_id"] == seller_id].iloc[0]
    grade = get_grade(row["trust_score"])
    results = evaluate_columns(row, grade)
    return {
        "seller_id": row["seller_id"],
        "총매출": round(row["total_sales"], 1),
        "신뢰도 점수": round(row["trust_score"], 4),
        "등급": grade,
        "항목별 결과": results,
        "row": row,
    }

def get_seller_report_by_num(seller_num, df):
    if seller_num not in df["seller_num"].values:
        return None
    row = df[df["seller_num"] == seller_num].iloc[0]
    grade = get_grade(row["trust_score"])
    results = evaluate_columns(row, grade)
    return {
        "seller_num": row["seller_num"],
        "seller_id": row["seller_id"],
        "총매출": round(row["total_sales"], 1),
        "신뢰도 점수": round(row["trust_score"], 4),
        "등급": grade,
        "항목별 결과": results,
        "row": row,
    }

def plot_seller_scores_plotly(report, top10_avg):
    metrics = ["avg_growth_rate", "repurchase_rate", "avg_review_score", "delay_rate"]
    labels = [explanations_simple[m] for m in metrics]
    seller_scores = []
    avg_scores = []

    for col in metrics:
        if explanations_detail[col] in report["항목별 결과"]:
            val_str = report["항목별 결과"][explanations_detail[col]]
            seller_val = float(val_str.split("내 점수: ")[1].split(",")[0])
            seller_scores.append(seller_val)
        else:
            seller_scores.append(0)

        avg_val = top10_avg.get(col, 0)
        avg_val = 0 if pd.isna(avg_val) else avg_val
        avg_scores.append(round(avg_val, 3))

    fig = go.Figure(
        data=[
            go.Bar(name="내 점수", x=labels, y=seller_scores, marker_color="#667eea"),
            go.Bar(name="상위 10% 평균", x=labels, y=avg_scores, marker_color="#764ba2"),
        ]
    )
    fig.update_layout(
        barmode="group",
        title="내 점수 vs 상위 10% 평균",
        xaxis_title="항목",
        yaxis_title="점수",
        template="plotly_white",
        width=900,
        height=640,
        font=dict(family="Segoe UI, Tahoma, Geneva, Verdana, sans-serif", color="#223"),
        legend=dict(bgcolor="#f0f0f0", bordercolor="#ccc", borderwidth=1, font=dict(color="black")),
    )
    st.plotly_chart(fig, use_container_width=True)

def sales_increase_regression_simulation(row, d_repurchase_rate, d_delay_rate, d_total_orders, d_avg_growth_rate, d_avg_review_score):
    coef = {
        "repurchase_rate": 601.35,
        "delay_rate": 317.22,
        "total_orders": 271.67,
        "avg_growth_rate": 171.98,
        "avg_review_score": 6.20,
    }

    base_sales = row["total_sales"]

    delta_sales = (
        coef["repurchase_rate"] * d_repurchase_rate
        + coef["delay_rate"] * d_delay_rate
        + coef["total_orders"] * d_total_orders
        + coef["avg_growth_rate"] * d_avg_growth_rate
        + coef["avg_review_score"] * d_avg_review_score
    )

    predicted_sales = base_sales + delta_sales
    return round(predicted_sales, 1), round(delta_sales, 1)

def plot_donut_chart(label, value, max_value=1.0, width=200, height=200):
    value = min(max(value, 0), max_value)  # 값 클립
    fig = go.Figure(
        data=[
            go.Pie(
                labels=[label, f"남은 부분"],
                values=[value, max_value - value],
                hole=0.55,
                sort=False,
                direction="clockwise",
                textinfo="none",
                marker_colors=["#667eea", "#e0e0e0"],
            )
        ]
    )
    fig.update_traces(textinfo="none", showlegend=False)
    fig.add_annotation(
        text=f"{label}<br><b>{value:.2f}</b>",
        x=0.5,
        y=0.5,
        font=dict(size=18),
        showarrow=False,
        xanchor="center",
        yanchor="middle",
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), width=width, height=height)
    return fig

try:
    img = Image.open("logo.png")
    st.image(img, width=150)
except FileNotFoundError:
    st.write("로고 이미지가 없습니다.")

st.title("판매자 관리 프로그램")

option = st.radio("조회 방법 선택", ["판매자 ID 입력", "숫자 번호 입력"])

if option == "판매자 ID 입력":
    id_input_str = st.text_input("판매자 ID를 입력하세요")
    if id_input_str:
        report = get_seller_report_by_id(id_input_str, seller_summary)
        if report:
            st.subheader("판매자 리포트")
            st.markdown(f'<div class="total-sales-highlight">총매출 금액: {report["총매출"]:,} BRL</div>', unsafe_allow_html=True)
            st.write(f"**신뢰도 점수:** {report['신뢰도 점수']}")
            st.write(f"**등급:** {report['등급']}")
            display_grade_benefits(report["등급"])
            plot_seller_scores_plotly(report, top10_avg)

            st.markdown("### 항목별 상세 결과")
            for k, v in report["항목별 결과"].items():
                st.markdown(f'<li class="detail-list">- {k}: {v}</li>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### 현재 주요 지표 점수")

            cols_top = st.columns(3)
            cols_bottom = st.columns(2)

            cols_top[0].plotly_chart(
                plot_donut_chart("재구매율", report["row"]["repurchase_rate"], max_value=1.0), use_container_width=True
            )
            cols_top[1].plotly_chart(
                plot_donut_chart("배송 지연율", report["row"]["delay_rate"], max_value=1.0), use_container_width=True
            )
            cols_top[2].plotly_chart(
                plot_donut_chart(
                    "주문 건수", report["row"]["total_orders"], max_value=max(1.0, report["row"]["total_orders"] * 1.5)
                ),
                use_container_width=True,
            )
            cols_bottom[0].plotly_chart(
                plot_donut_chart("매출 성장률", report["row"]["avg_growth_rate"], max_value=1.0), use_container_width=True
            )
            cols_bottom[1].plotly_chart(
                plot_donut_chart("평균 평점", report["row"]["avg_review_score"], max_value=5.0), use_container_width=True
            )

            st.markdown("---")
            st.markdown("### 매출 예측 시뮬레이션 (변경량 입력)")
            d_repurchase_rate = st.number_input("재구매율 변화량 (0~1)", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
            d_delay_rate = st.number_input("배송 지연율 변화량 (0~1)", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
            d_total_orders = st.number_input("주문 건수 변화량", min_value=0, max_value=10000, value=0, step=1)
            d_avg_growth_rate = st.number_input("매출 성장률 변화량 (소수)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
            d_avg_review_score = st.number_input("평균 평점 변화량 (0~5점)", min_value=0.0, max_value=5.0, value=0.0, step=0.1)

            expected_sales, delta_sales = sales_increase_regression_simulation(
                report["row"], d_repurchase_rate, d_delay_rate, d_total_orders, d_avg_growth_rate, d_avg_review_score
            )
            st.markdown(f"### 예상 매출액: {expected_sales:,} BRL (증가 예상액: {delta_sales:,} BRL)")
        else:
            st.error(":x: 해당 판매자 ID가 존재하지 않습니다.")
else:
    num_input_str = st.text_input("숫자 번호를 입력하세요 (1부터 시작)")
    if num_input_str:
        if num_input_str.isdigit():
            num_input = int(num_input_str)
            if 1 <= num_input <= len(seller_summary):
                report = get_seller_report_by_num(num_input, seller_summary)
                st.subheader("판매자 리포트")
                st.markdown(f'<div class="total-sales-highlight">총매출 금액: {report["총매출"]:,} BRL</div>', unsafe_allow_html=True)
                st.write(f"**신뢰도 점수:** {report['신뢰도 점수']}")
                st.write(f"**등급:** {report['등급']}")
                display_grade_benefits(report["등급"])
                plot_seller_scores_plotly(report, top10_avg)

                st.markdown("### 항목별 상세 결과")
                for k, v in report["항목별 결과"].items():
                    st.markdown(f'<li class="detail-list">- {k}: {v}</li>', unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("### 현재 주요 지표 점수")

                cols_top = st.columns(3)
                cols_bottom = st.columns(2)

                cols_top[0].plotly_chart(
                    plot_donut_chart("재구매율", report["row"]["repurchase_rate"], max_value=1.0), use_container_width=True
                )
                cols_top[1].plotly_chart(
                    plot_donut_chart("배송 지연율", report["row"]["delay_rate"], max_value=1.0), use_container_width=True
                )
                cols_top[2].plotly_chart(
                    plot_donut_chart(
                        "주문 건수", report["row"]["total_orders"], max_value=max(1.0, report["row"]["total_orders"] * 1.5)
                    ),
                    use_container_width=True,
                )
                cols_bottom[0].plotly_chart(
                    plot_donut_chart("매출 성장률", report["row"]["avg_growth_rate"], max_value=1.0), use_container_width=True
                )
                cols_bottom[1].plotly_chart(
                    plot_donut_chart("평균 평점", report["row"]["avg_review_score"], max_value=5.0), use_container_width=True
                )

                st.markdown("---")
                st.markdown("### 매출 예측 시뮬레이션 (변경량 입력)")
                d_repurchase_rate = st.number_input("재구매율 변화량 (0~1)", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
                d_delay_rate = st.number_input("배송 지연율 변화량 (0~1)", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
                d_total_orders = st.number_input("주문 건수 변화량", min_value=0, max_value=10000, value=0, step=1)
                d_avg_growth_rate = st.number_input("매출 성장률 변화량 (소수)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
                d_avg_review_score = st.number_input("평균 평점 변화량 (0~5점)", min_value=0.0, max_value=5.0, value=0.0, step=0.1)

                expected_sales, delta_sales = sales_increase_regression_simulation(
                    report["row"], d_repurchase_rate, d_delay_rate, d_total_orders, d_avg_growth_rate, d_avg_review_score
                )
                st.markdown(f"### 예상 매출액: {expected_sales:,} BRL (증가 예상액: {delta_sales:,} BRL)")
            else:
                st.error(":x: 유효하지 않은 숫자 범위입니다.")
        else:
            st.warning("숫자만 입력해주세요.")
