"""Generates clean preview images for README.md and documentation."""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("docs/assets", exist_ok=True)


def create_preview_card(
    filename,
    title,
    subtitle,
    items,
    bg_color="#0f172a",
    card_color="#1e293b",
    text_color="#f8fafc",
    accent_color="#6366f1",
):
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(card_color)

    # Hide axes
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(0.8, 8.5, title, fontsize=16, fontweight="bold", color=text_color, va="center")
    ax.text(0.8, 7.6, subtitle, fontsize=11, color="#94a3b8", va="center")

    # Divider line
    ax.plot([0.8, 9.2], [7.0, 7.0], color="#334155", lw=1.5)

    # Content cards/boxes
    for i, (label, val, note) in enumerate(items):
        y = 5.6 - (i * 1.6)
        # Background card pill
        rect = plt.Rectangle((0.8, y - 0.5), 8.4, 1.3, facecolor="#0f172a", edgecolor="#334155", lw=1, zorder=2)
        ax.add_patch(rect)

        # Text inside pill
        ax.text(1.2, y + 0.15, label, fontsize=11, fontweight="bold", color=text_color, zorder=3)
        ax.text(1.2, y - 0.25, note, fontsize=9, color="#94a3b8", zorder=3)
        ax.text(8.8, y, val, fontsize=14, fontweight="bold", color=accent_color, ha="right", va="center", zorder=3)

    plt.tight_layout()
    filepath = os.path.join("docs", "assets", filename)
    plt.savefig(filepath, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Generated {filepath}")


# 1. Dashboard Preview
create_preview_card(
    "dashboard_preview.png",
    "Interactive Analytics Dashboard",
    "Real-time KPIs, Dynamic Filters & Chart.js 4.4.1 Components",
    [
        ("Overall Placement Rate", "86.4%", "Eligible candidate recruitment across active academic drives"),
        ("Average Compensation CTC", "12.8 LPA", "Right-skewed mean package across engineering cohorts"),
        ("Active Corporate Recruiters", "28 Partners", "Tier-1 Super Dream, Dream, Core and Mass partner firms"),
    ],
    bg_color="#090d16",
    card_color="#131b2e",
    accent_color="#38bdf8",
)

# 2. Predictor Preview
create_preview_card(
    "predictor_preview.png",
    "Machine Learning 'What-If' Predictor",
    "Live CGPA slider, dynamic skills selector & animated circular gauge",
    [
        ("Placement Probability", "87.5%", "Calculated from pre-drive student attributes via Random Forest"),
        ("Assessed Risk Tier", "Low Risk", "Color-coded candidate readiness classification (#10b981)"),
        ("Top Influential Feature", "CGPA + Skills", "Positive contribution ranking derived from Gini importance"),
    ],
    bg_color="#0b132b",
    card_color="#1c2541",
    accent_color="#10b981",
)

# 3. Model Info Preview
create_preview_card(
    "model_info_preview.png",
    "Model Diagnostics & Performance Hub",
    "Empirical cross-validation, serialized pipelines & feature importance",
    [
        ("Classifier Accuracy", "79.55%", "5-Fold Cross Validation Mean: 80.39% (Stratified)"),
        ("Classifier ROC-AUC & F1", "0.85 / 0.76", "High discriminative threshold with macro weighted balance"),
        ("Salary Regressor MAE", "2.83 LPA", "Package estimation within +/- 2.83 LPA margin of error"),
    ],
    bg_color="#0f172a",
    card_color="#1e293b",
    accent_color="#a855f7",
)

# 4. Dark Mode Preview
create_preview_card(
    "dark_mode_preview.png",
    "Accessible Dark & Light Mode Theme",
    "Refined navy & indigo design system with localStorage memory",
    [
        ("Active Palette", "Navy / Slate", "High-contrast WCAG AA accessible color tokens"),
        ("Typography", "Inter", "Clean modern variable font loaded via Google Fonts"),
        ("Theme Memory", "Synchronized", "Honors prefers-color-scheme with instant user toggle"),
    ],
    bg_color="#020617",
    card_color="#0f172a",
    accent_color="#6366f1",
)
