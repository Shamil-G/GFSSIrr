function populateDistricts(regionCode, selectedDistrict = null) {
    const districts = window.DISTRICTS;
    const districtSelect = document.getElementById("district-select");

    if (!districts || !districtSelect || !regionCode) return;

    districtSelect.innerHTML = '<option value="" disabled>Выберите район</option>';
    districtSelect.disabled = true;

    const prefix = regionCode.substring(0, 2);

    Object.entries(districts).forEach(([code, name]) => {
        code = String(code).padStart(4, "0");

        if (code.startsWith(prefix) && !code.endsWith("00")) {
            const opt = document.createElement("option");
            opt.value = code;
            opt.textContent = name;

            if (selectedDistrict && code === selectedDistrict) {
                opt.selected = true;
            }

            districtSelect.appendChild(opt);
        }
    });

    districtSelect.disabled = false;
    districtSelect.classList.remove("hidden");
}


export function bindRegionDistrict() {
    const regionSelect = document.getElementById("region-select");
    const districtSelect = document.getElementById("district-select");

    if (!regionSelect || !districtSelect) return;

    // 1. Реакция на смену региона
    regionSelect.addEventListener("change", () => {
        populateDistricts(regionSelect.value);
    });

    // 2. Восстановление при возврате на страницу
    if (regionSelect.value) {
        populateDistricts(regionSelect.value, districtSelect.value);
    }

    // 3. Удаляем placeholder после выбора
    districtSelect.addEventListener("change", () => {
        const placeholder = districtSelect.querySelector('option[value=""]');
        if (placeholder) placeholder.remove();
    });
}


export function bindPhotoReport() {
    const input = document.getElementById("photo-report");
    const output = document.getElementById("photo-file-names");

    if (!input || !output) return;

    input.addEventListener("change", () => {
        output.innerHTML = "";

        if (!input.files.length) return;

        const list = document.createElement("ul");
        list.className = "file-list";

        Array.from(input.files).forEach(file => {
            const item = document.createElement("li");
            item.textContent = file.name;
            list.appendChild(item);
        });

        output.appendChild(list);
    });
}

export function setTheme() {
    const html = document.documentElement;
    const icon = document.getElementById("theme-icon");
    if (!icon) return;

    function updateIcon() {
        icon.src =
            html.dataset.theme === "dark"
                ? "/static/img/color-icon.png"
                : "/static/img/dark-icon.png";
    }

    updateIcon();

    window.toggleTheme = function () {
        const newTheme = html.dataset.theme === "dark" ? "color" : "dark";
        html.dataset.theme = newTheme;
        localStorage.setItem("theme", newTheme);
        updateIcon();
    };
}

export function bindBinOrganization() {
    const binInput = document.getElementById("bin-organization");
    const nameInput = document.getElementById("name-organization");

    if (!binInput || !nameInput) return;

    let lastBin = "";

    binInput.addEventListener("input", () => {
        const bin = binInput.value;

        // ждём ровно 12 цифр
        if (bin.length !== 12) {
            nameInput.value = "";
            lastBin = "";
            return;
        }

        // защита от повторного запроса
        if (bin === lastBin) return;
        lastBin = bin;

        fetch("/api/organization", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ bin })
        })
        .then(r => r.ok ? r.json() : null)
        .then(data => {
            if (data && data.name) {
                nameInput.value = data.name;
            } else {
                nameInput.value = "";
            }
        })
        .catch(() => {
            nameInput.value = "";
        });
    });
}


document.addEventListener("DOMContentLoaded", () => {
    bindRegionDistrict();
    bindPhotoReport();
    setTheme();
    bindBinOrganization();
});
