import os
import re
import sqlite3
from pathlib import Path
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_PATH = os.getenv(
    "DB_PATH",
    "/data/bot_database.db"
)

STORAGE_ROOT = Path(
    os.getenv(
        "STORAGE_ROOT",
        "/data/storage"
    )
)

ADMIN_IDS = {
    6448008082,
    8791458947, 8881717605
}

# =========================================================
# BUTTONS
# =========================================================

THEORETICAL = "📚 Theoretical"
PRACTICAL = "🩺 Practical"

BACK = "⬅️ Back"
HOME = "🏠 Home"
DELETE = "🗑️ Delete File"

SECTION_NAMES = {
    THEORETICAL,
    PRACTICAL,
}

# =========================================================
# STRUCTURE
# =========================================================

STRUCTURE = {

    # =====================================================
    # LEVEL 1
    # =====================================================

    "🔴 Level 1": {

        "Semester 1": {

            "🦴 Anatomy I": {
                "type": "subject",
                "lab": True,
            },

            "🧪 Biochemistry I": {
                "type": "subject",
                "lab": False,
            },

            "🔬 Histology": {
                "type": "subject",
                "lab": True,
            },

            "🫀 Physiology I": {
                "type": "subject",
                "lab": True,
            },
        },

        "Semester 2": {

            "🦴 Anatomy II": {
                "type": "subject",
                "lab": True,
            },

            "🧪 Biochemistry II": {
                "type": "subject",
                "lab": False,
            },

            "🫀 Physiology II": {
                "type": "subject",
                "lab": True,
            },

            "🏃 Kinesiology I": {
                "type": "subject",
                "lab": True,
            },

            "⚡ Biophysics": {
                "type": "subject",
                "lab": True,
            },
        },
    },

    # =====================================================
    # LEVEL 2
    # =====================================================

    "🟠 Level 2": {

        "Semester 3": {

            "🧠 Neuroanatomy": {
                "type": "subject",
                "lab": True,
            },

            "🦾 Biomechanics II": {
                "type": "subject",
                "lab": False,
            },

            "⚡ Electrotherapy I": {
                "type": "subject",
                "lab": True,
            },

            "📋 Evaluation I": {
                "type": "subject",
                "lab": True,
            },

            "🧠 Neurophysiology": {
                "type": "subject",
                "lab": False,
            },

            "🏋️ Therapeutic Ex. I": {
                "type": "subject",
                "lab": True,
            },
        },

        "Semester 4": {

            "🦾 Biomechanics III": {
                "type": "subject",
                "lab": True,
            },

            "🩺 Community Health": {
                "type": "subject",
                "lab": False,
            },

            "📋 Evaluation II": {
                "type": "subject",
                "lab": True,
            },

            "🫀 Exercise Physiology": {
                "type": "subject",
                "lab": False,
            },

            "🔬 Pathology": {
                "type": "subject",
                "lab": False,
            },

            "👐 Manual Therapy": {
                "type": "subject",
                "lab": True,
            },

            "⚡ Electrotherapy II": {
                "type": "subject",
                "lab": True,
            },

            "🦴 Anatomy IV": {
                "type": "subject",
                "lab": True,
            },

            "⚖️ Legal & Ethics": {
                "type": "subject",
                "lab": False,
            },
        },
    },

    # =====================================================
    # LEVEL 3
    # =====================================================

    "🟡 Level 3": {

        "Semester 5": {

            "🦾 Biomechanics IV": {
                "type": "subject",
                "lab": True,
            },

            "🌊 Hydrotherapy": {
                "type": "subject",
                "lab": True,
            },

            "📊 Research & Statistics": {
                "type": "subject",
                "lab": False,
            },

            "💼 Management & Decision": {
                "type": "subject",
                "lab": False,
            },

            "🩺 Pathophysiology": {
                "type": "subject",
                "lab": False,
            },

            "💊 Pharmacology": {
                "type": "subject",
                "lab": False,
            },

            "♿ Rehabilitation": {
                "type": "subject",
                "lab": False,
            },
        },
    },

    # =====================================================
    # TRACKS
    # =====================================================

    "🟢 Tracks": {

        # =================================================
        # BATNA
        # =================================================

        "🫀 Batna Track": {

            '🫁 PH pulmonary "CAPU324"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🩺 Medicine pulmonary "MED.314PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '👴 Geriatric rehabilitation "CAPU326"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '❤️ PH cardio "CAPU322"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🫀 Medicine cardio "MED.312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🏥 Hospital "CAPU312+CAPU314"': {
                "type": "subject",
                "lecture": False,
                "lab": True,
            },

            '🥗 Nutrition "BIOC312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🩻 Radiology "RAD.312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🧠 Psychology "PSYCH 312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },
        },

        # =================================================
        # GYNA
        # =================================================

        "🤰 Gyna Track": {

            '🩹 First Aid "FIRS 411E"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🪑 Ergonomics "BIOM 411"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🔪 Ph Surgery "PT421 / SURG"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🏥 General Surgery "SURG.411"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🤰 Ph Gyna "GYPD 421PT"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🩺 Med Gyna "MED 411PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '📚 Evidence "PT.441"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🏥 Hospital Surgery "SURG PT411"': {
                "type": "subject",
                "lecture": False,
                "lab": True,
            },

            '🤰 Hospital Gyna "GYPD.411"': {
                "type": "subject",
                "lecture": False,
                "lab": True,
            },
        },

        # =================================================
        # ORTHO
        # =================================================

        "🦴 Ortho Track": {

            '🦴 PH "MUSK424"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🦿 Orthoses & Prosthesis': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🔎 Examination "MUSK422"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '⚽ Sport Physical Therapy': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🏥 Hospital "MUSK412"': {
                "type": "subject",
                "lecture": False,
                "lab": True,
            },

            '🔪 Surgery "SURGPT412"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🩺 Medicine "MED412PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🩻 Radiology "RAD.412PT"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },
        },

        # =================================================
        # NEURO
        # =================================================

        "🧠 Neuro Track": {

            '🧠 Topic "NEUR526"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🏃 Motor "PT541"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🩺 medicine "MED512PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🦴 spinal "NEUR524"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🧠 Neurosurgery "SURG512PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🧠 PH "NEUR.522"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '📈 EMG "NEUR.525"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🏥 Hospital "NEUR512" + Spinal sec': {
                "type": "subject",
                "lecture": False,
                "lab": True,
            },
        },

        # =================================================
        # PEDS
        # =================================================

        "👶 Peds Track": {

            '🏥 Hospital "GYPD 511"': {
                "type": "subject",
                "lecture": False,
                "lab": True,
            },

            '👶 Ph "GYPD 525"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🩺 Surgery "GYPD 527"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '👶 Motor development "GYPD 521"': {
                "type": "subject",
                "lecture": True,
                "lab": True,
            },

            '🗣️ Speech Therapy "GYPD 529"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '👐 Occupational Therapy "OT.511"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },

            '🩺 Medicine "MED.511PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False,
            },
        },
    },
}

# =========================================================
# DATABASE
# =========================================================

def get_db():
    Path(DB_PATH).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path_key TEXT NOT NULL,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(path_key, name)
        )
    """)

    conn.commit()

    return conn


# =========================================================
# HELPERS
# =========================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS


def make_path_key(path):
    return " / ".join(path)


def sanitize_filename(name):
    name = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        name,
    )

    name = name.strip().strip(".")

    if not name:
        return "file"

    return name


def storage_directory(path):
    directory = STORAGE_ROOT

    for part in path:
        directory = directory / sanitize_filename(part)

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


def get_node(path):
    node = STRUCTURE

    for part in path:

        # Theoretical / Practical are storage sections,
        # NOT navigation nodes.
        if part in SECTION_NAMES:
            continue

        if not isinstance(node, dict):
            return None

        if part not in node:
            return None

        node = node[part]

    return node


def get_files(path):
    conn = get_db()

    rows = conn.execute(
        """
        SELECT id, name, file_path, file_type
        FROM files
        WHERE path_key = ?
        ORDER BY id
        """,
        (make_path_key(path),),
    ).fetchall()

    conn.close()

    return rows


def file_exists(path, name):
    conn = get_db()

    row = conn.execute(
        """
        SELECT id
        FROM files
        WHERE path_key = ? AND name = ?
        """,
        (
            make_path_key(path),
            name,
        ),
    ).fetchone()

    conn.close()

    return row is not None


def add_file(
    path,
    name,
    file_path,
    file_type,
):
    conn = get_db()

    try:

        conn.execute(
            """
            INSERT INTO files
            (
                path_key,
                name,
                file_path,
                file_type,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                make_path_key(path),
                name,
                str(file_path),
                file_type,
                datetime.utcnow().isoformat(),
            ),
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def remove_file(file_id):
    conn = get_db()

    row = conn.execute(
        """
        SELECT file_path
        FROM files
        WHERE id = ?
        """,
        (file_id,),
    ).fetchone()

    if not row:
        conn.close()
        return False

    conn.execute(
        """
        DELETE FROM files
        WHERE id = ?
        """,
        (file_id,),
    )

    conn.commit()
    conn.close()

    try:
        Path(row[0]).unlink(
            missing_ok=True
        )
    except Exception:
        pass

    return True


def make_keyboard(rows):
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
    )


def pair_buttons(items):
    rows = []

    for i in range(
        0,
        len(items),
        2,
    ):
        rows.append(
            items[i:i + 2]
        )

    return rows


def format_subject_button(name):
    """
    If a subject contains a code in quotes,
    display it on a second line.

    Example:

    🫁 PH pulmonary
    "CAPU324"
    """

    match = re.match(
        r'^(.*?)\s+("[^"]+")$',
        name,
    )

    if match:

        subject_name = match.group(1)
        code = match.group(2)

        return (
            f"{subject_name}\n"
            f"{code}"
        )

    return name


def split_subject_title(name):
    match = re.match(
        r'^(.*?)\s+("[^"]+")$',
        name,
    )

    if match:

        return (
            f"{match.group(1)}\n"
            f"{match.group(2)}"
        )

    return name


def subject_sections(node):

    # Track subjects explicitly define lecture/lab.
    if "lecture" in node:

        lecture = node.get(
            "lecture",
            False,
        )

        lab = node.get(
            "lab",
            False,
        )

    else:

        # Normal subjects:
        # lecture is always available.
        lecture = True

        lab = node.get(
            "lab",
            False,
        )

    sections = []

    if lecture:
        sections.append(
            THEORETICAL
        )

    if lab:
        sections.append(
            PRACTICAL
        )

    return sections


# =========================================================
# HOME
# =========================================================

async def show_home(
    update,
    context,
):
    context.user_data.clear()

    context.user_data[
        "nav_path"
    ] = []

    context.user_data[
        "section"
    ] = None

    context.user_data[
        "delete_mode"
    ] = False

    items = list(
        STRUCTURE.keys()
    )

    rows = pair_buttons(items)

    if is_admin(
        update.effective_user.id
    ):
        rows.append(
            [DELETE]
        )

    await update.effective_message.reply_text(
        "🏠 Home",
        reply_markup=make_keyboard(rows),
    )


# =========================================================
# SHOW CURRENT LOCATION
# =========================================================

async def show_location(
    update,
    context,
):
    nav_path = context.user_data.get(
        "nav_path",
        [],
    )

    section = context.user_data.get(
        "section"
    )

    # =====================================================
    # INSIDE THEORETICAL / PRACTICAL
    # =====================================================

    if section:

        storage_path = (
            nav_path
            + [section]
        )

        files = get_files(
            storage_path
        )

        rows = []

        for _, name, _, _ in files:

            rows.append(
                [name]
            )

        if (
            is_admin(
                update.effective_user.id
            )
            and files
        ):
            rows.append(
                [DELETE]
            )

        # IMPORTANT:
        # Back returns directly to the subject.
        rows.append(
            [BACK, HOME]
        )

        if files:

            message = (
                f"{section}\n\n"
                "📂 Choose a file:"
            )

        else:

            message = (
                f"{section}\n\n"
                "📂 No files here yet."
            )

        await update.effective_message.reply_text
