--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.user_profiles DROP CONSTRAINT IF EXISTS user_profiles_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_profiles DROP CONSTRAINT IF EXISTS user_profiles_created_by_id_fkey;
ALTER TABLE IF EXISTS ONLY public.import_logs DROP CONSTRAINT IF EXISTS import_logs_created_by_id_fkey;
ALTER TABLE IF EXISTS ONLY public.check_sequences DROP CONSTRAINT IF EXISTS check_sequences_bank_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_transactions DROP CONSTRAINT IF EXISTS bank_transactions_vendor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_transactions DROP CONSTRAINT IF EXISTS bank_transactions_client_id_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_transactions DROP CONSTRAINT IF EXISTS bank_transactions_case_id_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_transaction_audit DROP CONSTRAINT IF EXISTS bank_transaction_audit_transaction_fk;
DROP INDEX IF EXISTS public.user_profiles_user_id_idx;
DROP INDEX IF EXISTS public.user_profiles_role_idx;
DROP INDEX IF EXISTS public.user_profiles_created_by_id_idx;
DROP INDEX IF EXISTS public.idx_vendors_data_source;
DROP INDEX IF EXISTS public.idx_import_logs_status;
DROP INDEX IF EXISTS public.idx_import_logs_started_at;
DROP INDEX IF EXISTS public.idx_import_logs_import_type;
DROP INDEX IF EXISTS public.idx_import_logs_created_by;
DROP INDEX IF EXISTS public.idx_import_audit_date;
DROP INDEX IF EXISTS public.idx_clients_data_source;
DROP INDEX IF EXISTS public.idx_cases_data_source;
DROP INDEX IF EXISTS public.idx_bank_transactions_vendor_id;
DROP INDEX IF EXISTS public.idx_bank_transactions_type;
DROP INDEX IF EXISTS public.idx_bank_transactions_status;
DROP INDEX IF EXISTS public.idx_bank_transactions_payee_lower;
DROP INDEX IF EXISTS public.idx_bank_transactions_number;
DROP INDEX IF EXISTS public.idx_bank_transactions_date_type;
DROP INDEX IF EXISTS public.idx_bank_transactions_date;
DROP INDEX IF EXISTS public.idx_bank_transactions_data_source;
DROP INDEX IF EXISTS public.idx_bank_transactions_client_type_status;
DROP INDEX IF EXISTS public.idx_bank_transactions_client_id;
DROP INDEX IF EXISTS public.idx_bank_transactions_check_queries;
DROP INDEX IF EXISTS public.idx_bank_transactions_check_number;
DROP INDEX IF EXISTS public.idx_bank_transactions_case_id;
DROP INDEX IF EXISTS public.bank_transaction_audit_transaction_id_8fd3002a;
DROP INDEX IF EXISTS public.audit_user_idx;
DROP INDEX IF EXISTS public.audit_trans_date_idx;
DROP INDEX IF EXISTS public.audit_date_idx;
DROP INDEX IF EXISTS public.audit_action_idx;
ALTER TABLE IF EXISTS ONLY public.vendors DROP CONSTRAINT IF EXISTS vendors_pkey;
ALTER TABLE IF EXISTS ONLY public.vendor_types DROP CONSTRAINT IF EXISTS vendor_types_pkey;
ALTER TABLE IF EXISTS ONLY public.vendor_types DROP CONSTRAINT IF EXISTS vendor_types_name_key;
ALTER TABLE IF EXISTS ONLY public.user_profiles DROP CONSTRAINT IF EXISTS user_profiles_user_id_key;
ALTER TABLE IF EXISTS ONLY public.user_profiles DROP CONSTRAINT IF EXISTS user_profiles_pkey;
ALTER TABLE IF EXISTS ONLY public.clients DROP CONSTRAINT IF EXISTS unique_client_name;
ALTER TABLE IF EXISTS ONLY public.bank_transactions DROP CONSTRAINT IF EXISTS uk_bank_transactions_number;
ALTER TABLE IF EXISTS ONLY public.settlements DROP CONSTRAINT IF EXISTS settlements_settlement_number_key;
ALTER TABLE IF EXISTS ONLY public.settlements DROP CONSTRAINT IF EXISTS settlements_pkey;
ALTER TABLE IF EXISTS ONLY public.settlement_reconciliations DROP CONSTRAINT IF EXISTS settlement_reconciliations_settlement_id_key;
ALTER TABLE IF EXISTS ONLY public.settlement_reconciliations DROP CONSTRAINT IF EXISTS settlement_reconciliations_pkey;
ALTER TABLE IF EXISTS ONLY public.settlement_distributions DROP CONSTRAINT IF EXISTS settlement_distributions_pkey;
ALTER TABLE IF EXISTS ONLY public.settings DROP CONSTRAINT IF EXISTS settings_pkey;
ALTER TABLE IF EXISTS ONLY public.settings DROP CONSTRAINT IF EXISTS settings_category_key_key;
ALTER TABLE IF EXISTS ONLY public.law_firm DROP CONSTRAINT IF EXISTS law_firm_pkey;
ALTER TABLE IF EXISTS ONLY public.import_logs DROP CONSTRAINT IF EXISTS import_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.import_audit DROP CONSTRAINT IF EXISTS import_audit_pkey;
ALTER TABLE IF EXISTS ONLY public.django_session DROP CONSTRAINT IF EXISTS django_session_pkey;
ALTER TABLE IF EXISTS ONLY public.django_migrations DROP CONSTRAINT IF EXISTS django_migrations_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_app_label_model_76bd3d3b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_pkey;
ALTER TABLE IF EXISTS ONLY public.clients DROP CONSTRAINT IF EXISTS clients_pkey;
ALTER TABLE IF EXISTS ONLY public.clients DROP CONSTRAINT IF EXISTS clients_client_number_key;
ALTER TABLE IF EXISTS ONLY public.check_sequences DROP CONSTRAINT IF EXISTS check_sequences_pkey;
ALTER TABLE IF EXISTS ONLY public.check_sequences DROP CONSTRAINT IF EXISTS check_sequences_bank_account_id_key;
ALTER TABLE IF EXISTS ONLY public.cases DROP CONSTRAINT IF EXISTS cases_pkey;
ALTER TABLE IF EXISTS ONLY public.cases DROP CONSTRAINT IF EXISTS cases_case_number_key;
ALTER TABLE IF EXISTS ONLY public.case_number_counter DROP CONSTRAINT IF EXISTS case_number_counter_pkey;
ALTER TABLE IF EXISTS ONLY public.bank_transactions DROP CONSTRAINT IF EXISTS bank_transactions_pkey;
ALTER TABLE IF EXISTS ONLY public.bank_transaction_audit DROP CONSTRAINT IF EXISTS bank_transaction_audit_pkey;
ALTER TABLE IF EXISTS ONLY public.bank_reconciliations DROP CONSTRAINT IF EXISTS bank_reconciliations_pkey;
ALTER TABLE IF EXISTS ONLY public.bank_accounts DROP CONSTRAINT IF EXISTS bank_accounts_pkey;
ALTER TABLE IF EXISTS ONLY public.bank_accounts DROP CONSTRAINT IF EXISTS bank_accounts_account_number_key;
ALTER TABLE IF EXISTS ONLY public.auth_user DROP CONSTRAINT IF EXISTS auth_user_username_key;
ALTER TABLE IF EXISTS ONLY public.auth_user_user_permissions DROP CONSTRAINT IF EXISTS auth_user_user_permissions_user_id_permission_id_14a6b632_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_user_user_permissions DROP CONSTRAINT IF EXISTS auth_user_user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_user DROP CONSTRAINT IF EXISTS auth_user_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_user_groups DROP CONSTRAINT IF EXISTS auth_user_groups_user_id_group_id_94350c0c_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_user_groups DROP CONSTRAINT IF EXISTS auth_user_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_codename_01ab375a_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_name_key;
ALTER TABLE IF EXISTS public.vendors ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.vendor_types ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.user_profiles ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.settlements ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.settlement_reconciliations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.settlement_distributions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.settings ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.import_logs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.import_audit ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.clients ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.check_sequences ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.cases ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.bank_transactions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.bank_reconciliations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.bank_accounts ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.vendors_id_seq;
DROP TABLE IF EXISTS public.vendors;
DROP SEQUENCE IF EXISTS public.vendor_types_id_seq;
DROP TABLE IF EXISTS public.vendor_types;
DROP SEQUENCE IF EXISTS public.user_profiles_id_seq;
DROP TABLE IF EXISTS public.user_profiles;
DROP SEQUENCE IF EXISTS public.settlements_id_seq;
DROP TABLE IF EXISTS public.settlements;
DROP SEQUENCE IF EXISTS public.settlement_reconciliations_id_seq;
DROP TABLE IF EXISTS public.settlement_reconciliations;
DROP SEQUENCE IF EXISTS public.settlement_distributions_id_seq;
DROP TABLE IF EXISTS public.settlement_distributions;
DROP SEQUENCE IF EXISTS public.settings_id_seq;
DROP TABLE IF EXISTS public.settings;
DROP TABLE IF EXISTS public.law_firm;
DROP SEQUENCE IF EXISTS public.import_logs_id_seq;
DROP TABLE IF EXISTS public.import_logs;
DROP SEQUENCE IF EXISTS public.import_audit_id_seq;
DROP TABLE IF EXISTS public.import_audit;
DROP TABLE IF EXISTS public.django_session;
DROP TABLE IF EXISTS public.django_migrations;
DROP TABLE IF EXISTS public.django_content_type;
DROP TABLE IF EXISTS public.django_admin_log;
DROP SEQUENCE IF EXISTS public.clients_id_seq;
DROP TABLE IF EXISTS public.clients;
DROP SEQUENCE IF EXISTS public.check_sequences_id_seq;
DROP TABLE IF EXISTS public.check_sequences;
DROP SEQUENCE IF EXISTS public.cases_id_seq;
DROP TABLE IF EXISTS public.cases;
DROP TABLE IF EXISTS public.case_number_counter;
DROP SEQUENCE IF EXISTS public.bank_transactions_id_seq;
DROP TABLE IF EXISTS public.bank_transactions;
DROP TABLE IF EXISTS public.bank_transaction_audit;
DROP SEQUENCE IF EXISTS public.bank_reconciliations_id_seq;
DROP TABLE IF EXISTS public.bank_reconciliations;
DROP SEQUENCE IF EXISTS public.bank_accounts_id_seq;
DROP TABLE IF EXISTS public.bank_accounts;
DROP TABLE IF EXISTS public.auth_user_user_permissions;
DROP TABLE IF EXISTS public.auth_user_groups;
DROP TABLE IF EXISTS public.auth_user;
DROP TABLE IF EXISTS public.auth_permission;
DROP TABLE IF EXISTS public.auth_group_permissions;
DROP TABLE IF EXISTS public.auth_group;
-- *not* dropping schema, since initdb creates it
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: iolta_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO iolta_user;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: iolta_user
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO iolta_user;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO iolta_user;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO iolta_user;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO iolta_user;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO iolta_user;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.auth_user_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.auth_user ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO iolta_user;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.auth_user_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: bank_accounts; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.bank_accounts (
    id integer NOT NULL,
    account_number character varying(50) NOT NULL,
    bank_name character varying(200) NOT NULL,
    bank_address text,
    account_name character varying(200) NOT NULL,
    routing_number character varying(20),
    account_type character varying(50) DEFAULT 'Trust Account'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    opening_balance numeric(15,2) DEFAULT 0.00,
    next_check_number integer DEFAULT 1001,
    data_source character varying(20) DEFAULT 'webapp'::character varying
);


ALTER TABLE public.bank_accounts OWNER TO iolta_user;

--
-- Name: COLUMN bank_accounts.data_source; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.bank_accounts.data_source IS 'Source of data: webapp (default), csv, api';


--
-- Name: bank_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.bank_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_accounts_id_seq OWNER TO iolta_user;

--
-- Name: bank_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.bank_accounts_id_seq OWNED BY public.bank_accounts.id;


--
-- Name: bank_reconciliations; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.bank_reconciliations (
    id integer NOT NULL,
    bank_account_id integer NOT NULL,
    reconciliation_date date NOT NULL,
    statement_balance numeric(15,2) NOT NULL,
    book_balance numeric(15,2) NOT NULL,
    difference numeric(15,2) GENERATED ALWAYS AS ((statement_balance - book_balance)) STORED,
    is_reconciled boolean DEFAULT false,
    reconciled_by character varying(100),
    reconciled_at timestamp with time zone,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.bank_reconciliations OWNER TO iolta_user;

--
-- Name: bank_reconciliations_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.bank_reconciliations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_reconciliations_id_seq OWNER TO iolta_user;

--
-- Name: bank_reconciliations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.bank_reconciliations_id_seq OWNED BY public.bank_reconciliations.id;


--
-- Name: bank_transaction_audit; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.bank_transaction_audit (
    id bigint NOT NULL,
    action character varying(20) NOT NULL,
    action_date timestamp with time zone NOT NULL,
    action_by character varying(100) NOT NULL,
    old_values jsonb,
    new_values jsonb,
    old_amount numeric(15,2),
    new_amount numeric(15,2),
    old_status character varying(20),
    new_status character varying(20),
    change_reason text NOT NULL,
    ip_address inet,
    transaction_id bigint NOT NULL
);


ALTER TABLE public.bank_transaction_audit OWNER TO iolta_user;

--
-- Name: bank_transaction_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.bank_transaction_audit ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.bank_transaction_audit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: bank_transactions; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.bank_transactions (
    id integer NOT NULL,
    bank_account_id integer NOT NULL,
    transaction_date date NOT NULL,
    post_date date,
    transaction_type character varying(20) NOT NULL,
    amount numeric(15,2) NOT NULL,
    description text NOT NULL,
    reference_number character varying(100),
    check_number character varying(50),
    bank_reference character varying(100),
    bank_category character varying(100),
    status character varying(20) DEFAULT 'pending'::character varying,
    matched_transaction_id integer,
    reconciliation_notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(100),
    client_id integer,
    case_id integer,
    vendor_id integer,
    check_memo character varying(500),
    cleared_date date,
    transaction_number character varying(100),
    item_type character varying(20),
    check_is_printed boolean DEFAULT false,
    voided_date timestamp without time zone,
    voided_by character varying(100),
    void_reason text,
    payee character varying(255),
    rec_id integer,
    original_transaction_id integer,
    original_item_id integer,
    data_source character varying(20) DEFAULT 'webapp'::character varying NOT NULL,
    import_batch_id integer
);


ALTER TABLE public.bank_transactions OWNER TO iolta_user;

--
-- Name: COLUMN bank_transactions.data_source; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.bank_transactions.data_source IS 'Source of data entry: webapp, csv, or api';


--
-- Name: bank_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.bank_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_transactions_id_seq OWNER TO iolta_user;

--
-- Name: bank_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.bank_transactions_id_seq OWNED BY public.bank_transactions.id;


--
-- Name: case_number_counter; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.case_number_counter (
    id integer DEFAULT 1 NOT NULL,
    last_number integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.case_number_counter OWNER TO iolta_user;

--
-- Name: cases; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.cases (
    id integer NOT NULL,
    case_number character varying(100) NOT NULL,
    client_id integer NOT NULL,
    case_description text,
    case_amount numeric(15,2) DEFAULT 0.00,
    case_status character varying(50) DEFAULT 'Open'::character varying,
    opened_date date,
    closed_date date,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    case_title character varying(255) NOT NULL,
    data_source character varying(20) DEFAULT 'webapp'::character varying NOT NULL,
    import_batch_id integer
);


ALTER TABLE public.cases OWNER TO iolta_user;

--
-- Name: COLUMN cases.data_source; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.cases.data_source IS 'Source of data entry: webapp, csv, or api';


--
-- Name: cases_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.cases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cases_id_seq OWNER TO iolta_user;

--
-- Name: cases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.cases_id_seq OWNED BY public.cases.id;


--
-- Name: check_sequences; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.check_sequences (
    id integer NOT NULL,
    bank_account_id integer NOT NULL,
    next_check_number integer DEFAULT 1001 NOT NULL,
    last_assigned_number integer,
    last_assigned_date timestamp with time zone
);


ALTER TABLE public.check_sequences OWNER TO iolta_user;

--
-- Name: check_sequences_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.check_sequences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.check_sequences_id_seq OWNER TO iolta_user;

--
-- Name: check_sequences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.check_sequences_id_seq OWNED BY public.check_sequences.id;


--
-- Name: clients; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.clients (
    id integer NOT NULL,
    client_number character varying(50),
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    email character varying(255),
    phone character varying(20),
    address text,
    city character varying(100),
    state character varying(50),
    zip_code character varying(20),
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    client_type character varying(20) DEFAULT 'individual'::character varying,
    trust_account_status character varying(30) DEFAULT 'ACTIVE_ZERO_BALANCE'::character varying,
    data_source character varying(20) DEFAULT 'webapp'::character varying NOT NULL,
    import_batch_id integer
);


ALTER TABLE public.clients OWNER TO iolta_user;

--
-- Name: COLUMN clients.data_source; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.clients.data_source IS 'Source of data entry: webapp, csv, or api';


--
-- Name: clients_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.clients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clients_id_seq OWNER TO iolta_user;

--
-- Name: clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.clients_id_seq OWNED BY public.clients.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO iolta_user;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO iolta_user;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO iolta_user;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO iolta_user;

--
-- Name: import_audit; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.import_audit (
    id integer NOT NULL,
    import_date timestamp with time zone DEFAULT now() NOT NULL,
    import_type character varying(20) NOT NULL,
    file_name character varying(255),
    status character varying(20) DEFAULT 'in_progress'::character varying NOT NULL,
    total_records integer DEFAULT 0,
    successful_records integer DEFAULT 0,
    failed_records integer DEFAULT 0,
    clients_created integer DEFAULT 0,
    cases_created integer DEFAULT 0,
    transactions_created integer DEFAULT 0,
    vendors_created integer DEFAULT 0,
    error_log text,
    imported_by character varying(100) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    expected_clients integer DEFAULT 0,
    expected_cases integer DEFAULT 0,
    expected_transactions integer DEFAULT 0,
    expected_vendors integer DEFAULT 0,
    existing_clients integer DEFAULT 0,
    existing_cases integer DEFAULT 0,
    existing_vendors integer DEFAULT 0,
    preview_data text,
    preview_errors text,
    clients_skipped integer DEFAULT 0,
    cases_skipped integer DEFAULT 0,
    vendors_skipped integer DEFAULT 0,
    rows_with_errors integer DEFAULT 0,
    total_clients_in_csv integer DEFAULT 0,
    total_cases_in_csv integer DEFAULT 0,
    total_transactions_in_csv integer DEFAULT 0,
    total_vendors_in_csv integer DEFAULT 0
);


ALTER TABLE public.import_audit OWNER TO iolta_user;

--
-- Name: import_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.import_audit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.import_audit_id_seq OWNER TO iolta_user;

--
-- Name: import_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.import_audit_id_seq OWNED BY public.import_audit.id;


--
-- Name: import_logs; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.import_logs (
    id integer NOT NULL,
    import_type character varying(50) NOT NULL,
    filename character varying(255),
    status character varying(20) DEFAULT 'in_progress'::character varying NOT NULL,
    started_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at timestamp with time zone,
    total_rows integer DEFAULT 0,
    clients_created integer DEFAULT 0,
    clients_existing integer DEFAULT 0,
    cases_created integer DEFAULT 0,
    transactions_created integer DEFAULT 0,
    transactions_skipped integer DEFAULT 0,
    errors jsonb DEFAULT '[]'::jsonb,
    summary jsonb DEFAULT '{}'::jsonb,
    created_by_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.import_logs OWNER TO iolta_user;

--
-- Name: TABLE import_logs; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON TABLE public.import_logs IS 'Tracks all data import operations';


--
-- Name: COLUMN import_logs.import_type; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.import_logs.import_type IS 'Type of import: quickbooks_csv, generic_csv, api_bulk';


--
-- Name: COLUMN import_logs.status; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.import_logs.status IS 'Import status: in_progress, completed, failed, partial';


--
-- Name: COLUMN import_logs.errors; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.import_logs.errors IS 'JSON array of error objects';


--
-- Name: COLUMN import_logs.summary; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.import_logs.summary IS 'JSON object with additional import details';


--
-- Name: import_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.import_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.import_logs_id_seq OWNER TO iolta_user;

--
-- Name: import_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.import_logs_id_seq OWNED BY public.import_logs.id;


--
-- Name: law_firm; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.law_firm (
    id integer NOT NULL,
    firm_name character varying(200) NOT NULL,
    doing_business_as character varying(200) NOT NULL,
    address_line1 character varying(100) NOT NULL,
    address_line2 character varying(100) NOT NULL,
    city character varying(50) NOT NULL,
    state character varying(2) NOT NULL,
    zip_code character varying(10) NOT NULL,
    phone character varying(20) NOT NULL,
    fax character varying(20) NOT NULL,
    email character varying(254) NOT NULL,
    website character varying(200) NOT NULL,
    principal_attorney character varying(100) NOT NULL,
    attorney_bar_number character varying(20) NOT NULL,
    attorney_state character varying(2) NOT NULL,
    trust_account_required boolean NOT NULL,
    iolta_compliant boolean NOT NULL,
    trust_account_certification_date date,
    tax_id character varying(20) NOT NULL,
    state_registration character varying(50) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


ALTER TABLE public.law_firm OWNER TO iolta_user;

--
-- Name: law_firm_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

ALTER TABLE public.law_firm ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.law_firm_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: settings; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.settings (
    id integer NOT NULL,
    category character varying(50) NOT NULL,
    key character varying(100) NOT NULL,
    value character varying(255) NOT NULL,
    display_order integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.settings OWNER TO iolta_user;

--
-- Name: settings_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.settings_id_seq OWNER TO iolta_user;

--
-- Name: settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.settings_id_seq OWNED BY public.settings.id;


--
-- Name: settlement_distributions; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.settlement_distributions (
    id integer NOT NULL,
    settlement_id integer NOT NULL,
    vendor_id integer,
    client_id integer,
    distribution_type character varying(20) NOT NULL,
    amount numeric(15,2) NOT NULL,
    description text,
    check_number character varying(50),
    is_paid boolean DEFAULT false,
    paid_date date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT settlement_distributions_amount_check CHECK ((amount > (0)::numeric)),
    CONSTRAINT settlement_distributions_recipient_check CHECK ((((vendor_id IS NOT NULL) AND (client_id IS NULL)) OR ((vendor_id IS NULL) AND (client_id IS NOT NULL)))),
    CONSTRAINT settlement_distributions_type_check CHECK (((distribution_type)::text = ANY (ARRAY[('VENDOR_PAYMENT'::character varying)::text, ('CLIENT_REFUND'::character varying)::text, ('ATTORNEY_FEES'::character varying)::text, ('COURT_COSTS'::character varying)::text, ('MEDICAL_EXPENSES'::character varying)::text, ('OTHER'::character varying)::text])))
);


ALTER TABLE public.settlement_distributions OWNER TO iolta_user;

--
-- Name: TABLE settlement_distributions; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON TABLE public.settlement_distributions IS 'Individual distributions within a settlement';


--
-- Name: settlement_distributions_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.settlement_distributions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.settlement_distributions_id_seq OWNER TO iolta_user;

--
-- Name: settlement_distributions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.settlement_distributions_id_seq OWNED BY public.settlement_distributions.id;


--
-- Name: settlement_reconciliations; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.settlement_reconciliations (
    id integer NOT NULL,
    settlement_id integer NOT NULL,
    bank_balance_before numeric(15,2) NOT NULL,
    bank_balance_after numeric(15,2),
    client_balance_before numeric(15,2) NOT NULL,
    client_balance_after numeric(15,2),
    total_distributions numeric(15,2) DEFAULT 0.00 NOT NULL,
    reconciliation_status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    reconciled_by character varying(100),
    reconciled_at timestamp with time zone,
    notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT settlement_reconciliations_status_check CHECK (((reconciliation_status)::text = ANY (ARRAY[('PENDING'::character varying)::text, ('BALANCED'::character varying)::text, ('UNBALANCED'::character varying)::text, ('RESOLVED'::character varying)::text])))
);


ALTER TABLE public.settlement_reconciliations OWNER TO iolta_user;

--
-- Name: TABLE settlement_reconciliations; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON TABLE public.settlement_reconciliations IS 'Reconciliation records for 3-way balance checking';


--
-- Name: settlement_reconciliations_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.settlement_reconciliations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.settlement_reconciliations_id_seq OWNER TO iolta_user;

--
-- Name: settlement_reconciliations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.settlement_reconciliations_id_seq OWNED BY public.settlement_reconciliations.id;


--
-- Name: settlements; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.settlements (
    id integer NOT NULL,
    settlement_number character varying(100),
    settlement_date date DEFAULT CURRENT_DATE NOT NULL,
    client_id integer NOT NULL,
    case_id integer,
    bank_account_id integer NOT NULL,
    total_amount numeric(15,2) DEFAULT 0.00 NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    notes text,
    created_by character varying(100),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT settlements_status_check CHECK (((status)::text = ANY (ARRAY[('PENDING'::character varying)::text, ('IN_PROGRESS'::character varying)::text, ('COMPLETED'::character varying)::text, ('CANCELLED'::character varying)::text]))),
    CONSTRAINT settlements_total_amount_check CHECK ((total_amount >= (0)::numeric))
);


ALTER TABLE public.settlements OWNER TO iolta_user;

--
-- Name: TABLE settlements; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON TABLE public.settlements IS 'Main settlements table for tracking 3-way settlements';


--
-- Name: settlements_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.settlements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.settlements_id_seq OWNER TO iolta_user;

--
-- Name: settlements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.settlements_id_seq OWNED BY public.settlements.id;


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.user_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role character varying(30) DEFAULT 'paralegal'::character varying NOT NULL,
    phone character varying(20) DEFAULT ''::character varying,
    employee_id character varying(50) DEFAULT ''::character varying,
    department character varying(100) DEFAULT ''::character varying,
    is_active boolean DEFAULT true NOT NULL,
    can_approve_transactions boolean DEFAULT false NOT NULL,
    can_reconcile boolean DEFAULT false NOT NULL,
    can_print_checks boolean DEFAULT false NOT NULL,
    can_manage_users boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    created_by_id integer,
    CONSTRAINT check_role CHECK (((role)::text = ANY ((ARRAY['managing_attorney'::character varying, 'staff_attorney'::character varying, 'paralegal'::character varying, 'bookkeeper'::character varying, 'system_admin'::character varying])::text[])))
);


ALTER TABLE public.user_profiles OWNER TO iolta_user;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.user_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_profiles_id_seq OWNER TO iolta_user;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.user_profiles_id_seq OWNED BY public.user_profiles.id;


--
-- Name: vendor_types; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.vendor_types (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    data_source character varying(20) DEFAULT 'webapp'::character varying
);


ALTER TABLE public.vendor_types OWNER TO iolta_user;

--
-- Name: COLUMN vendor_types.data_source; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.vendor_types.data_source IS 'Source of data: webapp (default), csv, api';


--
-- Name: vendor_types_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.vendor_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vendor_types_id_seq OWNER TO iolta_user;

--
-- Name: vendor_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.vendor_types_id_seq OWNED BY public.vendor_types.id;


--
-- Name: vendors; Type: TABLE; Schema: public; Owner: iolta_user
--

CREATE TABLE public.vendors (
    id integer NOT NULL,
    vendor_number character varying(50),
    vendor_name character varying(200) NOT NULL,
    vendor_type_id integer,
    contact_person character varying(200),
    email character varying(255),
    phone character varying(20),
    address text,
    city character varying(100),
    state character varying(50),
    zip_code character varying(20),
    tax_id character varying(50),
    client_id integer,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    data_source character varying(20) DEFAULT 'webapp'::character varying NOT NULL,
    import_batch_id integer
);


ALTER TABLE public.vendors OWNER TO iolta_user;

--
-- Name: COLUMN vendors.data_source; Type: COMMENT; Schema: public; Owner: iolta_user
--

COMMENT ON COLUMN public.vendors.data_source IS 'Source of data entry: webapp, csv, or api';


--
-- Name: vendors_id_seq; Type: SEQUENCE; Schema: public; Owner: iolta_user
--

CREATE SEQUENCE public.vendors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vendors_id_seq OWNER TO iolta_user;

--
-- Name: vendors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: iolta_user
--

ALTER SEQUENCE public.vendors_id_seq OWNED BY public.vendors.id;


--
-- Name: bank_accounts id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_accounts ALTER COLUMN id SET DEFAULT nextval('public.bank_accounts_id_seq'::regclass);


--
-- Name: bank_reconciliations id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_reconciliations ALTER COLUMN id SET DEFAULT nextval('public.bank_reconciliations_id_seq'::regclass);


--
-- Name: bank_transactions id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_transactions ALTER COLUMN id SET DEFAULT nextval('public.bank_transactions_id_seq'::regclass);


--
-- Name: cases id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.cases ALTER COLUMN id SET DEFAULT nextval('public.cases_id_seq'::regclass);


--
-- Name: check_sequences id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.check_sequences ALTER COLUMN id SET DEFAULT nextval('public.check_sequences_id_seq'::regclass);


--
-- Name: clients id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.clients ALTER COLUMN id SET DEFAULT nextval('public.clients_id_seq'::regclass);


--
-- Name: import_audit id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.import_audit ALTER COLUMN id SET DEFAULT nextval('public.import_audit_id_seq'::regclass);


--
-- Name: import_logs id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.import_logs ALTER COLUMN id SET DEFAULT nextval('public.import_logs_id_seq'::regclass);


--
-- Name: settings id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settings ALTER COLUMN id SET DEFAULT nextval('public.settings_id_seq'::regclass);


--
-- Name: settlement_distributions id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settlement_distributions ALTER COLUMN id SET DEFAULT nextval('public.settlement_distributions_id_seq'::regclass);


--
-- Name: settlement_reconciliations id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settlement_reconciliations ALTER COLUMN id SET DEFAULT nextval('public.settlement_reconciliations_id_seq'::regclass);


--
-- Name: settlements id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settlements ALTER COLUMN id SET DEFAULT nextval('public.settlements_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: vendor_types id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.vendor_types ALTER COLUMN id SET DEFAULT nextval('public.vendor_types_id_seq'::regclass);


--
-- Name: vendors id; Type: DEFAULT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.vendors ALTER COLUMN id SET DEFAULT nextval('public.vendors_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add case	7	add_case
26	Can change case	7	change_case
27	Can delete case	7	delete_case
28	Can view case	7	view_case
29	Can add client	8	add_client
30	Can change client	8	change_client
31	Can delete client	8	delete_client
32	Can view client	8	view_client
33	Can add vendor type	9	add_vendortype
34	Can change vendor type	9	change_vendortype
35	Can delete vendor type	9	delete_vendortype
36	Can view vendor type	9	view_vendortype
37	Can add vendor	10	add_vendor
38	Can change vendor	10	change_vendor
39	Can delete vendor	10	delete_vendor
40	Can view vendor	10	view_vendor
41	Can add bank account	11	add_bankaccount
42	Can change bank account	11	change_bankaccount
43	Can delete bank account	11	delete_bankaccount
44	Can view bank account	11	view_bankaccount
45	Can add bank transaction	12	add_banktransaction
46	Can change bank transaction	12	change_banktransaction
47	Can delete bank transaction	12	delete_banktransaction
48	Can view bank transaction	12	view_banktransaction
49	Can add bank reconciliation	13	add_bankreconciliation
50	Can change bank reconciliation	13	change_bankreconciliation
51	Can delete bank reconciliation	13	delete_bankreconciliation
52	Can view bank reconciliation	13	view_bankreconciliation
53	Can add Bank Transaction Audit Log	14	add_banktransactionaudit
54	Can change Bank Transaction Audit Log	14	change_banktransactionaudit
55	Can delete Bank Transaction Audit Log	14	delete_banktransactionaudit
56	Can view Bank Transaction Audit Log	14	view_banktransactionaudit
57	Can add settlement	15	add_settlement
58	Can change settlement	15	change_settlement
59	Can delete settlement	15	delete_settlement
60	Can view settlement	15	view_settlement
61	Can add settlement reconciliation	16	add_settlementreconciliation
62	Can change settlement reconciliation	16	change_settlementreconciliation
63	Can delete settlement reconciliation	16	delete_settlementreconciliation
64	Can view settlement reconciliation	16	view_settlementreconciliation
65	Can add settlement distribution	17	add_settlementdistribution
66	Can change settlement distribution	17	change_settlementdistribution
67	Can delete settlement distribution	17	delete_settlementdistribution
68	Can view settlement distribution	17	view_settlementdistribution
69	Can add Import Audit	18	add_importaudit
70	Can change Import Audit	18	change_importaudit
71	Can delete Import Audit	18	delete_importaudit
72	Can view Import Audit	18	view_importaudit
73	Can add Law Firm	19	add_lawfirm
74	Can change Law Firm	19	change_lawfirm
75	Can delete Law Firm	19	delete_lawfirm
76	Can view Law Firm	19	view_lawfirm
77	Can add setting	20	add_setting
78	Can change setting	20	change_setting
79	Can delete setting	20	delete_setting
80	Can view setting	20	view_setting
81	Can add Check Sequence	21	add_checksequence
82	Can change Check Sequence	21	change_checksequence
83	Can delete Check Sequence	21	delete_checksequence
84	Can view Check Sequence	21	view_checksequence
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
3	pbkdf2_sha256$600000$Pfp5wm4m17gBSWeUgHAz5S$ei6DgkIxRspSuc6sdAWF8oPSVpftfiGPnThzoyIGoTc=	2025-11-14 15:09:36.996034+00	f	amin	Amin	Ezzy	amin@gmail.com	f	t	2025-11-14 15:09:13.90419+00
2	pbkdf2_sha256$600000$9lpIyB72aZyvdjdrCVieB1$l3hdcQVfdckWEZ3+xfwqdwMiumRBFT6C+BQTdzk0Hy4=	2025-11-14 15:13:46.186736+00	t	admin			admin@example.com	t	t	2025-09-28 11:34:41.843918+00
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: bank_accounts; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.bank_accounts (id, account_number, bank_name, bank_address, account_name, routing_number, account_type, is_active, created_at, updated_at, opening_balance, next_check_number, data_source) FROM stdin;
1	****9876	Chase Bank	270 Park Avenue, New York, NY 10017	IOLTA Trust Account - Main	021000021	Trust Account	t	2025-11-03 10:45:52.45886+00	2025-11-06 18:47:57.244296+00	0.00	1060	webapp
\.


--
-- Data for Name: bank_reconciliations; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.bank_reconciliations (id, bank_account_id, reconciliation_date, statement_balance, book_balance, is_reconciled, reconciled_by, reconciled_at, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: bank_transaction_audit; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.bank_transaction_audit (id, action, action_date, action_by, old_values, new_values, old_amount, new_amount, old_status, new_status, change_reason, ip_address, transaction_id) FROM stdin;
2	VOIDED	2025-11-03 10:58:24.367129+00	admin	{"payee": "Liability Investigations", "amount": "1800.00", "status": "pending", "case_id": 10, "client_id": 10, "vendor_id": 6, "voided_by": null, "check_memo": "Expert inspection", "description": "Facility inspection expert", "void_reason": null, "voided_date": null, "check_number": null, "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-03-03", "transaction_type": "WITHDRAWAL", "transaction_number": null}	{"payee": "Liability Investigations", "amount": "1800.00", "status": "voided", "case_id": 10, "client_id": 10, "vendor_id": 6, "voided_by": null, "check_memo": "Expert inspection", "description": "VOIDED - Reissued on 2025-11-03: Facility inspection expert", "void_reason": null, "voided_date": "2025-11-03 10:58:24.362684+00:00", "check_number": "Voided", "cleared_date": null, "reference_number": "Voided", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": null}	1800.00	0.00	pending	voided	Check reissued by admin - original voided	151.101.0.223	45
3	CREATED	2025-11-03 10:58:24.37336+00	system	\N	{"payee": "", "amount": "1800.00", "status": "cleared", "case_id": 10, "client_id": 10, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Reversal - Reissue of check #TO PRINT: Facility inspection expert", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-2025-001"}	\N	1800.00	\N	cleared		127.0.0.1	46
4	CREATED	2025-11-03 10:58:24.375709+00	system	\N	{"payee": "Liability Investigations", "amount": "1800.00", "status": "pending", "case_id": 10, "client_id": 10, "vendor_id": 6, "voided_by": "", "check_memo": "Expert inspection", "description": "Reissue of check #TO PRINT: Facility inspection expert", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-001"}	\N	1800.00	\N	pending		127.0.0.1	47
5	VOIDED	2025-11-03 11:00:27.673481+00	admin	{"payee": "Expert Witness Services", "amount": "3500.00", "status": "pending", "case_id": 9, "client_id": 9, "vendor_id": 2, "voided_by": null, "check_memo": "Expert testimony", "description": "Medical expert testimony", "void_reason": null, "voided_date": null, "check_number": null, "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-03-02", "transaction_type": "WITHDRAWAL", "transaction_number": null}	{"payee": "Expert Witness Services", "amount": "3500.00", "status": "voided", "case_id": 9, "client_id": 9, "vendor_id": 2, "voided_by": null, "check_memo": "Expert testimony", "description": "VOIDED - Reissued on 2025-11-03: Medical expert testimony", "void_reason": null, "voided_date": "2025-11-03 11:00:27.672060+00:00", "check_number": "Voided", "cleared_date": null, "reference_number": "Voided", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": null}	3500.00	0.00	pending	voided	Check reissued by admin - original voided	151.101.0.223	44
6	CREATED	2025-11-03 11:00:27.676326+00	system	\N	{"payee": "", "amount": "3500.00", "status": "cleared", "case_id": 9, "client_id": 9, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Reversal - Reissue of check #TO PRINT: Medical expert testimony", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-2025-002"}	\N	3500.00	\N	cleared		127.0.0.1	48
7	CREATED	2025-11-03 11:00:27.677668+00	system	\N	{"payee": "Expert Witness Services", "amount": "3500.00", "status": "pending", "case_id": 9, "client_id": 9, "vendor_id": 2, "voided_by": "", "check_memo": "Expert testimony", "description": "Reissue of check #TO PRINT: Medical expert testimony", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-002"}	\N	3500.00	\N	pending		127.0.0.1	49
8	VOIDED	2025-11-03 11:00:44.262293+00	admin	{"payee": "Expert Witness Services", "amount": "1500.00", "status": "pending", "case_id": 7, "client_id": 7, "vendor_id": 2, "voided_by": null, "check_memo": "Expert consultation", "description": "Expert witness consultation", "void_reason": null, "voided_date": null, "check_number": null, "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-02-28", "transaction_type": "WITHDRAWAL", "transaction_number": null}	{"payee": "Expert Witness Services", "amount": "1500.00", "status": "voided", "case_id": 7, "client_id": 7, "vendor_id": 2, "voided_by": null, "check_memo": "Expert consultation", "description": "VOIDED - Reissued on 2025-11-03: Expert witness consultation", "void_reason": null, "voided_date": "2025-11-03 11:00:44.259131+00:00", "check_number": "Voided", "cleared_date": null, "reference_number": "Voided", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": null}	1500.00	0.00	pending	voided	Check reissued by admin - original voided	151.101.0.223	42
9	CREATED	2025-11-03 11:00:44.267935+00	system	\N	{"payee": "", "amount": "1500.00", "status": "cleared", "case_id": 7, "client_id": 7, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Reversal - Reissue of check #TO PRINT: Expert witness consultation", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-2025-003"}	\N	1500.00	\N	cleared		127.0.0.1	50
10	CREATED	2025-11-03 11:00:44.270878+00	system	\N	{"payee": "Expert Witness Services", "amount": "1500.00", "status": "pending", "case_id": 7, "client_id": 7, "vendor_id": 2, "voided_by": "", "check_memo": "Expert consultation", "description": "Reissue of check #TO PRINT: Expert witness consultation", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-003"}	\N	1500.00	\N	pending		127.0.0.1	51
11	CREATED	2025-11-03 11:54:44.871158+00	admin	\N	{"payee": "Court Filing Services", "amount": "34.00", "status": "pending", "case_id": 6, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "ee", "description": "ee", "void_reason": "", "voided_date": null, "check_number": "TO PRINT", "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-004"}	\N	34.00	\N	pending	Transaction created via API	151.101.0.223	52
35	CREATED	2025-11-07 20:14:25.756474+00	system	\N	{"payee": "James Smith", "amount": "123509", "status": "pending", "case_id": 17, "client_id": 16, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for James Smith", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0001", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0001"}	\N	123509.00	\N	pending		127.0.0.1	71
12	VOIDED	2025-11-03 11:54:51.143634+00	admin	{"payee": "Court Filing Services", "amount": "34.00", "status": "pending", "case_id": 6, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "ee", "description": "ee", "void_reason": "", "voided_date": null, "check_number": "TO PRINT", "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-004"}	{"payee": "Court Filing Services", "amount": "34.00", "status": "voided", "case_id": 6, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "ee", "description": "VOIDED - Reissued on 2025-11-03: ee", "void_reason": "", "voided_date": "2025-11-03 11:54:51.140201+00:00", "check_number": "Voided", "cleared_date": null, "reference_number": "Voided", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-004"}	34.00	0.00	pending	voided	Check reissued by admin - original voided	151.101.0.223	52
13	CREATED	2025-11-03 11:54:51.148394+00	system	\N	{"payee": "", "amount": "34.00", "status": "cleared", "case_id": 6, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Reversal - Reissue of check #TO PRINT: ee", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-2025-004"}	\N	34.00	\N	cleared		127.0.0.1	53
14	CREATED	2025-11-03 11:54:51.15078+00	system	\N	{"payee": "Court Filing Services", "amount": "34.00", "status": "pending", "case_id": 6, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "ee", "description": "Reissue of check #TO PRINT: ee", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-005"}	\N	34.00	\N	pending		127.0.0.1	54
15	CREATED	2025-11-03 11:56:22.184882+00	admin	\N	{"payee": "Medical Records Plus", "amount": "3443.00", "status": "pending", "case_id": 6, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "ttttt", "description": "tttt", "void_reason": "", "voided_date": null, "check_number": "TO PRINT", "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-006"}	\N	3443.00	\N	pending	Transaction created via API	151.101.0.223	55
16	UPDATED	2025-11-03 11:56:59.73715+00	system	{"payee": "Medical Records Plus", "amount": "3443.00", "status": "pending", "case_id": 6, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "ttttt", "description": "tttt", "void_reason": "", "voided_date": null, "check_number": "TO PRINT", "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-006"}	{"payee": "Medical Records Plus", "amount": "3443.00", "status": "pending", "case_id": 6, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "ttttt", "description": "tttt", "void_reason": "", "voided_date": null, "check_number": "1045", "cleared_date": null, "reference_number": "1045", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-006"}	3443.00	3443.00	pending	pending		127.0.0.1	55
17	VOIDED	2025-11-05 20:15:04.405076+00	admin	{"payee": "Liability Investigations", "amount": "1800.00", "status": "pending", "case_id": 10, "client_id": 10, "vendor_id": 6, "voided_by": "", "check_memo": "Expert inspection", "description": "Reissue of check #TO PRINT: Facility inspection expert", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-001"}	{"payee": "Liability Investigations", "amount": "1800.00", "status": "voided", "case_id": 10, "client_id": 10, "vendor_id": 6, "voided_by": "", "check_memo": "Expert inspection", "description": "VOIDED - Reissued on 2025-11-05: Reissue of check #TO PRINT: Facility inspection expert", "void_reason": "", "voided_date": "2025-11-05 20:15:04.394236+00:00", "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-03", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-001"}	1800.00	0.00	pending	voided	Check reissued by admin - original voided	50.195.119.125	47
18	CREATED	2025-11-05 20:15:04.426098+00	system	\N	{"payee": "", "amount": "1800.00", "status": "cleared", "case_id": 10, "client_id": 10, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Reversal - Reissue of check #: Reissue of check #TO PRINT: Facility inspection expert", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-05", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-2025-005"}	\N	1800.00	\N	cleared		127.0.0.1	56
19	CREATED	2025-11-05 20:15:04.43385+00	system	\N	{"payee": "Liability Investigations", "amount": "1800.00", "status": "pending", "case_id": 10, "client_id": 10, "vendor_id": 6, "voided_by": "", "check_memo": "Expert inspection", "description": "Reissue of check #: Reissue of check #TO PRINT: Facility inspection expert", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "", "transaction_date": "2025-11-05", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-007"}	\N	1800.00	\N	pending		127.0.0.1	57
20	CREATED	2025-11-06 14:09:50.892231+00	admin	\N	{"payee": "Liberty Mutual Ins CO", "amount": "100000.00", "status": "pending", "case_id": 11, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Settlement", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP", "transaction_date": "2025-11-06", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-2025-006"}	\N	100000.00	\N	pending	Transaction created via API	50.195.119.125	58
21	CREATED	2025-11-06 14:11:59.118604+00	admin	\N	{"payee": "Mohamed Sonbol", "amount": "100000.00", "status": "pending", "case_id": 11, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "Distribution", "description": "Settlement Distribution", "void_reason": "", "voided_date": null, "check_number": "123", "cleared_date": null, "reference_number": "123", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-008"}	\N	100000.00	\N	pending	Transaction created via API	50.195.119.125	59
36	CREATED	2025-11-07 20:14:25.76301+00	system	\N	{"payee": "Mary Johnson", "amount": "56404", "status": "pending", "case_id": 18, "client_id": 17, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Mary Johnson", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0002", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0002"}	\N	56404.00	\N	pending		127.0.0.1	72
22	UPDATED	2025-11-06 14:12:33.996735+00	admin	{"payee": "Mohamed Sonbol", "amount": "100000.00", "status": "pending", "case_id": 11, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "Distribution", "description": "Settlement Distribution", "void_reason": "", "voided_date": null, "check_number": "123", "cleared_date": null, "reference_number": "123", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-008"}	{"payee": "Mohamed Sonbol", "amount": "100000.00", "status": "pending", "case_id": 11, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Settlement Distribution", "void_reason": "", "voided_date": null, "check_number": "TO PRINT", "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-008"}	100000.00	100000.00	pending	pending	Transaction updated via API	50.195.119.125	59
23	CREATED	2025-11-06 14:22:43.861885+00	admin	\N	{"payee": "Liberty Mutual Ins CO", "amount": "500000.00", "status": "pending", "case_id": 12, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Settlement", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "14114411", "transaction_date": "2025-11-06", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-2025-007"}	\N	500000.00	\N	pending	Transaction created via API	50.195.119.125	60
24	CREATED	2025-11-06 14:28:20.345855+00	admin	\N	{"payee": "Mohamed Sonbol", "amount": "5000.00", "status": "pending", "case_id": 11, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "sadas", "void_reason": "", "voided_date": null, "check_number": "124", "cleared_date": null, "reference_number": "124", "transaction_date": "2025-07-01", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-009"}	\N	5000.00	\N	pending	Transaction created via API	50.195.119.125	61
25	CREATED	2025-11-06 14:29:07.180332+00	admin	\N	{"payee": "Mohamed Sonbol", "amount": "5000.00", "status": "pending", "case_id": 11, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "12312", "void_reason": "", "voided_date": null, "check_number": "14125", "cleared_date": null, "reference_number": "14125", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-010"}	\N	5000.00	\N	pending	Transaction created via API	50.195.119.125	62
26	CREATED	2025-11-06 14:34:04.74471+00	admin	\N	{"payee": "Mohamed Sonbol", "amount": "2000.00", "status": "pending", "case_id": 11, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "fsdhfsjdkh", "void_reason": "", "voided_date": null, "check_number": "5484", "cleared_date": null, "reference_number": "5484", "transaction_date": "2025-06-17", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-011"}	\N	2000.00	\N	pending	Transaction created via API	50.195.119.125	63
27	CREATED	2025-11-06 15:18:24.142429+00	admin	\N	{"payee": "Liberty Mutual Ins CO", "amount": "1000000.00", "status": "pending", "case_id": 13, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Settlement", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "1215", "transaction_date": "2022-01-01", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-2025-008"}	\N	1000000.00	\N	pending	Transaction created via API	50.195.119.125	64
28	UPDATED	2025-11-06 17:34:33.967853+00	system	{"payee": "Mohamed Sonbol", "amount": "100000.00", "status": "pending", "case_id": 11, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Settlement Distribution", "void_reason": "", "voided_date": null, "check_number": "TO PRINT", "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-008"}	{"payee": "Mohamed Sonbol", "amount": "100000.00", "status": "pending", "case_id": 11, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Settlement Distribution", "void_reason": "", "voided_date": null, "check_number": "1053", "cleared_date": null, "reference_number": "1053", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-008"}	100000.00	100000.00	pending	pending		127.0.0.1	59
29	CREATED	2025-11-06 18:25:22.372387+00	admin	\N	{"payee": "Bassel Mohamed", "amount": "50000.00", "status": "pending", "case_id": 13, "client_id": 12, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Outside", "void_reason": "", "voided_date": null, "check_number": "125", "cleared_date": null, "reference_number": "125", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-012"}	\N	50000.00	\N	pending	Transaction created via API	50.195.119.125	65
30	CREATED	2025-11-06 18:34:02.66259+00	admin	\N	{"payee": "Deposition Reporting Co", "amount": "600000.00", "status": "pending", "case_id": 12, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "settlement", "void_reason": "", "voided_date": null, "check_number": "1231", "cleared_date": null, "reference_number": "1231", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-013"}	\N	600000.00	\N	pending	Transaction created via API	50.195.119.125	66
31	CREATED	2025-11-06 18:34:35.688261+00	admin	\N	{"payee": "Deposition Reporting Co", "amount": "5000.00", "status": "pending", "case_id": 12, "client_id": 6, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "fsdjfksdlj", "void_reason": "", "voided_date": null, "check_number": "12314", "cleared_date": null, "reference_number": "12314", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-014"}	\N	5000.00	\N	pending	Transaction created via API	50.195.119.125	67
32	CREATED	2025-11-06 18:41:58.359952+00	admin	\N	{"payee": "24/7 Towing & Recovery Services", "amount": "7000.00", "status": "pending", "case_id": 14, "client_id": 13, "vendor_id": null, "voided_by": "", "check_memo": "Aaaa", "description": "Abdo Withdrwal", "void_reason": "", "voided_date": null, "check_number": "Abdo 1500", "cleared_date": null, "reference_number": "Abdo 1500", "transaction_date": "2025-10-31", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-015"}	\N	7000.00	\N	pending	Transaction created via API	45.241.237.226	68
33	CREATED	2025-11-06 18:44:18.301266+00	admin	\N	{"payee": "Bassel Mohamed", "amount": "5000.00", "status": "pending", "case_id": 15, "client_id": 14, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "dd", "void_reason": "", "voided_date": null, "check_number": "dd", "cleared_date": null, "reference_number": "dd", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-016"}	\N	5000.00	\N	pending	Transaction created via API	45.241.237.226	69
34	CREATED	2025-11-06 18:47:57.249544+00	admin	\N	{"payee": "Liberty Mutual Ins CO", "amount": "1000.00", "status": "pending", "case_id": 14, "client_id": 13, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "dd", "void_reason": "", "voided_date": null, "check_number": "R1", "cleared_date": null, "reference_number": "R1", "transaction_date": "2025-11-06", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-017"}	\N	1000.00	\N	pending	Transaction created via API	45.241.237.226	70
37	CREATED	2025-11-07 20:14:25.767417+00	system	\N	{"payee": "John Williams", "amount": "14603", "status": "pending", "case_id": 19, "client_id": 18, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for John Williams", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0003", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0003"}	\N	14603.00	\N	pending		127.0.0.1	73
38	CREATED	2025-11-07 20:14:25.773262+00	system	\N	{"payee": "Patricia Brown", "amount": "56868", "status": "pending", "case_id": 20, "client_id": 19, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Patricia Brown", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0004", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0004"}	\N	56868.00	\N	pending		127.0.0.1	74
39	CREATED	2025-11-07 20:14:25.778332+00	system	\N	{"payee": "Robert Jones", "amount": "118343", "status": "pending", "case_id": 21, "client_id": 20, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Robert Jones", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0005", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0005"}	\N	118343.00	\N	pending		127.0.0.1	75
40	CREATED	2025-11-07 20:14:25.782336+00	system	\N	{"payee": "Jennifer Garcia", "amount": "85393", "status": "pending", "case_id": 22, "client_id": 21, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Jennifer Garcia", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0006", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0006"}	\N	85393.00	\N	pending		127.0.0.1	76
41	CREATED	2025-11-07 20:14:25.786426+00	system	\N	{"payee": "Michael Miller", "amount": "67638", "status": "pending", "case_id": 23, "client_id": 22, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Michael Miller", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0007", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0007"}	\N	67638.00	\N	pending		127.0.0.1	77
42	CREATED	2025-11-07 20:14:25.790257+00	system	\N	{"payee": "Linda Davis", "amount": "8796", "status": "pending", "case_id": 24, "client_id": 23, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Linda Davis", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0008", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0008"}	\N	8796.00	\N	pending		127.0.0.1	78
43	CREATED	2025-11-07 20:14:25.794165+00	system	\N	{"payee": "William Rodriguez", "amount": "102749", "status": "pending", "case_id": 25, "client_id": 24, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for William Rodriguez", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0009", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0009"}	\N	102749.00	\N	pending		127.0.0.1	79
44	CREATED	2025-11-07 20:14:25.798523+00	system	\N	{"payee": "Barbara Martinez", "amount": "44418", "status": "pending", "case_id": 26, "client_id": 25, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Barbara Martinez", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0010", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0010"}	\N	44418.00	\N	pending		127.0.0.1	80
45	CREATED	2025-11-07 20:14:25.802777+00	system	\N	{"payee": "David Hernandez", "amount": "134366", "status": "pending", "case_id": 27, "client_id": 26, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for David Hernandez", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0011", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0011"}	\N	134366.00	\N	pending		127.0.0.1	81
46	CREATED	2025-11-07 20:14:25.806775+00	system	\N	{"payee": "Elizabeth Lopez", "amount": "142978", "status": "pending", "case_id": 28, "client_id": 27, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Elizabeth Lopez", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0012", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0012"}	\N	142978.00	\N	pending		127.0.0.1	82
47	CREATED	2025-11-07 20:14:25.810851+00	system	\N	{"payee": "Richard Gonzalez", "amount": "76365", "status": "pending", "case_id": 29, "client_id": 28, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Richard Gonzalez", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0013", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0013"}	\N	76365.00	\N	pending		127.0.0.1	83
48	CREATED	2025-11-07 20:14:25.815112+00	system	\N	{"payee": "Susan Wilson", "amount": "39970", "status": "pending", "case_id": 30, "client_id": 29, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Susan Wilson", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0014", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0014"}	\N	39970.00	\N	pending		127.0.0.1	84
49	CREATED	2025-11-07 20:14:25.819185+00	system	\N	{"payee": "Joseph Anderson", "amount": "108142", "status": "pending", "case_id": 31, "client_id": 30, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Joseph Anderson", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0015", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0015"}	\N	108142.00	\N	pending		127.0.0.1	85
50	CREATED	2025-11-07 20:14:25.824486+00	system	\N	{"payee": "Jessica Thomas", "amount": "46577", "status": "pending", "case_id": 32, "client_id": 31, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Jessica Thomas", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0016", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0016"}	\N	46577.00	\N	pending		127.0.0.1	86
51	CREATED	2025-11-07 20:14:25.830301+00	system	\N	{"payee": "Thomas Taylor", "amount": "68898", "status": "pending", "case_id": 33, "client_id": 32, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Thomas Taylor", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0017", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0017"}	\N	68898.00	\N	pending		127.0.0.1	87
52	CREATED	2025-11-07 20:14:25.833731+00	system	\N	{"payee": "Sarah Moore", "amount": "51355", "status": "pending", "case_id": 34, "client_id": 33, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Sarah Moore", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0018", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0018"}	\N	51355.00	\N	pending		127.0.0.1	88
53	CREATED	2025-11-07 20:14:25.838411+00	system	\N	{"payee": "Charles Jackson", "amount": "138274", "status": "pending", "case_id": 35, "client_id": 34, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Charles Jackson", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0019", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0019"}	\N	138274.00	\N	pending		127.0.0.1	89
54	CREATED	2025-11-07 20:14:25.843331+00	system	\N	{"payee": "Karen Martin", "amount": "76101", "status": "pending", "case_id": 36, "client_id": 35, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Karen Martin", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0020", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0020"}	\N	76101.00	\N	pending		127.0.0.1	90
55	CREATED	2025-11-07 20:14:25.847755+00	system	\N	{"payee": "Christopher Lee", "amount": "105036", "status": "pending", "case_id": 37, "client_id": 36, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Christopher Lee", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0021", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0021"}	\N	105036.00	\N	pending		127.0.0.1	91
56	CREATED	2025-11-07 20:14:25.852236+00	system	\N	{"payee": "Nancy Perez", "amount": "23016", "status": "pending", "case_id": 38, "client_id": 37, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Nancy Perez", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0022", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0022"}	\N	23016.00	\N	pending		127.0.0.1	92
57	CREATED	2025-11-07 20:14:25.856318+00	system	\N	{"payee": "Daniel Thompson", "amount": "22398", "status": "pending", "case_id": 39, "client_id": 38, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Daniel Thompson", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0023", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0023"}	\N	22398.00	\N	pending		127.0.0.1	93
58	CREATED	2025-11-07 20:14:25.860551+00	system	\N	{"payee": "Lisa White", "amount": "35824", "status": "pending", "case_id": 40, "client_id": 39, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Lisa White", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0024", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0024"}	\N	35824.00	\N	pending		127.0.0.1	94
59	CREATED	2025-11-07 20:14:25.8652+00	system	\N	{"payee": "Matthew Harris", "amount": "72426", "status": "pending", "case_id": 41, "client_id": 40, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Matthew Harris", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0025", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0025"}	\N	72426.00	\N	pending		127.0.0.1	95
60	CREATED	2025-11-07 20:14:25.869652+00	system	\N	{"payee": "Betty Sanchez", "amount": "82908", "status": "pending", "case_id": 42, "client_id": 41, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Betty Sanchez", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0026", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0026"}	\N	82908.00	\N	pending		127.0.0.1	96
61	CREATED	2025-11-07 20:14:25.873692+00	system	\N	{"payee": "Anthony Clark", "amount": "56443", "status": "pending", "case_id": 43, "client_id": 42, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Anthony Clark", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0027", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0027"}	\N	56443.00	\N	pending		127.0.0.1	97
62	CREATED	2025-11-07 20:14:25.877687+00	system	\N	{"payee": "Margaret Ramirez", "amount": "138912", "status": "pending", "case_id": 44, "client_id": 43, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Margaret Ramirez", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0028", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0028"}	\N	138912.00	\N	pending		127.0.0.1	98
63	CREATED	2025-11-07 20:14:25.881967+00	system	\N	{"payee": "Mark Lewis", "amount": "65331", "status": "pending", "case_id": 45, "client_id": 44, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Mark Lewis", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0029", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0029"}	\N	65331.00	\N	pending		127.0.0.1	99
64	CREATED	2025-11-07 20:14:25.886209+00	system	\N	{"payee": "Sandra Robinson", "amount": "29227", "status": "pending", "case_id": 46, "client_id": 45, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Sandra Robinson", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0030", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0030"}	\N	29227.00	\N	pending		127.0.0.1	100
65	CREATED	2025-11-07 20:14:25.890477+00	system	\N	{"payee": "Donald Walker", "amount": "101019", "status": "pending", "case_id": 47, "client_id": 46, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Donald Walker", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0031", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0031"}	\N	101019.00	\N	pending		127.0.0.1	101
66	CREATED	2025-11-07 20:14:25.894545+00	system	\N	{"payee": "Ashley Young", "amount": "129693", "status": "pending", "case_id": 48, "client_id": 47, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Ashley Young", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0032", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0032"}	\N	129693.00	\N	pending		127.0.0.1	102
67	CREATED	2025-11-07 20:14:25.900107+00	system	\N	{"payee": "Steven Allen", "amount": "127196", "status": "pending", "case_id": 49, "client_id": 48, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Steven Allen", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0033", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0033"}	\N	127196.00	\N	pending		127.0.0.1	103
68	CREATED	2025-11-07 20:14:25.904086+00	system	\N	{"payee": "Kimberly King", "amount": "86558", "status": "pending", "case_id": 50, "client_id": 49, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Kimberly King", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0034", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0034"}	\N	86558.00	\N	pending		127.0.0.1	104
69	CREATED	2025-11-07 20:14:25.907471+00	system	\N	{"payee": "Paul Wright", "amount": "73851", "status": "pending", "case_id": 51, "client_id": 50, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Paul Wright", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0035", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0035"}	\N	73851.00	\N	pending		127.0.0.1	105
70	CREATED	2025-11-07 20:14:25.911634+00	system	\N	{"payee": "Emily Scott", "amount": "32087", "status": "pending", "case_id": 52, "client_id": 51, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Emily Scott", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0036", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0036"}	\N	32087.00	\N	pending		127.0.0.1	106
71	CREATED	2025-11-07 20:14:25.916448+00	system	\N	{"payee": "Andrew Torres", "amount": "108104", "status": "pending", "case_id": 53, "client_id": 52, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Andrew Torres", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0037", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0037"}	\N	108104.00	\N	pending		127.0.0.1	107
72	CREATED	2025-11-07 20:14:25.92221+00	system	\N	{"payee": "Donna Nguyen", "amount": "57270", "status": "pending", "case_id": 54, "client_id": 53, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Donna Nguyen", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0038", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0038"}	\N	57270.00	\N	pending		127.0.0.1	108
73	CREATED	2025-11-07 20:14:25.926681+00	system	\N	{"payee": "Joshua Hill", "amount": "18156", "status": "pending", "case_id": 55, "client_id": 54, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Joshua Hill", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0039", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0039"}	\N	18156.00	\N	pending		127.0.0.1	109
74	CREATED	2025-11-07 20:14:25.931967+00	system	\N	{"payee": "Michelle Flores", "amount": "137510", "status": "pending", "case_id": 56, "client_id": 55, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Initial deposit for Michelle Flores", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "DEP-TEST-0040", "transaction_date": "2025-10-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-TEST-0040"}	\N	137510.00	\N	pending		127.0.0.1	110
76	CREATED	2025-11-08 17:50:10.320196+00	admin	\N	{"payee": "Process Servers Inc", "amount": "2000.00", "status": "pending", "case_id": 40, "client_id": 39, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Payemnt1", "void_reason": "", "voided_date": null, "check_number": "TO PRINT", "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-11-08", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-018"}	\N	2000.00	\N	pending	Transaction created via API	172.28.0.1	112
78	CREATED	2025-11-08 17:55:33.79821+00	admin	\N	{"payee": "Medical Records Plus", "amount": "200.00", "status": "pending", "case_id": 33, "client_id": 32, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Treatment Session Visit 1", "void_reason": "", "voided_date": null, "check_number": "", "cleared_date": null, "reference_number": "111", "transaction_date": "2025-11-08", "transaction_type": "DEPOSIT", "transaction_number": "DEPO-2025-009"}	\N	200.00	\N	pending	Transaction created via API	172.28.0.1	114
4066	CREATED	2025-11-14 15:10:16.596221+00	amin	\N	{"payee": "Court Filing Services", "amount": "250.00", "status": "pending", "case_id": 43, "client_id": 42, "vendor_id": null, "voided_by": "", "check_memo": "", "description": "Case fees downpayemnt", "void_reason": "", "voided_date": null, "check_number": "TO PRINT", "cleared_date": null, "reference_number": "TO PRINT", "transaction_date": "2025-11-14", "transaction_type": "WITHDRAWAL", "transaction_number": "WITH-2025-019"}	\N	250.00	\N	pending	Transaction created via API	172.28.0.1	4103
\.


--
-- Data for Name: bank_transactions; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.bank_transactions (id, bank_account_id, transaction_date, post_date, transaction_type, amount, description, reference_number, check_number, bank_reference, bank_category, status, matched_transaction_id, reconciliation_notes, created_at, updated_at, created_by, client_id, case_id, vendor_id, check_memo, cleared_date, transaction_number, item_type, check_is_printed, voided_date, voided_by, void_reason, payee, rec_id, original_transaction_id, original_item_id, data_source, import_batch_id) FROM stdin;
1	1	2024-08-15	\N	DEPOSIT	500000.00	Initial trust account funding	DEP-001	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	Law Firm Capital	\N	\N	\N	webapp	\N
2	1	2024-09-20	\N	DEPOSIT	185000.00	Settlement deposit - Auto Accident Case	DEP-1000	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	1	1	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
3	1	2024-10-05	\N	DEPOSIT	95000.00	Settlement deposit - Slip and Fall Case	DEP-1001	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	2	2	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
4	1	2024-10-20	\N	DEPOSIT	450000.00	Settlement deposit - Medical Malpractice Case	DEP-1002	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	3	3	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
5	1	2024-11-05	\N	DEPOSIT	275000.00	Settlement deposit - Product Liability Case	DEP-1003	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	4	4	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
6	1	2024-11-20	\N	DEPOSIT	150000.00	Settlement deposit - Workers Comp Case	DEP-1004	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	5	5	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
7	1	2024-12-05	\N	DEPOSIT	320000.00	Settlement deposit - Truck Collision Case	DEP-1005	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	6	6	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
8	1	2025-01-10	\N	DEPOSIT	850000.00	Settlement deposit - Wrongful Death Case	DEP-1006	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	7	7	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
9	1	2025-01-25	\N	DEPOSIT	75000.00	Settlement deposit - Dog Bite Case	DEP-1007	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	8	8	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
10	1	2025-02-10	\N	DEPOSIT	425000.00	Settlement deposit - Bicycle Accident Case	DEP-1008	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	9	9	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
11	1	2025-02-25	\N	DEPOSIT	380000.00	Settlement deposit - Nursing Home Case	DEP-1009	\N	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	10	10	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	webapp	\N
12	1	2024-09-25	\N	WITHDRAWAL	350.00	Medical records retrieval	1001	1001	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	1	1	1	Medical records	\N	\N	\N	f	\N	\N	\N	Medical Records Plus	\N	\N	\N	webapp	\N
13	1	2024-10-10	\N	WITHDRAWAL	2500.00	Expert witness testimony	1002	1002	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	1	1	2	Expert testimony	\N	\N	\N	f	\N	\N	\N	Expert Witness Services	\N	\N	\N	webapp	\N
14	1	2024-10-15	\N	WITHDRAWAL	175.00	Court filing fees	1003	1003	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	1	1	3	Filing fees	\N	\N	\N	f	\N	\N	\N	Court Filing Services	\N	\N	\N	webapp	\N
15	1	2024-10-12	\N	WITHDRAWAL	275.00	Medical records	1004	1004	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	2	2	1	Medical records	\N	\N	\N	f	\N	\N	\N	Medical Records Plus	\N	\N	\N	webapp	\N
16	1	2024-10-28	\N	WITHDRAWAL	1200.00	Accident investigation	1005	1005	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	2	2	6	Investigation	\N	\N	\N	f	\N	\N	\N	Liability Investigations	\N	\N	\N	webapp	\N
17	1	2024-11-02	\N	WITHDRAWAL	125.00	Service of process	1006	1006	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	2	2	4	Process service	\N	\N	\N	f	\N	\N	\N	Process Servers Inc	\N	\N	\N	webapp	\N
18	1	2024-10-28	\N	WITHDRAWAL	450.00	Medical examination	1007	1007	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	3	3	1	IME	\N	\N	\N	f	\N	\N	\N	Medical Records Plus	\N	\N	\N	webapp	\N
19	1	2024-11-12	\N	WITHDRAWAL	3500.00	Expert witness consultation	1008	1008	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	3	3	2	Expert consultation	\N	\N	\N	f	\N	\N	\N	Expert Witness Services	\N	\N	\N	webapp	\N
20	1	2024-11-18	\N	WITHDRAWAL	800.00	Deposition transcript	1009	1009	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	3	3	5	Deposition	\N	\N	\N	f	\N	\N	\N	Deposition Reporting Co	\N	\N	\N	webapp	\N
21	1	2024-11-12	\N	WITHDRAWAL	2000.00	Product testing expert	1010	1010	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	4	4	2	Expert testing	\N	\N	\N	f	\N	\N	\N	Expert Witness Services	\N	\N	\N	webapp	\N
22	1	2024-11-25	\N	WITHDRAWAL	175.00	Court filing	1011	1011	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	4	4	3	Filing fees	\N	\N	\N	f	\N	\N	\N	Court Filing Services	\N	\N	\N	webapp	\N
23	1	2024-12-01	\N	WITHDRAWAL	1500.00	Investigation services	1012	1012	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	4	4	6	Investigation	\N	\N	\N	f	\N	\N	\N	Liability Investigations	\N	\N	\N	webapp	\N
24	1	2024-11-28	\N	WITHDRAWAL	300.00	Medical records	1013	1013	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	5	5	1	Medical records	\N	\N	\N	f	\N	\N	\N	Medical Records Plus	\N	\N	\N	webapp	\N
25	1	2024-12-08	\N	WITHDRAWAL	800.00	Deposition services	1014	1014	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	5	5	5	Deposition	\N	\N	\N	f	\N	\N	\N	Deposition Reporting Co	\N	\N	\N	webapp	\N
26	1	2024-12-15	\N	WITHDRAWAL	150.00	Process service	1015	1015	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	5	5	4	Service	\N	\N	\N	f	\N	\N	\N	Process Servers Inc	\N	\N	\N	webapp	\N
27	1	2024-12-12	\N	WITHDRAWAL	400.00	Accident reconstruction	1016	1016	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	6	6	6	Reconstruction	\N	\N	\N	f	\N	\N	\N	Liability Investigations	\N	\N	\N	webapp	\N
28	1	2024-12-22	\N	WITHDRAWAL	2800.00	Trucking industry expert	1017	1017	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	6	6	2	Expert witness	\N	\N	\N	f	\N	\N	\N	Expert Witness Services	\N	\N	\N	webapp	\N
29	1	2024-12-28	\N	WITHDRAWAL	225.00	Court filings	1018	1018	\N	\N	cleared	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	6	6	3	Filing fees	\N	\N	\N	f	\N	\N	\N	Court Filing Services	\N	\N	\N	webapp	\N
43	1	2025-03-01	\N	WITHDRAWAL	2200.00	Accident reconstruction	TO PRINT	\N	\N	\N	pending	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:45:52.45886	\N	8	8	6	Investigation	\N	\N	\N	f	\N	\N	\N	Liability Investigations	\N	\N	\N	webapp	\N
45	1	2025-11-03	\N	WITHDRAWAL	1800.00	VOIDED - Reissued on 2025-11-03: Facility inspection expert	Voided	Voided	\N	\N	voided	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 10:58:24.362965	\N	10	10	6	Expert inspection	\N	\N	\N	f	2025-11-03 10:58:24.362684	\N	\N	Liability Investigations	\N	\N	\N	webapp	\N
46	1	2025-11-03	\N	DEPOSIT	1800.00	Reversal - Reissue of check #TO PRINT: Facility inspection expert			BANK-20251103105824-NEW		cleared	\N		2025-11-03 10:58:24.372407	2025-11-03 10:58:24.372414		10	10	\N		\N	DEPO-2025-001		f	\N				\N	\N	\N	webapp	\N
44	1	2025-11-03	\N	WITHDRAWAL	3500.00	VOIDED - Reissued on 2025-11-03: Medical expert testimony	Voided	Voided	\N	\N	voided	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 11:00:27.672127	\N	9	9	2	Expert testimony	\N	\N	\N	f	2025-11-03 11:00:27.67206	\N	\N	Expert Witness Services	\N	\N	\N	webapp	\N
48	1	2025-11-03	\N	DEPOSIT	3500.00	Reversal - Reissue of check #TO PRINT: Medical expert testimony			BANK-20251103110027-NEW		cleared	\N		2025-11-03 11:00:27.675817	2025-11-03 11:00:27.675821		9	9	\N		\N	DEPO-2025-002		f	\N				\N	\N	\N	webapp	\N
49	1	2025-11-03	\N	WITHDRAWAL	3500.00	Reissue of check #TO PRINT: Medical expert testimony			BANK-20251103110027-NEW		pending	\N		2025-11-03 11:00:27.677251	2025-11-03 11:00:27.677254		9	9	2	Expert testimony	\N	WITH-2025-002	\N	f	\N			Expert Witness Services	\N	\N	\N	webapp	\N
42	1	2025-11-03	\N	WITHDRAWAL	1500.00	VOIDED - Reissued on 2025-11-03: Expert witness consultation	Voided	Voided	\N	\N	voided	\N	\N	2025-11-03 10:45:52.45886	2025-11-03 11:00:44.259311	\N	7	7	2	Expert consultation	\N	\N	\N	f	2025-11-03 11:00:44.259131	\N	\N	Expert Witness Services	\N	\N	\N	webapp	\N
50	1	2025-11-03	\N	DEPOSIT	1500.00	Reversal - Reissue of check #TO PRINT: Expert witness consultation			BANK-20251103110044-NEW		cleared	\N		2025-11-03 11:00:44.266996	2025-11-03 11:00:44.267003		7	7	\N		\N	DEPO-2025-003		f	\N				\N	\N	\N	webapp	\N
51	1	2025-11-03	\N	WITHDRAWAL	1500.00	Reissue of check #TO PRINT: Expert witness consultation			BANK-20251103110044-NEW		pending	\N		2025-11-03 11:00:44.269833	2025-11-03 11:00:44.269839		7	7	2	Expert consultation	\N	WITH-2025-003	\N	f	\N			Expert Witness Services	\N	\N	\N	webapp	\N
52	1	2025-11-03	\N	WITHDRAWAL	34.00	VOIDED - Reissued on 2025-11-03: ee	Voided	Voided	BANK-20251103115444-NEW		voided	\N		2025-11-03 11:54:44.867785	2025-11-03 11:54:51.140295		6	6	\N	ee	\N	WITH-2025-004		f	2025-11-03 11:54:51.140201			Court Filing Services	\N	\N	\N	webapp	\N
53	1	2025-11-03	\N	DEPOSIT	34.00	Reversal - Reissue of check #TO PRINT: ee			BANK-20251103115451-NEW		cleared	\N		2025-11-03 11:54:51.147537	2025-11-03 11:54:51.147544		6	6	\N		\N	DEPO-2025-004		f	\N				\N	\N	\N	webapp	\N
54	1	2025-11-03	\N	WITHDRAWAL	34.00	Reissue of check #TO PRINT: ee			BANK-20251103115451-NEW		pending	\N		2025-11-03 11:54:51.150081	2025-11-03 11:54:51.150088		6	6	\N	ee	\N	WITH-2025-005		f	\N			Court Filing Services	\N	\N	\N	webapp	\N
55	1	2025-11-03	\N	WITHDRAWAL	3443.00	tttt	1045	1045	BANK-20251103115622-NEW		pending	\N		2025-11-03 11:56:22.180475	2025-11-03 11:56:59.734326		6	6	\N	ttttt	\N	WITH-2025-006		f	\N			Medical Records Plus	\N	\N	\N	webapp	\N
4103	1	2025-11-14	\N	WITHDRAWAL	250.00	Case fees downpayemnt	TO PRINT	TO PRINT	BANK-20251114151016-NEW		pending	\N		2025-11-14 15:10:16.589622	2025-11-14 15:10:16.589631		42	43	\N		\N	WITH-2025-019		f	\N			Court Filing Services	\N	\N	\N	webapp	\N
47	1	2025-11-03	\N	WITHDRAWAL	1800.00	VOIDED - Reissued on 2025-11-05: Reissue of check #TO PRINT: Facility inspection expert			BANK-20251103105824-NEW		voided	\N		2025-11-03 10:58:24.37501	2025-11-05 20:15:04.394466		10	10	6	Expert inspection	\N	WITH-2025-001	\N	f	2025-11-05 20:15:04.394236			Liability Investigations	\N	\N	\N	webapp	\N
56	1	2025-11-05	\N	DEPOSIT	1800.00	Reversal - Reissue of check #: Reissue of check #TO PRINT: Facility inspection expert			BANK-20251105201504-NEW		cleared	\N		2025-11-05 20:15:04.421949	2025-11-05 20:15:04.421971		10	10	\N		\N	DEPO-2025-005		f	\N				\N	\N	\N	webapp	\N
57	1	2025-11-05	\N	WITHDRAWAL	1800.00	Reissue of check #: Reissue of check #TO PRINT: Facility inspection expert			BANK-20251105201504-NEW		pending	\N		2025-11-05 20:15:04.431567	2025-11-05 20:15:04.431586		10	10	6	Expert inspection	\N	WITH-2025-007	\N	f	\N			Liability Investigations	\N	\N	\N	webapp	\N
58	1	2025-11-06	\N	DEPOSIT	100000.00	Settlement	DEP		BANK-20251106140950-NEW		pending	\N		2025-11-06 14:09:50.888371	2025-11-06 14:09:50.888382		12	11	\N		\N	DEPO-2025-006		f	\N			Liberty Mutual Ins CO	\N	\N	\N	webapp	\N
60	1	2025-11-06	\N	DEPOSIT	500000.00	Settlement	14114411		BANK-20251106142243-NEW		pending	\N		2025-11-06 14:22:43.857488	2025-11-06 14:22:43.857504		6	12	\N		\N	DEPO-2025-007		f	\N			Liberty Mutual Ins CO	\N	\N	\N	webapp	\N
61	1	2025-07-01	\N	WITHDRAWAL	5000.00	sadas	124	124	BANK-20251106142820-NEW		pending	\N		2025-11-06 14:28:20.339198	2025-11-06 14:28:20.339212		12	11	\N		\N	WITH-2025-009		f	\N			Mohamed Sonbol	\N	\N	\N	webapp	\N
62	1	2025-11-06	\N	WITHDRAWAL	5000.00	12312	14125	14125	BANK-20251106142907-NEW		pending	\N		2025-11-06 14:29:07.176993	2025-11-06 14:29:07.177007		12	11	\N		\N	WITH-2025-010		f	\N			Mohamed Sonbol	\N	\N	\N	webapp	\N
63	1	2025-06-17	\N	WITHDRAWAL	2000.00	fsdhfsjdkh	5484	5484	BANK-20251106143404-NEW		pending	\N		2025-11-06 14:34:04.740346	2025-11-06 14:34:04.740367		12	11	\N		\N	WITH-2025-011		f	\N			Mohamed Sonbol	\N	\N	\N	webapp	\N
64	1	2022-01-01	\N	DEPOSIT	1000000.00	Settlement	1215		BANK-20251106151824-NEW		pending	\N		2025-11-06 15:18:24.137849	2025-11-06 15:18:24.137867		12	13	\N		\N	DEPO-2025-008		f	\N			Liberty Mutual Ins CO	\N	\N	\N	webapp	\N
59	1	2025-11-06	\N	WITHDRAWAL	100000.00	Settlement Distribution	1053	1053	BANK-20251106141159-NEW		pending	\N		2025-11-06 14:11:59.115813	2025-11-06 17:34:33.965716		12	11	\N		\N	WITH-2025-008		f	\N			Mohamed Sonbol	\N	\N	\N	webapp	\N
65	1	2025-11-06	\N	WITHDRAWAL	50000.00	Outside	125	125	BANK-20251106182522-NEW		pending	\N		2025-11-06 18:25:22.369028	2025-11-06 18:25:22.369043		12	13	\N		\N	WITH-2025-012		f	\N			Bassel Mohamed	\N	\N	\N	webapp	\N
66	1	2025-11-06	\N	WITHDRAWAL	600000.00	settlement	1231	1231	BANK-20251106183402-NEW		pending	\N		2025-11-06 18:34:02.657843	2025-11-06 18:34:02.657861		6	12	\N		\N	WITH-2025-013		f	\N			Deposition Reporting Co	\N	\N	\N	webapp	\N
67	1	2025-11-06	\N	WITHDRAWAL	5000.00	fsdjfksdlj	12314	12314	BANK-20251106183435-NEW		pending	\N		2025-11-06 18:34:35.683869	2025-11-06 18:34:35.683885		6	12	\N		\N	WITH-2025-014		f	\N			Deposition Reporting Co	\N	\N	\N	webapp	\N
68	1	2025-10-31	\N	WITHDRAWAL	7000.00	Abdo Withdrwal	Abdo 1500	Abdo 1500	BANK-20251106184158-NEW		pending	\N		2025-11-06 18:41:58.355594	2025-11-06 18:41:58.355611		13	14	\N	Aaaa	\N	WITH-2025-015		f	\N			24/7 Towing & Recovery Services	\N	\N	\N	webapp	\N
69	1	2025-11-06	\N	WITHDRAWAL	5000.00	dd	dd	dd	BANK-20251106184418-NEW		pending	\N		2025-11-06 18:44:18.297932	2025-11-06 18:44:18.297943		14	15	\N		\N	WITH-2025-016		f	\N			Bassel Mohamed	\N	\N	\N	webapp	\N
70	1	2025-11-06	\N	WITHDRAWAL	1000.00	dd	R1	R1	BANK-20251106184757-NEW		pending	\N		2025-11-06 18:47:57.24644	2025-11-06 18:47:57.246454		13	14	\N		\N	WITH-2025-017		f	\N			Liberty Mutual Ins CO	\N	\N	\N	webapp	\N
71	1	2025-10-08	\N	DEPOSIT	123509.00	Initial deposit for James Smith	DEP-TEST-0001		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.752527	2025-11-07 20:14:25.752542		16	17	\N		\N	DEPO-TEST-0001	deposit	f	\N			James Smith	\N	\N	\N	webapp	\N
72	1	2025-10-08	\N	DEPOSIT	56404.00	Initial deposit for Mary Johnson	DEP-TEST-0002		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.761342	2025-11-07 20:14:25.761352		17	18	\N		\N	DEPO-TEST-0002	deposit	f	\N			Mary Johnson	\N	\N	\N	webapp	\N
73	1	2025-10-08	\N	DEPOSIT	14603.00	Initial deposit for John Williams	DEP-TEST-0003		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.765893	2025-11-07 20:14:25.765903		18	19	\N		\N	DEPO-TEST-0003	deposit	f	\N			John Williams	\N	\N	\N	webapp	\N
74	1	2025-10-08	\N	DEPOSIT	56868.00	Initial deposit for Patricia Brown	DEP-TEST-0004		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.771467	2025-11-07 20:14:25.771484		19	20	\N		\N	DEPO-TEST-0004	deposit	f	\N			Patricia Brown	\N	\N	\N	webapp	\N
75	1	2025-10-08	\N	DEPOSIT	118343.00	Initial deposit for Robert Jones	DEP-TEST-0005		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.776693	2025-11-07 20:14:25.776708		20	21	\N		\N	DEPO-TEST-0005	deposit	f	\N			Robert Jones	\N	\N	\N	webapp	\N
76	1	2025-10-08	\N	DEPOSIT	85393.00	Initial deposit for Jennifer Garcia	DEP-TEST-0006		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.781091	2025-11-07 20:14:25.7811		21	22	\N		\N	DEPO-TEST-0006	deposit	f	\N			Jennifer Garcia	\N	\N	\N	webapp	\N
77	1	2025-10-08	\N	DEPOSIT	67638.00	Initial deposit for Michael Miller	DEP-TEST-0007		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.785021	2025-11-07 20:14:25.785036		22	23	\N		\N	DEPO-TEST-0007	deposit	f	\N			Michael Miller	\N	\N	\N	webapp	\N
78	1	2025-10-08	\N	DEPOSIT	8796.00	Initial deposit for Linda Davis	DEP-TEST-0008		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.788914	2025-11-07 20:14:25.788922		23	24	\N		\N	DEPO-TEST-0008	deposit	f	\N			Linda Davis	\N	\N	\N	webapp	\N
79	1	2025-10-08	\N	DEPOSIT	102749.00	Initial deposit for William Rodriguez	DEP-TEST-0009		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.792777	2025-11-07 20:14:25.792786		24	25	\N		\N	DEPO-TEST-0009	deposit	f	\N			William Rodriguez	\N	\N	\N	webapp	\N
80	1	2025-10-08	\N	DEPOSIT	44418.00	Initial deposit for Barbara Martinez	DEP-TEST-0010		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.79705	2025-11-07 20:14:25.79706		25	26	\N		\N	DEPO-TEST-0010	deposit	f	\N			Barbara Martinez	\N	\N	\N	webapp	\N
81	1	2025-10-08	\N	DEPOSIT	134366.00	Initial deposit for David Hernandez	DEP-TEST-0011		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.801402	2025-11-07 20:14:25.80141		26	27	\N		\N	DEPO-TEST-0011	deposit	f	\N			David Hernandez	\N	\N	\N	webapp	\N
82	1	2025-10-08	\N	DEPOSIT	142978.00	Initial deposit for Elizabeth Lopez	DEP-TEST-0012		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.805472	2025-11-07 20:14:25.805481		27	28	\N		\N	DEPO-TEST-0012	deposit	f	\N			Elizabeth Lopez	\N	\N	\N	webapp	\N
83	1	2025-10-08	\N	DEPOSIT	76365.00	Initial deposit for Richard Gonzalez	DEP-TEST-0013		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.809514	2025-11-07 20:14:25.809527		28	29	\N		\N	DEPO-TEST-0013	deposit	f	\N			Richard Gonzalez	\N	\N	\N	webapp	\N
84	1	2025-10-08	\N	DEPOSIT	39970.00	Initial deposit for Susan Wilson	DEP-TEST-0014		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.813523	2025-11-07 20:14:25.813532		29	30	\N		\N	DEPO-TEST-0014	deposit	f	\N			Susan Wilson	\N	\N	\N	webapp	\N
85	1	2025-10-08	\N	DEPOSIT	108142.00	Initial deposit for Joseph Anderson	DEP-TEST-0015		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.817663	2025-11-07 20:14:25.817671		30	31	\N		\N	DEPO-TEST-0015	deposit	f	\N			Joseph Anderson	\N	\N	\N	webapp	\N
86	1	2025-10-08	\N	DEPOSIT	46577.00	Initial deposit for Jessica Thomas	DEP-TEST-0016		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.822599	2025-11-07 20:14:25.822613		31	32	\N		\N	DEPO-TEST-0016	deposit	f	\N			Jessica Thomas	\N	\N	\N	webapp	\N
87	1	2025-10-08	\N	DEPOSIT	68898.00	Initial deposit for Thomas Taylor	DEP-TEST-0017		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.828949	2025-11-07 20:14:25.828957		32	33	\N		\N	DEPO-TEST-0017	deposit	f	\N			Thomas Taylor	\N	\N	\N	webapp	\N
88	1	2025-10-08	\N	DEPOSIT	51355.00	Initial deposit for Sarah Moore	DEP-TEST-0018		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.832555	2025-11-07 20:14:25.832562		33	34	\N		\N	DEPO-TEST-0018	deposit	f	\N			Sarah Moore	\N	\N	\N	webapp	\N
89	1	2025-10-08	\N	DEPOSIT	138274.00	Initial deposit for Charles Jackson	DEP-TEST-0019		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.836556	2025-11-07 20:14:25.836574		34	35	\N		\N	DEPO-TEST-0019	deposit	f	\N			Charles Jackson	\N	\N	\N	webapp	\N
90	1	2025-10-08	\N	DEPOSIT	76101.00	Initial deposit for Karen Martin	DEP-TEST-0020		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.841907	2025-11-07 20:14:25.841917		35	36	\N		\N	DEPO-TEST-0020	deposit	f	\N			Karen Martin	\N	\N	\N	webapp	\N
91	1	2025-10-08	\N	DEPOSIT	105036.00	Initial deposit for Christopher Lee	DEP-TEST-0021		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.846369	2025-11-07 20:14:25.846378		36	37	\N		\N	DEPO-TEST-0021	deposit	f	\N			Christopher Lee	\N	\N	\N	webapp	\N
92	1	2025-10-08	\N	DEPOSIT	23016.00	Initial deposit for Nancy Perez	DEP-TEST-0022		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.850649	2025-11-07 20:14:25.850658		37	38	\N		\N	DEPO-TEST-0022	deposit	f	\N			Nancy Perez	\N	\N	\N	webapp	\N
93	1	2025-10-08	\N	DEPOSIT	22398.00	Initial deposit for Daniel Thompson	DEP-TEST-0023		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.855069	2025-11-07 20:14:25.855079		38	39	\N		\N	DEPO-TEST-0023	deposit	f	\N			Daniel Thompson	\N	\N	\N	webapp	\N
94	1	2025-10-08	\N	DEPOSIT	35824.00	Initial deposit for Lisa White	DEP-TEST-0024		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.858992	2025-11-07 20:14:25.859001		39	40	\N		\N	DEPO-TEST-0024	deposit	f	\N			Lisa White	\N	\N	\N	webapp	\N
95	1	2025-10-08	\N	DEPOSIT	72426.00	Initial deposit for Matthew Harris	DEP-TEST-0025		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.863822	2025-11-07 20:14:25.863831		40	41	\N		\N	DEPO-TEST-0025	deposit	f	\N			Matthew Harris	\N	\N	\N	webapp	\N
96	1	2025-10-08	\N	DEPOSIT	82908.00	Initial deposit for Betty Sanchez	DEP-TEST-0026		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.868331	2025-11-07 20:14:25.86834		41	42	\N		\N	DEPO-TEST-0026	deposit	f	\N			Betty Sanchez	\N	\N	\N	webapp	\N
97	1	2025-10-08	\N	DEPOSIT	56443.00	Initial deposit for Anthony Clark	DEP-TEST-0027		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.872462	2025-11-07 20:14:25.87247		42	43	\N		\N	DEPO-TEST-0027	deposit	f	\N			Anthony Clark	\N	\N	\N	webapp	\N
98	1	2025-10-08	\N	DEPOSIT	138912.00	Initial deposit for Margaret Ramirez	DEP-TEST-0028		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.876448	2025-11-07 20:14:25.876457		43	44	\N		\N	DEPO-TEST-0028	deposit	f	\N			Margaret Ramirez	\N	\N	\N	webapp	\N
99	1	2025-10-08	\N	DEPOSIT	65331.00	Initial deposit for Mark Lewis	DEP-TEST-0029		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.880609	2025-11-07 20:14:25.880618		44	45	\N		\N	DEPO-TEST-0029	deposit	f	\N			Mark Lewis	\N	\N	\N	webapp	\N
100	1	2025-10-08	\N	DEPOSIT	29227.00	Initial deposit for Sandra Robinson	DEP-TEST-0030		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.884773	2025-11-07 20:14:25.884783		45	46	\N		\N	DEPO-TEST-0030	deposit	f	\N			Sandra Robinson	\N	\N	\N	webapp	\N
101	1	2025-10-08	\N	DEPOSIT	101019.00	Initial deposit for Donald Walker	DEP-TEST-0031		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.889182	2025-11-07 20:14:25.889191		46	47	\N		\N	DEPO-TEST-0031	deposit	f	\N			Donald Walker	\N	\N	\N	webapp	\N
102	1	2025-10-08	\N	DEPOSIT	129693.00	Initial deposit for Ashley Young	DEP-TEST-0032		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.893144	2025-11-07 20:14:25.893153		47	48	\N		\N	DEPO-TEST-0032	deposit	f	\N			Ashley Young	\N	\N	\N	webapp	\N
103	1	2025-10-08	\N	DEPOSIT	127196.00	Initial deposit for Steven Allen	DEP-TEST-0033		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.898427	2025-11-07 20:14:25.898448		48	49	\N		\N	DEPO-TEST-0033	deposit	f	\N			Steven Allen	\N	\N	\N	webapp	\N
104	1	2025-10-08	\N	DEPOSIT	86558.00	Initial deposit for Kimberly King	DEP-TEST-0034		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.902682	2025-11-07 20:14:25.902689		49	50	\N		\N	DEPO-TEST-0034	deposit	f	\N			Kimberly King	\N	\N	\N	webapp	\N
105	1	2025-10-08	\N	DEPOSIT	73851.00	Initial deposit for Paul Wright	DEP-TEST-0035		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.906452	2025-11-07 20:14:25.906459		50	51	\N		\N	DEPO-TEST-0035	deposit	f	\N			Paul Wright	\N	\N	\N	webapp	\N
106	1	2025-10-08	\N	DEPOSIT	32087.00	Initial deposit for Emily Scott	DEP-TEST-0036		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.910143	2025-11-07 20:14:25.910154		51	52	\N		\N	DEPO-TEST-0036	deposit	f	\N			Emily Scott	\N	\N	\N	webapp	\N
107	1	2025-10-08	\N	DEPOSIT	108104.00	Initial deposit for Andrew Torres	DEP-TEST-0037		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.914839	2025-11-07 20:14:25.91485		52	53	\N		\N	DEPO-TEST-0037	deposit	f	\N			Andrew Torres	\N	\N	\N	webapp	\N
108	1	2025-10-08	\N	DEPOSIT	57270.00	Initial deposit for Donna Nguyen	DEP-TEST-0038		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.920631	2025-11-07 20:14:25.920642		53	54	\N		\N	DEPO-TEST-0038	deposit	f	\N			Donna Nguyen	\N	\N	\N	webapp	\N
109	1	2025-10-08	\N	DEPOSIT	18156.00	Initial deposit for Joshua Hill	DEP-TEST-0039		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.925125	2025-11-07 20:14:25.925143		54	55	\N		\N	DEPO-TEST-0039	deposit	f	\N			Joshua Hill	\N	\N	\N	webapp	\N
110	1	2025-10-08	\N	DEPOSIT	137510.00	Initial deposit for Michelle Flores	DEP-TEST-0040		BANK-20251107201425-NEW		pending	\N		2025-11-07 20:14:25.930433	2025-11-07 20:14:25.930448		55	56	\N		\N	DEPO-TEST-0040	deposit	f	\N			Michelle Flores	\N	\N	\N	webapp	\N
112	1	2025-11-08	\N	WITHDRAWAL	2000.00	Payemnt1	TO PRINT	TO PRINT	BANK-20251108175010-NEW		pending	\N		2025-11-08 17:50:10.315533	2025-11-08 17:50:10.315543		39	40	\N		\N	WITH-2025-018		f	\N			Process Servers Inc	\N	\N	\N	webapp	\N
114	1	2025-11-08	\N	DEPOSIT	200.00	Treatment Session Visit 1	111		BANK-20251108175533-NEW		pending	\N		2025-11-08 17:55:33.794509	2025-11-08 17:55:33.79452		32	33	\N		\N	DEPO-2025-009		f	\N			Medical Records Plus	\N	\N	\N	webapp	\N
\.


--
-- Data for Name: case_number_counter; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.case_number_counter (id, last_number) FROM stdin;
1	13
\.


--
-- Data for Name: cases; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.cases (id, case_number, client_id, case_description, case_amount, case_status, opened_date, closed_date, is_active, created_at, updated_at, case_title, data_source, import_batch_id) FROM stdin;
1	INS-2025-1000	1	T-bone collision at intersection, multiple injuries including whiplash and back injury. Strong liability case.	185000.00	Pending Settlement	2024-09-01	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Auto Accident - Rear-End Collision (Personal Injury)	webapp	\N
2	INS-2025-1001	2	Slip and fall at shopping mall, resulting in back injury and ongoing treatment. Clear premises defect.	95000.00	Pending Settlement	2024-09-15	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Slip and Fall - Commercial Property (Premises Liability)	webapp	\N
3	INS-2025-1002	3	Wrong-site surgery resulting in permanent disability and additional surgeries. Extensive expert testimony required.	450000.00	Pending Settlement	2024-09-30	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Medical Malpractice - Surgical Error	webapp	\N
4	INS-2025-1003	4	Manufacturing defect in industrial equipment causing workplace injury. Multiple defendants involved.	275000.00	Pending Settlement	2024-10-15	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Product Liability - Defective Equipment	webapp	\N
5	INS-2025-1004	5	Fall from scaffolding resulting in multiple fractures and long-term disability. Safety violation documented.	150000.00	Pending Settlement	2024-10-30	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Workers Compensation - Construction Accident	webapp	\N
6	INS-2025-1005	6	Commercial truck accident on highway with catastrophic injuries. Commercial policy limits in play.	320000.00	Pending Settlement	2024-11-15	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Motor Vehicle - Truck Collision (Personal Injury)	webapp	\N
7	INS-2025-1006	7	Fatal workplace accident due to safety violations and negligent supervision. Pending settlement distribution.	850000.00	Open	2024-12-01	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Wrongful Death - Industrial Accident	webapp	\N
8	INS-2025-1007	8	Severe dog attack resulting in scarring and psychological trauma. Homeowner insurance coverage available.	75000.00	Open	2024-12-15	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Dog Bite - Homeowner Liability (Premises Liability)	webapp	\N
9	INS-2025-1008	9	Cyclist struck by vehicle resulting in traumatic brain injury. Ongoing medical treatment required.	425000.00	Open	2025-01-05	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Bicycle Accident - Vehicle Collision (Personal Injury)	webapp	\N
10	INS-2025-1009	10	Neglect and abuse at assisted living facility causing severe harm. Facility violations documented.	380000.00	Open	2025-01-20	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	Nursing Home Negligence (Elder Abuse)	webapp	\N
11	CASE-000001	12		\N	Open	2025-11-06	\N	t	2025-11-06 14:09:06.931316+00	2025-11-06 14:09:06.931334+00	W/C	webapp	\N
12	CASE-000002	6		\N	Open	\N	\N	t	2025-11-06 14:21:57.265659+00	2025-11-06 14:21:57.26568+00	Auto-3/11/2022	webapp	\N
13	CASE-000003	12		\N	Open	\N	\N	t	2025-11-06 15:17:44.994255+00	2025-11-06 15:17:44.994272+00	Litigation	webapp	\N
14	CASE-000004	13	dd	\N	Open	2025-11-06	\N	t	2025-11-06 18:41:49.739012+00	2025-11-06 18:41:49.739028+00	new	webapp	\N
15	CASE-000005	14	fff	\N	Open	2025-11-06	\N	t	2025-11-06 18:43:24.523385+00	2025-11-06 18:43:24.523404+00	new 2	webapp	\N
17	CASE-TEST-0015	16	Test case for pagination testing	\N	Open	2025-08-17	\N	t	2025-11-07 20:14:25.602659+00	2025-11-07 20:14:25.602668+00	Personal Injury - Auto Accident - Smith	webapp	\N
18	CASE-TEST-0016	17	Test case for pagination testing	\N	Open	2024-11-21	\N	t	2025-11-07 20:14:25.605674+00	2025-11-07 20:14:25.60569+00	Medical Malpractice - Johnson	webapp	\N
19	CASE-TEST-0017	18	Test case for pagination testing	\N	Open	2025-02-23	\N	t	2025-11-07 20:14:25.607923+00	2025-11-07 20:14:25.607937+00	Workers Compensation - Williams	webapp	\N
20	CASE-TEST-0018	19	Test case for pagination testing	\N	Open	2024-12-07	\N	t	2025-11-07 20:14:25.610309+00	2025-11-07 20:14:25.610325+00	Slip and Fall - Brown	webapp	\N
21	CASE-TEST-0019	20	Test case for pagination testing	\N	Open	2025-05-15	\N	t	2025-11-07 20:14:25.612798+00	2025-11-07 20:14:25.612806+00	Product Liability - Jones	webapp	\N
22	CASE-TEST-0020	21	Test case for pagination testing	\N	Open	2025-03-29	\N	t	2025-11-07 20:14:25.615082+00	2025-11-07 20:14:25.61509+00	Wrongful Death - Garcia	webapp	\N
23	CASE-TEST-0021	22	Test case for pagination testing	\N	Open	2024-12-14	\N	t	2025-11-07 20:14:25.617454+00	2025-11-07 20:14:25.617461+00	Dog Bite - Miller	webapp	\N
24	CASE-TEST-0022	23	Test case for pagination testing	\N	Open	2025-05-26	\N	t	2025-11-07 20:14:25.619684+00	2025-11-07 20:14:25.619701+00	Construction Accident - Davis	webapp	\N
25	CASE-TEST-0023	24	Test case for pagination testing	\N	Open	2025-07-16	\N	t	2025-11-07 20:14:25.622531+00	2025-11-07 20:14:25.622542+00	Nursing Home Negligence - Rodriguez	webapp	\N
26	CASE-TEST-0024	25	Test case for pagination testing	\N	Open	2025-01-31	\N	t	2025-11-07 20:14:25.625389+00	2025-11-07 20:14:25.625396+00	Premises Liability - Martinez	webapp	\N
27	CASE-TEST-0025	26	Test case for pagination testing	\N	Open	2025-04-15	\N	t	2025-11-07 20:14:25.627554+00	2025-11-07 20:14:25.627567+00	Personal Injury - Auto Accident - Hernandez	webapp	\N
28	CASE-TEST-0026	27	Test case for pagination testing	\N	Open	2025-08-06	\N	t	2025-11-07 20:14:25.629637+00	2025-11-07 20:14:25.62965+00	Medical Malpractice - Lopez	webapp	\N
29	CASE-TEST-0027	28	Test case for pagination testing	\N	Open	2025-06-08	\N	t	2025-11-07 20:14:25.631841+00	2025-11-07 20:14:25.631855+00	Workers Compensation - Gonzalez	webapp	\N
30	CASE-TEST-0028	29	Test case for pagination testing	\N	Open	2025-08-24	\N	t	2025-11-07 20:14:25.634098+00	2025-11-07 20:14:25.634106+00	Slip and Fall - Wilson	webapp	\N
31	CASE-TEST-0029	30	Test case for pagination testing	\N	Open	2025-02-25	\N	t	2025-11-07 20:14:25.636454+00	2025-11-07 20:14:25.636468+00	Product Liability - Anderson	webapp	\N
32	CASE-TEST-0030	31	Test case for pagination testing	\N	Open	2025-07-03	\N	t	2025-11-07 20:14:25.638965+00	2025-11-07 20:14:25.638979+00	Wrongful Death - Thomas	webapp	\N
33	CASE-TEST-0031	32	Test case for pagination testing	\N	Open	2025-02-10	\N	t	2025-11-07 20:14:25.641205+00	2025-11-07 20:14:25.641219+00	Dog Bite - Taylor	webapp	\N
34	CASE-TEST-0032	33	Test case for pagination testing	\N	Open	2025-08-27	\N	t	2025-11-07 20:14:25.643295+00	2025-11-07 20:14:25.643303+00	Construction Accident - Moore	webapp	\N
35	CASE-TEST-0033	34	Test case for pagination testing	\N	Open	2025-03-31	\N	t	2025-11-07 20:14:25.645315+00	2025-11-07 20:14:25.645323+00	Nursing Home Negligence - Jackson	webapp	\N
36	CASE-TEST-0034	35	Test case for pagination testing	\N	Open	2025-07-12	\N	t	2025-11-07 20:14:25.647324+00	2025-11-07 20:14:25.647331+00	Premises Liability - Martin	webapp	\N
37	CASE-TEST-0035	36	Test case for pagination testing	\N	Open	2024-11-26	\N	t	2025-11-07 20:14:25.649389+00	2025-11-07 20:14:25.649402+00	Personal Injury - Auto Accident - Lee	webapp	\N
38	CASE-TEST-0036	37	Test case for pagination testing	\N	Open	2025-07-28	\N	t	2025-11-07 20:14:25.651379+00	2025-11-07 20:14:25.651394+00	Medical Malpractice - Perez	webapp	\N
39	CASE-TEST-0037	38	Test case for pagination testing	\N	Open	2025-04-13	\N	t	2025-11-07 20:14:25.653919+00	2025-11-07 20:14:25.653934+00	Workers Compensation - Thompson	webapp	\N
41	CASE-TEST-0039	40	Test case for pagination testing	\N	Open	2024-11-18	\N	t	2025-11-07 20:14:25.65831+00	2025-11-07 20:14:25.65832+00	Product Liability - Harris	webapp	\N
42	CASE-TEST-0040	41	Test case for pagination testing	\N	Open	2025-03-28	\N	t	2025-11-07 20:14:25.660337+00	2025-11-07 20:14:25.660345+00	Wrongful Death - Sanchez	webapp	\N
43	CASE-TEST-0041	42	Test case for pagination testing	\N	Open	2024-12-13	\N	t	2025-11-07 20:14:25.662452+00	2025-11-07 20:14:25.66246+00	Dog Bite - Clark	webapp	\N
44	CASE-TEST-0042	43	Test case for pagination testing	\N	Open	2025-08-18	\N	t	2025-11-07 20:14:25.664408+00	2025-11-07 20:14:25.664417+00	Construction Accident - Ramirez	webapp	\N
45	CASE-TEST-0043	44	Test case for pagination testing	\N	Open	2025-08-18	\N	t	2025-11-07 20:14:25.666445+00	2025-11-07 20:14:25.666454+00	Nursing Home Negligence - Lewis	webapp	\N
46	CASE-TEST-0044	45	Test case for pagination testing	\N	Open	2025-09-27	\N	t	2025-11-07 20:14:25.668534+00	2025-11-07 20:14:25.668551+00	Premises Liability - Robinson	webapp	\N
47	CASE-TEST-0045	46	Test case for pagination testing	\N	Open	2025-08-04	\N	t	2025-11-07 20:14:25.670914+00	2025-11-07 20:14:25.670923+00	Personal Injury - Auto Accident - Walker	webapp	\N
48	CASE-TEST-0046	47	Test case for pagination testing	\N	Open	2025-06-12	\N	t	2025-11-07 20:14:25.673118+00	2025-11-07 20:14:25.673127+00	Medical Malpractice - Young	webapp	\N
49	CASE-TEST-0047	48	Test case for pagination testing	\N	Open	2025-07-20	\N	t	2025-11-07 20:14:25.675312+00	2025-11-07 20:14:25.67532+00	Workers Compensation - Allen	webapp	\N
50	CASE-TEST-0048	49	Test case for pagination testing	\N	Open	2025-05-01	\N	t	2025-11-07 20:14:25.677373+00	2025-11-07 20:14:25.67738+00	Slip and Fall - King	webapp	\N
51	CASE-TEST-0049	50	Test case for pagination testing	\N	Open	2024-12-03	\N	t	2025-11-07 20:14:25.679414+00	2025-11-07 20:14:25.679422+00	Product Liability - Wright	webapp	\N
52	CASE-TEST-0050	51	Test case for pagination testing	\N	Open	2025-08-23	\N	t	2025-11-07 20:14:25.681547+00	2025-11-07 20:14:25.681555+00	Wrongful Death - Scott	webapp	\N
53	CASE-TEST-0051	52	Test case for pagination testing	\N	Open	2025-07-11	\N	t	2025-11-07 20:14:25.683523+00	2025-11-07 20:14:25.683531+00	Dog Bite - Torres	webapp	\N
54	CASE-TEST-0052	53	Test case for pagination testing	\N	Open	2025-08-19	\N	t	2025-11-07 20:14:25.685322+00	2025-11-07 20:14:25.68533+00	Construction Accident - Nguyen	webapp	\N
55	CASE-TEST-0053	54	Test case for pagination testing	\N	Open	2025-01-27	\N	t	2025-11-07 20:14:25.687645+00	2025-11-07 20:14:25.687662+00	Nursing Home Negligence - Hill	webapp	\N
56	CASE-TEST-0054	55	Test case for pagination testing	\N	Open	2025-04-13	\N	t	2025-11-07 20:14:25.690232+00	2025-11-07 20:14:25.690242+00	Premises Liability - Flores	webapp	\N
57	CASE-TEST-0055	56	Test case for pagination testing	\N	Open	2025-03-13	\N	t	2025-11-07 20:14:25.692492+00	2025-11-07 20:14:25.692501+00	Personal Injury - Auto Accident - Green	webapp	\N
58	CASE-TEST-0056	57	Test case for pagination testing	\N	Open	2025-08-22	\N	t	2025-11-07 20:14:25.69525+00	2025-11-07 20:14:25.695258+00	Medical Malpractice - Adams	webapp	\N
59	CASE-TEST-0057	58	Test case for pagination testing	\N	Open	2025-02-05	\N	t	2025-11-07 20:14:25.697564+00	2025-11-07 20:14:25.697573+00	Workers Compensation - Nelson	webapp	\N
60	CASE-TEST-0058	59	Test case for pagination testing	\N	Open	2024-11-18	\N	t	2025-11-07 20:14:25.699737+00	2025-11-07 20:14:25.699746+00	Slip and Fall - Baker	webapp	\N
61	CASE-TEST-0059	60	Test case for pagination testing	\N	Open	2025-06-02	\N	t	2025-11-07 20:14:25.702179+00	2025-11-07 20:14:25.702188+00	Product Liability - Hall	webapp	\N
62	CASE-TEST-0060	61	Test case for pagination testing	\N	Open	2024-12-17	\N	t	2025-11-07 20:14:25.704367+00	2025-11-07 20:14:25.704376+00	Wrongful Death - Rivera	webapp	\N
63	CASE-TEST-0061	62	Test case for pagination testing	\N	Open	2025-01-27	\N	t	2025-11-07 20:14:25.706468+00	2025-11-07 20:14:25.706477+00	Dog Bite - Campbell	webapp	\N
64	CASE-TEST-0062	63	Test case for pagination testing	\N	Open	2025-02-06	\N	t	2025-11-07 20:14:25.708567+00	2025-11-07 20:14:25.708577+00	Construction Accident - Mitchell	webapp	\N
65	CASE-TEST-0063	64	Test case for pagination testing	\N	Open	2025-08-12	\N	t	2025-11-07 20:14:25.710711+00	2025-11-07 20:14:25.71072+00	Nursing Home Negligence - Carter	webapp	\N
66	CASE-TEST-0064	65	Test case for pagination testing	\N	Open	2025-07-12	\N	t	2025-11-07 20:14:25.713544+00	2025-11-07 20:14:25.713554+00	Premises Liability - Roberts	webapp	\N
67	CASE-TEST-0065	66	Test case for pagination testing	\N	Open	2025-09-09	\N	t	2025-11-07 20:14:25.715744+00	2025-11-07 20:14:25.715754+00	Personal Injury - Auto Accident - Gomez	webapp	\N
68	CASE-TEST-0066	67	Test case for pagination testing	\N	Open	2025-08-14	\N	t	2025-11-07 20:14:25.718046+00	2025-11-07 20:14:25.718056+00	Medical Malpractice - Phillips	webapp	\N
69	CASE-TEST-0067	68	Test case for pagination testing	\N	Open	2024-12-14	\N	t	2025-11-07 20:14:25.720321+00	2025-11-07 20:14:25.72033+00	Workers Compensation - Evans	webapp	\N
70	CASE-TEST-0068	69	Test case for pagination testing	\N	Open	2025-04-01	\N	t	2025-11-07 20:14:25.722455+00	2025-11-07 20:14:25.72247+00	Slip and Fall - Turner	webapp	\N
71	CASE-TEST-0069	70	Test case for pagination testing	\N	Open	2024-12-01	\N	t	2025-11-07 20:14:25.724988+00	2025-11-07 20:14:25.724997+00	Product Liability - Diaz	webapp	\N
72	CASE-TEST-0070	71	Test case for pagination testing	\N	Open	2025-09-01	\N	t	2025-11-07 20:14:25.72729+00	2025-11-07 20:14:25.727299+00	Wrongful Death - Parker	webapp	\N
73	CASE-TEST-0071	72	Test case for pagination testing	\N	Open	2025-04-09	\N	t	2025-11-07 20:14:25.729387+00	2025-11-07 20:14:25.729396+00	Dog Bite - Cruz	webapp	\N
74	CASE-TEST-0072	73	Test case for pagination testing	\N	Open	2025-06-11	\N	t	2025-11-07 20:14:25.731636+00	2025-11-07 20:14:25.731645+00	Construction Accident - Edwards	webapp	\N
75	CASE-TEST-0073	74	Test case for pagination testing	\N	Open	2025-03-11	\N	t	2025-11-07 20:14:25.733841+00	2025-11-07 20:14:25.73385+00	Nursing Home Negligence - Collins	webapp	\N
76	CASE-TEST-0074	75	Test case for pagination testing	\N	Open	2025-02-20	\N	t	2025-11-07 20:14:25.736329+00	2025-11-07 20:14:25.736339+00	Premises Liability - Reyes	webapp	\N
77	CASE-TEST-0075	76	Test case for pagination testing	\N	Open	2025-08-27	\N	t	2025-11-07 20:14:25.738959+00	2025-11-07 20:14:25.738974+00	Personal Injury - Auto Accident - Stewart	webapp	\N
78	CASE-TEST-0076	77	Test case for pagination testing	\N	Open	2025-02-12	\N	t	2025-11-07 20:14:25.741339+00	2025-11-07 20:14:25.741354+00	Medical Malpractice - Morris	webapp	\N
79	CASE-TEST-0077	78	Test case for pagination testing	\N	Open	2025-02-19	\N	t	2025-11-07 20:14:25.743318+00	2025-11-07 20:14:25.743327+00	Workers Compensation - Morales	webapp	\N
80	CASE-TEST-0078	79	Test case for pagination testing	\N	Open	2024-12-12	\N	t	2025-11-07 20:14:25.745475+00	2025-11-07 20:14:25.745485+00	Slip and Fall - Murphy	webapp	\N
81	CASE-TEST-0079	80	Test case for pagination testing	\N	Open	2025-04-09	\N	t	2025-11-07 20:14:25.747377+00	2025-11-07 20:14:25.747387+00	Product Liability - Cook	webapp	\N
87	CASE-000011	57	This is a closed case for testing closing date display	\N	Closed	2025-08-10	2025-10-24	t	2025-11-08 15:44:05.843883+00	2025-11-08 15:44:05.843902+00	Test Closed Case - MFLP-35	webapp	\N
40	CASE-TEST-0038	39	Test case for pagination testing	\N	Closed	2025-07-29	2025-11-08	t	2025-11-07 20:14:25.656214+00	2025-11-08 17:48:59.861638+00	Slip and Fall - White	webapp	\N
\.


--
-- Data for Name: check_sequences; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.check_sequences (id, bank_account_id, next_check_number, last_assigned_number, last_assigned_date) FROM stdin;
1	1	1054	1053	2025-11-06 17:34:33.958618+00
\.


--
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.clients (id, client_number, first_name, last_name, email, phone, address, city, state, zip_code, is_active, created_at, updated_at, client_type, trust_account_status, data_source, import_batch_id) FROM stdin;
1	C-2025-001	Sarah	Johnson	sarah.johnson@email.com	(555) 123-4567	1000 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
2	C-2025-002	Michael	Rodriguez	m.rodriguez@email.com	(555) 234-5678	1001 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
3	C-2025-003	Emily	Chen	emily.chen@email.com	(555) 345-6789	1002 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
4	C-2025-004	James	Williams	james.w@email.com	(555) 456-7890	1003 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
5	C-2025-005	Maria	Garcia	maria.garcia@email.com	(555) 567-8901	1004 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
7	C-2025-007	Jennifer	Martinez	j.martinez@email.com	(555) 789-0123	1006 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
8	C-2025-008	Robert	Anderson	robert.a@email.com	(555) 890-1234	1007 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
9	C-2025-009	Lisa	Taylor	lisa.taylor@email.com	(555) 901-2345	1008 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
10	C-2025-010	Thomas	White	thomas.white@email.com	(555) 012-3456	1009 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
12	CL-2027	Mohamed	Sonbol							t	2025-11-06 14:08:23.983866+00	2025-11-06 14:08:23.983883+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
6	C-2025-006	David	Thompson	d.thompson@email.com	(555) 678-9012	1005 Main Street	New York	NY	10001	t	2025-11-03 10:45:52.45886+00	2025-11-06 18:20:48.87104+00	individual	ACTIVE_WITH_FUNDS	webapp	\N
14	CL-2029	abdo	sa							t	2025-11-06 18:43:07.687927+00	2025-11-06 18:43:07.687951+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
15	CL-2030	Mohamed	Ahmed							t	2025-11-06 19:23:00.980222+00	2025-11-06 19:23:00.980246+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
16	TEST-0015	James	Smith	james.smith0@testclient.com	(555) 100-1000	100 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.600384+00	2025-11-07 20:14:25.600401+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
17	TEST-0016	Mary	Johnson	mary.johnson1@testclient.com	(555) 101-1001	101 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.604348+00	2025-11-07 20:14:25.604358+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
18	TEST-0017	John	Williams	john.williams2@testclient.com	(555) 102-1002	102 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.606839+00	2025-11-07 20:14:25.606854+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
19	TEST-0018	Patricia	Brown	patricia.brown3@testclient.com	(555) 103-1003	103 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.609079+00	2025-11-07 20:14:25.609113+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
20	TEST-0019	Robert	Jones	robert.jones4@testclient.com	(555) 104-1004	104 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.611563+00	2025-11-07 20:14:25.611576+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
21	TEST-0020	Jennifer	Garcia	jennifer.garcia5@testclient.com	(555) 105-1005	105 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.613906+00	2025-11-07 20:14:25.613914+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
22	TEST-0021	Michael	Miller	michael.miller6@testclient.com	(555) 106-1006	106 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.616181+00	2025-11-07 20:14:25.61619+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
23	TEST-0022	Linda	Davis	linda.davis7@testclient.com	(555) 107-1007	107 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.618463+00	2025-11-07 20:14:25.618471+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
24	TEST-0023	William	Rodriguez	william.rodriguez8@testclient.com	(555) 108-1008	108 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.62111+00	2025-11-07 20:14:25.621122+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
25	TEST-0024	Barbara	Martinez	barbara.martinez9@testclient.com	(555) 109-1009	109 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.624069+00	2025-11-07 20:14:25.62408+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
26	TEST-0025	David	Hernandez	david.hernandez10@testclient.com	(555) 110-1010	110 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.626506+00	2025-11-07 20:14:25.626515+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
27	TEST-0026	Elizabeth	Lopez	elizabeth.lopez11@testclient.com	(555) 111-1011	111 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.628584+00	2025-11-07 20:14:25.628597+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
28	TEST-0027	Richard	Gonzalez	richard.gonzalez12@testclient.com	(555) 112-1012	112 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.630644+00	2025-11-07 20:14:25.630657+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
29	TEST-0028	Susan	Wilson	susan.wilson13@testclient.com	(555) 113-1013	113 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.632946+00	2025-11-07 20:14:25.63296+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
30	TEST-0029	Joseph	Anderson	joseph.anderson14@testclient.com	(555) 114-1014	114 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.635151+00	2025-11-07 20:14:25.635166+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
31	TEST-0030	Jessica	Thomas	jessica.thomas15@testclient.com	(555) 115-1015	115 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.63759+00	2025-11-07 20:14:25.637606+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
32	TEST-0031	Thomas	Taylor	thomas.taylor16@testclient.com	(555) 116-1016	116 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.640066+00	2025-11-07 20:14:25.640076+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
33	TEST-0032	Sarah	Moore	sarah.moore17@testclient.com	(555) 117-1017	117 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.642312+00	2025-11-07 20:14:25.642323+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
34	TEST-0033	Charles	Jackson	charles.jackson18@testclient.com	(555) 118-1018	118 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.644284+00	2025-11-07 20:14:25.644292+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
35	TEST-0034	Karen	Martin	karen.martin19@testclient.com	(555) 119-1019	119 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.646298+00	2025-11-07 20:14:25.646306+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
36	TEST-0035	Christopher	Lee	christopher.lee20@testclient.com	(555) 120-1020	120 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.648375+00	2025-11-07 20:14:25.648384+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
37	TEST-0036	Nancy	Perez	nancy.perez21@testclient.com	(555) 121-1021	121 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.650207+00	2025-11-07 20:14:25.650215+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
38	TEST-0037	Daniel	Thompson	daniel.thompson22@testclient.com	(555) 122-1022	122 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.652446+00	2025-11-07 20:14:25.652458+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
39	TEST-0038	Lisa	White	lisa.white23@testclient.com	(555) 123-1023	123 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.65509+00	2025-11-07 20:14:25.655106+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
40	TEST-0039	Matthew	Harris	matthew.harris24@testclient.com	(555) 124-1024	124 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.657188+00	2025-11-07 20:14:25.657198+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
41	TEST-0040	Betty	Sanchez	betty.sanchez25@testclient.com	(555) 125-1025	125 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.65931+00	2025-11-07 20:14:25.659321+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
42	TEST-0041	Anthony	Clark	anthony.clark26@testclient.com	(555) 126-1026	126 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.661278+00	2025-11-07 20:14:25.661288+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
43	TEST-0042	Margaret	Ramirez	margaret.ramirez27@testclient.com	(555) 127-1027	127 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.663286+00	2025-11-07 20:14:25.663295+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
44	TEST-0043	Mark	Lewis	mark.lewis28@testclient.com	(555) 128-1028	128 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.665465+00	2025-11-07 20:14:25.665473+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
45	TEST-0044	Sandra	Robinson	sandra.robinson29@testclient.com	(555) 129-1029	129 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.667281+00	2025-11-07 20:14:25.667289+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
13	CL-2028	Abdelrahman	Salah					IL		t	2025-11-06 17:54:30.886644+00	2025-11-08 12:33:08.077286+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
46	TEST-0045	Donald	Walker	donald.walker30@testclient.com	(555) 130-1030	130 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.669683+00	2025-11-07 20:14:25.669693+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
48	TEST-0047	Steven	Allen	steven.allen32@testclient.com	(555) 132-1032	132 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.674187+00	2025-11-07 20:14:25.674195+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
49	TEST-0048	Kimberly	King	kimberly.king33@testclient.com	(555) 133-1033	133 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.676393+00	2025-11-07 20:14:25.676402+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
50	TEST-0049	Paul	Wright	paul.wright34@testclient.com	(555) 134-1034	134 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.678423+00	2025-11-07 20:14:25.678431+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
51	TEST-0050	Emily	Scott	emily.scott35@testclient.com	(555) 135-1035	135 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.680276+00	2025-11-07 20:14:25.680285+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
53	TEST-0052	Donna	Nguyen	donna.nguyen37@testclient.com	(555) 137-1037	137 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.684386+00	2025-11-07 20:14:25.684394+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
54	TEST-0053	Joshua	Hill	joshua.hill38@testclient.com	(555) 138-1038	138 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.686239+00	2025-11-07 20:14:25.686249+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
55	TEST-0054	Michelle	Flores	michelle.flores39@testclient.com	(555) 139-1039	139 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.689039+00	2025-11-07 20:14:25.68905+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
56	TEST-0055	Kenneth	Green	kenneth.green40@testclient.com	(555) 140-1040	140 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.691411+00	2025-11-07 20:14:25.691423+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
57	TEST-0056	Dorothy	Adams	dorothy.adams41@testclient.com	(555) 141-1041	141 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.693798+00	2025-11-07 20:14:25.693807+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
58	TEST-0057	Kevin	Nelson	kevin.nelson42@testclient.com	(555) 142-1042	142 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.696365+00	2025-11-07 20:14:25.696374+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
59	TEST-0058	Carol	Baker	carol.baker43@testclient.com	(555) 143-1043	143 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.698613+00	2025-11-07 20:14:25.698622+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
60	TEST-0059	Brian	Hall	brian.hall44@testclient.com	(555) 144-1044	144 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.700829+00	2025-11-07 20:14:25.700838+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
61	TEST-0060	Amanda	Rivera	amanda.rivera45@testclient.com	(555) 145-1045	145 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.703319+00	2025-11-07 20:14:25.703329+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
62	TEST-0061	George	Campbell	george.campbell46@testclient.com	(555) 146-1046	146 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.705336+00	2025-11-07 20:14:25.705347+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
63	TEST-0062	Melissa	Mitchell	melissa.mitchell47@testclient.com	(555) 147-1047	147 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.707476+00	2025-11-07 20:14:25.707488+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
64	TEST-0063	Timothy	Carter	timothy.carter48@testclient.com	(555) 148-1048	148 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.709577+00	2025-11-07 20:14:25.709589+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
65	TEST-0064	Deborah	Roberts	deborah.roberts49@testclient.com	(555) 149-1049	149 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.712158+00	2025-11-07 20:14:25.712169+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
66	TEST-0065	Ronald	Gomez	ronald.gomez50@testclient.com	(555) 150-1050	150 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.714633+00	2025-11-07 20:14:25.714645+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
67	TEST-0066	Stephanie	Phillips	stephanie.phillips51@testclient.com	(555) 151-1051	151 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.716871+00	2025-11-07 20:14:25.716881+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
68	TEST-0067	Edward	Evans	edward.evans52@testclient.com	(555) 152-1052	152 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.71915+00	2025-11-07 20:14:25.71916+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
69	TEST-0068	Rebecca	Turner	rebecca.turner53@testclient.com	(555) 153-1053	153 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.721329+00	2025-11-07 20:14:25.721338+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
70	TEST-0069	Jason	Diaz	jason.diaz54@testclient.com	(555) 154-1054	154 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.723734+00	2025-11-07 20:14:25.723744+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
71	TEST-0070	Sharon	Parker	sharon.parker55@testclient.com	(555) 155-1055	155 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.726107+00	2025-11-07 20:14:25.726117+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
72	TEST-0071	Jeffrey	Cruz	jeffrey.cruz56@testclient.com	(555) 156-1056	156 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.728364+00	2025-11-07 20:14:25.728373+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
73	TEST-0072	Laura	Edwards	laura.edwards57@testclient.com	(555) 157-1057	157 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.73047+00	2025-11-07 20:14:25.73048+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
74	TEST-0073	Ryan	Collins	ryan.collins58@testclient.com	(555) 158-1058	158 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.732668+00	2025-11-07 20:14:25.732677+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
75	TEST-0074	Cynthia	Reyes	cynthia.reyes59@testclient.com	(555) 159-1059	159 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.734997+00	2025-11-07 20:14:25.735007+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
76	TEST-0075	Jacob	Stewart	jacob.stewart60@testclient.com	(555) 160-1060	160 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.737611+00	2025-11-07 20:14:25.73763+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
77	TEST-0076	Kathleen	Morris	kathleen.morris61@testclient.com	(555) 161-1061	161 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.74002+00	2025-11-07 20:14:25.740048+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
78	TEST-0077	Gary	Morales	gary.morales62@testclient.com	(555) 162-1062	162 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.742289+00	2025-11-07 20:14:25.742298+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
79	TEST-0078	Amy	Murphy	amy.murphy63@testclient.com	(555) 163-1063	163 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.744346+00	2025-11-07 20:14:25.744356+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
80	TEST-0079	Nicholas	Cook	nicholas.cook64@testclient.com	(555) 164-1064	164 Test Street	Test City	NY	10001	t	2025-11-07 20:14:25.746404+00	2025-11-07 20:14:25.746413+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
52	TEST-0051	Andrew	Torres	andrew.torres36@testclient.com	(555) 136-1036	136 Test Street	Test City	NY	10001	f	2025-11-07 20:14:25.682381+00	2025-11-08 13:32:07.147118+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
47	TEST-0046	Ashley	Young	ashley.young31@testclient.com	(555) 131-1031	131 Test Street	Test City	NY	10001	f	2025-11-07 20:14:25.67193+00	2025-11-08 14:11:25.9415+00	individual	ACTIVE_ZERO_BALANCE	webapp	\N
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	clients	case
8	clients	client
9	vendors	vendortype
10	vendors	vendor
11	bank_accounts	bankaccount
12	bank_accounts	banktransaction
13	bank_accounts	bankreconciliation
14	bank_accounts	banktransactionaudit
15	settlements	settlement
16	settlements	settlementreconciliation
17	settlements	settlementdistribution
18	settings	importaudit
19	settings	lawfirm
20	settings	setting
21	settings	checksequence
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	bank_accounts	0001_initial	2025-10-07 09:34:01.527345+00
2	bank_accounts	0002_add_payee_index	2025-10-07 09:34:01.528689+00
3	bank_accounts	0003_banktransactionaudit	2025-10-07 09:34:35.704128+00
4	contenttypes	0001_initial	2025-10-07 09:53:58.438992+00
5	auth	0001_initial	2025-10-07 09:53:58.444918+00
6	admin	0001_initial	2025-10-07 09:53:58.447585+00
7	admin	0002_logentry_remove_auto_add	2025-10-07 09:53:58.449765+00
8	admin	0003_logentry_add_action_flag_choices	2025-10-07 09:53:58.452028+00
9	settings	0001_initial	2025-10-13 18:36:34.006589+00
10	contenttypes	0002_remove_content_type_name	2025-11-13 19:43:20.25841+00
11	auth	0002_alter_permission_name_max_length	2025-11-13 19:43:20.2627+00
12	auth	0003_alter_user_email_max_length	2025-11-13 19:43:20.266182+00
13	auth	0004_alter_user_username_opts	2025-11-13 19:43:20.269678+00
14	auth	0005_alter_user_last_login_null	2025-11-13 19:43:20.273829+00
15	auth	0006_require_contenttypes_0002	2025-11-13 19:43:20.278186+00
16	auth	0007_alter_validators_add_error_messages	2025-11-13 19:43:20.281834+00
17	auth	0008_alter_user_username_max_length	2025-11-13 19:43:20.285194+00
18	auth	0009_alter_user_last_name_max_length	2025-11-13 19:43:20.289233+00
19	auth	0010_alter_group_name_max_length	2025-11-13 19:43:20.294035+00
20	auth	0011_update_proxy_permissions	2025-11-13 19:43:20.29863+00
21	auth	0012_alter_user_first_name_max_length	2025-11-13 19:43:20.302607+00
22	clients	0001_initial	2025-11-13 19:43:20.305869+00
23	reports	0001_initial	2025-11-13 19:43:20.310139+00
24	sessions	0001_initial	2025-11-13 19:43:20.313735+00
25	settlements	0001_initial	2025-11-13 19:43:20.317216+00
26	vendors	0001_initial	2025-11-13 19:43:20.320945+00
27	settings	0002_userprofile	2025-11-14 13:11:48.320041+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
vhmsmoj01a1n8yuebegf2vqdlhnwnhke	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v2ued:VYcm0GoszKRM45R9E2-QL3z47NzpwbbDTraKT30KeGg	2025-09-29 00:53:43.145624+00
vni9787kpgryv9n2726u2tvohf0notcs	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v2uem:vZZfmBFmbSaqVre5DG-LzfB44GVp-Xc63qFcef0_MKo	2025-09-29 00:53:52.643016+00
5s1cnlku3egon0pnm9k8uge5tecp2glq	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v2uiF:bk47XEM5KkNetBkN_hUk4Vy_77lLcosI0cXC-gFWX7I	2025-09-29 00:57:27.258241+00
1x7dey6g1gl8aoz9rd5ajzr0uc0vvxgx	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v2pkE:LeUlvG-nBwyQVEjyhNp6OVjtlFmQB83xfsx_YLMKRvY	2025-09-28 19:39:10.925855+00
btc5d7bbnw6prqvo0baju4kbdxmkria4	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v2ud0:Lm7dBiMLZk0upH_EwjGRa9D0Tl0d80uGKzPljpYulXM	2025-09-29 00:52:02.891069+00
io237p5uaw2hu2woia1u7frl2dvywviq	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v2wF8:4tB7j8PZWxFpcSSVog8pRGcc11xkK5-oIJ_unvTfVXA	2025-09-29 02:35:30.577681+00
kq5e41pbqm3m3q1tb8mgstj0q17uqpe3	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v3E3V:GvmcOZna9ajDRVEVCpjbbaRATjGwI5GrHc2KLnY4Fb8	2025-09-29 21:36:41.837326+00
0z6kb23x1vae9xw32qvnb4vi5sq6zts5	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v52AH:zdHlMsyt3ptfJ72YZlbaJGRp8O_WaT8xZP8_PcM4KZE	2025-10-04 21:19:09.5662+00
l1l4llqsyft8909afwjdvxxvcge5kiat	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v4yW4:nRj8bCsOAU_smSs6Np-izRi51jhUwFez_uYJPNtkAEo	2025-10-04 17:25:24.355097+00
3pdy7xnoje9umkhqzesrhajmd2nc5ju0	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v4kZs:Ji8RB2ynOTO3SVQdrhw-tC1-ZpbQGniDyceOl3-rVcE	2025-10-04 02:32:24.967662+00
99w27olntxb8qyo3m8ulictw2ot6ui33	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v636C:aF6Jk47sSsqepey5OU9C_QMyPSh-LU8M_eZR1MynTC4	2025-10-07 16:31:08.597425+00
ratexbkn7jpy4tqnjhs1oczcly961tft	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v6C60:pXgZ4VdU1cQOsNd-jqZzmFdp2ilo0n-bdo2-mGn2DVY	2025-10-08 02:07:32.825867+00
yjqnevqxrows9dvpj600kocgkk9fi1qv	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v8NlO:8bLqR9SuyDZjrSkcr2cut46tvTWfFqY70FQSEB6y7qk	2025-10-14 02:59:18.897313+00
rwbqqvk7wt7cnqod2vx8lq1jdxsm0hal	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v8NmC:MBCVpccw0QxlafAxhU1akgzIS5mQZFAc0puPbsh-7dU	2025-10-14 03:00:08.150987+00
i7idnrajybnffakd7icauih3hylprvl6	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v8Mou:EuBLoKgfUZA2IaMGlQtwWA6MrE4A5ndZEZJ4jYN5BfA	2025-10-14 01:58:52.128375+00
1g7bey91n5alco127pg4r9geqz8jigi3	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v8N8i:NX9TSqdDScuWTfWjskIFSp04qYYMi6BM7yJtZ3nkUUY	2025-10-14 02:19:20.148643+00
h4wkktpkzz1h306yx3rzs4dwrlgsgivl	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v8Z68:Y_eEu9CI5XfdWBTyGEyXq5XcfkFQFTJmhzx34Hxg8UY	2025-10-14 15:05:28.880872+00
28xnumnrxdujubsxzm6358p3zc7qqnzm	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v8NPb:wv33hq-lc45Gjf4_u8uKKNjJQDI6SctoQCNWTgZso1A	2025-10-14 02:36:47.622994+00
jp08x815d1l5ac1d99jvffb2l1x0sn3a	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v8Nwu:nCeAo-TpCaAh5rUUcZIhoE9GvSX48t95s5A6S804Hls	2025-10-14 03:11:12.225048+00
5szsyyljcp39y7alkrkxtvedezxlc0ad	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v8ZTY:CnrNH8UeyRNeQf_iukp7T4z4OIBd8WxNx25VyCs3-5k	2025-10-14 15:29:40.292581+00
uolrbar7m57sf0k8n77do0a5eekcszjc	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1v8ZQ1:dnprS8TpnzZsCG8srYAofCYsKZ4YpWHG9FacLjHNKxQ	2025-10-14 15:26:01.098702+00
u38u8qrzqyjogkiro6hy86qpcdurt4po	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vFbXY:6iCpOqpjWwgdnxnyG_SqQbL2A7_d2Xb1jiJStfeorfQ	2025-11-03 01:06:52.157803+00
1lm38rz8n2z1u8jkbkox4nbd3ih4okdn	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vFswz:WrU_fvYZY4EiSc7uTVfYcSF1aJu8CkySIjzyztNsweQ	2025-11-03 19:42:17.675753+00
bota3hn6o8xco1rmhouz05z31pgo4wgc	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vFtBT:b6Aw1hu1liaQwzOwGm2HEl2zVdWahQ__TL_be4cBeic	2025-11-03 19:57:15.818285+00
t3oxsp69pbd6ddmzokzlqcv38twosyyv	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vFrDo:uxBUpaG517_1L6vTYJfnD6PNUAkMdlfttA_jBa-1na8	2025-11-03 17:51:32.226801+00
3eaj54gkh8q5zhx1nwe4s2w875yoaxgz	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vFrJG:UlsGrrHA64GGXgpSgFrHZy5qa0GsolL2iyfTfQ7DFfs	2025-11-03 17:57:10.113329+00
6yno44ftn8n7sa413rrl5d5xb08r54in	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vGFLk:q6qDWOZJwKXq69Unfx8OU09QgkBe_4Ureaj9l2Mg8wE	2025-11-04 19:37:20.565424+00
ol2k1tp3tye8ghch0q6u4ye26xfpm44u	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vH5bs:r8oQqdAMCjqw9BrodGHt0wejLMdSYpKmF7D57mNm0L4	2025-11-07 03:25:28.207443+00
grx5qdh0otmq082ervwikqsgc220htph	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vGa7l:Qt76-4XoP_VBD1WspL8E6D3et8DHZKaKaNlMOrUj4Wc	2025-11-05 17:48:17.918965+00
6mot8vjuwno2j89ibb9fc4q6lh9jwww6	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vGGWc:33SjSPU9THVwU6_Dx1ZZjxaBgXIx06wCxZbgzwdorrM	2025-11-04 20:52:38.833661+00
f11llg92len5518okxj4fju9i7qeshug	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vGGIt:hvAyyM6sUZb6q8DGCYa55Kq_7f8YTqGu31vwVDUKpaY	2025-11-04 20:38:27.193153+00
y05gxu8tnwy3ppa3487rgcnbvqxyj52y	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vH5GY:bOq9b17xbGIalGY1yPNTh3GgOLM8bpzlk1oDKX0IEPo	2025-11-07 03:03:26.793005+00
faou9mg2eptyn1mwu0qtyvv3dhr0q07k	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vGgPM:hoeDFenh3pXFfB6fh60VrPTS96be2Gh0MHqcCAZT7DE	2025-11-06 00:30:52.575616+00
873r1ltjs7bdvhg0hgbjyq1xouhm905f	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vGjwQ:t94Dn2RIAKNNJRDRz4mX0deBbtHJe5sxVrLIHrUcGmU	2025-11-06 04:17:14.227638+00
2x8b72eewl98veq6npi0asuv1jhs5fu0	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vHR5X:tx3S-_cbpkKqHVa2Y5Ujk_BvqXYAcpGVvua2o4OK_7o	2025-11-08 02:21:31.966153+00
u691uqgr3z8625kvtgs9ev86a0glr69c	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vH55y:aITgX2sMJ2XSGH0HjfOR2VUynqv3-2K1gzorplUUDDA	2025-11-07 02:52:30.29098+00
e29ql2s67iczpxhri7iyz7yddou57ulv	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vH40e:Xl8nWo7qt8OiYYtnPU3kJmO_gTjtSGlNXu5BbMtu0gg	2025-11-07 01:42:56.644913+00
n0r9vlc9ie3ks8w5xubddrekbsgbja0j	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vITlF:7fL4pZRj4Ph7mskURM5yEGjKcEoWdkMLntLfPCRHWLI	2025-11-10 23:24:53.826481+00
akgupwz7qiz69cxxqavylxu5zr3yv366	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vHnHE:RZPK75W4uiQvsXJEGs7xdCWx_eeBi40XaMtlvAvTkrI	2025-11-09 02:03:04.929252+00
yerqzx5c6ecztilm9ubicq4yiftbpova	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vHSw2:p_VlVehW2knFx655kqjaHkaR4LazxQMG9h2hzY5QiOI	2025-11-08 04:19:50.730202+00
fbpku8y0mjxs6sunqagew51aisbcsq7x	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vIS5V:u4mgdbqzH0F7ON9MWxv-ULGl1C-A1pONEKMxHut_RfU	2025-11-10 21:37:41.080667+00
r8ozbns55n23xtcko9wyqt5mkca2qe1z	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vIZsU:tciJUww2zykL7pnSRucYFVymKR258kNakqZia_DrkMA	2025-11-11 05:56:46.978002+00
cxw69g2fn1ta90uye694hh9k1rn1f15y	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vIVZU:I9kdYt7JVbGYjqhQtzlvCi9DJpnjSmz19B1-R5D9fvE	2025-11-11 01:20:52.330241+00
hxt9382gn73oarph5bzm9w0zw14pzek9	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vIVcf:MxaGsWG36vtgqTG0P5Ur5ZT8bqXL2dBbSFy6Q9W3Ojc	2025-11-11 01:24:09.384061+00
2ex4md1qau2aar7a85ayggdz662kunzj	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vJ8eo:WjodHfucRdWAn5bRHgwHX-VkR4V-izgn_sAzMbl5wPA	2025-11-12 19:04:58.95672+00
qhykwcru9bus1m2lf7pfvc69nu637y2a	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vIiKF:ixa9x-ulIv9tfJ_YPeV9YiUxEoiR52e-b6fJqSkgWP8	2025-11-11 14:57:59.699713+00
6mzog4lf8ncn2g3629kxa0giqfklchfu	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vIuUM:bS8FU0uCRBmC5s5FgeMD1A_zpH-YeTvQIXZTsPkqgcA	2025-11-12 03:57:14.347764+00
16rmhap3my7137d16jczguqiqg4pqye8	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vJG4N:8YEO1171oj8BNQ3z89BjWKlnTgI3CE-7_Kqy0QVYjHM	2025-11-13 02:59:51.353895+00
t6vpjsyden4ga52ercacf3cmvf98bk9l	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vJYzg:mVJKVqxApLdLAWg2G3aULVOZVW9Bw4m-JO0vyvunHs8	2025-11-13 23:12:16.014935+00
s2a3wzy2jzg7etw8xkvidmbojk38afy3	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vJdDd:WXJyhHIS_M49K5VB32qyIoAJkv0iikmCiPO4TRfKGiE	2025-11-14 03:42:57.301367+00
txwu0llt0k1lyvgetf1li8at3lcvhkjq	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vJZyW:91C6-JVvZXOVZ_itDOT-lnEvaXd5-nJ_5oIM3h3AYqE	2025-11-14 00:15:08.824077+00
5gg054v7v6vome2zoumo91xtnl48almq	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vJZvC:YQSpU_0XXQ_0CrHAnCWvqM-ung5vMbktWGGa6SCerus	2025-11-14 00:11:42.738339+00
kduhgickznvai2io5vud1k6papztrqta	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vJvUi:eKBiiVuButPCJL7hnn5USRVonAZIV_ukw4_5_INaWEQ	2025-11-14 23:13:48.254713+00
4mayu59nq63pbborc466ib0a148ei47y	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vJZFw:HiF8TM4fxS03J_GwJ1CrbGD74s1KQkvP5I_tEvqhdyA	2025-11-13 23:29:04.460248+00
e3s48uw7nxw5qn9hf8re4j5kvxd849eq	.eJxVjEEOwiAQRe_C2pgKlKnu9AoegAzDkKIJNTAsjPHutokL3f28n_deymOX2ffG1eeoTkqr3S8LSHcu2yG1N_FItPQi_lGXG5PsG1OvWZ776zb4vIpcJBNKXsrlK_8VZ2zzmiNDQ0IDaJMJB0CCMehoAOIx2BSTY7JxismA04kReCR02oF1kwthiOr9ATJVQOE:1vJZBA:wKcgL3nMiwePm2OfOEkcFs7I8wH2a0sTaQDWHzya9-8	2025-11-13 23:24:08.211345+00
e8vxrzcbvj1u0cruxvj80zgq5vh6acti	.eJxVjUEOwiAQRe_C2jRAGQru9AoegAxTmqIJNTAsjPHu2sSF7n7ez_v_KQJ2XkNvqYY8i6MYxeGXRaRbKnvBtTcOSLT1wuFet2siHlqiXjM_hsse0ukjpsKZkPNWzl_5b3HFtu4_EjH6RapoPEzSevLRzQBACaJzOBrplYLRm8mC1tNktLLRaguLcQsY8XoD35Y-HA:1vJvmc:PfS99mJqznKTjY2_l0kPHsQqJGsag3MIVTeP3uWqaTo	2025-11-14 23:32:18.324603+00
\.


--
-- Data for Name: import_audit; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.import_audit (id, import_date, import_type, file_name, status, total_records, successful_records, failed_records, clients_created, cases_created, transactions_created, vendors_created, error_log, imported_by, created_at, completed_at, expected_clients, expected_cases, expected_transactions, expected_vendors, existing_clients, existing_cases, existing_vendors, preview_data, preview_errors, clients_skipped, cases_skipped, vendors_skipped, rows_with_errors, total_clients_in_csv, total_cases_in_csv, total_transactions_in_csv, total_vendors_in_csv) FROM stdin;
\.


--
-- Data for Name: import_logs; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.import_logs (id, import_type, filename, status, started_at, completed_at, total_rows, clients_created, clients_existing, cases_created, transactions_created, transactions_skipped, errors, summary, created_by_id, created_at, updated_at) FROM stdin;
1	quickbooks_csv	quickbooks_anonymized.csv	in_progress	2025-11-10 14:11:51.247078+00	\N	1263	0	0	0	0	0	[]	{}	2	2025-11-10 14:11:51.247078+00	2025-11-10 14:11:51.247078+00
2	quickbooks_csv	quickbooks_anonymized.csv	completed	2025-11-10 15:08:10.061491+00	2025-11-10 15:08:16.449788+00	1263	166	28	194	1263	0	[]	{}	2	2025-11-10 15:08:10.061491+00	2025-11-10 15:08:16.449934+00
3	quickbooks_csv	quickbooks_anonymized.csv	partial	2025-11-13 11:48:57.427042+00	2025-11-13 11:48:57.878581+00	1263	0	28	0	0	0	[{"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Kevin Nelson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jerry Patel"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jacob Henry"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Charles Romero"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Laura Guzman"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Rebecca Nguyen"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Carolyn Stephens"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Elizabeth Brown"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Brenda Edwards"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Ryan Collins"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Edward Green"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "David Ryan"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Steven Taylor"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jerry Gray"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Dorothy Aguilar"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Raymond Warren"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Dennis Castillo"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Stephen Peterson"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Sandra Robinson"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "George Campbell"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "John Dunn"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Ronald Gomez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Donna Aguilar"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Mark Lee"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Gary Freeman"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Daniel Gonzales"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Unassigned"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Charles Jackson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Linda Hawkins"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Jeffrey Cruz"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Cynthia Crawford"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jonathan Stewart"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Patrick Gray"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Alexander Watson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Steven Reynolds"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Margaret Jordan"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Griffin Solutions Inc"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Helen Morris"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Margaret Lopez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Nicholas Cruz"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Richard Dunn"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Donna Robinson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Brandon Robertson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Richard Jones"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Margaret Martin"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Robert Payne"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Emily Ramirez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Deborah Castro"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Barbara Johnson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Debra Boyd"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Elizabeth Lopez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Daniel Anderson"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Richard Gonzalez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Shirley Guzman"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Kathleen Simpson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Angela Phillips"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Justin Gutierrez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Deborah King"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Andrew Lewis"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Sandra Alexander"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Alexander Schmidt"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Ronald Wells"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "William Coleman"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Laura Roberts"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Helen Cooper"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Anna Murphy"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Michael Miller"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Melissa Young"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jack Chavez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Betty Martinez"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Paul Wright"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jack Salazar"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "James Ryan"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Mary Ross"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Charles Hernandez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Andrew Lee"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Elizabeth Jimenez"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Sarah Johnson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Brenda Kelly"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Jennifer Garcia"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "George Walker"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Brandon Ward"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jonathan Morgan"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Dorothy Fernandez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Katherine Ramos"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Emma Bailey"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Donna Nguyen"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Helen Turner"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Kenneth Harris"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Raymond Kim"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Robert Daniels"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Melissa Woods"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Laura Adams"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "James Ruiz"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Sharon Woods"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Matthew Harris"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Betty Moore"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Nancy Wilson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jerry Meyer"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Christine Cox"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Joshua Walker"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Scott Wagner"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Stephen Morales"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Larry Cook"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Kathleen Turner"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Linda Russell"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "George Stevens"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Amy Hunter"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Mark Lewis"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jessica Russell"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Edward Washington"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Thomas Rodriguez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Barbara Gardner"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Linda Weaver"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Patricia Alvarez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Kevin Ellis"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Angela Crawford"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Patrick Ward"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Anthony Clark"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "James Smith"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Sarah Bell"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Dorothy Robinson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Larry Hunt"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Edward Ford"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Michael Soto"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Cole Solutions Inc"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "David Smith"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Susan Wilson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jessica Fisher"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Benjamin Hunt"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Amy Murphy"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Ross Solutions Inc"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Pamela Shaw"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Nancy Perez"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Christopher Lee"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Barbara Bell"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Samuel Chavez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Susan Jenkins"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Linda Myers"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Dennis Nichols"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Donna Cole"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Patrick Meyer"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Justin Collins"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Rachel Brooks"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Charles Williams"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Karen Butler"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Sharon Parker"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Emma Boyd"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Samuel Holmes"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Angela Shaw"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "James Long"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jacob Hall"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Patrick Robertson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Katherine Palmer"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Daniel Thompson"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Kimberly King"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Eric Silva"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Donald Anderson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Anna Bailey"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Betty Griffin"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jonathan Snyder"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Stephanie Owens"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Pamela Ramos"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Steven Harris"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jacob Evans"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Mark West"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jason McDonald"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Ashley Thomas"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Pamela Palmer"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "David Long"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Brandon Dixon"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Stephanie Phillips"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Melissa Mitchell"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jennifer Stephens"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Katherine Fox"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Paul Jackson"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Timothy Torres"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Nicholas Carter"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Alexander Rose"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Cynthia Vargas"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Matthew Reynolds"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Lopez Corporation"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jackson Company"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jeffrey Green"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Dorothy Nguyen"}, {"error": "Case() got unexpected keyword arguments: 'data_source'", "client": "Kenneth Green"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Sandra Perez"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Joseph Miller"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Paul Clark"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Ashley White"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Timothy Harrison"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Deborah Kennedy"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Lisa Davis"}, {"error": "Client() got unexpected keyword arguments: 'data_source'", "client": "Jennifer Jenkins"}]	{}	2	2025-11-13 11:48:57.427042+00	2025-11-13 11:48:57.879517+00
4	quickbooks_csv	quickbooks_anonymized.csv	completed	2025-11-13 12:20:57.000817+00	2025-11-13 12:21:04.831026+00	1263	166	28	194	1263	0	[]	{}	2	2025-11-13 12:20:57.000817+00	2025-11-13 12:21:04.831202+00
5	quickbooks_csv	transactions_anonymized.csv	completed	2025-11-13 16:59:06.027695+00	2025-11-13 16:59:13.846857+00	1263	166	28	194	1263	0	[]	{}	2	2025-11-13 16:59:06.027695+00	2025-11-13 16:59:13.846981+00
\.


--
-- Data for Name: law_firm; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.law_firm (id, firm_name, doing_business_as, address_line1, address_line2, city, state, zip_code, phone, fax, email, website, principal_attorney, attorney_bar_number, attorney_state, trust_account_required, iolta_compliant, trust_account_certification_date, tax_id, state_registration, is_active, created_at, updated_at) FROM stdin;
1	IOLTA Guard Insurance Law		1200 Insurance Plaza	Suite 500	New York	NY	10004	(212) 555-0100	(212) 555-0101	contact@ioltaguard.com	www.ioltaguard.com	John Smith	NY-123456	NY	t	t	\N	12-3456789	NY-987654	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00
\.


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.settings (id, category, key, value, display_order, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: settlement_distributions; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.settlement_distributions (id, settlement_id, vendor_id, client_id, distribution_type, amount, description, check_number, is_paid, paid_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: settlement_reconciliations; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.settlement_reconciliations (id, settlement_id, bank_balance_before, bank_balance_after, client_balance_before, client_balance_after, total_distributions, reconciliation_status, reconciled_by, reconciled_at, notes, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: settlements; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.settlements (id, settlement_number, settlement_date, client_id, case_id, bank_account_id, total_amount, status, notes, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.user_profiles (id, user_id, role, phone, employee_id, department, is_active, can_approve_transactions, can_reconcile, can_print_checks, can_manage_users, created_at, updated_at, created_by_id) FROM stdin;
1	2	managing_attorney				t	t	t	t	t	2025-11-14 13:32:10.71685	2025-11-14 13:32:10.71685	\N
2	3	bookkeeper				t	f	t	t	f	2025-11-14 15:09:14.413202	2025-11-14 15:09:14.415779	2
\.


--
-- Data for Name: vendor_types; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.vendor_types (id, name, description, is_active, created_at, updated_at, data_source) FROM stdin;
1	Medical Provider	Medical records and healthcare providers	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp
2	Expert Witness	Expert witness services	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp
3	Court Services	Court filing and legal services	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp
4	Process Server	Service of process providers	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp
5	Court Reporter	Deposition and court reporting services	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp
6	Investigator	Private investigation services	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp
8	CSV Import	Vendors auto-created from CSV payees	t	2025-11-10 15:18:31.740849+00	2025-11-10 15:18:31.740849+00	csv
\.


--
-- Data for Name: vendors; Type: TABLE DATA; Schema: public; Owner: iolta_user
--

COPY public.vendors (id, vendor_number, vendor_name, vendor_type_id, contact_person, email, phone, address, city, state, zip_code, tax_id, client_id, is_active, created_at, updated_at, data_source, import_batch_id) FROM stdin;
1	V-1001	Medical Records Plus	1	Dr. Sarah Johnson	records@medicalrecordsplus.com	(212) 555-0201	100 Medical Plaza	New York	NY	10001	12-3456789	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp	\N
2	V-1002	Expert Witness Services	2	Dr. Michael Chen	contact@expertwitness.com	(212) 555-0202	200 Legal Tower	New York	NY	10002	23-4567890	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp	\N
3	V-1003	Court Filing Services	3	Lisa Martinez	filings@courtservices.com	(212) 555-0203	300 Court Street	New York	NY	10003	34-5678901	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp	\N
4	V-1004	Process Servers Inc	4	Robert Anderson	serve@processservers.com	(212) 555-0204	400 Service Ave	New York	NY	10004	45-6789012	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp	\N
5	V-1005	Deposition Reporting Co	5	Jennifer White	report@depositionreporting.com	(212) 555-0205	500 Reporter Lane	New York	NY	10005	56-7890123	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp	\N
6	V-1006	Liability Investigations	6	David Thompson	info@liabilityinv.com	(212) 555-0206	600 Investigation Way	New York	NY	10006	67-8901234	\N	t	2025-11-03 10:45:52.45886+00	2025-11-03 10:45:52.45886+00	webapp	\N
7	VEN-001	Liberty Mutual Ins CO	\N								\N	\N	t	2025-11-06 14:09:36.494867+00	2025-11-06 14:09:36.494886+00	webapp	\N
8	VEN-002	Mohamed Sonbol	\N								\N	\N	t	2025-11-06 14:11:33.974338+00	2025-11-06 14:11:33.974361+00	webapp	\N
9	VEN-003	Bassel Mohamed	\N								\N	\N	t	2025-11-06 18:25:02.360935+00	2025-11-06 18:25:02.360958+00	webapp	\N
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 84, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 3, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: bank_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.bank_accounts_id_seq', 1, true);


--
-- Name: bank_reconciliations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.bank_reconciliations_id_seq', 1, false);


--
-- Name: bank_transaction_audit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.bank_transaction_audit_id_seq', 4066, true);


--
-- Name: bank_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.bank_transactions_id_seq', 4103, true);


--
-- Name: cases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.cases_id_seq', 700, true);


--
-- Name: check_sequences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.check_sequences_id_seq', 1, true);


--
-- Name: clients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.clients_id_seq', 578, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 21, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 27, true);


--
-- Name: import_audit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.import_audit_id_seq', 1, false);


--
-- Name: import_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.import_logs_id_seq', 5, true);


--
-- Name: law_firm_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.law_firm_id_seq', 1, true);


--
-- Name: settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.settings_id_seq', 1, false);


--
-- Name: settlement_distributions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.settlement_distributions_id_seq', 1, false);


--
-- Name: settlement_reconciliations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.settlement_reconciliations_id_seq', 1, false);


--
-- Name: settlements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.settlements_id_seq', 1, false);


--
-- Name: user_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.user_profiles_id_seq', 2, true);


--
-- Name: vendor_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.vendor_types_id_seq', 8, true);


--
-- Name: vendors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: iolta_user
--

SELECT pg_catalog.setval('public.vendors_id_seq', 803, true);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: bank_accounts bank_accounts_account_number_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_account_number_key UNIQUE (account_number);


--
-- Name: bank_accounts bank_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_pkey PRIMARY KEY (id);


--
-- Name: bank_reconciliations bank_reconciliations_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_reconciliations
    ADD CONSTRAINT bank_reconciliations_pkey PRIMARY KEY (id);


--
-- Name: bank_transaction_audit bank_transaction_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_transaction_audit
    ADD CONSTRAINT bank_transaction_audit_pkey PRIMARY KEY (id);


--
-- Name: bank_transactions bank_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_pkey PRIMARY KEY (id);


--
-- Name: case_number_counter case_number_counter_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.case_number_counter
    ADD CONSTRAINT case_number_counter_pkey PRIMARY KEY (id);


--
-- Name: cases cases_case_number_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_case_number_key UNIQUE (case_number);


--
-- Name: cases cases_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_pkey PRIMARY KEY (id);


--
-- Name: check_sequences check_sequences_bank_account_id_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.check_sequences
    ADD CONSTRAINT check_sequences_bank_account_id_key UNIQUE (bank_account_id);


--
-- Name: check_sequences check_sequences_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.check_sequences
    ADD CONSTRAINT check_sequences_pkey PRIMARY KEY (id);


--
-- Name: clients clients_client_number_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_client_number_key UNIQUE (client_number);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: import_audit import_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.import_audit
    ADD CONSTRAINT import_audit_pkey PRIMARY KEY (id);


--
-- Name: import_logs import_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.import_logs
    ADD CONSTRAINT import_logs_pkey PRIMARY KEY (id);


--
-- Name: law_firm law_firm_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.law_firm
    ADD CONSTRAINT law_firm_pkey PRIMARY KEY (id);


--
-- Name: settings settings_category_key_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_category_key_key UNIQUE (category, key);


--
-- Name: settings settings_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settings
    ADD CONSTRAINT settings_pkey PRIMARY KEY (id);


--
-- Name: settlement_distributions settlement_distributions_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settlement_distributions
    ADD CONSTRAINT settlement_distributions_pkey PRIMARY KEY (id);


--
-- Name: settlement_reconciliations settlement_reconciliations_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settlement_reconciliations
    ADD CONSTRAINT settlement_reconciliations_pkey PRIMARY KEY (id);


--
-- Name: settlement_reconciliations settlement_reconciliations_settlement_id_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settlement_reconciliations
    ADD CONSTRAINT settlement_reconciliations_settlement_id_key UNIQUE (settlement_id);


--
-- Name: settlements settlements_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settlements
    ADD CONSTRAINT settlements_pkey PRIMARY KEY (id);


--
-- Name: settlements settlements_settlement_number_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.settlements
    ADD CONSTRAINT settlements_settlement_number_key UNIQUE (settlement_number);


--
-- Name: bank_transactions uk_bank_transactions_number; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT uk_bank_transactions_number UNIQUE (transaction_number) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: clients unique_client_name; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT unique_client_name UNIQUE (first_name, last_name);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_key UNIQUE (user_id);


--
-- Name: vendor_types vendor_types_name_key; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.vendor_types
    ADD CONSTRAINT vendor_types_name_key UNIQUE (name);


--
-- Name: vendor_types vendor_types_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.vendor_types
    ADD CONSTRAINT vendor_types_pkey PRIMARY KEY (id);


--
-- Name: vendors vendors_pkey; Type: CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_pkey PRIMARY KEY (id);


--
-- Name: audit_action_idx; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX audit_action_idx ON public.bank_transaction_audit USING btree (action);


--
-- Name: audit_date_idx; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX audit_date_idx ON public.bank_transaction_audit USING btree (action_date);


--
-- Name: audit_trans_date_idx; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX audit_trans_date_idx ON public.bank_transaction_audit USING btree (transaction_id, action_date DESC);


--
-- Name: audit_user_idx; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX audit_user_idx ON public.bank_transaction_audit USING btree (action_by);


--
-- Name: bank_transaction_audit_transaction_id_8fd3002a; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX bank_transaction_audit_transaction_id_8fd3002a ON public.bank_transaction_audit USING btree (transaction_id);


--
-- Name: idx_bank_transactions_case_id; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_case_id ON public.bank_transactions USING btree (case_id);


--
-- Name: idx_bank_transactions_check_number; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_check_number ON public.bank_transactions USING btree (check_number) WHERE ((check_number IS NOT NULL) AND ((check_number)::text <> ''::text));


--
-- Name: idx_bank_transactions_check_queries; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_check_queries ON public.bank_transactions USING btree (check_number, transaction_type, status, transaction_date) WHERE ((check_number IS NOT NULL) AND ((check_number)::text <> ''::text));


--
-- Name: idx_bank_transactions_client_id; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_client_id ON public.bank_transactions USING btree (client_id);


--
-- Name: idx_bank_transactions_client_type_status; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_client_type_status ON public.bank_transactions USING btree (client_id, transaction_type, status) WHERE (client_id IS NOT NULL);


--
-- Name: idx_bank_transactions_data_source; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_data_source ON public.bank_transactions USING btree (data_source);


--
-- Name: idx_bank_transactions_date; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_date ON public.bank_transactions USING btree (transaction_date);


--
-- Name: idx_bank_transactions_date_type; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_date_type ON public.bank_transactions USING btree (transaction_date, transaction_type);


--
-- Name: idx_bank_transactions_number; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_number ON public.bank_transactions USING btree (transaction_number);


--
-- Name: idx_bank_transactions_payee_lower; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_payee_lower ON public.bank_transactions USING btree (lower((payee)::text));


--
-- Name: idx_bank_transactions_status; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_status ON public.bank_transactions USING btree (status);


--
-- Name: idx_bank_transactions_type; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_type ON public.bank_transactions USING btree (transaction_type);


--
-- Name: idx_bank_transactions_vendor_id; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_bank_transactions_vendor_id ON public.bank_transactions USING btree (vendor_id);


--
-- Name: idx_cases_data_source; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_cases_data_source ON public.cases USING btree (data_source);


--
-- Name: idx_clients_data_source; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_clients_data_source ON public.clients USING btree (data_source);


--
-- Name: idx_import_audit_date; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_import_audit_date ON public.import_audit USING btree (import_date DESC);


--
-- Name: idx_import_logs_created_by; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_import_logs_created_by ON public.import_logs USING btree (created_by_id);


--
-- Name: idx_import_logs_import_type; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_import_logs_import_type ON public.import_logs USING btree (import_type);


--
-- Name: idx_import_logs_started_at; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_import_logs_started_at ON public.import_logs USING btree (started_at DESC);


--
-- Name: idx_import_logs_status; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_import_logs_status ON public.import_logs USING btree (status);


--
-- Name: idx_vendors_data_source; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX idx_vendors_data_source ON public.vendors USING btree (data_source);


--
-- Name: user_profiles_created_by_id_idx; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX user_profiles_created_by_id_idx ON public.user_profiles USING btree (created_by_id);


--
-- Name: user_profiles_role_idx; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX user_profiles_role_idx ON public.user_profiles USING btree (role);


--
-- Name: user_profiles_user_id_idx; Type: INDEX; Schema: public; Owner: iolta_user
--

CREATE INDEX user_profiles_user_id_idx ON public.user_profiles USING btree (user_id);


--
-- Name: bank_transaction_audit bank_transaction_audit_transaction_fk; Type: FK CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_transaction_audit
    ADD CONSTRAINT bank_transaction_audit_transaction_fk FOREIGN KEY (transaction_id) REFERENCES public.bank_transactions(id) ON DELETE CASCADE;


--
-- Name: bank_transactions bank_transactions_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_case_id_fkey FOREIGN KEY (case_id) REFERENCES public.cases(id);


--
-- Name: bank_transactions bank_transactions_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- Name: bank_transactions bank_transactions_vendor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.bank_transactions
    ADD CONSTRAINT bank_transactions_vendor_id_fkey FOREIGN KEY (vendor_id) REFERENCES public.vendors(id);


--
-- Name: check_sequences check_sequences_bank_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.check_sequences
    ADD CONSTRAINT check_sequences_bank_account_id_fkey FOREIGN KEY (bank_account_id) REFERENCES public.bank_accounts(id) ON DELETE CASCADE;


--
-- Name: import_logs import_logs_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.import_logs
    ADD CONSTRAINT import_logs_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.auth_user(id) ON DELETE SET NULL;


--
-- Name: user_profiles user_profiles_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.auth_user(id) ON DELETE SET NULL;


--
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: iolta_user
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.auth_user(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: iolta_user
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

