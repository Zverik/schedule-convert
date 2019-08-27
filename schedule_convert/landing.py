import os
import qrcode

try:
    from PIL import Image
    import qrcode.image.pil
    QR_FACTORY = qrcode.image.pil.PilImage
    QR_EXT = 'png'
except ImportError:
    import qrcode.image.svg
    QR_FACTORY = qrcode.image.svg.SvgPathImage
    QR_EXT = 'svg'


def make_schedule_name(path, base, ext):
    os.makedirs(path, exist_ok=True)
    basename = base[base.rindex('/')+1:]
    return os.path.join(path, basename+'.'+ext)


def make_qr(url):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(image_factory=QR_FACTORY)


def make_landing_page(conf, path, base):
    GIGGITY_URL = 'https://play.google.com/store/apps/details?id=net.gaast.giggity'
    template = open(os.path.join(os.path.dirname(__file__), 'landing_template.html'), 'r').read()
    var = {
        'xml': base + '.xml',
        'ics': base + '.ics',
        'xml_qr': base + '.xml.' + QR_EXT,
        'ics_qr': base + '.ics.' + QR_EXT,
        'giggity': GIGGITY_URL,
        'giggity_qr': base[:base.rindex('/')+1] + 'giggity.' + QR_EXT,
        'title': conf.title,
        'url': conf.url or '#',
    }
    for k, v in var.items():
        template = template.replace('{'+k+'}', v)
    with open(make_schedule_name(path, base, 'html'), 'w') as f:
        f.write(template)
    with open(make_schedule_name(path, base, 'xml.' + QR_EXT), 'wb') as f:
        make_qr(base + '.xml').save(f)
    with open(make_schedule_name(path, base, 'ics.' + QR_EXT), 'wb') as f:
        make_qr(base + '.ics').save(f)
    with open(os.path.join(path, 'giggity.' + QR_EXT), 'wb') as f:
        make_qr(GIGGITY_URL).save(f)
