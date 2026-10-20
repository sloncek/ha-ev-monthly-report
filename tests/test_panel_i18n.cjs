const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {parseHTML}=require('linkedom');
const source=fs.readFileSync('custom_components/energy_ledger/www/energy_ledger_panel.js','utf8');
const prefs=(language,extra={})=>({locale:{language,...extra},config:{time_zone:'Europe/Ljubljana'},states:{'select.energy_ledger_report_month':{state:'2026-09',attributes:{options:['2026-09']}}}});
function panel(language='en',extra={}){
 const {window}=parseHTML('<html><body></body></html>');
 // The old dashboard resource must not prevent the native panel from loading.
 window.customElements.define('energy-ledger-panel',class extends window.HTMLElement{});
 const context=vm.createContext({HTMLElement:window.HTMLElement,customElements:window.customElements,document:window.document,Intl,Date,console});
 vm.runInContext(source,context);
 const el=window.document.createElement('energy-ledger-native-panel');
 el.panel={config:{vehicle_name:'Test EV'}};
 el.hass=prefs(language,extra);
 return el;
}
const record={month:'2026-09',status:'DRAFT',home_kwh:'1234.5',reimbursement_rate:'0.22',home_reimbursement_eur:'271.59',eligible_expenses_eur:'10.00',opening_balance_eur:'0.00',requested_eur:'281.59',reported_eur:'0.00',energy_complete:true,ready_to_report:true,odometer_km:'12345',monthly_distance_km:'1234',expenses:[]};
test('static labels, accessibility and formatting follow the HA user language',()=>{
 const en=panel('en-US'),sl=panel('sl-SI');
 assert.equal(en.querySelector('#vehicle-heading').textContent,'Test EV · monthly ledger');
 assert.equal(sl.querySelector('#vehicle-heading').textContent,'Test EV · mesečna preglednica');
 assert.equal(en.querySelector('#forecast-tab').textContent,'Mileage forecast');
 assert.equal(sl.querySelector('#forecast-tab').textContent,'Napoved kilometrov');
 assert.equal(sl.querySelector('#register-month').getAttribute('aria-label'),'Mesec poročila');
 assert.equal(en.formatCell(1234.5,'home_kwh'),'1,234.500');
 assert.equal(sl.formatCell(12345.5,'home_kwh'),'12.345,500');
 assert.equal(sl.querySelector('#expense-kind option').textContent,'Javno polnjenje');
});
test('unsupported languages and absent locale fall back to English',()=>{
 const de=panel('de-DE');assert.equal(de.querySelector('#forecast-tab').textContent,'Mileage forecast');
 assert.equal(de.formatCell(1234.5,'home_kwh'),'1.234,500');
 de.hass={states:{}};assert.equal(de.querySelector('#forecast-tab').textContent,'Mileage forecast');
 assert.equal(de.t('PDF je sprejet; čakam na branje in preverjanje računa.'),'PDF received; waiting to parse and validate the invoice.');
});
test('live language changes preserve unfinished forms, attachments, selected month and view',()=>{
 const p=panel();p._registerData=record;p.showRegister(record);p.showHistory([record]);p.setMode('forecast');
 const provider=p.querySelector('#expense-provider'),file=p.querySelector('#invoice');
 const attachment={name:'private.pdf'};Object.defineProperty(file,'files',{value:[attachment]});
 provider.value='Unfinished provider';p.querySelector('#expense-gross').value='12.34';p.querySelector('#expense-editor').open=true;
 const range=p.querySelector('#forecast-range');range.querySelector('[value=all]').selected=true;
 p.hass=prefs('sl');
 assert.equal(p.querySelector('#expense-provider'),provider);
 assert.equal(provider.value,'Unfinished provider');assert.equal(p.querySelector('#expense-gross').value,'12.34');
 assert.equal(p.querySelector('#invoice'),file);assert.equal(file.files[0],attachment);
 assert.equal(p.querySelector('#expense-editor').open,true);assert.equal(p.querySelector('#forecast-range'),range);assert.equal(range.value,'all');
 assert.equal(p.selectedMonth(),'2026-09');assert.equal(p.querySelector('#mileage').hidden,false);
 assert.match(p.querySelector('#month-heading').textContent,/vnos manjkajočih podatkov/);
 assert.match(p.querySelector('#email-text').value,/Polnjenje službenega vozila/);
 p.hass=prefs('en');assert.match(p.querySelector('#email-text').value,/Company vehicle/);
 assert.match(p.querySelector('#month-heading').textContent,/enter missing data/);
 assert.equal(provider.value,'Unfinished provider');
});
test('backend import progress is translated without changing durable state',()=>{
 const p=panel();const progress={step:4,level:'success',terminal:true,label:'Račun je obdelan in primerjava z Moj Elektro je zaključena.'};
 p.showProgress(progress,{job_id:'1234567890',year_month:'2026-09'});
 assert.equal(p.querySelector('#import-label').textContent,'Invoice processed and Moj Elektro comparison complete.');
 p.hass=prefs('sl');assert.equal(p.querySelector('#import-label').textContent,progress.label);
 assert.equal(progress.label,'Račun je obdelan in primerjava z Moj Elektro je zaključena.');
});
test('number, date, time and timezone preferences override language defaults',()=>{
 const p=panel('en',{number_format:'decimal_comma',date_format:'DMY',time_format:'24',time_zone:'server'});
 assert.equal(p.formatCell(1234.5,'home_kwh'),'1.234,500');
 assert.match(p.formatDateTime('2026-10-20T13:05:00Z'),/20\/10\/2026.*15:05/);
 p.hass=prefs('sl',{number_format:'none'});assert.equal(p.formatCell(1234.5,'home_kwh'),'1234.500');
 p.hass=prefs('sl',{number_format:'comma_decimal'});assert.equal(p.formatCell(1234.5,'home_kwh'),'1,234.500');
});
test('every static label and message placeholder has a matching Slovenian translation',()=>{
 const p=panel();
 const context={HTMLElement:class{},customElements:{get:()=>true}};vm.runInNewContext(source+';globalThis.catalog=PANEL_TRANSLATIONS.sl;',context);
 for(const node of p.querySelectorAll('[data-i18n], [data-i18n-aria-label]')){const key=node.getAttribute('data-i18n')||node.getAttribute('data-i18n-aria-label');assert.ok(Object.hasOwn(context.catalog,key),key);}
 vm.runInNewContext(source+'\nfor(const [en,sl] of Object.entries(PANEL_TRANSLATIONS.sl)){const slots=s=>[...s.matchAll(/\\{(\\d+)\\}/g)].map(x=>x[1]).sort().join();if(slots(en)!==slots(sl))throw Error(en);}',{HTMLElement:class{},customElements:{get:()=>true}});
});
