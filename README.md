# Math-Modeling-Assignment-251 - Symbolic and Algebraic Reasoning in Petri Nets ⚛️

# 📘 Petri Net Analyzer – Installation & Usage Guide (Ubuntu)

This project implements:
- Petri Net parsing from PNML  
- BFS reachable markings  
- DFS reachable markings  
- BDD symbolic state-space exploration (PyEDA)  
- Deadlock detection  
- Optimization of linear function c·M (PuLP)  

The project is written in **Python ≥ 3.10** and designed to run on **Ubuntu / WSL2 Ubuntu**.

---

## 🔧 System Requirements

Make sure your system has:
- Python 3.10+
- pip package manager
- Ubuntu 20.04 / 22.04 / WSL2 Ubuntu

Check Python version:

```bash
python3 --version
```

---

# Install Dependencies (Ubuntu)
## Update package index
```sh
sudo apt update
```

## Install VENV and required Python packages
```sh
sudo apt install python3-venv python3-full -y
```

## Create a virtual environment named '.venv'
```sh
python3 -m venv .venv
```

## Activate the virtual environment
```sh
source .venv/bin/activate
```

## Install required Python libraries
| Library                 | Purpose                       |
| ----------------------- | ----------------------------- |
| **pyeda**               | BDD symbolic model checking   |
| **pulp**                | Linear programming solver     |
| **numpy**               | Matrix & marking operations   |

Install them using pip:
```sh
pip3 install pyeda pulp numpy
```

---

# How to Run the Program After Installation
## Activate venv
```sh
source .venv/bin/activate
```

## Run the program:
```sh
python3 -m src.main
```

---

# Example Program Output
```text
--- BFS Reachable Markings ---
[1 0 0 0 0]
[0 1 0 0 0]
[0 0 1 0 0]
...
Total BFS reachable = 6
```