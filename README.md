# Proyek UAS Python for Cyber Security - SIEM

## Status Implementasi

Project ini masih dalam tahap pengembangan.

- SIEM server: selesai tahap awal
- Endpoint agent: belum dikonfigurasi
- Pengujian VM: belum dilakukan
- Screenshot dashboard dan event: belum dilengkapi
- Report dan log hasil pengujian: belum dilengkapi

## Deskripsi Project

Project ini mengembangkan aplikasi Security Information and Event Management (SIEM) menggunakan Python. SIEM server menerima event keamanan dari endpoint yang dimonitor, menyimpan event ke database SQLite, menganalisis event menggunakan rule sederhana, menghasilkan alert, dan menampilkan data melalui dashboard web.

## Arsitektur Sistem

Topologi yang digunakan sesuai requirement project:

- VM1 sebagai SIEM server
- VM2 sebagai endpoint yang dimonitor

Aliran data:

1. Endpoint agent membaca log dan aktivitas lokal pada VM2.
2. Agent mengklasifikasikan aktivitas menjadi event keamanan.
3. Agent mengirim event ke SIEM server melalui HTTP POST.
4. SIEM server menerima event melalui API `/api/events`.
5. Event disimpan ke database SQLite.
6. Rule engine menganalisis event dan menghasilkan alert jika cocok dengan rule.
7. Dashboard menampilkan event, alert, summary, dan filter.
8. Report dapat diekspor dalam bentuk CSV dan ringkasan teks.

## Teknologi

- Linux Server
- Python
- Flask
- SQLite
- Virtual Machine VirtualBox atau VMware

## Struktur Project

```text
.
├── database.sql
├── requirements.txt
├── README.md
└── server/
    ├── __init__.py
    ├── app.py
    ├── analyzer.py
    ├── config.py
    ├── database.py
    ├── repositories.py
    ├── routes.py
    └── templates.py
```

## SIEM Server

SIEM server memiliki fitur berikut:

- Menerima event keamanan dalam format JSON
- Menyimpan event ke database SQLite
- Menganalisis event menggunakan rule engine sederhana
- Menghasilkan alert berdasarkan tipe event
- Menampilkan dashboard web
- Menampilkan daftar event dan alert
- Menyediakan filter event berdasarkan hostname, event type, dan severity
- Mengekspor event ke CSV
- Mengekspor alert ke CSV
- Membuat ringkasan report dalam format teks

## Endpoint API

Endpoint untuk menerima event:

```text
POST /api/events
```

Contoh payload JSON:

```json
{
  "timestamp": "2026-06-17 10:00:00",
  "hostname": "endpoint-vm",
  "source": "auth.log",
  "event_type": "failed_ssh_login",
  "severity": "medium",
  "message": "Failed SSH login detected",
  "raw_log": "sshd: Failed password for invalid user test"
}
```

Field yang wajib dikirim:

- `timestamp`
- `hostname`
- `source`
- `event_type`
- `severity`
- `message`
- `raw_log`

## Detection Rule

Rule engine saat ini mendukung tipe event berikut:

| Event Type | Alert Type | Severity |
| --- | --- | --- |
| `failed_ssh_login` | Failed SSH Login | medium |
| `successful_ssh_login` | Successful SSH Login | low |
| `failed_sudo` | Failed Sudo Attempt | high |
| `user_created` | User Account Created | medium |
| `user_deleted` | User Account Deleted | medium |
| `package_installed` | Package Installed | low |
| `service_started` | Service Started | low |
| `service_stopped` | Service Stopped | high |
| `file_created` | File Created | low |
| `file_modified` | File Modified | medium |
| `file_deleted` | File Deleted | medium |
| `custom_app_log` dengan `ERROR` atau `WARNING` | Custom Application Error | medium |

## Desain Database

Database menggunakan SQLite dengan dua tabel utama.

### Tabel `events`

Menyimpan event yang diterima dari endpoint.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `timestamp` | TEXT | Waktu event |
| `hostname` | TEXT | Host endpoint |
| `source` | TEXT | Sumber log |
| `event_type` | TEXT | Jenis event |
| `severity` | TEXT | Tingkat severity |
| `message` | TEXT | Pesan event |
| `raw_log` | TEXT | Log asli |

### Tabel `alerts`

Menyimpan alert yang dihasilkan oleh rule engine.

| Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `event_id` | INTEGER | Referensi ke tabel events |
| `timestamp` | TEXT | Waktu alert dibuat |
| `alert_type` | TEXT | Jenis alert |
| `severity` | TEXT | Tingkat severity alert |
| `description` | TEXT | Deskripsi alert |

## Instalasi SIEM Server di Linux

Clone repository ke VM SIEM server:

```bash
git clone <repository-url>
cd <repository-folder>
```

Buat virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependency:

```bash
pip install -r requirements.txt
```

Jalankan SIEM server:

```bash
python server/app.py
```

Secara default aplikasi berjalan pada:

```text
http://0.0.0.0:5000
```

Dashboard dapat diakses dari browser melalui:

```text
http://<IP-SIEM-SERVER>:5000/dashboard
```

Konfigurasi opsional melalui environment variable:

```bash
SIEM_HOST=0.0.0.0 SIEM_PORT=5000 SIEM_DEBUG=0 python server/app.py
```

## Endpoint Agent

Endpoint agent belum dikonfigurasi pada tahap ini.

Rencana fitur agent:

- Membaca log `/var/log/auth.log` atau `/var/log/syslog`
- Mendeteksi penambahan baris log baru
- Mengklasifikasikan log menjadi event keamanan
- Memonitor perubahan file pada direktori tertentu
- Mengecek status service tertentu
- Mengirim event ke SIEM server melalui HTTP POST

## Skenario Pengujian

Skenario pengujian yang akan dilakukan setelah agent selesai dikonfigurasi:

1. Failed SSH login
2. Successful SSH login
3. Failed sudo attempt
4. User account creation/deletion
5. Package installation
6. Service stop/start
7. File creation/modification/deletion
8. Custom application log

## Output Report

Report dibuat melalui endpoint berikut:

```text
/export/events
/export/alerts
/report/summary
```

File report yang dihasilkan:

```text
reports/events.csv
reports/alerts.csv
reports/report_summary.txt
```

## Anggota Kelompok

Bagian ini akan dilengkapi dengan daftar anggota kelompok dan pembagian tugas.

| Nama | NIM | Tugas |
| --- | --- | --- |
|  |  |  |

## Catatan Pengembangan

README ini masih draft dan akan diperbarui setelah endpoint agent, pengujian VM, diagram, screenshot, dan report final selesai dibuat.
