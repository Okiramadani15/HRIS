from odoo import models

class AttendanceCardXlsx(models.AbstractModel):
    _name = 'report.oki_custom_attendance_card.report_attendance_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, cards):
        for obj in cards:
            sheet = workbook.add_worksheet(obj.employee_id.name[:31] if obj.employee_id else 'Report')
            bold = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#D3D3D3', 'align': 'center'})
            date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
            num_format = workbook.add_format({'num_format': '0.00', 'border': 1})
            border = workbook.add_format({'border': 1})

            sheet.set_column(0, 6, 18)

            sheet.write(0, 0, 'Reference', bold)
            sheet.write(0, 1, obj.name or '-')
            sheet.write(1, 0, 'Employee', bold)
            sheet.write(1, 1, obj.employee_id.name if obj.employee_id else '-')

            row = 3
            headers = ['Tanggal', 'Masuk', 'Pulang', 'Jam Kerja', 'Terlambat', 'SPL (Sistem)', 'Keterangan']
            for col, title in enumerate(headers):
                sheet.write(row, col, title, bold)

            row += 1
            for line in obj.line_ids:
                sheet.write(row, 0, line.date, date_format)
                sheet.write(row, 1, line.check_in.astimezone(pytz.timezone('Asia/Jakarta')).strftime('%H:%M') if line.check_in else '-', border)
                sheet.write(row, 2, line.check_out.astimezone(pytz.timezone('Asia/Jakarta')).strftime('%H:%M') if line.check_out else '-', border)
                sheet.write(row, 3, line.worked_hours, num_format)
                sheet.write(row, 4, line.late_minutes, num_format)
                sheet.write(row, 5, line.overtime_sys, num_format)
                sheet.write(row, 6, line.note or '', border)
                row += 1