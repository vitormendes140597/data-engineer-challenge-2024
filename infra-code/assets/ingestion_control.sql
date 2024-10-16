SELECT
    ingestion_id,
    COUNT(1) AS count_of_records
FROM
    `${project_id}.${dataset_id}.${table_id}`
GROUP BY
    1