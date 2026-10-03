import base64
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKGROUND_IMAGE = PROJECT_ROOT / "assets" / "images" / "farm_background.jpg"


def get_base64_image(image_path: Path) -> str | None:
    if not image_path.is_file():
        return None

    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    extension = image_path.suffix.lower().lstrip(".")
    if extension == "jpg":
        extension = "jpeg"
    return f"data:image/{extension};base64,{encoded}"


def apply_custom_css() -> None:
    background_image = get_base64_image(BACKGROUND_IMAGE)
    background_url = (
        f"url('{background_image}')"
        if background_image
        else "url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1920')"
    )
    st.markdown(
        CUSTOM_CSS.format(background_url=background_url),
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="brand-signature">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#86efac" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <path d="M7 20h10"/><path d="M10 20c0-4 1.5-7 4-9"/>
                <path d="M14 11c0-3-1.5-6-4.5-8 0 3-1.5 6 0 8"/>
                <path d="M14 11c2.5 0 5-1.5 6-4-2.5 0-5 1.5-6 4z"/>
            </svg>
            <span class="brand-name">Hex<span>Perts</span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

CUSTOM_CSS = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

        * {{
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }}

        .landing-hero {{
            display: grid;
            grid-template-columns: minmax(0, 1.12fr) minmax(320px, 0.88fr);
            align-items: center;
            gap: clamp(2rem, 5vw, 5rem);
            min-height: 500px;
            padding: 2.4rem 0 3.4rem;
        }}

        .landing-copy {{ max-width: 620px; }}

        .landing-eyebrow {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            width: fit-content;
            margin: 0 0 1.2rem;
            padding: 0.35rem 0.65rem;
            border: 1px solid rgba(134, 239, 172, 0.24);
            border-radius: 999px;
            background: rgba(8, 27, 14, 0.48);
            color: #d7f8df;
            font-size: 0.78rem;
        }}

        .landing-eyebrow span, .field-panel-footer span {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #86efac;
            box-shadow: 0 0 12px rgba(134, 239, 172, 0.65);
        }}

        .landing-title {{
            margin: 0 0 1.2rem !important;
            color: #ffffff !important;
            font-size: 3.2rem !important;
            font-weight: 800 !important;
            line-height: 1.08 !important;
            text-shadow: 0 3px 18px rgba(0, 0, 0, 0.62) !important;
        }}

        .landing-title span {{ color: #a8e6a0; }}

        .landing-description {{
            max-width: 540px;
            margin: 0;
            color: rgba(255, 255, 255, 0.92);
            font-size: 1rem;
            line-height: 1.7;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.72);
        }}

        .landing-actions {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 1.7rem;
        }}

        .landing-cta {{
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.72rem 1rem;
            border: 1px solid rgba(134, 239, 172, 0.45);
            border-radius: 7px;
            background: #174b2c;
            color: #ffffff !important;
            font-size: 0.9rem;
            font-weight: 700;
            text-decoration: none !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.24);
            transition: background 160ms ease, transform 160ms ease;
        }}

        .landing-cta:hover {{
            background: #21653b;
            transform: translateY(-1px);
        }}

        .landing-note {{
            color: rgba(255, 255, 255, 0.78);
            font-size: 0.82rem;
            text-shadow: 0 1px 6px rgba(0, 0, 0, 0.8);
        }}

        .field-panel {{
            padding: 1.35rem 1.4rem 1.05rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 14px;
            background: rgba(6, 19, 11, 0.63);
            box-shadow: 0 18px 55px rgba(0, 0, 0, 0.24);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }}

        .field-panel-heading {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            padding: 0 0 1rem;
        }}

        .field-panel-kicker, .overview-kicker {{
            margin: 0 0 0.35rem;
            color: #a9e4ae;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .field-panel-heading .field-panel-title {{
            margin: 0;
            color: #ffffff !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.45) !important;
        }}

        .module-count {{
            padding: 0.3rem 0.55rem;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 999px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.7rem;
            white-space: nowrap;
        }}

        .field-row {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.8rem 0;
            border-top: 1px solid rgba(255, 255, 255, 0.12);
            color: #ffffff !important;
            text-decoration: none !important;
        }}

        .field-row:hover .field-row-copy strong {{ color: #b9f2c1; }}

        .field-icon {{
            display: grid;
            width: 38px;
            height: 38px;
            flex: 0 0 38px;
            place-items: center;
            border: 1px solid rgba(134, 239, 172, 0.24);
            border-radius: 10px;
            color: #9ae7a7;
            background: rgba(134, 239, 172, 0.07);
        }}

        .field-row-copy {{ display: flex; min-width: 0; flex: 1; flex-direction: column; gap: 0.12rem; }}
        .field-row-copy strong {{ color: #ffffff; font-size: 0.86rem; font-weight: 700; }}
        .field-row-copy small {{ color: rgba(255, 255, 255, 0.72); font-size: 0.76rem; line-height: 1.4; }}
        .field-row-kind {{ color: rgba(206, 229, 210, 0.64); font-size: 0.62rem; white-space: nowrap; }}

        .field-panel-footer {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding-top: 0.8rem;
            border-top: 1px solid rgba(255, 255, 255, 0.12);
            color: rgba(255, 255, 255, 0.75);
            font-size: 0.72rem;
        }}

        .field-panel-footer span {{ width: 6px; height: 6px; }}

        .platform-overview {{
            padding: 1.65rem 0 1.1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.23);
        }}

        .overview-heading {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) minmax(220px, 0.65fr);
            align-items: end;
            gap: 2rem;
            margin-bottom: 1.5rem;
        }}

        .overview-heading h2 {{
            margin: 0;
            color: #ffffff !important;
            font-size: 1.55rem !important;
            font-weight: 700 !important;
            text-shadow: 0 2px 6px rgba(0, 0, 0, 0.6) !important;
        }}

        .overview-heading > p {{
            margin: 0;
            color: rgba(255, 255, 255, 0.82);
            font-size: 0.86rem;
            line-height: 1.55;
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            font-weight: 800 !important;
            color: #86efac !important;
            letter-spacing: -0.015em;
            text-shadow: 0 2px 5px rgba(0,0,0,0.7), 0 0 10px rgba(134, 239, 172, 0.15);
        }}

        h1 {{ font-size: 2.8rem !important; }}
        h2 {{ font-size: 2.4rem !important; }}
        h3 {{ font-size: 2.2rem !important; }}
        h4 {{ font-size: 1.35rem !important; }}
        h5, h6 {{ font-size: 1.1rem !important; }}

        .home-hero {{
            padding: 1.4rem 1.8rem 1.2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.025);
        }}

        .hero-title {{
            display: flex !important;
            align-items: center !important;
            gap: 0.55rem !important;
            margin: 0 0 1.25rem !important;
            color: #ffffff !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            line-height: 1.4 !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.65) !important;
        }}

        .hero-title svg, .feature-item svg {{
            color: #86efac;
            flex: 0 0 auto;
        }}

        .home-hero p {{
            margin: 0;
            color: rgba(255, 255, 255, 0.94);
            font-size: 0.95rem;
            line-height: 1.55;
            text-shadow: 0 1px 3px rgba(0,0,0,0.6);
        }}

        .welcome-title {{
            margin: 1.4rem 0 0.5rem !important;
            color: #ffffff !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.7) !important;
        }}

        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            padding: 0;
        }}

        .feature-item {{
            flex: 1;
            min-width: 0;
            padding: 0 1.5rem;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .feature-item:first-child {{ padding-left: 0; }}
        .feature-item:last-child {{ padding-right: 0; border-right: 0; }}

        .feature-item h3 {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin: 0 0 1.1rem;
            color: #ffffff !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.65) !important;
        }}

        .feature-item p {{
            margin: 0;
            color: rgba(255, 255, 255, 0.92);
            font-size: 0.92rem;
            line-height: 1.55;
            text-shadow: 0 1px 3px rgba(0,0,0,0.6);
        }}

        .module-title {{
            font-size: 2.3rem !important;
            font-weight: 800 !important;
            color: #86efac !important;
            letter-spacing: -0.02em !important;
            text-shadow: 0 2px 5px rgba(0,0,0,0.8), 0 0 14px rgba(134, 239, 172, 0.22) !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.75rem !important;
            margin-bottom: 1.2rem !important;
        }}

        .card-title {{
            font-size: 1.3rem !important;
            font-weight: 700 !important;
            color: #86efac !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
            margin: 0 0 0.6rem 0 !important;
        }}

        /* ── Team Logo Signature (Top-Left) ── */
        .brand-signature {{
            position: fixed !important;
            top: 0.65rem !important;
            left: 1.5rem !important;
            z-index: 10000000 !important;
            display: flex !important;
            align-items: center !important;
            gap: 0.55rem !important;
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 999px !important;
            padding: 0.2rem 0.85rem 0.2rem 0.65rem !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
            user-select: none !important;
            pointer-events: auto !important;
            transition: all 0.25s ease !important;
        }}

        .brand-signature:hover {{
            background: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(134, 239, 172, 0.4) !important;
            transform: translateY(-1px);
        }}

        .brand-signature svg {{
            filter: drop-shadow(0 0 6px rgba(134, 239, 172, 0.5)) !important;
            flex-shrink: 0 !important;
        }}

        .brand-signature .brand-name {{
            font-family: 'Caveat', cursive !important;
            font-size: 1.65rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            letter-spacing: 0.03em !important;
            line-height: 1 !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.8) !important;
        }}

        .brand-signature .brand-name span {{
            color: #86efac !important;
            text-shadow: 0 0 10px rgba(134, 239, 172, 0.5) !important;
            font-family: 'Caveat', cursive !important;
            font-size: 1.65rem !important;
        }}

        .stApp {{
            background: linear-gradient(180deg, rgba(2, 6, 3, 0.75) 0%, rgba(2, 6, 3, 0.6) 40%, rgba(2, 6, 3, 0.8) 100%), {background_url} no-repeat center center fixed;
            background-size: cover;
            margin-top: 0 !important;
            padding-top: 0 !important;
        }}

        .main .block-container {{
            padding-top: 4.8rem !important;
            padding-bottom: 2rem !important;
        }}

        header[data-testid="stHeader"] {{
            background: rgba(3, 8, 5, 0.95) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.8) !important;
        }}

        .main, .block-container, div[data-testid="stVerticalBlock"] {{
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            transform: none !important;
            filter: none !important;
        }}

        /* Hide Streamlit Deploy button */
        [data-testid="stAppDeployButton"],
        .stAppDeployButton,
        [data-testid="stToolbarActions"],
        button[data-testid="stAppDeployButton"],
        header [data-testid="stAppDeployButton"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        .stTabs [role="tablist"] {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            height: 3.6rem !important;
            z-index: 9999999 !important;
            background: rgba(3, 8, 5, 0.95) !important;
            border: none !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 0 !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.8) !important;
            display: flex !important;
            gap: 2.2rem !important;
            justify-content: center !important;
            align-items: center !important;
            flex-wrap: nowrap !important;
            padding: 0 1rem !important;
            margin: 0 !important;
            pointer-events: auto !important;
        }}

        .stTabs [role="tab"] {{
            pointer-events: auto !important;
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            color: rgba(255, 255, 255, 0.85) !important;
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
            font-weight: 600;
            font-size: 1.05rem !important;
            letter-spacing: 0.01em;
            padding: 0.35rem 0.8rem !important;
            min-height: auto;
            min-width: 0;
            cursor: pointer;
            transition: all 0.2s ease;
            text-shadow: 0 2px 4px rgba(0,0,0,0.7);
            border-bottom: 2px solid transparent !important;
            filter: grayscale(100%) brightness(300%) !important;
        }}

        .stTabs [role="tab"][aria-selected="true"] {{
            background: transparent !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border: none !important;
            border-bottom: 2px solid #ffffff !important;
            box-shadow: none !important;
            text-shadow: 0 2px 6px rgba(0,0,0,0.8), 0 0 8px rgba(255,255,255,0.4) !important;
        }}

        .stTabs [role="tab"]:hover {{
            background: transparent !important;
            color: #ffffff !important;
            border: none !important;
            border-bottom: 2px solid rgba(255,255,255,0.6) !important;
            box-shadow: none !important;
        }}

        .stTabs [data-baseweb="tab-border"],
        .stTabs [data-baseweb="tab-highlight"] {{
            display: none !important;
        }}

        /* ── All Streamlit containers: ultra transparent ── */
        .stContainer > div,
        .stAlert,
        .stDataFrame,
        .stFileUploader,
        .stSelectbox,
        .stTextInput,
        .stTextArea,
        .stNumberInput,
        .stRadio,
        .stCheckbox,
        .stSlider,
        .stChatMessage {{
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 18px !important;
            backdrop-filter: blur(2px) !important;
            -webkit-backdrop-filter: blur(2px) !important;
            box-shadow: none !important;
        }}

        .stMarkdown, .stWrite {{
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            box-shadow: none !important;
        }}

        .stButton > button {{
            background: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            border-radius: 14px !important;
            color: #ffffff !important;
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em;
            backdrop-filter: blur(5px) !important;
            text-shadow: 0 1px 3px rgba(0,0,0,0.7);
            transition: all 0.2s ease;
        }}

        .stButton > button:hover {{
            background: rgba(255, 255, 255, 0.25) !important;
            border-color: #ffffff !important;
            color: #ffffff !important;
        }}

        p, li, label, span,
        .stMarkdown p, .stMarkdown li,
        .stTextInput input, .stTextArea textarea,
        .stSelectbox div, .stNumberInput input,
        .stSlider div, .stFileUploader div,
        .stRadio div, .stCheckbox div, .stChatMessage,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] span,
        div[data-testid="stMarkdownContainer"] li,
        .stWidgetLabel label,
        .stWidgetLabel span,
        [data-testid="stWidgetLabel"] p {{
            color: #ffffff !important;
            font-family: 'Inter', 'Plus Jakarta Sans', sans-serif !important;
            font-size: 0.95rem !important;
            line-height: 1.55;
            text-shadow: 0 1px 3px rgba(0,0,0,0.6);
        }}

        /* ── Chat avatars: make emojis pure white ── */
        div[data-testid="stChatMessage"] > div:first-child {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 12px !important;
            filter: grayscale(100%) brightness(300%) !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
        }}

        [data-testid="stChatMessageAvatarAssistant"],
        [data-testid="stChatMessageAvatarUser"],
        .stChatMessage [data-testid="chatAvatarIcon-assistant"],
        .stChatMessage [data-testid="chatAvatarIcon-user"] {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 12px !important;
            filter: grayscale(100%) brightness(300%) !important;
        }}

        /* ── White divider lines ── */
        hr, [data-testid="stDivider"] hr, .stDivider hr {{
            border: none !important;
            border-top: 1.5px solid rgba(255, 255, 255, 0.25) !important;
            margin: 1.2rem 0 !important;
            background: none !important;
            box-shadow: 0 1px 4px rgba(255,255,255,0.06) !important;
        }}
        @media (max-width: 760px) {{
            .landing-hero {{
                grid-template-columns: 1fr;
                gap: 1.5rem;
                min-height: 0;
                padding: 2rem 0 2.5rem;
            }}
            .landing-title {{ font-size: 2.5rem !important; }}
            .field-panel {{ max-width: none; }}
            .overview-heading {{ grid-template-columns: 1fr; gap: 0.65rem; }}
            .feature-grid {{ grid-template-columns: 1fr; gap: 1.2rem; }}
            .feature-item, .feature-item:first-child, .feature-item:last-child {{
                padding: 0 0 1rem;
                border-right: 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .feature-item:last-child {{ padding-bottom: 0; border-bottom: 0; }}
        }}
    </style>
"""

