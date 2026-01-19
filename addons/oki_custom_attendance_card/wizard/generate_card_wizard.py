from odoo import models, fields, api
from datetime import date

class OkiGenerateAttendanceCardWizard(models.TransientModel):
    _name = 'oki.attendance.card.generate.wizard'
    _description = 'Oki Generate Attendance Card Wizard'

    employee_ids = fields.Many2many(
        'hr.employee',
        string='Karyawan',
        required=True
    )

    date_from = fields.Date(
        string='Dari Tanggal',
        required=True,
        default=lambda self: date.today().replace(day=1)
    )

    date_to = fields.Date(
        string='Sampai Tanggal',
        required=True,
        default=lambda self: date.today()
    )

    def action_generate_card(self):
        """
        Generate kartu absensi dan tampilkan di list view
        """
        AttendanceCard = self.env['oki.attendance.card']
        cards = AttendanceCard.browse()

        for emp in self.employee_ids:
            card = AttendanceCard.create({
                'employee_id': emp.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
            # Langsung panggil fungsi generate detail agar data terisi (worked_hours, lembur, dll)
            card.action_generate_lines()
            cards |= card

        return {
            'type': 'ir.actions.act_window',
            'name': 'Kartu Absensi Terbentuk',
            'res_model': 'oki.attendance.card',
            'view_mode': 'list,form',
            'domain': [('id', 'in', cards.ids)],
            'target': 'current',
        }

    def action_generate_and_print(self):
        """
        Generate kartu absensi dan LANGSUNG download Excel
        """
        AttendanceCard = self.env['oki.attendance.card']
        cards = AttendanceCard.browse()

        for emp in self.employee_ids:
            card = AttendanceCard.create({
                'employee_id': emp.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
            })
            card.action_generate_lines()
            cards |= card
        
        # Mengarahkan langsung ke action report Excel yang sudah kita buat di XML
        return self.env.ref('oki_custom_attendance_card.action_report_attendance_xlsx').report_action(cards)