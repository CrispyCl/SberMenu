const BadAlertClose = document.querySelector(".bad_alert_box .close"),
    GoodAlertClose = document.querySelector(".good_alert_box .close"),
    WarningAlertClose = document.querySelector(".warning_alert_box .close"),
    GoodAlertBox = document.querySelector(".good_alert_box"),
    BadAlertBox = document.querySelector(".bad_alert_box"),
    WarningAlertBox = document.querySelector(".warning_alert_box"),
    GoodAlertProgress = document.querySelector(".good_alert_progress"),
    BadAlertProgress = document.querySelector(".bad_alert_progress"),
    WarningAlertProgress = document.querySelector(".warning_alert_progress"),
    Badmess = document.querySelector(".bad_alert_message .text.text-2"),
    Warningmess = document.querySelector(".warning_alert_message .text.text-2"),
    Goodmess = document.querySelector(".good_alert_message .text.text-2"),
    Styles = document.querySelector(".PC");

function AddMessage(mes, close_time=5000) {
    Styles.style.setProperty("--message_time", `${close_time / 1000}s`)
    if (typeof mes === "string"){
        mes = JSON.parse(mes);
    }
    console.log(mes);
    if (mes["status"] == 404) {
        return;
    }
    if (mes["status"] == 0) {
        BadAlertBox.classList.add("alert_show");
        BadAlertProgress.classList.add("active");
        Badmess.appendChild(document.createTextNode(mes["text"]));

        if (BadAlertBox.classList.contains("alert_show")) {
        setTimeout(() => {
            BadAlertBox.classList.remove("alert_show");
            setTimeout(() => {
            BadAlertProgress.classList.remove("active");
            }, close_time - 100);
        }, close_time);
        }
    } else if (mes["status"] == 1) {
        GoodAlertBox.classList.add("alert_show");
        GoodAlertProgress.classList.add("active");
        Goodmess.appendChild(document.createTextNode(mes["text"]));

        if (GoodAlertBox.classList.contains("alert_show")) {
        setTimeout(() => {
            GoodAlertBox.classList.remove("alert_show");
            setTimeout(() => {
            GoodAlertProgress.classList.remove("active");
            }, close_time - 100);
        }, close_time);
        }
    } else {
        WarningAlertBox.classList.add("alert_show");
        WarningAlertProgress.classList.add("active");
        Warningmess.appendChild(document.createTextNode(mes["text"]));

        if (WarningAlertBox.classList.contains("alert_show")) {
        setTimeout(() => {
            WarningAlertBox.classList.remove("alert_show");
            setTimeout(() => {
            GoodAlertProgress.classList.remove("active");
            }, close_time - 100);
        }, close_time);
        }
    }
}

BadAlertClose.addEventListener("click", () => {
  BadAlertBox.classList.remove("alert_show");
});

GoodAlertClose.addEventListener("click", () => {
  GoodAlertBox.classList.remove("alert_show");
});
