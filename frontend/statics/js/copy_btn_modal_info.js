// Копирует в буфер обмена и меняет цвет кнопки
document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('copy-btn');
    var span = document.getElementById('plain-data');

    if (btn && span) {
        btn.addEventListener('click', function () {

            let text = span.textContent;
            navigator.clipboard.writeText(text).then(function () {

                // Optional: анимация или смена цвета иконки
                btn.style.background = "#79e27a99";
                setTimeout(function () {
                    btn.style.background = "#7c848e22";
                }, 100);
            });
        });
    }
});