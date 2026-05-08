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
            color=(25, 25, 25)
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
        (0, 0, 0, 110)
    )

    final_img.paste(
        overlay,
        (x_img, y_img),
        overlay
    )

    draw = ImageDraw.Draw(final_img)

    # =========================
    # FONT ENORME
    # =========================
    try:

        font = ImageFont.truetype(
            "arialbd.ttf",
            110
        )

    except:

        font = ImageFont.load_default()

    # =========================
    # TESTO
    # =========================
    title = title.upper()

    wrapped = textwrap.fill(
        title,
        width=12
    )

    # =========================
    # CALCOLO TESTO
    # =========================
    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped,
        font=font,
        spacing=20
    )

    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x_text = (1080 - text_w) // 2
    y_text = 620

    # =========================
    # BOX NEWS
    # =========================
    padding_x = 50
    padding_y = 40

    box_x1 = x_text - padding_x
    box_y1 = y_text - padding_y

    box_x2 = x_text + text_w + padding_x
    box_y2 = y_text + text_h + padding_y

    # sfondo
    box_bg = Image.new(
        "RGBA",
        (
            box_x2 - box_x1,
            box_y2 - box_y1
        ),
        (0, 0, 0, 200)
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
        width=6
    )

    # =========================
    # TESTO BIANCO
    # =========================
    draw.multiline_text(
        (x_text, y_text),
        wrapped,
        font=font,
        fill=(255, 255, 255),
        spacing=20,
        align="center"
    )

    # =========================
    # LOGO
    # =========================
    try:

        logo = Image.open(
            "logo.png"
        ).convert("RGBA")

        logo_size = 110

        logo = logo.resize(
            (logo_size, logo_size)
        )

        logo_x = 900
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
