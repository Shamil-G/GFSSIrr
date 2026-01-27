document.addEventListener('click', e => {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;

    const action = btn.dataset.action;   // approve | finalize | remove
    const protNum = btn.dataset.prot;

    if (!confirm(`Выполнить действие "${action}" для протокола ${protNum}?`)) {
        return;
    }

    callProtocolAction(action, protNum);
});

function callProtocolAction(action, protNum) {
    fetch('/protocol/action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: action,
            prot_num: protNum
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            location.reload();   // или обновить строку без reload
        } else {
            alert(data.message || 'Ошибка выполнения операции');
        }
    })
    .catch(err => {
        console.error(err);
        alert('Ошибка связи с сервером');
    });
}
