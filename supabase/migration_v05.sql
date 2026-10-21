-- NutriDeník v0.5: run once in Supabase SQL Editor.
alter table public.profiles add column if not exists protein_goal integer not null default 160;
alter table public.profiles add column if not exists carbs_goal integer not null default 250;
alter table public.profiles add column if not exists fat_goal integer not null default 80;
create table if not exists public.favorite_foods (
 user_id uuid not null references auth.users(id) on delete cascade,
 food_key text not null,
 food_name text not null,
 kcal numeric not null check(kcal>=0),
 protein numeric not null check(protein>=0),
 carbs numeric not null check(carbs>=0),
 fat numeric not null check(fat>=0),
 barcode text,
 primary key(user_id,food_key)
);
create table if not exists public.recipes (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 name text not null check(length(trim(name))>0),
 portions integer not null check(portions between 1 and 100),
 ingredients jsonb not null default '[]'::jsonb,
 created_at timestamptz not null default now()
);
alter table public.favorite_foods enable row level security;
alter table public.recipes enable row level security;
drop policy if exists "favorite foods own" on public.favorite_foods;
create policy "favorite foods own" on public.favorite_foods for all to authenticated using(user_id=auth.uid()) with check(user_id=auth.uid());
drop policy if exists "recipes own" on public.recipes;
create policy "recipes own" on public.recipes for all to authenticated using(user_id=auth.uid()) with check(user_id=auth.uid());
