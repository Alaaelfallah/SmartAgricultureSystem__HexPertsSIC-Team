import streamlit as st


def render_home_tab() -> None:
    st.markdown(
        """
        <section class="landing-hero">
            <div class="landing-copy">
                <p class="landing-eyebrow"><span></span> Smart farming for a sustainable future</p>
                <div class="landing-title" role="heading" aria-level="1">Know your crops.<br><span>Grow with confidence.</span></div>
                <p class="landing-description">HexPerts brings crop health checks, irrigation planning, and practical growing guidance together in one smart farm workspace.</p>
                <div class="landing-actions">
                    <a class="landing-cta" href="#platform-modules">Explore the platform
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
                        </svg>
                    </a>
                    <span class="landing-note">Three tools. One growing season.</span>
                </div>
            </div>
            <div class="field-panel" aria-label="HexPerts platform modules">
                <div class="field-panel-heading">
                    <div>
                        <p class="field-panel-kicker">Platform at a glance</p>
                        <div class="field-panel-title" role="heading" aria-level="2">Field intelligence</div>
                    </div>
                    <span class="module-count">03 tools</span>
                </div>
                <a class="field-row" href="#module-vision">
                    <span class="field-icon">
                        <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
                            <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
                        </svg>
                    </span>
                    <span class="field-row-copy"><strong>Plant vision</strong><small>Check a leaf photo for disease</small></span>
                    <span class="field-row-kind">IMAGE</span>
                </a>
                <a class="field-row" href="#module-irrigation">
                    <span class="field-icon">
                        <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M12 2.7 17.7 8.4a8 8 0 1 1-11.4 0L12 2.7Z"/>
                            <path d="M8 15a4 4 0 0 0 4 4"/>
                        </svg>
                    </span>
                    <span class="field-row-copy"><strong>Irrigation planner</strong><small>Estimate water from field readings</small></span>
                    <span class="field-row-kind">SENSORS</span>
                </a>
                <a class="field-row" href="#module-chat">
                    <span class="field-icon">
                        <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        </svg>
                    </span>
                    <span class="field-row-copy"><strong>Farm advisor</strong><small>Explore crop and care questions</small></span>
                    <span class="field-row-kind">GUIDANCE</span>
                </a>
                <div class="field-panel-footer"><span></span> From crop signals to practical next steps</div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <section class="platform-overview" id="platform-modules">
            <div class="overview-heading">
                <div>
                    <p class="overview-kicker">One workspace, three tools</p>
                    <h2>Make the next field decision clearer.</h2>
                </div>
                <p>Move from an early crop check to smarter watering and useful agronomy guidance.</p>
            </div>
            <div class="feature-grid">
            <article class="feature-item" id="module-vision">
                <h3>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#86efac" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
                        <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
                    </svg>
                    Vision Track
                </h3>
                <p>Upload or capture a leaf photo to receive a disease label and confidence estimate.</p>
            </article>
            <article class="feature-item" id="module-irrigation">
                <h3>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#86efac" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
                        <line x1="6" y1="20" x2="6" y2="14"/>
                    </svg>
                    Environmental Track
                </h3>
                <p>Combine soil moisture and weather readings for a straightforward water estimate.</p>
            </article>
            <article class="feature-item" id="module-chat">
                <h3>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#86efac" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                    RAG Chatbot
                </h3>
                <p>Ask about crop care, disease prevention, soil, or irrigation timing.</p>
            </article>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p style="color:rgba(255,255,255,.55); text-align:center; font-size:.88rem">HexPerts Smart Farm Platform — AI Capstone Project</p>',
        unsafe_allow_html=True,
    )
