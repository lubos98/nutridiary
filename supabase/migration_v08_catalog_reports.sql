-- v08: user reports of questionable catalog nutrition data
create table if not exists public.food_catalog_reports (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade,
 barcode text not null references public.food_catalog(barcode) on delete cascade,
 note text not null check (char_length(trim(note)) between 5 and 1000),
 status text not null default 'new' check(status in ('new','reviewed','resolved')),
 created_at timestamptz not null default now(),
 unique(user_id,barcode)
);
create index if not exists food_catalog_reports_status_idx on public.food_catalog_reports(status,created_at desc);
alter table public.food_catalog_reports enable row level security;
drop policy if exists "users can read own food reports" on public.food_catalog_reports;
drop policy if exists "users can submit food reports" on public.food_catalog_reports;
create policy "users can read own food reports" on public.food_catalog_reports for select to authenticated using(user_id=auth.uid());
create policy "users can submit food reports" on public.food_catalog_reports for insert to authenticated with check(user_id=auth.uid() and status='new');
-- No public access to other users' reports and no user editing of moderation status.
