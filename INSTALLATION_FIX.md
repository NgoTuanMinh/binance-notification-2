# 🔧 Installation Troubleshooting

## ❌ Lỗi thường gặp

### 1. SSL Certificate Error (macOS)

**Lỗi:**
```
SSLError(SSLCertVerificationError('OSStatus -26276'))
```

**Nguyên nhân:** Python trên macOS không có SSL certificates

**Giải pháp:**

#### Option A: Cài đặt certificates (Khuyến nghị)

```bash
# Tìm folder Python của bạn
ls /Applications/Python*

# Chạy script cài đặt certificates (thay Python version của bạn)
/Applications/Python\ 3.11/Install\ Certificates.command

# Hoặc
/Applications/Python\ 3.12/Install\ Certificates.command
```

#### Option B: Bypass SSL verification (Tạm thời)

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

#### Option C: Upgrade pip và setuptools

```bash
pip install --upgrade pip setuptools
```

---

### 2. pandas-ta Version Error

**Lỗi:**
```
ERROR: No matching distribution found for pandas-ta>=0.3.14b0
```

**Giải pháp:** Đã sửa trong `requirements.txt`

Nếu vẫn lỗi, cài thủ công:

```bash
pip install pandas-ta==0.3.14b
# Hoặc
pip install pandas-ta
```

---

### 3. Permission Error

**Lỗi:**
```
PermissionError: [Errno 13] Permission denied
```

**Giải pháp:**

```bash
# Option 1: User install
pip install --user -r requirements.txt

# Option 2: Virtual environment (Khuyến nghị)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ✅ Cách cài đặt đúng (Step by step)

### Bước 1: Fix SSL (nếu cần)

```bash
# Check Python version
python3 --version

# Cài certificates
ls /Applications/Python*
/Applications/Python\ 3.XX/Install\ Certificates.command
```

### Bước 2: Tạo virtual environment (Khuyến nghị)

```bash
cd "/Users/tuanminh/Airdrop tool/Binance-2"

# Tạo venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Bước 3: Cài đặt packages

```bash
# Cài từ requirements
pip install -r requirements.txt

# Nếu vẫn lỗi SSL, dùng:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Bước 4: Verify installation

```bash
python -c "import ccxt, pandas, pandas_ta, aiohttp; print('✅ All packages installed')"
```

---

## 🐍 Alternative: Install packages riêng lẻ

Nếu requirements.txt không work, cài từng package:

```bash
pip install ccxt
pip install pandas
pip install pandas-ta
pip install python-dotenv
pip install aiohttp
pip install numpy
```

---

## 🔍 Check installed packages

```bash
pip list | grep -E "ccxt|pandas|aiohttp|dotenv"
```

Expected output:
```
ccxt                 4.2.x
pandas               2.0.x
pandas-ta            0.3.14b
python-dotenv        1.0.x
aiohttp              3.9.x
```

---

## 💡 Tips

### Sử dụng Virtual Environment

**Tại sao cần venv?**
- ✅ Tránh conflict với system packages
- ✅ Dễ dàng cleanup
- ✅ Portable

**Cách dùng:**

```bash
# Tạo (chỉ 1 lần)
python3 -m venv venv

# Activate (mỗi lần mở terminal mới)
source venv/bin/activate

# Khi activate, prompt sẽ có (venv)
(venv) user@mac Binance-2 %

# Deactivate (khi muốn thoát)
deactivate
```

### Check Python version

```bash
python3 --version
# Cần Python 3.8 trở lên
```

### Update pip

```bash
pip install --upgrade pip
```

---

## 🆘 Vẫn không work?

### Option 1: Sử dụng Anaconda/Miniconda

```bash
# Download Miniconda
# https://docs.conda.io/en/latest/miniconda.html

# Tạo environment
conda create -n binance-bot python=3.11
conda activate binance-bot

# Cài packages
conda install -c conda-forge ccxt pandas python-dotenv aiohttp
pip install pandas-ta
```

### Option 2: Docker

```bash
# Build image
docker build -t binance-bot .

# Run
docker run -it --env-file .env binance-bot
```

(Cần tạo Dockerfile - xem DEPLOYMENT.md)

---

## 📞 Contact Support

Nếu vẫn gặp vấn đề:

1. Check Python version: `python3 --version`
2. Check pip version: `pip --version`
3. Check OS: `sw_vers` (macOS) hoặc `uname -a` (Linux)
4. Share error message đầy đủ

---

## ✅ Verification Script

Tạo file `test_imports.py`:

```python
#!/usr/bin/env python3
"""Test if all required packages are installed."""

def test_imports():
    errors = []
    
    try:
        import ccxt
        print(f"✅ ccxt {ccxt.__version__}")
    except ImportError as e:
        errors.append(f"❌ ccxt: {e}")
    
    try:
        import pandas as pd
        print(f"✅ pandas {pd.__version__}")
    except ImportError as e:
        errors.append(f"❌ pandas: {e}")
    
    try:
        import pandas_ta as ta
        print(f"✅ pandas_ta (version check skipped)")
    except ImportError as e:
        errors.append(f"❌ pandas_ta: {e}")
    
    try:
        import aiohttp
        print(f"✅ aiohttp {aiohttp.__version__}")
    except ImportError as e:
        errors.append(f"❌ aiohttp: {e}")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv")
    except ImportError as e:
        errors.append(f"❌ python-dotenv: {e}")
    
    try:
        import numpy as np
        print(f"✅ numpy {np.__version__}")
    except ImportError as e:
        errors.append(f"❌ numpy: {e}")
    
    if errors:
        print("\n❌ Errors found:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("\n🎉 All packages installed successfully!")
        return True

if __name__ == "__main__":
    test_imports()
```

Chạy:
```bash
python test_imports.py
```

---

**Good luck! 🚀**
