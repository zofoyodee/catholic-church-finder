-- Catholic Church Finder: saved favorites for signed-in users.
-- Run once in Supabase: SQL Editor > New query > paste > Run.

create table if not exists public.favorites (
  user_id    uuid        not null default auth.uid() references auth.users (id) on delete cascade,
  church     integer     not null check (church >= 0),
  name       text        not null default '' check (char_length(name) <= 300),
  place      text        not null default '' check (char_length(place) <= 300),
  t          smallint,
  created_at timestamptz not null default now(),
  primary key (user_id, church)
);

-- Each person can only see and change their own favorites.
alter table public.favorites enable row level security;

drop policy if exists "Read own favorites" on public.favorites;
create policy "Read own favorites" on public.favorites
  for select to authenticated using ((select auth.uid()) = user_id);

drop policy if exists "Add own favorites" on public.favorites;
create policy "Add own favorites" on public.favorites
  for insert to authenticated with check ((select auth.uid()) = user_id);

drop policy if exists "Update own favorites" on public.favorites;
create policy "Update own favorites" on public.favorites
  for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);

drop policy if exists "Remove own favorites" on public.favorites;
create policy "Remove own favorites" on public.favorites
  for delete to authenticated using ((select auth.uid()) = user_id);
