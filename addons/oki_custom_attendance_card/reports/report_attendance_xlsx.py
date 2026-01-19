from odoo import models
from datetime import datetime

class AttendanceFormatXlsx(models.AbstractModel):
    _name = 'report.oki_custom_attendance_card.report_absensi_format'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, cards):
        sheet = workbook.add_worksheet('Rekap Absensi')
        sheet.freeze_panes(6, 4) # Kunci header
        
        # STYLE DEFINITION
        title_style = workbook.add_format({'bold': True, 'font_size': 14, 'font_name': 'Arial'})
        header_style = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'bg_color': '#4472C4', 'font_color': 'white', 'font_size': 10})
        dept_style = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'font_name': 'Arial'})
        cell_style = workbook.add_format({'align': 'center', 'border': 1, 'font_size': 9})
        name_style = workbook.add_format({'align': 'left', 'border': 1, 'font_size': 9})
        alpa_style = workbook.add_format({'align': 'center', 'border': 1, 'font_color': 'red', 'bold': True, 'font_size': 9})
        zebra_style = workbook.add_format({'align': 'center', 'border': 1, 'bg_color': '#F9F9F9', 'font_size': 9})

        # Judul Laporan
        sheet.merge_range('A1:G1', 'REKAPITULASI PRESENSI KARYAWAN', title_style)
        sheet.write(1, 0, f'PT Karyabhakti Manunggal - Mill 2', workbook.add_format({'bold': True}))
        sheet.write(2, 0, f'Tanggal Cetak: {datetime.now().strftime("%d/%m/%Y %H:%M")}', workbook.add_format({'italic': True, 'font_size': 8}))

        # Header Tabel
        headers = ['NO', 'ID REG', 'NAMA KARYAWAN', 'JABATAN']
        for i, h in enumerate(headers):
            sheet.merge_range(4, i, 5, i, h, header_style)

        if cards and cards[0].line_ids:
            col_date = 4
            for line in cards[0].line_ids:
                sheet.write(5, col_date, line.date.day, header_style)
                col_date += 1

        # Looping Data - Mendukung 1 orang atau Massal
        sorted_cards = cards.sorted(key=lambda r: (r.department_id.name or '', r.employee_id.name))
        current_dept = None
        row = 6
        no_urut = 1
        
        for obj in sorted_cards:
            # Tambah Header Departemen jika ganti departemen
            if obj.department_id != current_dept:
                current_dept = obj.department_id
                sheet.merge_range(row, 0, row, 3, f" DEPARTEMEN: {current_dept.name or 'N/A'}", dept_style)
                if cards[0].line_ids:
                    for c in range(4, 4 + len(cards[0].line_ids)):
                        sheet.write(row, c, "", dept_style)
                row += 1
                no_urut = 1
            
            # Baris Data
            style = zebra_style if no_urut % 2 == 0 else cell_style
            sheet.write(row, 0, no_urut, style)
            emp_id = getattr(obj.employee_id, 'barcode', '') or getattr(obj.employee_id, 'pin', '-')
            sheet.write(row, 1, emp_id, style)
            sheet.write(row, 2, obj.employee_id.name, name_style)
            sheet.write(row, 3, obj.employee_id.job_id.name or '-', name_style)
            
            col = 4
            for line in obj.line_ids:
                val = line.note if line.note else ("H" if line.check_in else "A")
                sheet.write(row, col, val, alpa_style if val == "A" else style)
                col += 1
            row += 1
            no_urut += 1
        
        sheet.set_column('B:B', 12)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 20)

class OvertimeFormatXlsx(models.AbstractModel):
    _name = 'report.oki_custom_attendance_card.report_overtime_format'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, cards):
        sheet = workbook.add_worksheet('Rekap Lembur')
        sheet.freeze_panes(4, 3)
        
        header_style = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'bg_color': '#70AD47', 'font_color': 'white'})
        num_style = workbook.add_format({'align': 'center', 'border': 1, 'font_size': 9})
        total_style = workbook.add_format({'bold': True, 'align': 'center', 'border': 1, 'bg_color': '#E2EFDA'})
        dept_style = workbook.add_format({'bold': True, 'bg_color': '#E2EFDA', 'border': 1})

        sheet.write(0, 0, 'LAPORAN LEMBUR KARYAWAN', workbook.add_format({'bold': True, 'font_size': 14}))
        sheet.write(1, 0, 'PT Karyabhakti Manunggal - Mill 2', workbook.add_format({'italic': True}))

        headers = ['ID REG', 'FULL NAME', 'JOB POSITION']
        for i, h in enumerate(headers):
            sheet.write(3, i, h, header_style)

        if cards and cards[0].line_ids:
            col_idx = 3
            for line in cards[0].line_ids:
                sheet.write(3, col_idx, line.date.day, header_style)
                col_idx += 1
            sheet.write(3, col_idx, 'TOTAL (HH:MM)', header_style)

        sorted_cards = cards.sorted(key=lambda r: (r.department_id.name or '', r.employee_id.name))
        current_dept = None
        row = 4
        
        for obj in sorted_cards:
            if obj.department_id != current_dept:
                current_dept = obj.department_id
                sheet.merge_range(row, 0, row, 2, f" UNIT: {current_dept.name or 'N/A'}", dept_style)
                row += 1
            
            emp_id = getattr(obj.employee_id, 'barcode', '') or getattr(obj.employee_id, 'pin', '-')
            sheet.write(row, 0, emp_id, num_style)
            sheet.write(row, 1, obj.employee_id.name, workbook.add_format({'border': 1, 'font_size': 9}))
            sheet.write(row, 2, obj.employee_id.job_id.name or '-', workbook.add_format({'border': 1, 'font_size': 9}))
            
            col = 3
            total_jam = 0
            for line in obj.line_ids:
                val = line.overtime_hours or 0
                sheet.write(row, col, val if val > 0 else '', num_style)
                total_jam += val
                col += 1
            
            hours = int(total_jam)
            minutes = int((total_jam - hours) * 60)
            sheet.write(row, col, f'{hours:02d}:{minutes:02d}', total_style)
            row += 1
            
        sheet.set_column('A:A', 12)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 20)