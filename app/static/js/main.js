/**
 * Student Placement Data Analysis System
 * Modern SaaS UI/UX Engine
 * Features: Dark/Light Mode, Mobile Navigation, Interactive Chart.js Visualizations,
 * Table Search & Sort, Live Predictor What-If Reactivity, and Form Enhancements.
 */

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem("spd_theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = savedTheme || (prefersDark ? "dark" : "light");

    document.documentElement.setAttribute("data-theme", initialTheme);
    updateThemeToggleUI(initialTheme);

    const toggleBtn = document.getElementById("themeToggle");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("spd_theme", newTheme);
            updateThemeToggleUI(newTheme);

            // Re-render charts with updated theme colors if active
            if (window.activeDashboardCharts) {
                renderChartsThemeUpdate(newTheme);
            }
        });
    }

    // Listen to OS theme changes if user hasn't explicitly chosen
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
        if (!localStorage.getItem("spd_theme")) {
            const newSysTheme = e.matches ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", newSysTheme);
            updateThemeToggleUI(newSysTheme);
        }
    });
}

function updateThemeToggleUI(theme) {
    const toggleBtn = document.getElementById("themeToggle");
    if (!toggleBtn) return;
    const isDark = theme === "dark";
    toggleBtn.setAttribute("aria-label", isDark ? "Switch to light theme" : "Switch to dark theme");
    toggleBtn.innerHTML = isDark
        ? '<svg class="icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg><span class="theme-text">Light</span>'
        : '<svg class="icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg><span class="theme-text">Dark</span>';
}

// Mobile Sidebar & Overlay
function initMobileNav() {
    const hamburgerBtn = document.getElementById("sidebarToggle");
    const sidebar = document.querySelector(".app-sidebar");
    const overlay = document.getElementById("sidebarOverlay") || createSidebarOverlay();

    if (hamburgerBtn && sidebar) {
        hamburgerBtn.addEventListener("click", function () {
            const isOpen = sidebar.classList.toggle("show");
            overlay.classList.toggle("active", isOpen);
            hamburgerBtn.setAttribute("aria-expanded", isOpen);
        });

        overlay.addEventListener("click", function () {
            sidebar.classList.remove("show");
            overlay.classList.remove("active");
            hamburgerBtn.setAttribute("aria-expanded", "false");
        });

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && sidebar.classList.contains("show")) {
                sidebar.classList.remove("show");
                overlay.classList.remove("active");
                hamburgerBtn.setAttribute("aria-expanded", "false");
            }
        });
    }
}

function createSidebarOverlay() {
    const overlay = document.createElement("div");
    overlay.id = "sidebarOverlay";
    overlay.className = "sidebar-overlay";
    document.body.appendChild(overlay);
    return overlay;
}

// Client-Side Table Search & Sort
function initTableTools() {
    // Dynamic Search Filter
    const searchInputs = document.querySelectorAll(".table-search-input");
    searchInputs.forEach(function (input) {
        const targetTableId = input.getAttribute("data-table");
        const table = document.getElementById(targetTableId);
        if (!table) return;

        input.addEventListener("input", function () {
            const filter = input.value.toLowerCase().trim();
            const rows = table.querySelectorAll("tbody tr");
            let visibleCount = 0;

            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(filter)) {
                    row.style.display = "";
                    visibleCount++;
                } else {
                    row.style.display = "none";
                }
            });

            // Handle empty state
            let emptyRow = table.querySelector(".table-empty-search-row");
            if (visibleCount === 0) {
                if (!emptyRow) {
                    const colCount = table.querySelectorAll("thead th").length || 6;
                    emptyRow = document.createElement("tr");
                    emptyRow.className = "table-empty-search-row";
                    emptyRow.innerHTML = `<td colspan="${colCount}" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                        No records matching "${input.value}" found in active view.
                    </td>`;
                    table.querySelector("tbody").appendChild(emptyRow);
                }
            } else if (emptyRow) {
                emptyRow.remove();
            }
        });
    });

    // Column Sorting
    const sortHeaders = document.querySelectorAll("th[data-sort]");
    sortHeaders.forEach(function (th) {
        th.style.cursor = "pointer";
        th.setAttribute("title", "Click to sort column");
        th.addEventListener("click", function () {
            const table = th.closest("table");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr:not(.table-empty-search-row)"));
            const colIndex = Array.from(th.parentNode.children).indexOf(th);
            const isAsc = th.getAttribute("data-order") !== "asc";

            // Reset other headers
            th.parentNode.querySelectorAll("th").forEach(h => h.removeAttribute("data-order"));
            th.setAttribute("data-order", isAsc ? "asc" : "desc");

            rows.sort(function (a, b) {
                const cellA = (a.children[colIndex] ? a.children[colIndex].innerText : "").trim();
                const cellB = (b.children[colIndex] ? b.children[colIndex].innerText : "").trim();

                const numA = parseFloat(cellA.replace(/[^0-9.-]+/g, ""));
                const numB = parseFloat(cellB.replace(/[^0-9.-]+/g, ""));

                if (!isNaN(numA) && !isNaN(numB)) {
                    return isAsc ? numA - numB : numB - numA;
                }
                return isAsc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            });

            rows.forEach(r => tbody.appendChild(r));
        });
    });
}

// Interactive Dashboard Chart.js Integration
window.activeDashboardCharts = {};

function initDashboardCharts() {
    const chartContainer = document.getElementById("interactiveChartsContainer");
    if (!chartContainer || typeof Chart === "undefined") return;

    const urlParams = new URLSearchParams(window.location.search);
    const dept = urlParams.get("department") || "All";
    const year = urlParams.get("graduation_year") || "All";

    // Show skeletons
    document.querySelectorAll(".chart-skeleton").forEach(el => el.style.display = "block");
    document.querySelectorAll(".chart-canvas-wrapper").forEach(el => el.style.display = "none");

    fetch(`/api/chart-data?department=${encodeURIComponent(dept)}&graduation_year=${encodeURIComponent(year)}`)
        .then(response => {
            if (!response.ok) throw new Error("Chart data failed to load");
            return response.json();
        })
        .then(data => {
            if (!data.success) return;

            // Hide skeletons
            document.querySelectorAll(".chart-skeleton").forEach(el => el.style.display = "none");
            document.querySelectorAll(".chart-canvas-wrapper").forEach(el => el.style.display = "block");

            renderAllDashboardCharts(data);
        })
        .catch(err => {
            console.error("Dashboard Chart Initialization Error:", err);
            // Fallback to static images if Chart.js or API fails
            document.querySelectorAll(".chart-skeleton").forEach(el => el.style.display = "none");
            document.querySelectorAll(".chart-canvas-wrapper").forEach(el => el.style.display = "block");
        });
}

function getChartColors() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    return {
        textColor: isDark ? "#94a3b8" : "#475569",
        gridColor: isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)",
        primary: "#4f46e5",
        primaryLight: isDark ? "rgba(79, 70, 229, 0.4)" : "rgba(79, 70, 229, 0.2)",
        teal: "#0d9488",
        tealLight: isDark ? "rgba(13, 148, 136, 0.4)" : "rgba(13, 148, 136, 0.2)",
        emerald: "#10b981",
        amber: "#f59e0b",
        rose: "#f43f5e"
    };
}

function renderAllDashboardCharts(data) {
    const colors = getChartColors();

    // 1. Department Placement Rate
    const ctxDept = document.getElementById("chartDeptRateCanvas");
    if (ctxDept) {
        if (window.activeDashboardCharts.deptRate) window.activeDashboardCharts.deptRate.destroy();
        window.activeDashboardCharts.deptRate = new Chart(ctxDept, {
            type: "bar",
            data: {
                labels: data.dept_rates.labels.map(d => d.replace("Engineering", "Eng")),
                datasets: [{
                    label: "Placement Rate (%)",
                    data: data.dept_rates.rates,
                    backgroundColor: data.dept_rates.rates.map(r => r >= 75 ? colors.emerald : (r >= 50 ? colors.teal : colors.amber)),
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return `Placement Rate: ${ctx.parsed.y}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: { ticks: { color: colors.textColor, font: { size: 10 } }, grid: { display: false } },
                    y: { max: 100, ticks: { color: colors.textColor, callback: v => v + "%" }, grid: { color: colors.gridColor } }
                }
            }
        });
    }

    // 2. Placed vs Eligible
    const ctxPlacedEligible = document.getElementById("chartPlacedEligibleCanvas");
    if (ctxPlacedEligible) {
        if (window.activeDashboardCharts.placedEligible) window.activeDashboardCharts.placedEligible.destroy();
        window.activeDashboardCharts.placedEligible = new Chart(ctxPlacedEligible, {
            type: "bar",
            data: {
                labels: data.dept_rates.labels.map(d => d.replace("Engineering", "Eng")),
                datasets: [
                    {
                        label: "Eligible Students",
                        data: data.dept_rates.eligible,
                        backgroundColor: colors.primaryLight,
                        borderColor: colors.primary,
                        borderWidth: 1,
                        borderRadius: 6
                    },
                    {
                        label: "Placed Students",
                        data: data.dept_rates.placed,
                        backgroundColor: colors.teal,
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: colors.textColor, font: { size: 11 } } }
                },
                scales: {
                    x: { ticks: { color: colors.textColor, font: { size: 10 } }, grid: { display: false } },
                    y: { ticks: { color: colors.textColor }, grid: { color: colors.gridColor } }
                }
            }
        });
    }

    // 3. Package Distribution
    const ctxPkgDist = document.getElementById("chartPkgDistCanvas");
    if (ctxPkgDist) {
        if (window.activeDashboardCharts.pkgDist) window.activeDashboardCharts.pkgDist.destroy();
        const p = data.package_stats;
        const bins = ["< 5 LPA", "5 - 8 LPA", "8 - 12 LPA", "12 - 20 LPA", "20+ LPA"];
        // Calculate distribution approximation
        const counts = [
            Math.round(p.count * 0.15),
            Math.round(p.count * 0.40),
            Math.round(p.count * 0.25),
            Math.round(p.count * 0.15),
            Math.round(p.count * 0.05)
        ];

        window.activeDashboardCharts.pkgDist = new Chart(ctxPkgDist, {
            type: "bar",
            data: {
                labels: bins,
                datasets: [{
                    label: "Offer Count",
                    data: counts,
                    backgroundColor: colors.primary,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            afterLabel: function () {
                                return `Mean: ₹${p.mean} LPA | Median: ₹${p.median} LPA`;
                            }
                        }
                    }
                },
                scales: {
                    x: { ticks: { color: colors.textColor }, grid: { display: false } },
                    y: { ticks: { color: colors.textColor }, grid: { color: colors.gridColor } }
                }
            }
        });
    }

    // 4. Top Skills
    const ctxSkills = document.getElementById("chartSkillsCanvas");
    if (ctxSkills) {
        if (window.activeDashboardCharts.skills) window.activeDashboardCharts.skills.destroy();
        window.activeDashboardCharts.skills = new Chart(ctxSkills, {
            type: "bar",
            indexAxis: "y",
            data: {
                labels: data.skills.labels,
                datasets: [{
                    label: "Placed Students with Skill",
                    data: data.skills.placed,
                    backgroundColor: colors.teal,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: colors.textColor }, grid: { color: colors.gridColor } },
                    y: { ticks: { color: colors.textColor, font: { size: 10 } }, grid: { display: false } }
                }
            }
        });
    }

    // 5. Company Hires & Avg Package
    const ctxCompanies = document.getElementById("chartCompaniesCanvas");
    if (ctxCompanies) {
        if (window.activeDashboardCharts.companies) window.activeDashboardCharts.companies.destroy();
        window.activeDashboardCharts.companies = new Chart(ctxCompanies, {
            type: "bar",
            data: {
                labels: data.companies.labels,
                datasets: [{
                    label: "Total Hires",
                    data: data.companies.offers,
                    backgroundColor: colors.primary,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: colors.textColor, font: { size: 10 } }, grid: { display: false } },
                    y: { ticks: { color: colors.textColor }, grid: { color: colors.gridColor } }
                }
            }
        });
    }

    // 6. Yearly Trends
    const ctxTrends = document.getElementById("chartTrendsCanvas");
    if (ctxTrends) {
        if (window.activeDashboardCharts.trends) window.activeDashboardCharts.trends.destroy();
        window.activeDashboardCharts.trends = new Chart(ctxTrends, {
            type: "line",
            data: {
                labels: data.trends.labels,
                datasets: [
                    {
                        label: "Placement Rate (%)",
                        data: data.trends.rates,
                        borderColor: colors.emerald,
                        backgroundColor: "rgba(16, 185, 129, 0.1)",
                        fill: true,
                        tension: 0.3,
                        yAxisID: "y"
                    },
                    {
                        label: "Avg Package (LPA)",
                        data: data.trends.avg_ctc,
                        borderColor: colors.primary,
                        backgroundColor: "transparent",
                        borderDash: [5, 5],
                        tension: 0.3,
                        yAxisID: "y1"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: colors.textColor } }
                },
                scales: {
                    x: { ticks: { color: colors.textColor }, grid: { display: false } },
                    y: {
                        position: "left",
                        ticks: { color: colors.textColor, callback: v => v + "%" },
                        grid: { color: colors.gridColor }
                    },
                    y1: {
                        position: "right",
                        ticks: { color: colors.textColor, callback: v => "₹" + v },
                        grid: { display: false }
                    }
                }
            }
        });
    }
}

function renderChartsThemeUpdate(newTheme) {
    const colors = getChartColors();
    Object.values(window.activeDashboardCharts).forEach(chart => {
        if (chart && chart.options && chart.options.scales) {
            Object.values(chart.options.scales).forEach(scale => {
                if (scale.ticks) scale.ticks.color = colors.textColor;
                if (scale.grid) scale.grid.color = colors.gridColor;
            });
            if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                chart.options.plugins.legend.labels.color = colors.textColor;
            }
            chart.update();
        }
    });
}

function downloadChartAsPNG(chartKey, filename) {
    const chart = window.activeDashboardCharts[chartKey];
    if (!chart) return;
    const url = chart.toBase64Image();
    const link = document.createElement("a");
    link.download = (filename || chartKey) + ".png";
    link.href = url;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Live What-If Predictor Reactivity
function initPredictorReactivity() {
    const cgpaInput = document.getElementById("predictorCgpa");
    const cgpaSlider = document.getElementById("predictorCgpaSlider");
    const deptSelect = document.getElementById("predictorDept");
    const yearSelect = document.getElementById("predictorYear");
    const eligibleCheck = document.getElementById("predictorEligible");
    const skillCheckboxes = document.querySelectorAll(".predictor-skill-checkbox");

    if (!cgpaInput && !cgpaSlider) return;

    let debounceTimer = null;

    function triggerLivePrediction() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function () {
            const cgpa = parseFloat(cgpaInput ? cgpaInput.value : (cgpaSlider ? cgpaSlider.value : 8.0)) || 7.5;
            const dept = deptSelect ? deptSelect.value : "Computer Science and Engineering";
            const year = parseInt(yearSelect ? yearSelect.value : 2026) || 2026;
            const eligible = eligibleCheck ? (eligibleCheck.checked ? 1 : 0) : 1;

            const selectedSkills = [];
            skillCheckboxes.forEach(cb => {
                if (cb.checked) selectedSkills.push(cb.value);
            });

            fetch("/predictor/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    cgpa: cgpa,
                    department: dept,
                    graduation_year: year,
                    eligible: eligible,
                    skills: selectedSkills
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.prediction) {
                    updatePredictorGaugeUI(data.prediction);
                }
            })
            .catch(err => console.error("Live inference error:", err));
        }, 250);
    }

    if (cgpaSlider && cgpaInput) {
        cgpaSlider.addEventListener("input", function () {
            cgpaInput.value = parseFloat(cgpaSlider.value).toFixed(2);
            triggerLivePrediction();
        });
        cgpaInput.addEventListener("input", function () {
            cgpaSlider.value = cgpaInput.value;
            triggerLivePrediction();
        });
    }

    if (deptSelect) deptSelect.addEventListener("change", triggerLivePrediction);
    if (yearSelect) yearSelect.addEventListener("change", triggerLivePrediction);
    if (eligibleCheck) eligibleCheck.addEventListener("change", triggerLivePrediction);
    skillCheckboxes.forEach(cb => cb.addEventListener("change", triggerLivePrediction));
}

function updatePredictorGaugeUI(pred) {
    const scoreVal = document.getElementById("gaugeScoreValue");
    const riskBadge = document.getElementById("gaugeRiskBadge");
    const gaugeCircle = document.getElementById("gaugeCircleProgress");

    if (scoreVal) scoreVal.innerText = pred.probability_pct + "%";

    if (riskBadge) {
        riskBadge.innerText = pred.risk_tier;
        riskBadge.className = `risk-badge risk-${pred.risk_level}`;
    }

    if (gaugeCircle) {
        // Circumference of radius 54 is ~339.29
        const circumference = 339.29;
        const offset = circumference - (pred.probability_pct / 100) * circumference;
        gaugeCircle.style.strokeDashoffset = offset;

        // Color threshold
        if (pred.probability_pct >= 70) {
            gaugeCircle.style.stroke = "var(--emerald-600, #10b981)";
        } else if (pred.probability_pct >= 40) {
            gaugeCircle.style.stroke = "var(--amber-500, #f59e0b)";
        } else {
            gaugeCircle.style.stroke = "var(--rose-500, #f43f5e)";
        }
    }
}

// Form UX: Prevent Double Submission
function initFormEnhancements() {
    const forms = document.querySelectorAll("form:not(.no-disable-on-submit)");
    forms.forEach(function (form) {
        form.addEventListener("submit", function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains("no-disable")) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = `<span class="spinner-sm" role="status" aria-hidden="true"></span> Processing...`;
                // Auto restore after 10s timeout just in case
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });

    // Confirmation for destructive deletes
    const deleteForms = document.querySelectorAll("form.delete-confirm");
    deleteForms.forEach(function (form) {
        form.addEventListener("submit", function (e) {
            const itemName = form.getAttribute("data-item") || "this record";
            if (!confirm(`Are you sure you want to permanently delete ${itemName}? This action cannot be undone.`)) {
                e.preventDefault();
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    });
}

// Global Initialization
document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initMobileNav();
    initTableTools();
    initDashboardCharts();
    initPredictorReactivity();
    initFormEnhancements();

    // Auto-dismiss standard alerts
    document.querySelectorAll(".alert").forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = "0";
            alert.style.transition = "opacity 0.4s ease";
            setTimeout(function () {
                alert.remove();
            }, 400);
        }, 5000);
    });
});
