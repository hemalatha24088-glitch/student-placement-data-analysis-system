"""
Chart Service Module.
Generates professional Matplotlib data visualizations using the Agg backend.
Charts can be returned as PNG binary streams or base64 encoded strings.
"""

import io

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend safe for web servers
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from app.services.analytics_service import (
    get_department_analytics,
    get_package_analytics,
    get_skill_analytics,
    get_yearly_trends,
    load_placement_dataframe,
)
from app.services.company_service import get_companies

# Visual Theme Palette (Navy, Indigo, Teal, Amber, Slate)
PRIMARY_COLOR = "#1e3a8a"  # Deep Navy
SECONDARY_COLOR = "#4f46e5"  # Indigo
ACCENT_TEAL = "#0d9488"  # Teal
ACCENT_AMBER = "#f59e0b"  # Amber
BG_LIGHT = "#f8fafc"  # Slate Light
TEXT_DARK = "#0f172a"  # Slate 900
GRID_COLOR = "#e2e8f0"  # Slate 200


def _setup_figure(figsize=(8, 4.5)):
    fig, ax = plt.subplots(figsize=figsize, facecolor="white")
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.tick_params(colors="#475569", labelsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5, color=GRID_COLOR)
    return fig, ax


def _empty_chart(title="No Data Available"):
    fig, ax = _setup_figure()
    ax.text(
        0.5,
        0.5,
        "No data matching selected filters",
        ha="center",
        va="center",
        color="#94a3b8",
        fontsize=12,
        fontweight="medium",
    )
    ax.set_title(title, fontsize=12, fontweight="bold", color=TEXT_DARK, pad=12)
    ax.set_xticks([])
    ax.set_yticks([])
    return fig


def _fig_to_png_bytes(fig):
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def generate_dept_placement_rate_chart(graduation_year=None):
    """
    Chart 1: Department-Wise Placement Rate (%) Bar Chart.
    """
    depts = get_department_analytics(graduation_year=graduation_year)
    if not depts:
        return _fig_to_png_bytes(_empty_chart("Department Placement Rates"))

    names = [d["department"].replace(" and ", " & ").replace("Engineering", "Engg.") for d in depts]
    rates = [d["placement_rate"] for d in depts]

    fig, ax = _setup_figure(figsize=(8.5, 4.5))
    bars = ax.bar(names, rates, color=SECONDARY_COLOR, width=0.55, edgecolor="#3730a3", linewidth=1)

    # Average benchmark line
    avg_rate = np.mean(rates) if rates else 0
    ax.axhline(avg_rate, color="#dc2626", linestyle="--", linewidth=1.5, label=f"Avg Benchmark ({avg_rate:.1f}%)")

    # Add value labels above bars
    for bar in bars:
        h = bar.get_height()
        ax.annotate(
            f"{h:.1f}%",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=PRIMARY_COLOR,
        )

    ax.set_title("Department-Wise Placement Rate (%)", fontsize=13, fontweight="bold", color=TEXT_DARK, pad=14)
    ax.set_ylabel("Placement Rate (%)", fontsize=10, fontweight="bold", color="#334155")
    ax.set_ylim(0, 110)
    plt.xticks(rotation=25, ha="right")
    ax.legend(frameon=True, facecolor="white", edgecolor=GRID_COLOR, fontsize=8, loc="upper right")
    return _fig_to_png_bytes(fig)


def generate_placed_vs_eligible_chart(graduation_year=None):
    """
    Chart 2: Placed vs Eligible Students Grouped Bar Chart.
    """
    depts = get_department_analytics(graduation_year=graduation_year)
    if not depts:
        return _fig_to_png_bytes(_empty_chart("Placed vs Eligible Students"))

    labels = [d["department"].replace(" and ", " & ").replace("Engineering", "Engg.") for d in depts]
    eligible = [d["eligible_students"] for d in depts]
    placed = [d["placed_students"] for d in depts]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = _setup_figure(figsize=(9, 4.5))
    rects1 = ax.bar(x - width / 2, eligible, width, label="Eligible Students", color="#93c5fd", edgecolor="#60a5fa")
    rects2 = ax.bar(x + width / 2, placed, width, label="Placed Students", color=PRIMARY_COLOR, edgecolor="#172554")

    # Labels
    for bar in rects1:
        h = bar.get_height()
        ax.annotate(
            f"{h}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#1e40af",
        )

    for bar in rects2:
        h = bar.get_height()
        ax.annotate(
            f"{h}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
            color=TEXT_DARK,
        )

    ax.set_title("Eligible vs Placed Students by Department", fontsize=13, fontweight="bold", color=TEXT_DARK, pad=14)
    ax.set_ylabel("Number of Students", fontsize=10, fontweight="bold", color="#334155")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylim(0, max(eligible + [10]) * 1.25)
    ax.legend(frameon=True, facecolor="white", edgecolor=GRID_COLOR, fontsize=9)
    return _fig_to_png_bytes(fig)


def generate_package_distribution_chart(department=None, graduation_year=None):
    """
    Chart 3: Salary Package Distribution (Histogram with Mean and Median markers).
    """
    df = load_placement_dataframe(department=department, graduation_year=graduation_year)
    if df.empty or "placement_status" not in df.columns:
        return _fig_to_png_bytes(_empty_chart("Salary Package Distribution"))

    placed_offers = df[(df["placement_status"].isin(["Placed", "Offer Accepted"])) & (df["package_amount"].notna())]
    packages = placed_offers["package_amount"].values

    if len(packages) == 0:
        return _fig_to_png_bytes(_empty_chart("Salary Package Distribution"))

    fig, ax = _setup_figure(figsize=(8, 4.5))

    # Custom binning
    bins = np.linspace(min(packages), max(packages), 12)
    n, bins_out, patches = ax.hist(packages, bins=bins, color=ACCENT_TEAL, edgecolor="#0f766e", alpha=0.85, rwidth=0.85)

    mean_val = np.mean(packages)
    median_val = np.median(packages)

    ax.axvline(mean_val, color="#dc2626", linestyle="--", linewidth=1.8, label=f"Mean: {mean_val:.2f} LPA")
    ax.axvline(median_val, color="#1e3a8a", linestyle="-.", linewidth=1.8, label=f"Median: {median_val:.2f} LPA")

    ax.set_title("Salary Package Distribution (LPA CTC)", fontsize=13, fontweight="bold", color=TEXT_DARK, pad=14)
    ax.set_xlabel("Annual CTC (LPA in INR)", fontsize=10, fontweight="bold", color="#334155")
    ax.set_ylabel("Number of Placement Offers", fontsize=10, fontweight="bold", color="#334155")
    ax.legend(frameon=True, facecolor="white", edgecolor=GRID_COLOR, fontsize=9)
    return _fig_to_png_bytes(fig)


def generate_top_skills_chart(department=None):
    """
    Chart 4: Most Frequently Recorded Skills among Placed Students (Horizontal Bar Chart).
    """
    skills = get_skill_analytics(department=department)
    if not skills:
        return _fig_to_png_bytes(_empty_chart("Top Skills Recorded"))

    # Top 8 skills
    top_skills = skills[:8]
    names = [s["skill_name"] for s in reversed(top_skills)]
    counts = [s["placed_students_with_skill"] for s in reversed(top_skills)]

    fig, ax = _setup_figure(figsize=(8.5, 4.5))
    ax.grid(axis="x", linestyle="--", alpha=0.5, color=GRID_COLOR)
    ax.grid(axis="y", visible=False)

    bars = ax.barh(names, counts, color="#6366f1", height=0.6, edgecolor="#4338ca")

    for bar in bars:
        w = bar.get_width()
        ax.annotate(
            f"{int(w)} students",
            xy=(w, bar.get_y() + bar.get_height() / 2),
            xytext=(6, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            color=PRIMARY_COLOR,
        )

    ax.set_title("Top Skills Recorded Among Placed Students", fontsize=13, fontweight="bold", color=TEXT_DARK, pad=14)
    ax.set_xlabel("Number of Placed Students", fontsize=10, fontweight="bold", color="#334155")
    ax.set_xlim(0, max(counts + [5]) * 1.25)
    return _fig_to_png_bytes(fig)


def generate_company_recruitment_chart():
    """
    Chart 5: Company-Wise Recruitment Count (Top 8 Hiring Companies).
    """
    companies = get_companies()
    if not companies:
        return _fig_to_png_bytes(_empty_chart("Company Recruitment Summary"))

    top_companies = [c for c in companies if c["total_offers"] > 0][:8]
    if not top_companies:
        return _fig_to_png_bytes(_empty_chart("No Company Recruitment Data"))

    names = [c["company_name"].split("(")[0].strip() for c in top_companies]
    offers = [c["total_offers"] for c in top_companies]
    avg_packages = [c["avg_package_lpa"] or 0 for c in top_companies]

    fig, ax = _setup_figure(figsize=(8.5, 4.5))
    bars = ax.bar(names, offers, color=ACCENT_AMBER, edgecolor="#d97706", width=0.55)

    for i, bar in enumerate(bars):
        h = bar.get_height()
        pkg = avg_packages[i]
        label = f"{h}\n({pkg:.1f}L)" if pkg > 0 else f"{h}"
        ax.annotate(
            label,
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
            color="#78350f",
        )

    ax.set_title("Top Recruiting Companies (Offers & Avg LPA)", fontsize=13, fontweight="bold", color=TEXT_DARK, pad=14)
    ax.set_ylabel("Number of Offers Made", fontsize=10, fontweight="bold", color="#334155")
    ax.set_ylim(0, max(offers + [5]) * 1.3)
    plt.xticks(rotation=25, ha="right")
    return _fig_to_png_bytes(fig)


def generate_yearly_trends_chart():
    """
    Chart 6: Placement Trends Across Graduation Years (2024 - 2026).
    """
    trends = get_yearly_trends()
    if not trends or len(trends) < 2:
        return _fig_to_png_bytes(_empty_chart("Placement Trends Over Time"))

    years = [str(t["graduation_year"]) for t in trends]
    rates = [float(t["placement_rate"]) for t in trends]
    avg_pkgs = [float(t["avg_package_lpa"] or 0) for t in trends]

    fig, ax1 = _setup_figure(figsize=(8.5, 4.5))
    ax2 = ax1.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.grid(False)

    # Line 1: Placement Rate
    line1 = ax1.plot(
        years, rates, marker="o", linewidth=2.5, color=PRIMARY_COLOR, markersize=8, label="Placement Rate (%)"
    )
    for x, y in zip(years, rates):
        ax1.annotate(
            f"{y:.1f}%",
            xy=(x, y),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=PRIMARY_COLOR,
        )

    # Line 2: Average Package
    line2 = ax2.plot(
        years,
        avg_pkgs,
        marker="s",
        linewidth=2.5,
        color=ACCENT_TEAL,
        markersize=8,
        linestyle="--",
        label="Avg CTC (LPA)",
    )
    for x, y in zip(years, avg_pkgs):
        ax2.annotate(
            f"{y:.1f} L",
            xy=(x, y),
            xytext=(0, -14),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=ACCENT_TEAL,
        )

    ax1.set_title(
        "Placement Rate & Average CTC Trends by Graduation Year",
        fontsize=13,
        fontweight="bold",
        color=TEXT_DARK,
        pad=14,
    )
    ax1.set_ylabel("Placement Rate (%)", fontsize=10, fontweight="bold", color=PRIMARY_COLOR)
    ax2.set_ylabel("Average Package (LPA)", fontsize=10, fontweight="bold", color=ACCENT_TEAL)
    ax1.set_ylim(0, 110)
    ax2.set_ylim(0, max(avg_pkgs + [15.0]) * 1.35)

    # Combined legend
    lines = line1 + line2
    labels = [ln.get_label() for ln in lines]
    ax1.legend(lines, labels, frameon=True, facecolor="white", edgecolor=GRID_COLOR, fontsize=8.5, loc="lower right")
    return _fig_to_png_bytes(fig)
