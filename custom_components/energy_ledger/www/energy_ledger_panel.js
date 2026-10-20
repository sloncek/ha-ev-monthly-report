class EnergyLedgerPanel extends HTMLElement {
  setConfig(config) { this._config=config; }
  vehicleName() { return this._config?.vehicle_name || this._panel?.config?.vehicle_name || 'EV'; }
  getCardSize() { return 12; }
  set hass(value) { this._hass=value; if(!this._rendered) this.render(); if(this.isConnected&&!this._resumeRequested) this.resumeLatest(); if(this.isConnected) this.syncRegister(); }
  set panel(value) { this._panel=value; }
  connectedCallback(){if(this._hass) {this.resumeLatest(); this.syncRegister();}}
  disconnectedCallback(){this._watchGeneration=(this._watchGeneration||0)+1; this._resumeRequested=false;}
  render() {
    this._rendered=true;
    this.innerHTML=`<style>energy-ledger-panel section{background:var(--card-background-color)}energy-ledger-panel label{display:block;margin-top:12px}energy-ledger-panel input{width:100%;box-sizing:border-box;padding:10px}energy-ledger-panel button{cursor:pointer}energy-ledger-panel progress{width:100%;height:14px;accent-color:var(--primary-color)}energy-ledger-panel #import-status{margin-top:20px;padding:16px;border:1px solid var(--divider-color);border-radius:8px}energy-ledger-panel #import-status[data-level=error]{border-color:var(--error-color)}energy-ledger-panel #import-status[data-level=warning]{border-color:var(--warning-color,#ef9b0f)}energy-ledger-panel #import-status[data-level=success]{border-color:var(--success-color)}energy-ledger-panel #import-status p{overflow-wrap:anywhere}energy-ledger-panel #stages{padding-left:24px;color:var(--secondary-text-color)}energy-ledger-panel #stages li{padding:4px}energy-ledger-panel #stages .done{color:var(--success-color)}energy-ledger-panel #stages .active{color:var(--primary-text-color);font-weight:600}energy-ledger-panel small{color:var(--secondary-text-color)}</style>
      <style>energy-ledger-panel{display:block}energy-ledger-panel main{max-width:1600px;margin:0 auto;padding:16px;font-family:var(--paper-font-body1_-_font-family,Arial)}energy-ledger-panel section{padding:16px;border:1px solid var(--divider-color);margin:12px 0;border-radius:8px}energy-ledger-panel h1{font-size:24px;margin:8px 0}energy-ledger-panel h2{font-size:18px;margin:0 0 12px}energy-ledger-panel button{font:inherit;border:1px solid var(--divider-color);border-radius:5px;background:var(--card-background-color);color:var(--primary-color);margin:4px 0;padding:8px 12px}energy-ledger-panel button:disabled{color:var(--disabled-text-color,#888);cursor:default}energy-ledger-panel input,energy-ledger-panel select,energy-ledger-panel textarea{font:inherit;color:var(--primary-text-color);background:var(--secondary-background-color);border:1px solid var(--divider-color);border-radius:4px}energy-ledger-panel select{padding:9px}energy-ledger-panel .sheet-scroll{overflow:auto;max-height:62vh;border:1px solid var(--divider-color)}energy-ledger-panel table{border-collapse:separate;border-spacing:0;width:100%;font-size:14px;font-variant-numeric:tabular-nums}energy-ledger-panel th,energy-ledger-panel td{padding:9px 10px;border-right:1px solid var(--divider-color);border-bottom:1px solid var(--divider-color);white-space:nowrap;text-align:right}energy-ledger-panel th{position:sticky;top:0;background:var(--secondary-background-color);z-index:2;text-align:center;font-size:12px}energy-ledger-panel th:first-child,energy-ledger-panel td:first-child{position:sticky;left:0;text-align:left;background:var(--card-background-color);z-index:1}energy-ledger-panel th:first-child{z-index:3}energy-ledger-panel tbody tr:nth-child(even) td{background:var(--secondary-background-color)}energy-ledger-panel tr.selected td{background:var(--primary-color-light,#dbeffc);color:var(--primary-text-color)}energy-ledger-panel tr.selected{outline:2px solid var(--primary-color);outline-offset:-2px}energy-ledger-panel td button{padding:3px 6px;font-size:13px;white-space:nowrap}energy-ledger-panel .manual{color:var(--primary-color)}energy-ledger-panel .sheet-help{font-size:13px;color:var(--secondary-text-color)}energy-ledger-panel details{margin:12px 0}energy-ledger-panel summary{cursor:pointer;font-weight:600;padding:8px 0}energy-ledger-panel .entry-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;align-items:end}energy-ledger-panel .entry-grid label{margin:0}energy-ledger-panel .entry-grid select{width:100%;box-sizing:border-box}energy-ledger-panel .entry-grid .wide{grid-column:span 2}energy-ledger-panel #register-warning{font-size:13px;color:var(--secondary-text-color)}energy-ledger-panel #register-summary{font-size:14px}energy-ledger-panel .toolbar{display:flex;align-items:center;gap:16px;flex-wrap:wrap}energy-ledger-panel .toolbar label{margin:0}energy-ledger-panel .tools{margin-left:auto}energy-ledger-panel a{color:var(--primary-color)}@media(max-width:700px){energy-ledger-panel main{padding:8px}energy-ledger-panel section{padding:12px}energy-ledger-panel .entry-grid{grid-template-columns:repeat(2,minmax(0,1fr))}energy-ledger-panel .tools{margin-left:0}energy-ledger-panel th,energy-ledger-panel td{padding:8px}energy-ledger-panel .sheet-scroll{max-height:58vh}}</style>
      <style>energy-ledger-panel tr.selected td{background:var(--secondary-background-color)}</style><main><h1 id="vehicle-heading"></h1><p id="message" style="position:sticky;top:0;background:var(--card-background-color);z-index:4" role="status" aria-live="polite"></p>
      <div class="toolbar"><label>Izbrani mesec <select id="register-month" aria-label="Mesec poročila"></select></label></div><nav aria-label="Pogled evidence"><button id="ledger-tab" aria-pressed="true">Polnjenja in stroški</button> <button id="forecast-tab" aria-pressed="false">Napoved kilometrov</button> <button id="deviations-tab" aria-pressed="false">Odstopanja kilometrov</button></nav>
      <section id="mileage-comparison" hidden><h2>Dejanski kilometri proti pričakovanim</h2><p id="comparison-summary" role="status" aria-live="polite">Nalagam primerjavo …</p><div class="sheet-scroll" tabindex="0" aria-label="Odstopanja kilometrov, samo za branje"><table id="comparison-table"><caption style="text-align:left;padding:8px">Zaključeni meseci iz te namestitve · pozitiven odmik pomeni več vožnje</caption><thead><tr><th scope="col">Mesec</th><th scope="col">Dejansko km</th><th scope="col">Pričakovano km</th><th scope="col">Odmik km</th><th scope="col">Odmik %</th><th scope="col">Povprečje km</th><th scope="col">Odmik od povp. km</th><th scope="col">Odmik od povp. %</th></tr></thead><tbody></tbody></table></div><p class="sheet-help">Primerjava je retrospektivna in uporablja samo predhodne zaključene mesečne razdalje v tej namestitvi. Za izračun so potrebni vsaj trije predhodni meseci z veljavnimi odčitki.</p></section>
      <section id="sheet"><p class="sheet-help">Ena vrstica = en mesec. Sivi podatki se izračunajo sami. Modri gumbi odprejo samo potrebni vnos. Na telefonu tabelo pomakni levo/desno.</p><div class="sheet-scroll" tabindex="0" aria-label="Mesečna preglednica, vodoravno pomična"><table id="register-history"><caption style="text-align:left;padding:8px">Evidenca polnjenj in povračil · zneski v €</caption><thead><tr><th scope="col">Mesec</th><th scope="col">Števec km</th><th scope="col">Prevoženo km</th><th scope="col">Doma kWh</th><th scope="col">Tarifa €/kWh</th><th scope="col">Doma €</th><th scope="col" class="manual">Javno € ✎</th><th scope="col" class="manual">Drugo € ✎</th><th scope="col">Prenos prej €</th><th scope="col">Upravičeno €</th><th scope="col">Za sporočiti €</th><th scope="col" class="manual">Sporočeno € ✎</th><th scope="col">Prenos naprej €</th><th scope="col">Stanje</th></tr></thead><tbody></tbody></table></div><p id="history-status" class="sheet-help"></p></section>
      <section id="mileage" hidden><h2>Napoved kilometrov iz celotne zgodovine</h2><p id="mileage-summary" role="status" aria-live="polite">Nalagam napoved …</p><p id="mileage-basis" class="sheet-help"></p><label>Obdobje prikaza <select id="forecast-range"><option value="12">Naslednjih 12 mesecev</option><option value="all">Do konca pogodbe</option></select></label><div class="sheet-scroll" tabindex="0" aria-label="Napoved kilometrov, samo za branje"><table id="mileage-table"><caption style="text-align:left;padding:8px">Prihodnji kilometri · napoved, ne dejanski odčitki</caption><thead><tr><th scope="col">Mesec</th><th scope="col">Napoved km</th><th scope="col">Napoved števca</th><th scope="col">Pogodbeni načrt</th><th scope="col">Odmik km</th><th scope="col">Sezonska primerjava km</th><th scope="col">Sezonski števec</th></tr></thead><tbody></tbody></table></div><p id="mileage-scenarios" class="sheet-help"></p><p class="sheet-help">Napoved ne vpliva na zahtevke za povračilo. Novi veljavni zaključeni odčitki posodobijo nadaljnjo napoved samodejno; odčitek sredi meseca ni zaključena mesečna kilometrina. Sezonska primerjava na preteklih preizkusih ni bila natančnejša od osnovne metode.</p></section>
      <section id="register"><h2 id="month-heading">Izbrani mesec</h2><p id="register-summary" role="status" aria-live="polite"></p><p id="register-warning"></p><details id="report-editor"><summary>✎ Sporočeni znesek in besedilo za email</summary><label>Besedilo za email<textarea id="email-text" rows="2" readonly style="width:100%;box-sizing:border-box"></textarea></label><button id="copy-email">Kopiraj besedilo</button><label>Znesek, ki si ga dejansko sporočil (€)<input id="reported-amount" type="number" min="0" step="0.01"></label><button id="save-reported">Označi kot sporočeno</button><p class="sheet-help">Email pošlješ sam. Potrdi šele dejansko sporočeni znesek. Že sporočeni meseci so zaščiteni; naknadne razlike niso samodejni popravek.</p></details><details id="rate-editor"><summary>Nastavitev tarife · samo ob spremembi</summary><label>Končna tarifa €/kWh od izbranega meseca naprej<input id="claim-rate" type="number" min="0" max="10" step="0.0001"></label><button id="save-rate">Shrani tarifo</button><p class="sheet-help">Tarifa delodajalca ni cena domačega računa; DDV se ji ne prišteva.</p></details></section>
      <section id="expenses"><details id="expense-editor"><summary>✎ Dodaj javno polnjenje ali drug strošek</summary><div class="entry-grid"><label>Vrsta<select id="expense-kind"><option value="PUBLIC">Javno polnjenje</option><option value="OTHER">Drug strošek</option></select></label><label>Datum<input id="expense-date" type="date"></label><label>Ponudnik / kategorija<input id="expense-provider" maxlength="200"></label><label>Plačano z DDV (€)<input id="expense-gross" type="number" min="0" step="0.01"></label><label>kWh (neobvezno)<input id="expense-kwh" type="number" min="0.001" step="0.001"></label><label class="wide"><input id="expense-eligible" type="checkbox" style="width:auto"> Vključi v zahtevek delodajalcu</label><label class="wide">Opomba (neobvezno)<input id="expense-notes" maxlength="2000"></label><button id="save-expense">Dodaj vrstico</button></div><p class="sheet-help">Drug strošek ni samodejno upravičen do povračila. Neznani javni kWh ostanejo prazni, ne nič.</p></details><details><summary>Vpisane postavke izbranega meseca</summary><ul id="expense-list"></ul></details></section>
      <section id="odometer-section"><details><summary>Števec kilometrov · samodejno iz Kie; ročni vnos samo izjemoma</summary><p id="odometer-current"></p><p id="odometer-month"></p><label>Ročni odčitek števca (km)<input id="odometer-value" type="number" min="0" step="1"></label><label>Datum in čas odčitka<input id="odometer-date" type="datetime-local"></label><button id="save-odometer">Shrani odčitek</button><p class="sheet-help">Odčitek in čas nista napoved. Kilometri ne vplivajo na povračilo energije.</p></details></section>
      <section id="invoice-section"><details id="invoice-editor"><summary>Uvozi domači račun PDF</summary><p>Račun, Moj Elektro in primerjava se obdelajo samodejno. Domači račun ni zahtevek delodajalcu.</p><input id="invoice" type="file" accept="application/pdf"><button id="upload">Uvozi PDF</button></details>
        <div id="import-status" hidden><p id="import-label" role="status" aria-live="polite" aria-atomic="true"></p><progress id="import-progress" max="4" aria-label="Zaključene faze obdelave"></progress>
          <ol id="stages"><li>PDF sprejet</li><li>Račun prebran in preverjen</li><li>Moj Elektro in primerjava</li><li>Obdelava zaključena</li></ol>
          <p id="import-detail"></p><small id="import-meta"></small><br><button id="check" hidden>Preveri stanje</button>
        </div></section>
      </main>`;
    this.querySelector('#vehicle-heading').textContent=`${this.vehicleName()} · mesečna preglednica`;
    this.querySelector('#message').setAttribute('role','status'); this.querySelector('#message').setAttribute('aria-live','polite');
    this.querySelector('#ledger-tab').onclick=()=>this.setMode('ledger');
    this.querySelector('#forecast-tab').onclick=()=>this.setMode('forecast');
    this.querySelector('#deviations-tab').onclick=()=>this.setMode('deviations');
    this.querySelector('#forecast-range').onchange=()=>this.showMileage(this._mileageData);
    this.querySelector('#register-month').onchange=async()=>{try{await this._hass.callService('select','select_option',{entity_id:'select.energy_ledger_report_month',option:this.querySelector('#register-month').value});}catch(e){this.msg(this.errorText(e),true);}};
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
  }
  async filePayload(file) {
    if(!file) return {data_base64:""};
    if(file.size>15728640) throw new Error("Datoteka je večja od 15 MiB");
    const buffer=await file.arrayBuffer(); const bytes=new Uint8Array(buffer); let binary="";
    for(let i=0;i<bytes.length;i+=32768) binary+=String.fromCharCode(...bytes.subarray(i,i+32768));
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",buffer))).map(v=>v.toString(16).padStart(2,"0")).join("");
    return {data_base64:btoa(binary),filename:file.name,content_type:file.type,sha256:hash};
  }
  async uploadInvoice(){
    const button=this.querySelector("#upload");
    try{const file=this.querySelector("#invoice").files[0]; if(!file) throw new Error("Izberi PDF");
      this._watchGeneration=(this._watchGeneration||0)+1;
      button.disabled=true; this.showProgress({step:0,level:"working",label:"Pripravljam in nalagam PDF …"});
      const payload=await this.filePayload(file);
      const result=await this._hass.callApi("post","energy_ledger/invoice",{...payload,idempotency_key:`invoice-${payload.sha256}`});
      this.watchJob(result.job_id);}
    catch(e){this.showProgress({step:0,level:"error",terminal:true,label:"Uvoz ni uspel.",error_code:this.errorText(e)});}
    finally {button.disabled=false}
  }
  errorText(error){
    const status=error.status_code||error.status;
    const detail=error.body?.detail||error.message;
    if(status===413) return "PDF je prevelik (največ 15 MiB).";
    if(status===415) return "Izbrana datoteka ni veljaven PDF.";
    if(status===401||status===403) return "Za uvoz se prijavi z administratorskim računom.";
    return typeof detail==="string"?detail.slice(0,500):`Povezava s servisom ni uspela${status?` (HTTP ${status})`:""}.`;
  }
  showProgress(progress,job={}){
    const box=this.querySelector("#import-status"); box.hidden=false; box.dataset.level=progress.level;
    const label=this.querySelector("#import-label"); label.setAttribute("role",progress.level==="error"?"alert":"status"); label.textContent=progress.label;
    const bar=this.querySelector("#import-progress");
    if(progress.step===0&&progress.level==="working") bar.removeAttribute("value"); else bar.value=progress.step;
    bar.setAttribute("aria-valuetext",progress.label);
    this.querySelectorAll("#stages li").forEach((li,i)=>{li.className=i<progress.step?"done":i===progress.step?"active":"";});
    const next=progress.next_attempt_at?new Date(progress.next_attempt_at).toLocaleString("sl-SI"):null;
    this.querySelector("#import-detail").textContent=[progress.error_code?`Podrobnosti: ${progress.error_code}`:"",next?`Samodejni ponovni poskus: ${next}. Računa ni treba ponovno uvoziti.`:"",progress.level==="error"&&job.job_id?"Izvirni PDF je shranjen.":"",progress.level==="success"?"Mesečni podatki se osvežijo samodejno. Ocena stroška ni računovodska potrditev.":""].filter(Boolean).join(" ");
    this.querySelector("#import-meta").textContent=job.job_id?`Mesec: ${job.year_month||"še ni določen"} · Uvoz: ${job.job_id.slice(0,8)} · Osveženo: ${new Date().toLocaleTimeString("sl-SI")}`:"";
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
        this.showProgress({step:0,level:"error",label:"Stanja zadnjega uvoza ne morem pridobiti.",error_code:this.errorText(e)});
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
        if(!job.progress) throw new Error("Servis še nima novega prikaza napredka. Osveži stran po posodobitvi.");
        this.showProgress(job.progress,job); failures=0;
        if(job.progress.terminal) return;
        if(["error","warning"].includes(job.progress.level)) delay=15000;
      }catch(e){
        if(generation!==this._watchGeneration||!this.isConnected) return;
        failures++;
        this.showProgress({step:1,level:"error",label:"Povezava za prikaz napredka je prekinjena; obdelava lahko še teče.",error_code:this.errorText(e)},{job_id:id});
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
  selectedMonth(){return this._hass.states?.['select.energy_ledger_report_month']?.state;}
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
      if(month!==this.selectedMonth())await this._hass.callService('select','select_option',{entity_id:'select.energy_ledger_report_month',option:month});
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
    this._mileageData=null;this.querySelector('#mileage-table tbody').replaceChildren();this.querySelector('#mileage-summary').textContent=`Nalagam napoved za ${month} …`;this.querySelector('#mileage-basis').textContent='';this.querySelector('#mileage-scenarios').textContent='';
    this.querySelector('#comparison-table tbody').replaceChildren();this.querySelector('#comparison-summary').textContent=`Nalagam odstopanja za ${month} …`;
    this.querySelector('#register-summary').textContent=`Nalagam evidenco za ${month} …`;
    this.querySelector('#register-warning').textContent='';
    for(const id of ['#save-reported','#save-rate','#save-expense','#save-odometer','#copy-email'])this.querySelector(id).disabled=true;
    try{
      const select=this.querySelector('#register-month'); select.replaceChildren();
      for(const option of this._hass.states['select.energy_ledger_report_month'].attributes.options||[month]) {const el=document.createElement('option');el.value=option;el.textContent=option;select.append(el);} select.value=month;
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
        }catch(e){if(month===this.selectedMonth()){this.querySelector('#mileage-summary').textContent='Napoved trenutno ni dosegljiva. '+this.errorText(e);this.querySelector('#comparison-summary').textContent='Primerjava trenutno ni dosegljiva. '+this.errorText(e);}}
      }
    }catch(e){this.querySelector('#register-summary').textContent='Evidence trenutno ni mogoče osvežiti. '+this.errorText(e);}
    finally{this._registerLoading=false;if(month!==this.selectedMonth()&&this.isConnected)this.syncRegister();else {this.applyEditingRules();if(this.registerReady())this.openPendingEditor();}}
  }
  showRegister(data){
    this.querySelector('#month-heading').textContent=`${data.month} · ${data.status==='REPORTED'?'že sporočeno, samo za branje':'vnos manjkajočih podatkov'}`;
    const value=x=>x===null||x===undefined?'manjka':String(x);
    this.querySelector('#register-summary').textContent=`${data.month}: doma ${value(data.home_kwh)} kWh × ${value(data.reimbursement_rate)} €/kWh = ${value(data.home_reimbursement_eur)} €. Upravičeni stroški: ${value(data.eligible_expenses_eur)} €. Prenos: ${value(data.opening_balance_eur)} €. Za sporočiti: ${value(data.requested_eur)} €. Že sporočeno: ${value(data.reported_eur)} €.`;
    const warnings=[]; if(data.current_home_kwh!==undefined) warnings.push(`Naknadno preverjena energija doma: ${value(data.current_home_kwh)} kWh (${data.current_source_quality||'neznana kakovost'}); že sporočeni mesec ohranja prvotni odčitek.`);if(!data.energy_complete) warnings.push('Celotna energija ni potrjena: preveri zgodovino izbranega števca in manjkajoče javne kWh.'); if(Number(data.pending_home_delta_eur)) warnings.push(`Naknadna razlika domačega povračila: ${data.pending_home_delta_eur} €${data.pending_delta_verified===false?' (nepotrjena ocena)':''}; ni vključena samodejno.`); if(data.status==='REPORTED') warnings.push('Ta mesec je že sporočen; izvirni znesek ostaja shranjen.');if(data.ready_to_report===false&&data.status!=='REPORTED')warnings.push('Označitev kot sporočeno je možna po koncu meseca in popolni zgodovini števca.');
    this.querySelector('#register-warning').textContent=warnings.join(' ');
    this.querySelector('#email-text').value=data.requested_eur===null?'Podatki za zahtevek še niso popolni.':`Polnjenje službenega vozila ${this.vehicleName()} za ${data.month}: ${value(data.requested_eur)} €.`;
    // Only initialise editable fields on month changes; HA updates must preserve typing.
    if(this._formMonth!==data.month){this._formMonth=data.month;this.querySelector('#claim-rate').value=data.reimbursement_rate||'';this.querySelector('#reported-amount').value=(data.status==='REPORTED'?data.reported_eur:data.requested_eur)||'';this.querySelector('#odometer-value').value='';this.querySelector('#odometer-date').value='';this.querySelector('#expense-date').value=data.month===new Date().toLocaleDateString('sv-SE').slice(0,7)?new Date().toLocaleDateString('sv-SE'):data.month+'-01';for(const id of ['#expense-provider','#expense-gross','#expense-kwh','#expense-notes'])this.querySelector(id).value='';for(const id of ['#expense-editor','#report-editor','#rate-editor'])this.querySelector(id).open=false;}
    this.querySelector('#save-reported').disabled=data.status==='REPORTED'||data.requested_eur===null||data.ready_to_report===false;
    const odometerEntity=this._config?.odometer_entity || this._panel?.config?.odometer_entity;
    const odometer=odometerEntity && this._hass.states?.[odometerEntity];
    this.querySelector('#odometer-current').textContent=odometer&&!['unknown','unavailable'].includes(odometer.state)?`Trenutni števec (${odometerEntity}): ${odometer.state} km. HA-posodobitev: ${odometer.last_updated}; to ni samodejen odčitek ob koncu izbranega meseca.`:'Zemljevidani števec trenutno ni na voljo; ročni mesečni odčitek je mogoč.';
    this.querySelector('#odometer-month').textContent=`Evidentirani števec: ${value(data.odometer_km)} km; razdalja meseca: ${value(data.monthly_distance_km)} km.`;
    const list=this.querySelector('#expense-list');list.replaceChildren();for(const expense of data.expenses||[]){const li=document.createElement('li');li.textContent=`${expense.occurred_date||expense.date}: ${expense.provider||expense.kind} · ${expense.gross_eur} € · ${expense.eligible?'v zahtevku':'ni v zahtevku'}${expense.energy_kwh===null?' · kWh neznani':''}${expense.notes?' · '+expense.notes:''}`;list.append(li);}
  }
  showHistory(months){
    const body=this.querySelector('#register-history tbody');body.replaceChildren();
    const keys=['month','odometer_km','monthly_distance_km','home_kwh','reimbursement_rate','home_reimbursement_eur','public_gross_eur','other_gross_eur','opening_balance_eur','monthly_eligible_eur','requested_eur','reported_eur','closing_balance_eur','status'];
    for(const month of [...months].sort((a,b)=>b.month.localeCompare(a.month))){
      const row=document.createElement('tr');row.className=month.month===this.selectedMonth()?'selected':'';
      for(const key of keys){
        const cell=document.createElement('td'),missing=month[key]===null||month[key]===undefined;
        let display=missing?'—':key==='month'?month[key]:key==='status'?(month.status==='REPORTED'?'Sporočeno 🔒':'Osnutek'):this.formatCell(month[key],key);
        const editor={public_gross_eur:['expense-editor','PUBLIC'],other_gross_eur:['expense-editor','OTHER'],reported_eur:['report-editor',null]}[key];
        if(key==='month'||(editor&&month.status!=='REPORTED')){
          const button=document.createElement('button');button.type='button';button.textContent=display+(editor?' ✎':'');button.setAttribute('aria-label',`${month.month}: ${key==='month'?'izberi mesec':key==='public_gross_eur'?'dodaj javno polnjenje':key==='other_gross_eur'?'dodaj drug strošek':'vpiši dejansko sporočeni znesek'}`);
          button.onclick=()=>this.chooseMonth(month.month,editor?.[0],editor?.[1]);cell.append(button);
        }else cell.textContent=display;
        row.append(cell);
      }
      body.append(row);
    }
    this.querySelector('#history-status').textContent=months.length?'Domači kWh, izračuni in prenos so samo za branje. Stara javna polnjenja so mesečni seštevki: istih plačil ne vpisuj ponovno. Že sporočeni zneski se ne spreminjajo.':'Še ni mesečnih zapisov.';
  }
  formatCell(value,key){
    const digits=key==='home_kwh'?3:key==='reimbursement_rate'?4:key.endsWith('_km')?0:2;
    return new Intl.NumberFormat('sl-SI',{minimumFractionDigits:digits,maximumFractionDigits:digits}).format(Number(value));
  }
  showMileage(data){
    this.showComparisons(data);
    const body=this.querySelector('#mileage-table tbody');body.replaceChildren();
    if(!data?.available){this.querySelector('#mileage-summary').textContent='Za napoved še ni dovolj veljavnih zaključenih odčitkov ali pogodbenega načrta.';return;}
    const km=x=>x===null||x===undefined?'—':this.formatCell(x,'distance_km');
    const final=data.final||{};
    this.querySelector('#mileage-summary').textContent=`Napoved ob koncu pogodbe (${final.month||'—'}): ${km(final.predicted_odometer_km)} km. Limit: ${km(final.allowance_km)} km. Predvideni presežek: ${km(final.excess_km)} km.`;
    this.querySelector('#mileage-basis').textContent=`Podatki do zaključenega meseca ${data.anchor_month}: števec ${km(data.anchor_odometer_km)} km; ${data.historical_months} lastnih mesečnih razdalj. Napoved uporablja samo zgodovino te namestitve in 12-mesečno drseče povprečje. Neveljavni ali manjkajoči odčitki niso dopolnjeni.`;
    if(data.source_quality==='history_with_gaps')this.querySelector('#mileage-basis').textContent+=' Opozorilo: nekateri zaključeni mesečni odčitki manjkajo ali so neveljavni; izpuščeni kilometri niso nadomeščeni z ničlo.';
    const rows=this.querySelector('#forecast-range').value==='all'?data.months:(data.months||[]).slice(0,12);
    for(const month of rows||[]){const row=document.createElement('tr');for(const key of ['month','predicted_distance_km','predicted_odometer_km','allowed_odometer_km','variance_km','seasonal_history_sensitivity_km','seasonal_history_odometer_km']){const cell=document.createElement('td');cell.textContent=key==='month'?month.month:km(key==='variance_km'?(month.predicted_odometer_km===null||month.allowed_odometer_km===null?null:month.predicted_odometer_km-month.allowed_odometer_km):month[key]);row.append(cell);}body.append(row);}
    this.querySelector('#mileage-scenarios').textContent=`Scenarij 20 % nižjega / višjega prihodnjega tempa: končni števec ${km(final.lower_pace_odometer_km)}–${km(final.higher_pace_odometer_km)} km. To je občutljivost, ne 80- ali 95-odstotni verjetnostni interval.`;
  }
  showComparisons(data){
    const body=this.querySelector('#comparison-table tbody');body.replaceChildren();
    const rows=data?.history_comparison||[];
    this.querySelector('#comparison-summary').textContent=rows.length?`${rows.length} zaključenih mesecev te namestitve. Zgodovinsko povprečje do izbranega meseca: ${this.formatCell(data.average_monthly_km,'distance_km')} km/mesec. Primerjava je informativna in ne spreminja finančne evidence.`:'Za primerjavo še ni dovolj zaključenih mesečnih podatkov.';
    for(const month of [...rows].sort((a,b)=>b.month.localeCompare(a.month))){const row=document.createElement('tr');for(const key of ['month','actual_distance_km','expected_distance_km','delta_forecast_km','delta_forecast_pct','average_distance_km','delta_average_km','delta_average_pct']){const cell=document.createElement('td'),value=month[key];cell.textContent=key==='month'?month.month:value===null||value===undefined?'—':(key.startsWith('delta_')&&Number(value)>0?'+':'')+this.formatCell(value,key.endsWith('_pct')?'percent':key)+(key.endsWith('_pct')?' %':'');row.append(cell);}body.append(row);}
  }
  async saveRegister(action,payload,buttonId){
    if(!this.registerReady()){this.msg('Počakaj na podatke izbranega meseca.',true);return false;}
    const month=this.selectedMonth();
    const button=this.querySelector(buttonId);button.disabled=true;
    try{await this._hass.callApi('post',`energy_ledger/${action}`,{month,...payload});this.msg(`Shranjeno za ${month}.`);await this.syncRegister(true);return true;}
    catch(e){this.msg(this.errorText(e),true);return false;}
    finally{this.applyEditingRules();}
  }
  async saveExpense(){
    const gross=this.querySelector('#expense-gross').value,date=this.querySelector('#expense-date').value,provider=this.querySelector('#expense-provider').value.trim();
    const kind=this.querySelector('#expense-kind').value,kwh=this.querySelector('#expense-kwh').value;
    if(!date||!provider||!gross||Number(gross)<0||(kwh&&Number(kwh)<=0)){this.msg('Vpiši datum, ponudnika/kategorijo in veljaven znesek; kWh so neobvezni.',true);return;}
    const body={date,kind,provider,gross_eur:gross,energy_kwh:kind==='PUBLIC'&&kwh?kwh:null,eligible:this.querySelector('#expense-eligible').checked,notes:this.querySelector('#expense-notes').value};
    const signature=JSON.stringify({...body,month:this.selectedMonth()});if(this._expenseSignature!==signature){this._expenseSignature=signature;this._expenseKey=crypto.randomUUID();}
    if(await this.saveRegister('register-expense',{...body,idempotency_key:this._expenseKey},'#save-expense')){for(const id of ['#expense-gross','#expense-kwh','#expense-notes'])this.querySelector(id).value='';this._expenseKey=null;this._expenseSignature=null;}
  }
  async saveReported(){
    if(!this.registerReady()){this.msg('Počakaj na podatke izbranega meseca.',true);return;}
    const amount=this.querySelector('#reported-amount').value;if(!amount||Number(amount)<0){this.msg('Vpiši dejansko sporočeni znesek.',true);return;}
    if(!confirm(`Shranim ${amount} € kot dejansko sporočeni znesek za ${this.selectedMonth()}? Email se ne bo poslal.`))return;
    const signature=this.selectedMonth()+'|'+amount;if(this._reportedSignature!==signature){this._reportedSignature=signature;this._reportedKey=crypto.randomUUID();}
    await this.saveRegister('register-reported',{amount_eur:amount,idempotency_key:this._reportedKey},'#save-reported');
  }
  async saveOdometer(){
    const km=this.querySelector('#odometer-value').value,date=this.querySelector('#odometer-date').value;
    if(!km||Number(km)<0||!date){this.msg('Vpiši števec in dejanski čas odčitka.',true);return;}
    await this.saveRegister('register-odometer',{odometer_km:Number(km),observed_at:new Date(date).toISOString(),source:'manual'},'#save-odometer');
  }
  async copyEmail(){try{await navigator.clipboard.writeText(this.querySelector('#email-text').value);this.msg('Besedilo kopirano; pošlji ga v svojem emailu.');}catch(e){this.querySelector('#email-text').select();this.msg('Označeno besedilo kopiraj ročno.');}}
}
if(!customElements.get("energy-ledger-panel")) customElements.define("energy-ledger-panel",EnergyLedgerPanel);
