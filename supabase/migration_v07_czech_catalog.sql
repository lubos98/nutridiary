-- NutriDenik: shared Czech food catalog (run in Supabase SQL editor)
create extension if not exists pg_trgm;
create table if not exists public.food_catalog (
  barcode text primary key,
  name text not null,
  brand text not null default '',
  kcal numeric(9,2),
  protein numeric(9,2),
  carbs numeric(9,2),
  fat numeric(9,2),
  source text not null default 'openfoodfacts',
  country text not null default 'CZ' check (country='CZ'),
  updated_at timestamptz not null default now(),
  constraint catalog_nutrients_nonnegative check (
    (kcal is null or kcal>=0) and (protein is null or protein>=0)
    and (carbs is null or carbs>=0) and (fat is null or fat>=0)
  )
);
create index if not exists food_catalog_name_trgm on public.food_catalog using gin (name gin_trgm_ops);
create index if not exists food_catalog_brand_trgm on public.food_catalog using gin (brand gin_trgm_ops);
create index if not exists food_catalog_updated_idx on public.food_catalog(updated_at desc);
alter table public.food_catalog enable row level security;
drop policy if exists "catalog readable by authenticated users" on public.food_catalog;
create policy "catalog readable by authenticated users" on public.food_catalog for select to authenticated using (true);
-- No browser insert/update/delete permissions. Imports use service-role key server-side only.
