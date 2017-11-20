CACHE_HITS_NAME = 'cache-hits'
CACHE_HITS_SQL = '''
    SELECT
        sum(heap_blks_read) heap_read,
        sum(heap_blks_hit)  heap_hit,
        sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) ratio
    FROM
        pg_statio_user_tables;
'''

INDEX_USAGE_NAME = 'index-usage'
INDEX_USAGE_SQL = '''
    SELECT
        relname,
        100 * idx_scan / (seq_scan + idx_scan) percent_of_times_index_used,
        n_live_tup rows_in_table
    FROM
        pg_stat_user_tables
    WHERE
        seq_scan + idx_scan > 0
    ORDER BY
        percent_of_times_index_used DESC;
'''

METRICS = {
    CACHE_HITS_NAME: CACHE_HITS_SQL,
    INDEX_USAGE_NAME: INDEX_USAGE_SQL,
}
