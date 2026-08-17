/* =========================================================================
   Menu mobile
   Un'unica implementazione per tutte le pagine. Il pannello e' gia' nel
   markup con la classe "hidden": qui gestiamo apertura, chiusura e stato
   accessibile del pulsante.
   ========================================================================= */
document.addEventListener("DOMContentLoaded", function () {
  var btn  = document.getElementById("mobile-toggle");
  var menu = document.getElementById("mobile-menu");
  if (!btn || !menu) return;

  var icon = btn.querySelector(".material-symbols-outlined");

  function setOpen(open) {
    menu.classList.toggle("hidden", !open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    btn.setAttribute("aria-label", open ? "Chiudi il menu" : "Apri il menu");
    if (icon) icon.textContent = open ? "close" : "menu";
  }

  btn.addEventListener("click", function () {
    setOpen(menu.classList.contains("hidden"));
  });

  /* Chiude quando si sceglie una voce */
  Array.prototype.forEach.call(menu.querySelectorAll("a"), function (a) {
    a.addEventListener("click", function () { setOpen(false); });
  });

  /* Chiude con Esc */
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });

  /* Se si allarga la finestra oltre il breakpoint, il pannello va richiuso:
     altrimenti resta aperto e riappare tornando su mobile. */
  var wide = window.matchMedia("(min-width: 768px)");
  var onChange = function (e) { if (e.matches) setOpen(false); };
  if (wide.addEventListener) wide.addEventListener("change", onChange);
  else wide.addListener(onChange);
});


/* =========================================================================
   Modale WhatsApp
   Il pulsante flottante non apre piu' un link vuoto: mostra una finestra
   con un messaggio precompilato che il visitatore puo' ritoccare, poi apre
   WhatsApp (wa.me) direttamente sul numero con il testo pronto.
   Nessuna dipendenza: JS puro, funziona su qualsiasi hosting.
   ========================================================================= */
var WHATSAPP_NUMERO = (window.SITO || {}).whatsappNumero || "";
var WHATSAPP_MESSAGGIO = (window.SITO || {}).whatsappMessaggio || "";

document.addEventListener("DOMContentLoaded", function () {
  var fab = document.getElementById("whatsapp-fab");
  if (!fab) return;

  /* Il modale viene costruito una volta sola e riusato */
  var overlay = document.createElement("div");
  overlay.id = "wa-overlay";
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");
  overlay.setAttribute("aria-label", "Scrivi a Laura su WhatsApp");
  overlay.className = "fixed inset-0 z-[100] hidden items-end md:items-center justify-center bg-black/40 p-sm";
  overlay.innerHTML =
    '<div class="bg-white w-full max-w-md rounded-t-xl md:rounded-xl shadow-2xl overflow-hidden" id="wa-card">' +
      '<div class="flex items-center justify-between px-md py-sm" style="background:#B8735A">' +
        '<div class="flex items-center gap-xs text-white">' +
          '<svg fill="currentColor" height="20" viewBox="0 0 24 24" width="20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.417-.415.833-.93.96-1.129.127-.198.063-.372-.026-.52-.089-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.464 3.488"/></svg>' +
          '<span class="font-label text-label uppercase tracking-wider">Scrivi a Laura</span>' +
        '</div>' +
        '<button aria-label="Chiudi" class="text-white/90 hover:text-white p-1" id="wa-close" type="button">' +
          '<span class="material-symbols-outlined">close</span>' +
        '</button>' +
      '</div>' +
      '<div class="p-md space-y-sm">' +
        '<p class="font-body text-body-sm text-on-surface-variant">Il messaggio è già pronto: puoi mandarlo così o farlo tuo. Si aprirà WhatsApp con il testo inserito.</p>' +
        '<label class="font-label text-micro uppercase tracking-wider text-on-surface-variant" for="wa-text">Il tuo messaggio</label>' +
        '<textarea class="w-full border border-light-border rounded-lg p-sm font-body text-body-sm text-on-surface focus:border-primary focus:ring-primary" id="wa-text" rows="4"></textarea>' +
        '<a class="flex items-center justify-center gap-xs w-full text-center text-white py-sm rounded-lg font-label text-label uppercase tracking-wider transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg" href="#" id="wa-send" rel="noopener" style="background:#25D366" target="_blank">' +
          '<span>Apri WhatsApp</span>' +
          '<span class="material-symbols-outlined icon-sm" aria-hidden="true">arrow_forward</span>' +
        '</a>' +
      '</div>' +
    '</div>';
  document.body.appendChild(overlay);

  var area = overlay.querySelector("#wa-text");
  var send = overlay.querySelector("#wa-send");

  function apri() {
    area.value = WHATSAPP_MESSAGGIO;
    overlay.classList.remove("hidden");
    overlay.classList.add("flex");
    area.focus();
  }
  function chiudi() {
    overlay.classList.add("hidden");
    overlay.classList.remove("flex");
    fab.focus();
  }

  fab.addEventListener("click", function (e) { e.preventDefault(); apri(); });
  overlay.querySelector("#wa-close").addEventListener("click", chiudi);
  overlay.addEventListener("click", function (e) { if (e.target === overlay) chiudi(); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !overlay.classList.contains("hidden")) chiudi();
  });

  /* il link si compone al momento del clic, cosi' porta il testo corrente */
  send.addEventListener("click", function () {
    send.href = "https://wa.me/" + WHATSAPP_NUMERO + "?text=" + encodeURIComponent(area.value.trim());
  });
});


/* FAQ della home */
function toggleFaq(i) {
  var body = document.getElementById("faq-body-" + i);
  var icon = document.getElementById("faq-icon-" + i);
  if (!body || !icon) return;
  var btn = icon.closest("button");
  var aperto = body.classList.toggle("hidden") === false;
  btn.setAttribute("aria-expanded", aperto ? "true" : "false");
  icon.classList.toggle("rotate-180");
}
