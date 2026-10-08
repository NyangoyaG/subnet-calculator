# 🌐 AI-Powered IPv4 Subnet Calculator

A professional, web-based IPv4 subnet calculator that answers all 7 essential subnetting questions instantly.

**Live Demo:** (https://subnet-calculator-pggw.onrender.com/)
![Subnet Calculator UI](subnet%20calculator.png)

---

## 📋 Table of Contents
- [About](#about)
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Deployment](#deployment)
- [API Usage](#api-usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## 📖 About

This subnet calculator answers the 7 most common subnetting questions instantly:

1. Number of subnets
2. Number of usable hosts
3. First usable IP
4. Last usable IP
5. Broadcast IP
6. Network IP
7. Wildcard mask

Built with Flask and deployed on PythonAnywhere.

---

## ✨ Features

- ✅ **CIDR Notation** - Enter IPs as `192.168.34.221/27`
- ✅ **Class Detection** - Auto-detects Class A, B, or C
- ✅ **Batch Processing** - Calculate multiple IPs at once
- ✅ **RESTful API** - Programmatic access
- ✅ **Mobile Responsive** - Works on all devices
- ✅ **Free** - No registration required

---

## 🎓 How It Works

### Formulas Used:

| Formula | Description |
|---------|-------------|
| **Block Size = 2^(NB-NM)** | Calculate subnet block size |
| **Subnets = 2^(NM-CB)** | Calculate total subnets |
| **Usable Hosts = 2^(32-NM) - 2** | Calculate usable addresses |

### Example:

**Input:** `192.168.34.221/27`

**Results:**
- Network: `192.168.34.192`
- First Usable: `192.168.34.193`
- Last Usable: `192.168.34.222`
- Broadcast: `192.168.34.223`
- Usable Hosts: **30**
- Subnets: **8**
- Wildcard: `0.0.0.31`

---

## 💻 Installation

### Prerequisites
- Python 3.10+
- Git
- pip

### Steps:

```bash
# 1. Clone the repository
git clone https://github.com/NyangoyaG/subnet-calculator.git
cd subnet-calculator

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
cd web_app
python app.py

# 5. Open browser to http://localhost:5000
