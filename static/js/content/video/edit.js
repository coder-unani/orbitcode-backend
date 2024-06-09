const btnWatchDelete = document.querySelector('#btnWatchDelete');
btnWatchDelete.addEventListener('click', () => {
    const watchId = btnWatchDelete.dataset.watchId;
    fetch(`/api/watch/${watchId}`, {
        method: 'DELETE',
    })
        .then((res) => res.json())
        .then((data) => {
        if (data.success) {
            location.href = '/content/video';
        } else {
            alert(data.message);
        }
        });

});
const btnWatchAdd = document.querySelector('#btnWatchAdd');
btnWatchAdd.addEventListener('click', () => {

});
