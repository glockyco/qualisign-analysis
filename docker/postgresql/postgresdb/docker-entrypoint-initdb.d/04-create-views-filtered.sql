-- patterns that can/can't be mapped to projects/packages/classes
with
    total as (select count(distinct pattern_id) as count from mv_pattern_roles_processed),
    mappable_projects as (select * from mv_pattern_roles_processed inner join mv_projects_processed mp on mv_pattern_roles_processed.project_name_full = mp.project_name_full),
    mappable_pakkages as (select * from mv_pattern_roles_processed inner join mv_pakkages_processed mp on mv_pattern_roles_processed.pakkage_name_full = mp.pakkage_name_full),
    mappable_clazzes as (select * from mv_pattern_roles_processed inner join mv_clazzes_processed mc on mv_pattern_roles_processed.clazz_name_full = mc.clazz_name_full)
select 0 as index, 'Total' as type, count from total
union
select 1, 'Mappable - Projects', count(distinct pattern_id) from mappable_projects
union
select 2, 'Unmappable - Projects', (select count from total) - count(distinct pattern_id) from mappable_projects
union
select 3, 'Mappable - Packages', count(distinct pattern_id) from mappable_pakkages
union
select 4, 'Unmappable - Packages', (select count from total) - count(distinct pattern_id) from mappable_pakkages
union
select 5, 'Mappable - Classes', count(distinct pattern_id) from mappable_clazzes
union
select 6, 'Unmappable - Classes', (select count from total) - count(distinct pattern_id) from mappable_clazzes
order by index;

-- pattern roles that can/can't be mapped to projects/packages/classes
with
    total as (select count(*) as count from mv_pattern_roles_processed),
    mappable_projects as (select * from mv_pattern_roles_processed inner join mv_projects_processed mp on mv_pattern_roles_processed.project_name_full = mp.project_name_full),
    mappable_pakkages as (select * from mv_pattern_roles_processed inner join mv_pakkages_processed mp on mv_pattern_roles_processed.pakkage_name_full = mp.pakkage_name_full),
    mappable_clazzes as (select * from mv_pattern_roles_processed inner join mv_clazzes_processed mc on mv_pattern_roles_processed.clazz_name_full = mc.clazz_name_full)
select 0 as index, 'Total' as type, count from total
union
select 1, 'Mappable - Projects', count(*) from mappable_projects
union
select 2, 'Unmappable - Projects', (select count from total) - count(*) from mappable_projects
union
select 3, 'Mappable - Packages', count(*) from mappable_pakkages
union
select 4, 'Unmappable - Packages', (select count from total) - count(*) from mappable_pakkages
union
select 5, 'Mappable - Classes', count(*) from mappable_clazzes
union
select 6, 'Unmappable - Classes', (select count from total) - count(*) from mappable_clazzes
order by index;

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

drop materialized view mv_projects;
create materialized view mv_projects as (
    -- projects without patterns
    select mv_projects_processed.* from mv_projects_processed
                                            left join mv_pattern_instances_processed on mv_projects_processed.project_name_full = mv_pattern_instances_processed.project_name_full
    where mv_pattern_instances_processed.pattern_id is null
    union all
    -- projects that have metrics for all patterns
    select mv_projects_processed.* from mv_projects_processed
                                            inner join mv_pattern_roles_processed on mv_pattern_roles_processed.project_name_full = mv_projects_processed.project_name_full
                                            left join mv_clazzes_processed on mv_pattern_roles_processed.clazz_name_full = mv_clazzes_processed.clazz_name_full
    group by
        mv_projects_processed.project_name_full,
        mv_projects_processed.group_id,
        mv_projects_processed.artifact_id,
        mv_projects_processed.version,
        mv_projects_processed.java_version
    having every(mv_clazzes_processed.clazz_name_full is not null)
    order by project_name_full
);

create unique index on mv_projects (project_name_full);

create materialized view mv_pakkages as (
    select mv_pakkages_processed.*
    from mv_pakkages_processed
             inner join mv_projects on mv_projects.project_name_full = mv_pakkages_processed.project_name_full
);

create unique index on mv_pakkages (pakkage_name_full);

create materialized view mv_clazzes as (
    select mv_clazzes_processed.*
    from mv_clazzes_processed
             inner join mv_projects on mv_projects.project_name_full = mv_clazzes_processed.project_name_full
);

create unique index on mv_clazzes (clazz_name_full);

-- create materialized view mv_methods as (
--     select mv_methods.*
--     from mv_methods
--     inner join mv_projects_mappable on mv_projects_mappable.project_name_full = mv_methods.project_name_full
-- );

create materialized view mv_pattern_instances as (
    select mv_pattern_instances_processed.*
    from mv_pattern_instances_processed
             inner join mv_projects on mv_projects.project_name_full = mv_pattern_instances_processed.project_name_full
);

create unique index on mv_pattern_instances (pattern_id);

create materialized view mv_pattern_roles as (
    select mv_pattern_roles_processed.*
    from mv_pattern_roles_processed
             inner join mv_projects on mv_projects.project_name_full = mv_pattern_roles_processed.project_name_full
);

create unique index on mv_pattern_roles (role_id);

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

