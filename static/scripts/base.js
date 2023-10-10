var script = document.createElement('script');
script.src = '//code.jquery.com/jquery-3.6.3.min.js';
document.getElementsByTagName('head')[0].appendChild(script);


const BadAlertClose = document.querySelector('.bad_alert_box .close'),
    GoodAlertClose = document.querySelector('.good_alert_box .close'),
    WarningAlertClose = document.querySelector('.warning_alert_box .close'),
    GoodAlertBox = document.querySelector('.good_alert_box'),
    BadAlertBox = document.querySelector('.bad_alert_box'),
    WarningAlertBox = document.querySelector('.warning_alert_box'),
    GoodAlertProgress = document.querySelector('.good_alert_progress'),
    BadAlertProgress = document.querySelector('.bad_alert_progress'),
    WarningAlertProgress = document.querySelector('.warning_alert_progress'),
    Badmess = document.querySelector('.bad_alert_message .text.text-2'),
    Warningmess = document.querySelector('.warning_alert_message .text.text-2'),
    Goodmess = document.querySelector('.good_alert_message .text.text-2');



let mes = JSON.parse(document.querySelector('.message-content').innerHTML);

$(function () {
    if (mes['status'] != 404) {
        mes = JSON.parse(mes);
        if (mes['status'] == 404) {
            return
        }
        if (mes['status'] == 0) {
            BadAlertBox.classList.add('alert_show');
            BadAlertProgress.classList.add('active');
            Badmess.appendChild(document.createTextNode(mes['text']));


            if (BadAlertBox.classList.contains('alert_show')) {
                setTimeout(() => {
                    BadAlertBox.classList.remove('alert_show');
                    setTimeout(() => {
                        BadAlertProgress.classList.remove('active');
                    }, 4900);
                }, 5000);
            };
        }
        else if (mes['status'] == 1) {
            GoodAlertBox.classList.add('alert_show')
            GoodAlertProgress.classList.add('active')
            Goodmess.appendChild(document.createTextNode(mes['text']))


            if (GoodAlertBox.classList.contains('alert_show')) {
                setTimeout(() => {
                    GoodAlertBox.classList.remove('alert_show')
                    setTimeout(() => {
                        GoodAlertProgress.classList.remove('active')
                    }, 4900);
                }, 5000);
            }
        }
        else {
            WarningAlertBox.classList.add('alert_show')
            WarningAlertProgress.classList.add('active')
            Warningmess.appendChild(document.createTextNode(mes['text']))


            if (WarningAlertBox.classList.contains('alert_show')) {
                setTimeout(() => {
                    WarningAlertBox.classList.remove('alert_show')
                    setTimeout(() => {
                        GoodAlertProgress.classList.remove('active')
                    }, 4900);
                }, 5000);
            }
        }
    }
});





BadAlertClose.addEventListener('click', () => {
    BadAlertBox.classList.remove('alert_show');

});

GoodAlertClose.addEventListener('click', () => {
    GoodAlertBox.classList.remove('alert_show');
});


!function () { "use strict"; function e(e, t) { const s = e.target.closest(`[${t.toggle}]`), o = e.target.closest(`[${t.remove}]`), l = e.target.closest(`[${t.add}]`); s && (e.preventDefault(), ((e, t) => { const s = e.getAttribute(t.toggle); document.querySelectorAll(`[${t.toggle}]`).forEach((s => { if (!s.hasAttribute(t.parallel) && s !== e) { document.querySelector(s.getAttribute(t.toggle)).classList.remove(s.getAttribute(t.class)); const o = e.getAttribute(t.self); o && e.classList.remove(o) } })), document.querySelector(s)?.classList.toggle(e.getAttribute(t.class)); const o = e.getAttribute(t.self); o && e.classList.toggle(o), t.onToggle(e) })(s, t)), o && (e.preventDefault(), ((e, t) => { const s = e.getAttribute(t.remove), o = e.getAttribute(t.class); document.querySelectorAll(s).forEach((e => { e.classList.remove(o) })); const l = e.getAttribute(t.self); l && e.classList.remove(l), t.onRemove(e) })(o, t)), l && (e.preventDefault(), ((e, t) => { const s = e.getAttribute(t.add), o = e.getAttribute(t.class); document.querySelectorAll(s).forEach((e => { e.classList.add(o) })); const l = e.getAttribute(t.self); l && e.classList.add(l), t.onAdd(e) })(l, t)), s || o || l || ((e, t) => { const s = document.querySelectorAll(`[${t.rcoe}]`); Array.from(s).forEach((s => { let o = s.getAttribute(t.toggle), l = s.getAttribute(t.class); if (!e.target.closest(o)) { document.querySelector(o)?.classList.remove(l); const e = s.getAttribute(t.self); e && s.classList.remove(e), t.onRcoe(s) } })) })(e, t) } const t = { toggle: "easy-toggle", add: "easy-add", remove: "easy-remove", class: "easy-class", rcoe: "easy-rcoe", parallel: "easy-parallel", self: "easy-self", selfRcoe: "easy-self-rcoe", onToggle(e) { }, onAdd(e) { }, onRemove(e) { }, onRcoe(e) { } }; document.addEventListener("DOMContentLoaded", (() => { document.addEventListener("click", (s => { e(s, t) })) })) }();