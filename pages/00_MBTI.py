# app.py
# Streamlit MBTI -> 진로 추천 앱
# 요구: streamlit만 설치되어 있으면 작동합니다.
import streamlit as st

st.set_page_config(page_title="MBTI 진로 추천 🌟", page_icon="🧭", layout="centered")

st.title("✨ MBTI로 똑똑하게 진로 고르기")
st.write("내 MBTI 골라봐! 각 유형에 맞춘 **진로 2가지**랑 어떤 학과/어떤 성격이 잘 맞는지도 알려줄게 😄")

MBTI_TYPES = [
    "ISTJ","ISFJ","INFJ","INTJ",
    "ISTP","ISFP","INFP","INTP",
    "ESTP","ESFP","ENFP","ENTP",
    "ESTJ","ESFJ","ENFJ","ENTJ"
]

# 데이터: 각 MBTI에 대해 (진로1, 학과/설명, 성격), (진로2,...)
MBTI_CAREERS = {
    "ISTJ": [
        {
            "career":"공무원 / 행정직",
            "dept":"행정학, 법학, 공공정책",
            "personality":"규칙적이고 책임감 강한 사람에게 딱. 체계적으로 일하는 걸 좋아하면 OK ✅",
            "emoji":"🏛️"
        },
        {
            "career":"회계사 / 재무",
            "dept":"회계학, 경영학, 재무",
            "personality":"숫자에 강하고 꼼꼼한 성격이면 잘 맞음. 디테일 파괴자! 💼",
            "emoji":"📊"
        }
    ],
    "ISFJ": [
        {
            "career":"간호사 / 보건의료직",
            "dept":"간호학, 보건학",
            "personality":"타인을 돌보는 걸 좋아하고 신중한 성향이면 만족감 최고 💖",
            "emoji":"🩺"
        },
        {
            "career":"교사(초등/유치원)",
            "dept":"교육학, 유아교육",
            "personality":"섬세하고 책임감 있는 성격이면 학생들과 잘 어울려요 🍎",
            "emoji":"🍎"
        }
    ],
    "INFJ": [
        {
            "career":"상담사 / 임상심리사",
            "dept":"심리학, 상담학",
            "personality":"사람 마음에 공감하고 깊은 통찰을 갖춘 사람에게 잘 맞음 💬",
            "emoji":"🧠"
        },
        {
            "career":"창의적 작가 / 콘텐츠 크리에이터",
            "dept":"문예창작, 커뮤니케이션",
            "personality":"내면 세계가 풍부하고 메시지를 전달하고 싶어하면 굿 ✍️",
            "emoji":"📚"
        }
    ],
    "INTJ": [
        {
            "career":"연구원 / 데이터사이언티스트",
            "dept":"수학, 통계학, 컴퓨터공학",
            "personality":"전략적으로 사고하고 시스템을 설계하는 걸 즐기는 사람에게 적합 🧩",
            "emoji":"🔬"
        },
        {
            "career":"전략 컨설턴트",
            "dept":"경영학, 산업공학",
            "personality":"논리적이고 미래지향적인 문제 해결을 좋아하면 최고 💡",
            "emoji":"🧭"
        }
    ],
    "ISTP": [
        {
            "career":"기계공학자 / 엔지니어",
            "dept":"기계공학, 전기전자공학",
            "personality":"손으로 만들고 문제를 즉각 해결하는 걸 좋아하는 실전형 🛠️",
            "emoji":"⚙️"
        },
        {
            "career":"응급구조사 / 현장 기술자",
            "dept":"응급구조학, 산업안전",
            "personality":"침착하고 즉각 행동할 수 있는 성향이면 잘 맞음 🚑",
            "emoji":"🚧"
        }
    ],
    "ISFP": [
        {
            "career":"디자이너(그래픽/패션)",
            "dept":"시각디자인, 패션디자인",
            "personality":"감각적이고 미적 감각이 좋은 사람에게 추천 🎨",
            "emoji":"🎨"
        },
        {
            "career":"음악가 / 공연예술",
            "dept":"음악학, 공연예술",
            "personality":"감성표현이 풍부하고 창의성을 발휘하고 싶다면 굿 🎵",
            "emoji":"🎤"
        }
    ],
    "INFP": [
        {
            "career":"작가 / 편집자",
            "dept":"문예창작, 국어국문학",
            "personality":"이상주의적이고 깊이 있는 표현을 좋아하는 사람에게 잘 맞음 ✨",
            "emoji":"📝"
        },
        {
            "career":"사회적기업가 / NGO 활동가",
            "dept":"사회복지학, 국제관계학",
            "personality":"가치 중심적으로 세상을 바꾸고 싶은 마음이 있다면 굿 🌱",
            "emoji":"🌍"
        }
    ],
    "INTP": [
        {
            "career":"소프트웨어 개발자 / 연구자",
            "dept":"컴퓨터공학, 전산학, 물리학",
            "personality":"이론적 사고를 즐기고 문제를 깊게 파는 타입에게 딱 💻",
            "emoji":"💡"
        },
        {
            "career":"학술연구 / 대학원 진학",
            "dept":"전공 기반 학과(수학/철학/물리 등)",
            "personality":"자유롭게 탐구하고 혼자 집중하는 걸 좋아하면 OK 📚",
            "emoji":"🔍"
        }
    ],
    "ESTP": [
        {
            "career":"영업 / 이벤트 기획",
            "dept":"경영학, 관광학, 커뮤니케이션",
            "personality":"행동력이 빠르고 사람 만나는 걸 좋아하면 흥미진진 😎",
            "emoji":"🎪"
        },
        {
            "career":"파일럿 / 소방관 / 응급대원",
            "dept":"항공학, 소방안전, 응급구조",
            "personality":"모험심 있고 실전에서 민첩한 사람에게 잘 맞음 ✈️",
            "emoji":"🔥"
        }
    ],
    "ESFP": [
        {
            "career":"연예/엔터테인먼트",
            "dept":"연기, 음악, 공연예술",
            "personality":"사람들 앞에서 빛나고 재미있는 걸 좋아하면 찰떡 ⭐",
            "emoji":"🎭"
        },
        {
            "career":"관광/서비스업",
            "dept":"관광학, 호텔경영",
            "personality":"친화력 좋고 즐겁게 고객을 대하는 걸 좋아하면 굿 🏨",
            "emoji":"🌟"
        }
    ],
    "ENFP": [
        {
            "career":"마케팅 / 브랜드 기획",
            "dept":"광고홍보, 경영학, 커뮤니케이션",
            "personality":"창의적 아이디어가 넘치고 사람 연결을 즐기면 찰떡 💥",
            "emoji":"📣"
        },
        {
            "career":"창업가 / 스타트업",
            "dept":"경영학, 창업 관련 학과",
            "personality":"새로운 것 시도하고 사람과 협업하는 걸 즐긴다면 추천 🚀",
            "emoji":"🚀"
        }
    ],
    "ENTP": [
        {
            "career":"창업가 / 제품기획자",
            "dept":"경영학, 산업디자인, 컴퓨터공학",
            "personality":"아이디어가 많고 도전적이면 빠르게 시도해보는 타입 ⚡",
            "emoji":"💡"
        },
        {
            "career":"변호사 / 토론가",
            "dept":"법학, 정치외교학",
            "personality":"논쟁을 즐기고 논리로 설득하는 걸 좋아하면 잘 맞음 ⚖️",
            "emoji":"🗣️"
        }
    ],
    "ESTJ": [
        {
            "career":"경영관리 / 운영매니저",
            "dept":"경영학, 산업공학",
            "personality":"조직을 이끌고 효율을 높이는 걸 좋아하는 리더형 🏢",
            "emoji":"📈"
        },
        {
            "career":"군인 / 경찰",
            "dept":"국방/경찰학 관련, 공공안전",
            "personality":"규율과 책임감을 중요시하는 사람에게 적합 👮",
            "emoji":"🪖"
        }
    ],
    "ESFJ": [
        {
            "career":"간호/사회복지/교육",
            "dept":"간호학, 사회복지학, 교육학",
            "personality":"사람 돌보는 걸 좋아하고 팀워크를 중시하면 행복함 🤝",
            "emoji":"❤️"
        },
        {
            "career":"HR / 인사담당",
            "dept":"경영학, 인사관리",
            "personality":"사람 관계를 잘 관리하고 배려심 많은 타입에게 좋아요 👥",
            "emoji":"🗂️"
        }
    ],
    "ENFJ": [
        {
            "career":"교육자 / 리더십 코치",
            "dept":"교육학, 상담학, 경영학",
            "personality":"사람을 이끌고 동기부여하는 걸 즐기는 카리스마형 ✨",
            "emoji":"🌱"
        },
        {
            "career":"PR / 커뮤니케이션 매니저",
            "dept":"광고홍보, 커뮤니케이션",
            "personality":"사람과 메시지를 연결시키는 걸 잘하는 외향형에게 추천 📢",
            "emoji":"🤝"
        }
    ],
    "ENTJ": [
        {
            "career":"CEO / 경영컨설턴트",
            "dept":"경영학, 경제학, 산업공학",
            "personality":"전략적이고 목표지향적인 리더십이 있는 사람에게 최고 🦾",
            "emoji":"🏆"
        },
        {
            "career":"금융투자 전문가",
            "dept":"금융학, 경영학, 경제학",
            "personality":"결단력 있고 큰 그림을 보며 의사결정하는 걸 즐기면 굿 💹",
            "emoji":"💼"
        }
    ],
}

# UI
col1, col2 = st.columns([1,1])
with col1:
    mbti = st.selectbox("너의 MBTI를 선택해줘 💫", MBTI_TYPES, index=0)
with col2:
    st.write("")
    st.write("")
    st.caption("친구한테도 보여주기 쉬운 추천이야! 😎")

st.markdown("---")

if mbti:
    st.subheader(f"{mbti} 유형 추천 결과 {MBTI_CAREERS[mbti][0]['emoji']}{MBTI_CAREERS[mbti][1]['emoji']}")
    for idx, item in enumerate(MBTI_CAREERS[mbti], start=1):
        st.markdown(f"### {idx}. {item['career']} {item['emoji']}")
        st.write(f"**어떤 학과가 좋아?** {item['dept']}")
        st.write(f"**어떤 성격이 잘 맞을까?** {item['personality']}")
        st.write("---")

st.info("참고: 이건 성향 기반 추천이야. 너만의 흥미와 경험도 꼭 고려해~ 필요하면 지원 전형/학과 정보도 정리해줄게! 😉")
st.write("© MBTI 진로 추천기 — 재밌게 참고만 해줘 😄")
