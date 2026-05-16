# ======================================================
#   KỊCH BẢN ĐÓNG GÓI GNOC AUTO TOOL (DUY NHẤT 1 FILE EXE)
# ======================================================

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   DONG GOI THANH 1 FILE DUY NHAT (ONEFILE MODE)" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# 1. Cai dat/Cap nhat thu vien
Write-Host "[*] Dang chuan bi moi truong..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install pyinstaller playwright requests urllib3

# 2. Dong goi (Su dung --onefile)
Write-Host "[*] Dang dong goi. Vui long cho..." -ForegroundColor Yellow

python -m PyInstaller --noconfirm --onefile --console `
    --name "GNOC_Auto_Tool" `
    --collect-all playwright `
    --hidden-import playwright.sync_api `
    "gnoc_auto_report.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host "[THANH CONG] File EXE duy nhat da duoc tao tai: dist\GNOC_Auto_Tool.exe" -ForegroundColor Green
    Write-Host "Ban co the copy file nay đi bat cu dau (nho đe config.json ben canh)." -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Green
} else {
    Write-Host "[LOI] Co loi xay ra." -ForegroundColor Red
}

Read-Host "An Enter de ket thuc..."
