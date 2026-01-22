export function bindRegionDistrict() {
    const districts = window.DISTRICTS;
    if (!districts) return;

    const regionSelect = document.getElementById("region-select");
    const districtSelect = document.getElementById("district-select");
    if (!regionSelect || !districtSelect) return;

    regionSelect.addEventListener("change", () => {
        const regionCode = regionSelect.value;

        districtSelect.innerHTML = '<option value="" disabled selected>Выберите район</option>';
        districtSelect.disabled = true;

        if (!regionCode) return;

        const prefix = regionCode.substring(0, 2);

        Object.entries(districts).forEach(([code, name]) => {
            code = String(code).padStart(4, "0");

            if (code.startsWith(prefix) && !code.endsWith("00")) {
                const opt = document.createElement("option");
                opt.value = code;
                opt.textContent = name;
                districtSelect.appendChild(opt);
            }
        });

        districtSelect.disabled = false;
    });
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

document.addEventListener("DOMContentLoaded", () => {
    bindRegionDistrict();
    bindPhotoReport();
});
