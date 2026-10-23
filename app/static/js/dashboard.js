/**
 * Dashboard interactivity:
 * Dynamic chart reloading on filter change, download buttons, and KPI animations.
 */

document.addEventListener("DOMContentLoaded", function () {
    const filterForm = document.getElementById("dashboardFilterForm");
    
    // Refresh chart images with cache buster on demand
    const refreshButtons = document.querySelectorAll(".btn-refresh-chart");
    refreshButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const chartImgId = btn.getAttribute("data-target");
            const chartImg = document.getElementById(chartImgId);
            if (chartImg) {
                const currentSrc = new URL(chartImg.src, window.location.origin);
                currentSrc.searchParams.set("t", Date.now());
                chartImg.src = currentSrc.toString();
            }
        });
    });

    // Download chart image feature
    const downloadButtons = document.querySelectorAll(".btn-download-chart");
    downloadButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            const chartImgId = btn.getAttribute("data-target");
            const chartImg = document.getElementById(chartImgId);
            if (chartImg) {
                const a = document.createElement("a");
                a.href = chartImg.src;
                a.download = `${chartImgId}_chart.png`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }
        });
    });
});
