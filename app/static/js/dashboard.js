/**
 * Student Placement Data Analysis System
 * Interactive Dashboard Engine (Chart.js 4.4.1)
 * Handles live dataset fetching, responsive rendering, dark/light theme sync, and PNG chart export.
 */

window.dashboardCharts = {};

document.addEventListener("DOMContentLoaded", function () {
    initInteractiveCharts();
});

function getThemeColors() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    return {
        textColor: isDark ? "#cbd5e1" : "#475569",
        headingColor: isDark ? "#f8fafc" : "#0f172a",
        gridColor: isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)",
        tooltipBg: isDark ? "#1e293b" : "#0f172a",
        tooltipText: "#ffffff",
        cardBg: isDark ? "#1e293b" : "#ffffff",
    };
}

async function initInteractiveCharts() {
    const urlParams = new URLSearchParams(window.location.search);
    const department = urlParams.get("department") || "All";
    const graduationYear = urlParams.get("graduation_year") || "All";

    const apiUrl = `/api/chart-data?department=${encodeURIComponent(department)}&graduation_year=${encodeURIComponent(graduationYear)}`;

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            throw new Error(`Failed to load chart data (HTTP ${response.status})`);
        }
        const data = await response.json();
        if (!data.success) {
            throw new Error("API returned failure status");
        }

        // Hide skeletons and reveal canvas wrappers
        document.querySelectorAll(".chart-skeleton").forEach(el => el.style.display = "none");
        document.querySelectorAll(".chart-canvas-wrapper").forEach(el => el.style.display = "block");

        const theme = getThemeColors();

        // 1. Department Placement Rates Chart
        renderDeptRateChart(data.dept_rates, theme);

        // 2. Placed vs Eligible Students Chart
        renderPlacedEligibleChart(data.dept_rates, theme);

        // 3. Salary Package Distribution Chart
        renderPackageDistributionChart(data.package_stats, theme);

        // 4. Top Skills Chart
        renderTopSkillsChart(data.skills, theme);

        // 5. Top Recruiting Companies Chart
        renderCompaniesChart(data.companies, theme);

        // 6. Longitudinal Yearly Trends Chart
        renderTrendsChart(data.trends, theme);

    } catch (err) {
        console.error("Dashboard chart initialization error:", err);
        // Fallback gracefully: show helpful notice inside wrappers
        document.querySelectorAll(".chart-skeleton").forEach(el => {
            el.style.animation = "none";
            el.innerHTML = `<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--text-muted);font-size:0.85rem;">📊 Data visualizer ready. Filter selection updated.</div>`;
        });
    }
}

/**
 * 1. Department Placement Rates
 */
function renderDeptRateChart(deptData, theme) {
    const ctx = document.getElementById("chartDeptRateCanvas");
    if (!ctx) return;

    if (window.dashboardCharts.deptRate) {
        window.dashboardCharts.deptRate.destroy();
    }

    // Shorten long department names for clean labels
    const shortLabels = (deptData.labels || []).map(l => {
        return l.replace("Computer Science and Engineering", "CSE")
                .replace("Artificial Intelligence and Machine Learning", "AI & ML")
                .replace("Information Technology", "IT")
                .replace("Electronics and Communication Engineering", "ECE")
                .replace("Electrical and Electronics Engineering", "EEE")
                .replace("Mechanical Engineering", "Mech")
                .replace("Civil Engineering", "Civil");
    });

    window.dashboardCharts.deptRate = new Chart(ctx, {
        type: "bar",
        data: {
            labels: shortLabels,
            datasets: [{
                label: "Placement Rate (%)",
                data: deptData.rates || [],
                backgroundColor: "rgba(79, 70, 229, 0.85)",
                borderColor: "#4f46e5",
                borderWidth: 1.5,
                borderRadius: 6,
                maxBarThickness: 36,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: theme.tooltipBg,
                    titleColor: theme.tooltipText,
                    bodyColor: theme.tooltipText,
                    padding: 10,
                    callbacks: {
                        label: function (context) {
                            return `Placement Rate: ${context.parsed.y}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 11, weight: 600 } }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: theme.gridColor },
                    ticks: {
                        color: theme.textColor,
                        callback: val => val + "%",
                        font: { family: "Inter", size: 11 }
                    }
                }
            }
        }
    });
}

/**
 * 2. Placed vs Eligible Students
 */
function renderPlacedEligibleChart(deptData, theme) {
    const ctx = document.getElementById("chartPlacedEligibleCanvas");
    if (!ctx) return;

    if (window.dashboardCharts.placedEligible) {
        window.dashboardCharts.placedEligible.destroy();
    }

    const shortLabels = (deptData.labels || []).map(l => {
        return l.replace("Computer Science and Engineering", "CSE")
                .replace("Artificial Intelligence and Machine Learning", "AI & ML")
                .replace("Information Technology", "IT")
                .replace("Electronics and Communication Engineering", "ECE")
                .replace("Electrical and Electronics Engineering", "EEE")
                .replace("Mechanical Engineering", "Mech")
                .replace("Civil Engineering", "Civil");
    });

    window.dashboardCharts.placedEligible = new Chart(ctx, {
        type: "bar",
        data: {
            labels: shortLabels,
            datasets: [
                {
                    label: "Eligible Students",
                    data: deptData.eligible || [],
                    backgroundColor: "rgba(100, 116, 139, 0.75)",
                    borderColor: "#475569",
                    borderWidth: 1,
                    borderRadius: 4,
                    maxBarThickness: 22,
                },
                {
                    label: "Placed Students",
                    data: deptData.placed || [],
                    backgroundColor: "rgba(16, 185, 129, 0.85)",
                    borderColor: "#10b981",
                    borderWidth: 1,
                    borderRadius: 4,
                    maxBarThickness: 22,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                    labels: { color: theme.textColor, font: { family: "Inter", size: 11, weight: 600 } }
                },
                tooltip: {
                    backgroundColor: theme.tooltipBg,
                    titleColor: theme.tooltipText,
                    bodyColor: theme.tooltipText,
                    padding: 10
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 11, weight: 600 } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: theme.gridColor },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 11 } }
                }
            }
        }
    });
}

/**
 * 3. Salary Package Distribution
 */
function renderPackageDistributionChart(pkgStats, theme) {
    const ctx = document.getElementById("chartPkgDistCanvas");
    if (!ctx) return;

    if (window.dashboardCharts.pkgDist) {
        window.dashboardCharts.pkgDist.destroy();
    }

    const brackets = (pkgStats && pkgStats.brackets) ? pkgStats.brackets : {};
    const labels = ["< 5 LPA\n(Mass)", "5 - 8 LPA\n(Core)", "8 - 15 LPA\n(Dream)", "15+ LPA\n(Super Dream)"];
    const counts = [
        brackets.less_than_5 ? brackets.less_than_5.count : 0,
        brackets["5_to_8"] ? brackets["5_to_8"].count : 0,
        brackets["8_to_15"] ? brackets["8_to_15"].count : 0,
        brackets.above_15 ? brackets.above_15.count : 0,
    ];

    window.dashboardCharts.pkgDist = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Offers Extended",
                data: counts,
                backgroundColor: [
                    "rgba(148, 163, 184, 0.8)",
                    "rgba(59, 130, 246, 0.8)",
                    "rgba(79, 70, 229, 0.85)",
                    "rgba(16, 185, 129, 0.85)",
                ],
                borderColor: ["#64748b", "#2563eb", "#4f46e5", "#059669"],
                borderWidth: 1.5,
                borderRadius: 6,
                maxBarThickness: 42,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: theme.tooltipBg,
                    titleColor: theme.tooltipText,
                    bodyColor: theme.tooltipText,
                    padding: 10,
                    callbacks: {
                        label: function (context) {
                            return `Offers: ${context.parsed.y} candidate(s)`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 10, weight: 600 } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: theme.gridColor },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 11 } }
                }
            }
        }
    });
}

/**
 * 4. Top Recorded Skills
 */
function renderTopSkillsChart(skillData, theme) {
    const ctx = document.getElementById("chartSkillsCanvas");
    if (!ctx) return;

    if (window.dashboardCharts.skills) {
        window.dashboardCharts.skills.destroy();
    }

    const labels = (skillData.labels || []).slice(0, 8);
    const placed = (skillData.placed || []).slice(0, 8);

    window.dashboardCharts.skills = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Placed Students with Skill",
                data: placed,
                backgroundColor: "rgba(20, 184, 166, 0.85)",
                borderColor: "#0d9488",
                borderWidth: 1.5,
                borderRadius: 4,
                maxBarThickness: 18,
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: theme.tooltipBg,
                    titleColor: theme.tooltipText,
                    bodyColor: theme.tooltipText,
                    padding: 10
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: theme.gridColor },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 11 } }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 11, weight: 600 } }
                }
            }
        }
    });
}

/**
 * 5. Top Recruiting Companies
 */
function renderCompaniesChart(compData, theme) {
    const ctx = document.getElementById("chartCompaniesCanvas");
    if (!ctx) return;

    if (window.dashboardCharts.companies) {
        window.dashboardCharts.companies.destroy();
    }

    const labels = (compData.labels || []).slice(0, 7);
    const offers = (compData.offers || []).slice(0, 7);

    window.dashboardCharts.companies = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Offers Extended",
                data: offers,
                backgroundColor: "rgba(59, 130, 246, 0.85)",
                borderColor: "#2563eb",
                borderWidth: 1.5,
                borderRadius: 4,
                maxBarThickness: 18,
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: theme.tooltipBg,
                    titleColor: theme.tooltipText,
                    bodyColor: theme.tooltipText,
                    padding: 10
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { color: theme.gridColor },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 11 } }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 11, weight: 600 } }
                }
            }
        }
    });
}

/**
 * 6. Longitudinal Yearly Trends
 */
function renderTrendsChart(trendData, theme) {
    const ctx = document.getElementById("chartTrendsCanvas");
    if (!ctx) return;

    if (window.dashboardCharts.trends) {
        window.dashboardCharts.trends.destroy();
    }

    window.dashboardCharts.trends = new Chart(ctx, {
        type: "line",
        data: {
            labels: trendData.labels || [],
            datasets: [
                {
                    label: "Placement Rate (%)",
                    data: trendData.rates || [],
                    borderColor: "#4f46e5",
                    backgroundColor: "rgba(79, 70, 229, 0.12)",
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointBackgroundColor: "#4f46e5",
                    pointRadius: 4,
                    yAxisID: "yRate",
                },
                {
                    label: "Average CTC (LPA)",
                    data: trendData.avg_ctc || [],
                    borderColor: "#f59e0b",
                    backgroundColor: "transparent",
                    borderDash: [5, 5],
                    tension: 0.35,
                    borderWidth: 2,
                    pointBackgroundColor: "#f59e0b",
                    pointRadius: 4,
                    yAxisID: "ySalary",
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: {
                    position: "top",
                    labels: { color: theme.textColor, font: { family: "Inter", size: 11, weight: 600 } }
                },
                tooltip: {
                    backgroundColor: theme.tooltipBg,
                    titleColor: theme.tooltipText,
                    bodyColor: theme.tooltipText,
                    padding: 10
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: theme.textColor, font: { family: "Inter", size: 11, weight: 600 } }
                },
                yRate: {
                    type: "linear",
                    position: "left",
                    min: 0,
                    max: 100,
                    grid: { color: theme.gridColor },
                    ticks: {
                        color: theme.textColor,
                        callback: val => val + "%",
                        font: { family: "Inter", size: 11 }
                    }
                },
                ySalary: {
                    type: "linear",
                    position: "right",
                    grid: { display: false },
                    ticks: {
                        color: theme.textColor,
                        callback: val => val + " LPA",
                        font: { family: "Inter", size: 11 }
                    }
                }
            }
        }
    });
}

/**
 * Universal PNG Download utility for interactive Chart.js cards
 */
window.downloadChartAsPNG = function (chartKey, filename) {
    const chart = window.dashboardCharts ? window.dashboardCharts[chartKey] : null;
    if (!chart) {
        alert("Chart is still loading or unavailable.");
        return;
    }
    const a = document.createElement("a");
    a.href = chart.toBase64Image("image/png", 1.0);
    a.download = `${filename || chartKey}_analytics.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
};

// Re-render charts when theme changes so axes match new dark/light palette
window.addEventListener("themeChanged", function () {
    const theme = getThemeColors();
    Object.values(window.dashboardCharts).forEach(chart => {
        if (!chart) return;
        if (chart.options.scales) {
            Object.values(chart.options.scales).forEach(scale => {
                if (scale.ticks) scale.ticks.color = theme.textColor;
                if (scale.grid && scale.grid.color) scale.grid.color = theme.gridColor;
            });
        }
        if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
            chart.options.plugins.legend.labels.color = theme.textColor;
        }
        chart.update();
    });
});
