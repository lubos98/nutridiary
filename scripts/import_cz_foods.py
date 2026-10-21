#!/usr/bin/env python3
"""Import Czech-market foods from an Open Food Facts TSV/CSV dump to Supabase.

Usage:
  SUPABASE_URL=https://... SUPABASE_SERVICE_ROLE_KEY=... python3 scripts/import_cz_foods.py /path/to/en.openfoodfacts.org.products.csv.gz

Download an Open Food Facts product export from https://world.openfoodfacts.org/data
Never put the service-role key into the web app or GitHub.
"""
import csv, gzip, json, os, sys, time, urllib.request, urllib.error
# Open Food Facts exports contain exceptionally long ingredient/metadata fields.
csv.field_size_limit(10 * 1024 * 1024)
from urllib.parse import urlsplit

def normalize_url(raw):
    raw = raw.strip().strip('"').strip("'").rstrip("/")
    parsed = urlsplit(raw)
    if parsed.scheme != "https" or not parsed.hostname:
        raise SystemExit("SUPABASE_URL must be the HTTPS Project URL (https://<project-ref>.supabase.co).")
    if not (parsed.hostname.endswith(".supabase.co") or parsed.hostname.endswith(".supabase.in")):
        raise SystemExit("SUPABASE_URL is not a Supabase project URL. Use Project Settings > API > Project URL, not the dashboard URL.")
    if parsed.path not in ("", "/", "/rest/v1"):
        raise SystemExit("SUPABASE_URL contains an unsupported path. Use the Project URL without /rest/v1.")
    return parsed.scheme + "://" + parsed.netloc

URL = normalize_url(os.environ.get("SUPABASE_URL", ""))
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
BATCH = 250
CZ_TAGS = {"en:czech-republic", "cs:cesko", "cs:ceska-republika"}
FIELDS = ("energy-kcal_100g", "proteins_100g", "carbohydrates_100g", "fat_100g")

def num(value):
    try:
        n = float(str(value).strip())
        return round(n, 2) if 0 <= n < 100000 else None
    except (ValueError, TypeError):
        return None

def open_data(path):
    return gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") if path.endswith(".gz") else open(path, "r", encoding="utf-8", errors="replace", newline="")

def check_catalog():
    req = urllib.request.Request(URL + "/rest/v1/food_catalog?select=barcode&limit=1", headers={
        "apikey": KEY, "Authorization": "Bearer " + KEY, "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            response.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:350]
        raise SystemExit(f"Cannot access food_catalog (HTTP {e.code}): {detail}. Check SUPABASE_URL, migration v07 and the API key.") from e
    print("Supabase food_catalog connection verified.", flush=True)

def upload(rows):
    body = json.dumps(rows, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(URL + "/rest/v1/food_catalog?on_conflict=barcode", body, {
        "apikey": KEY, "Authorization": "Bearer " + KEY,
        "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"
    }, method="POST")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                response.read()
            return
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:300]
            if e.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise RuntimeError(f"Supabase HTTP {e.code}: {detail}") from e
            time.sleep(2 ** attempt)

def main(path):
    if not URL or not KEY:
        raise SystemExit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your terminal.")
    check_catalog()
    seen = set()
    batch = []
    processed = imported = 0
    with open_data(path) as f:
        reader = csv.DictReader(f, delimiter="\t" if ".tsv" in path or ".csv" in path else ",")
        for row in reader:
            processed += 1
            tags = set((row.get("countries_tags") or "").lower().split(","))
            if not tags.intersection(CZ_TAGS):
                continue
            barcode = (row.get("code") or "").strip()
            name = (row.get("product_name_cs") or row.get("product_name") or "").strip()
            if not barcode.isdigit() or not name or barcode in seen:
                continue
            seen.add(barcode)
            vals = [num(row.get(field)) for field in FIELDS]
            if vals[0] is None:
                kj = num(row.get("energy-kj_100g"))
                if kj is not None:
                    vals[0] = round(kj / 4.184, 2)
            if any(v is None for v in vals):
                continue  # Only verified complete macro records enter the catalog.
            batch.append(dict(barcode=barcode, name=name[:300], brand=(row.get("brands") or "")[:300],
                              kcal=vals[0], protein=vals[1], carbs=vals[2], fat=vals[3],
                              country="CZ", source="openfoodfacts"))
            if len(batch) >= BATCH:
                upload(batch)
                imported += len(batch)
                batch.clear()
                if imported % 5000 == 0:
                    print(f"Imported {imported} products; scanned {processed} rows", flush=True)
    if batch:
        upload(batch)
        imported += len(batch)
    print(f"Done. Scanned {processed} rows; imported {imported} Czech-market products.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 scripts/import_cz_foods.py <OpenFoodFacts CSV/TSV[.gz]>")
    main(sys.argv[1])
