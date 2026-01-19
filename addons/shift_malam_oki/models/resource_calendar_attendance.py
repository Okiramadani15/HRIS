from odoo import models, fields

class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    # Menambahkan pilihan 'Malam' ke field day_period bawaan Odoo
    day_period = fields.Selection(
        selection_add=[('night', 'Malam')],
        ondelete={'night': 'set default'}
    )