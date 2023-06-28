{{ config(materialized='table') }}
with source_data_ as (
select * from {{source('stock','prediction')}}

),

final as (select * from source_data_)

select *
from final

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
