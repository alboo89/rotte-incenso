# Rotte d'incenso — sito di produzione

Eleventy (generatore statico) + Sveltia CMS (backoffice) + Tailwind compilato in build.
Nessun database, nessun costo di hosting: i contenuti sono file nel repository.

## Struttura

```
src/
  _includes/base.njk     layout unico: navbar, footer, CTA, WhatsApp
  _data/sito.json        contatti, WhatsApp, CTA, chiave form   ← editabile dal CMS
  _data/home.json        tutti i testi della Home               ← editabile dal CMS
  _data/servizi.json     pagina Servizi                         ← editabile dal CMS
  _data/contatti.json    pagina Contatti (incluse fasce budget) ← editabile dal CMS
  destinazioni/*.md      una destinazione per file              ← editabile dal CMS
  admin/                 il backoffice (Sveltia CMS)
  assets/                brand.css, brand.js, immagini
tailwind.config.js       token di design (colori, tipografia)
```

## Comandi

```
npm install        una tantum
npm run dev        anteprima locale su http://localhost:8080
npm run build      genera il sito in _site/
```

## Messa online (una tantum)

1. Creare un repository GitHub e caricare questa cartella.
2. In `src/admin/config.yml` sostituire `IL-TUO-UTENTE/IL-TUO-REPO` col nome vero del repo.
3. Collegare il repo a Netlify (o Cloudflare Pages): build `npm run build`, publish `_site`.
   Con Netlify il file `netlify.toml` configura già tutto.
4. Registrarsi su web3forms.com (gratis), ottenere la Access Key e inserirla
   dal CMS in Impostazioni → Chiave Web3Forms. Le richieste del form arrivano
   via email a Laura.
5. Per il login di Laura al backoffice: su GitHub creare una OAuth App
   (Settings → Developer settings) e configurarla su Netlify
   (Site settings → Access control → OAuth). Laura entra su /admin/ col suo
   account GitHub (da invitare come collaboratore del repo).

## Al lancio, da ricordare

- Rimuovere le due righe `robots` in `src/_includes/base.njk` e il Disallow in `src/robots.txt`.
- Sostituire i segnaposto: ritratti (`ritratto-laura.jpg`, `laura-taccuino.jpg`),
  foto delle destinazioni (dal CMS), numero di telefono e WhatsApp veri.
- Privacy Policy, Cookie Policy e banner di consenso (i link nel footer sono ancora vuoti).
- Favicon e meta Open Graph.

## Bilingue

Il sito è in italiano (alla radice) e inglese (sotto `/en/`, con slug propri:
`/en/destinations.html`, `/en/services.html`, `/en/contact.html`). Il selettore
IT/EN in navbar porta alla pagina corrispondente nell'altra lingua. Ogni coppia
di pagine è collegata con `hreflang` (anche nella sitemap), quindi Google serve
la lingua giusta a ciascun visitatore.

I contenuti inglesi sono file separati (`home_en.json`, `servizi_en.json`,
`contatti_en.json`, più i campi `titolo_en`/`descrizione_en` nelle destinazioni):
Laura li modifica dal CMS esattamente come quelli italiani. Le traduzioni
attuali sono una prima stesura da rivedere.

## SEO — già incluso

- meta description per pagina (modificabile dal CMS), canonical, hreflang it/en/x-default
- Open Graph (titolo, descrizione, immagine `og-image.png` generata dal logo)
- `sitemap.xml` con le 8 pagine e le alternanze di lingua
- favicon e apple-touch-icon
- semantica corretta (h1 unico, landmark), alt sulle immagini, CSS statico leggero

## SEO — da fare al lancio (non automatizzabile da qui)

1. Rimuovere il `noindex` dal layout e il Disallow da `robots.txt`.
2. Verificare il dominio su Google Search Console e inviare la sitemap.
3. Compilare descrizioni SEO definitive dal CMS (quelle attuali sono bozze).
4. Foto reali con alt curati: pesano più di qualsiasi meta tag.
5. Nel tempo: contenuti. Un sito di 4 pagine si posiziona sul nome del brand,
   non su "viaggi su misura vietnam" — se la SEO organica diventerà un canale,
   servirà una sezione di contenuti (il vecchio Journal, reintrodotto con criterio).

## Cosa modifica Laura dal CMS

Tutti i testi delle quattro pagine in entrambe le lingue, le foto (caricamento
diretto), le destinazioni (aggiunta/rimozione/riordino), le FAQ, le etichette e le
fasce di budget del form, il numero e i messaggi WhatsApp, i testi della CTA e le
descrizioni SEO. Ogni salvataggio ripubblica il sito da solo in un paio di minuti.
