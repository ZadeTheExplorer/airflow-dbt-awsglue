
-- Use the `ref` function to select from other models

select id, NOW() as ts
from {{ ref('d_usersname') }}
