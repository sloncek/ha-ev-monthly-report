// English message keys are the fallback; additional languages can be added here.
const PANEL_TRANSLATIONS = {
  "sl": {
    "Selected month": "Izbrani mesec",
    "Charging and expenses": "Polnjenja in stroški",
    "Mileage forecast": "Napoved kilometrov",
    "Mileage deviations": "Odstopanja kilometrov",
    "Actual versus expected mileage": "Dejanski kilometri proti pričakovanim",
    "Loading comparison …": "Nalagam primerjavo …",
    "Completed months from this installation · a positive deviation means more driving": "Zaključeni meseci iz te namestitve · pozitiven odmik pomeni več vožnje",
    "Month": "Mesec",
    "Actual km": "Dejansko km",
    "Expected km": "Pričakovano km",
    "Deviation km": "Odmik km",
    "Deviation %": "Odmik %",
    "Average km": "Povprečje km",
    "Deviation from average km": "Odmik od povp. km",
    "Deviation from average %": "Odmik od povp. %",
    "This retrospective comparison uses only earlier completed monthly distances from this installation. At least three earlier months with valid readings are required.": "Primerjava je retrospektivna in uporablja samo predhodne zaključene mesečne razdalje v tej namestitvi. Za izračun so potrebni vsaj trije predhodni meseci z veljavnimi odčitki.",
    "One row per month. Grey values are calculated automatically. Blue buttons open the relevant input. On a phone, scroll the table horizontally.": "Ena vrstica = en mesec. Sivi podatki se izračunajo sami. Modri gumbi odprejo samo potrebni vnos. Na telefonu tabelo pomakni levo/desno.",
    "Charging and reimbursement ledger · amounts in €": "Evidenca polnjenj in povračil · zneski v €",
    "Odometer km": "Števec km",
    "Distance km": "Prevoženo km",
    "Home kWh": "Doma kWh",
    "Rate €/kWh": "Tarifa €/kWh",
    "Home €": "Doma €",
    "Public € ✎": "Javno € ✎",
    "Other € ✎": "Drugo € ✎",
    "Opening balance €": "Prenos prej €",
    "Eligible €": "Upravičeno €",
    "To report €": "Za sporočiti €",
    "Reported € ✎": "Sporočeno € ✎",
    "Closing balance €": "Prenos naprej €",
    "Status": "Stanje",
    "Mileage forecast from historical readings": "Napoved kilometrov iz celotne zgodovine",
    "Loading forecast …": "Nalagam napoved …",
    "Display range": "Obdobje prikaza",
    "Next 12 months": "Naslednjih 12 mesecev",
    "Until contract end": "Do konca pogodbe",
    "Future mileage · forecasts, not actual readings": "Prihodnji kilometri · napoved, ne dejanski odčitki",
    "Forecast km": "Napoved km",
    "Forecast odometer": "Napoved števca",
    "Contract allowance": "Pogodbeni načrt",
    "Seasonal comparison km": "Sezonska primerjava km",
    "Seasonal odometer": "Sezonski števec",
    "Forecasts do not affect reimbursement claims. New valid completed readings update future forecasts automatically; a mid-month reading is not a month-end reading. The seasonal comparison was not more accurate than the baseline in historical tests.": "Napoved ne vpliva na zahtevke za povračilo. Novi veljavni zaključeni odčitki posodobijo nadaljnjo napoved samodejno; odčitek sredi meseca ni zaključena mesečna kilometrina. Sezonska primerjava na preteklih preizkusih ni bila natančnejša od osnovne metode.",
    "✎ Reported amount and email text": "✎ Sporočeni znesek in besedilo za email",
    "Email text": "Besedilo za email",
    "Copy text": "Kopiraj besedilo",
    "Amount you actually reported (€)": "Znesek, ki si ga dejansko sporočil (€)",
    "Mark as reported": "Označi kot sporočeno",
    "Send the email yourself. Confirm only the amount you actually reported. Reported months are protected; later differences are not automatic corrections.": "Email pošlješ sam. Potrdi šele dejansko sporočeni znesek. Že sporočeni meseci so zaščiteni; naknadne razlike niso samodejni popravek.",
    "Reimbursement rate · change only when needed": "Nastavitev tarife · samo ob spremembi",
    "Final rate €/kWh from the selected month onwards": "Končna tarifa €/kWh od izbranega meseca naprej",
    "Save rate": "Shrani tarifo",
    "The employer reimbursement rate is separate from your home electricity price; VAT is not added to it.": "Tarifa delodajalca ni cena domačega računa; DDV se ji ne prišteva.",
    "✎ Add public charging or another expense": "✎ Dodaj javno polnjenje ali drug strošek",
    "Type": "Vrsta",
    "Public charging": "Javno polnjenje",
    "Other expense": "Drug strošek",
    "Date": "Datum",
    "Provider / category": "Ponudnik / kategorija",
    "Paid including VAT (€)": "Plačano z DDV (€)",
    "kWh (optional)": "kWh (neobvezno)",
    "Include in employer claim": "Vključi v zahtevek delodajalcu",
    "Note (optional)": "Opomba (neobvezno)",
    "Add entry": "Dodaj vrstico",
    "Other expenses are not automatically eligible for reimbursement. Unknown public charging kWh remain blank, not zero.": "Drug strošek ni samodejno upravičen do povračila. Neznani javni kWh ostanejo prazni, ne nič.",
    "Entries for the selected month": "Vpisane postavke izbranega meseca",
    "Odometer · automatic from the selected entity; manual input only when needed": "Števec kilometrov · samodejno iz izbrane entitete; ročni vnos samo izjemoma",
    "Manual odometer reading (km)": "Ročni odčitek števca (km)",
    "Reading date and time": "Datum in čas odčitka",
    "Save reading": "Shrani odčitek",
    "The reading and timestamp are actual observations, not forecasts. Mileage does not affect energy reimbursement.": "Odčitek in čas nista napoved. Kilometri ne vplivajo na povračilo energije.",
    "Import home electricity invoice PDF": "Uvozi domači račun PDF",
    "The invoice, Moj Elektro data and comparison are processed automatically. A home electricity invoice is separate from an employer claim.": "Račun, Moj Elektro in primerjava se obdelajo samodejno. Domači račun ni zahtevek delodajalcu.",
    "Import PDF": "Uvozi PDF",
    "PDF received": "PDF sprejet",
    "Invoice parsed and validated": "Račun prebran in preverjen",
    "Moj Elektro and comparison": "Moj Elektro in primerjava",
    "Processing complete": "Obdelava zaključena",
    "Check status": "Preveri stanje",
    "Report month": "Mesec poročila",
    "Ledger view": "Pogled evidence",
    "Mileage deviations, read only": "Odstopanja kilometrov, samo za branje",
    "Monthly ledger, horizontally scrollable": "Mesečna preglednica, vodoravno pomična",
    "Mileage forecast, read only": "Napoved kilometrov, samo za branje",
    "Completed processing stages": "Zaključene faze obdelave",
    "{0} · monthly ledger": "{0} · mesečna preglednica",
    "The file is larger than 15 MiB": "Datoteka je večja od 15 MiB",
    "Choose a PDF": "Izberi PDF",
    "Preparing and uploading PDF …": "Pripravljam in nalagam PDF …",
    "Import failed.": "Uvoz ni uspel.",
    "The PDF is too large (maximum 15 MiB).": "PDF je prevelik (največ 15 MiB).",
    "The selected file is not a valid PDF.": "Izbrana datoteka ni veljaven PDF.",
    "Sign in with an administrator account to import invoices.": "Za uvoz se prijavi z administratorskim računom.",
    "Could not connect to the service{0}.": "Povezava s servisom ni uspela{0}.",
    " (HTTP {0})": " (HTTP {0})",
    "Details: {0}": "Podrobnosti: {0}",
    "Automatic retry: {0}. You do not need to import the invoice again.": "Samodejni ponovni poskus: {0}. Računa ni treba ponovno uvoziti.",
    "The original PDF has been saved.": "Izvirni PDF je shranjen.",
    "Monthly data refreshes automatically. The cost estimate is not an accounting confirmation.": "Mesečni podatki se osvežijo samodejno. Ocena stroška ni računovodska potrditev.",
    "Month: {0} · Import: {1} · Updated: {2}": "Mesec: {0} · Uvoz: {1} · Osveženo: {2}",
    "not yet determined": "še ni določen",
    "Could not retrieve the latest import status.": "Stanja zadnjega uvoza ne morem pridobiti.",
    "The service does not support the new progress display yet. Refresh the page after updating.": "Servis še nima novega prikaza napredka. Osveži stran po posodobitvi.",
    "The progress connection was interrupted; processing may still be running.": "Povezava za prikaz napredka je prekinjena; obdelava lahko še teče.",
    "Loading forecast for {0} …": "Nalagam napoved za {0} …",
    "Loading deviations for {0} …": "Nalagam odstopanja za {0} …",
    "Loading ledger for {0} …": "Nalagam evidenco za {0} …",
    "The forecast is currently unavailable. ": "Napoved trenutno ni dosegljiva. ",
    "The comparison is currently unavailable. ": "Primerjava trenutno ni dosegljiva. ",
    "The ledger could not be refreshed. ": "Evidence trenutno ni mogoče osvežiti. ",
    "already reported, read only": "že sporočeno, samo za branje",
    "enter missing data": "vnos manjkajočih podatkov",
    "missing": "manjka",
    "{0}: home {1} kWh × {2} €/kWh = {3} €. Eligible expenses: {4} €. Opening balance: {5} €. To report: {6} €. Already reported: {7} €.": "{0}: doma {1} kWh × {2} €/kWh = {3} €. Upravičeni stroški: {4} €. Prenos: {5} €. Za sporočiti: {6} €. Že sporočeno: {7} €.",
    "Rechecked home energy: {0} kWh ({1}); the reported month retains its original reading.": "Naknadno preverjena energija doma: {0} kWh ({1}); že sporočeni mesec ohranja prvotni odčitek.",
    "unknown quality": "neznana kakovost",
    "Total energy is not confirmed: check the selected meter history and missing public charging kWh.": "Celotna energija ni potrjena: preveri zgodovino izbranega števca in manjkajoče javne kWh.",
    "Later home reimbursement difference: {0} €{1}; not included automatically.": "Naknadna razlika domačega povračila: {0} €{1}; ni vključena samodejno.",
    " (unverified estimate)": " (nepotrjena ocena)",
    "This month has already been reported; the original amount remains saved.": "Ta mesec je že sporočen; izvirni znesek ostaja shranjen.",
    "A month can be marked as reported after it ends and the meter history is complete.": "Označitev kot sporočeno je možna po koncu meseca in popolni zgodovini števca.",
    "The claim data is not complete yet.": "Podatki za zahtevek še niso popolni.",
    "Company vehicle {0} charging for {1}: {2} €.": "Polnjenje službenega vozila {0} za {1}: {2} €.",
    "Current odometer ({0}): {1} km. HA update: {2}; this is not an automatic month-end reading for the selected month.": "Trenutni števec ({0}): {1} km. HA-posodobitev: {2}; to ni samodejen odčitek ob koncu izbranega meseca.",
    "The mapped odometer is currently unavailable; a manual monthly reading can be entered.": "Zemljevidani števec trenutno ni na voljo; ročni mesečni odčitek je mogoč.",
    "Recorded odometer: {0} km; monthly distance: {1} km.": "Evidentirani števec: {0} km; razdalja meseca: {1} km.",
    "included in claim": "v zahtevku",
    "excluded from claim": "ni v zahtevku",
    " · kWh unknown": " · kWh neznani",
    "Reported 🔒": "Sporočeno 🔒",
    "Draft": "Osnutek",
    "select month": "izberi mesec",
    "add public charging": "dodaj javno polnjenje",
    "add another expense": "dodaj drug strošek",
    "enter the amount actually reported": "vpiši dejansko sporočeni znesek",
    "Home kWh, calculations and balances are read only. Legacy public charging records are monthly totals: do not enter the same payments again. Reported amounts remain unchanged.": "Domači kWh, izračuni in prenos so samo za branje. Stara javna polnjenja so mesečni seštevki: istih plačil ne vpisuj ponovno. Že sporočeni zneski se ne spreminjajo.",
    "No monthly records yet.": "Še ni mesečnih zapisov.",
    "There are not enough valid completed readings or contract allowance details for a forecast yet.": "Za napoved še ni dovolj veljavnih zaključenih odčitkov ali pogodbenega načrta.",
    "Forecast at contract end ({0}): {1} km. Allowance: {2} km. Expected excess: {3} km.": "Napoved ob koncu pogodbe ({0}): {1} km. Limit: {2} km. Predvideni presežek: {3} km.",
    "Data through completed month {0}: odometer {1} km; {2} monthly distances from this installation. The forecast uses only this installation's history and a 12-month rolling average. Invalid or missing readings are not filled in.": "Podatki do zaključenega meseca {0}: števec {1} km; {2} lastnih mesečnih razdalj. Napoved uporablja samo zgodovino te namestitve in 12-mesečno drseče povprečje. Neveljavni ali manjkajoči odčitki niso dopolnjeni.",
    " Warning: some completed monthly readings are missing or invalid; missing mileage is not replaced with zero.": " Opozorilo: nekateri zaključeni mesečni odčitki manjkajo ali so neveljavni; izpuščeni kilometri niso nadomeščeni z ničlo.",
    "Scenario with a 20% lower / higher future pace: final odometer {0}–{1} km. This is a sensitivity scenario, not an 80% or 95% probability interval.": "Scenarij 20 % nižjega / višjega prihodnjega tempa: končni števec {0}–{1} km. To je občutljivost, ne 80- ali 95-odstotni verjetnostni interval.",
    "{0} completed months from this installation. Historical average through the selected month: {1} km/month. This comparison is informational and does not change the financial ledger.": "{0} zaključenih mesecev te namestitve. Zgodovinsko povprečje do izbranega meseca: {1} km/mesec. Primerjava je informativna in ne spreminja finančne evidence.",
    "There are not enough completed monthly records for a comparison yet.": "Za primerjavo še ni dovolj zaključenih mesečnih podatkov.",
    "Wait for the selected month's data.": "Počakaj na podatke izbranega meseca.",
    "Saved for {0}.": "Shranjeno za {0}.",
    "Enter a date, provider/category and valid amount; kWh are optional.": "Vpiši datum, ponudnika/kategorijo in veljaven znesek; kWh so neobvezni.",
    "Enter the amount you actually reported.": "Vpiši dejansko sporočeni znesek.",
    "Save €{0} as the amount actually reported for {1}? No email will be sent.": "Shranim {0} € kot dejansko sporočeni znesek za {1}? Email se ne bo poslal.",
    "Enter the odometer reading and its actual timestamp.": "Vpiši števec in dejanski čas odčitka.",
    "Text copied; send it in your own email.": "Besedilo kopirano; pošlji ga v svojem emailu.",
    "Copy the selected text manually.": "Označeno besedilo kopiraj ročno.",
    "PDF received; waiting to parse and validate the invoice.": "PDF je sprejet; čakam na branje in preverjanje računa.",
    "The invoice cannot be processed. Check the PDF and invoice data.": "Računa ni mogoče obdelati. Preveri PDF in podatke na računu.",
    "The invoice needs review; its data has not been automatically confirmed.": "Račun potrebuje pregled; podatki niso samodejno potrjeni.",
    "The invoice conflicts with an invoice already saved.": "Račun je v konfliktu z že shranjenim računom.",
    "Invoice parsed. Waiting for Moj Elektro data and comparison.": "Račun je prebran. Čakam na podatke Moj Elektro in primerjavo.",
    "Retrieving Moj Elektro data and checking the invoice.": "Pridobivam podatke Moj Elektro in preverjam skladnost računa.",
    "Processing is complete, but the invoice differs from meter readings. Review the comparison.": "Obdelava je zaključena, vendar račun odstopa od meritev. Preveri primerjavo.",
    "Invoice processed and Moj Elektro comparison complete.": "Račun je obdelan in primerjava z Moj Elektro je zaključena.",
    "Moj Elektro does not have all data for this month yet.": "Moj Elektro še nima vseh podatkov za mesec.",
    "Automatic invoice processing failed.": "Napaka pri samodejni obdelavi računa.",
    "Moj Elektro authentication failed. Check the integration settings.": "Prijava v Moj Elektro ni uspela. Preveri nastavitve integracije.",
    "complete": "popolna",
    "partial": "delna",
    "unknown": "neznana",
    "unavailable": "ni na voljo"
  }
};
const LEGACY_MESSAGE_KEYS = Object.fromEntries(Object.entries(PANEL_TRANSLATIONS.sl).map(([key,value])=>[value,key]));

class EnergyLedgerPanel extends HTMLElement {
  setConfig(config) { this._config=config; }
  vehicleName() { return this._config?.vehicle_name || this._panel?.config?.vehicle_name || 'EV'; }
  getCardSize() { return 12; }
  set hass(value) {
    const preferences=JSON.stringify([value?.locale,value?.language,value?.config?.time_zone]);
    const changed=preferences!==this._localePreferences;
    this._localePreferences=preferences;this._hass=value;
    if(!this._rendered)this.render();
    else if(changed)this.localize();
    if(this.isConnected&&!this._resumeRequested)this.resumeLatest();
    if(this.isConnected)this.syncRegister();
  }
  set panel(value) { this._panel=value;if(this._rendered)this.localize(); }
  language() { return this._hass?.locale?.language || this._hass?.language || 'en'; }
  t(message, ...values) {
    message=String(message ?? '');
    const key=Object.hasOwn(LEGACY_MESSAGE_KEYS,message)?LEGACY_MESSAGE_KEYS[message]:message;
    const language=this.language().toLowerCase().replace('_','-').split('-')[0];
    const catalog=Object.hasOwn(PANEL_TRANSLATIONS,language)?PANEL_TRANSLATIONS[language]:{};
    const text=Object.hasOwn(catalog,key)?catalog[key]:key;
    return text.replace(/\{(\d+)\}/g, (match,index)=>index<values.length?String(values[index]):match);
  }
  numberLocale() {
    const format=this._hass?.locale?.number_format;
    return ({comma_decimal:'en-US',decimal_comma:'de-DE',space_comma:'fr-FR',quote_decimal:'de-CH',none:'en-US'})[format]
      || (format==='system'?undefined:this.language());
  }
  formatNumber(value, options={}) {
    try { return new Intl.NumberFormat(this.numberLocale(),{...options,...(this._hass?.locale?.number_format==='none'?{useGrouping:false}:{})}).format(Number(value)); }
    catch { return new Intl.NumberFormat('en',options).format(Number(value)); }
  }
  formatDateTime(value, timeOnly=false) {
    const date=new Date(value); if(Number.isNaN(date.getTime()))return String(value);
    const locale=this._hass?.locale || {};
    const dateLanguage=({DMY:'en-GB',MDY:'en-US',YMD:'sv-SE'})[locale.date_format]
      || (locale.date_format==='system'?undefined:this.language());
    const options={hour:'2-digit',minute:'2-digit',...(!timeOnly?{year:'numeric',month:'2-digit',day:'2-digit'}:{})};
    if(locale.time_format==='12')options.hourCycle='h12';
    else if(locale.time_format==='24')options.hourCycle='h23';
    else {
      try {options.hourCycle=new Intl.DateTimeFormat(locale.time_format==='system'?undefined:this.language(),{hour:'numeric'}).resolvedOptions().hourCycle;} catch {}
    }
    if(locale.time_zone==='server'&&this._hass?.config?.time_zone)options.timeZone=this._hass.config.time_zone;
    try { return new Intl.DateTimeFormat(dateLanguage,options).format(date); }
    catch { return new Intl.DateTimeFormat('en',options).format(date); }
  }
  localize() {
    this.setAttribute('lang',this.language());
    for(const node of this.querySelectorAll('[data-i18n]'))node.textContent=this.t(node.getAttribute('data-i18n'));
    for(const node of this.querySelectorAll('[data-i18n-aria-label]'))node.setAttribute('aria-label',this.t(node.getAttribute('data-i18n-aria-label')));
    const heading=this.querySelector('#vehicle-heading');if(heading)heading.textContent=this.t('{0} · monthly ledger',this.vehicleName());
    // Update text in place so language changes preserve inputs, attachments and open editors.
    if(this._registerData)this.showRegister(this._registerData);
    if(this._historyMonths)this.showHistory(this._historyMonths);
    if(this._mileageData)this.showMileage(this._mileageData);
    if(this._lastProgress)this.showProgress(this._lastProgress.progress,this._lastProgress.job);
  }
  connectedCallback(){if(this._hass) {this.resumeLatest(); this.syncRegister();}}
  disconnectedCallback(){this._watchGeneration=(this._watchGeneration||0)+1; this._resumeRequested=false;}
  render() {
    this._rendered=true;
    this.innerHTML=`<style>energy-ledger-native-panel section{background:var(--card-background-color)}energy-ledger-native-panel label{display:block;margin-top:12px}energy-ledger-native-panel input{width:100%;box-sizing:border-box;padding:10px}energy-ledger-native-panel button{cursor:pointer}energy-ledger-native-panel progress{width:100%;height:14px;accent-color:var(--primary-color)}energy-ledger-native-panel #import-status{margin-top:20px;padding:16px;border:1px solid var(--divider-color);border-radius:8px}energy-ledger-native-panel #import-status[data-level=error]{border-color:var(--error-color)}energy-ledger-native-panel #import-status[data-level=warning]{border-color:var(--warning-color,#ef9b0f)}energy-ledger-native-panel #import-status[data-level=success]{border-color:var(--success-color)}energy-ledger-native-panel #import-status p{overflow-wrap:anywhere}energy-ledger-native-panel #stages{padding-left:24px;color:var(--secondary-text-color)}energy-ledger-native-panel #stages li{padding:4px}energy-ledger-native-panel #stages .done{color:var(--success-color)}energy-ledger-native-panel #stages .active{color:var(--primary-text-color);font-weight:600}energy-ledger-native-panel small{color:var(--secondary-text-color)}</style>
      <style>energy-ledger-native-panel{display:block}energy-ledger-native-panel main{max-width:1600px;margin:0 auto;padding:16px;font-family:var(--paper-font-body1_-_font-family,Arial)}energy-ledger-native-panel section{padding:16px;border:1px solid var(--divider-color);margin:12px 0;border-radius:8px}energy-ledger-native-panel h1{font-size:24px;margin:8px 0}energy-ledger-native-panel h2{font-size:18px;margin:0 0 12px}energy-ledger-native-panel button{font:inherit;border:1px solid var(--divider-color);border-radius:5px;background:var(--card-background-color);color:var(--primary-color);margin:4px 0;padding:8px 12px}energy-ledger-native-panel button:disabled{color:var(--disabled-text-color,#888);cursor:default}energy-ledger-native-panel input,energy-ledger-native-panel select,energy-ledger-native-panel textarea{font:inherit;color:var(--primary-text-color);background:var(--secondary-background-color);border:1px solid var(--divider-color);border-radius:4px}energy-ledger-native-panel select{padding:9px}energy-ledger-native-panel .sheet-scroll{overflow:auto;max-height:62vh;border:1px solid var(--divider-color)}energy-ledger-native-panel table{border-collapse:separate;border-spacing:0;width:100%;font-size:14px;font-variant-numeric:tabular-nums}energy-ledger-native-panel th,energy-ledger-native-panel td{padding:9px 10px;border-right:1px solid var(--divider-color);border-bottom:1px solid var(--divider-color);white-space:nowrap;text-align:right}energy-ledger-native-panel th{position:sticky;top:0;background:var(--secondary-background-color);z-index:2;text-align:center;font-size:12px}energy-ledger-native-panel th:first-child,energy-ledger-native-panel td:first-child{position:sticky;left:0;text-align:left;background:var(--card-background-color);z-index:1}energy-ledger-native-panel th:first-child{z-index:3}energy-ledger-native-panel tbody tr:nth-child(even) td{background:var(--secondary-background-color)}energy-ledger-native-panel tr.selected td{background:var(--primary-color-light,#dbeffc);color:var(--primary-text-color)}energy-ledger-native-panel tr.selected{outline:2px solid var(--primary-color);outline-offset:-2px}energy-ledger-native-panel td button{padding:3px 6px;font-size:13px;white-space:nowrap}energy-ledger-native-panel .manual{color:var(--primary-color)}energy-ledger-native-panel .sheet-help{font-size:13px;color:var(--secondary-text-color)}energy-ledger-native-panel details{margin:12px 0}energy-ledger-native-panel summary{cursor:pointer;font-weight:600;padding:8px 0}energy-ledger-native-panel .entry-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;align-items:end}energy-ledger-native-panel .entry-grid label{margin:0}energy-ledger-native-panel .entry-grid select{width:100%;box-sizing:border-box}energy-ledger-native-panel .entry-grid .wide{grid-column:span 2}energy-ledger-native-panel #register-warning{font-size:13px;color:var(--secondary-text-color)}energy-ledger-native-panel #register-summary{font-size:14px}energy-ledger-native-panel .toolbar{display:flex;align-items:center;gap:16px;flex-wrap:wrap}energy-ledger-native-panel .toolbar label{margin:0}energy-ledger-native-panel .tools{margin-left:auto}energy-ledger-native-panel a{color:var(--primary-color)}@media(max-width:700px){energy-ledger-native-panel main{padding:8px}energy-ledger-native-panel section{padding:12px}energy-ledger-native-panel .entry-grid{grid-template-columns:repeat(2,minmax(0,1fr))}energy-ledger-native-panel .tools{margin-left:0}energy-ledger-native-panel th,energy-ledger-native-panel td{padding:8px}energy-ledger-native-panel .sheet-scroll{max-height:58vh}}</style>
      <style>energy-ledger-native-panel tr.selected td{background:var(--secondary-background-color)}</style><main><h1 id="vehicle-heading"></h1><p id="message" style="position:sticky;top:0;background:var(--card-background-color);z-index:4" role="status" aria-live="polite"></p>
      <div class="toolbar"><label><span data-i18n="Selected month">Selected month</span> <select id="register-month" aria-label="Report month" data-i18n-aria-label="Report month"></select></label></div><nav aria-label="Ledger view" data-i18n-aria-label="Ledger view"><button id="ledger-tab" aria-pressed="true"><span data-i18n="Charging and expenses">Charging and expenses</span></button> <button id="forecast-tab" aria-pressed="false"><span data-i18n="Mileage forecast">Mileage forecast</span></button> <button id="deviations-tab" aria-pressed="false"><span data-i18n="Mileage deviations">Mileage deviations</span></button></nav>
      <section id="mileage-comparison" hidden><h2><span data-i18n="Actual versus expected mileage">Actual versus expected mileage</span></h2><p id="comparison-summary" role="status" aria-live="polite"><span data-i18n="Loading comparison …">Loading comparison …</span></p><div class="sheet-scroll" tabindex="0" aria-label="Mileage deviations, read only" data-i18n-aria-label="Mileage deviations, read only"><table id="comparison-table"><caption style="text-align:left;padding:8px"><span data-i18n="Completed months from this installation · a positive deviation means more driving">Completed months from this installation · a positive deviation means more driving</span></caption><thead><tr><th scope="col"><span data-i18n="Month">Month</span></th><th scope="col"><span data-i18n="Actual km">Actual km</span></th><th scope="col"><span data-i18n="Expected km">Expected km</span></th><th scope="col"><span data-i18n="Deviation km">Deviation km</span></th><th scope="col"><span data-i18n="Deviation %">Deviation %</span></th><th scope="col"><span data-i18n="Average km">Average km</span></th><th scope="col"><span data-i18n="Deviation from average km">Deviation from average km</span></th><th scope="col"><span data-i18n="Deviation from average %">Deviation from average %</span></th></tr></thead><tbody></tbody></table></div><p class="sheet-help"><span data-i18n="This retrospective comparison uses only earlier completed monthly distances from this installation. At least three earlier months with valid readings are required.">This retrospective comparison uses only earlier completed monthly distances from this installation. At least three earlier months with valid readings are required.</span></p></section>
      <section id="sheet"><p class="sheet-help"><span data-i18n="One row per month. Grey values are calculated automatically. Blue buttons open the relevant input. On a phone, scroll the table horizontally.">One row per month. Grey values are calculated automatically. Blue buttons open the relevant input. On a phone, scroll the table horizontally.</span></p><div class="sheet-scroll" tabindex="0" aria-label="Monthly ledger, horizontally scrollable" data-i18n-aria-label="Monthly ledger, horizontally scrollable"><table id="register-history"><caption style="text-align:left;padding:8px"><span data-i18n="Charging and reimbursement ledger · amounts in €">Charging and reimbursement ledger · amounts in €</span></caption><thead><tr><th scope="col"><span data-i18n="Month">Month</span></th><th scope="col"><span data-i18n="Odometer km">Odometer km</span></th><th scope="col"><span data-i18n="Distance km">Distance km</span></th><th scope="col"><span data-i18n="Home kWh">Home kWh</span></th><th scope="col"><span data-i18n="Rate €/kWh">Rate €/kWh</span></th><th scope="col"><span data-i18n="Home €">Home €</span></th><th scope="col" class="manual"><span data-i18n="Public € ✎">Public € ✎</span></th><th scope="col" class="manual"><span data-i18n="Other € ✎">Other € ✎</span></th><th scope="col"><span data-i18n="Opening balance €">Opening balance €</span></th><th scope="col"><span data-i18n="Eligible €">Eligible €</span></th><th scope="col"><span data-i18n="To report €">To report €</span></th><th scope="col" class="manual"><span data-i18n="Reported € ✎">Reported € ✎</span></th><th scope="col"><span data-i18n="Closing balance €">Closing balance €</span></th><th scope="col"><span data-i18n="Status">Status</span></th></tr></thead><tbody></tbody></table></div><p id="history-status" class="sheet-help"></p></section>
      <section id="mileage" hidden><h2><span data-i18n="Mileage forecast from historical readings">Mileage forecast from historical readings</span></h2><p id="mileage-summary" role="status" aria-live="polite"><span data-i18n="Loading forecast …">Loading forecast …</span></p><p id="mileage-basis" class="sheet-help"></p><label><span data-i18n="Display range">Display range</span> <select id="forecast-range"><option value="12" data-i18n="Next 12 months">Next 12 months</option><option value="all" data-i18n="Until contract end">Until contract end</option></select></label><div class="sheet-scroll" tabindex="0" aria-label="Mileage forecast, read only" data-i18n-aria-label="Mileage forecast, read only"><table id="mileage-table"><caption style="text-align:left;padding:8px"><span data-i18n="Future mileage · forecasts, not actual readings">Future mileage · forecasts, not actual readings</span></caption><thead><tr><th scope="col"><span data-i18n="Month">Month</span></th><th scope="col"><span data-i18n="Forecast km">Forecast km</span></th><th scope="col"><span data-i18n="Forecast odometer">Forecast odometer</span></th><th scope="col"><span data-i18n="Contract allowance">Contract allowance</span></th><th scope="col"><span data-i18n="Deviation km">Deviation km</span></th><th scope="col"><span data-i18n="Seasonal comparison km">Seasonal comparison km</span></th><th scope="col"><span data-i18n="Seasonal odometer">Seasonal odometer</span></th></tr></thead><tbody></tbody></table></div><p id="mileage-scenarios" class="sheet-help"></p><p class="sheet-help"><span data-i18n="Forecasts do not affect reimbursement claims. New valid completed readings update future forecasts automatically; a mid-month reading is not a month-end reading. The seasonal comparison was not more accurate than the baseline in historical tests.">Forecasts do not affect reimbursement claims. New valid completed readings update future forecasts automatically; a mid-month reading is not a month-end reading. The seasonal comparison was not more accurate than the baseline in historical tests.</span></p></section>
      <section id="register"><h2 id="month-heading"><span data-i18n="Selected month">Selected month</span></h2><p id="register-summary" role="status" aria-live="polite"></p><p id="register-warning"></p><details id="report-editor"><summary><span data-i18n="✎ Reported amount and email text">✎ Reported amount and email text</span></summary><label><span data-i18n="Email text">Email text</span><textarea id="email-text" rows="2" readonly style="width:100%;box-sizing:border-box"></textarea></label><button id="copy-email"><span data-i18n="Copy text">Copy text</span></button><label><span data-i18n="Amount you actually reported (€)">Amount you actually reported (€)</span><input id="reported-amount" type="number" min="0" step="0.01"></label><button id="save-reported"><span data-i18n="Mark as reported">Mark as reported</span></button><p class="sheet-help"><span data-i18n="Send the email yourself. Confirm only the amount you actually reported. Reported months are protected; later differences are not automatic corrections.">Send the email yourself. Confirm only the amount you actually reported. Reported months are protected; later differences are not automatic corrections.</span></p></details><details id="rate-editor"><summary><span data-i18n="Reimbursement rate · change only when needed">Reimbursement rate · change only when needed</span></summary><label><span data-i18n="Final rate €/kWh from the selected month onwards">Final rate €/kWh from the selected month onwards</span><input id="claim-rate" type="number" min="0" max="10" step="0.0001"></label><button id="save-rate"><span data-i18n="Save rate">Save rate</span></button><p class="sheet-help"><span data-i18n="The employer reimbursement rate is separate from your home electricity price; VAT is not added to it.">The employer reimbursement rate is separate from your home electricity price; VAT is not added to it.</span></p></details></section>
      <section id="expenses"><details id="expense-editor"><summary><span data-i18n="✎ Add public charging or another expense">✎ Add public charging or another expense</span></summary><div class="entry-grid"><label><span data-i18n="Type">Type</span><select id="expense-kind"><option value="PUBLIC" data-i18n="Public charging">Public charging</option><option value="OTHER" data-i18n="Other expense">Other expense</option></select></label><label><span data-i18n="Date">Date</span><input id="expense-date" type="date"></label><label><span data-i18n="Provider / category">Provider / category</span><input id="expense-provider" maxlength="200"></label><label><span data-i18n="Paid including VAT (€)">Paid including VAT (€)</span><input id="expense-gross" type="number" min="0" step="0.01"></label><label><span data-i18n="kWh (optional)">kWh (optional)</span><input id="expense-kwh" type="number" min="0.001" step="0.001"></label><label class="wide"><input id="expense-eligible" type="checkbox" style="width:auto"> <span data-i18n="Include in employer claim">Include in employer claim</span></label><label class="wide"><span data-i18n="Note (optional)">Note (optional)</span><input id="expense-notes" maxlength="2000"></label><button id="save-expense"><span data-i18n="Add entry">Add entry</span></button></div><p class="sheet-help"><span data-i18n="Other expenses are not automatically eligible for reimbursement. Unknown public charging kWh remain blank, not zero.">Other expenses are not automatically eligible for reimbursement. Unknown public charging kWh remain blank, not zero.</span></p></details><details><summary><span data-i18n="Entries for the selected month">Entries for the selected month</span></summary><ul id="expense-list"></ul></details></section>
      <section id="odometer-section"><details><summary><span data-i18n="Odometer · automatic from the selected entity; manual input only when needed">Odometer · automatic from the selected entity; manual input only when needed</span></summary><p id="odometer-current"></p><p id="odometer-month"></p><label><span data-i18n="Manual odometer reading (km)">Manual odometer reading (km)</span><input id="odometer-value" type="number" min="0" step="1"></label><label><span data-i18n="Reading date and time">Reading date and time</span><input id="odometer-date" type="datetime-local"></label><button id="save-odometer"><span data-i18n="Save reading">Save reading</span></button><p class="sheet-help"><span data-i18n="The reading and timestamp are actual observations, not forecasts. Mileage does not affect energy reimbursement.">The reading and timestamp are actual observations, not forecasts. Mileage does not affect energy reimbursement.</span></p></details></section>
      <section id="invoice-section"><details id="invoice-editor"><summary><span data-i18n="Import home electricity invoice PDF">Import home electricity invoice PDF</span></summary><p><span data-i18n="The invoice, Moj Elektro data and comparison are processed automatically. A home electricity invoice is separate from an employer claim.">The invoice, Moj Elektro data and comparison are processed automatically. A home electricity invoice is separate from an employer claim.</span></p><input id="invoice" type="file" accept="application/pdf"><button id="upload"><span data-i18n="Import PDF">Import PDF</span></button></details>
        <div id="import-status" hidden><p id="import-label" role="status" aria-live="polite" aria-atomic="true"></p><progress id="import-progress" max="4" aria-label="Completed processing stages" data-i18n-aria-label="Completed processing stages"></progress>
          <ol id="stages"><li><span data-i18n="PDF received">PDF received</span></li><li><span data-i18n="Invoice parsed and validated">Invoice parsed and validated</span></li><li><span data-i18n="Moj Elektro and comparison">Moj Elektro and comparison</span></li><li><span data-i18n="Processing complete">Processing complete</span></li></ol>
          <p id="import-detail"></p><small id="import-meta"></small><br><button id="check" hidden><span data-i18n="Check status">Check status</span></button>
        </div></section>
      </main>`;
    this.querySelector('#vehicle-heading').textContent=this.t("{0} · monthly ledger", this.vehicleName());
    this.querySelector('#message').setAttribute('role','status'); this.querySelector('#message').setAttribute('aria-live','polite');
    this.querySelector('#ledger-tab').onclick=()=>this.setMode('ledger');
    this.querySelector('#forecast-tab').onclick=()=>this.setMode('forecast');
    this.querySelector('#deviations-tab').onclick=()=>this.setMode('deviations');
    this.querySelector('#forecast-range').onchange=()=>this.showMileage(this._mileageData);
    this.querySelector('#register-month').onchange=async()=>{try{await this._hass.callService('select','select_option',{entity_id:this.monthEntity(),option:this.querySelector('#register-month').value});}catch(e){this.msg(this.errorText(e),true);}};
    this.querySelector('#expense-date').value=new Date().toLocaleDateString('sv-SE');
    this.querySelector('#expense-eligible').checked=false;
    this.querySelector('#expense-kind').onchange=()=>{const other=this.querySelector('#expense-kind').value==='OTHER';this.querySelector('#expense-eligible').checked=false;this.querySelector('#expense-kwh').disabled=other;};
    this.querySelector('#save-expense').onclick=()=>this.saveExpense();
    this.querySelector('#save-rate').onclick=()=>this.saveRegister('register-rate',{rate_eur_per_kwh:this.querySelector('#claim-rate').value},'#save-rate');
    this.querySelector('#save-reported').onclick=()=>this.saveReported();
    this.querySelector('#save-odometer').onclick=()=>this.saveOdometer();
    this.querySelector('#copy-email').onclick=()=>this.copyEmail();
    this.querySelector("#upload").onclick=()=>this.uploadInvoice();
    this.querySelector("#check").onclick=()=>this.checkStatus();
    this.localize();
  }
  async filePayload(file) {
    if(!file) return {data_base64:""};
    if(file.size>15728640) throw new Error(this.t("The file is larger than 15 MiB"));
    const buffer=await file.arrayBuffer(); const bytes=new Uint8Array(buffer); let binary="";
    for(let i=0;i<bytes.length;i+=32768) binary+=String.fromCharCode(...bytes.subarray(i,i+32768));
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",buffer))).map(v=>v.toString(16).padStart(2,"0")).join("");
    return {data_base64:btoa(binary),filename:file.name,content_type:file.type,sha256:hash};
  }
  async uploadInvoice(){
    const button=this.querySelector("#upload");
    try{const file=this.querySelector("#invoice").files[0]; if(!file) throw new Error(this.t("Choose a PDF"));
      this._watchGeneration=(this._watchGeneration||0)+1;
      button.disabled=true; this.showProgress({step:0,level:"working",label:this.t("Preparing and uploading PDF …")});
      const payload=await this.filePayload(file);
      const result=await this._hass.callApi("post","energy_ledger/invoice",{...payload,idempotency_key:`invoice-${payload.sha256}`});
      this.watchJob(result.job_id);}
    catch(e){this.showProgress({step:0,level:"error",terminal:true,label:this.t("Import failed."),error_code:this.errorText(e)});}
    finally {button.disabled=false}
  }
  errorText(error){
    const status=error.status_code||error.status;
    const detail=error.body?.detail||error.message;
    if(status===413) return this.t("The PDF is too large (maximum 15 MiB).");
    if(status===415) return this.t("The selected file is not a valid PDF.");
    if(status===401||status===403) return this.t("Sign in with an administrator account to import invoices.");
    return typeof detail==="string"?this.t(detail.slice(0,500)):this.t("Could not connect to the service{0}.", status?this.t(" (HTTP {0})", status):"");
  }
  showProgress(progress,job={}){
    this._lastProgress={progress,job};
    const box=this.querySelector("#import-status"); box.hidden=false; box.dataset.level=progress.level;
    const label=this.querySelector("#import-label"); label.setAttribute("role",progress.level==="error"?"alert":"status"); label.textContent=this.t(progress.label);
    const bar=this.querySelector("#import-progress");
    if(progress.step===0&&progress.level==="working") bar.removeAttribute("value"); else bar.value=progress.step;
    bar.setAttribute("aria-valuetext",this.t(progress.label));
    this.querySelectorAll("#stages li").forEach((li,i)=>{li.className=i<progress.step?"done":i===progress.step?"active":"";});
    const next=progress.next_attempt_at?this.formatDateTime(progress.next_attempt_at):null;
    this.querySelector("#import-detail").textContent=[progress.error_code?this.t("Details: {0}", progress.error_code):"",next?this.t("Automatic retry: {0}. You do not need to import the invoice again.", next):"",progress.level==="error"&&job.job_id?this.t("The original PDF has been saved."):"",progress.level==="success"?this.t("Monthly data refreshes automatically. The cost estimate is not an accounting confirmation."):""].filter(Boolean).join(" ");
    this.querySelector("#import-meta").textContent=job.job_id?this.t("Month: {0} · Import: {1} · Updated: {2}", job.year_month||this.t("not yet determined"), job.job_id.slice(0,8), this.formatDateTime(new Date(),true)):"";
    this.querySelector("#check").hidden=!this._jobId;
  }
  async resumeLatest(){
    if(this._resumeRequested) return;
    this._resumeRequested=true;
    const generation=this._watchGeneration||0;
    try{
      const job=await this._hass.callApi("get","energy_ledger/invoice-job-latest");
      if(this.isConnected&&generation===(this._watchGeneration||0)) this.watchJob(job.job_id,job);
    }catch(e){
      if(this.isConnected&&generation===(this._watchGeneration||0)&&(e.status_code||e.status)!==404){
        this.showProgress({step:0,level:"error",label:this.t("Could not retrieve the latest import status."),error_code:this.errorText(e)});
        this.querySelector("#check").hidden=false;
      }
    }
  }
  checkStatus(){
    if(this._jobId) return this.watchJob(this._jobId);
    this._resumeRequested=false;
    return this.resumeLatest();
  }
  async watchJob(id,initial=null){
    this._jobId=id;
    const generation=this._watchGeneration=(this._watchGeneration||0)+1;
    let failures=0;
    while(this.isConnected&&generation===this._watchGeneration){
      let delay=2000;
      try{
        const job=initial||await this._hass.callApi("get",`energy_ledger/invoice-job-${id}`); initial=null;
        if(generation!==this._watchGeneration||!this.isConnected) return;
        if(!job.progress) throw new Error(this.t("The service does not support the new progress display yet. Refresh the page after updating."));
        this.showProgress(job.progress,job); failures=0;
        if(job.progress.terminal) return;
        if(["error","warning"].includes(job.progress.level)) delay=15000;
      }catch(e){
        if(generation!==this._watchGeneration||!this.isConnected) return;
        failures++;
        this.showProgress({step:1,level:"error",label:this.t("The progress connection was interrupted; processing may still be running."),error_code:this.errorText(e)},{job_id:id});
        if(failures>=3) return;
        delay=5000;
      }
      await new Promise(resolve=>setTimeout(resolve,delay));
    }
  }
  async addPublic(){
    try{const file=this.querySelector("#evidence").files[0]; const started=this.querySelector("#started").value;
      const body={...(await this.filePayload(file)),started_at:new Date(started).toISOString(),provider:this.querySelector("#provider").value,energy_kwh:this.querySelector("#kwh").value,gross_eur:this.querySelector("#gross").value,external_key:crypto.randomUUID(),idempotency_key:crypto.randomUUID()};
      const result=await this._hass.callApi("post","energy_ledger/public-charge",body); this.msg(JSON.stringify(result));}
    catch(e){this.msg(e.message,true)}
  }
  msg(text,error=false){const el=this.querySelector("#message");el.textContent=text;el.setAttribute('role',error?'alert':'status');el.style.color=error?"var(--error-color)":"var(--success-color)";}
  monthEntity(){return this._config?.month_entity || this._panel?.config?.month_entity || 'select.energy_ledger_report_month';}
  selectedMonth(){return this._hass.states?.[this.monthEntity()]?.state;}
  setMode(mode){
    this._mode=mode;
    for(const id of ['#sheet','#register','#expenses','#odometer-section','#invoice-section'])this.querySelector(id).hidden=mode!=='ledger';
    this.querySelector('#mileage').hidden=mode!=='forecast';
    this.querySelector('#mileage-comparison').hidden=mode!=='deviations';
    this.querySelector('#ledger-tab').setAttribute('aria-pressed',String(mode==='ledger'));
    this.querySelector('#forecast-tab').setAttribute('aria-pressed',String(mode==='forecast'));
    this.querySelector('#deviations-tab').setAttribute('aria-pressed',String(mode==='deviations'));
  }
  registerReady(){return !this._registerLoading&&this._registerData?.month===this.selectedMonth();}
  async chooseMonth(month,editor=null,kind=null){
    this._pendingEditor=editor?{month,editor,kind}:null;
    try{
      if(month!==this.selectedMonth())await this._hass.callService('select','select_option',{entity_id:this.monthEntity(),option:month});
      if(month===this.selectedMonth()){await this.syncRegister(true);this.openPendingEditor();}
    }catch(e){this._pendingEditor=null;this.msg(this.errorText(e),true);}
  }
  openPendingEditor(){
    const pending=this._pendingEditor;
    if(!pending||pending.month!==this._registerData?.month)return;
    const editor=this.querySelector('#'+pending.editor);editor.open=true;
    if(pending.kind){this.querySelector('#expense-kind').value=pending.kind;this.querySelector('#expense-kind').onchange();}
    editor.scrollIntoView?.({behavior:'smooth',block:'center'});this._pendingEditor=null;
  }
  applyEditingRules(){
    const data=this._registerData,locked=data?.status==='REPORTED',ready=this.registerReady();
    for(const id of ['#save-expense','#save-odometer','#save-rate'])this.querySelector(id).disabled=!ready||locked;
    this.querySelector('#copy-email').disabled=!ready;
    this.querySelector('#save-reported').disabled=!ready||locked||data?.requested_eur===null||data?.ready_to_report===false;
    for(const id of ['#reported-amount','#claim-rate','#expense-kind','#expense-date','#expense-provider','#expense-gross','#expense-kwh','#expense-eligible','#expense-notes','#odometer-value','#odometer-date'])this.querySelector(id).disabled=!ready||locked||(id==='#expense-kwh'&&this.querySelector('#expense-kind').value==='OTHER');
  }
  async syncRegister(force=false){
    const month=this.selectedMonth(); if(!/^\d{4}-(0[1-9]|1[0-2])$/.test(month||'')) return;
    const state=this._hass.states?.['sensor.energy_ledger_report_claim_status'];
    const version=month+'|'+(state?.last_updated||'');
    if(this._registerLoading||(!force&&version===this._registerVersion)) return;
    this._registerLoading=true;
    this._mileageData=null;this.querySelector('#mileage-table tbody').replaceChildren();this.querySelector('#mileage-summary').textContent=this.t("Loading forecast for {0} …", month);this.querySelector('#mileage-basis').textContent='';this.querySelector('#mileage-scenarios').textContent='';
    this.querySelector('#comparison-table tbody').replaceChildren();this.querySelector('#comparison-summary').textContent=this.t("Loading deviations for {0} …", month);
    this.querySelector('#register-summary').textContent=this.t("Loading ledger for {0} …", month);
    this.querySelector('#register-warning').textContent='';
    for(const id of ['#save-reported','#save-rate','#save-expense','#save-odometer','#copy-email'])this.querySelector(id).disabled=true;
    try{
      const select=this.querySelector('#register-month'); select.replaceChildren();
      for(const option of this._hass.states[this.monthEntity()].attributes.options||[month]) {const el=document.createElement('option');el.value=option;el.textContent=option;select.append(el);} select.value=month;
      const data=await this._hass.callApi('get',`energy_ledger/register-${month}`);
      if(month!==this.selectedMonth()||!this.isConnected) return;
      this._registerData=data; this._registerVersion=version;
      this.showRegister(data);
      const history=await this._hass.callApi('get','energy_ledger/register-history');
      if(month===this.selectedMonth()&&this.isConnected) this.showHistory(history.months||[]);
      if(month===this.selectedMonth()&&this.isConnected){
        try{
          const forecast=await this._hass.callApi('get',`energy_ledger/mileage-forecast-${month}`);
          if(month===this.selectedMonth()&&this.isConnected){this._mileageData=forecast;this.showMileage(forecast);}
        }catch(e){if(month===this.selectedMonth()){this.querySelector('#mileage-summary').textContent=this.t("The forecast is currently unavailable. ")+this.errorText(e);this.querySelector('#comparison-summary').textContent=this.t("The comparison is currently unavailable. ")+this.errorText(e);}}
      }
    }catch(e){this.querySelector('#register-summary').textContent=this.t("The ledger could not be refreshed. ")+this.errorText(e);}
    finally{this._registerLoading=false;if(month!==this.selectedMonth()&&this.isConnected)this.syncRegister();else {this.applyEditingRules();if(this.registerReady())this.openPendingEditor();}}
  }
  showRegister(data){
    this.querySelector('#month-heading').textContent=`${data.month} · ${data.status==='REPORTED'?this.t("already reported, read only"):this.t("enter missing data")}`;
    const value=x=>x===null||x===undefined?this.t("missing"):this.formatNumber(x,{maximumFractionDigits:4});
    this.querySelector('#register-summary').textContent=this.t("{0}: home {1} kWh × {2} €/kWh = {3} €. Eligible expenses: {4} €. Opening balance: {5} €. To report: {6} €. Already reported: {7} €.", data.month, value(data.home_kwh), value(data.reimbursement_rate), value(data.home_reimbursement_eur), value(data.eligible_expenses_eur), value(data.opening_balance_eur), value(data.requested_eur), value(data.reported_eur));
    const warnings=[]; if(data.current_home_kwh!==undefined) warnings.push(this.t("Rechecked home energy: {0} kWh ({1}); the reported month retains its original reading.", value(data.current_home_kwh), this.t(data.current_source_quality||'unknown quality')));if(!data.energy_complete) warnings.push(this.t("Total energy is not confirmed: check the selected meter history and missing public charging kWh.")); if(Number(data.pending_home_delta_eur)) warnings.push(this.t("Later home reimbursement difference: {0} €{1}; not included automatically.", this.formatNumber(data.pending_home_delta_eur,{minimumFractionDigits:2}), data.pending_delta_verified===false?this.t(" (unverified estimate)"):'')); if(data.status==='REPORTED') warnings.push(this.t("This month has already been reported; the original amount remains saved."));if(data.ready_to_report===false&&data.status!=='REPORTED')warnings.push(this.t("A month can be marked as reported after it ends and the meter history is complete."));
    this.querySelector('#register-warning').textContent=warnings.join(' ');
    this.querySelector('#email-text').value=data.requested_eur===null?this.t("The claim data is not complete yet."):this.t("Company vehicle {0} charging for {1}: {2} €.", this.vehicleName(), data.month, value(data.requested_eur));
    // Only initialise editable fields on month changes; HA updates must preserve typing.
    if(this._formMonth!==data.month){this._formMonth=data.month;this.querySelector('#claim-rate').value=data.reimbursement_rate||'';this.querySelector('#reported-amount').value=(data.status==='REPORTED'?data.reported_eur:data.requested_eur)||'';this.querySelector('#odometer-value').value='';this.querySelector('#odometer-date').value='';this.querySelector('#expense-date').value=data.month===new Date().toLocaleDateString('sv-SE').slice(0,7)?new Date().toLocaleDateString('sv-SE'):data.month+'-01';for(const id of ['#expense-provider','#expense-gross','#expense-kwh','#expense-notes'])this.querySelector(id).value='';for(const id of ['#expense-editor','#report-editor','#rate-editor'])this.querySelector(id).open=false;}
    this.querySelector('#save-reported').disabled=data.status==='REPORTED'||data.requested_eur===null||data.ready_to_report===false;
    const odometerEntity=this._config?.odometer_entity || this._panel?.config?.odometer_entity;
    const odometer=odometerEntity && this._hass.states?.[odometerEntity];
    this.querySelector('#odometer-current').textContent=odometer&&!['unknown','unavailable'].includes(odometer.state)?this.t("Current odometer ({0}): {1} km. HA update: {2}; this is not an automatic month-end reading for the selected month.", odometerEntity, this.formatNumber(odometer.state), this.formatDateTime(odometer.last_updated)):this.t("The mapped odometer is currently unavailable; a manual monthly reading can be entered.");
    this.querySelector('#odometer-month').textContent=this.t("Recorded odometer: {0} km; monthly distance: {1} km.", value(data.odometer_km), value(data.monthly_distance_km));
    const list=this.querySelector('#expense-list');list.replaceChildren();for(const expense of data.expenses||[]){const li=document.createElement('li');li.textContent=`${expense.occurred_date||expense.date}: ${expense.provider||expense.kind} · ${this.formatNumber(expense.gross_eur,{minimumFractionDigits:2})} € · ${expense.eligible?this.t("included in claim"):this.t("excluded from claim")}${expense.energy_kwh===null?this.t(" · kWh unknown"):''}${expense.notes?' · '+expense.notes:''}`;list.append(li);}
  }
  showHistory(months){
    this._historyMonths=months;
    const body=this.querySelector('#register-history tbody');body.replaceChildren();
    const keys=['month','odometer_km','monthly_distance_km','home_kwh','reimbursement_rate','home_reimbursement_eur','public_gross_eur','other_gross_eur','opening_balance_eur','monthly_eligible_eur','requested_eur','reported_eur','closing_balance_eur','status'];
    for(const month of [...months].sort((a,b)=>b.month.localeCompare(a.month))){
      const row=document.createElement('tr');row.className=month.month===this.selectedMonth()?'selected':'';
      for(const key of keys){
        const cell=document.createElement('td'),missing=month[key]===null||month[key]===undefined;
        let display=missing?'—':key==='month'?month[key]:key==='status'?(month.status==='REPORTED'?this.t("Reported 🔒"):this.t("Draft")):this.formatCell(month[key],key);
        const editor={public_gross_eur:['expense-editor','PUBLIC'],other_gross_eur:['expense-editor','OTHER'],reported_eur:['report-editor',null]}[key];
        if(key==='month'||(editor&&month.status!=='REPORTED')){
          const button=document.createElement('button');button.type='button';button.textContent=display+(editor?' ✎':'');button.setAttribute('aria-label',`${month.month}: ${key==='month'?this.t("select month"):key==='public_gross_eur'?this.t("add public charging"):key==='other_gross_eur'?this.t("add another expense"):this.t("enter the amount actually reported")}`);
          button.onclick=()=>this.chooseMonth(month.month,editor?.[0],editor?.[1]);cell.append(button);
        }else cell.textContent=display;
        row.append(cell);
      }
      body.append(row);
    }
    this.querySelector('#history-status').textContent=months.length?this.t("Home kWh, calculations and balances are read only. Legacy public charging records are monthly totals: do not enter the same payments again. Reported amounts remain unchanged."):this.t("No monthly records yet.");
  }
  formatCell(value,key){
    const digits=key==='home_kwh'?3:key==='reimbursement_rate'?4:key.endsWith('_km')?0:2;
    return this.formatNumber(value,{minimumFractionDigits:digits,maximumFractionDigits:digits});
  }
  showMileage(data){
    this.showComparisons(data);
    const body=this.querySelector('#mileage-table tbody');body.replaceChildren();
    if(!data?.available){this.querySelector('#mileage-summary').textContent=this.t("There are not enough valid completed readings or contract allowance details for a forecast yet.");return;}
    const km=x=>x===null||x===undefined?'—':this.formatCell(x,'distance_km');
    const final=data.final||{};
    this.querySelector('#mileage-summary').textContent=this.t("Forecast at contract end ({0}): {1} km. Allowance: {2} km. Expected excess: {3} km.", final.month||'—', km(final.predicted_odometer_km), km(final.allowance_km), km(final.excess_km));
    this.querySelector('#mileage-basis').textContent=this.t("Data through completed month {0}: odometer {1} km; {2} monthly distances from this installation. The forecast uses only this installation's history and a 12-month rolling average. Invalid or missing readings are not filled in.", data.anchor_month, km(data.anchor_odometer_km), data.historical_months);
    if(data.source_quality==='history_with_gaps')this.querySelector('#mileage-basis').textContent+=this.t(" Warning: some completed monthly readings are missing or invalid; missing mileage is not replaced with zero.");
    const rows=this.querySelector('#forecast-range').value==='all'?data.months:(data.months||[]).slice(0,12);
    for(const month of rows||[]){const row=document.createElement('tr');for(const key of ['month','predicted_distance_km','predicted_odometer_km','allowed_odometer_km','variance_km','seasonal_history_sensitivity_km','seasonal_history_odometer_km']){const cell=document.createElement('td');cell.textContent=key==='month'?month.month:km(key==='variance_km'?(month.predicted_odometer_km===null||month.allowed_odometer_km===null?null:month.predicted_odometer_km-month.allowed_odometer_km):month[key]);row.append(cell);}body.append(row);}
    this.querySelector('#mileage-scenarios').textContent=this.t("Scenario with a 20% lower / higher future pace: final odometer {0}–{1} km. This is a sensitivity scenario, not an 80% or 95% probability interval.", km(final.lower_pace_odometer_km), km(final.higher_pace_odometer_km));
  }
  showComparisons(data){
    const body=this.querySelector('#comparison-table tbody');body.replaceChildren();
    const rows=data?.history_comparison||[];
    this.querySelector('#comparison-summary').textContent=rows.length?this.t("{0} completed months from this installation. Historical average through the selected month: {1} km/month. This comparison is informational and does not change the financial ledger.", rows.length, this.formatCell(data.average_monthly_km,'distance_km')):this.t("There are not enough completed monthly records for a comparison yet.");
    for(const month of [...rows].sort((a,b)=>b.month.localeCompare(a.month))){const row=document.createElement('tr');for(const key of ['month','actual_distance_km','expected_distance_km','delta_forecast_km','delta_forecast_pct','average_distance_km','delta_average_km','delta_average_pct']){const cell=document.createElement('td'),value=month[key];cell.textContent=key==='month'?month.month:value===null||value===undefined?'—':(key.startsWith('delta_')&&Number(value)>0?'+':'')+this.formatCell(value,key.endsWith('_pct')?'percent':key)+(key.endsWith('_pct')?' %':'');row.append(cell);}body.append(row);}
  }
  async saveRegister(action,payload,buttonId){
    if(!this.registerReady()){this.msg(this.t("Wait for the selected month's data."),true);return false;}
    const month=this.selectedMonth();
    const button=this.querySelector(buttonId);button.disabled=true;
    try{await this._hass.callApi('post',`energy_ledger/${action}`,{month,...payload});this.msg(this.t("Saved for {0}.", month));await this.syncRegister(true);return true;}
    catch(e){this.msg(this.errorText(e),true);return false;}
    finally{this.applyEditingRules();}
  }
  async saveExpense(){
    const gross=this.querySelector('#expense-gross').value,date=this.querySelector('#expense-date').value,provider=this.querySelector('#expense-provider').value.trim();
    const kind=this.querySelector('#expense-kind').value,kwh=this.querySelector('#expense-kwh').value;
    if(!date||!provider||!gross||Number(gross)<0||(kwh&&Number(kwh)<=0)){this.msg(this.t("Enter a date, provider/category and valid amount; kWh are optional."),true);return;}
    const body={date,kind,provider,gross_eur:gross,energy_kwh:kind==='PUBLIC'&&kwh?kwh:null,eligible:this.querySelector('#expense-eligible').checked,notes:this.querySelector('#expense-notes').value};
    const signature=JSON.stringify({...body,month:this.selectedMonth()});if(this._expenseSignature!==signature){this._expenseSignature=signature;this._expenseKey=crypto.randomUUID();}
    if(await this.saveRegister('register-expense',{...body,idempotency_key:this._expenseKey},'#save-expense')){for(const id of ['#expense-gross','#expense-kwh','#expense-notes'])this.querySelector(id).value='';this._expenseKey=null;this._expenseSignature=null;}
  }
  async saveReported(){
    if(!this.registerReady()){this.msg(this.t("Wait for the selected month's data."),true);return;}
    const amount=this.querySelector('#reported-amount').value;if(!amount||Number(amount)<0){this.msg(this.t("Enter the amount you actually reported."),true);return;}
    if(!confirm(this.t("Save €{0} as the amount actually reported for {1}? No email will be sent.", amount, this.selectedMonth())))return;
    const signature=this.selectedMonth()+'|'+amount;if(this._reportedSignature!==signature){this._reportedSignature=signature;this._reportedKey=crypto.randomUUID();}
    await this.saveRegister('register-reported',{amount_eur:amount,idempotency_key:this._reportedKey},'#save-reported');
  }
  async saveOdometer(){
    const km=this.querySelector('#odometer-value').value,date=this.querySelector('#odometer-date').value;
    if(!km||Number(km)<0||!date){this.msg(this.t("Enter the odometer reading and its actual timestamp."),true);return;}
    await this.saveRegister('register-odometer',{odometer_km:Number(km),observed_at:new Date(date).toISOString(),source:'manual'},'#save-odometer');
  }
  async copyEmail(){try{await navigator.clipboard.writeText(this.querySelector('#email-text').value);this.msg(this.t("Text copied; send it in your own email."));}catch(e){this.querySelector('#email-text').select();this.msg(this.t("Copy the selected text manually."));}}
}
if(!customElements.get("energy-ledger-native-panel")) customElements.define("energy-ledger-native-panel",EnergyLedgerPanel);
