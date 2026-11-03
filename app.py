"""AURA — AI Music Composer: Streamlit front-end."""

from datetime import datetime
from html import escape
from io import BytesIO
from math import ceil

import streamlit as st
from dotenv import load_dotenv

from app.main import MusicLLM
from app.utils import generate_wav_bytes_from_notes_freq, note_to_frequencies


load_dotenv()

DURATION_SECONDS = {
    "30 seconds": 30,
    "60 seconds": 60,
    "90 seconds": 90,
    "2 minutes": 120,
}
GENRE_OPTIONS = ["Ambient", "Cinematic", "Jazz", "Electronic", "Lo-fi", "Classical"]
MOOD_OPTIONS = ["Dreamy", "Euphoric", "Melancholic", "Focused", "Mysterious", "Serene"]
PALETTE_OPTIONS = [
    "Piano & strings",
    "Synth & pads",
    "Acoustic ensemble",
    "Guitar & drums",
    "Orchestral",
]
SECONDS_PER_NOTE = 0.5
MAX_HISTORY_TRACKS = 6


st.set_page_config(
    page_title="AURA — AI Music Composer",
    page_icon="🎼",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_styles() -> None:
    """Inject the page theme once per render."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
            --ink: #f7f6fb;
            --muted: #9c9aa9;
            --subtle: #6f6d7d;
            --line: rgba(255, 255, 255, .09);
            --purple: #a98cff;
            --purple-bright: #c4b2ff;
        }

        .stApp {
            color: var(--ink);
            background:
                radial-gradient(circle at 82% 0%, rgba(108, 76, 182, .18), transparent 32rem),
                radial-gradient(circle at 5% 48%, rgba(47, 42, 84, .18), transparent 30rem),
                #0b0b10;
            font-family: 'Manrope', sans-serif;
        }
        .block-container { max-width: 1120px; padding: 2rem 2.5rem 4.5rem; }
        header[data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
        h1, h2, h3, p { font-family: 'Manrope', sans-serif; }

        .eyebrow {
            color: var(--purple-bright); font-family: 'DM Mono', monospace;
            font-size: .68rem; letter-spacing: .2em; text-transform: uppercase;
        }
        .brand {
            align-items: center; display: flex; gap: .65rem; margin-bottom: 4.5rem;
            color: var(--ink); font-size: .85rem; font-weight: 800; letter-spacing: .14em;
        }
        .brand-mark {
            align-items: center; background: linear-gradient(135deg, #aa8dff, #6048a4);
            border-radius: 10px; display: flex; height: 34px; justify-content: center; width: 34px;
        }
        .hero { max-width: 790px; margin-bottom: 3.4rem; }
        .hero h1 {
            font-size: clamp(2.8rem, 6vw, 5.2rem); letter-spacing: -.075em;
            line-height: .98; margin: .85rem 0 1.4rem;
        }
        .hero h1 span { color: var(--purple-bright); }
        .hero p { color: var(--muted); font-size: 1.03rem; line-height: 1.7; max-width: 560px; }

        .section-label {
            color: var(--muted); font-family: 'DM Mono', monospace; font-size: .68rem;
            letter-spacing: .14em; margin: 2.4rem 0 .85rem; text-transform: uppercase;
        }
        .prompt-label { color: var(--ink); font-size: .92rem; font-weight: 700; margin-bottom: .55rem; }
        .hint { color: var(--subtle); font-size: .75rem; margin-top: -.35rem; }

        div[data-testid="stTextArea"] textarea {
            background: rgba(9, 9, 14, .62); border: 1px solid rgba(255, 255, 255, .1);
            border-radius: 14px; color: var(--ink); font-size: .94rem; line-height: 1.55;
            min-height: 112px; padding: 1rem; transition: border .2s, box-shadow .2s;
        }
        div[data-testid="stTextArea"] textarea:focus {
            border-color: var(--purple); box-shadow: 0 0 0 3px rgba(169, 140, 255, .12);
        }
        div[data-testid="stTextArea"] textarea::placeholder { color: var(--subtle); }
        label { color: var(--muted) !important; font-size: .78rem !important; }
        div[data-baseweb="select"] > div, div[data-testid="stNumberInput"] input {
            background: rgba(9, 9, 14, .62); border: 1px solid var(--line);
            border-radius: 11px; color: var(--ink);
        }
        div.stButton > button, div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, #bba5ff, #8665d9); border: 0; border-radius: 12px;
            color: #15111f; font-weight: 800; min-height: 48px;
            transition: transform .2s, box-shadow .2s; width: 100%;
        }
        div.stButton > button:hover, div[data-testid="stButton"] > button:hover {
            box-shadow: 0 10px 28px rgba(144, 106, 223, .3); transform: translateY(-2px);
        }

        .track-header { align-items: start; display: flex; justify-content: space-between; gap: 1rem; }
        .track-title { font-size: 1.25rem; font-weight: 800; letter-spacing: -.03em; }
        .track-meta { color: var(--muted); font-size: .75rem; margin-top: .35rem; }
        .status-pill {
            background: rgba(169, 140, 255, .12); border-radius: 999px; color: var(--purple-bright);
            font-family: 'DM Mono', monospace; font-size: .64rem; padding: .38rem .65rem;
            white-space: nowrap;
        }
        audio { width: 100%; margin-top: 1.1rem; }
        .summary {
            border-left: 2px solid var(--purple); color: var(--muted); font-size: .82rem;
            line-height: 1.7; margin-top: 1.15rem; padding: .2rem 0 .2rem 1rem;
            white-space: pre-line;
        }
        .history-heading {
            align-items: baseline; display: flex; justify-content: space-between;
            margin: 2.8rem 0 .4rem;
        }
        .history-heading h2 { font-size: 1.25rem; letter-spacing: -.04em; margin: 0; }
        .history-heading span { color: var(--subtle); font-size: .75rem; }
        .history-empty { color: var(--subtle); font-size: .82rem; padding: 1rem 0 0; }

        @media (max-width: 720px) {
            .block-container { padding: 1.4rem 1rem 3rem; }
            .brand { margin-bottom: 3.2rem; }
            .hero { margin-bottom: 2.2rem; }
            .hero h1 { font-size: 3.3rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand() -> None:
    st.markdown(
        '<div class="brand"><div class="brand-mark">♫</div><span>AURA / MUSIC LAB</span></div>',
        unsafe_allow_html=True,
    )


def render_track_header(icon: str, track: dict, pill: str) -> None:
    """Render the shared title/meta/pill header used by results and history."""
    st.markdown(
        f'<div class="track-header"><div>'
        f'<div class="track-title">{icon} {escape(str(track["title"]))}</div>'
        f'<div class="track-meta">{escape(str(track["style"]))} · '
        f'{escape(str(track["mood"]))} · {track["tempo"]} BPM · '
        f'{escape(str(track["duration"]))}</div></div>'
        f'<div class="status-pill">{pill}</div></div>',
        unsafe_allow_html=True,
    )


def render_history() -> None:
    history = st.session_state.get("history", [])
    st.markdown(
        f'<div class="history-heading"><h2>Recent compositions</h2>'
        f'<span>{len(history)} session tracks</span></div>',
        unsafe_allow_html=True,
    )
    if not history:
        st.markdown(
            '<p class="history-empty">Your first composition will appear here. '
            "Start with a feeling, a scene, or a single line of poetry.</p>",
            unsafe_allow_html=True,
        )
        return

    for index, track in enumerate(history):
        if index:
            st.divider()
        render_track_header("🎵", track, "COMPOSED")
        st.audio(BytesIO(track["audio"]), format="audio/wav")


def collect_frequencies(melody: str, harmony: str) -> list[float]:
    """Convert the LLM note strings into a flat list of playable frequencies."""
    melody_freqs = note_to_frequencies(melody.split())
    harmony_notes: list[str] = []
    for chord in harmony.split():
        harmony_notes.extend(chord.split("-"))
    return melody_freqs + note_to_frequencies(harmony_notes)


def compose_track(
    music_input: str,
    style: str,
    mood: str,
    tempo: int,
    instruments: str,
    duration: str,
) -> dict:
    generator = MusicLLM()
    enriched_prompt = (
        f"{music_input.strip()}. Genre: {style}. Mood: {mood}. Tempo: {tempo} BPM. "
        f"Instruments: {instruments}. Target duration: {duration}."
    )

    with st.spinner("Sketching your composition..."):
        melody = generator.generate_melody(enriched_prompt)
        harmony = generator.generate_harmony(melody)
        rhythm = generator.generate_rythm(melody)
        composition = generator.adapt_style(style, melody, harmony, rhythm)

        frequencies = collect_frequencies(melody, harmony)
        if not frequencies:
            st.error(
                "The composition did not contain playable notes. "
                "Try a more specific musical description and generate again."
            )
            st.stop()

        target_notes = max(1, round(DURATION_SECONDS[duration] / SECONDS_PER_NOTE))
        frequencies = (frequencies * ceil(target_notes / len(frequencies)))[:target_notes]
        wav_bytes = generate_wav_bytes_from_notes_freq(frequencies)

    title = music_input.strip().split(".")[0][:48].strip().capitalize()
    return {
        "title": title or "Untitled atmosphere",
        "style": style,
        "mood": mood,
        "tempo": tempo,
        "duration": duration,
        "audio": wav_bytes,
        "summary": composition,
        "created": datetime.now().strftime("%H:%M"),
    }


load_styles()
render_brand()

st.markdown(
    '<div class="hero"><div class="eyebrow">AI-assisted composition studio</div>'
    "<h1>Turn a feeling into<br><span>something you can hear.</span></h1>"
    "<p>Shape a musical idea with intention. AURA translates your words into an original "
    "melody, harmony, and rhythm — ready for your next creative moment.</p></div>",
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">01 / Compose a new piece</div>', unsafe_allow_html=True)
st.markdown('<div class="prompt-label">What should it sound like?</div>', unsafe_allow_html=True)
music_input = st.text_area(
    "Describe the scene, feeling, or story",
    placeholder="A cinematic night drive through a neon city, slowly opening into dawn...",
    label_visibility="collapsed",
)
st.markdown(
    '<div class="hint">Be evocative — the more atmosphere you share, the more character your '
    "composition will have.</div>",
    unsafe_allow_html=True,
)
st.space("small")

control_columns = st.columns(5)
with control_columns[0]:
    style = st.selectbox("Genre", GENRE_OPTIONS)
with control_columns[1]:
    mood = st.selectbox("Mood", MOOD_OPTIONS)
with control_columns[2]:
    tempo = st.number_input("Tempo", min_value=50, max_value=180, value=92, step=1, format="%d")
with control_columns[3]:
    instruments = st.selectbox("Palette", PALETTE_OPTIONS)
with control_columns[4]:
    duration = st.selectbox("Length", list(DURATION_SECONDS))

st.space("small")
generate = st.button("Generate Music  🎵", type="primary", width="stretch")

if generate:
    if not music_input.strip():
        st.warning("Add a musical idea before composing.")
    else:
        try:
            track = compose_track(music_input, style, mood, tempo, instruments, duration)
        except Exception as exc:  # noqa: BLE001 - surface API/audio failures in the UI
            st.error(f"Could not compose the piece: {exc}")
        else:
            st.session_state["current_track"] = track
            history = st.session_state.setdefault("history", [])
            history.insert(0, track)
            del history[MAX_HISTORY_TRACKS:]
            st.rerun()

track = st.session_state.get("current_track")
if track:
    st.markdown(
        '<div class="section-label">02 / Your latest composition</div>',
        unsafe_allow_html=True,
    )
    render_track_header("🎧", track, "READY TO PLAY")
    st.audio(BytesIO(track["audio"]), format="audio/wav")
    st.markdown(
        f'<div class="summary">{escape(str(track["summary"]))}</div>',
        unsafe_allow_html=True,
    )

render_history()
