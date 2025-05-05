import os
import json
from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.font_manager as fm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import anthropic
from dotenv import load_dotenv
from io import BytesIO

# 환경 변수 로드
load_dotenv()

# Anthropic 클라이언트 설정
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 모델 설정
MODEL = "claude-3-7-sonnet-20250219"

# 한글 폰트 설정
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
if not os.path.exists(font_path):
    raise FileNotFoundError(f"폰트 파일이 존재하지 않습니다: {font_path}")

# reportlab 한글 폰트 설정
pdfmetrics.registerFont(TTFont('NanumGothic', font_path))

# matplotlib 한글 폰트 설정
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fontprop.get_name()
plt.rcParams['axes.unicode_minus'] = False

def create_report_with_claude(data):
    """Claude API를 사용하여 상세 리포트 생성"""
    prompt = f"""
당신은 뉴스 데이터 분석 전문가입니다. 다음 데이터를 바탕으로 전문적이고 통찰력 있는 일일 뉴스 분석 리포트를 작성해주세요.

데이터:
- 날짜: {data['meta']['date']}
- 총 기사 수: {data['meta']['total_articles']}
- 주요 카테고리: {data['meta']['top_category']}
- 주요 언론사: {data['meta']['top_source']}
- 주요 키워드: {data['meta']['top_keyword']}

카테고리별 분포:
{json.dumps(data['category_counts'], ensure_ascii=False, indent=2)}

언론사별 분포:
{json.dumps(data['source_counts'][:10], ensure_ascii=False, indent=2)}

상위 키워드:
{json.dumps(data['keyword_counts'][:30], ensure_ascii=False, indent=2)}

기사 길이 분포:
{json.dumps(data['length_distribution'], ensure_ascii=False, indent=2)}

다음 구조로 상세한 분석 리포트를 작성해주세요:

1. 요약 (Executive Summary)
   - 오늘의 주요 뉴스 트렌드 3-4가지
   - 특이사항 및 주목할 점

2. 카테고리별 상세 분석
   - 주요 카테고리의 특징
   - AI 재분류 vs 원본 카테고리 비교 인사이트

3. 언론사 분석
   - 주요 언론사들의 보도 특성
   - 언론사별 주력 분야

4. 키워드 트렌드 분석
   - 상위 키워드의 의미와 맥락
   - 키워드 클러스터링 및 연관성

5. 기사 길이 분포 분석
   - 길이별 기사 특성
   - 카테고리와 길이의 연관성

6. 종합 인사이트
   - 오늘의 뉴스가 시사하는 바
   - 향후 주목해야 할 트렌드

전문적이고 분석적인 톤으로 작성하되, 이해하기 쉽게 설명해주세요.
"""
    
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            temperature=0.7,
            system="당신은 한국 뉴스 시장에 정통한 미디어 분석 전문가입니다. 데이터를 기반으로 통찰력 있는 분석을 제공합니다.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    except Exception as e:
        print(f"Claude API 오류: {e}")
        return "리포트 생성 중 오류가 발생했습니다."

def plot_bar_chart(items, title, label_key, value_key):
    """막대 차트 생성 후 이미지로 반환"""
    labels = [item[label_key] for item in items]
    values = [item[value_key] for item in items]
    
    # 정사각형에 가까운 비율로 수정
    fig, ax = plt.subplots(figsize=(8, 8))
    bars = ax.barh(labels[::-1], values[::-1])
    ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel('기사 수', fontsize=12)
    
    # 막대에 값 표시
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', ha='left', va='center', fontsize=10)
    
    plt.tight_layout()
    
    # 이미지를 메모리에 저장 - DPI 높여서 선명도 개선
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    
    return img_buffer

def create_keyword_chart(keyword_counts):
    """키워드 차트 생성"""
    keywords = [item['keyword'] for item in keyword_counts[:15]]  # 20개에서 15개로 줄임
    counts = [item['count'] for item in keyword_counts[:15]]
    
    # 정사각형 비율
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.tab20(range(len(keywords)))
    
    wedges, texts, autotexts = ax.pie(counts, labels=keywords, autopct='%1.1f%%', 
                                     colors=colors, pctdistance=0.85)
    
    ax.set_title('상위 15개 키워드 분포', fontsize=16, fontweight='bold', pad=15)
    
    # 텍스트 크기 조정
    for text in texts:
        text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_fontsize(8)
    
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    
    return img_buffer

def generate_pdf(date, input_dir, output_dir):
    """Claude API를 활용한 PDF 리포트 생성"""
    
    print(f"[INFO] PDF 리포트 생성 날짜: {date}")
    
    # 파일 경로 설정
    report_filename = f"{date}_report.json"
    report_path = os.path.join(input_dir, report_filename)
    output_pdf_path = os.path.join(output_dir, f"{date}_report.pdf")

    if not os.path.exists(report_path):
        raise FileNotFoundError(f"리포트 JSON 파일이 존재하지 않습니다: {report_path}")

    # JSON 데이터 로드
    with open(report_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Claude로 리포트 생성
    print("Claude API로 리포트 생성 중...")
    claude_report = create_report_with_claude(data)

    # 차트 이미지 생성
    print("차트 생성 중...")
    category_chart = plot_bar_chart(data['category_counts'], "AI 카테고리별 기사 수", "category", "count")
    original_category_chart = plot_bar_chart(data['original_category_counts'], "원본 카테고리별 기사 수", "category", "count")
    keyword_chart = create_keyword_chart(data['keyword_counts'])

    # PDF 생성
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    # 스타일 설정
    styles = getSampleStyleSheet()
    
    # 한글 폰트 스타일
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='NanumGothic',
        fontSize=24,
        spaceAfter=30,
        alignment=1  # 중앙 정렬
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName='NanumGothic',
        fontSize=18,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#1a5276')
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='NanumGothic',
        fontSize=11,
        leading=16,
        spaceBefore=6,
        spaceAfter=6
    )
    
    story = []
    
    # 표지
    story.append(Spacer(1, 100))
    story.append(Paragraph(f"{data['meta']['date']}", title_style))
    story.append(Paragraph("일일 뉴스 분석 리포트", title_style))
    story.append(Spacer(1, 50))
    
    # 요약 정보
    summary_data = [
        ["총 기사 수", str(data['meta']['total_articles'])],
        ["주요 카테고리", data['meta']['top_category']],
        ["주요 언론사", data['meta']['top_source']],
        ["주요 키워드", data['meta']['top_keyword']]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a5276')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 100))
    
    # AI 분석 마크
    ai_mark = Paragraph(
        "본 리포트는 Claude AI를 활용하여 자동 생성되었습니다.",
        ParagraphStyle('AImark', parent=normal_style, fontSize=10, textColor=colors.grey)
    )
    story.append(ai_mark)
    story.append(PageBreak())
    
    # Claude가 생성한 리포트 내용
    story.append(Paragraph("AI 뉴스 분석 리포트", heading_style))
    story.append(Spacer(1, 20))
    
    # 리포트 텍스트를 단락별로 분리하여 추가
    paragraphs = claude_report.split('\n\n')
    for para in paragraphs:
        if para.strip():
            # 제목 처리
            if para.startswith('#'):
                level = len(para.split()[0])
                clean_text = para.lstrip('#').strip()
                story.append(Paragraph(clean_text, heading_style))
            elif any(para.startswith(f"{i}.") for i in range(1, 10)):
                # 번호가 매겨진 항목
                story.append(Paragraph(para, normal_style))
            else:
                # 일반 단락
                story.append(Paragraph(para, normal_style))
            story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # 시각화 자료
    story.append(Paragraph("데이터 시각화", heading_style))
    story.append(Spacer(1, 20))
    
    # 차트 삽입 - 3개의 차트만 사용
    charts = [
        ("AI 카테고리별 기사 분포", category_chart),
        ("원본 카테고리별 기사 분포", original_category_chart),
        ("상위 키워드 분포", keyword_chart)
    ]
    
    # 차트를 2x2 그리드로 배치 (3개의 차트)
    chart_data = []
    for i in range(0, len(charts), 2):
        row = []
        for j in range(2):
            if i + j < len(charts):
                title, chart = charts[i + j]
                # 제목과 이미지를 포함한 셀 생성
                cell_content = [
                    Paragraph(f"{i+j+1}. {title}", heading_style),
                    Spacer(1, 10),
                    Image(chart, width=250, height=250)  # 크기 축소
                ]
                row.append(cell_content)
            else:
                row.append("")  # 빈 셀
        chart_data.append(row)
    
    # 차트 테이블 생성
    chart_table = Table(chart_data, colWidths=[270, 270])
    chart_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(chart_table)
    
    # PDF 생성
    doc.build(story)
    print(f"✅ PDF 리포트 저장 완료: {output_pdf_path}")

# 실행 코드 수정
if __name__ == "__main__":
    import argparse
    
    # 명령행 인자 파서 설정
    parser = argparse.ArgumentParser(description="Claude를 이용한 일일 뉴스 PDF 리포트 생성")
    parser.add_argument("--date", required=True, help="리포트 생성 날짜 (YYYY-MM-DD)")
    parser.add_argument("--input-dir", default="./data/news_archive", help="입력 디렉토리 경로")
    parser.add_argument("--output-dir", default="./data/news_archive", help="출력 디렉토리 경로")
    
    args = parser.parse_args()
    
    # .env 파일에서 환경 변수 로드
    load_dotenv()
    
    # API 키 확인
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY 환경 변수가 설정되어 있지 않습니다.")
    
    # 디렉토리 존재 확인
    if not os.path.exists(args.input_dir):
        raise FileNotFoundError(f"입력 디렉토리가 존재하지 않습니다: {args.input_dir}")
    
    # 출력 디렉토리 생성
    os.makedirs(args.output_dir, exist_ok=True)
    
    # PDF 생성
    generate_pdf(args.date, args.input_dir, args.output_dir)