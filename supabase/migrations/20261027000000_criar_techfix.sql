-- Clientes
create table public.clientes (
    id bigint generated always as identity primary key,
    nome text not null check (length(trim(nome)) > 0),
    endereco text not null check (length(trim(endereco)) > 0),
    email text not null unique,
    celular_whatsapp text not null,
    data_cadastro timestamptz not null default now(),
    constraint email_valido check (
        email = lower(trim(email)) and email ~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'
    ),
    constraint celular_valido check (celular_whatsapp ~ '^[0-9]{10,13}$')
);

-- Ordens de serviço: o cliente só pode ser excluído depois das suas OS.
create table public.ordens_servico (
    id bigint generated always as identity primary key,
    cliente_id bigint not null references public.clientes(id) on delete restrict,
    modelo_computador text not null check (length(trim(modelo_computador)) > 0),
    problema_relatado text not null check (length(trim(problema_relatado)) > 0),
    status text not null default 'Aberto' check (
        status in ('Aberto', 'Em análise', 'Aguardando peça', 'Concluído', 'Entregue')
    ),
    data_abertura timestamptz not null default now(),
    data_atualizacao timestamptz not null default now()
);

-- Índices para consultas por cliente e status.
create index ordens_cliente_idx on public.ordens_servico(cliente_id);
create index ordens_status_idx on public.ordens_servico(status);

-- Atualiza a data quando uma OS é alterada.
create function public.atualizar_data_os()
returns trigger language plpgsql set search_path = '' as $$
begin
    new.data_atualizacao = clock_timestamp();
    return new;
end;
$$;
create trigger atualizar_os before update on public.ordens_servico
for each row execute function public.atualizar_data_os();

-- Cria cliente e OS na mesma transação, reaproveitando o e-mail existente.
create function public.cadastrar_os(
    p_nome text, p_endereco text, p_email text, p_celular text,
    p_modelo text, p_problema text
)
returns bigint language plpgsql security invoker set search_path = '' as $$
declare
    v_cliente bigint;
    v_os bigint;
begin
    insert into public.clientes(nome, endereco, email, celular_whatsapp)
    values (trim(p_nome), trim(p_endereco), lower(trim(p_email)), trim(p_celular))
    on conflict (email) do update set email = excluded.email
    returning id into v_cliente;

    insert into public.ordens_servico(cliente_id, modelo_computador, problema_relatado)
    values (v_cliente, trim(p_modelo), trim(p_problema)) returning id into v_os;
    return v_os;
end;
$$;

-- Os aplicativos acessam o banco pelo servidor, com a chave service_role.
alter table public.clientes enable row level security;
alter table public.ordens_servico enable row level security;
revoke all on public.clientes, public.ordens_servico from anon, authenticated;
grant select, insert, update, delete on public.clientes, public.ordens_servico to service_role;
grant usage, select on sequence public.clientes_id_seq, public.ordens_servico_id_seq to service_role;
revoke execute on function public.cadastrar_os(text,text,text,text,text,text) from public, anon, authenticated;
grant execute on function public.cadastrar_os(text,text,text,text,text,text) to service_role;
