import qrcode
from PIL import Image
import os
from pymongo import MongoClient

def make_qr(str, save):
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # L:7% M:15% Q:25% H:30%
        box_size=10,
        border=2,
    )
    qr.add_data(str)
    qr.make(fit=True)

    img = qr.make_image()
    img.save(save)



def make_logo_qr(str, logo, save):

    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=8,
        border=2
    )

    qr.add_data(str)

    qr.make(fit=True)

    img = qr.make_image()

    img = img.convert("RGBA")


    if logo and os.path.exists(logo):
        icon = Image.open(logo)

        img_w, img_h = img.size

        factor = 4
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)


        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)

        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)
        icon = icon.convert("RGBA")
        img.paste(icon, (w, h), icon)

    img.save(save)


if __name__ == '__main__':
    save_path = 'D:\\antchain.me\\static\\address\\'
    logo = 'logo.jpg'

    str = 'AZPM5rEeVnHrr5zyFWQB8FLJ3sr1D86nu5'
    db=MongoClient().antchain
    cur_address=db.Address.find({},{'address':1,'_id':-1})
    for ad in cur_address:
        make_qr(ad['address'],save_path+ad['address']+'.png')
    # make_qr(str,save_path)
    #make_logo_qr(str, logo, save_path)