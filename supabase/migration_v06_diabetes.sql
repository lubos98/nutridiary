alter table public.profiles add column if not exists sj_grams numeric not null default 10 check (sj_grams between 1 and 100);
create table if not exists public.glucose_logs (id uuid primary key default gen_random_uuid(),user_id uuid not null references auth.users(id) on delete cascade,measured_at timestamptz not null,mmol_l numeric(4,1) not null check (mmol_l between 1 and 40),context text not null check(context in ('before_meal','after_meal','bedtime','other')),note text not null default '',created_at timestamptz not null default now());
create index if not exists glucose_logs_user_time_idx on public.glucose_logs(user_id,measured_at desc);
alter table public.glucose_logs enable row level security;
drop policy if exists "glucose logs own" on public.glucose_logs;
create policy "glucose logs own" on public.glucose_logs for all to authenticated using(user_id=auth.uid()) with check(user_id=auth.uid());
