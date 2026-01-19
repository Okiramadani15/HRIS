{
    "name": "Oki - Kartu Absensi",
    "summary": "Kartu Absensi berbasis jadwal kerja dan attendance",
    "version": "18.0.1.0.0",
    "author": "Oki Ramadani",
    "category": "Human Resources",
    "depends": [
        "hr",
        "hr_attendance",
        "hr_holidays",  # Tambahkan ini agar bisa baca data Cuti/Sakit
        "report_xlsx"
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/attendance_card_wizard_views.xml", # URUTAN 1
        "views/attendance_card_views.xml",          # URUTAN 2
        "views/attendance_card_action.xml",         # URUTAN 3
        "views/menu.xml",                          # URUTAN 4 (Menu harus paling bawah)
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}