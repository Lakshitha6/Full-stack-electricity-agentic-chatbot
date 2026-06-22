-- 1. Secure RPC: Dynamic SELECT with strict validation
CREATE OR REPLACE FUNCTION exec_secure_select(
    p_electricity_id TEXT,
    p_columns TEXT[],
    p_where_clause TEXT DEFAULT NULL
) RETURNS JSONB LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
    safe_cols TEXT;
    full_query TEXT;
    result JSONB;
    allowed_cols TEXT[] := ARRAY['units','month','price','paid_amount','balance'];
BEGIN
    -- Validate columns
    IF NOT ARRAY(SELECT unnest(p_columns)) <@ allowed_cols THEN
        RAISE EXCEPTION 'Invalid columns requested';
    END IF;
    safe_cols := array_to_string(ARRAY(SELECT quote_ident(c) FROM unnest(p_columns) AS c), ', ');

    -- Build query with electricity_id filter
    full_query := format('SELECT %s FROM usage WHERE electricity_id = $1', safe_cols);
    IF p_where_clause IS NOT NULL THEN
        -- Only allow simple, safe WHERE clauses (alphanumeric, quotes, operators)
        IF p_where_clause ~ '^[a-zA-Z0-9_=\''\s\-\.<>!%]+$' THEN
            full_query := full_query || ' AND ' || p_where_clause;
        ELSE
            RAISE EXCEPTION 'Invalid WHERE clause';
        END IF;
    END IF;
    full_query := full_query || ' LIMIT 50';

    -- Execute safely with parameter binding
    EXECUTE format('SELECT jsonb_agg(row_to_json(t)) FROM (%s) t', full_query)
    INTO result USING p_electricity_id;
    RETURN COALESCE(result, '[]'::JSONB);
END;
$$;

-- 2. Auto Balance Trigger (handles over/under payments automatically)
CREATE OR REPLACE FUNCTION calc_usage_balance() RETURNS TRIGGER AS $$
BEGIN
    NEW.balance := (
        SELECT COALESCE(SUM(price) - SUM(paid_amount), 0)
        FROM usage
        WHERE electricity_id = NEW.electricity_id
          AND month <= NEW.month
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_balance_calc ON usage;
CREATE TRIGGER trg_balance_calc BEFORE INSERT OR UPDATE ON usage
FOR EACH ROW EXECUTE FUNCTION calc_usage_balance();

-- 3. Revoke public access to RPC
REVOKE ALL ON FUNCTION exec_secure_select(TEXT, TEXT[], TEXT) FROM PUBLIC;