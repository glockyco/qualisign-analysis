drop materialized view if exists mv_clazzes_np;
drop materialized view if exists mv_clazzes_mp;
drop materialized view if exists mv_clazzes_sp;
drop materialized view if exists mv_clazzes_p;

drop materialized view mv_clazzes_pattern_counts;
drop materialized view mv_clazzes_patterns;

drop materialized view mv_pattern_roles;
drop materialized view mv_pattern_instances;

drop materialized view if exists mv_methods;
drop materialized view if exists mv_clazzes;
drop materialized view if exists mv_pakkages;
drop materialized view if exists mv_projects;

-- fully processed projects
create materialized view mv_projects as
    select
        projects.name as project_name_full,
        projects.group_id,
        projects.artifact_id,
        projects.version,
        projects.java_version
    from projects
    where pattern_persistence_status = 1;

-- packages in fully processed projects
create materialized view mv_pakkages as
    select
        mv_projects.*,
        pakkages.name as pakkage_name_full,
        replace(pakkages.name, mv_projects.project_name_full || '.', '') as pakkage_name_short
    from mv_projects
    inner join pakkages on mv_projects.project_name_full = pakkages.project;

-- classes in fully processed projects
create materialized view mv_clazzes as
    select
        mv_pakkages.*,
        clazzes.name as clazz_name_full,
        replace(clazzes.name, mv_pakkages.project_name_full || '.', '') as clazz_name_short
    from clazzes
    inner join mv_pakkages on mv_pakkages.pakkage_name_full = clazzes.pakkage;

-- methods in fully processed projects
create materialized view mv_methods as
    select
        mv_clazzes.*,
        methods.name as method_name_full,
        replace(methods.name, mv_clazzes.project_name_full || '.', '') as method_name_short
    from methods
    inner join mv_clazzes on mv_clazzes.clazz_name_full = methods.clazz;

-- patterns in fully processed projects
create materialized view mv_pattern_instances as
    select pattern_instances.*
    from pattern_instances
    inner join mv_projects on pattern_instances.project = mv_projects.project_name_full;

-- pattern roles in fully processed projects
create materialized view mv_pattern_roles as
    select pattern_roles.*
    from pattern_roles
    inner join mv_pattern_instances on pattern_roles.instance_id = mv_pattern_instances.id;

-- classes and the patterns they are participating in
create materialized view mv_clazzes_patterns as
    select
        mv_clazzes.*,
        pattern_instances.id as pattern_id,
        pattern_instances.pattern,
        pattern_roles.id as role_id,
        pattern_roles.role
    from mv_clazzes
    inner join pattern_instances on mv_clazzes.project_name_full = pattern_instances.project
    inner join pattern_roles on pattern_instances.id = pattern_roles.instance_id
    where mv_clazzes.clazz_name_short = pattern_roles.element;

-- classes and number of patterns they are participating in
create materialized view mv_clazzes_pattern_counts as (
    with pattern_counts as (
        select mv_clazzes_patterns.clazz_name_full, count(*) as pattern_count
        from mv_clazzes_patterns
        group by mv_clazzes_patterns.clazz_name_full
    )
    select mv_clazzes.*, coalesce(pattern_counts.pattern_count, 0) as pattern_count
    from mv_clazzes
    left join pattern_counts on mv_clazzes.clazz_name_full = pattern_counts.clazz_name_full
    order by pattern_count desc
);

--  classes that DO participate in ONE OR MORE patterns
create materialized view mv_clazzes_p as
    select * from mv_clazzes_pattern_counts where mv_clazzes_pattern_counts.pattern_count >= 1;

-- classes that DO participate in EXACTLY ONE pattern
create materialized view mv_clazzes_sp as
    select * from mv_clazzes_pattern_counts where mv_clazzes_pattern_counts.pattern_count = 1;

-- classes that DO participate in MORE THAN ONE patterns
create materialized view mv_clazzes_mp as
    select * from mv_clazzes_pattern_counts where mv_clazzes_pattern_counts.pattern_count > 1;

-- classes that DON'T participate in any patterns
create materialized view mv_clazzes_np as
    select * from mv_clazzes_pattern_counts where mv_clazzes_pattern_counts.pattern_count = 0;

-- proportions of non-pattern, pattern, single-pattern and multi-pattern classes
-- with total as (select 0 as index, 'total' as type, count(*) as count, 100 as proportion_of_total from mv_clazzes)
-- select * from total
-- union
-- select 1, 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) from mv_clazzes_np
-- union
-- select 2, 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) from mv_clazzes_p
-- union
-- select 3, 'single-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) from mv_clazzes_sp
-- union
-- select 4, 'multi-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) from mv_clazzes_mp
-- order by index;

-- invalid metrics calculation results
-- select * from clazz_metrics;
-- select * from clazz_metrics where clazz_metrics.loc < 0 or clazz_metrics.cumulative_number_of_comment_lines < 0 order by clazz;
-- select * from clazz_metrics where clazz_metrics.cumulative_number_of_comment_lines < 0;
-- select * from clazz_metrics where clazz_metrics.cumulative_number_of_comments < 0;
