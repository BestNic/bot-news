import telebot
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
import os

# =========================
# TOKEN DA RAILWAY
# =========================
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)
# =========================
# ESTRAZIONE DATI DAL LINK
# =========================
def extract_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # ===== TITOLO =====
        title = soup.title.string if soup.title else "Notizia importante"
        title = title.split("-")[0].split("|")[0].strip()

        # ===== DESCRIZIONE LUNGA =====
        paragraphs = soup.find_all("p")
        desc_list = []

        for p in paragraphs:
            text = p.get_text(separator=" ").strip()

# rimuove caratteri strani
text = text.encode("utf-8", "ignore").decode("utf-8")

# pulizia simboli brutti
bad_chars = [" ", "□", "\\xa0"]

for c in bad_chars:
    text = text.replace(c, "")

# evita spazi doppi
text = " ".join(text.split())

            if "javascript" in text.lower():
    continue

if "loading" in text.lower():
    continue

if "advertisement" in text.lower():
    continue
            if "cookie" in text.lower():
                continue

            if "pubblicità" in text.lower():
                continue

            desc_list.append(text)

            # prende fino a 10 paragrafi
            if len(desc_list) >= 10:
                break

        desc = "\n\n".join(desc_list[:5])

        if len(desc) < 100:
            desc = (
                "Non sono disponibili molti dettagli, "
                "ma la notizia è in aggiornamento."
            )

        # ===== IMMAGINE =====
        img_tag = soup.find("meta", property="og:image")

        if img_tag:
            img_url = img_tag["content"]
        else:
            img_url = "https://picsum.photos/1080/1350"

        return title, desc, img_url

    except Exception as e:
        print(e)

        return (
            "Notizia importante",
            "Errore nel recupero della notizia",
            "https://picsum.photos/1080/1350"
        )

# =========================
# CREA IMMAGINE NEWS PRO
# =========================
def create_image(title, img_url):

    try:
        response = requests.get(img_url)
        base_img = Image.open(BytesIO(response.content)).convert("RGB")

    except:
        base_img = Image.new(
            "RGB",
            (1080, 1000),
            color=(30, 30, 30)
        )

    # ===== TELA NERA =====
    final_img = Image.new(
        "RGB",
        (1080, 1350),
        (0, 0, 0)
    )

    # ===== IMMAGINE =====
    base_img = base_img.resize((1040, 1000))

    x_img = (1080 - 1040) // 2
    y_img = 80

    final_img.paste(base_img, (x_img, y_img))

    draw = ImageDraw.Draw(final_img)

    # ===== OVERLAY =====
    overlay = Image.new(
        'RGBA',
        (1040, 1000),
        (0, 0, 0, 70)
    )

    final_img.paste(
        overlay,
        (x_img, y_img),
        overlay
    )

    # ===== FONT =====
  font = ImageFont.truetype("arialbd.ttf", 64)

    except:
        font = ImageFont.load_default()

    # ===== TESTO =====
    title = title.upper()

 wrapped = textwrap.fill(title, width=20)

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped,
        font=font
    )

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x_text = (1080 - text_w) // 2
    y_text = y_img + 720

    # ===== BOX NEWS =====
    padding = 20

    box_x1 = x_text - padding
    box_y1 = y_text - padding
    box_x2 = x_text + text_w + padding
    box_y2 = y_text + text_h + padding

    # sfondo box
    box_bg = Image.new(
        'RGBA',
        (
            box_x2 - box_x1,
            box_y2 - box_y1
        ),
        (0, 0, 0, 160)
    )

    final_img.paste(
        box_bg,
        (box_x1, box_y1),
        box_bg
    )

    # bordo box
    draw.rectangle(
        [
            box_x1,
            box_y1,
            box_x2,
            box_y2
        ],
        outline="white",
        width=3
    )

    # ===== TESTO =====
    draw.multiline_text(
        (x_text, y_text),
        wrapped,
        font=font,
        fill=(255, 255, 255)
    )

    # ===== LOGO =====
    try:
        logo = Image.open("logo.png").convert("RGBA")

        logo_size = 90

        logo = logo.resize(
            (logo_size, logo_size)
        )

        logo_x = x_img + 1040 - logo_size - 15
        logo_y = y_img + 15

        final_img.paste(
            logo,
            (logo_x, logo_y),
            logo
        )

    except:
        pass

    # ===== SALVA =====
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

    # ===== FOTO =====
    bot.send_photo(
        message.chat.id,
        img
    )

    # ===== TESTO =====
    bot.send_message(
        message.chat.id,
        f"📰 {title}\n\n{desc}"
    )

# =========================
# AVVIO BOT
# =========================
print("Bot avviato...")

bot.infinity_polling(
    timeout=60,
    long_polling_timeout=60
)
