FROM odoo:18.0

USER root

RUN pip3 install --no-cache-dir \
    pyzk \
    openupgradelib \
    --break-system-packages

USER odoo
