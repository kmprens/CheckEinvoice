# https://ebelge.gib.gov.tr/efaturakayitlikullanicilar.html

from requests    import Session
from shutil      import copyfileobj
from uuid        import uuid4
from os          import remove
from bs4         import BeautifulSoup
from PIL         import Image
from pytesseract import image_to_string

def e_fatura(vergi_numarasi:str | int) -> bool | None:
    """Vergi Numarasından E-Fatura Kontrolü Sağlama"""
    captcha_resmi = f"captcha_{uuid4()}.jpg"

    oturum = Session()

    captcha_istek = oturum.get("https://sorgu.efatura.gov.tr/kullanicilar/img.php", stream=True)
    with open(captcha_resmi, "wb") as file:
        copyfileobj(captcha_istek.raw, file)

    captcha_metni = image_to_string(Image.open(captcha_resmi))
    remove(captcha_resmi)

    e_fatura_istek = oturum.post(
        url     = "https://sorgu.efatura.gov.tr/kullanicilar/xliste.php",
        headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"},
        data    = {"search_string": f"{vergi_numarasi}", "captcha_code": f"{captcha_metni}"}
    )

    corba = BeautifulSoup(e_fatura_istek.text, features="html.parser")

    if corba.find("p", attrs={"style": "color:red;font-weight:bold"}):
        return False
    elif corba.find("div"):
        return True
    else:
        return None