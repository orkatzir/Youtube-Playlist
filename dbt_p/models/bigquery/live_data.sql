{{ config(materialized='table') }}
with source_data_ as (
select * from {{source('youtube_live','youtube_videos')}}

),
max_date as(
SELECT  MAX(yt.TIME) as run_time
FROM source_data_  AS yt),

final as (select * from source_data_  AS yt 
inner join max_date on yt.TIME=max_date.run_time
)

select *
from final

/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
