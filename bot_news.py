import telebot
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
import os

# =========================
# TOKEN RAILWAY
# =========================
TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

# =========================
# ESTRAZIONE DATI
# =========================
def extract_data(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(r.text, "html.parser")

        # =========================
        # TITOLO
        # =========================
        title = soup.title.string if soup.title else "ULTIMA ORA"

        title = (
            title
            .replace("\n", "")
            .replace("\t", "")
            .split("-")[0]
            .split("|")[0]
            .strip()
        )

        # evita titoli troppo lunghi
        if len(title) > 120:
            title = title[:120] + "..."

        # =========================
        # DESCRIZIONE
        # =========================
        paragraphs = soup.find_all("p")

        desc_list = []

        for p in paragraphs:

            text = p.get_text(separator=" ").strip()

            # pulizia caratteri
            text = text.encode(
                "utf-8",
                "ignore"
            ).decode("utf-8")

            bad_chars = [
                "�",
                "□",
                "\\xa0",
                "Â",
                "â"
            ]

            for c in bad_chars:
                text = text.replace(c, "")

            text = " ".join(text.split())

            # filtri
            if len(text) < 70:
                continue

            if "cookie" in text.lower():
                continue

            if "javascript" in text.lower():
                continue

            if "advertisement" in text.lower():
                continue

            if "pubblicità" in text.lower():
                continue

            if "loading" in text.lower():
                continue

            desc_list.append(text)

            if len(desc_list) >= 5:
                break

        desc = "\n\n".join(desc_list)

        # fallback
        if len(desc) < 120:
            desc = (
                "La notizia è in aggiornamento. "
                "Seguiranno ulteriori dettagli "
                "nelle prossime ore."
            )

        # =========================
        # IMMAGINE
        # =========================
        img_tag = soup.find(
            "meta",
            property="og:image"
        )

        if img_tag:
            img_url = img_tag["content"]
        else:
            img_url = "https://picsum.photos/1080/1350"

        return title, desc, img_url

    except Exception as e:

        print(e)

        return (
            "ULTIMA ORA",
            "Errore nel recupero della notizia.",
            "https://picsum.photos/1080/1350"
        )

# =========================
# CREA IMMAGINE
# =========================
def create_image(title, img_url):

    try:

        response = requests.get(
            img_url,
            timeout=10
        )

        base_img = Image.open(
            BytesIO(response.content)
        ).convert("RGB")

    except:

        base_img = Image.new(
            "RGB",
            (1080, 1000),
            color=(20, 20, 20)
        )

    # =========================
    # TELA FINALE
    # =========================
    final_img = Image.new(
        "RGB",
        (1080, 1350),
        (0, 0, 0)
    )

    # =========================
    # IMMAGINE
    # =========================
    base_img = base_img.resize((1040, 1000))

    x_img = 20
    y_img = 80

    final_img.paste(
        base_img,
        (x_img, y_img)
    )

    # =========================
    # OVERLAY SCURO
    # =========================
    overlay = Image.new(
        "RGBA",
        (1040, 1000),
        (0, 0, 0, 85)
    )

    final_img.paste(
        overlay,
        (x_img, y_img),
        overlay
    )

    draw = ImageDraw.Draw(final_img)

    # =========================
    # FONT GRANDE
    # =========================
    try:

        font = ImageFont.truetype(
            "arialbd.ttf",
            82
        )

    except:

        font = ImageFont.load_default()

    # =========================
    # TESTO
    # =========================
    title = title.upper()

    wrapped = textwrap.fill(
        title,
        width=16
    )

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped,
        font=font,
        spacing=15
    )

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x_text = (1080 - text_w) // 2
    y_text = 690

    # =========================
    # BOX TESTO
    # =========================
    padding_x = 40
    padding_y = 30

    box_x1 = x_text - padding_x
    box_y1 = y_text - padding_y

    box_x2 = x_text + text_w + padding_x
    box_y2 = y_text + text_h + padding_y

    # sfondo nero elegante
    box_bg = Image.new(
        "RGBA",
        (
            box_x2 - box_x1,
            box_y2 - box_y1
        ),
        (0, 0, 0, 185)
    )

    final_img.paste(
        box_bg,
        (box_x1, box_y1),
        box_bg
    )

    # bordo bianco
    draw.rectangle(
        [
            box_x1,
            box_y1,
            box_x2,
            box_y2
        ],
        outline="white",
        width=5
    )

    # =========================
    # TESTO FINALE
    # =========================
    draw.multiline_text(
        (x_text, y_text),
        wrapped,
        font=font,
        fill=(255, 255, 255),
        spacing=15,
        align="center"
    )

    # =========================
    # LOGO
    # =========================
    try:

        logo = Image.open(
            "logo.png"
        ).convert("RGBA")

        logo_size = 100

        logo = logo.resize(
            (logo_size, logo_size)
        )

        logo_x = 920
        logo_y = 100

        final_img.paste(
            logo,
            (logo_x, logo_y),
            logo
        )

    except:
        pass

    # =========================
    # SALVA
    # =========================
    output = BytesIO()

    final_img.save(
        output,
        format="JPEG",
        quality=95
    )

    output.seek(0)

    return output

# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):

    bot.reply_to(
        message,
        "🔥 Mandami il link di una notizia"
    )

# =========================
# RICEZIONE LINK
# =========================
@bot.message_handler(
    func=lambda message: message.text.startswith("http")
)
def news(message):

    bot.reply_to(
        message,
        "🔎 Creo la notizia..."
    )

    title, desc, img_url = extract_data(
        message.text
    )

    img = create_image(
        title,
        img_url
    )

    # FOTO
    bot.send_photo(
        message.chat.id,
        img
    )

    # TESTO
    bot.send_message(
        message.chat.id,
        f"📰 {title}\n\n{desc}"
    )

# =========================
# AVVIO
# =========================
print("Bot avviato...")

bot.infinity_polling(
    timeout=60,
    long_polling_timeout=60
)
