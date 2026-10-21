-- v09: voluntary hydration tracking, independent of nutrition calculations
create table if not exists public.water_entries (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 date date not null,
 ml integer not null check(ml between 1 and 10000),
 created_at timestamptz not null default now()
);
create index if not exists water_entries_user_date_idx on public.water_entries(user_id,date);
alter table public.water_entries enable row level security;
drop policy if exists "water entries own select" on public.water_entries;
drop policy if exists "water entries own insert" on public.water_entries;
drop policy if exists "water entries own delete" on public.water_entries;
create policy "water entries own select" on public.water_entries for select to authenticated using(user_id=auth.uid());
create policy "water entries own insert" on public.water_entries for insert to authenticated with check(user_id=auth.uid());
create policy "water entries own delete" on public.water_entries for delete to authenticated using(user_id=auth.uid());
