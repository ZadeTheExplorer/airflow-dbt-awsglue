
/*
    Welcome to your first dbt model!
    Did you know that you can also configure models directly within SQL files?
    This will override configurations stated in dbt_project.yml

    Try changing "table" to "view" below
*/

{{ config(materialized='table') }}

with source AS (
    SELECT * FROM {{ ref('telco_customer') }}
)

select 
    gender as Gender_Type,
    count(*) as Gender_Count
from source
group by gender

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
