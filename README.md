# NutriDeník PWA 0.4

## Změny ve verzi 0.4
- Vytváření vlastní potraviny (nutriční hodnoty na 100 g) a okamžité pokračování k zadání gramáže a uložení do deníku.
- Editace pouze vlastních potravin; ostatní potraviny lze zkopírovat do soukromé varianty.
- Filtrování „Jen moje potraviny“, vyhledávání podle názvu/EAN a odstranění vlastního produktu.
- Základní validace a upozornění na duplicitní vlastní název + EAN.
- Nenalezený EAN otevře formulář nové potraviny s předvyplněným kódem.
- Staré deníkové záznamy uchovávají snapshot nutričních hodnot.

## Spuštění
1. `npm install`
2. V Supabase vytvořte projekt a spusťte `supabase/schema.sql` v SQL editoru. Pokud jste schéma z v0.3 už aplikovali, **nespouštějte jej znovu** (obsahuje CREATE POLICY bez IF NOT EXISTS).
3. V Supabase Authentication > Providers aktivujte Google a nakonfigurujte Google Cloud OAuth. Redirect callback je uveden v Supabase (obvykle `https://<project>.supabase.co/auth/v1/callback`).
4. Do Supabase Authentication > URL Configuration přidejte lokální a produkční redirect URL.
5. `cp .env.example .env` a vyplňte `VITE_SUPABASE_URL` a `VITE_SUPABASE_ANON_KEY` (veřejný publishable/anon klíč; nikdy service_role).
6. `npm run dev` pro vývoj nebo `npm run build` pro sestavení.
7. Pro PWA nasaďte na HTTPS (např. Vercel), otestujte instalaci v Safari/Chrome.

## Omezení
- Bez Supabase běží jen demo v paměti prohlížeče; obnovení stránky data smaže.
- Přímý skener EAN využívá BarcodeDetector, který není podporován ve všech prohlížečích. Ruční EAN funguje.
- Open Food Facts nemusí mít úplné ani správné údaje; uživatel je má zkontrolovat.
- Vyhledávání externích produktů podle názvu zatím není integrováno; podle názvu se hledá v lokálním katalogu.
- Veřejná moderovaná databáze, offline zápis a AI OCR fotografií nejsou součástí verze 0.4.
- Pro produkční nasazení je nutné ověřit OAuth, RLS, ochranu dat a testování na reálných zařízeních.
