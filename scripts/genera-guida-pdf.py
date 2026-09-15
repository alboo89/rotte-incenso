#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la guida al backoffice per Laura: docs/Guida-backoffice-Rotte-dincenso.pdf

    python3 scripts/genera-guida-pdf.py

Richiede: pip install reportlab fonttools brotli
Il catalogo delle icone viene letto da src/_data/icone.json, quindi resta
allineato da solo al menu a tendina del CMS: se aggiungi un'icona lì dentro,
basta rilanciare questo script perché compaia anche nella guida.

Nota tecnica: ReportLab non applica le legature OpenType, quindi le icone non
si possono scrivere per nome ("favorite"). Servono i codepoint veri, che
ricaviamo dal font completo in node_modules e teniamo in cache qui accanto.
"""
import json, os, sys, tempfile
from fontTools.ttLib import TTFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLFont
from reportlab.lib.colors import Color

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RADICE)
USCITA = 'docs/Guida-backoffice-Rotte-dincenso.pdf'
CACHE_CODEPOINT = 'scripts/icone-codepoint.json'
MESE = 'settembre 2026'

# ---------------------------------------------------------------- colori
def rgb(hexstr):
    h = hexstr.lstrip('#')
    return Color(*(int(h[i:i+2], 16) / 255 for i in (0, 2, 4)))

CARTA       = rgb('#FAF8F4')   # fondo pagina
VERDE       = rgb('#516442')   # titoli
VERDE_SCURO = rgb('#4A5A3E')   # fascia in fondo alla copertina
RAME        = rgb('#B8735A')   # occhielli, bordi
RAME_SCURO  = rgb('#A55C41')   # icone, pallini numerati
TESTO       = rgb('#444840')
TESTO_FORTE = rgb('#1B1C1A')
TENUE       = rgb('#A09A90')   # piè di pagina
CARD        = rgb('#F2ECE3')   # righe e riquadri chiari
NOTA        = rgb('#E8DED1')   # riquadri di avvertenza

# ------------------------------------------------------------- geometria
L, A = 595, 842                # A4 in punti
MARGINE, DESTRA = 58, 537
COLONNA = DESTRA - MARGINE     # 479

# ----------------------------------------------------------------- font
FAMIGLIE = {
    'Corm':    ['src/assets/fonts/cormorant-garamond-latin-300-normal.woff2',
                'node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-300-normal.woff2'],
    'CormIt':  ['node_modules/@fontsource/cormorant-garamond/files/cormorant-garamond-latin-300-italic.woff2',
                'src/assets/fonts/cormorant-garamond-latin-400-italic.woff2'],
    'DMLight': ['src/assets/fonts/dm-sans-latin-300-normal.woff2'],
    'DMReg':   ['src/assets/fonts/dm-sans-latin-400-normal.woff2'],
    'DMSemi':  ['src/assets/fonts/dm-sans-latin-600-normal.woff2'],
    # font completo: serve la tabella cmap con i codepoint delle icone,
    # che il subset del sito non conserva. ReportLab incorpora solo i
    # glifi usati, quindi il PDF resta leggero.
    'MSym':    ['node_modules/material-symbols/material-symbols-outlined.woff2'],
}

def registra_font(tmp):
    for nome, candidati in FAMIGLIE.items():
        percorso = next((p for p in candidati if os.path.exists(p)), None)
        if not percorso:
            sys.exit(f"Font mancante per «{nome}». Hai lanciato npm install?\n"
                     f"  cercato in: {', '.join(candidati)}")
        ttf = os.path.join(tmp, nome + '.ttf')
        f = TTFont(percorso)
        f.flavor = None                      # woff2 -> ttf
        f.save(ttf)
        pdfmetrics.registerFont(RLFont(nome, ttf))

def mappa_icone():
    """nome icona -> codepoint, dalle legature del font completo."""
    sorgente = FAMIGLIE['MSym'][0]
    nomi = {i['nome'] for i in json.load(open('src/_data/icone.json', encoding='utf-8'))}
    nomi |= {'check_circle', 'info', 'menu', 'close'}   # usate dalla guida stessa
    if not os.path.exists(sorgente):
        mappa = json.load(open(CACHE_CODEPOINT, encoding='utf-8'))
        print(f"font completo assente: uso la cache {CACHE_CODEPOINT}")
        return {k: chr(v) for k, v in mappa.items()}
    f = TTFont(sorgente)
    g2c = {v: chr(k) for k, v in f.getBestCmap().items()}
    trovate = {}
    for lookup in f['GSUB'].table.LookupList.Lookup:
        for st in lookup.SubTable:
            st = st.ExtSubTable if lookup.LookupType == 7 else st
            if not hasattr(st, 'ligatures'):
                continue
            for primo, ligs in st.ligatures.items():
                for lig in ligs:
                    nome = g2c.get(primo, '?') + ''.join(g2c.get(c, '?') for c in lig.Component)
                    if nome in nomi:
                        trovate[nome] = ord(g2c[lig.LigGlyph])
    mancanti = nomi - set(trovate)
    assert not mancanti, f"icone inesistenti nel font: {sorted(mancanti)}"
    json.dump(dict(sorted(trovate.items())), open(CACHE_CODEPOINT, 'w'), indent=1)
    return {k: chr(v) for k, v in trovate.items()}

# ------------------------------------------------------------ impaginato
class Guida:
    """Le coordinate y sono distanze dal bordo ALTO della pagina (come si legge)."""

    def __init__(self, percorso, icone):
        self.c = canvas.Canvas(percorso, pagesize=(L, A))
        self.c.setTitle("Guida al backoffice — Rotte d'incenso")
        self.c.setAuthor('Alberto Piras')
        self.ico = icone
        self.pagina = 0
        self.y = 0

    # --- primitive ---------------------------------------------------
    def _testo(self, x, y, s, font, size, colore, ancora='l', spaziatura=0):
        self.c.setFont(font, size)
        self.c.setFillColor(colore)
        if spaziatura:
            # La spaziatura fra lettere si imposta solo dal text object, e in PDF
            # resta valida anche dopo (Tc appartiene allo stato del testo, non al
            # blocco): va riazzerata subito, altrimenti sbrodola su tutta la pagina.
            t = self.c.beginText(x, A - y)
            t.setFont(font, size)
            t.setFillColor(colore)
            t.setCharSpace(spaziatura)
            t.textOut(s)
            t.setCharSpace(0)
            self.c.drawText(t)
        elif ancora == 'c':
            self.c.drawCentredString(x, A - y, s)
        elif ancora == 'r':
            self.c.drawRightString(x, A - y, s)
        else:
            self.c.drawString(x, A - y, s)

    def _spezza(self, s, font, size, larghezza):
        righe, riga = [], ''
        for parola in s.split():
            prova = (riga + ' ' + parola).strip()
            if pdfmetrics.stringWidth(prova, font, size) <= larghezza:
                riga = prova
            else:
                if riga:
                    righe.append(riga)
                riga = parola
        if riga:
            righe.append(riga)
        return righe

    def _blocco(self, s, x, larghezza, font, size, interlinea, colore):
        righe = [r for p in s.split('\n') for r in self._spezza(p, font, size, larghezza)]
        for riga in righe:
            self._testo(x, self.y, riga, font, size, colore)
            self.y += interlinea
        self.y -= interlinea          # la y resta sull'ultima riga scritta

    def _icona(self, x, y, nome, size, colore=RAME_SCURO):
        self._testo(x, y, self.ico[nome], 'MSym', size, colore)

    # --- pagine ------------------------------------------------------
    def _fondo(self):
        self.c.setFillColor(CARTA)
        self.c.rect(0, 0, L, A, fill=1, stroke=0)

    def copertina(self, titolo, sottotitolo, testo, firma):
        self._fondo()
        self.c.setFillColor(VERDE_SCURO)
        self.c.rect(0, 0, L, 10, fill=1, stroke=0)
        self._testo(L / 2, 361, titolo, 'Corm', 34, VERDE, 'c')
        self._testo(L / 2, 388, sottotitolo, 'CormIt', 16, RAME, 'c')
        self.y = 436
        for riga in self._spezza(testo, 'DMLight', 10.5, 330):
            self._testo(L / 2, self.y, riga, 'DMLight', 10.5, TESTO, 'c')
            self.y += 16
        self._testo(L / 2, 722, firma, 'DMReg', 9, TENUE, 'c')

    def apri(self, occhiello, titolo):
        if self.pagina:
            self._pie()
        self.c.showPage()          # chiude la copertina o la pagina precedente
        self.pagina += 1
        self._fondo()
        self._testo(MARGINE, 70.5, occhiello.upper(), 'DMSemi', 8, RAME, spaziatura=1.1)
        self._testo(MARGINE, 93, titolo, 'Corm', 26, VERDE)
        self.c.setStrokeColor(RAME)
        self.c.setLineWidth(2)
        self.c.line(MARGINE, A - 102, MARGINE + 46, A - 102)
        self.y = 129

    def _pie(self):
        self._testo(MARGINE, 812, "Rotte d’incenso — guida al backoffice", 'DMReg', 7.5, TENUE)
        self._testo(DESTRA - 4, 812, str(self.pagina), 'DMReg', 7.5, TENUE, 'r')

    def chiudi(self, titolo, testo, contatto, data):
        self._pie()
        self.c.showPage()
        self._fondo()
        self.c.setFillColor(VERDE_SCURO)
        self.c.rect(0, 0, L, 10, fill=1, stroke=0)
        self._testo(L / 2, 330, titolo, 'Corm', 30, VERDE, 'c')
        self.y = 380
        for riga in self._spezza(testo, 'DMLight', 10.5, 340):
            self._testo(L / 2, self.y, riga, 'DMLight', 10.5, TESTO, 'c')
            self.y += 16
        self._testo(L / 2, self.y + 26, contatto, 'DMSemi', 10, VERDE, 'c')
        self._testo(L / 2, 722, data, 'DMReg', 9, TENUE, 'c')
        self.c.save()

    # --- elementi di contenuto --------------------------------------
    def paragrafo(self, s, size=10.5, interlinea=16, dopo=24):
        self._blocco(s, MARGINE, COLONNA, 'DMLight', size, interlinea, TESTO)
        self.y += dopo

    def sezione(self, titolo, prima=26, dopo=24):
        self.y += prima - 16      # il paragrafo precedente ha già lasciato spazio
        self._testo(MARGINE, self.y, titolo, 'Corm', 13, VERDE)
        self.y += dopo

    def elenco(self, voci, icona='check_circle', dopo=26):
        for voce in voci:
            righe = self._spezza(voce, 'DMLight', 9.5, COLONNA - 20)
            self._icona(MARGINE + 2, self.y - 0.5, icona, 9.5)
            for i, riga in enumerate(righe):
                self._testo(MARGINE + 20, self.y, riga, 'DMLight', 9.5, TESTO)
                self.y += 14 if i < len(righe) - 1 else 16
        self.y += dopo - 16

    def nota(self, s, icona='info'):
        righe = self._spezza(s, 'DMLight', 9, COLONNA - 52)
        alto = self.y - 13.5
        altezza = 22 + 13 * len(righe)
        self.c.setFillColor(NOTA)
        self.c.setStrokeColor(RAME)
        self.c.setLineWidth(0.6)
        self.c.roundRect(MARGINE, A - alto - altezza, COLONNA, altezza, 6, fill=1, stroke=1)
        self._icona(MARGINE + 14, self.y - 0.5, icona, 13)
        for riga in righe:
            self._testo(MARGINE + 40, self.y, riga, 'DMLight', 9, TESTO)
            self.y += 13
        self.y = alto + altezza + 30

    def passi(self, elenco):
        for numero, (titolo, corpo) in enumerate(elenco, 1):
            self.c.setFillColor(RAME_SCURO)
            self.c.circle(MARGINE + 9, A - self.y + 4.2, 10.5, fill=1, stroke=0)
            self._testo(MARGINE + 9, self.y, str(numero), 'DMSemi', 9.5, Color(1, 1, 1), 'c')
            self._testo(MARGINE + 30, self.y, titolo, 'DMSemi', 10.5, TESTO_FORTE)
            self.y += 16
            self._blocco(corpo, MARGINE + 30, COLONNA - 30, 'DMLight', 9.5, 14, TESTO)
            self.y += 25
        self.y -= 4

    def definizioni(self, righe, dopo=28):
        for termine, spiegazione in righe:
            self.c.setFillColor(CARD)
            self.c.roundRect(MARGINE, A - self.y - 16.5, COLONNA, 26, 5, fill=1, stroke=0)
            corpo = 9.5                       # i termini lunghi si stringono, non si sovrappongono
            while pdfmetrics.stringWidth(termine, 'DMSemi', corpo) > 145 and corpo > 7.5:
                corpo -= 0.25
            self._testo(MARGINE + 12, self.y, termine, 'DMSemi', corpo, VERDE)
            self._testo(MARGINE + 165, self.y, spiegazione, 'DMLight', 8.5, TESTO)
            ultima = self.y
            self.y += 32
        # lo spazio successivo si misura dal bordo basso dell'ultima riga,
        # non dalla sua linea di base: altrimenti il riquadro che segue la tocca
        self.y = ultima + 16.5 + dopo

    def banda(self, celle, dopo=30):
        larghezza = (COLONNA - 40) / 3
        alto = self.y
        for i, (titolo, sotto) in enumerate(celle):
            x = MARGINE + i * (larghezza + 20)
            self.c.setFillColor(CARD)
            self.c.setStrokeColor(RAME)
            self.c.setLineWidth(0.6)
            self.c.roundRect(x, A - alto - 58, larghezza, 58, 6, fill=1, stroke=1)
            self._testo(x + larghezza / 2, alto + 24.6, titolo, 'DMSemi', 10, VERDE, 'c')
            self._testo(x + larghezza / 2, alto + 40.5, sotto, 'DMLight', 8.5, TESTO, 'c')
        self.y = alto + 58 + dopo

    def catalogo(self, icone, dopo=30):
        """Due colonne: icona, etichetta leggibile, nome tecnico allineato a destra."""
        larghezza = (COLONNA - 14) / 2
        righe = (len(icone) + 1) // 2
        alto = self.y
        for i, voce in enumerate(icone):
            col, riga = i % 2, i // 2
            x = MARGINE + col * (larghezza + 14)
            y = alto + riga * 25
            self.c.setFillColor(CARD)
            self.c.roundRect(x, A - y - 17, larghezza, 23, 5, fill=1, stroke=0)
            self._icona(x + 9, y, voce['nome'], 13)
            etichetta = voce['etichetta']
            spazio = larghezza - 32 - pdfmetrics.stringWidth(voce['nome'], 'DMLight', 6.8) - 10
            while pdfmetrics.stringWidth(etichetta, 'DMLight', 8.3) > spazio and len(etichetta) > 4:
                etichetta = etichetta[:-2] + '…'
            self._testo(x + 32, y, etichetta, 'DMLight', 8.3, TESTO)
            self._testo(x + larghezza - 8, y, voce['nome'], 'DMLight', 6.8, TENUE, 'r')
        self.y = alto + righe * 25 + dopo


# ------------------------------------------------------------- contenuto
def costruisci(g, icone):
    g.copertina(
        'Guida al tuo sito',
        'come modificare testi, foto e destinazioni',
        'Questa guida ti accompagna passo per passo nell’uso del backoffice: la zona '
        'riservata dove puoi cambiare i contenuti del sito senza toccare una riga di '
        'codice, in autonomia e in qualsiasi momento.',
        f'Preparata da Alberto Piras · {MESE}')

    # ---- pagina 1
    g.apri('Prima di cominciare', 'Come funziona, in breve')
    g.paragrafo('Il tuo sito non è un programma da installare: è un insieme di pagine già '
                'pronte, pubblicate su internet. Il backoffice è una scrivania separata dove '
                'modifichi i contenuti; quando salvi, il sito si ricostruisce da solo e dopo '
                'un paio di minuti le modifiche sono online per tutti.', dopo=41)
    g.banda([('1. Modifichi', 'dal backoffice, nei campi'),
             ('2. Salvi', 'con un clic'),
             ('3. È online', 'dopo 1-2 minuti')], dopo=25)
    g.nota('Non puoi rompere il sito. Ogni salvataggio resta registrato e si può tornare '
           'indietro a una versione precedente in qualunque momento: se qualcosa non ti '
           'piace, si recupera.')
    g.sezione('Cosa puoi cambiare da sola', prima=16)
    g.elenco([
        'tutti i testi delle quattro pagine, in italiano e in inglese',
        'le fotografie (caricandole direttamente dal computer)',
        'le destinazioni: aggiungerne di nuove, rimuoverle, cambiarne l’ordine',
        'le domande frequenti: aggiungerle, riscriverle, eliminarle',
        'i tuoi contatti: email, telefono, numero WhatsApp, Instagram',
        'le fasce di budget e le opzioni del modulo di contatto',
    ])
    g.sezione('Cosa invece è meglio non toccare')
    g.paragrafo('Nelle impostazioni trovi due campi tecnici: «Chiave Web3Forms» (fa arrivare '
                'i messaggi del modulo nella tua casella) e «ID sito Umami» (le statistiche '
                'di visita). Se li svuoti, quelle due funzioni si spengono. Non c’è altro di '
                'delicato.', size=9.5, interlinea=14)

    # ---- pagina 2
    g.apri('Primo accesso', 'Entrare nel backoffice')
    g.passi([
        ('Vai all’indirizzo del backoffice',
         'Apri il browser e digita:\nwww.rottedincenso.it/admin'),
        ('Accedi con GitHub',
         'Trovi un solo pulsante: «Sign in with GitHub». GitHub è il servizio dove sono '
         'conservati in sicurezza i contenuti del sito: ti serve solo per farti riconoscere. '
         'Le credenziali te le ha preparate Alberto.'),
        ('Autorizza, la prima volta',
         'Al primo accesso GitHub ti chiede se autorizzi «Rotte d’incenso CMS» a lavorare '
         'per te: conferma. Non te lo chiederà più.'),
        ('Aggiungi il sito ai preferiti',
         'Così la volta successiva ci arrivi con un clic.'),
    ])
    g.nota('Se vedi la scritta «This site is private» o ti chiede un account Netlify, non '
           'stai sbagliando nulla: scrivi ad Alberto, è un’impostazione da cambiare una '
           'volta sola.')
    g.sezione('Cosa trovi appena entri', prima=16)
    g.paragrafo('A sinistra c’è l’elenco delle sezioni del sito. Ognuna raccoglie i contenuti '
                'di una parte:', size=9.5, interlinea=14, dopo=24)
    g.definizioni([
        ('Impostazioni del sito', 'i tuoi contatti, WhatsApp, Instagram e i testi dell’invito finale'),
        ('Home', 'tutto il contenuto della pagina iniziale: storia, valori, metodo, FAQ'),
        ('Testo pagina Destinazioni', 'il titolo e la frase in cima alla pagina Destinazioni'),
        ('Destinazioni', 'un elemento per ogni paese'),
        ('Servizi', 'le tre proposte con i loro prezzi'),
        ('Contatti', 'i testi della pagina e le voci del modulo'),
    ], dopo=24)
    g.nota('Le sezioni che finiscono con «(English)» contengono la versione inglese del '
           'sito. Se modifichi solo l’italiano, la pagina inglese resta come prima: '
           'ricordati di aggiornare entrambe.')

    # ---- pagina 3
    g.apri('Operazione quotidiana', 'Modificare un testo')
    g.passi([
        ('Scegli la sezione', 'Per esempio «Home» per la pagina iniziale.'),
        ('Trova il campo',
         'I campi hanno nomi in italiano che dicono cosa contengono: «Frase di apertura», '
         '«Titolo», «Paragrafi di apertura». Clicca dentro e scrivi.'),
        ('Salva',
         'In alto trovi il pulsante di salvataggio. Dopo un paio di minuti la modifica è '
         'online: ricarica il sito per vederla.'),
    ])
    g.sezione('I paragrafi lunghi', prima=20)
    g.paragrafo('Il racconto della tua storia non è un blocco unico: è una lista di paragrafi '
                'separati. Ogni elemento della lista è un paragrafo che sul sito appare '
                'staccato dagli altri. Puoi aggiungerne di nuovi con il pulsante «+», '
                'riordinarli trascinandoli, o eliminarli.', size=9.5, interlinea=14)
    g.sezione('Le domande frequenti')
    g.paragrafo('Funzionano allo stesso modo: ogni voce ha una domanda e la sua risposta. '
                'Puoi averne tre o dieci, il sito si adatta da solo. Un consiglio: le domande '
                'che ti arrivano più spesso per email sono le migliori da aggiungere qui, '
                'perché ti risparmiano lavoro.', size=9.5, interlinea=14)
    g.sezione('Gli apostrofi')
    g.paragrafo('Nel sito usiamo l’apostrofo tipografico curvo (’) e non quello dritto ('
                "'"
                '): è un dettaglio che si nota nella resa tipografica. Se scrivi da telefono '
                'viene inserito automaticamente; da computer, se ti capita quello dritto, non '
                'è un problema grave.', size=9.5, interlinea=14, dopo=30)
    g.nota('Un testo salvato per errore non è perduto: chiedi ad Alberto di recuperare la '
           'versione precedente.')

    # ---- pagina 4
    g.apri('Caricare e sostituire', 'Fotografie')
    g.passi([
        ('Clicca sul campo dell’immagine',
         'Trovi l’anteprima di quella attuale e un pulsante per scegliere un file nuovo.'),
        ('Carica dal computer',
         'Trascina il file o selezionalo. Resta salvato nel sito: non serve nient’altro.'),
        ('Scrivi la descrizione',
         'Sotto ogni immagine c’è un campo «Descrizione foto». Serve a chi naviga con '
         'lettori vocali e ai motori di ricerca: descrivi in poche parole cosa si vede, per '
         'esempio «Donna che cammina in un mercato di spezie».'),
    ])
    g.sezione('Come preparare le foto', prima=20)
    g.elenco([
        'Dimensione: vanno bene foto grandi, ma non enormi. Fino a circa 2000 pixel di lato '
        'è perfetto; oltre, il sito rischia di diventare lento.',
        'Formato: JPG per le fotografie, PNG se serve la trasparenza.',
        'Peso: meglio sotto 500 KB per immagine. Se le tue foto pesano diversi megabyte, si '
        'possono alleggerire senza perdere qualità visibile.',
        'Taglio: il ritratto grande in apertura è verticale, le schede delle destinazioni '
        'sono orizzontali. Scegli foto già orientate così.',
    ], icona='check', dopo=30)
    g.nota('Le destinazioni senza foto mostrano un rettangolo colorato con la scritta «foto '
           'da inserire»: è voluto, così si vede subito cosa manca. Appena carichi una '
           'fotografia, il segnaposto sparisce da sé.')

    # ---- pagina 5
    g.apri('Aggiungere, riordinare, togliere', 'Destinazioni')
    g.paragrafo('Ogni paese è un elemento a sé. Nella sezione «Destinazioni» li vedi '
                'elencati: clicca su uno per modificarlo, o usa «New Destinazioni» per '
                'aggiungerne uno.', size=9.5, interlinea=14, dopo=26)
    g.sezione('I campi di una destinazione', prima=16, dopo=26)
    g.definizioni([
        ('Nome', 'come apparirà sulla scheda, per esempio «Vietnam»'),
        ('Descrizione breve', 'una o due righe che raccontano il carattere del luogo'),
        ('Nome / Descrizione (inglese)', 'la stessa cosa in inglese, per la versione EN'),
        ('Foto', 'la fotografia; se la lasci vuota appare il segnaposto colorato'),
        ('Colore segnaposto', 'il colore del rettangolo quando non c’è la foto'),
        ('Icona', 'il disegno in filigrana sul segnaposto: si sceglie da un elenco'),
        ('Ordine in griglia', 'un numero: 1 compare per prima, 7 per ultima'),
    ], dopo=24)
    g.nota('Per cambiare l’ordine delle schede non serve spostare nulla: basta cambiare il '
           'numero nel campo «Ordine in griglia». Se vuoi che il Marocco venga per primo, '
           'mettigli 1.')
    g.sezione('Il testo in cima alla pagina', prima=16)
    g.paragrafo('Il titolo «Destinazioni» e la frase che lo accompagna non appartengono a '
                'nessun paese: sono l’introduzione della pagina. Li trovi nella sezione '
                '«Testo pagina Destinazioni», con i campi in italiano e in inglese.',
                size=9.5, interlinea=14)
    g.sezione('Togliere una destinazione')
    g.paragrafo('Aprila e usa l’opzione di eliminazione. Se invece pensi di riproporla più '
                'avanti, un’alternativa è darle un numero d’ordine alto e lasciarla in fondo '
                '— ma la strada pulita è eliminarla: si può sempre ricreare.',
                size=9.5, interlinea=14)

    # ---- pagina 6: catalogo icone
    g.apri('Catalogo', 'Le icone disponibili')
    g.paragrafo('Quando un campo chiede un’icona, la scegli da un elenco a tendina: non serve '
                'ricordare i nomi. Queste sono tutte quelle a disposizione, con il nome che '
                'vedrai nel menu.', size=10, interlinea=15, dopo=24)
    g.catalogo(icone, dopo=16)
    g.nota('Se ti serve un’icona che qui non c’è, scrivi ad Alberto: aggiungerla richiede un '
           'intervento tecnico di pochi minuti.')

    # ---- pagina 7
    g.apri('Italiano e inglese', 'Le due lingue')
    g.paragrafo('Il sito esiste in due versioni: quella italiana (rottedincenso.it) e quella '
                'inglese (rottedincenso.it/en). Sono pagine separate con contenuti separati: '
                'il sito non traduce da sé.', dopo=20)
    g.paragrafo('Nel backoffice le sezioni con «(English)» accanto al nome contengono i testi '
                'inglesi. La regola pratica: quando cambi qualcosa di importante in italiano, '
                'apri anche la versione inglese e aggiorna la stessa parte. Se non lo fai, il '
                'sito continua a funzionare — mostrerà semplicemente il testo inglese vecchio.',
                dopo=30)
    g.nota('Le traduzioni attuali sono una prima stesura fatta in fase di costruzione. '
           'Rileggile con calma: sei tu a sapere come vuoi suonare in inglese.')
    g.sezione('Se qualcosa va storto', prima=16, dopo=26)
    for domanda, risposta in [
        ('Ho salvato e non vedo la modifica sul sito',
         'Aspetta due o tre minuti e ricarica la pagina con un ricaricamento forzato '
         '(Cmd+Shift+R su Mac). Il sito si ricostruisce ogni volta: non è immediato.'),
        ('Ho cancellato un testo per sbaglio',
         'Nulla è perduto: ogni versione resta registrata. Scrivi ad Alberto indicando cosa '
         'e quando, si recupera.'),
        ('Il backoffice non mi fa entrare',
         'Controlla di essere connessa con l’account GitHub giusto. Se insiste, scrivi ad '
         'Alberto.'),
        ('Non arrivano più i messaggi dal modulo',
         'Controlla la cartella spam di info@rottedincenso.it. Se il problema resta, '
         'potrebbe essere il campo «Chiave Web3Forms» nelle impostazioni: non modificarlo, '
         'segnalalo.'),
        ('Ho caricato una foto e il sito è diventato lento',
         'Probabilmente la foto è troppo pesante. Ricaricala più leggera, sotto 500 KB.'),
    ]:
        g._testo(MARGINE, g.y, domanda, 'DMSemi', 9.5, TESTO_FORTE)
        g.y += 15
        g._blocco(risposta, MARGINE, COLONNA, 'DMLight', 9, 13, TESTO)
        g.y += 22

    g.chiudi('Buon lavoro',
             'Il sito è tuo: sperimenta senza timore. Ogni modifica è reversibile, e non '
             'esiste un pulsante capace di combinare guai irreparabili. Se un dubbio ti '
             'blocca, chiedere costa meno che restare ferma.',
             'Per qualsiasi cosa: Alberto Piras',
             f'Guida aggiornata a {MESE}')


def main():
    icone = json.load(open('src/_data/icone.json', encoding='utf-8'))
    with tempfile.TemporaryDirectory() as tmp:
        registra_font(tmp)
        g = Guida(USCITA, mappa_icone())
        costruisci(g, icone)
    print(f"OK: {USCITA} — {g.pagina + 2} pagine, "
          f"{os.path.getsize(USCITA) / 1024:.0f} KB, {len(icone)} icone a catalogo")


if __name__ == '__main__':
    main()
