create table
  public.potions (
    sku text not null,
    name text not null default 'NULL'::text,
    inventory integer null default 0,
    price integer null default 50,
    num_red_ml integer null,
    num_green_ml integer null,
    num_blue_ml integer null,
    num_dark_ml integer null,
    constraint potions_pkey primary key (sku)
  ) tablespace pg_default;

create table
  public.account (
    account_id bigint generated by default as identity,
    name text not null,
    constraint account_pkey primary key (account_id)
  ) tablespace pg_default;

create table
  public.account_gold_ledger_entries (
    id bigint generated by default as identity,
    account_id bigint not null,
    account_transaction_id bigint null,
    gold_change bigint null,
    constraint account_ledger_entries_pkey primary key (id),
    constraint account_gold_ledger_entries_account_id_fkey foreign key (account_id) references account (account_id),
    constraint account_gold_ledger_entries_account_transaction_id_fkey foreign key (account_transaction_id) references account_transactions (id)
  ) tablespace pg_default;

create table
  public.account_ml_ledger_entries (
    id bigint generated by default as identity,
    account_id bigint not null,
    account_transaction_id bigint null,
    red_ml_change bigint null,
    green_ml_change integer null,
    blue_ml_change integer null,
    dark_ml_change integer null,
    constraint account_ml_ledger_entries_pkey primary key (id),
    constraint account_ml_ledger_entries_account_id_fkey foreign key (account_id) references account (account_id),
    constraint account_ml_ledger_entries_account_transaction_id_fkey foreign key (account_transaction_id) references account_transactions (id)
  ) tablespace pg_default;

  create table
  public.account_potion_ledger_entries (
    id bigint generated by default as identity,
    account_id bigint not null,
    account_transaction_id bigint null,
    potion_change bigint null,
    potion_type text null,
    constraint account_potion_ledger_entries_duplicate_pkey primary key (id),
    constraint account_potion_ledger_entries_account_id_fkey foreign key (account_id) references account (account_id),
    constraint account_potion_ledger_entries_account_transaction_id_fkey foreign key (account_transaction_id) references account_transactions (id)
  ) tablespace pg_default;

create table
  public.account_transactions (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    description text null,
    constraint account_transactions_pkey primary key (id)
  ) tablespace pg_default;  

create table
  public.cart_item (
    cart_id integer generated by default as identity,
    potion_sku text not null,
    quantity integer null,
    constraint cart_item_pkey primary key (cart_id),
    constraint cart_item_potion_sku_fkey foreign key (potion_sku) references potions (sku)
  ) tablespace pg_default;

  create table
  public.cart (
    cart_id integer generated by default as identity,
    name text not null,
    total_cost integer null,
    num_potions integer null,
    constraint cart_pkey primary key (cart_id),
    constraint cart_cart_id_fkey foreign key (cart_id) references cart_item (cart_id)
  ) tablespace pg_default;