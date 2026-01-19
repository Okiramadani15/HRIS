from odoo import models, fields, api

class HrOvertimePolicy(models.AbstractModel):
    _name = 'hr.overtime.policy'
    _description = 'Logika Kebijakan Lembur URD'

    @api.model
    def apply_urd_rounding(self, duration_hours):
        total_minutes = duration_hours * 60
        if total_minutes < 30:
            return 0.0
        # Bulatkan ke bawah per 30 menit
        rounded_minutes = (total_minutes // 30) * 30
        return rounded_minutes / 60.0