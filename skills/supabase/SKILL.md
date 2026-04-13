---
name: supabase
description: Supabase for database, auth, storage, and realtime features. Use when user mentions "supabase", "supabase auth", "supabase storage", "supabase realtime", "supabase edge functions", "postgres with supabase", "row level security", "RLS", "supabase client", or building apps with Supabase as the backend.
---

# Supabase

## Setup

```bash
npm install -g supabase          # or: brew install supabase/tap/supabase
supabase init                    # initialize local project
supabase link --project-ref <id> # link to remote project

npm install @supabase/supabase-js  # JS/TS client
# pip install supabase             # Python client
```

Client initialization:

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_ANON_KEY!)

// Server-side with elevated privileges (bypasses RLS, never expose to client)
const supabaseAdmin = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!)
```

With generated types:

```typescript
import { Database } from './types/database'
const supabase = createClient<Database>(url, key)
```

## Database

```sql
create table public.posts (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  content text,
  user_id uuid references auth.users(id) on delete cascade not null,
  created_at timestamptz default now() not null
);
```

### Migrations and Types

```bash
supabase migration new create_posts_table   # create migration file
supabase db push                             # apply migrations to remote
supabase db pull                             # pull remote schema into migration
supabase db reset                            # reset local DB, rerun migrations
supabase gen types typescript --linked > src/types/database.ts  # generate types
```

Migration files live in `supabase/migrations/` with timestamped filenames.

## Row Level Security (RLS)

Always enable RLS on tables exposed to the client. Key functions: `auth.uid()` returns current user ID, `auth.jwt()` returns full JWT claims. `using` controls which existing rows are visible; `with check` controls which new/modified rows are allowed.

```sql
alter table public.posts enable row level security;

create policy "Public read access" on public.posts
  for select using (true);

create policy "Users can insert own posts" on public.posts
  for insert to authenticated
  with check (auth.uid() = user_id);

create policy "Users can update own posts" on public.posts
  for update to authenticated
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "Users can delete own posts" on public.posts
  for delete to authenticated
  using (auth.uid() = user_id);
```

## Authentication

```typescript
// Email/password sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com', password: 'secure-password',
})

// Email/password sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com', password: 'secure-password',
})

// OAuth (github, google, apple, discord, etc.)
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'github',
  options: { redirectTo: 'https://yourapp.com/auth/callback' },
})

// Magic link
const { data, error } = await supabase.auth.signInWithOtp({
  email: 'user@example.com',
  options: { emailRedirectTo: 'https://yourapp.com/welcome' },
})

// Phone OTP
const { data, error } = await supabase.auth.signInWithOtp({ phone: '+15551234567' })
const { data, error } = await supabase.auth.verifyOtp({
  phone: '+15551234567', token: '123456', type: 'sms',
})
```

### Auth Helpers

```typescript
const { data: { user } } = await supabase.auth.getUser()
const { data: { session } } = await supabase.auth.getSession()
await supabase.auth.signOut()

const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
  console.log(event, session)
})
subscription.unsubscribe()
```

## Storage

```typescript
// Create bucket (requires service role or appropriate policies)
await supabase.storage.createBucket('avatars', {
  public: false, fileSizeLimit: 1048576, allowedMimeTypes: ['image/png', 'image/jpeg'],
})

// Upload
await supabase.storage.from('avatars').upload('user1/avatar.png', file, {
  cacheControl: '3600', upsert: true,
})

// Download
const { data } = await supabase.storage.from('avatars').download('user1/avatar.png')

// Signed URL (temporary, private buckets)
const { data } = await supabase.storage.from('avatars').createSignedUrl('user1/avatar.png', 3600)

// Public URL (public buckets only)
const { data } = supabase.storage.from('avatars').getPublicUrl('user1/avatar.png')
```

Storage policies use the `storage.objects` table:

```sql
create policy "Users upload own avatars" on storage.objects
  for insert to authenticated
  with check (bucket_id = 'avatars' and (storage.foldername(name))[1] = auth.uid()::text);

create policy "Public avatar access" on storage.objects
  for select using (bucket_id = 'avatars');
```

## Realtime

Enable realtime for a table: `alter publication supabase_realtime add table public.posts;`

### Postgres Changes Subscription

```typescript
const channel = supabase.channel('posts-changes')
  .on('postgres_changes', { event: '*', schema: 'public', table: 'posts' },
    (payload) => console.log('Change:', payload))
  .subscribe()

// Filter by event type
supabase.channel('new-posts')
  .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'posts' },
    (payload) => console.log('New:', payload.new))
  .subscribe()

supabase.removeChannel(channel) // unsubscribe
```

### Presence

```typescript
const channel = supabase.channel('room-1')
channel
  .on('presence', { event: 'sync' }, () => console.log(channel.presenceState()))
  .on('presence', { event: 'join' }, ({ key, newPresences }) => console.log('Joined:', newPresences))
  .on('presence', { event: 'leave' }, ({ key, leftPresences }) => console.log('Left:', leftPresences))
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') {
      await channel.track({ user_id: 'user-1', online_at: new Date().toISOString() })
    }
  })
```

### Broadcast

```typescript
const channel = supabase.channel('room-1')
channel.on('broadcast', { event: 'cursor-pos' }, (payload) => console.log(payload)).subscribe()
channel.send({ type: 'broadcast', event: 'cursor-pos', payload: { x: 100, y: 200 } })
```

## Edge Functions

Deno-based server-side TypeScript functions.

```bash
supabase functions new my-function      # create
supabase functions serve my-function    # local dev
supabase functions deploy my-function   # deploy
supabase secrets set MY_API_KEY=value   # set secret
supabase secrets list                   # list secrets
```

```typescript
// supabase/functions/my-function/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_ANON_KEY')!,
    { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
  )
  const { data } = await supabase.from('posts').select('*')
  return new Response(JSON.stringify(data), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  })
})
```

Invoke from client:

```typescript
const { data, error } = await supabase.functions.invoke('my-function', { body: { name: 'world' } })
```

## Client Library Queries

Supabase auto-generates a PostgREST API from your schema. The client library wraps it.

```typescript
// Select
const { data } = await supabase.from('posts').select('*')
const { data } = await supabase.from('posts').select('id, title')
const { data } = await supabase.from('posts').select('id, title, comments(id, body)')  // join
const { count } = await supabase.from('posts').select('*', { count: 'exact', head: true })

// Insert
const { data } = await supabase.from('posts')
  .insert({ title: 'Hello', content: 'World', user_id: userId }).select()
const { data } = await supabase.from('posts')
  .insert([{ title: 'A', user_id: userId }, { title: 'B', user_id: userId }]).select()

// Update
const { data } = await supabase.from('posts')
  .update({ title: 'New Title' }).eq('id', postId).select()

// Delete
await supabase.from('posts').delete().eq('id', postId)

// Filters
const { data } = await supabase.from('posts').select('*')
  .eq('user_id', userId)        // equals
  .neq('status', 'draft')       // not equals
  .gt('views', 100)             // greater than
  .lt('views', 1000)            // less than
  .like('title', '%hello%')     // case-sensitive pattern
  .ilike('title', '%hello%')    // case-insensitive pattern
  .in('status', ['published', 'archived'])
  .is('deleted_at', null)       // null check
  .order('created_at', { ascending: false })
  .range(0, 9)                  // pagination (first 10)
  .limit(10)
  .single()                     // expect exactly one row
```

## Database Functions and RPC

```sql
create or replace function get_posts_by_author(author_id uuid)
returns setof posts language sql security definer as $$
  select * from posts where user_id = author_id order by created_at desc;
$$;
```

```typescript
const { data } = await supabase.rpc('get_posts_by_author', { author_id: userId })
```

`security definer` bypasses RLS. `security invoker` (default) respects caller RLS policies.

## CLI Reference

```bash
supabase start           # start local stack (Postgres, Auth, Storage, Studio)
supabase stop            # stop local stack
supabase status          # show local URLs and keys
supabase db push         # apply migrations to remote
supabase db pull         # pull remote schema
supabase db reset        # reset local DB
supabase db lint         # lint SQL
supabase db diff         # diff local vs remote
supabase migration new <name>
supabase migration list
supabase gen types typescript --linked > types/database.ts
supabase functions new <name>
supabase functions serve
supabase functions deploy <name>
supabase secrets set KEY=value
supabase secrets list
```

## Local Development

`supabase start` launches the full stack. Studio runs at `http://localhost:54323`. Use local keys in `.env.local`:

```
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<anon-key-from-supabase-start>
```

## Common Patterns

### User Profiles with Auto-Create Trigger

```sql
create table public.profiles (
  id uuid references auth.users(id) on delete cascade primary key,
  display_name text, avatar_url text, updated_at timestamptz default now()
);
alter table public.profiles enable row level security;

create policy "Public read" on public.profiles for select using (true);
create policy "Own update" on public.profiles for update to authenticated using (auth.uid() = id);

create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, new.raw_user_meta_data ->> 'full_name');
  return new;
end;
$$;

create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();
```

### File Uploads with Auth

```typescript
async function uploadAvatar(userId: string, file: File) {
  const path = `${userId}/${Date.now()}-${file.name}`
  const { error } = await supabase.storage.from('avatars').upload(path, file, { upsert: true })
  if (error) throw error
  const { data } = supabase.storage.from('avatars').getPublicUrl(path)
  await supabase.from('profiles').update({ avatar_url: data.publicUrl }).eq('id', userId)
  return data.publicUrl
}
```

### Realtime Chat

```typescript
async function sendMessage(channelId: string, content: string) {
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')
  return supabase.from('messages').insert({ channel_id: channelId, content, user_id: user.id })
}

function subscribeToMessages(channelId: string, onMessage: (msg: any) => void) {
  return supabase.channel(`messages:${channelId}`)
    .on('postgres_changes', {
      event: 'INSERT', schema: 'public', table: 'messages',
      filter: `channel_id=eq.${channelId}`,
    }, (payload) => onMessage(payload.new))
    .subscribe()
}
```
