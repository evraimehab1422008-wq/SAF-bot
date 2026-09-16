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
# SETTINGS
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


THEORETICAL = "📚 Theoretical"
PRACTICAL = "🩺 Practical"

BACK = "⬅️ Back"
HOME = "🏠 Home"

DELETE_FILE = "🗑️ Delete File"
CANCEL_DELETE = "❌ Cancel Delete"


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
                "lab": True
            },

            "🧪 Biochemistry I": {
                "type": "subject",
                "lab": False
            },

            "🔬 Histology": {
                "type": "subject",
                "lab": True
            },

            "🫀 Physiology I": {
                "type": "subject",
                "lab": True
            }
        },

        "Semester 2": {

            "🦴 Anatomy II": {
                "type": "subject",
                "lab": True
            },

            "🧪 Biochemistry II": {
                "type": "subject",
                "lab": False
            },

            "🫀 Physiology II": {
                "type": "subject",
                "lab": True
            },

            "🏃 Kinesiology I": {
                "type": "subject",
                "lab": True
            },

            "⚡ Biophysics": {
                "type": "subject",
                "lab": True
            }
        }
    },


    # =====================================================
    # LEVEL 2
    # =====================================================

    "🟠 Level 2": {

        "Semester 3": {

            "🧠 Neuroanatomy": {
                "type": "subject",
                "lab": True
            },

            "🦾 Biomechanics II": {
                "type": "subject",
                "lab": False
            },

            "⚡ Electrotherapy I": {
                "type": "subject",
                "lab": True
            },

            "📋 Evaluation I": {
                "type": "subject",
                "lab": True
            },

            "🧠 Neurophysiology": {
                "type": "subject",
                "lab": False
            },

            "🏋️ Therapeutic Ex. I": {
                "type": "subject",
                "lab": True
            }
        },

        "Semester 4": {

            "🦾 Biomechanics III": {
                "type": "subject",
                "lab": True
            },

            "🩺 Community Health": {
                "type": "subject",
                "lab": False
            },

            "📋 Evaluation II": {
                "type": "subject",
                "lab": True
            },

            "🫀 Exercise Physiology": {
                "type": "subject",
                "lab": False
            },

            "🔬 Pathology": {
                "type": "subject",
                "lab": False
            },

            "👐 Manual Therapy": {
                "type": "subject",
                "lab": True
            },

            "⚡ Electrotherapy II": {
                "type": "subject",
                "lab": True
            },

            "🦴 Anatomy IV": {
                "type": "subject",
                "lab": True
            },

            "⚖️ Legal & Ethics": {
                "type": "subject",
                "lab": False
            }
        }
    },


    # =====================================================
    # LEVEL 3
    # =====================================================

    "🟡 Level 3": {

        "Semester 5": {

            "🦾 Biomechanics IV": {
                "type": "subject",
                "lab": True
            },

            "🌊 Hydrotherapy": {
                "type": "subject",
                "lab": True
            },

            "📊 Research & Statistics": {
                "type": "subject",
                "lab": False
            },

            "💼 Management & Decision": {
                "type": "subject",
                "lab": False
            },

            "🩺 Pathophysiology": {
                "type": "subject",
                "lab": False
            },

            "💊 Pharmacology": {
                "type": "subject",
                "lab": False
            },

            "♿ Rehabilitation": {
                "type": "subject",
                "lab": False
            }
        }
    },


    # =====================================================
    # TRACKS
    # =====================================================

    "🟢 Tracks": {

        # =================================================
        # BATNA
        # =================================================

        "🫀 Batna Track": {

            'PH pulmonary "CAPU324"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Medicine pulmonary "MED.314PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Geriatric rehabilitation "CAPU326"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'PH cardio "CAPU322"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Medicine cardio "MED.312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Hospital "CAPU312+CAPU314"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            },

            'Nutrition "BIOC312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Radiology "RAD.312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Psychology "PSYCH 312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            }
        },


        # =================================================
        # GYNA
        # =================================================

        "🤰 Gyna Track": {

            'First Aid "FIRS 411E"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Ergonomics "BIOM 411"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Ph Surgery "PT421 / SURG"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'General Surgery "SURG.411"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Ph Gyna "GYPD 421PT"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Med Gyna "MED 411PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Evidence "PT.441"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Hospital Surgery "SURG PT411"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            },

            'Hospital Gyna "GYPD.411"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            }
        },


        # =================================================
        # ORTHO
        # =================================================

        "🦴 Ortho Track": {

            'PH "MUSK424"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            "Orthoses & Prosthesis": {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Examination "MUSK422"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            "Sport Physical Therapy": {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Hospital "MUSK412"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            },

            'Surgery "SURGPT412"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Medicine "MED412PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Radiology "RAD.412PT"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            }
        },


        # =================================================
        # NEURO
        # =================================================

        "🧠 Neuro Track": {

            'Topic "NEUR526"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Motor "PT541"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'medicine "MED512PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'spinal "NEUR524"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Neurosurgery "SURG512PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'PH "NEUR.522"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'EMG "NEUR.525"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Hospital "NEUR512" + Spinal sec': {
                "type": "subject",
                "lecture": False,
                "lab": True
            }
        },


        # =================================================
        # PEDS
        # =================================================

        "👶 Peds Track": {

            'Hospital "GYPD 511"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            },

            'Ph "GYPD 525"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Surgery "GYPD 527"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Motor development "GYPD 521"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Speech Therapy "GYPD 529"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Occupational Therapy "OT.511"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Medicine "MED.511PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            }
        }
    }
}


# =========================================================
# DATABASE
# =========================================================

def get_db():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

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
    conn.close()


# =========================================================
# HELPERS
# =========================================================

def is_admin(user_id):

    return user_id in ADMIN_IDS


def get_path_key(path):

    return " / ".join(path)


def sanitize_filename(filename):

    filename = filename.strip()

    filename = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        filename
    )

    filename = filename.rstrip(". ")

    if not filename:
        filename = "file"

    return filename


def get_current_node(path):

    node = STRUCTURE

    for part in path:

        if part in (
            THEORETICAL,
            PRACTICAL
        ):
            continue

        if not isinstance(node, dict):
            return None

        if part not in node:
            return None

        node = node[part]

    return node


def get_storage_directory(path):

    directory = STORAGE_ROOT

    for part in path:

        safe_part = sanitize_filename(part)

        directory = directory / safe_part

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return directory


def get_files_in_path(path):

    path_key = get_path_key(path)

    conn = get_db()

    rows = conn.execute(
        """
        SELECT *
        FROM files
        WHERE path_key = ?
        ORDER BY id ASC
        """,
        (path_key,)
    ).fetchall()

    conn.close()

    return rows


def get_file_by_name(path, filename):

    path_key = get_path_key(path)

    conn = get_db()

    row = conn.execute(
        """
        SELECT *
        FROM files
        WHERE path_key = ?
        AND name = ?
        """,
        (
            path_key,
            filename
        )
    ).fetchone()

    conn.close()

    return row


# =========================================================
# MENU
# =========================================================

async def send_menu(
    update,
    context,
    path=None,
    delete_mode=False
):

    if path is None:

        path = context.user_data.get(
            "path",
            []
        )

    context.user_data["path"] = path

    context.user_data["delete_mode"] = (
        delete_mode
    )

    node = get_current_node(path)

    if node is None:

        await update.message.reply_text(
            "❌ Invalid location."
        )

        return


    buttons = []


    # =====================================================
    # DELETE MODE
    # =====================================================

    if delete_mode:

        files = get_files_in_path(path)

        if not files:

            context.user_data[
                "delete_mode"
            ] = False

            await send_menu(
                update,
                context,
                path,
                False
            )

            return

        for file in files:

            buttons.append([
                file["name"]
            ])

        buttons.append([
            CANCEL_DELETE
        ])

        await update.message.reply_text(
            "🗑️ Choose the file you want to delete:",
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True
            )
        )

        return


    # =====================================================
    # SUBJECT
    # =====================================================

    if (
        isinstance(node, dict)
        and node.get("type") == "subject"
    ):

        lecture = node.get(
            "lecture",
            True
        )

        lab = node.get(
            "lab",
            False
        )

        subject_buttons = []


        if lecture:

            subject_buttons.append(
                THEORETICAL
            )


        if lab:

            subject_buttons.append(
                PRACTICAL
            )


        if len(subject_buttons) == 2:

            buttons.append([
                subject_buttons[0],
                subject_buttons[1]
            ])

        elif len(subject_buttons) == 1:

            buttons.append([
                subject_buttons[0]
            ])


    # =====================================================
    # NORMAL NAVIGATION
    # =====================================================

    else:

        if isinstance(node, dict):

            navigation_buttons = []

            for name, value in node.items():

                if isinstance(
                    value,
                    dict
                ):

                    navigation_buttons.append(
                        name
                    )


            # Two columns
            for i in range(
                0,
                len(navigation_buttons),
                2
            ):

                row = navigation_buttons[
                    i:i + 2
                ]

                buttons.append(row)


    # =====================================================
    # FILES
    # =====================================================

    files = get_files_in_path(path)

    for file in files:

        buttons.append([
            file["name"]
        ])


    # =====================================================
    # DELETE BUTTON
    # =====================================================

    if (
        is_admin(update.effective_user.id)
        and files
    ):

        buttons.append([
            DELETE_FILE
        ])


    # =====================================================
    # BACK + HOME
    # =====================================================

    if path:

        buttons.append([
            BACK,
            HOME
        ])


    # =====================================================
    # SEND MENU
    # =====================================================

    if path:

        title = (
            "📍 "
            + get_path_key(path)
        )

    else:

        title = "🏠 Home"


    await update.message.reply_text(
        "📚 PT Materials\n\n"
        + title,
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True
        )
    )


# =========================================================
# START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data["path"] = []

    context.user_data[
        "delete_mode"
    ] = False

    await update.message.reply_text(
        "👋 Welcome to PT Materials Bot!"
    )

    await send_menu(
        update,
        context,
        []
    )


# =========================================================
# SEND SAVED FILE
# =========================================================

async def send_saved_file(
    update,
    file
):

    file_path = file["file_path"]

    file_type = file["file_type"]


    if not os.path.exists(file_path):

        await update.message.reply_text(
            "❌ This file is no longer available."
        )

        return


    with open(
        file_path,
        "rb"
    ) as f:

        if file_type == "document":

            await update.message.reply_document(
                document=f,
                filename=file["name"]
            )


        elif file_type == "photo":

            await update.message.reply_photo(
                photo=f
            )


        elif file_type == "audio":

            await update.message.reply_audio(
                audio=f,
                filename=file["name"]
            )


        elif file_type == "voice":

            await update.message.reply_voice(
                voice=f
            )


# =========================================================
# MEDIA UPLOAD
# =========================================================

async def handle_media_upload(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "❌ Admins only."
        )

        return


    path = context.user_data.get(
        "path",
        []
    )


    # =====================================================
    # DOCUMENT
    # =====================================================

    if update.message.document:

        media = update.message.document

        filename = (
            media.file_name
            or "document"
        )

        file_type = "document"


    # =====================================================
    # PHOTO
    # =====================================================

    elif update.message.photo:

        media = update.message.photo[-1]

        filename = (
            "photo_"
            + media.file_unique_id
            + ".jpg"
        )

        file_type = "photo"


    # =====================================================
    # AUDIO
    # =====================================================

    elif update.message.audio:

        media = update.message.audio

        filename = (
            media.file_name
            or "audio"
        )

        file_type = "audio"


    # =====================================================
    # VOICE
    # =====================================================

    elif update.message.voice:

        media = update.message.voice

        filename = (
            "voice_"
            + media.file_unique_id
            + ".ogg"
        )

        file_type = "voice"


    else:

        return


    filename = sanitize_filename(
        filename
    )


    # =====================================================
    # DUPLICATE CHECK
    # =====================================================

    existing = get_file_by_name(
        path,
        filename
    )

    if existing:

        await update.message.reply_text(
            f'❌ File "{filename}" already exists in this location.'
        )

        return


    # =====================================================
    # STORAGE DIRECTORY
    # =====================================================

    directory = get_storage_directory(
        path
    )

    file_path = directory / filename


    if file_path.exists():

        await update.message.reply_text(
            f'❌ File "{filename}" already exists in this location.'
        )

        return


    # =====================================================
    # DOWNLOAD
    # =====================================================

    telegram_file = await media.get_file()

    await telegram_file.download_to_drive(
        custom_path=str(file_path)
    )


    # =====================================================
    # DATABASE
    # =====================================================

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
                get_path_key(path),
                filename,
                str(file_path),
                file_type,
                datetime.utcnow().isoformat()
            )
        )

        conn.commit()


    except sqlite3.IntegrityError:

        if file_path.exists():

            file_path.unlink()

        conn.close()

        await update.message.reply_text(
            f'❌ File "{filename}" already exists in this location.'
        )

        return


    conn.close()


    await update.message.reply_text(
        f'✅ "{filename}" uploaded successfully.'
    )


    await send_menu(
        update,
        context,
        path
    )


# =========================================================
# DELETE FILE
# =========================================================

def delete_file_record(
    path,
    filename
):

    path_key = get_path_key(path)

    conn = get_db()


    row = conn.execute(
        """
        SELECT *
        FROM files
        WHERE path_key = ?
        AND name = ?
        """,
        (
            path_key,
            filename
        )
    ).fetchone()


    if not row:

        conn.close()

        return False


    file_path = row["file_path"]


    conn.execute(
        """
        DELETE FROM files
        WHERE path_key = ?
        AND name = ?
        """,
        (
            path_key,
            filename
        )
    )


    conn.commit()

    conn.close()


    try:

        if os.path.exists(file_path):

            os.remove(file_path)

    except Exception:

        pass


    return True


# =========================================================
# MESSAGE HANDLER
# =========================================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = update.message.text

    path = context.user_data.get(
        "path",
        []
    )

    delete_mode = context.user_data.get(
        "delete_mode",
        False
    )

    user_id = update.effective_user.id


    # =====================================================
    # HOME
    # =====================================================

    if text == HOME:

        context.user_data["path"] = []

        context.user_data[
            "delete_mode"
        ] = False

        await send_menu(
            update,
            context,
            []
        )

        return


    # =====================================================
    # BACK
    # =====================================================

    if text == BACK:

        if path:

            new_path = path[:-1]

            context.user_data[
                "path"
            ] = new_path

            context.user_data[
                "delete_mode"
            ] = False

            await send_menu(
                update,
                context,
                new_path
            )

        return


    # =====================================================
    # CANCEL DELETE
    # =====================================================

    if text == CANCEL_DELETE:

        context.user_data[
            "delete_mode"
        ] = False

        await send_menu(
            update,
            context,
            path
        )

        return


    # =====================================================
    # DELETE FILE
    # =====================================================

    if text == DELETE_FILE:

        if not is_admin(user_id):

            return


        files = get_files_in_path(
            path
        )


        if not files:

            await update.message.reply_text(
                "❌ There are no files to delete here."
            )

            return


        context.user_data[
            "delete_mode"
        ] = True


        await send_menu(
            update,
            context,
            path,
            True
        )

        return


    # =====================================================
    # DELETE SELECTED FILE
    # =====================================================

    if delete_mode:

        if not is_admin(user_id):

            return


        row = get_file_by_name(
            path,
            text
        )


        if not row:

            await update.message.reply_text(
                "❌ File not found."
            )

            await send_menu(
                update,
                context,
                path,
                True
            )

            return


        success = delete_file_record(
            path,
            text
        )


        if success:

            context.user_data[
                "delete_mode"
            ] = False

            await update.message.reply_text(
                f'🗑️ "{text}" deleted successfully.'
            )

            await send_menu(
                update,
                context,
                path
            )

        return


    # =====================================================
    # THEORETICAL
    # =====================================================

    if text == THEORETICAL:

        node = get_current_node(
            path
        )


        if (
            not isinstance(node, dict)
            or node.get("type") != "subject"
            or not node.get(
                "lecture",
                True
            )
        ):

            await update.message.reply_text(
                "❌ Theoretical is not available here."
            )

            return


        new_path = (
            path
            + [THEORETICAL]
        )


        context.user_data[
            "path"
        ] = new_path


        await send_menu(
            update,
            context,
            new_path
        )

        return


    # =====================================================
    # PRACTICAL
    # =====================================================

    if text == PRACTICAL:

        node = get_current_node(
            path
        )


        if (
            not isinstance(node, dict)
            or node.get("type") != "subject"
            or not node.get(
                "lab",
                False
            )
        ):

            await update.message.reply_text(
                "❌ Practical is not available here."
            )

            return


        new_path = (
            path
            + [PRACTICAL]
        )


        context.user_data[
            "path"
        ] = new_path


        await send_menu(
            update,
            context,
            new_path
        )

        return


    # =====================================================
    # FILE SELECTION
    # =====================================================

    file = get_file_by_name(
        path,
        text
    )


    if file:

        await send_saved_file(
            update,
            file
        )

        return


    # =====================================================
    # NORMAL NAVIGATION
    # =====================================================

    node = get_current_node(
        path
    )


    if (
        isinstance(node, dict)
        and text in node
    ):

        value = node[text]


        if isinstance(
            value,
            dict
        ):

            new_path = (
                path
                + [text]
            )


            context.user_data[
                "path"
            ] = new_path


            await send_menu(
                update,
                context,
                new_path
            )

            return


    # =====================================================
    # UNKNOWN BUTTON
    # =====================================================

    await update.message.reply_text(
        "❌ Please choose an option from the menu."
    )


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    print(
        "ERROR:",
        repr(context.error)
    )


# =========================================================
# MAIN
# =========================================================

def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN is not set."
        )


    # =====================================================
    # CREATE DIRECTORIES
    # =====================================================

    Path(
        DB_PATH
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )


    STORAGE_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )


    # =====================================================
    # DATABASE
    # =====================================================

    init_db()


    # =====================================================
    # APPLICATION
    # =====================================================

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )


    # =====================================================
    # START
    # =====================================================

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    # =====================================================
    # MEDIA
    # =====================================================

    app.add_handler(
        MessageHandler(
            filters.Document.ALL
            | filters.PHOTO
            | filters.AUDIO
            | filters.VOICE,
            handle_media_upload
        )
    )


    # =====================================================
    # TEXT
    # =====================================================

    app.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            handle_message
        )
    )


    # =====================================================
    # ERRORS
    # =====================================================

    app.add_error_handler(
        error_handler
    )


    # =====================================================
    # START BOT
    # =====================================================

    print(
        "PT MATERIALS BOT STARTING"
    )

    print(
        "BOT IS RUNNING..."
    )


    app.run_polling(
        drop_pending_updates=True
    )


# =========================================================
# PROGRAM ENTRY
# =========================================================

if __name__ == "__main__":
    main()
