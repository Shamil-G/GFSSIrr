// Подмена submit в форме
export const SubmitFormBinder = {
    role: 'submit-form',

    attach(form) {
        if (form.__submitFormBound) return;
        form.__submitFormBound = true;
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const targetUrl = form.dataset.targetUrl;
            const formData = new FormData(form);

            if (!targetUrl) {
                console.error('SubmitFormBinder: Input has no targetUrl for Zone');
                return;
            }

            try {
                const response = await fetch(targetUrl, { method: 'POST', body: formData }
                );

                if (!response.ok) {
                    console.error('SubmitFormBinder: server error', response.status);
                    return;
                }
                //form.querySelector('#event_date').value = '';
                form.querySelectorAll('input').forEach(input => { input.value = ''; });
                
                const messageSpan = form.querySelector('.save-message'); 
                messageSpan.textContent = 'Сохранено успешно'; 
                setTimeout(() => { messageSpan.textContent = ''; }, 3000);
            } catch (err) {
                console.error('SubmitFormBinder: fetch error', err);
            }
        });
    },

    attachAll(zone = document) {
        const forms = zone.querySelectorAll(`[data-role="${this.role}"]`);
        console.log('SubmitFormBinder. attachAll\nzone: ', zone, '\nbuttons:', forms);
        forms.forEach(form => this.attach(form));
    }
};
