# Energy Ledger – mesečno poročilo za domače polnjenje EV

Ta paket pripravi mesečno poročilo o domači porabi za polnjenje, stroških oziroma povračilu ter kilometrini. Namenjen je samostojni namestitvi v Home Assistantu z ločenim API/parserjem. Priložen je primer za Audi e-tron, vendar integracija ne predpostavlja znamke: izbrati morate svoje entitete števca kilometrov in energije.

## Kaj je v paketu

- `energy_ledger/`: API, obdelava računov in izračun mesečnega registra.
- `custom_components/energy_ledger/`: integracija HA, senzorji in konfiguracijski obrazec.
- `www/energy_ledger_panel.js`: stranska plošča z mesečnim poročilom.
- `migrations/`: shema lokalne zbirke podatkov.
- `compose.yaml`: API in izoliran parser.
- `config/config.example.json`: očiščen primer konfiguracije brez dejanskih računov, zgodovine ali skrivnosti.

## Zahteve

- Home Assistant z omogočenim Recorderjem in Docker Compose v2 na istem Docker gostitelju.
- HA in storitev API morata komunicirati prek istega Docker omrežja. Sestava privzeto ne objavi API porta na gostitelju.
- V HA mora obstajati entiteta števca kilometrov za vozilo ter statistika energije za domači polnilnik. Vir je lahko Audi e-tron integracija ali drug senzor; konkretna integracija vozila ni priložena.
- Za poročila o stroških morate sami določiti tarifo, upravičenost stroškov, obdobje veljavnosti in pravila povračila.

## Namestitev z Docker Compose

1. Kopirajte ta projekt na gostitelja Home Assistanta in odprite njegovo mapo. Ustvarite lokalni delovni imenik:

   ```sh
   cp config/config.example.json config/config.json
   cp .env.example .env
   mkdir -p data/inbox data/outbox
   ```

2. Ugotovite Docker omrežje, na katerem je HA. Uporabite `docker network ls` in `docker inspect <ime-kontejnerja-ha>`; v `.env` nastavite `HA_DOCKER_NETWORK` na dejansko ime omrežja. Poskrbite, da je HA priključen nanj. Sestava uporablja DNS ime `energy-ledger-api`, zato iz HA vnesite ta naslov:

   ```text
   http://energy-ledger-api:8099
   ```

   Če HA teče v načinu `network_mode: host`, ne uporablja Docker DNS omrežja. V tem primeru prilagodite Compose omrežje API-ja na `host` in uporabite `http://127.0.0.1:8099`; ne kombinirajte `network_mode: host` in zunanjega omrežja. Če sta HA in API na različnih gostiteljih, uredite zaseben šifriran dostop (npr. povratni proxy z TLS) in ne odpirajte API-ja javnemu internetu.

3. Ustvarite tri skrivnosti. Te datoteke ostanejo samo na vaši napravi:

   ```sh
   umask 077
   openssl rand -hex 32 > secrets/read_token
   openssl rand -hex 32 > secrets/write_token
   openssl rand -hex 32 > secrets/ha_signing_secret
   ```

   Kontejnerji tečejo kot UID/GID `10001:10001`. Po ustvarjanju skrivnosti nastavite lastništvo in pravice, da API lahko bere datoteke, ne da bi jih izpostavil drugim uporabnikom:

   ```sh
   sudo chown -R 10001:10001 data secrets
   sudo chmod 700 data secrets
   sudo chmod 600 secrets/read_token secrets/write_token secrets/ha_signing_secret
   ```

   Če izbrani NAS uporablja drugačen model pravic, nastavite ustrezen ACL za UID/GID 10001. Za konfiguracijo integracije boste pozneje uporabili vsebino skrivnosti; vrednosti ne objavljajte v repozitoriju ali posnetkih zaslona.

4. Uredite `config/config.json` (glejte razdelek **Ročne nastavitve**). `timezone` v tej datoteki in časovni pas, ki ga vnesete v obrazec integracije HA, morata biti enaka. API uporablja prvi za mesečne registre, integracija pa drugega za odčitke Recorderja in števca. `vehicle_name` v backend konfiguraciji naj se ujema s prikaznim imenom v obrazcu HA. Nato zaženite:

   ```sh
   docker compose build
   docker compose up -d
   docker compose logs -f api
   ```

   `data/` vsebuje lokalno zbirko in uvožene podatke. Vključite jo v lastno varnostno kopijo in omejite dostop do nje.

## Namestitev v Home Assistant

1. Kopirajte mapo `custom_components/energy_ledger` v `/config/custom_components/energy_ledger`.
2. Kopirajte `www/energy_ledger_panel.js` v `/config/www/energy_ledger_panel.js`.
3. Znova zaženite Home Assistant. V **Nastavitve → Naprave in storitve → Dodaj integracijo** poiščite **Energy Ledger**.
4. Vnesite URL API-ja iz prejšnjega razdelka, ime vozila, časovni pas, ID entitete števca kilometrov, ID statistike energije in tri ustrezne skrivnosti. Časovni pas naj bo veljaven IANA zapis, na primer `Europe/Ljubljana`, in naj se ujema z `timezone` v `config/config.json`.
5. Po namestitvi se poročilo prikaže v stranski plošči Home Assistanta. Če se panel ali entitete ne pokažejo, preverite dnevnike HA in API ter ali lahko HA razreši `energy-ledger-api`.

### Ročne nastavitve in povezava Audi e-tron

Konfiguracijski obrazec HA pričakuje ID-je entitet, ne imen naprav. Primeri (zamenjajte z dejanskimi ID-ji iz **Orodja za razvijalce → Stanja**):

- števec kilometrov: na primer `sensor.audi_e_tron_odometer`;
- energija domačega polnilnika: na primer Recorder statistika `sensor.wallbox_energy_total`.

Statistika energije mora predstavljati porabo **vozila na domačem polnilniku**, izraženo v kWh, imeti zgodovinske urne statistike in biti pravilno nastavljena kot `total` ali `total_increasing`. Skupna poraba hiše ni ustrezen približek, razen če jo namensko razdelite na polnjenje EV. Ustrezno Audi integracijo oziroma polnilnik namestite in nastavite sami; ta paket ne kliče Audi oblaka in ne vključuje poverilnic.

Za pravilno kilometrino mora biti odčitek na voljo ob koncu meseca. Integracija shrani mesečni odčitek, ko je entiteta posodobljena zadnji koledarski dan v izbranem časovnem pasu. Če se senzor takrat ne posodobi, vnesite manjkajoči mesečni odčitek v obrazcu za register, če je na voljo, ali zagotovite avtomatizacijo, ki senzor osveži zadnji dan meseca. Brez treh zaporednih mesečnih razdalj napoved ni prikazana.

### Nastavitve za kilometrino

Privzeto ni načrta kilometrov. Po potrebi sami dodajte v `config/config.json`:

```json
"mileage_plan": {
  "allowance_km": 20000,
  "contract_end_month": "2030-12"
}
```

To sta zgolj označeni zgledni vrednosti: pred uporabo ju zamenjajte s svojim dovoljenim obsegom in končnim mesecem ali pustite `mileage_plan` nastavljen na `null`. Napoved se izračuna samo iz mesečnih odčitkov posamezne namestitve. Po spremembi konfiguracije ponovno zaženite API.

## Stroški, povračilo in računi

Tarife in finančna pravila so odvisna od delodajalca, pogodbe, države in obračunskega obdobja, zato v paketu ni privzete tarife ali stopnje DDV. Ročno vnesite tarifo in datume veljavnosti v poročilo/registrski obrazec. Preverite, ali je znesek bruto ali neto, kako se zaokrožuje, kateri strošek je upravičen in ali potrebujete račun. Rezultat je evidenca za pregled, ne davčni ali računovodski nasvet.

Računovodska uvozna pot je neobvezna. Trenutni parser podpira omejen format računov dobavitelja GEN-I; računov, predlog ali osebnih podatkov ni vključenih. Uvozite samo svoje dokumente in preverite razčlenjene zneske pred uporabo. Integracija Moj Elektro je prav tako neobvezna in privzeto izklopljena; za uporabo sami nastavite veljaven `usage_point`, pridobite lasten API žeton in dodajte varno mount točke skrivnosti v Compose. Osebni merilni priključek ali žeton nista priložena.

## Omejitve in predpostavke

- To je očiščen začetni paket, ne že preverjen obračun za specifično podjetje ali Audi namestitev.
- Poročilo uporablja samo podatke, ki jih vnese posamezna namestitev. Prazne oziroma neustrezne HA entitete ne bodo dale uporabnega poročila.
- Napoved kilometrov potrebuje zaporedne mesečne odčitke. Ne zapolnjuje manjkajoče zgodovine s podatki iz drugega vozila.
- Samodejni odčitek števca se shrani le ob koncu koledarskega meseca, ko se entiteta posodobi; zagotovite posodobitev ali ročni vnos.
- Domača energija mora biti ločena za EV. Paket ne more določiti, kateri del skupne hišne porabe je polnjenje.
- Stroški in povračila so odvisni od ročnih tarif in pravil; preverite jih pred oddajo zahtevka.
- Parser računov ni univerzalen; ni priloženih vhodnih računov ali vzorčnih izpisov z osebnimi podatki.
- Compose ohranja način `SHADOW`; ne vklopite zunanjih zapisovalnih operacij, dokler ne razumete posledic.

## Preverjanje paketa

Ob pripravi so na voljo preverjanje sintakse JavaScripta z Node.js ter pregled JSON datotek. Python/pytest in Docker v okolju priprave nista bila na voljo, zato Python testov, gradnje slike ali zagona Compose ni mogoče potrditi. Pred uporabo izvedite lokalno gradnjo in teste:

```sh
python -m pytest
docker compose config
docker compose build
```
