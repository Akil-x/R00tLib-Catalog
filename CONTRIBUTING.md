# Contributing to R00tLib Knowledge Hub

Thank you for your interest in contributing to the **R00tLib Knowledge Hub**!

We welcome community contributions to keep this technical index comprehensive, accurate, and up-to-date.

---

## 📌 How Can You Contribute?

### 1. Suggesting New Books
If there is an essential technical book missing from our catalog:
1. Open an **Issue** titled `[Book Request]: Book Title`.
2. Include the following details:
   - **Title & Subtitle**
   - **Author(s)**
   - **Publication Year & Edition**
   - **ISBN-10 / ISBN-13**
   - **Topic/Category** (e.g., Python, Cybersecurity, AI & ML, Reverse Engineering)
   - **Amazon or Official Publisher Link**

### 2. Fixing Inaccurate Metadata
If you spot a typo in a title, wrong author attribution, outdated edition, or broken link:
1. Fork the repository.
2. Edit `BOOKS.json` or regenerate using `extract_books.py`.
3. Submit a Pull Request clearly explaining what was corrected.

### 3. Improving Automation & Tooling
We welcome enhancements to:
- `extract_books.py` (performance improvements, better parsing heuristics, automated CI/CD actions).
- Export formats (e.g., generating CSV, SQLite, or search web interfaces).

---

## 🚀 Submitting a Pull Request (PR)

1. **Fork** the repository to your own GitHub account.
2. Create a clean feature branch:
   ```bash
   git checkout -b feat/suggested-book-or-fix
   ```
3. Commit your changes with clear, descriptive commit messages:
   ```bash
   git commit -m "docs: add missing ISBN for Designing Data-Intensive Applications"
   ```
4. Push your branch to GitHub:
   ```bash
   git push origin feat/suggested-book-or-fix
   ```
5. Open a **Pull Request** against the `master` / `main` branch.

---

## 📜 Community Code of Conduct
- Be respectful and supportive of all contributors.
- Do not submit copyrighted materials directly into the repository; this repository maintains an index/catalog only.

---

*Join the discussion on Telegram:* [**@R00tLib**](https://t.me/R00tLib)
