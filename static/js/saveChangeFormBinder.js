export function serializeParams(params) {
    const isJson = Object.values(params).some(v => typeof v === 'object' && v !== null);

    const headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': isJson ? 'application/json' : 'application/x-www-form-urlencoded'
    };

    const body = isJson
        ? JSON.stringify(params)
        : new URLSearchParams(params).toString();

    return { headers, body };
}

export const SaveChangeFormBinder = {
    role: 'save-change-form',

    attach(button) {
        if (button.__saveChangeFormBound) return;
        button.__saveChangeFormBound = true;

        button.addEventListener('change', async (e) => {
            e.preventDefault();

            const value = button.value;
            const targetZone = button.dataset.targetId;

            if (!value) {
                console.error('SaveChangeFormBinder: Input has no value');
                return;
            }
            if (!targetZone) {
                console.error('SaveChangeFormBinder: Input has no targetZone');
                return;
            }
            const params = {period: value};
            const { headers, body } = serializeParams(params)

            try {
                const response = await fetch('/change-list-protocols', 
                                { method: 'POST', headers, body }
                );

                if (!response.ok) {
                    console.error('SaveFormBinder: server error', response.status);
                    return;
                }

                const html = await response.text();
                const target = document.getElementById(targetZone);
                target.innerHTML = html;

                console.log('SaveFormBinder: success');
            } catch (err) {
                console.error('SaveFormBinder: fetch error', err);
            }
        });
    },

    attachAll(zone = document) {
        const buttons = zone.querySelectorAll(`[data-role="${this.role}"]`);
        console.log('SaveChangeFormBinder. attachAll\nzone: ', zone, '\nbuttons:', buttons);
        buttons.forEach(btn => this.attach(btn));
    }
};
